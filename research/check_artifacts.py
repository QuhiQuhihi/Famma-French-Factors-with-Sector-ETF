"""Check saved evidence, public-file boundaries, and independent full reconciliations."""

import argparse
import json
import re
import subprocess
from urllib.parse import unquote

import nbformat
import numpy as np
import pandas as pd

from research.data import FACTORS, ROOT, TICKERS, digest, load_panel


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
    for month, ticker in [("2012-01", "IYW"), ("2020-03", "IYE"), ("2026-07", "IYC")]:
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
