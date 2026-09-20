"""Resume cached acquisition or restore the exact pinned public-source vintage."""

import argparse
from datetime import datetime, timezone
import json
import shutil
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import yfinance as yf

from research.data import (
    END,
    MANIFEST,
    RAW,
    ROOT,
    START,
    ALL_TICKERS,
    SECTORS,
    digest,
    expected_sessions,
    french_monthly,
    source_start,
)

BASE = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"


def specifications():
    sources = [
        {
            "filename": "ff5.zip",
            "url": BASE + "F-F_Research_Data_5_Factors_2x3_CSV.zip",
            "columns": ["Mkt-RF", "SMB", "HML", "RMW", "CMA", "RF"],
            "provider": "Kenneth R. French Data Library",
            "units": "percent per month",
        },
        {
            "filename": "momentum.zip",
            "url": BASE + "F-F_Momentum_Factor_CSV.zip",
            "columns": ["Mom"],
            "provider": "Kenneth R. French Data Library",
            "units": "percent per month",
        },
    ]
    sources += [
        {
            "filename": f"{t}.csv",
            "ticker": t,
            "sector": SECTORS[t],
            "url": f"https://finance.yahoo.com/quote/{t}/history/",
            "provider": "Yahoo Finance via yfinance",
            "units": "USD adjusted close",
            "start_inclusive": source_start(t),
            "end_exclusive": END,
        }
        for t in ALL_TICKERS
    ]
    sources.append(
        {
            "filename": "XLF_2016_event.csv",
            "ticker": "XLF",
            "kind": "corporate_action",
            "url": "https://finance.yahoo.com/quote/XLF/history/",
            "provider": "Yahoo Finance via yfinance",
            "units": "USD closes and vendor action fields",
            "start_inclusive": "2016-09-15",
            "end_exclusive": "2016-09-23",
        }
    )
    return sources


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-cache", type=Path)
    args = parser.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    pinned = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else None
    yf.set_tz_cache_location(str(ROOT / ".cache/yfinance"))
    yf.config.debug.hide_exceptions = False
    records = []
    for spec in specifications():
        path = RAW / spec["filename"]
        checkpoint = path.with_suffix(path.suffix + ".json")
        prior = (
            next((m for m in pinned["sources"] if m["filename"] == path.name), None)
            if pinned
            else None
        )
        if prior is None and checkpoint.exists():
            prior = json.loads(checkpoint.read_text())
        if path.exists():
            if prior is None or digest(path) != prior["sha256"]:
                raise ValueError("Unverified or changed cache: " + path.name)
            records.append(prior)
            print("Verified", path.name, flush=True)
            continue
        partial = path.with_suffix(path.suffix + ".partial")
        meta = dict(spec)
        if args.from_cache:
            shutil.copyfile(args.from_cache / path.name, partial)
            if prior is None:
                raise ValueError("Cache restoration requires existing provenance pin")
        elif "ticker" in spec:
            start, end = spec["start_inclusive"], spec["end_exclusive"]
            h = yf.Ticker(spec["ticker"]).history(
                start=start,
                end=end,
                auto_adjust=False,
                actions=True,
            )
            series = (
                h[["Close", "Adj Close", "Dividends", "Stock Splits"]].copy()
                if spec.get("kind") == "corporate_action"
                else h["Adj Close"].rename(spec["ticker"])
            )
            series.index = series.index.tz_localize(None).normalize().rename("Date")
            if (
                not series.index.equals(expected_sessions(start, end))
                or not np.isfinite(series.to_numpy()).all()
                or (
                    (
                        series[["Close", "Adj Close"]]
                        if spec.get("kind") == "corporate_action"
                        else series
                    )
                    <= 0
                )
                .to_numpy()
                .any()
            ):
                raise ValueError("Incomplete or invalid ETF source: " + spec["ticker"])
            series.to_csv(partial, float_format="%.17g", lineterminator="\n")
            meta.update(
                rows=len(series),
                first_date=str(series.index[0].date()),
                last_date=str(series.index[-1].date()),
                yfinance_version=yf.__version__,
            )
        else:
            request = Request(spec["url"], headers={"User-Agent": "Mozilla/5.0 research"})
            with urlopen(request, timeout=90) as response:
                partial.write_bytes(response.read())
            frame = french_monthly(partial, spec["columns"])
            meta.update(
                rows=len(frame), first_month=str(frame.index[0]), last_month=str(frame.index[-1])
            )
        actual = digest(partial)
        if prior and actual != prior["sha256"]:
            raise ValueError(
                "Source vintage changed; retained .partial. Restore pinned cache, or explicitly document a new vintage: "
                + path.name
            )
        meta.update(sha256=actual, retrieved_at_utc=datetime.now(timezone.utc).isoformat())
        if prior:
            meta = prior
        partial.replace(path)
        checkpoint.write_text(json.dumps(meta, indent=2) + "\n")
        records.append(meta)
        print("Acquired", path.name, meta.get("last_month", meta.get("last_date")), flush=True)
    if not pinned:
        manifest = {
            "study_vintage": "2026-09-20",
            "universe": "State Street Select Sector SPDR ETFs; nine long-history primary, eleven-sector shorter supplement",
            "supersedes_manifest": "research/input_manifest_ishares.json",
            "factor_vintage": "Reuses the exact original pinned French archives",
            "start_inclusive": START,
            "end_exclusive": END,
            "sources": records,
            "availability": "Retrospective downloaded vintage, not point-in-time monthly release history",
            "redistribution": "Raw archives and price series stay local; source rights are separate from code license",
        }
        temp = MANIFEST.with_suffix(".partial")
        temp.write_text(json.dumps(manifest, indent=2) + "\n")
        temp.replace(MANIFEST)


if __name__ == "__main__":
    main()
