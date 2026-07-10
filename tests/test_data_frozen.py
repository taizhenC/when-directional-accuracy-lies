"""Round-trip / checksum / sector-filter tests for finetune/data_frozen.py.

Uses a tiny synthetic artifact in tmp_path — no network, no real fetch.
"""

import json

import numpy as np
import pandas as pd
import pytest

from finetune import data_frozen


def _make_artifact(tmp_path, tickers):
    """tickers: {ticker: (sector, category, n_obs)} -> writes data/frozen/v1/."""
    version_dir = tmp_path / "v1"
    version_dir.mkdir()
    rows, tinfo = [], {}
    for t, (sector, category, n) in tickers.items():
        idx = pd.date_range("2005-01-03", periods=n, freq="B")
        vals = 100.0 + np.arange(n, dtype=float)
        rows += [{"date": d.strftime("%Y-%m-%d"), "ticker": t,
                  "adjusted_close": float(v)} for d, v in zip(idx, vals)]
        tinfo[t] = {"sector": sector, "category": category,
                    "start": idx.min().strftime("%Y-%m-%d"),
                    "end": idx.max().strftime("%Y-%m-%d"), "n_obs": n}
    df = pd.DataFrame(rows).sort_values(["ticker", "date"])
    price_path = version_dir / "prices.csv.gz"
    df.to_csv(price_path, index=False, compression="gzip")
    sha = data_frozen.sha256_file(str(price_path))
    universe = {"version": "v1", "price_file": "prices.csv.gz",
                "price_file_sha256": sha, "tickers": tinfo}
    (version_dir / "universe.json").write_text(json.dumps(universe))
    return str(tmp_path)


@pytest.fixture
def root(tmp_path):
    return _make_artifact(tmp_path, {
        "AAPL": ("tech", "stock", 300),
        "XLK": ("tech", "etf", 300),
        "JPM": ("financials", "stock", 300),
    })


def test_round_trip(root):
    records, meta = data_frozen.load_frozen("v1", root=root)
    assert [t for t, _ in records] == ["AAPL", "JPM", "XLK"]   # sorted
    for _, s in records:
        assert len(s) == 300
        assert isinstance(s.index, pd.DatetimeIndex)
        assert s.index.is_monotonic_increasing
        assert s.iloc[0] == 100.0 and s.iloc[-1] == 399.0
    assert meta["tickers"]["XLK"]["category"] == "etf"


def test_checksum_mismatch_raises(root, tmp_path):
    bad = json.loads((tmp_path / "v1" / "universe.json").read_text())
    bad["price_file_sha256"] = "0" * 64
    (tmp_path / "v1" / "universe.json").write_text(json.dumps(bad))
    with pytest.raises(ValueError, match="checksum mismatch"):
        data_frozen.load_frozen("v1", root=root)
    # but verify=False bypasses the guard
    records, _ = data_frozen.load_frozen("v1", root=root, verify=False)
    assert len(records) == 3


def test_load_by_sector_includes_etf_anchor(root):
    tech = data_frozen.load_frozen_by_sector("tech", "v1", root=root,
                                             include_etf=True)
    assert sorted(t for t, _ in tech) == ["AAPL", "XLK"]
    tech_no_etf = data_frozen.load_frozen_by_sector("tech", "v1", root=root,
                                                    include_etf=False)
    assert [t for t, _ in tech_no_etf] == ["AAPL"]


def test_ticker_to_sector_category_filter(root):
    _, meta = data_frozen.load_frozen("v1", root=root)
    stocks = data_frozen.ticker_to_sector(meta, category="stock")
    assert stocks == {"AAPL": "tech", "JPM": "financials"}   # XLK (etf) excluded
