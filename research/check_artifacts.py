"""Check saved evidence, public-file boundaries, and independent full reconciliations."""

import argparse
import json
import re
import subprocess
from urllib.parse import unquote

import nbformat
import numpy as np
import pandas as pd

from research.data import ALL_TICKERS, FACTORS, RAW, ROOT, SECTORS, TICKERS, digest, load_panel


def verify_manifest(path, full=False):
    manifest = json.loads(path.read_text())
    for section in ("source_and_code", "artifacts"):
        for name, expected in manifest[section].items():
            if "/private/" in name and not full:
                continue
            target = ROOT / name
            if not target.is_file() or digest(target) != expected:
                raise AssertionError("Stale or missing artifact: " + name)


def public_files():
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    files = sorted(set(result.stdout.decode().split("\0")) - {""})
    prohibited = []
    for name in files:
        p = ROOT / name
        if not p.exists():
            continue
        parts = p.relative_to(ROOT).parts
        base = p.name.lower()
        if (
            any(
                part
                in {
                    ".venv",
                    ".env",
                    ".codex",
                    ".agents",
                    "private",
                    "private-legacy",
                    "raw",
                    "preview",
                    "__pycache__",
                }
                for part in parts
            )
            or base.startswith(("agents.", "codex."))
            or base == "renovation_agent_instructions.md"
        ):
            prohibited.append(name)
    if prohibited:
        raise AssertionError(
            "Private paths present in proposed public tree: " + ", ".join(prohibited)
        )
    return [ROOT / name for name in files if (ROOT / name).is_file()]


def local_links(files):
    checked = 0
    for path in files:
        if path.suffix == ".md":
            text = path.read_text()
        elif path.suffix == ".ipynb":
            text = "\n".join(
                c.source
                for c in nbformat.read(path, as_version=4).cells
                if c.cell_type == "markdown"
            )
        else:
            continue
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            if target.startswith(("https://", "http://", "mailto:", "#")):
                continue
            target = unquote(target.split("#")[0])
            if not (path.parent / target).exists():
                raise AssertionError(f"Broken local link in {path.relative_to(ROOT)}: {target}")
            checked += 1
    return checked


def full_reconciliation():
    x, y, audit = load_panel()
    assert audit == json.loads((ROOT / "research/results/data_audit.json").read_text())
    paths = pd.read_csv(ROOT / "research/results/private/rolling_60.csv")
    assert not paths.duplicated(["month", "ticker", "model"]).any()
    target = pd.PeriodIndex(paths.month, freq="M")
    assert (pd.PeriodIndex(paths.train_end, freq="M") == target - 1).all()
    assert (pd.PeriodIndex(paths.train_start, freq="M") == target - 60).all()
    assert paths.groupby(["month", "model"]).ticker.nunique().eq(len(TICKERS)).all()
    errors = ((paths.actual - paths.prediction) * 100) ** 2
    np.testing.assert_allclose(errors, paths.squared_error_pp2, rtol=1e-11, atol=1e-10)
    # Independently use raw-coordinate least squares and direct ridge equations.
    for month, ticker in [("2012-01", "XLK"), ("2020-03", "XLE"), ("2026-07", "XLY")]:
        pos = x.index.get_loc(pd.Period(month, freq="M"))
        train = x.iloc[pos - 60 : pos].to_numpy()
        response = y[ticker].iloc[pos - 60 : pos].to_numpy()
        test = x.iloc[pos].to_numpy()
        direct = np.linalg.lstsq(np.column_stack([np.ones(60), train]), response, rcond=None)[0]
        ols_prediction = np.r_[1, test] @ direct
        z = (train - train.mean(axis=0)) / train.std(axis=0, ddof=0)
        slopes = np.linalg.solve(z.T @ z + 60 * 0.1 * np.eye(6), z.T @ (response - response.mean()))
        ridge_prediction = (
            response.mean() + ((test - train.mean(axis=0)) / train.std(axis=0, ddof=0)) @ slopes
        )
        for label, prediction in [("OLS", ols_prediction), ("Ridge 0.1", ridge_prediction)]:
            row = paths[
                (paths.month == month) & (paths.ticker == ticker) & (paths.model == label)
            ].iloc[0]
            np.testing.assert_allclose(prediction, row.prediction, atol=1e-10)
            np.testing.assert_allclose(
                y.loc[pd.Period(month, freq="M"), ticker], row.actual, atol=1e-12
            )
    losses = paths.groupby(["month", "model"]).squared_error_pp2.mean().unstack()
    difference = (losses["Ridge 0.1"] - losses.OLS).to_numpy()
    h = json.loads((ROOT / "research/results/headline.json").read_text())
    np.testing.assert_allclose(difference.mean(), h["estimate"], atol=1e-10)
    rng = np.random.default_rng(20260920)
    n, block = len(difference), 12
    starts = rng.integers(0, n, size=(2000, int(np.ceil(n / block))))
    # Explicit block concatenation provides a separate implementation path.
    means = [
        difference[
            np.concatenate([np.arange(start, start + block) % n for start in row])[:n]
        ].mean()
        for row in starts
    ]
    np.testing.assert_allclose(
        np.quantile(means, [0.025, 0.975]), [h["lower95"], h["upper95"]], atol=1e-10
    )
    exposures = pd.read_csv(ROOT / "research/results/exposures.csv").set_index("ticker")
    for ticker in TICKERS:
        beta = np.linalg.lstsq(np.column_stack([np.ones(len(x)), x]), y[ticker], rcond=None)[0]
        np.testing.assert_allclose(
            beta[1:], exposures.loc[ticker, FACTORS].to_numpy(dtype=float), atol=1e-10
        )
        assert exposures.loc[ticker, "sector"] == SECTORS[ticker]
    ex, ey, extended_audit = load_panel(extended=True)
    assert extended_audit == json.loads(
        (ROOT / "research/results/extended_data_audit.json").read_text()
    )
    assert len(ex) == 97 and list(ey.columns) == ALL_TICKERS
    extension = pd.read_csv(ROOT / "research/results/private/extended_rolling_60.csv")
    assert extension.month.nunique() == 37
    assert extension.month.min() == "2023-07"
    assert not extension.duplicated(["month", "ticker", "model"]).any()
    assert extension.groupby(["month", "model"]).ticker.nunique().eq(11).all()
    extended_target = pd.PeriodIndex(extension.month, freq="M")
    assert (pd.PeriodIndex(extension.train_end, freq="M") == extended_target - 1).all()
    assert (pd.PeriodIndex(extension.train_start, freq="M") == extended_target - 60).all()
    np.testing.assert_allclose(
        ((extension.actual - extension.prediction) * 100) ** 2,
        extension.squared_error_pp2,
        atol=1e-10,
    )
    observed = ey.stack().rename("expected_actual")
    observed.index = observed.index.set_names(["month", "ticker"])
    observed = observed.reset_index()
    observed["month"] = observed.month.astype(str)
    joined = extension.merge(observed, on=["month", "ticker"], validate="many_to_one")
    assert len(joined) == len(extension)
    np.testing.assert_allclose(joined.actual, joined.expected_actual, atol=1e-12)
    # On the same recent dates the original nine must receive identical fits:
    # adding other targets cannot change their independent regressions.
    recent = extension[extension.ticker.isin(TICKERS)].merge(
        paths, on=["month", "ticker", "model"], validate="one_to_one", suffixes=("_ext", "_long")
    )
    assert len(recent) == 37 * 9 * 5
    np.testing.assert_allclose(recent.prediction_ext, recent.prediction_long, atol=1e-12)
    extended_head = json.loads((ROOT / "research/results/extended_headline.json").read_text())
    for tickers, result in [(ALL_TICKERS, extended_head), (TICKERS, extended_head["recent_nine"])]:
        subset = extension[extension.ticker.isin(tickers)]
        monthly = subset.groupby(["month", "model"]).squared_error_pp2.mean().unstack()
        differences = (monthly["Ridge 0.1"] - monthly.OLS).to_numpy()
        np.testing.assert_allclose(differences.mean(), result["estimate"], atol=1e-10)
        starts = np.random.default_rng(20260920).integers(0, 37, size=(2000, 4))
        values = [
            differences[np.concatenate([np.arange(s, s + 12) % 37 for s in row])[:37]].mean()
            for row in starts
        ]
        np.testing.assert_allclose(
            np.quantile(values, [0.025, 0.975]), [result["lower95"], result["upper95"]], atol=1e-10
        )
    expanded = pd.read_csv(ROOT / "research/results/extended_exposures.csv").set_index("ticker")
    for ticker in ALL_TICKERS:
        direct = np.linalg.lstsq(np.column_stack([np.ones(len(ex)), ex]), ey[ticker], rcond=None)[0]
        np.testing.assert_allclose(
            direct[1:], expanded.loc[ticker, FACTORS].to_numpy(dtype=float), atol=1e-10
        )
        assert expanded.loc[ticker, "sector"] == SECTORS[ticker]
    event = pd.read_csv(RAW / "XLF_2016_event.csv", index_col=0)
    event_audit = json.loads((ROOT / "research/results/corporate_action_audit.json").read_text())
    np.testing.assert_allclose(
        100 * (event.loc["2016-09-19", "Adj Close"] / event.loc["2016-09-16", "Adj Close"] - 1),
        event_audit["event_adjusted_return_pct"],
        atol=1e-12,
    )
    assert event_audit["manual_distribution_added"] is False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    files = public_files()
    links = local_links(files)
    verify_manifest(ROOT / "research/results/run_metadata.json", full=args.full)
    verify_manifest(ROOT / "research/notebook_manifest.json")
    books = [ROOT / "study.ipynb", *sorted((ROOT / "topics").glob("*/study.ipynb"))]
    assert len(books) == 6
    code_cells, images = 0, 0
    readme = (ROOT / "README.md").read_text()
    for path in books:
        book = nbformat.read(path, as_version=4)
        nbformat.validate(book)
        expected_count = 0
        book_images = 0
        for cell in book.cells:
            if cell.cell_type == "code":
                expected_count += 1
                assert cell.execution_count == expected_count, (
                    f"Unexecuted or out-of-order cell: {path}"
                )
                code_cells += 1
                for output in cell.outputs:
                    assert output.output_type != "error"
                    book_images += "image/png" in output.get("data", {})
        assert book_images > 0
        images += book_images
        if path.parent != ROOT:
            for target in [path, path.parent / "README.md"]:
                assert str(target.relative_to(ROOT)) in readme
    h = json.loads((ROOT / "research/results/headline.json").read_text())
    for text in [f"{h['relative_mse_reduction_pct']:.2f}%", f"{h['condition_median']:.2f}"]:
        assert text in readme, "README headline stale: " + text
    if args.full:
        full_reconciliation()
    print(
        f"Passed: {len(books)} executed notebooks, {code_cells} code cells, {images} figures; {links} local links; provenance and public file checks"
        + ("; full independent reconciliation" if args.full else "")
    )


if __name__ == "__main__":
    main()
