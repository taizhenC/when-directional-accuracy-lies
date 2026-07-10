"""Load a frozen price artifact written by ``scripts/freeze_data.py``.

Drop-in replacement for ``finetune.data_collector.fetch_market_data*``: returns
``list[(ticker, pd.Series)]`` with a DatetimeIndex, so the training / benchmark
pipeline consumes frozen, reproducible data instead of live yfinance.

Artifact layout (``data/frozen/<version>/``):
    prices.parquet | prices.csv.gz   tidy: date, ticker, adjusted_close
    universe.json                    provenance + per-ticker {sector, category, ...}
    environment.json                 python + package versions
    requirements_freeze.txt          pip freeze
"""

from __future__ import annotations

import hashlib
import json
import os

import pandas as pd

from finetune.data_collector import SECTOR_TO_ETF

DEFAULT_ROOT = os.path.join("data", "frozen")


# --------------------------------------------------------------------------- #
# Low-level helpers
# --------------------------------------------------------------------------- #
def _price_path(version_dir: str) -> str:
    for name in ("prices.parquet", "prices.csv.gz"):
        p = os.path.join(version_dir, name)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"no prices.parquet / prices.csv.gz under {version_dir}")


def _read_price_table(path: str) -> pd.DataFrame:
    df = pd.read_parquet(path) if path.endswith(".parquet") \
        else pd.read_csv(path, compression="gzip")
    df["date"] = pd.to_datetime(df["date"])
    return df


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def latest_version(root: str = DEFAULT_ROOT) -> str:
    if not os.path.isdir(root):
        raise FileNotFoundError(f"frozen-data root does not exist: {root}")
    dirs = [d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))]
    if not dirs:
        raise FileNotFoundError(f"no frozen versions under {root}")
    return sorted(dirs)[-1]


def load_meta(version: str | None = None, root: str = DEFAULT_ROOT):
    """Return (meta_dict, version_dir)."""
    version = version or latest_version(root)
    version_dir = os.path.join(root, version)
    with open(os.path.join(version_dir, "universe.json")) as f:
        return json.load(f), version_dir


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def _records_from_df(df: pd.DataFrame, keep: set | None = None):
    out = []
    for ticker, g in df.groupby("ticker", sort=True):
        if keep is not None and ticker not in keep:
            continue
        g = g.sort_values("date")
        s = pd.Series(
            g["adjusted_close"].to_numpy(dtype=float),
            index=pd.DatetimeIndex(g["date"].to_numpy()),
            name=ticker,
        )
        out.append((ticker, s))
    return out


def load_frozen(version: str | None = None, root: str = DEFAULT_ROOT,
                verify: bool = True):
    """Load all frozen series.

    Returns (records, meta) where records = list[(ticker, pd.Series)].
    Verifies the price file's sha256 against ``universe.json`` (guards silent
    data drift); pass ``verify=False`` to skip.
    """
    meta, version_dir = load_meta(version, root)
    path = _price_path(version_dir)
    if verify:
        expected = meta.get("price_file_sha256")
        actual = sha256_file(path)
        if expected and expected != actual:
            raise ValueError(
                f"checksum mismatch for {path}:\n  expected {expected}\n  actual   {actual}"
            )
    df = _read_price_table(path)
    return _records_from_df(df), meta


def load_frozen_by_sector(sector: str, version: str | None = None,
                          root: str = DEFAULT_ROOT, include_etf: bool = True,
                          verify: bool = True):
    """Frozen series for one GICS sector (+ its SPDR ETF anchor if include_etf).

    Mirrors ``data_collector.fetch_market_data_by_sector`` but from frozen data.
    """
    records, meta = load_frozen(version, root, verify)
    tinfo = meta["tickers"]
    keep = {
        t for t, info in tinfo.items()
        if info["sector"] == sector and (include_etf or info["category"] == "stock")
    }
    if include_etf and sector in SECTOR_TO_ETF:
        keep.add(SECTOR_TO_ETF[sector])
    return [(t, s) for (t, s) in records if t in keep]


def ticker_to_sector(meta: dict, category: str | None = None) -> dict:
    """ticker -> sector map from a loaded ``meta``. ``category`` filters to
    'stock' or 'etf' (None = both). Use ``category='stock'`` for holdout_split.
    """
    return {
        t: info["sector"]
        for t, info in meta["tickers"].items()
        if category is None or info["category"] == category
    }
