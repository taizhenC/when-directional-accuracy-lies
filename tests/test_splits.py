"""Unit tests for finetune/splits.py (CPU, pure)."""

import numpy as np
import pandas as pd
import pytest

from finetune.splits import (
    holdout_split,
    train_val_test,
    walk_forward_folds,
)


# ----------------------------- time folds -------------------------------- #
def test_default_folds_dates_and_ordering():
    folds = walk_forward_folds("2005-01-01", "2026-01-01",
                               n_folds=3, val_years=1, test_years=2)
    assert len(folds) == 3
    f0, f1, f2 = folds
    assert (f0.data_start, f0.train_end, f0.val_end, f0.test_end) == \
        ("2005-01-01", "2019-01-01", "2020-01-01", "2022-01-01")
    assert f2.test_end == "2026-01-01"
    # test_start == val_end, and within each fold train < val < test
    for f in folds:
        assert f.test_start == f.val_end
        assert f.train_end < f.val_end < f.test_end


def test_test_windows_non_overlapping_and_chronological():
    folds = walk_forward_folds("2005-01-01", "2026-01-01")
    starts = [f.test_start for f in folds]
    ends = [f.test_end for f in folds]
    assert starts == sorted(starts)
    for i in range(len(folds) - 1):
        assert ends[i] <= starts[i + 1]   # no overlap


def test_expanding_train_start_is_constant():
    folds = walk_forward_folds("2005-01-01", "2026-01-01", expanding=True)
    assert {f.data_start for f in folds} == {"2005-01-01"}


def test_not_enough_history_raises():
    # first val window would start 2019-01-01, before data_start -> no train room
    with pytest.raises(ValueError):
        walk_forward_folds("2019-06-01", "2026-01-01", n_folds=3, test_years=2)


# ----------------------------- holdout ----------------------------------- #
def _toy_universe():
    # tech: 10 names, energy: 3 names (small), materials: 1 name (tiny)
    t2s = {}
    for i in range(10):
        t2s[f"TECH{i}"] = "tech"
    for i in range(3):
        t2s[f"NRG{i}"] = "energy"
    t2s["MAT0"] = "materials"
    return t2s


def test_holdout_deterministic_and_disjoint():
    t2s = _toy_universe()
    a = holdout_split(t2s, holdout_frac=0.2, seed=42)
    b = holdout_split(t2s, holdout_frac=0.2, seed=42)
    assert a.to_dict() == b.to_dict()                # reproducible
    assert a.seen_set().isdisjoint(a.held_out_set())  # disjoint
    assert a.seen_set() | a.held_out_set() == set(t2s)


def test_holdout_independent_of_input_order():
    t2s = _toy_universe()
    shuffled = dict(reversed(list(t2s.items())))
    assert holdout_split(t2s, seed=7).to_dict() == \
        holdout_split(shuffled, seed=7).to_dict()


def test_holdout_stratified_counts():
    t2s = _toy_universe()
    s = holdout_split(t2s, holdout_frac=0.2, seed=1)
    # tech (n=10): ceil(0.2*10)=2 held out
    assert len(s.by_sector["tech"]["held_out"]) == 2
    # materials (n=1) too small -> no held out; flagged
    assert s.by_sector["materials"]["held_out"] == []
    assert "materials" in s.sectors_without_holdout()


def test_different_seed_changes_split():
    t2s = _toy_universe()
    assert holdout_split(t2s, seed=1).to_dict() != \
        holdout_split(t2s, seed=2).to_dict()


# --------------------------- series slicing ------------------------------ #
def test_train_val_test_half_open_slicing():
    idx = pd.date_range("2005-01-01", "2026-01-01", freq="D")
    series = pd.Series(np.arange(len(idx), dtype=float), index=idx)
    folds = walk_forward_folds("2005-01-01", "2026-01-01")
    tr, va, te = train_val_test(series, folds[0])
    # train ends before 2019, val [2019,2020), test [2020,2022)
    assert series.index[len(tr) - 1] < pd.Timestamp("2019-01-01")
    n_val = ((series.index >= "2019-01-01") & (series.index < "2020-01-01")).sum()
    assert len(va) == n_val
    n_test = ((series.index >= "2020-01-01") & (series.index < "2022-01-01")).sum()
    assert len(te) == n_test
