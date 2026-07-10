"""Fetch real market data via yfinance for fine-tuning."""

import io
import json
import os
import time

import pandas as pd
import requests
import yfinance as yf


# Ticker lists per asset class
EQUITY_TICKERS = None  # fetched dynamically from Wikipedia
FOREX_TICKERS = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X",
    "USDCHF=X", "NZDUSD=X", "EURGBP=X", "EURJPY=X", "GBPJPY=X",
    "AUDJPY=X", "EURAUD=X", "EURCHF=X", "AUDNZD=X", "NZDJPY=X",
    "GBPAUD=X", "GBPCAD=X", "EURNZD=X", "AUDCAD=X", "GBPCHF=X",
    "AUDCHF=X", "EURCAD=X", "CADJPY=X", "GBPNZD=X", "CADCHF=X",
    "CHFJPY=X", "NZDCAD=X", "NZDCHF=X", "SGDJPY=X", "HKDJPY=X",
]
MACRO_TICKERS = [
    # Sector ETFs
    "XLF", "XLK", "XLE", "XLV", "XLI", "XLP", "XLU", "XLB", "XLC", "XLRE",
    # Bond ETFs
    "TLT", "IEF", "SHY", "LQD", "HYG", "BND", "AGG", "TIP", "MUB", "EMB",
    # Commodity ETFs
    "GLD", "SLV", "USO", "UNG", "DBA", "DBB", "DBC", "PDBC", "PPLT", "PALL",
    # Index ETFs
    "SPY", "QQQ", "IWM", "DIA", "VTI", "EFA", "EEM", "VWO", "VEA", "IEMG",
    # Volatility / specialty
    "VXX", "SVXY", "UVXY",
    # REITs
    "VNQ", "IYR", "SCHH", "RWR",
    # International
    "FXI", "EWJ", "EWZ", "EWG", "EWU", "EWY", "EWT", "EWA", "EWC", "EWH",
]

# Wikipedia GICS Sector name -> our short code
SECTOR_NAME_MAP = {
    "Information Technology": "tech",
    "Financials": "financials",
    "Health Care": "healthcare",
    "Consumer Discretionary": "cons_disc",
    "Industrials": "industrials",
    "Communication Services": "comms",
    "Consumer Staples": "cons_staples",
    "Energy": "energy",
    "Utilities": "utilities",
    "Real Estate": "real_estate",
    "Materials": "materials",
}

# Sector code -> matching SPDR sector ETF (anchor series for training)
SECTOR_TO_ETF = {
    "tech": "XLK",
    "financials": "XLF",
    "healthcare": "XLV",
    "cons_disc": "XLY",
    "industrials": "XLI",
    "comms": "XLC",
    "cons_staples": "XLP",
    "energy": "XLE",
    "utilities": "XLU",
    "real_estate": "XLRE",
    "materials": "XLB",
}

SECTOR_CODES = list(SECTOR_TO_ETF.keys())

# Fallback (used only if Wikipedia fetch fails). Sectors are best-effort guesses.
_FALLBACK_SP500_WITH_SECTORS = [
    ("AAPL", "tech"), ("MSFT", "tech"), ("GOOGL", "comms"),
    ("AMZN", "cons_disc"), ("NVDA", "tech"), ("META", "comms"),
    ("TSLA", "cons_disc"), ("BRK-B", "financials"), ("JPM", "financials"),
    ("V", "financials"), ("UNH", "healthcare"), ("JNJ", "healthcare"),
    ("XOM", "energy"), ("MA", "financials"), ("PG", "cons_staples"),
]

# The Nasdaq-100 Wikipedia page classifies constituents by **ICB Industry**, not
# GICS like the S&P 500 page. Crosswalk ICB top-level industry -> our short code.
# (Sector labels are used only to stratify the held-out split, so they need not
# match GICS exactly; the Nasdaq-100 excludes financials by index construction.)
ICB_INDUSTRY_MAP = {
    "Technology": "tech",
    "Telecommunications": "comms",
    "Health Care": "healthcare",
    "Consumer Discretionary": "cons_disc",
    "Consumer Staples": "cons_staples",
    "Industrials": "industrials",
    "Basic Materials": "materials",
    "Energy": "energy",
    "Utilities": "utilities",
    "Real Estate": "real_estate",
    "Financials": "financials",
}

# The authoritative Nasdaq-100 universe + sector tags come from the advisor's
# "simofi" catalog (simofi/data/{universes,stocks}.json). simofi tags sectors in
# the Yahoo Finance scheme; crosswalk Yahoo sector -> our short code so NASDAQ
# and S&P 500 share one sector taxonomy.
YAHOO_SECTOR_MAP = {
    "Technology": "tech",
    "Communication Services": "comms",
    "Healthcare": "healthcare",
    "Consumer Cyclical": "cons_disc",
    "Consumer Defensive": "cons_staples",
    "Industrials": "industrials",
    "Basic Materials": "materials",
    "Energy": "energy",
    "Utilities": "utilities",
    "Real Estate": "real_estate",
    "Financial Services": "financials",
}

# Repo-root/simofi/data — the advisor's curated universe + sector catalog.
_SIMOFI_DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "simofi", "data"
)

# Fallback (used only if Wikipedia fetch fails). Best-effort sector guesses.
_FALLBACK_NASDAQ100_WITH_SECTORS = [
    ("AAPL", "tech"), ("MSFT", "tech"), ("NVDA", "tech"), ("AVGO", "tech"),
    ("AMD", "tech"), ("ADBE", "tech"), ("CSCO", "tech"), ("INTC", "tech"),
    ("QCOM", "tech"), ("TXN", "tech"), ("AMAT", "tech"), ("INTU", "tech"),
    ("AMZN", "cons_disc"), ("TSLA", "cons_disc"), ("BKNG", "cons_disc"),
    ("MELI", "cons_disc"), ("SBUX", "cons_disc"), ("ORLY", "cons_disc"),
    ("GOOGL", "comms"), ("GOOG", "comms"), ("META", "comms"), ("NFLX", "comms"),
    ("CMCSA", "comms"), ("TMUS", "comms"), ("PEP", "cons_staples"),
    ("COST", "cons_staples"), ("MDLZ", "cons_staples"), ("KDP", "cons_staples"),
    ("AMGN", "healthcare"), ("GILD", "healthcare"), ("ISRG", "healthcare"),
    ("VRTX", "healthcare"), ("REGN", "healthcare"), ("HON", "industrials"),
    ("CSX", "industrials"), ("PAYX", "industrials"), ("ADP", "industrials"),
    ("AEP", "utilities"), ("EXC", "utilities"), ("XEL", "utilities"),
    ("CEG", "utilities"), ("FANG", "energy"), ("BKR", "energy"),
    ("LIN", "materials"),
]


def _get_sp500_with_sectors():
    """Fetch S&P 500 (ticker, sector_code) pairs from Wikipedia.

    Retries up to 3 times. Falls back to the hardcoded list ONLY as a last
    resort, printing a loud warning so the caller knows the data is thin.

    Returns:
        list of (ticker, sector_code). Tickers with unmapped sectors are
        dropped.
    """
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    max_retries = 3

    for attempt in range(1, max_retries + 1):
        try:
            print(f"  [Wikipedia] attempt {attempt}/{max_retries}...")
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            table = pd.read_html(io.StringIO(resp.text))[0]
            results = []
            for _, row in table.iterrows():
                ticker = str(row["Symbol"]).replace(".", "-")
                sector_name = str(row["GICS Sector"]).strip()
                sector_code = SECTOR_NAME_MAP.get(sector_name)
                if sector_code is not None:
                    results.append((ticker, sector_code))
            print(f"  [Wikipedia] OK — {len(results)} tickers across "
                  f"{len(set(s for _, s in results))} sectors")
            return results
        except Exception as e:
            print(f"  [Wikipedia] attempt {attempt} failed: {e}")
            if attempt < max_retries:
                time.sleep(2 * attempt)

    print("  *** WARNING: Wikipedia fetch failed after all retries. ***")
    print(f"  *** Falling back to {len(_FALLBACK_SP500_WITH_SECTORS)} "
          f"hardcoded tickers — results will be severely limited. ***")
    return list(_FALLBACK_SP500_WITH_SECTORS)


def _get_sp500_tickers():
    """Return just the S&P 500 ticker symbols (legacy callers)."""
    return [t for t, _ in _get_sp500_with_sectors()]


def _get_nasdaq100_from_simofi(universe_key="QQQ"):
    """Read Nasdaq-100 (ticker, sector_code) pairs from the simofi catalog.

    Universe membership comes from ``simofi/data/universes.json`` (the ``QQQ``
    universe == NASDAQ-100); per-ticker sectors come from
    ``simofi/data/stocks.json`` and are crosswalked from the Yahoo scheme via
    ``YAHOO_SECTOR_MAP``. This is the advisor's curated, fully sector-labeled
    source and is preferred over the Wikipedia scrape.

    Returns:
        list of (ticker, sector_code), or [] if the catalog is unavailable.
        Tickers with no/unmapped sector are kept with code "unknown" so the
        universe is never silently truncated.
    """
    uni_path = os.path.join(_SIMOFI_DATA_DIR, "universes.json")
    stk_path = os.path.join(_SIMOFI_DATA_DIR, "stocks.json")
    try:
        with open(uni_path, encoding="utf-8") as f:
            universes = json.load(f)["universes"]
        with open(stk_path, encoding="utf-8") as f:
            stocks = json.load(f)["stocks"]
    except (OSError, KeyError, json.JSONDecodeError) as e:
        print(f"  [simofi] catalog unavailable ({e.__class__.__name__}: {e})")
        return []

    members = universes.get(universe_key, {}).get("members", [])
    if not members:
        print(f"  [simofi] universe {universe_key!r} has no members")
        return []

    results, unmapped = [], []
    for ticker in members:
        yahoo_sector = stocks.get(ticker, {}).get("gics", {}).get("sector", "")
        code = YAHOO_SECTOR_MAP.get(yahoo_sector, "unknown")
        if code == "unknown":
            unmapped.append((ticker, yahoo_sector or "<none>"))
        # yfinance uses '-' where some sources use '.' (e.g. BRK.B -> BRK-B)
        results.append((ticker.replace(".", "-"), code))
    n_sectors = len({c for _, c in results if c != "unknown"})
    print(f"  [simofi] OK — {len(results)} tickers from {universe_key} across "
          f"{n_sectors} sectors")
    if unmapped:
        print(f"  [simofi] {len(unmapped)} ticker(s) with unmapped sector "
              f"(kept as 'unknown'): {unmapped}")
    return results


def _get_nasdaq100_with_sectors():
    """Return Nasdaq-100 (ticker, sector_code) pairs.

    Source priority: the advisor's **simofi** catalog (authoritative) ->
    Wikipedia ICB scrape -> hardcoded fallback. Same return contract as
    ``_get_sp500_with_sectors``.
    """
    pairs = _get_nasdaq100_from_simofi()
    if pairs:
        return pairs
    print("  [simofi] unavailable — falling back to Wikipedia scrape")
    return _get_nasdaq100_from_wikipedia()


def _get_nasdaq100_from_wikipedia():
    """Fetch Nasdaq-100 (ticker, sector_code) pairs from Wikipedia.

    The Nasdaq-100 page classifies by ICB Industry, so we crosswalk via
    ``ICB_INDUSTRY_MAP``. Same retry/fallback contract as
    ``_get_sp500_with_sectors``. Tickers whose industry is unmapped are dropped.

    Returns:
        list of (ticker, sector_code).
    """
    url = "https://en.wikipedia.org/wiki/Nasdaq-100"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    max_retries = 3

    for attempt in range(1, max_retries + 1):
        try:
            print(f"  [Wikipedia] Nasdaq-100 attempt {attempt}/{max_retries}...")
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            tables = pd.read_html(io.StringIO(resp.text))

            # Locate the components table: a Ticker/Symbol column + an ICB
            # Industry column, with ~100 rows.
            comp = None
            for t in tables:
                cols = [str(c) for c in t.columns]
                tcol = next((c for c in cols if c.lower() in ("ticker", "symbol")), None)
                icol = next((c for c in cols if c.lower().startswith("icb industry")), None)
                if tcol and icol and len(t) > 50:
                    comp = (t, tcol, icol)
                    break
            if comp is None:
                raise ValueError("Nasdaq-100 components table not found")

            table, tcol, icol = comp
            results = []
            for _, row in table.iterrows():
                ticker = str(row[tcol]).strip().replace(".", "-")
                industry = str(row[icol]).strip()
                sector_code = ICB_INDUSTRY_MAP.get(industry)
                if sector_code is not None:
                    results.append((ticker, sector_code))
            if not results:
                raise ValueError("no Nasdaq-100 tickers parsed")
            print(f"  [Wikipedia] OK — {len(results)} tickers across "
                  f"{len(set(s for _, s in results))} sectors")
            return results
        except Exception as e:
            print(f"  [Wikipedia] Nasdaq-100 attempt {attempt} failed: {e}")
            if attempt < max_retries:
                time.sleep(2 * attempt)

    print("  *** WARNING: Nasdaq-100 Wikipedia fetch failed after all retries. ***")
    print(f"  *** Falling back to {len(_FALLBACK_NASDAQ100_WITH_SECTORS)} "
          f"hardcoded tickers — results will be severely limited. ***")
    return list(_FALLBACK_NASDAQ100_WITH_SECTORS)


def _fetch_tickers(tickers, start_date, end_date, min_len):
    """Bulk-fetch daily close prices for a list of tickers.

    Returns:
        list of (ticker, pd.Series) with DatetimeIndex
    """
    results = []
    failed = 0
    batch_size = 50
    total_batches = (len(tickers) + batch_size - 1) // batch_size

    for i in range(0, len(tickers), batch_size):
        batch_num = i // batch_size + 1
        batch = tickers[i : i + batch_size]
        print(f"  [yfinance] batch {batch_num}/{total_batches} "
              f"({len(results)} loaded so far, {failed} failed)")
        try:
            df = yf.download(
                batch, start=start_date, end=end_date,
                auto_adjust=True, progress=False, threads=True,
            )
            if df.empty:
                failed += len(batch)
                continue

            close = df["Close"] if "Close" in df.columns else df
            if isinstance(close, pd.Series):
                # Single ticker
                close = close.dropna()
                if len(close) >= min_len:
                    results.append((batch[0], close))
                else:
                    failed += 1
            else:
                for ticker in close.columns:
                    series = close[ticker].dropna()
                    if len(series) >= min_len:
                        results.append((ticker, series))
                    else:
                        failed += 1
        except Exception as e:
            print(f"  [yfinance] batch {batch_num} error: {e}")
            failed += len(batch)

        # Rate limit
        if i + batch_size < len(tickers):
            time.sleep(0.5)

    print(f"  [yfinance] done — {len(results)} loaded, {failed} failed")
    return results, failed


def fetch_market_data(asset_class, start_date="2014-01-01",
                      end_date="2024-01-01", min_len=252):
    """Fetch daily close prices for an asset class.

    Returns:
        list of (ticker, pd.Series) with DatetimeIndex
    """
    if asset_class == "equity":
        tickers = _get_sp500_tickers()
    elif asset_class == "forex":
        tickers = FOREX_TICKERS
    elif asset_class == "macro":
        tickers = MACRO_TICKERS
    else:
        raise ValueError(f"Unknown asset class: {asset_class}")

    results, failed = _fetch_tickers(tickers, start_date, end_date, min_len)
    print(f"  {asset_class}: {len(results)} series loaded, {failed} skipped")
    return results


def fetch_market_data_by_sector(sector_code, start_date="2014-01-01",
                                end_date="2024-01-01", min_len=252):
    """Fetch daily close prices for a single GICS sector.

    Tickers = S&P 500 constituents in this sector + the matching SPDR ETF
    (anchor series). The ETF gives every adapter a long, clean reference
    even when individual constituents have short histories.

    Returns:
        list of (ticker, pd.Series) with DatetimeIndex
    """
    if sector_code not in SECTOR_TO_ETF:
        raise ValueError(
            f"Unknown sector: {sector_code}. "
            f"Valid: {sorted(SECTOR_TO_ETF.keys())}"
        )

    pairs = _get_sp500_with_sectors()
    tickers = [t for t, s in pairs if s == sector_code]

    # Anchor with the SPDR sector ETF
    etf = SECTOR_TO_ETF[sector_code]
    if etf not in tickers:
        tickers.append(etf)

    results, failed = _fetch_tickers(tickers, start_date, end_date, min_len)
    print(f"  sector={sector_code}: {len(results)} series loaded "
          f"({failed} skipped, anchor={etf})")
    return results
