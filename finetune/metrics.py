"""Single source of truth for benchmark metrics, naive baselines, and
significance tests.

Everything here is pure numpy/scipy so it runs in CPU unit tests. The benchmark
harness (``finetune/benchmark.py``) feeds model/baseline outputs into these
functions; nothing here imports torch or timesfm.

Sign convention notes
---------------------
* Direction is invariant to the monotonic log + z-score transform, so
  directional metrics may be computed in normalized space. **Returns/Sharpe must
  use price space** (inverse-transformed), since magnitude is not transform-
  invariant.
* Diebold-Mariano is called as ``diebold_mariano(model_loss, base_loss)``; a
  **negative** statistic means the model has lower forecast loss (is better).

Definitions are written out (with formulas) so they lift directly into the
paper's Methods section.
"""

from __future__ import annotations

import math

import numpy as np
from scipy.stats import binomtest, norm

__all__ = [
    # directional
    "directional_metrics",
    # point
    "point_metrics",
    "naive_scale",
    "macro_average",
    # calibration
    "calibration_table",
    # trading
    "trading_metrics",
    # significance
    "mcnemar_test",
    "block_bootstrap_ci",
    "diebold_mariano",
    "benjamini_hochberg",
]

_EPS = 1e-12


# --------------------------------------------------------------------------- #
# Directional metrics
# --------------------------------------------------------------------------- #
def _balanced_accuracy(actual_up: np.ndarray, pred_up: np.ndarray) -> float:
    """Mean of per-class recall (up / down) — robust to class imbalance."""
    recalls = []
    for cls in (True, False):
        m = actual_up == cls
        if m.sum() > 0:
            recalls.append(float((pred_up[m] == cls).mean()))
    return float(np.mean(recalls)) if recalls else float("nan")


def _matthews_corrcoef(actual_up: np.ndarray, pred_up: np.ndarray) -> float:
    """Matthews correlation coefficient for the up/down confusion matrix.

    MCC = (TP*TN - FP*FN) / sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)); 0 if any
    marginal is empty (degenerate predictor).
    """
    tp = float(np.sum(pred_up & actual_up))
    tn = float(np.sum(~pred_up & ~actual_up))
    fp = float(np.sum(pred_up & ~actual_up))
    fn = float(np.sum(~pred_up & actual_up))
    denom = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    return (tp * tn - fp * fn) / denom if denom > 0 else 0.0


def directional_metrics(pred_change: np.ndarray, actual_change: np.ndarray) -> dict:
    """Directional skill of a forecaster vs the always-up base rate.

    A *window* contributes only if the model makes a directional call
    (``pred_change != 0``) and the actual move is non-flat (``actual_change !=
    0``). This excludes random-walk "no-change" predictions (they make no bet)
    and undefined-direction targets.

    Returns (all on the same filtered windows, so ``excess_acc`` is a proper
    paired quantity):
        acc            : P(sign(pred) == sign(actual))
        always_up_acc  : P(actual went up)  — the base rate / "always predict up"
        excess_acc     : acc - always_up_acc
        balanced_acc   : mean of up-recall and down-recall
        mcc            : Matthews correlation coefficient
        n_windows      : number of contributing windows
    """
    pred_change = np.asarray(pred_change, dtype=float)
    actual_change = np.asarray(actual_change, dtype=float)
    call = (pred_change != 0) & (actual_change != 0)
    n = int(call.sum())
    nan = float("nan")
    if n == 0:
        return {
            "acc": nan, "always_up_acc": nan, "excess_acc": nan,
            "balanced_acc": nan, "mcc": nan, "n_windows": 0,
        }
    pred_up = pred_change[call] > 0
    actual_up = actual_change[call] > 0
    acc = float((pred_up == actual_up).mean())
    always_up = float(actual_up.mean())
    return {
        "acc": acc,
        "always_up_acc": always_up,
        "excess_acc": acc - always_up,
        "balanced_acc": _balanced_accuracy(actual_up, pred_up),
        "mcc": _matthews_corrcoef(actual_up, pred_up),
        "n_windows": n,
    }


# --------------------------------------------------------------------------- #
# Point-forecast metrics (price space, macro-averaged per ticker upstream)
# --------------------------------------------------------------------------- #
def naive_scale(train_prices: np.ndarray) -> float:
    """In-sample one-step random-walk MAE used to scale MASE.

    scale = mean_t |P_t - P_{t-1}| over the training portion of the series.
    """
    p = np.asarray(train_prices, dtype=float)
    if p.size < 2:
        return float("nan")
    return float(np.mean(np.abs(np.diff(p))))


def point_metrics(y_true: np.ndarray, y_pred: np.ndarray, scale: float | None = None) -> dict:
    """MAE / RMSE / sMAPE / MASE on aligned price-space arrays.

    MASE = MAE / scale, where ``scale`` is the in-sample random-walk MAE
    (``naive_scale`` on the training prices). sMAPE is reported as a fraction in
    [0, 2]: mean( 2|y-ŷ| / (|y|+|ŷ|) ).
    """
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_pred = np.asarray(y_pred, dtype=float).ravel()
    # Drop any non-finite aligned pairs: the inverse transform is exp(...), so a
    # divergent forecast can reconstruct to +inf and poison MAE/RMSE. Guards the
    # model path; divergent baselines are excluded upstream (see POINT_EXCLUDE).
    finite = np.isfinite(y_true) & np.isfinite(y_pred)
    y_true, y_pred = y_true[finite], y_pred[finite]
    if y_true.size == 0:
        return {"MAE": float("nan"), "RMSE": float("nan"), "sMAPE": float("nan"),
                "MASE": float("nan"), "n": 0}
    err = y_true - y_pred
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err ** 2)))
    smape = float(np.mean(2.0 * np.abs(err) / (np.abs(y_true) + np.abs(y_pred) + _EPS)))
    mase = float(mae / scale) if scale and scale > 0 else float("nan")
    return {"MAE": mae, "RMSE": rmse, "sMAPE": smape, "MASE": mase,
            "n": int(y_true.size)}


def macro_average(metric_dicts: list[dict]) -> dict:
    """Average a list of per-ticker metric dicts key-wise (ignoring NaNs).

    Use for point metrics so high-priced tickers don't dominate pooled RMSE/MAE.
    ``n_windows`` is summed; everything else is nan-mean averaged.
    """
    if not metric_dicts:
        return {}
    keys = set().union(*(d.keys() for d in metric_dicts))
    out = {}
    for k in keys:
        vals = [d[k] for d in metric_dicts if k in d]
        if k in ("n", "n_windows", "n_trades"):
            out[k] = int(np.nansum(vals))
        else:
            arr = np.array(vals, dtype=float)
            out[k] = float(np.nanmean(arr)) if np.any(~np.isnan(arr)) else float("nan")
    return out


# --------------------------------------------------------------------------- #
# Calibration (probabilistic) — from the quantile head
# --------------------------------------------------------------------------- #
def _pinball(y_true: np.ndarray, q_pred: np.ndarray, level: float) -> float:
    """Pinball (quantile) loss at one level: mean(max(q·e, (q-1)·e)), e=y-ŷ_q."""
    e = y_true - q_pred
    return float(np.mean(np.maximum(level * e, (level - 1.0) * e)))


def calibration_table(y_true: np.ndarray, quantile_preds: np.ndarray,
                      quantile_levels) -> tuple[list[dict], float]:
    """Per-level coverage + pinball, and an approximate CRPS.

    Args:
        y_true: (n,) realized values (price space).
        quantile_preds: (n, K) forecasts, column k = level quantile_levels[k].
        quantile_levels: length-K nominal levels in (0, 1).

    coverage(level) = empirical P(y <= ŷ_level); a calibrated forecast has
    coverage ≈ level. CRPS is approximated by 2·mean_k pinball_k (exact in the
    limit of densely, evenly spaced levels).

    Returns (rows, crps) where each row has level/nominal/empirical_coverage/
    pinball/n.
    """
    y_true = np.asarray(y_true, dtype=float).ravel()
    quantile_preds = np.asarray(quantile_preds, dtype=float)
    rows = []
    for k, level in enumerate(quantile_levels):
        qp = quantile_preds[:, k]
        rows.append({
            "quantile_level": float(level),
            "nominal": float(level),
            "empirical_coverage": float(np.mean(y_true <= qp)),
            "pinball": _pinball(y_true, qp, float(level)),
            "n": int(y_true.size),
        })
    crps = float(2.0 * np.mean([r["pinball"] for r in rows])) if rows else float("nan")
    return rows, crps


# --------------------------------------------------------------------------- #
# Trading / economic metrics — REAL returns (price space)
# --------------------------------------------------------------------------- #
def _sharpe(returns: np.ndarray, horizon: int) -> float:
    """Annualized Sharpe = mean(r)/std(r) * sqrt(252/h) for non-overlapping
    h-day trades. Sample std (ddof=1)."""
    r = np.asarray(returns, dtype=float)
    if r.size < 2:
        return float("nan")
    sd = r.std(ddof=1)
    if sd <= 0:
        return 0.0
    return float(r.mean() / sd * math.sqrt(252.0 / horizon))


def _max_drawdown(returns: np.ndarray) -> float:
    """Most negative peak-to-trough of the compounded equity curve, in [-1, 0].

    Per-trade returns are floored at -1.0 (a total, 100% loss of the capital
    allocated to that trade — i.e. a stopped-out position) before compounding.
    Without the floor a *short* trade whose underlying more than doubles has a
    return below -100%, which drives ``1 + r`` negative; the cumulative-product
    equity curve then flips sign and the drawdown ratio explodes to nonsensical
    values (observed: -60 for pooled, -25636 for ar1 at h=128). The floor keeps
    equity >= 0 and drawdown >= -1, matching the economics of a margin stop. The
    curve is seeded with 1.0 so the running peak is always positive.
    """
    r = np.asarray(returns, dtype=float)
    if r.size == 0:
        return 0.0
    equity = np.concatenate([[1.0], np.cumprod(1.0 + np.maximum(r, -1.0))])
    peak = np.maximum.accumulate(equity)
    return float((equity / peak - 1.0).min())


def trading_metrics(pred_change: np.ndarray, current_price: np.ndarray,
                    future_price: np.ndarray, horizon: int,
                    cost_bps: float = 0.0) -> dict:
    """Directional long/short strategy on non-overlapping h-day trades.

    signal = sign(pred_change)  (+1 long, -1 short, 0 = no trade / random-walk).
    market return r_m = future_price/current_price - 1   (price space).
    gross strategy return = signal · r_m.
    Round-trip transaction cost = (cost_bps/1e4)·2 applied to traded windows;
    net = gross - cost.

    Returns Sharpe (gross + cost-adjusted), max drawdown, hit rate, turnover,
    mean return, and n_trades. Windows with signal==0 are not counted as trades.
    """
    signal = np.sign(np.asarray(pred_change, dtype=float))
    cur = np.asarray(current_price, dtype=float)
    fut = np.asarray(future_price, dtype=float)
    market_ret = fut / np.where(cur == 0, np.nan, cur) - 1.0

    traded = signal != 0
    n_trades = int(traded.sum())
    if n_trades == 0:
        return {"sharpe": float("nan"), "sharpe_net": float("nan"),
                "max_drawdown": 0.0, "hit_rate": float("nan"),
                "turnover": 0.0, "mean_return": float("nan"), "n_trades": 0}

    gross = (signal * market_ret)[traded]
    cost = (cost_bps / 1e4) * 2.0
    net = gross - cost
    # turnover: fraction of consecutive trades that flip position (0..1)
    s = signal[traded]
    turnover = float(np.mean(np.abs(np.diff(s)) / 2.0)) if s.size > 1 else 0.0

    return {
        "sharpe": _sharpe(gross, horizon),
        "sharpe_net": _sharpe(net, horizon),
        "max_drawdown": _max_drawdown(gross),
        "hit_rate": float(np.mean(gross > 0)),
        "turnover": turnover,
        "mean_return": float(np.mean(gross)),
        "n_trades": n_trades,
    }


# --------------------------------------------------------------------------- #
# Significance tests (paired / block — not plain binomial vs 50%)
# --------------------------------------------------------------------------- #
def mcnemar_test(model_correct: np.ndarray, base_correct: np.ndarray) -> dict:
    """Exact McNemar test on paired per-window correctness (model vs baseline).

    Uses discordant pairs b = (model right, base wrong), c = (model wrong, base
    right). Exact two-sided binomial on min(b, c) ~ Binom(b+c, 0.5).
    """
    model_correct = np.asarray(model_correct, dtype=bool)
    base_correct = np.asarray(base_correct, dtype=bool)
    b = int(np.sum(model_correct & ~base_correct))
    c = int(np.sum(~model_correct & base_correct))
    n = b + c
    if n == 0:
        return {"b": b, "c": c, "n_discordant": 0, "statistic": 0.0, "p": 1.0}
    p = binomtest(min(b, c), n, 0.5, alternative="two-sided").pvalue
    # chi-square statistic with continuity correction (for reporting)
    stat = (abs(b - c) - 1.0) ** 2 / n
    return {"b": b, "c": c, "n_discordant": n, "statistic": float(stat), "p": float(p)}


def block_bootstrap_ci(values: np.ndarray, block_ids: np.ndarray,
                       statistic=np.mean, n_boot: int = 2000,
                       alpha: float = 0.05, seed: int = 0) -> dict:
    """Block bootstrap CI for a statistic of ``values``, resampling whole blocks.

    Financial windows are autocorrelated within a ticker (and across nearby
    dates), so we resample by block id (e.g. ticker, or ticker×date-bucket)
    rather than i.i.d. For paired excess accuracy, pass values = (model_correct
    - base_correct) and statistic = mean → CI for excess_acc.
    """
    values = np.asarray(values, dtype=float)
    block_ids = np.asarray(block_ids)
    if values.size == 0:
        return {"point": float("nan"), "lo": float("nan"), "hi": float("nan"),
                "n_blocks": 0}

    uniq = np.unique(block_ids)
    blocks = [values[block_ids == b] for b in uniq]
    rng = np.random.default_rng(seed)
    n_blocks = len(blocks)

    point = float(statistic(values))
    boots = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        pick = rng.integers(0, n_blocks, size=n_blocks)
        sample = np.concatenate([blocks[j] for j in pick])
        boots[i] = statistic(sample)
    lo = float(np.percentile(boots, 100 * alpha / 2))
    hi = float(np.percentile(boots, 100 * (1 - alpha / 2)))
    return {"point": point, "lo": lo, "hi": hi, "n_blocks": n_blocks}


def diebold_mariano(model_loss: np.ndarray, base_loss: np.ndarray,
                    horizon: int = 1) -> dict:
    """Diebold-Mariano test of equal forecast accuracy.

    d_t = model_loss_t - base_loss_t. Long-run variance uses a Newey-West /
    Bartlett kernel with lag h-1 (h-step forecasts are MA(h-1) autocorrelated).
    DM = mean(d) / sqrt(LRV/n); two-sided normal p-value. A **negative** DM
    means the model has lower loss (better) than the baseline.
    """
    d = np.asarray(model_loss, dtype=float) - np.asarray(base_loss, dtype=float)
    n = d.size
    if n < 2:
        return {"statistic": float("nan"), "p": float("nan"), "mean_diff": float("nan"), "n": int(n)}
    dbar = float(d.mean())
    dc = d - dbar
    gamma0 = float(np.mean(dc * dc))
    lrv = gamma0
    # Newey-West / Bartlett HAC long-run variance. Cap the lag at n-2: h-step
    # forecasts are MA(h-1)-correlated in theory, but with non-overlapping
    # long-horizon windows n can be < h (e.g. n~66 at h=128) and you cannot
    # estimate more autocovariances than you have data.
    max_lag = max(0, min(int(horizon) - 1, n - 2))
    for k in range(1, max_lag + 1):
        cov = float(np.mean(dc[k:] * dc[:-k]))
        lrv += 2.0 * (1.0 - k / (max_lag + 1)) * cov
    # The sample HAC estimate can still come out <= 0 when n is small relative to
    # the lag; previously that was floored to _EPS, which exploded the statistic
    # (observed |DM| ~ 1e5 at h=128, n~66). Fall back to the non-negative iid
    # variance gamma0 in that degenerate case instead.
    if lrv <= 0:
        lrv = gamma0
    lrv = max(lrv, _EPS)
    stat = dbar / math.sqrt(lrv / n)
    p = float(2.0 * (1.0 - norm.cdf(abs(stat))))
    return {"statistic": float(stat), "p": p, "mean_diff": dbar, "n": int(n)}


def benjamini_hochberg(pvals, alpha: float = 0.05):
    """Benjamini-Hochberg FDR control.

    Returns (qvalues, reject) where qvalues are the BH-adjusted p-values
    (monotone) and reject is the boolean accept/reject mask at level ``alpha``.
    NaN p-values pass through as NaN q-values and reject=False.
    """
    p = np.asarray(pvals, dtype=float)
    finite = ~np.isnan(p)
    q = np.full_like(p, np.nan, dtype=float)
    reject = np.zeros_like(p, dtype=bool)

    idx = np.where(finite)[0]
    if idx.size == 0:
        return q, reject
    pv = p[idx]
    order = np.argsort(pv)
    ranked = pv[order]
    m = ranked.size
    # adjusted p-values, enforced monotone from the largest rank down
    adj = ranked * m / (np.arange(1, m + 1))
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    adj = np.clip(adj, 0.0, 1.0)
    q_sorted = np.empty(m, dtype=float)
    q_sorted[order] = adj
    q[idx] = q_sorted
    reject[idx] = q_sorted <= alpha
    return q, reject
