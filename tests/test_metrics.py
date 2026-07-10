"""Known-answer unit tests for finetune/metrics.py (CPU, no torch)."""

import math

import numpy as np
import pytest

from finetune.metrics import (
    benjamini_hochberg,
    block_bootstrap_ci,
    calibration_table,
    diebold_mariano,
    directional_metrics,
    macro_average,
    mcnemar_test,
    naive_scale,
    point_metrics,
    trading_metrics,
)
from finetune.metrics import _sharpe  # private, tested directly


# ----------------------------- directional ------------------------------- #
def test_always_up_predictor_has_zero_excess():
    # A model that always predicts up: acc == base rate, so excess == 0 exactly.
    pred = np.array([1, 1, 1, 1, 1.0])
    actual = np.array([1, -1, 1, 1, -1.0])  # 3 up / 2 down
    m = directional_metrics(pred, actual)
    assert m["n_windows"] == 5
    assert m["acc"] == pytest.approx(0.6)
    assert m["always_up_acc"] == pytest.approx(0.6)
    assert m["excess_acc"] == pytest.approx(0.0, abs=1e-12)


def test_perfect_direction_has_positive_excess_and_unit_mcc():
    actual = np.array([1, -1, 2, -3, 1.0])
    pred = np.array([0.5, -0.2, 1, -1, 0.3])  # same signs as actual
    m = directional_metrics(pred, actual)
    assert m["acc"] == pytest.approx(1.0)
    assert m["always_up_acc"] == pytest.approx(0.6)
    assert m["excess_acc"] == pytest.approx(0.4)
    assert m["balanced_acc"] == pytest.approx(1.0)
    assert m["mcc"] == pytest.approx(1.0)


def test_random_walk_no_call_excluded():
    # pred_change all zero -> no directional calls -> n_windows == 0
    m = directional_metrics(np.zeros(4), np.array([1, -1, 1, -1.0]))
    assert m["n_windows"] == 0
    assert math.isnan(m["acc"])


# ------------------------------- point ----------------------------------- #
def test_point_metrics_perfect():
    y = np.array([1.0, 2.0, 3.0])
    m = point_metrics(y, y, scale=2.0)
    assert m["MAE"] == 0 and m["RMSE"] == 0
    assert m["sMAPE"] == pytest.approx(0.0)
    assert m["MASE"] == pytest.approx(0.0)


def test_point_metrics_known_values():
    y_true = np.array([1.0, 2.0, 3.0])
    y_pred = np.array([1.0, 2.0, 4.0])
    m = point_metrics(y_true, y_pred, scale=2.0)
    assert m["MAE"] == pytest.approx(1 / 3)
    assert m["RMSE"] == pytest.approx(math.sqrt(1 / 3))
    assert m["sMAPE"] == pytest.approx(2 / 21)         # 2*1/(3+4) over 3 windows
    assert m["MASE"] == pytest.approx((1 / 3) / 2.0)


def test_naive_scale():
    assert naive_scale([10, 11, 9, 12]) == pytest.approx(2.0)  # mean(|1,2,3|)


def test_macro_average_nanmean_and_sum():
    a = {"MAE": 1.0, "n_windows": 10}
    b = {"MAE": 3.0, "n_windows": 5}
    out = macro_average([a, b])
    assert out["MAE"] == pytest.approx(2.0)
    assert out["n_windows"] == 15


# --------------------------- calibration --------------------------------- #
def test_calibration_well_calibrated_normal():
    rng = np.random.default_rng(0)
    n = 40000
    y = rng.standard_normal(n)
    levels = [0.1, 0.5, 0.9]
    from scipy.stats import norm
    preds = np.column_stack([np.full(n, norm.ppf(q)) for q in levels])
    rows, crps = calibration_table(y, preds, levels)
    for r in rows:
        assert r["empirical_coverage"] == pytest.approx(r["nominal"], abs=0.02)
    assert crps > 0


# ----------------------------- trading ----------------------------------- #
def test_trading_all_correct_positive_sharpe():
    cur = np.array([100.0, 100.0])
    fut = np.array([110.0, 80.0])          # +10%, -20%
    pred = np.array([1.0, -1.0])           # long then short -> both win
    m = trading_metrics(pred, cur, fut, horizon=1)
    assert m["n_trades"] == 2
    assert m["hit_rate"] == pytest.approx(1.0)
    assert m["sharpe"] > 0
    assert m["max_drawdown"] <= 0.0


def test_max_drawdown_bounded_under_short_blowup():
    # A short whose underlying triples => per-trade return -200%. The OLD
    # cumprod(1+r) curve flips sign and explodes (<<-1); the floor keeps the
    # drawdown in [-1, 0].
    from finetune.metrics import _max_drawdown
    returns = np.array([0.05, -2.0, 0.03, -1.5, 0.02])   # two sub -100% trades
    dd = _max_drawdown(returns)
    assert np.isfinite(dd)
    assert -1.0 <= dd <= 0.0


def test_max_drawdown_known_value():
    from finetune.metrics import _max_drawdown
    # +20% then -50%: equity 1 -> 1.2 -> 0.6; peak 1.2 -> drawdown -0.5.
    assert _max_drawdown(np.array([0.2, -0.5])) == pytest.approx(-0.5)
    # all gains -> no drawdown
    assert _max_drawdown(np.array([0.1, 0.1, 0.1])) == pytest.approx(0.0)


def test_point_metrics_drops_nonfinite_predictions():
    # A divergent forecast can reconstruct to +inf via exp(); it must not poison
    # the error (the finite pairs decide it), and an all-inf case is NaN, not inf.
    y = np.array([1.0, 2.0, 3.0])
    p = np.array([1.0, 2.0, np.inf])
    m = point_metrics(y, p, scale=2.0)
    assert m["n"] == 2 and m["MAE"] == pytest.approx(0.0)
    allbad = point_metrics(y, np.full(3, np.inf), scale=2.0)
    assert allbad["n"] == 0 and math.isnan(allbad["MAE"])


def test_trading_no_trade_when_signal_zero():
    m = trading_metrics(np.zeros(3), np.array([1.0, 1, 1]),
                        np.array([2.0, 2, 2]), horizon=1)
    assert m["n_trades"] == 0
    assert math.isnan(m["sharpe"])


def test_sharpe_formula():
    r = np.array([0.01, -0.005, 0.02])
    h = 5
    expected = r.mean() / r.std(ddof=1) * math.sqrt(252.0 / h)
    assert _sharpe(r, h) == pytest.approx(expected)


# --------------------------- significance -------------------------------- #
def test_mcnemar_symmetric_is_insignificant():
    model = np.array([True, False, True, False])
    base = np.array([False, True, False, True])  # b == c == 2
    res = mcnemar_test(model, base)
    assert res["b"] == 2 and res["c"] == 2
    assert res["p"] == pytest.approx(1.0)


def test_mcnemar_model_strictly_better_is_significant():
    n = 20
    model = np.ones(n, dtype=bool)
    base = np.zeros(n, dtype=bool)
    res = mcnemar_test(model, base)
    assert res["p"] < 1e-3


def test_block_bootstrap_constant():
    vals = np.full(50, 0.1)
    ids = np.arange(50)
    ci = block_bootstrap_ci(vals, ids, n_boot=200, seed=1)
    assert ci["point"] == pytest.approx(0.1)
    assert ci["lo"] == pytest.approx(0.1) and ci["hi"] == pytest.approx(0.1)


def test_diebold_mariano_sign_and_equal():
    rng = np.random.default_rng(3)
    base_loss = rng.random(200) + 1.0
    model_loss = base_loss - 0.5            # model uniformly better
    dm = diebold_mariano(model_loss, base_loss, horizon=1)
    assert dm["statistic"] < 0 and dm["p"] < 1e-6
    eq = diebold_mariano(base_loss, base_loss, horizon=1)
    assert eq["statistic"] == pytest.approx(0.0)
    assert eq["p"] == pytest.approx(1.0)


def test_dm_stable_when_horizon_exceeds_n():
    # Long horizon + small n (lag >> data) must NOT blow the statistic up via a
    # degenerate HAC variance floored to _EPS (the h=128, n~66 pathology).
    rng = np.random.default_rng(0)
    base = rng.random(40) + 1.0
    model = base + rng.normal(0, 0.01, 40)        # tiny, noisy loss difference
    dm = diebold_mariano(model, base, horizon=128)  # lag capped to n-2=38
    assert np.isfinite(dm["statistic"])
    assert abs(dm["statistic"]) < 1e3             # no degenerate-LRV explosion


def test_benjamini_hochberg_known():
    q, reject = benjamini_hochberg([0.001, 0.002, 0.003, 0.9], alpha=0.05)
    assert list(reject) == [True, True, True, False]
    assert q[0] == pytest.approx(0.004)

    q2, reject2 = benjamini_hochberg([1.0, 1.0, 1.0])
    assert not reject2.any()


def test_benjamini_hochberg_nan_passthrough():
    q, reject = benjamini_hochberg([0.01, np.nan, 0.9])
    assert math.isnan(q[1]) and not reject[1]
