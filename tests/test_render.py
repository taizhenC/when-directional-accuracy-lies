"""Tests for scripts/render_tables.py (CPU, synthetic payload)."""

from scripts.render_tables import aggregate, render


def test_aggregate_mean_and_sum():
    rows = [
        {"method": "pooled", "split": "seen", "horizon": 2, "acc": 0.6, "n_windows": 10},
        {"method": "pooled", "split": "seen", "horizon": 2, "acc": 0.4, "n_windows": 5},
    ]
    out = aggregate(rows, ["method", "split", "horizon"],
                    sum_fields=["n_windows"], mean_fields=["acc"])
    assert len(out) == 1
    assert out[0]["acc"] == 0.5 and out[0]["n_windows"] == 15


def _payload():
    return {
        "version": "vX", "smoke": True, "folds": [{}],
        "tables": {
            "A": [{"method": "per_sector", "split": "held_out", "category": "stock",
                   "horizon": 128, "n_windows": 50, "n_trades": 50, "acc": 0.55,
                   "always_up_acc": 0.54, "excess_acc": 0.01, "balanced_acc": 0.52,
                   "mcc": 0.03, "sharpe": 0.2, "sharpe_net": 0.1,
                   "max_drawdown": -0.1, "hit_rate": 0.55}],
            "B": [{"method": "per_sector", "split": "held_out", "category": "stock",
                   "n": 6400, "n_windows": 50, "MAE": 1.2, "RMSE": 2.0,
                   "sMAPE": 0.3, "MASE": 1.1}],
            "C": [{"method": "per_sector", "split": "held_out", "category": "stock",
                   "quantile_level": 0.1, "nominal": 0.1, "empirical_coverage": 0.12,
                   "pinball": 0.5}],
            "D": [{"comparison": "per_sector vs pooled", "split": "held_out",
                   "category": "stock", "horizon": 128, "test": "diebold_mariano",
                   "statistic": -1.2, "p": 0.2, "primary": True,
                   "fdr_adjusted": None, "fdr_reject": False, "n": 50},
                  {"comparison": "pooled vs zero_shot", "split": "held_out",
                   "category": "stock", "horizon": 128, "test": "diebold_mariano",
                   "statistic": -0.5, "p": 0.6, "primary": False,
                   "fdr_adjusted": 0.6, "fdr_reject": False, "n": 50}],
        },
    }


def test_render_contains_all_tables_and_flags_primary():
    md = render(_payload())
    for header in ("Table A", "Table B", "Table C", "Table D"):
        assert header in md
    assert "★ per_sector vs pooled" in md      # primary test flagged
    assert "always_up_acc" in md               # base-rate column present
