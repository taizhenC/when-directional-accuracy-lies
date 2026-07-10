"""CPU tests for benchmark windowing, naive baselines, and metric assembly.

No torch / timesfm — uses a fake predictor and the real LogNormalizer.
"""

import numpy as np
import pytest

from finetune.benchmark import (
    CONTEXT_LEN,
    HORIZON,
    POINT_EXCLUDE,
    EvalSeries,
    MethodWindows,
    assemble,
    baseline_paths,
    build_windows,
    score_directional_trading,
    score_point,
    squared_error_at,
)
from finetune.data_prep import LogNormalizer


def _series_norm(n=CONTEXT_LEN + 2 * HORIZON, seed=0):
    rng = np.random.default_rng(seed)
    prices = 100.0 * np.exp(np.cumsum(rng.normal(0.0003, 0.01, size=n)))
    norm = LogNormalizer()
    s = norm.fit_transform(prices, series_id=0)
    return prices, norm, s


# ------------------------------ windowing -------------------------------- #
def test_build_windows_counts_and_shapes():
    _, _, s = _series_norm()
    ctx, fut = build_windows(s)                 # stride defaults to HORIZON
    assert ctx.shape == (2, CONTEXT_LEN)
    assert fut.shape == (2, HORIZON)
    # window 0 future is the segment right after its context
    assert np.allclose(fut[0], s[CONTEXT_LEN:CONTEXT_LEN + HORIZON])


def test_build_windows_empty_when_too_short():
    ctx, fut = build_windows(np.zeros(CONTEXT_LEN + HORIZON - 1))
    assert ctx.shape[0] == 0 and fut.shape[0] == 0


# ------------------------------ baselines -------------------------------- #
def test_always_up_predicts_up_everywhere():
    _, _, s = _series_norm()
    ctx, _ = build_windows(s)
    path = baseline_paths("always_up", ctx)
    change = path - ctx[:, -1:]
    assert (change > 0).all()


def test_random_walk_is_flat():
    _, _, s = _series_norm()
    ctx, _ = build_windows(s)
    path = baseline_paths("random_walk", ctx)
    assert np.allclose(path, ctx[:, -1:])        # no directional call


def test_persistence_follows_last_return_sign():
    ctx = np.array([[0.0, 1.0, 2.0, 2.5]])       # last return +0.5 -> up
    up = baseline_paths("persistence", ctx, horizon=3)
    assert (up - ctx[:, -1:] > 0).all()
    ctx2 = np.array([[0.0, 1.0, 2.0, 1.5]])      # last return -0.5 -> down
    down = baseline_paths("persistence", ctx2, horizon=3)
    assert (down - ctx2[:, -1:] < 0).all()


def test_ar1_shape_and_finite_and_drift():
    _, _, s = _series_norm()
    ctx, _ = build_windows(s)
    path = baseline_paths("ar1", ctx)
    assert path.shape == (ctx.shape[0], HORIZON)
    assert np.isfinite(path).all()
    # constant positive returns -> cumulative drift up
    drift = np.cumsum(np.full(CONTEXT_LEN, 0.1))[None, :]
    p = baseline_paths("ar1", drift, horizon=5)
    assert (p[:, -1] > drift[:, -1]).all()


# --------------------- assembly + scoring (CPU) -------------------------- #
def _eval_series(seed=0, split="seen"):
    prices, norm, s = _series_norm(seed=seed)
    return EvalSeries(ticker=f"T{seed}", sector="tech", category="stock",
                      split=split, series_norm=s, normalizer=norm, series_id=0,
                      train_prices=prices[:CONTEXT_LEN])


def test_assemble_price_inverse_roundtrips():
    es = _eval_series()
    mw = assemble([es], lambda c: baseline_paths("always_up", c))
    # price space must equal inverse-transform of normalized predictions
    assert np.allclose(mw.pred_price, es.normalizer.inverse_transform(mw.pred_norm, 0))
    assert mw.n == 2 and mw.quantile_price is None


def test_always_up_excess_is_zero_end_to_end():
    series = [_eval_series(seed=i) for i in range(8)]   # more windows
    mw = assemble(series, lambda c: baseline_paths("always_up", c))
    rows = {r["horizon"]: r for r in score_directional_trading(mw)}
    for h, r in rows.items():
        assert r["excess_acc"] == pytest.approx(0.0, abs=1e-9)
        assert r["n_trades"] == mw.n                    # always trades (long)


def test_random_walk_makes_no_trades():
    series = [_eval_series(seed=i) for i in range(4)]
    mw = assemble(series, lambda c: baseline_paths("random_walk", c))
    rows = score_directional_trading(mw)
    assert all(r["n_trades"] == 0 for r in rows)
    assert all(r["n_windows"] == 0 for r in rows)       # no directional call


def test_score_point_returns_macro_metrics():
    series = [_eval_series(seed=i) for i in range(4)]
    mw = assemble(series, lambda c: baseline_paths("random_walk", c))
    pt = score_point(mw)
    assert pt["MAE"] >= 0 and np.isfinite(pt["RMSE"])
    assert pt["n_windows"] == mw.n


# ------------- numerical-stability fixes (h=128 overflow) ---------------- #
def test_squared_error_uses_normalized_space_not_price():
    # DM loss must be computed in normalized (log-z) space so a price-space
    # explosion (exp() overflow at long horizon) can't blow up the statistic.
    H = 4
    n = 3
    pred_norm = np.zeros((n, H))
    future_norm = np.full((n, H), 0.5)
    mw = MethodWindows(
        ticker_id=np.arange(n), current_norm=np.zeros(n),
        future_norm=future_norm, pred_norm=pred_norm,
        current_price=np.full(n, 50.0),
        future_price=np.full((n, H), 50.0),
        pred_price=np.full((n, H), 1e30),   # exploded price space (would be 1e60)
        quantile_price=None, per_ticker_scale={})
    se = squared_error_at(mw, H)
    assert np.isfinite(se).all()
    assert np.allclose(se, 0.25)            # (0 - 0.5)^2, NOT 1e60


def test_persistence_excluded_from_point_table():
    assert "persistence" in POINT_EXCLUDE
