"""Strict, vintage-aware source parsing and monthly return construction."""

from hashlib import sha256
from io import StringIO
import json
from pathlib import Path
import re
from zipfile import ZipFile

import exchange_calendars as xcals
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "research/data/raw"
MANIFEST = ROOT / "research/input_manifest.json"
SECTORS = {
    "XLC": "Communication Services",
    "XLY": "Consumer Discretionary",
    "XLP": "Consumer Staples",
    "XLE": "Energy",
    "XLF": "Financials",
    "XLV": "Health Care",
    "XLI": "Industrials",
    "XLB": "Materials",
    "XLRE": "Real Estate",
    "XLK": "Technology",
    "XLU": "Utilities",
}
ALL_TICKERS = list(SECTORS)
TICKERS = [t for t in ALL_TICKERS if t not in {"XLC", "XLRE"}]
FACTORS = ["Mkt-RF", "SMB", "HML", "RMW", "CMA", "Mom"]
START, END = "2006-12-01", "2026-08-01"
EXTENDED_START = "2018-06-19"


def source_start(ticker):
    # XLC's first listed session is June 19, after its June 18 fund inception.
    return EXTENDED_START if ticker in {"XLC", "XLRE"} else START


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def french_monthly(path, columns):
    """Parse only YYYYMM rows, excluding annual tables and prose; percent -> decimal."""
    with ZipFile(path) as archive:
        names = [n for n in archive.namelist() if n.lower().endswith(".csv")]
        if len(names) != 1:
            raise ValueError("Expected one French CSV member")
        text = archive.read(names[0]).decode("utf-8-sig")
    lines = text.splitlines()
    headers = [i for i, s in enumerate(lines) if s.strip().startswith(",")]
    if not headers:
        raise ValueError("Missing French header")
    header = [s.strip() for s in lines[headers[0]].split(",")[1:]]
    if header != columns:
        raise ValueError(f"French schema changed: {header}")
    rows = [s for s in lines if re.match(r"^\s*\d{6}\s*,", s)]
    frame = pd.read_csv(StringIO("\n".join(rows)), header=None, index_col=0)
    if frame.shape[1] != len(columns):
        raise ValueError("French row width changed")
    frame.columns = columns
    frame.index = pd.PeriodIndex(frame.index.astype(str), freq="M")
    frame = frame.apply(pd.to_numeric, errors="raise")
    if (frame <= -99).any().any() or not np.isfinite(frame).all().all():
        raise ValueError("French missing sentinel/nonfinite return")
    if frame.index.has_duplicates or not frame.index.is_monotonic_increasing:
        raise ValueError("French months duplicated or unordered")
    if not frame.index.equals(pd.period_range(frame.index[0], frame.index[-1], freq="M")):
        raise ValueError("French months missing")
    return frame / 100


def expected_sessions(start=START, end=END):
    return xcals.get_calendar(
        "XNYS", start=start, end=pd.Timestamp(end) - pd.Timedelta(days=1)
    ).sessions.tz_localize(None)


def monthly_simple_returns(prices, sessions):
    """Require all expected daily closes; retain actual last-session month ends."""
    if prices.index.has_duplicates or not prices.index.equals(sessions):
        raise ValueError("Daily prices must exactly match ordered exchange sessions")
    if not np.isfinite(prices).all().all() or (prices <= 0).any().any():
        raise ValueError("Prices must be finite and positive; filling is prohibited")
    monthly = prices.groupby(prices.index.to_period("M")).last()
    result = monthly.pct_change(fill_method=None).iloc[1:]
    if (result <= -1).any().any() or not np.isfinite(result).all().all():
        raise ValueError("Invalid simple monthly returns")
    return result


def load_panel(extended=False):
    manifest = json.loads(MANIFEST.read_text())
    for source in manifest["sources"]:
        if digest(RAW / source["filename"]) != source["sha256"]:
            raise ValueError("Source hash mismatch: " + source["filename"])
    ff = french_monthly(RAW / "ff5.zip", ["Mkt-RF", "SMB", "HML", "RMW", "CMA", "RF"])
    mom = french_monthly(RAW / "momentum.zip", ["Mom"])
    first_month = "2018-07" if extended else "2007-01"
    tickers = ALL_TICKERS if extended else TICKERS
    start = EXTENDED_START if extended else START
    f = ff.join(mom, how="inner").loc[first_month:"2026-07"]
    required = pd.period_range(first_month, "2026-07", freq="M")
    if not f.index.equals(required) or f.isna().any().any():
        raise ValueError("Factor coverage does not match the frozen protocol")
    prices = pd.concat(
        [pd.read_csv(RAW / f"{t}.csv", index_col=0, parse_dates=True).loc[start:] for t in tickers],
        axis=1,
    )
    if list(prices.columns) != tickers:
        raise ValueError("ETF columns changed")
    r = monthly_simple_returns(prices, expected_sessions(start=start))
    if not r.index.equals(required):
        raise ValueError("ETF month coverage differs from factors")
    y = r.sub(f["RF"], axis=0)
    audit = {
        "price_rows_per_etf": len(prices),
        "etfs": len(tickers),
        "universe": "all eleven State Street sectors"
        if extended
        else "original nine State Street sectors",
        "monthly_observations": len(y),
        "first_month": str(y.index[0]),
        "last_month": str(y.index[-1]),
        "missing_prices": int(prices.isna().sum().sum()),
        "duplicate_price_dates": int(prices.index.duplicated().sum()),
        "missing_factors": int(f.isna().sum().sum()),
        "ff5_source_last_month": str(ff.index[-1]),
        "momentum_source_last_month": str(mom.index[-1]),
        "min_monthly_simple_return": float(r.min().min()),
        "max_monthly_simple_return": float(r.max().max()),
        "zero_daily_changes": {SECTORS[t]: int(prices[t].diff().eq(0).sum()) for t in tickers},
        "min_rf_monthly_decimal": float(f.RF.min()),
        "max_rf_monthly_decimal": float(f.RF.max()),
        "units": "decimal arithmetic monthly returns; ETF excess = simple return minus RF",
        "fills": 0,
        "coverage_exclusions_within_core": 0,
    }
    return f[FACTORS], y, audit
