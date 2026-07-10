import argparse
import ftplib
import io
import json
import logging
import os
import random
import time
import urllib.request
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import yfinance as yf

log = logging.getLogger(__name__)

# --- schema / config property keys ---

MIME_CSV = "text/csv"
MIME_HTML = "text/html"
MIME_XLS = "application/vnd.ms-excel"

# general meta
META = "meta"
META_CREATED = "created_on"
META_UPDATED = "updated_on"
META_NOTES = "notes"

# universes.json
U_ROOT = "universes"
U_NAME = "name"
U_PROXY = "index_proxy_for"
U_MEMBERS = "members"
U_SOURCES = "sources"
U_SOURCE_ID = "source_id"
U_SOURCE_TICKER_COL = "ticker_col"
U_SOURCE_DELIMITER = "delimiter"
U_SOURCE_TYPE = "source_type"
U_SOURCE_TYPE_FTP = "ftp"
U_SOURCE_TYPE_URL = "url"
U_SOURCE_FTP_HOST = "host"
U_SOURCE_FTP_DIR = "dir"
U_SOURCE_URL_MIME_TYPE = "mime_type"
U_SOURCE_URL_BASE = "base_url"
U_SOURCE_URL_TABLE_IDX = "table_index"

# stocks.json
S_ROOT = "stocks"
S_NAME = "name"
S_NAME_SECURITY = "Security Name"
S_GICS = "gics"
S_GICS_SECTOR = "sector"
S_GICS_INDUSTRY_GROUP = "industry_group"
S_GICS_INDUSTRY = "industry"
S_GICS_SUB_INDUSTRY = "sub_industry"
S_MEMBERSHIPS = "memberships"

# model_configs.json
MC_ROOT = "model_configs"
MC_THRESHOLD = "threshold"
MC_BIAS_MULTIPLIERS = "bias_multipliers"
MC_BIAS = "bias"
MC_BIAS_UNIVERSE = "universe"
MC_BIAS_GICS = "gics"
MC_BIAS_GICS_KEYS = {
    S_GICS_SECTOR,
    S_GICS_INDUSTRY_GROUP,
    S_GICS_INDUSTRY,
    S_GICS_SUB_INDUSTRY,
}
MC_BIAS_CUSTOM = "custom"

# model.json
M_ROOT = "model"
M_META_MODEL_CONFIG = "model_config"

# --- request / http constants ---

USER_AGENTS: list[str] = [
    # 260609 Chrome desktop
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    # 260609 Edge desktop
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0",
    # 260609 Firefox desktop
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) "
    "Gecko/20100101 Firefox/138.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:150.0) "
    "Gecko/20100101 Firefox/150.0",
    # 260609 Safari desktop
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 15_7_5) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Safari/605.1.15",
]


def setup_logging(
    log_to_file: bool = False,
    level: int = logging.WARNING,
    filename: str = "run.log",
    log_dir: str | None = None,
) -> None:
    """logging to console by default, optionally to file in log_dir"""

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    config = {
        "level": level,
        "format": "%(levelname).1s %(asctime)s [%(funcName)s] %(message)s",
        "datefmt": "%m%d.%H%M%S",
        "force": True,
    }

    if log_to_file:
        log_dir = log_dir or os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(log_dir, exist_ok=True)
        config.update({"filename": os.path.join(log_dir, filename), "filemode": "a"})

    logging.basicConfig(**config)


def _default_meta() -> dict:
    """Return a meta dict with created_on set to today."""
    today = date.today().isoformat()
    return {META_CREATED: today}


def get_model_configs_from_file(model_configs_path: str | Path) -> dict:
    """Load and return the model_configs root from a JSON file."""
    with open(model_configs_path) as f:
        raw = json.load(f)
    return raw[MC_ROOT]


def get_universes_from_file(universes_path: str | Path) -> dict:
    """Load and return the universes root from a JSON file."""
    with open(universes_path) as f:
        raw = json.load(f)
    return raw[U_ROOT]


def get_stocks_from_file(stocks_path: str | Path) -> dict:
    """Load and return the stocks root from a JSON file."""
    with open(stocks_path) as f:
        raw = json.load(f)
    return raw[S_ROOT]


def get_meta_from_file(path: str | Path, meta_key: str = META) -> dict:
    """Load and return the meta section from a JSON file."""
    with open(path) as f:
        raw = json.load(f)
    return raw.get(meta_key, {})


def write_file(
    path: str | Path, root_key: str, data: dict, meta: dict | None = None
) -> None:
    """Write data with meta wrapper to a JSON file."""
    out_meta = _default_meta()
    if meta:
        out_meta.update(meta)
    out = {META: out_meta, root_key: data}
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    log.info(f"Output {len(data)} records to {Path(path).name}.")


def list_ftp(universes: dict, universe_key: str) -> None:
    """List FTP directory contents for a universe's FTP sources."""
    universe = universes.get(universe_key)
    if not universe:
        log.error(f"No configuration found for source {universe_key}")
    else:
        ftp_sources = [
            s
            for s in universe.get(U_SOURCES, [])
            if s.get(U_SOURCE_TYPE) == U_SOURCE_TYPE_FTP
        ]
        if not ftp_sources:
            log.error(f"No FTP source configured for {universe_key}")
        else:

            for source in ftp_sources:
                ftp_host = source.get(U_SOURCE_FTP_HOST)
                ftp_dir = source.get(U_SOURCE_FTP_DIR)
                try:
                    with ftplib.FTP(ftp_host) as ftp:
                        ftp.login("anonymous", "")
                        ftp.cwd(ftp_dir)
                        ftp.retrlines("LIST")
                    log.info(f"FTP listing complete for {ftp_host}/{ftp_dir}")
                    break
                except ftplib.error_perm as e:
                    log.error(f"FTP permission error: {e}")
                except ftplib.error_temp as e:
                    log.error(f"FTP temporary error: {e}")
                except Exception as e:
                    log.error(f"FTP failed: {e}")


def generate_model(stocks: dict, model_config: str | Path | dict) -> dict:
    """Score and filter stocks against a model config, returning tickers above threshold."""
    if not isinstance(model_config, dict):
        model_config = get_model_configs_from_file(model_config)

    threshold = model_config.get(MC_THRESHOLD, 0.51)
    bias_multipliers = model_config.get(MC_BIAS_MULTIPLIERS, {})

    bias = model_config.get(MC_BIAS, {})
    universe_bias = bias.get(MC_BIAS_UNIVERSE, {})
    gics_bias = bias.get(MC_BIAS_GICS, {})
    custom_bias = bias.get(MC_BIAS_CUSTOM, {})

    # total_multipliers = sum(bias_multipliers.values()) or 1
    total_multipliers = (
        sum(v for k, v in bias_multipliers.items() if k != MC_BIAS_CUSTOM) or 1
    )

    model = {}
    for ticker, stock in stocks.items():
        # weights accumulate across bias, gics, memberships without normalization
        weight = 0.0

        # bias
        if ticker in custom_bias:
            weight += custom_bias[ticker] * bias_multipliers.get(MC_BIAS_CUSTOM, 0)

        # gics
        stock_gics = stock.get(S_GICS, {})
        for gics_key in MC_BIAS_GICS_KEYS:
            gics_levels = gics_bias.get(gics_key, {})
            gics_value = stock_gics.get(gics_key, "")
            if gics_value and gics_value in gics_levels:
                bias_key = MC_BIAS_GICS + "_" + gics_key
                weight += gics_levels[gics_value] * bias_multipliers.get(bias_key, 0)

        # universe memberships: top n by bias value (vs as multiplier)
        n = bias_multipliers.get(MC_BIAS_UNIVERSE, 0)
        universe_scores = sorted(
            (
                universe_bias[m]
                for m in stock.get(S_MEMBERSHIPS, [])
                if m in universe_bias
            ),
            reverse=True,
        )[:n]
        weight += sum(universe_scores)

        # normalize bias
        weight /= total_multipliers

        if weight >= threshold:
            model[ticker] = {S_NAME: stock.get(S_NAME, ""), "weight": round(weight, 1)}

    return model


class UniverseBuilder:
    YFINANCE_DELAY = 0.5

    def __init__(self, universes: str | Path | dict, stocks: str | Path | dict):
        self._universes = (
            get_universes_from_file(universes)
            if not isinstance(universes, dict)
            else universes
        )
        self._stocks = (
            get_stocks_from_file(stocks) if not isinstance(stocks, dict) else stocks
        )

    # --- properties ---

    @property
    def stocks(self) -> dict:
        if self._universes and not self._stocks:
            self.refresh()
        return self._stocks

    @property
    def universes(self) -> dict:
        return self._universes

    # --- private helpers: stocks ---

    def _fetch_stock_details_yf(self, ticker: str) -> dict:
        """Pull fields from yfinance."""
        try:
            info = yf.Ticker(ticker).info
            return {
                S_NAME: info.get("longName", ""),
                S_GICS: {
                    S_GICS_SECTOR: info.get(S_GICS_SECTOR, ""),
                    S_GICS_INDUSTRY_GROUP: "",  # yfinance doesnt provide
                    S_GICS_INDUSTRY: info.get(S_GICS_INDUSTRY, ""),
                    S_GICS_SUB_INDUSTRY: "",  # yfinance doesnt provide
                },
            }
        except Exception as e:
            log.warning(f"yfinance failed for {ticker}: {e}")
            return {S_NAME: "", S_GICS: {}}

    def _update_stock_details(self):
        """Enrich each stock with yfinance details."""
        for k, v in self._stocks.items():
            if not self._stocks[k]:
                self._stocks[k] = self._fetch_stock_details_yf(k)
                # delay avoids rate-limiting from yfinance
                time.sleep(self.YFINANCE_DELAY)

    def _update_stocks(self):
        """
        Tag memberships for each stock from universe members.
        Assumes stock keys are already populated in self._stocks
        by _update_universes(). Must be called after _update_universes().
        """
        self._update_stock_details()
        for k, v in self._universes.items():
            for s in v.get(U_MEMBERS, []):
                if s in self._stocks:
                    self._stocks[s].setdefault(S_MEMBERSHIPS, []).append(k)

    # --- private helpers: universes ---
    def _populate_stock_keys(self):
        """Seed self._stocks with empty dicts for all universe members not yet present."""
        for v in self._universes.values():
            self._stocks.update(
                {s: {} for s in v.get(U_MEMBERS, []) if s and s not in self._stocks}
            )

    def _fetch_from_ftp(
        self, host: str, dir: str, file: str, delimiter: str, column: str
    ) -> list[dict]:
        """Pull raw symbol rows from FTP."""
        lines = []
        with ftplib.FTP(host) as ftp:
            ftp.login("anonymous", "")
            ftp.cwd(dir)
            buf = io.BytesIO()
            ftp.retrbinary(f"RETR {file}", buf.write)
        buf.seek(0)
        raw = buf.read().decode("utf-8").splitlines()
        headers = raw[0].split(delimiter)
        for line in raw[1:]:
            if line.startswith("File Creation Time"):
                continue
            parts = line.split(delimiter)
            if len(parts) == len(headers):
                lines.append(dict(zip(headers, parts)))
        return [row[column].strip() for row in lines if row.get(column, "").strip()]

    def _parse_html_table(
        self, url: str, table_index: int, col: str, headers: dict | None = None
    ) -> list[dict]:
        """Fetch and parse an HTML table, returning list of Symbol dicts."""
        req = urllib.request.Request(url, headers=headers or {})
        html = urllib.request.urlopen(req).read()
        df = pd.read_html(io.BytesIO(html), header=0)[table_index]
        return df[col].dropna().tolist()

    def _fetch_from_source(self, source) -> list[dict]:
        try:
            source_type = source.get(U_SOURCE_TYPE)
            source_id = source.get(U_SOURCE_ID)
            col_name = source[U_SOURCE_TICKER_COL]

            if source_type == U_SOURCE_TYPE_FTP:
                delimiter = source.get(U_SOURCE_DELIMITER)
                return (
                    self._fetch_from_ftp(
                        source.get(U_SOURCE_FTP_HOST),
                        source.get(U_SOURCE_FTP_DIR),
                        source_id,
                        delimiter,
                        col_name,
                    )
                    or []
                )

            url = source[U_SOURCE_URL_BASE] + source_id
            if source[U_SOURCE_URL_MIME_TYPE] == MIME_CSV:
                df = pd.read_csv(url)
                return df[col_name].dropna().tolist()

            if source[U_SOURCE_URL_MIME_TYPE] == MIME_XLS:
                df = pd.read_excel(url, skiprows=source.get("skiprows", 0))
                return df[col_name].dropna().tolist()

            headers = {"User-Agent": random.choice(USER_AGENTS)}
            return (
                self._parse_html_table(
                    url, source[U_SOURCE_URL_TABLE_IDX], col_name, headers=headers
                )
                or []
            )
        except Exception as e:
            log.warning(f"Source failed: {e}")
            return []

    def _fetch_constituents(self, universe_key: str) -> list[str]:
        """Try each source in order, then proxy sources if all fail."""
        universe = self._universes.get(universe_key, {})

        # try own sources in order
        for source in universe.get(U_SOURCES, []):
            try:
                result = self._fetch_from_source(source)
                if result:
                    return result
            except Exception as e:
                log.warning(f"Source failed for {universe_key}: {e}")

        # try proxy universe sources in order
        proxy_key = next(
            (k for k, v in self._universes.items() if v.get(U_PROXY) == universe_key),
            None,
        )
        if proxy_key:
            for source in self._universes[proxy_key].get(U_SOURCES, []):
                try:
                    result = self._fetch_from_source(source)
                    if result:
                        return result
                except Exception as e:
                    log.warning(f"Proxy source failed for {proxy_key}: {e}")
        else:
            log.warning(f"No source proxy configured for {universe_key}")

        # try yfinance fallback
        try:
            holdings = yf.Ticker(universe_key).funds_data.top_holdings
            return list(holdings.index)
        except Exception as e:
            log.warning(f"yfinance source holdings failed for {universe_key}: {e}")
            return []

    def _update_universes(self):
        """Populate selected attributes for each universe that lacks them."""
        for k, v in self._universes.items():

            if not v.get(U_NAME):
                if k.startswith("^"):
                    try:
                        name = yf.Ticker(k).info.get("shortName", k[1:].lower())
                        v[U_NAME] = name.replace(" ", "_").replace("-", "_")
                    except Exception as e:
                        log.warning(f"yfinance failed for {k}: {e}")
                        v[U_NAME] = k[1:]
                else:
                    v[U_NAME] = k

            if not v.get(U_MEMBERS):
                v[U_MEMBERS] = self._fetch_constituents(k)

        # build stock keys
        self._populate_stock_keys()

    # --- public ---

    def refresh(self):
        """Fetch universe members and enrich stocks from all configured sources."""
        self._update_universes()
        self._update_stocks()

    def get_stock(self, ticker: str) -> dict:
        """Return stock data for a single ticker, or None if not found."""
        return self._stocks.get(ticker)

    def get_universe(self, universe: str) -> dict:
        """Return universe data for a single key, or None if not found."""
        return self._universes.get(universe)


def main() -> None:
    parser = argparse.ArgumentParser(description="simple modeler for finance")
    parser.add_argument(
        "--refresh", nargs="?", const="both", default=None, choices=["u", "s", "both"]
    )
    parser.add_argument("--model", default="default", help="model from configuration")
    parser.add_argument("--lftp", metavar="SRC", help="list FTP files for universe")
    parser.add_argument("--log-file", action="store_true", help="log to file")
    parser.add_argument(
        "--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"]
    )
    args = parser.parse_args()

    setup_logging(log_to_file=args.log_file, level=getattr(logging, args.log_level))
    t0 = time.time()

    data_dir = Path(__file__).parent / "data"
    universes_path = data_dir / (U_ROOT + ".json")
    universes = get_universes_from_file(universes_path)

    if args.lftp:
        list_ftp(universes, args.lftp)

    else:
        stocks_path = data_dir / (S_ROOT + ".json")
        try:
            stocks = get_stocks_from_file(stocks_path)
        except FileNotFoundError:
            stocks = {}

        if args.refresh:
            # refresh system

            ub = UniverseBuilder(universes, stocks)

            if args.refresh in ("u", "both"):
                ub._update_universes()
                meta = get_meta_from_file(universes_path)
                created = meta.get(META_CREATED, datetime.now().strftime("%Y%m%d"))
                archive_path = universes_path.with_suffix(
                    f".{created.replace('-','')}.json"
                )
                universes_path.rename(archive_path)
                write_file(universes_path, U_ROOT, ub.universes)

            if args.refresh == "s":
                ub._populate_stock_keys()

            if args.refresh in ("s", "both"):
                ub._update_stocks()
                write_file(stocks_path, S_ROOT, ub.stocks)

        else:
            # generate model

            model_configs_path = data_dir / (MC_ROOT + ".json")
            model_configs = get_model_configs_from_file(model_configs_path)

            if args.model:
                model_config_name = args.model
                model_config = model_configs.get(model_config_name)
                if model_config is None:
                    log.error(f"No model config found: {model_config_name}")
                    exit(1)

            stocks = get_stocks_from_file(stocks_path)
            model = generate_model(stocks, model_config)

            meta = {M_META_MODEL_CONFIG: model_config_name}

            model_name = model_config_name.replace(" ", "_").replace("-", "_").lower()
            model_path = data_dir / f"{M_ROOT}_{model_name}.json"
            write_file(model_path, M_ROOT, model, meta)

    log.info(f"timer: {time.time() - t0:.2f} s")


if __name__ == "__main__":
    main()
