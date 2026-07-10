"""Unified evaluation harness for the per-sector LoRA benchmark.

Wires the metrics in ``finetune/metrics.py`` to model and baseline forecasts over
a single set of identical windows. Produces the paper's canonical tables
(A: directional/trading, B: point, C: calibration) plus the per-window arrays
that ``run_benchmark.py`` needs for the pairwise significance table (D).

Only the model path imports torch/timesfm (via ``decode_forward``); the naive
baselines and all metric assembly are pure numpy and CPU-testable.

Window protocol
---------------
A test series is the per-ticker normalized array ``[pre-test context prefix of
length context_len] + [test values]`` (the prefix uses pre-test data only, per
the normalization rule). We slide **non-overlapping** windows (stride = horizon)
so trades don't overlap (valid Sharpe) and windows are weakly autocorrelated
(valid block bootstrap). Directional accuracy at horizon h reads step h of each
window's predicted path; trading uses the h=128 endpoint.
"""



from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from finetune.metrics import (
    _sharpe,
    block_bootstrap_ci,
    calibration_table,
    directional_metrics,
    macro_average,
    naive_scale,
    point_metrics,
    trading_metrics,
)

CONTEXT_LEN = 512
HORIZON = 128
HORIZONS = (2, 4, 8, 16, 32, 64, 128)
# TimesFM 2.5 output channels (median at index 5). Verify against the model's
# own quantile definition on first GPU run (calibration coverage confirms it).
QUANTILE_LEVELS = (0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
BASELINES = ("always_up", "random_walk", "persistence", "ar1")
# Methods excluded from the point-forecast table (Table B). Persistence
# extrapolates the last log-return linearly for `horizon` steps, so its price
# path = exp(last_return * step) diverges geometrically (observed MAE ~8e5 at
# h=128) — it has no meaningful level forecast and is reported only in the
# directional / trading table (Table A). All other methods give a bounded level.
POINT_EXCLUDE = ("persistence",)


# --------------------------------------------------------------------------- #
# Per-ticker evaluation input
# --------------------------------------------------------------------------- #
@dataclass
class EvalSeries:
    """One ticker's prepared test data for a single fold."""
    ticker: str
    sector: str
    category: str          # "stock" | "etf"
    split: str             # "seen" | "held_out"
    series_norm: np.ndarray   # normalized [prefix + test]
    normalizer: object        # LogNormalizer (has inverse_transform)
    series_id: int
    train_prices: np.ndarray  # raw train prices (for MASE naive scale)


# --------------------------------------------------------------------------- #
# Windowing
# --------------------------------------------------------------------------- #
def build_windows(series_norm: np.ndarray, context_len: int = CONTEXT_LEN,
                  horizon: int = HORIZON, stride: int | None = None):
    """Slide non-overlapping windows over a normalized series.

    Returns (contexts (W, context_len), futures (W, horizon)). The first window's
    context is the pre-test prefix; every window's target lies in the test span.
    """
    stride = stride or horizon
    W = []
    F = []
    last = len(series_norm) - context_len - horizon
    for start in range(0, last + 1, stride):
        W.append(series_norm[start:start + context_len])
        F.append(series_norm[start + context_len:start + context_len + horizon])
    if not W:
        return (np.empty((0, context_len)), np.empty((0, horizon)))
    return np.asarray(W, dtype=float), np.asarray(F, dtype=float)


# --------------------------------------------------------------------------- #
# Baseline forecasts (CPU) — return a normalized predicted path (W, horizon)
# --------------------------------------------------------------------------- #
def baseline_paths(name: str, contexts: np.ndarray, horizon: int = HORIZON) -> np.ndarray:
    """Predicted normalized path for a naive baseline. See module docstring /
    EXPERIMENT_LOG for exact definitions."""
    cur = contexts[:, -1:]                       # (W,1)
    steps = np.arange(1, horizon + 1, dtype=float)  # (horizon,)

    if name == "always_up":
        # strictly increasing -> directional call is "up" at every horizon
        return cur + 1e-6 * steps
    if name == "random_walk":
        # flat -> no directional call (excluded), 0 trade return
        return np.repeat(cur, horizon, axis=1)
    if name == "persistence":
        r = (contexts[:, -1] - contexts[:, -2])[:, None]   # last return (W,1)
        return cur + r * steps
    if name == "ar1":
        return _ar1_paths(contexts, horizon)
    raise ValueError(f"unknown baseline: {name}")


def _ar1_paths(contexts: np.ndarray, horizon: int) -> np.ndarray:
    """AR(1)-on-returns, directly projecting the h-period cumulative return.

    Fit r_t = a + b r_{t-1} per window; closed-form conditional mean
    E[r_{T+k}] = mu + b^k (r_T - mu), cumulative over k=1..h. Level path =
    current + cumret(h). Not recursive one-step.
    """
    d = np.diff(contexts, axis=1)                 # returns (W, L-1)
    mu = d.mean(axis=1, keepdims=True)            # (W,1)
    dc = d - mu
    num = np.sum(dc[:, 1:] * dc[:, :-1], axis=1)
    den = np.sum(dc[:, :-1] ** 2, axis=1)
    b = np.divide(num, den, out=np.zeros_like(num), where=den > 0)
    b = np.clip(b, -0.999, 0.999)[:, None]        # (W,1)
    last = d[:, -1:]                               # (W,1)
    cur = contexts[:, -1:]

    k = np.arange(1, horizon + 1, dtype=float)[None, :]   # (1,h)
    # cumulative expected return to each horizon
    geom = b * (1.0 - b ** k) / (1.0 - b)         # sum_{j=1..k} b^j, (W,h)
    cumret = mu * k + (last - mu) * geom
    return cur + cumret


# --------------------------------------------------------------------------- #
# Model forecasts (GPU) — batched decode_forward
# --------------------------------------------------------------------------- #
def model_paths(model, contexts: np.ndarray, horizon: int = HORIZON,
                eval_batch_size: int = 256):
    """Run the (LoRA or base) TimesFM model over windows.

    Returns (mean_path (W, horizon), quantile_path (W, horizon, K)) in normalized
    space. Imports torch lazily so the module stays importable on CPU-only boxes.
    """
    import torch

    from finetune.trainer import decode_forward

    device = next(model.parameters()).device
    means, quants = [], []
    model.eval()
    for i in range(0, len(contexts), eval_batch_size):
        batch = torch.tensor(contexts[i:i + eval_batch_size], dtype=torch.float32,
                             device=device)
        with torch.no_grad():
            m, q = decode_forward(model, batch, horizon)
        means.append(m.cpu().numpy())
        quants.append(q.cpu().numpy())
    if not means:
        return np.empty((0, horizon)), np.empty((0, horizon, len(QUANTILE_LEVELS)))
    return np.concatenate(means), np.concatenate(quants)


# --------------------------------------------------------------------------- #
# Assemble per-window arrays for one method across many tickers
# --------------------------------------------------------------------------- #
@dataclass
class MethodWindows:
    """Per-window arrays (concatenated across tickers) for one method/split/category."""
    ticker_id: np.ndarray          # (N,) block id for clustered bootstrap
    current_norm: np.ndarray       # (N,)
    future_norm: np.ndarray        # (N, horizon)
    pred_norm: np.ndarray          # (N, horizon) mean path
    current_price: np.ndarray      # (N,)
    future_price: np.ndarray       # (N, horizon)
    pred_price: np.ndarray         # (N, horizon)
    quantile_price: np.ndarray | None  # (N, horizon, K) or None
    per_ticker_scale: dict         # ticker_id -> MASE naive scale

    @property
    def n(self) -> int:
        return len(self.current_norm)

    @staticmethod
    def concat(parts: list["MethodWindows"]) -> "MethodWindows":
        """Concatenate windows (e.g. per-sector results) preserving row order.

        Row order is preserved so a per-sector composite stays window-aligned
        with a pooled / zero-shot run over the same ordered series (required for
        Diebold-Mariano). ticker_ids are offset to remain distinct across parts.
        """
        parts = [p for p in parts if p.n > 0]
        H = parts[0].future_norm.shape[1] if parts else HORIZON
        if not parts:
            e = np.empty(0)
            return MethodWindows(e, e, np.empty((0, H)), np.empty((0, H)),
                                 e, np.empty((0, H)), np.empty((0, H)), None, {})
        tids, scales, off = [], {}, 0
        for p in parts:
            tids.append(p.ticker_id + off)
            for t, sc in p.per_ticker_scale.items():
                scales[t + off] = sc
            off += int(p.ticker_id.max()) + 1
        quant = (np.concatenate([p.quantile_price for p in parts])
                 if all(p.quantile_price is not None for p in parts) else None)
        cat = lambda attr: np.concatenate([getattr(p, attr) for p in parts])
        return MethodWindows(
            ticker_id=np.concatenate(tids),
            current_norm=cat("current_norm"), future_norm=cat("future_norm"),
            pred_norm=cat("pred_norm"), current_price=cat("current_price"),
            future_price=cat("future_price"), pred_price=cat("pred_price"),
            quantile_price=quant, per_ticker_scale=scales,
        )


def assemble(eval_series: list[EvalSeries], predict_fn, horizon: int = HORIZON,
             stride: int | None = None, with_quantiles: bool = False) -> MethodWindows:
    """Build windows for every series, run ``predict_fn`` (returns mean path or
    (mean, quant)), and assemble normalized + price-space per-window arrays.

    ``predict_fn(contexts) -> pred_norm`` (baseline) or ``-> (pred_norm, quant_norm)``
    (model, when with_quantiles=True).
    """
    tid, cur_n, fut_n, pred_n = [], [], [], []
    cur_p, fut_p, pred_p, quant_p = [], [], [], []
    scales = {}
    for k, es in enumerate(eval_series):
        ctx, fut = build_windows(es.series_norm, horizon=horizon, stride=stride)
        if len(ctx) == 0:
            continue
        out = predict_fn(ctx)
        if with_quantiles:
            pred, quant = out
        else:
            pred, quant = out, None

        inv = lambda a: es.normalizer.inverse_transform(a, es.series_id)
        cur = ctx[:, -1]
        tid.append(np.full(len(ctx), k))
        cur_n.append(cur); fut_n.append(fut); pred_n.append(pred)
        cur_p.append(inv(cur)); fut_p.append(inv(fut)); pred_p.append(inv(pred))
        if quant is not None:
            quant_p.append(inv(quant))
        scales[k] = naive_scale(es.train_prices)

    if not tid:
        empty = np.empty(0)
        return MethodWindows(empty, empty, np.empty((0, horizon)), np.empty((0, horizon)),
                             empty, np.empty((0, horizon)), np.empty((0, horizon)),
                             None, {})
    return MethodWindows(
        ticker_id=np.concatenate(tid),
        current_norm=np.concatenate(cur_n),
        future_norm=np.concatenate(fut_n),
        pred_norm=np.concatenate(pred_n),
        current_price=np.concatenate(cur_p),
        future_price=np.concatenate(fut_p),
        pred_price=np.concatenate(pred_p),
        quantile_price=np.concatenate(quant_p) if quant_p else None,
        per_ticker_scale=scales,
    )


# --------------------------------------------------------------------------- #
# Scoring -> table rows + raw arrays for significance
# --------------------------------------------------------------------------- #
def directional_correct(mw: MethodWindows, h: int):
    """Per-window correctness (bool) and the contributing mask at horizon h."""
    pred_change = mw.pred_norm[:, h - 1] - mw.current_norm
    actual_change = mw.future_norm[:, h - 1] - mw.current_norm
    call = (pred_change != 0) & (actual_change != 0)
    correct = (np.sign(pred_change) == np.sign(actual_change)) & call
    return correct, call


def score_directional_trading(mw: MethodWindows, horizons=HORIZONS,
                              trade_h: int = HORIZON, cost_bps: float = 0.0,
                              seed: int = 0):
    """Table-A rows for one method/split/category (one row per horizon)."""
    rows = []
    for h in horizons:
        dpred = mw.pred_norm[:, h - 1] - mw.current_norm
        dact = mw.future_norm[:, h - 1] - mw.current_norm
        dm = directional_metrics(dpred, dact)

        # paired excess CI: model-correct minus always-up-correct on shared windows
        call = (dpred != 0) & (dact != 0)
        model_ok = (np.sign(dpred) == np.sign(dact))[call].astype(float)
        alwaysup_ok = (dact[call] > 0).astype(float)
        ci = block_bootstrap_ci(model_ok - alwaysup_ok, mw.ticker_id[call],
                                seed=seed) if call.any() else {"lo": np.nan, "hi": np.nan}

        trade = trading_metrics(dpred, mw.current_price,
                                mw.future_price[:, h - 1], horizon=h,
                                cost_bps=cost_bps)

        # Sharpe CI: block-bootstrap per-trade returns, clustered by ticker
        signal = np.sign(dpred)
        traded = signal != 0
        if int(traded.sum()) > 1:
            mret = mw.future_price[:, h - 1] / np.where(
                mw.current_price == 0, np.nan, mw.current_price) - 1.0
            sc = block_bootstrap_ci((signal * mret)[traded], mw.ticker_id[traded],
                                    statistic=lambda r: _sharpe(r, h), seed=seed)
            sharpe_ci = (sc["lo"], sc["hi"])
        else:
            sharpe_ci = (float("nan"), float("nan"))

        rows.append({
            "horizon": h, "n_windows": dm["n_windows"], "n_trades": trade["n_trades"],
            "acc": dm["acc"], "always_up_acc": dm["always_up_acc"],
            "excess_acc": dm["excess_acc"],
            "excess_acc_ci": (ci["lo"], ci["hi"]),
            "balanced_acc": dm["balanced_acc"], "mcc": dm["mcc"],
            "sharpe": trade["sharpe"], "sharpe_net": trade["sharpe_net"],
            "sharpe_ci": sharpe_ci,
            "max_drawdown": trade["max_drawdown"], "hit_rate": trade["hit_rate"],
        })
    return rows


def score_point(mw: MethodWindows, horizon: int = HORIZON):
    """Table-B row: point metrics per ticker then macro-averaged."""
    per = []
    for tid, scale in mw.per_ticker_scale.items():
        m = mw.ticker_id == tid
        if not m.any():
            continue
        per.append(point_metrics(mw.future_price[m].ravel(),
                                 mw.pred_price[m].ravel(), scale=scale))
    out = macro_average(per)
    out["n_windows"] = mw.n            # window count (distinct from n = #points)
    return out


def score_calibration(mw: MethodWindows, levels=QUANTILE_LEVELS):
    """Table-C rows from the quantile head (None if baseline has no quantiles)."""
    if mw.quantile_price is None or mw.n == 0:
        return None, np.nan
    y = mw.future_price.ravel()                       # (N*horizon,)
    q = mw.quantile_price.reshape(-1, len(levels))    # (N*horizon, K)
    return calibration_table(y, q, levels)


def squared_error_at(mw: MethodWindows, h: int) -> np.ndarray:
    """Per-window squared forecast error at horizon h, in NORMALIZED (log-z)
    space, for the Diebold-Mariano test.

    Using normalized errors instead of price-space errors keeps the DM loss
    differential numerically stable at long horizons. The inverse transform is
    ``price = exp(z*std + mean)``, so a price-space squared error grows
    exponentially in the normalized error; at h=128 a few windows then dominate
    the Newey-West long-run variance and the DM statistic blows up to ~1e10
    (observed in the first Nasdaq-100 run). The normalized error is the
    per-series-standardized log-price error — monotone and sign-preserving — and
    both methods in a DM pair share the same per-window normalizer, so the paired
    differential remains valid.
    """
    return (mw.pred_norm[:, h - 1] - mw.future_norm[:, h - 1]) ** 2
