"""Walk-forward time folds + per-sector held-out ticker split.

Two orthogonal split dimensions for the paper-grade benchmark:

1. Time (walk-forward, expanding): each fold is **train -> validation -> test**.
   Validation is the ONLY signal for early stopping / model selection; the test
   window is never used for selection (fixes the leak in the old `main.py`,
   which early-stopped on the evaluation window).

2. Symbol (held-out tickers): a per-sector stratified seen/held-out partition,
   seeded and fixed across folds, so held-out tickers are never trained in any
   fold. ETFs are anchors handled by the caller and always treated as 'seen'
   (reported as their own category).

Everything here is pure (numpy/pandas only) so it runs in CPU unit tests.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

__all__ = [
    "Fold",
    "walk_forward_folds",
    "HoldoutSplit",
    "holdout_split",
    "values_between",
    "train_val_test",
]


# --------------------------------------------------------------------------- #
# Time dimension: walk-forward folds
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Fold:
    """One walk-forward fold. Dates are ISO 'YYYY-MM-DD', half-open intervals.

    train = [data_start, train_end)
    val   = [train_end,  val_end)
    test  = [val_end,    test_end)      (test_start == val_end)
    """

    index: int
    data_start: str
    train_end: str
    val_end: str
    test_end: str

    @property
    def test_start(self) -> str:
        return self.val_end

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "data_start": self.data_start,
            "train_end": self.train_end,
            "val_end": self.val_end,
            "test_start": self.test_start,
            "test_end": self.test_end,
        }


def _iso(ts: pd.Timestamp) -> str:
    return ts.strftime("%Y-%m-%d")


def walk_forward_folds(
    data_start: str = "2005-01-01",
    final_end: str = "2026-01-01",
    n_folds: int = 3,
    val_years: int = 1,
    test_years: int = 2,
    expanding: bool = True,
    train_years: int | None = None,
) -> list[Fold]:
    """Expanding (or rolling) walk-forward folds.

    Tiles the most recent ``n_folds * test_years`` years with **non-overlapping
    test windows** ending at ``final_end``. Each fold reserves ``val_years``
    immediately before its test window for validation; training is everything
    before that.

    For data_start=2005, final_end=2026, n_folds=3, val_years=1, test_years=2::

        fold 0: train 2005-2019 | val 2019-2020 | test 2020-2022
        fold 1: train 2005-2021 | val 2021-2022 | test 2022-2024
        fold 2: train 2005-2023 | val 2023-2024 | test 2024-2026

    expanding=True  -> train starts at data_start every fold.
    expanding=False -> rolling train window of ``train_years`` (required).
    """
    start = pd.Timestamp(data_start)
    end = pd.Timestamp(final_end)
    if not expanding and train_years is None:
        raise ValueError("rolling folds (expanding=False) require train_years")

    first_test_start = end - pd.DateOffset(years=n_folds * test_years)
    if first_test_start - pd.DateOffset(years=val_years) <= start:
        raise ValueError(
            "not enough history: data_start is too close to the first val window "
            f"(first val starts {_iso(first_test_start - pd.DateOffset(years=val_years))}, "
            f"data starts {_iso(start)})"
        )

    folds: list[Fold] = []
    for k in range(n_folds):
        test_start = first_test_start + pd.DateOffset(years=k * test_years)
        test_end = test_start + pd.DateOffset(years=test_years)
        val_end = test_start
        train_end = val_end - pd.DateOffset(years=val_years)
        fold_start = (
            start if expanding else train_end - pd.DateOffset(years=train_years)
        )
        folds.append(
            Fold(
                index=k,
                data_start=_iso(fold_start),
                train_end=_iso(train_end),
                val_end=_iso(val_end),
                test_end=_iso(test_end),
            )
        )
    return folds


# --------------------------------------------------------------------------- #
# Symbol dimension: per-sector held-out tickers
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class HoldoutSplit:
    """Per-sector seen/held-out partition (stocks only)."""

    seed: int
    holdout_frac: float
    by_sector: dict  # sector -> {"seen": [...], "held_out": [...]}

    def seen_set(self) -> set:
        return {t for v in self.by_sector.values() for t in v["seen"]}

    def held_out_set(self) -> set:
        return {t for v in self.by_sector.values() for t in v["held_out"]}

    def split_of(self, ticker: str) -> str:
        """Return 'held_out' if the ticker is held out, else 'seen'."""
        return "held_out" if ticker in self.held_out_set() else "seen"

    def sectors_without_holdout(self) -> list[str]:
        """Sectors too small to reserve a held-out set (flagged for wider CIs)."""
        return [s for s, v in self.by_sector.items() if not v["held_out"]]

    def to_dict(self) -> dict:
        return {
            "seed": self.seed,
            "holdout_frac": self.holdout_frac,
            "by_sector": {s: dict(v) for s, v in self.by_sector.items()},
        }


def holdout_split(
    ticker_to_sector: dict,
    holdout_frac: float = 0.2,
    seed: int = 42,
    min_holdout: int = 2,
    min_seen: int = 2,
) -> HoldoutSplit:
    """Per-sector stratified seen/held-out partition (stocks only).

    Deterministic: within each sector, tickers are **sorted then shuffled** with
    a seeded RNG, so the split depends only on (ticker set, seed) — never on
    input order. Each sector holds out ``ceil(holdout_frac * n)`` names, clamped
    so both sides keep at least ``min_seen`` / ``min_holdout``. Sectors too small
    to satisfy both keep everything as 'seen' (see ``sectors_without_holdout``).

    ETFs must NOT be passed here — they are anchors, always 'seen', and reported
    as their own category.
    """
    rng = np.random.default_rng(seed)

    by_sector_tickers: dict[str, list[str]] = {}
    for ticker, sector in ticker_to_sector.items():
        by_sector_tickers.setdefault(sector, []).append(ticker)

    by_sector: dict[str, dict] = {}
    for sector in sorted(by_sector_tickers):
        names = sorted(by_sector_tickers[sector])
        n = len(names)
        if n < min_holdout + min_seen:
            n_hold = 0
        else:
            n_hold = math.ceil(holdout_frac * n)
            n_hold = max(n_hold, min_holdout)
            n_hold = min(n_hold, n - min_seen)
        perm = rng.permutation(n)
        hold_idx = set(int(i) for i in perm[:n_hold])
        held = sorted(names[i] for i in range(n) if i in hold_idx)
        seen = sorted(names[i] for i in range(n) if i not in hold_idx)
        by_sector[sector] = {"seen": seen, "held_out": held}

    return HoldoutSplit(seed=seed, holdout_frac=holdout_frac, by_sector=by_sector)


# --------------------------------------------------------------------------- #
# Date slicing helpers (used by the benchmark to realise a fold on a series)
# --------------------------------------------------------------------------- #
def values_between(series: pd.Series, start=None, end=None) -> np.ndarray:
    """Values of a DatetimeIndex-ed series on the half-open interval [start, end)."""
    idx = series.index
    mask = np.ones(len(series), dtype=bool)
    if start is not None:
        mask &= idx >= pd.Timestamp(start)
    if end is not None:
        mask &= idx < pd.Timestamp(end)
    return series.values[mask]


def train_val_test(series: pd.Series, fold: Fold):
    """Return (train, val, test) raw value arrays for a fold (half-open slices)."""
    train = values_between(series, fold.data_start, fold.train_end)
    val = values_between(series, fold.train_end, fold.val_end)
    test = values_between(series, fold.val_end, fold.test_end)
    return train, val, test
