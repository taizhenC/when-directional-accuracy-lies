"""Freeze S&P 500 + SPDR sector ETF daily adjusted closes into a versioned
artifact, so every adapter trains/evaluates on identical, reproducible data.

Run once (CPU, needs network)::

    python -m scripts.freeze_data --start 2005-01-01 --end 2026-01-01

Writes ``data/frozen/<version>/``:
    prices.parquet | prices.csv.gz   tidy: date, ticker, adjusted_close
    universe.json                    ticker->{sector,category,...}, sha256, params
    environment.json                 python + package versions (Colab reproducibility)
    requirements_freeze.txt          full pip freeze

Price column is named **adjusted_close** (yfinance auto_adjust=True) — the single
price definition used everywhere downstream.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone

import pandas as pd

from finetune.data_collector import (
    SECTOR_TO_ETF,
    _fetch_tickers,
    _get_nasdaq100_with_sectors,
    _get_sp500_with_sectors,
)


def build_universe(universe: str):
    """Return ``(stock_pairs, etf_sector)`` for a named universe.

    stock_pairs : list[(ticker, sector_code)] — the trainable stock universe.
    etf_sector  : {etf_ticker: label}         — anchor ETF(s), stored as the
                  'etf' category (excluded from pooled training, reported on).
    """
    if universe == "sp500":
        pairs = _get_sp500_with_sectors()
        etf_sector = {etf: sec for sec, etf in SECTOR_TO_ETF.items()}
    elif universe == "nasdaq100":
        # Nasdaq-100 constituents; QQQ (the Nasdaq-100 ETF) as the index anchor.
        pairs = _get_nasdaq100_with_sectors()
        etf_sector = {"QQQ": "index"}
    else:
        raise ValueError(f"unknown universe: {universe!r} (use sp500|nasdaq100)")
    return pairs, etf_sector


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_price_table(df: pd.DataFrame, version_dir: str) -> str:
    """Prefer parquet (compact, typed); fall back to gzip-CSV if pyarrow absent."""
    try:
        import pyarrow  # noqa: F401

        path = os.path.join(version_dir, "prices.parquet")
        df.to_parquet(path, index=False)
    except Exception as e:
        path = os.path.join(version_dir, "prices.csv.gz")
        print(f"  [write] parquet unavailable ({e.__class__.__name__}); "
              f"writing gzip-CSV instead")
        df.to_csv(path, index=False, compression="gzip")
    return path


def _capture_environment(version_dir: str) -> dict:
    import importlib.metadata as im

    pkgs = {}
    for p in ["numpy", "pandas", "scipy", "yfinance", "requests",
              "torch", "peft", "timesfm", "pyarrow"]:
        try:
            pkgs[p] = im.version(p)
        except Exception:
            pkgs[p] = None
    env = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "packages": pkgs,
    }
    with open(os.path.join(version_dir, "environment.json"), "w") as f:
        json.dump(env, f, indent=2)
    try:
        out = subprocess.run([sys.executable, "-m", "pip", "freeze"],
                             capture_output=True, text=True, timeout=120)
        with open(os.path.join(version_dir, "requirements_freeze.txt"), "w") as f:
            f.write(out.stdout)
    except Exception as e:
        print(f"  [env] pip freeze failed: {e}")
    return env


def freeze(start: str, end: str, out_root: str, min_len: int,
           version: str | None = None, universe: str = "sp500") -> str:
    fetch_started = datetime.now(timezone.utc).isoformat()

    # 1. Universe: stocks + anchor ETF(s) for the requested index
    pairs, etf_sector = build_universe(universe)       # [(ticker, sector_code)], {etf: label}
    stock_sector = dict(pairs)
    all_tickers = sorted(set(stock_sector) | set(etf_sector))
    print(f"[freeze] universe={universe}: {len(stock_sector)} stocks + "
          f"{len(etf_sector)} ETFs = {len(all_tickers)} tickers")

    # 2. Fetch
    results, failed = _fetch_tickers(all_tickers, start, end, min_len)
    print(f"[freeze] fetched {len(results)} series ({failed} failed/too short)")
    if not results:
        raise RuntimeError("no series fetched — aborting freeze")

    # 3. Assemble tidy table + per-ticker provenance
    frames, tinfo = [], {}
    for ticker, series in results:
        series = series.sort_index().dropna()
        if series.empty:
            continue
        frames.append(pd.DataFrame({
            "date": series.index.strftime("%Y-%m-%d"),
            "ticker": ticker,
            "adjusted_close": series.to_numpy(dtype=float),
        }))
        tinfo[ticker] = {
            "sector": stock_sector.get(ticker) or etf_sector.get(ticker) or "unknown",
            "category": "etf" if ticker in etf_sector else "stock",
            "start": series.index.min().strftime("%Y-%m-%d"),
            "end": series.index.max().strftime("%Y-%m-%d"),
            "n_obs": int(len(series)),
        }
    df = (pd.concat(frames, ignore_index=True)
          .sort_values(["ticker", "date"]).reset_index(drop=True))

    # 4. Write artifact
    if version is None:
        fetch_day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        version = f"{universe}_{start}_{end}_f{fetch_day}"
    version_dir = os.path.join(out_root, version)
    os.makedirs(version_dir, exist_ok=True)

    price_path = _write_price_table(df, version_dir)
    sha = _sha256(price_path)
    env = _capture_environment(version_dir)

    n_stock = sum(1 for v in tinfo.values() if v["category"] == "stock")
    n_etf = sum(1 for v in tinfo.values() if v["category"] == "etf")
    sectors = sorted({v["sector"] for v in tinfo.values() if v["category"] == "stock"})

    universe_meta = {
        "version": version,
        "universe": universe,
        "source": "yfinance",
        "yfinance_params": {"auto_adjust": True, "start": start, "end": end,
                            "min_len": min_len},
        "fetch_started_at": fetch_started,
        "fetch_finished_at": datetime.now(timezone.utc).isoformat(),
        "price_file": os.path.basename(price_path),
        "price_file_sha256": sha,
        "n_tickers": len(tinfo),
        "n_stocks": n_stock,
        "n_etfs": n_etf,
        "sectors": sectors,
        "environment": env,
        "tickers": dict(sorted(tinfo.items())),
    }
    with open(os.path.join(version_dir, "universe.json"), "w") as f:
        json.dump(universe_meta, f, indent=2)

    print(f"[freeze] wrote {price_path} ({len(df):,} rows)")
    print(f"[freeze] sha256={sha[:16]}...  stocks={n_stock} etfs={n_etf} "
          f"sectors={len(sectors)}")
    print(f"[freeze] version dir: {version_dir}")
    return version_dir


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--universe", default="sp500", choices=["sp500", "nasdaq100"],
                    help="which index universe to freeze")
    ap.add_argument("--start", default="2005-01-01")
    ap.add_argument("--end", default="2026-01-01")
    ap.add_argument("--out-root", default=os.path.join("data", "frozen"))
    ap.add_argument("--min-len", type=int, default=252)
    ap.add_argument("--version", default=None, help="override version string")
    args = ap.parse_args()
    freeze(args.start, args.end, args.out_root, args.min_len, args.version,
           universe=args.universe)


if __name__ == "__main__":
    main()
