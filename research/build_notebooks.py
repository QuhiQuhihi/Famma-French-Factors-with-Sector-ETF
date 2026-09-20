"""Build and freshly execute the central research report and five focused chapters."""

import argparse
import json

import nbformat as nbf
from nbclient import NotebookClient
from nbconvert import HTMLExporter

from research.data import ROOT, digest
from research.topic_notebooks import topic_specs

M = nbf.v4.new_markdown_cell
C = nbf.v4.new_code_cell
SETUP = """from pathlib import Path
import sys
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / 'research/models.py').exists())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, Image
plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
RESULTS = ROOT / 'research/results'
FIGURES = ROOT / 'research/figures'
"""


def evidence_specs():
    return [
        {
            "slug": "04-economic-exposures",
            "title": "Read the economic exposure map",
            "intro": "A sector name is not a factor portfolio. Compare market, size, value, profitability, investment and momentum sensitivities in their original units, then separate fitted contributions from residual risk.",
            "cells": [
                M(
                    "## Question\nWhat does a technology or utilities label tell us about the fund's economic risks? This chapter uses the historical ten-fund panel, January 2007–July 2026. Full-sample estimates describe that sample; they do not reconstruct historical holdings."
                ),
                C(
                    "from research.data import FACTORS, load_panel\nfrom research.models import fit_factor_model, hac_ols\nx, y, audit = load_panel()\nexposures = pd.read_csv(RESULTS / 'exposures.csv').set_index('ticker')\ndisplay(exposures.round(3))"
                ),
                M(
                    "## Compare the factor sensitivities\nBeta 1 means a one-percentage-point factor return contributes one percentage point to the fitted ETF excess return, conditional on the other factors. A coefficient is not a portfolio weight."
                ),
                C("display(Image(filename=str(FIGURES / 'factor_map.png')))"),
                M(
                    "## Reconcile one fund in arithmetic return units\nIYW is a fixed teaching example, not the best-looking intercept selected from the table. The intercept, factor contributions and mean residual must reconcile to the mean ETF excess return. These annual arithmetic quantities do not compound to a wealth path."
                ),
                C(
                    "ticker = 'IYW'\nfit = fit_factor_model(x.to_numpy(), y[ticker].to_numpy())\ncontributions = pd.Series(fit.beta * x.mean().to_numpy(), index=FACTORS)\ncontributions['Intercept'] = fit.intercept\nresidual = y[ticker].to_numpy() - fit.predict(x.to_numpy())\ncontributions['Mean residual'] = residual.mean()\nassert np.isclose(contributions.sum(), y[ticker].mean(), atol=1e-12)\ndisplay((contributions * 1200).rename('Annual arithmetic contribution (%)').round(3).to_frame())"
                ),
                M(
                    "## How much precision does the value loading have?\nThe HAC interval is model-conditional and pointwise. Correlated factors can make one coefficient imprecise even when the fitted total return is useful."
                ),
                C(
                    "inference = hac_ols(x.to_numpy(), y[ticker].to_numpy(), lags=6)\nj = FACTORS.index('HML') + 1\nvalue_beta = inference.coefficients[j]\nvalue_se = inference.standard_errors[j]\ndisplay(pd.DataFrame({'HML beta': [value_beta], 'Pointwise lower 95%': [value_beta - 1.96*value_se], 'Pointwise upper 95%': [value_beta + 1.96*value_se]}).round(3))"
                ),
                M(
                    "## Interpretation\nEnergy exposure is not an oil futures position, utilities are not duration alone, and profitability beta is not an accounting screen applied to today's holdings. The fixed model and changing benchmark history limit those interpretations. [Data and fund identity](../../docs/01-data.md) explains the September 2021 changes."
                ),
            ],
        },
        {
            "slug": "05-rolling-attribution",
            "title": "Do the exposures travel to the next month?",
            "intro": "Freeze a 60-month exposure estimate, supply the next month's realized factors, and measure reconstruction error. Compare ridge's smaller coefficient changes with its uncertain tracking gain and PCR's cost of discarding directions.",
            "cells": [
                M(
                    "## Question and timing\nThe coefficients are fitted through t−1. Factor returns for t are observed afterward and enter the reconstruction. This is a test of exposure portability conditional on realized factors, not an ex ante return forecast. The source files are also revised vintages."
                ),
                C(
                    "from research.data import load_panel\nfrom research.run_study import rolling_reconstruction, comparison, summarize\nx, y, audit = load_panel()\npaths = rolling_reconstruction(x, y)\nassert (paths.train_end < paths.month).all()\ndisplay(summarize(paths).round(4))"
                ),
                M(
                    "## Paired panel comparison\nAverage squared percentage-point errors equally across all ten funds within each month. Resample those paired months in common 12-month blocks, retaining sector dependence."
                ),
                C(
                    "interval = comparison(paths)\ndisplay(pd.Series({k: interval[k] for k in ['estimate', 'lower95', 'upper95', 'relative_mse_reduction_pct', 'n']}).to_frame('Ridge minus OLS comparison'))\ndisplay(Image(filename=str(FIGURES / 'reconstruction.png')))"
                ),
                M(
                    "## Stable is not necessarily more accurate\nThe next figure uses all six raw slopes for the change statistic. PCR's lower dimensional subspace can move from one rolling fit to the next, so lower rank need not give smoother economic betas."
                ),
                C("display(Image(filename=str(FIGURES / 'stability.png')))"),
                M(
                    "## Retain the unfavorable sensitivities\nLarger shrinkage can remove useful exposures. Compare every fixed penalty/rank, then compare windows on the same January 2017–July 2026 dates. These diagnostics do not replace the primary 60-month specification."
                ),
                C(
                    "display(pd.read_csv(RESULTS / 'estimator_sensitivity.csv').round(4))\nwindows = pd.read_csv(RESULTS / 'window_sensitivity.csv')\ndisplay(windows[windows.scope.eq('common dates')][['window', 'estimate', 'lower95', 'upper95', 'relative_mse_reduction_pct']].round(4))"
                ),
                M(
                    "## Research decision\nThe primary interval spans zero. Ridge provides a useful controlled regularization example and smoother loadings, but this study does not establish a robust improvement in reconstruction. A shorter-window sensitivity supports a more favorable estimate; it remains supporting evidence after a fixed primary comparison. [Full results](../../docs/03-results.md) retain the complete record."
                ),
            ],
        },
    ]


def central_cells():
    h = json.loads((ROOT / "research/results/headline.json").read_text())
    return [
        M(
            "# When can we trust a sector ETF's factor exposures?\n\nFama–French factors, SVD geometry and robust attribution."
        ),
        M(
            f"## Findings\nAcross ten original broad iShares funds, fixed ridge reduces reconstruction MSE by **{h['relative_mse_reduction_pct']:.2f}%** relative to OLS. The paired difference is **{h['estimate']:.3f} pp²**, with a 95% block interval **[{h['lower95']:.3f}, {h['upper95']:.3f}]**. The interval spans zero. Ridge smooths exposures, but the evidence does not establish an improvement. PCR rank four performs worse on the point estimate.\n\nThe contribution is a disciplined comparison of attribution methods, not a trading strategy."
        ),
        M(
            "## Context and methods\nThe response is monthly simple ETF return less RF; the regressors are FF5 plus momentum in consistent decimal units. Full-sample fits describe history. Rolling estimates use only preceding observations, then reconstruct the next return with its **realized factors**. The primary window is 60 months, ridge lambda is 0.1 in mean-loss units, and PCR retains four singular directions.\n\n### Key assumptions\nYahoo adjusted close is a total-return proxy. Current-vintage factors and evolving fund benchmarks prevent a point-in-time holdings or deployment interpretation. The ten funds are selected survivors. [Protocol](research/PROTOCOL.md) records the design and bounded sensitivities."
        ),
        C(SETUP),
        M(
            "## Data\nThe common sample has 235 months, January 2007–July 2026. December 2006 supplies the first return denominator. Raw downloads stay local; source URLs, retrieval timestamps and checksums are public."
        ),
        C(
            "from research.data import load_panel\nx, y, audit = load_panel()\ndisplay(pd.Series({k: audit[k] for k in ['etfs','price_rows_per_etf','monthly_observations','first_month','last_month','missing_prices','missing_factors','fills']}).to_frame('Validated panel'))"
        ),
        M(
            "## Economic exposures\nThese are economic regression coefficients, not holdings weights. Market exposure differs across sectors; the remaining factors refine rather than replace that common equity risk."
        ),
        C(
            "display(Image(filename=str(FIGURES / 'factor_map.png')))\ndisplay(pd.read_csv(RESULTS / 'exposures.csv')[['ticker','r_squared','residual_vol_annual_pct']].round(3))"
        ),
        M(
            f"## SVD diagnoses the problem before changing the estimator\nThe median rolling condition number is **{h['condition_median']:.2f}**, ranging from **{h['condition_min']:.2f} to {h['condition_max']:.2f}**. These actual factor designs are not numerically near-singular. In the final training window, ridge attenuates each singular direction continuously; PCR deletes two directions. Small factor variance does not imply little information about a particular ETF."
        ),
        C("display(Image(filename=str(FIGURES / 'singular_geometry.png')))"),
        M(
            "## Recompute the primary comparison\nThe next cell fits every primary model again from the pinned inputs. The supplied factors from the target month make this conditional reconstruction, not a before-month prediction."
        ),
        C(
            "from research.run_study import rolling_reconstruction, comparison, summarize\npaths = rolling_reconstruction(x, y)\nhead = comparison(paths)\nrecorded = json.loads((RESULTS / 'headline.json').read_text())\nfor key in ['estimate','lower95','upper95','relative_mse_reduction_pct']:\n    assert np.isclose(head[key], recorded[key], rtol=1e-10, atol=1e-12)\ndisplay(summarize(paths).round(4))\ndisplay(pd.Series({k: head[k] for k in ['estimate','lower95','upper95','n']}).to_frame('Paired MSE difference (pp²)'))"
        ),
        C("display(Image(filename=str(FIGURES / 'reconstruction.png')))"),
        M(
            "## Coefficient stability and reconstruction accuracy are different\nRidge lowers the RMS change in the six economic betas. PCR's changing truncated subspace produces more unstable raw exposures in this sample. Neither smoothness nor explained factor variance is itself evidence of better attribution."
        ),
        C("display(Image(filename=str(FIGURES / 'stability.png')))"),
        M(
            "## Residual means and uncertainty\nThe intervals are six-lag HAC, pointwise and normal-approximation. No intercept survives Holm adjustment across the ten ETFs at 5%. This is not proof that every alpha is zero; precision, omitted factors and changing betas matter."
        ),
        C(
            "display(Image(filename=str(FIGURES / 'alpha_intervals.png')))\ndisplay(pd.read_csv(RESULTS / 'alpha.csv')[['ticker','alpha_arithmetic_annual_pct','lower95_arithmetic_annual_pct','upper95_arithmetic_annual_pct','holm_p_value']].round(3))"
        ),
        M(
            "## Sensitivities without choosing a winner\nKeep the stronger and weaker penalties, all retained ranks, and windows on common dates. The favorable 36-month result is supporting evidence; it does not rewrite the prespecified primary result."
        ),
        C(
            "display(pd.read_csv(RESULTS / 'estimator_sensitivity.csv').round(4))\nwindows = pd.read_csv(RESULTS / 'window_sensitivity.csv')\ndisplay(windows[windows.scope.eq('common dates')][['window','estimate','lower95','upper95','relative_mse_reduction_pct']].round(4))"
        ),
        M(
            "## Takeaways\nUse SVD to understand identification, preserve economic units, and test whether regularization earns its bias. In this vintage, fixed ridge smooths exposures and has a modest, uncertain reconstruction advantage; aggressive shrinkage or truncation can remove useful information. More reliable attribution would require independent price reconciliation, dated holdings and a genuinely later evaluation period.\n\nExplore the [five chapters](README.md#explore-the-research), [sources](research/SOURCES.md), [full evidence](docs/03-results.md), and [next experiments](research/RESEARCH_AGENDA.md)."
        ),
    ]


def execute(path, cells):
    book = nbf.v4.new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.12"},
        },
    )
    NotebookClient(
        book,
        timeout=300,
        kernel_name="python3",
        resources={"metadata": {"path": str(ROOT)}},
        record_timing=False,
    ).execute()
    nbf.validate(book)
    # Stable cell ids make regenerated notebooks easier to review.
    for i, cell in enumerate(book.cells):
        cell.id = f"cell-{i:03d}"
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".partial")
    nbf.write(book, temp)
    temp.replace(path)
    preview = (
        ROOT
        / "research/preview"
        / ("study.html" if path.parent == ROOT else path.parent.name + ".html")
    )
    preview.parent.mkdir(exist_ok=True)
    preview.write_text(HTMLExporter().from_notebook_node(book)[0])
    code_count = sum(cell.cell_type == "code" for cell in book.cells)
    image_count = sum(
        "image/png" in out.get("data", {}) for c in book.cells for out in c.get("outputs", [])
    )
    print(
        f"Executed {path.relative_to(ROOT)}: {code_count} code cells, {image_count} figures",
        flush=True,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="Topic slug, or study; defaults to all")
    args = parser.parse_args()
    for spec in topic_specs() + evidence_specs():
        if args.only and args.only != spec["slug"]:
            continue
        folder = ROOT / "topics" / spec["slug"]
        folder.mkdir(parents=True, exist_ok=True)
        prose = [
            f"# {spec['title']}",
            spec["intro"],
            "[Open the executed notebook](study.ipynb) · [Research overview](../../README.md)",
            "This note outlines the research argument. Worked calculations and tables referenced below are in the linked notebook; selected figures are reproduced at the end of this note.",
        ]
        prose.extend(c.source for c in spec["cells"] if c.cell_type == "markdown")
        previews = {
            "01-return-alignment": ["topic_return_alignment.png"],
            "02-svd-geometry": ["topic_svd_filters.png", "topic_svd_stability.png"],
            "03-alpha-uncertainty": ["topic_alpha_uncertainty.png"],
            "04-economic-exposures": ["factor_map.png"],
            "05-rolling-attribution": ["reconstruction.png", "stability.png"],
        }
        prose.append("## Evidence preview")
        prose.extend(
            f"![{spec['title']}](../../research/figures/{name})" for name in previews[spec["slug"]]
        )
        prose.append(
            "## Further reading\n[Data](../../docs/01-data.md) · [Methods](../../docs/02-methods.md) · [Source register](../../research/SOURCES.md)"
        )
        (folder / "README.md").write_text("\n\n".join(prose) + "\n")
        execute(
            folder / "study.ipynb",
            [M(f"# {spec['title']}\n\n{spec['intro']}"), C(SETUP), *spec["cells"]],
        )
    if args.only in (None, "study"):
        execute(ROOT / "study.ipynb", central_cells())
    if args.only is None:
        artifacts = [
            ROOT / "study.ipynb",
            *sorted((ROOT / "topics").glob("*/*")),
            *sorted((ROOT / "research/figures").glob("topic_*.png")),
        ]
        (ROOT / "research/notebook_manifest.json").write_text(
            json.dumps(
                {
                    "source_and_code": {
                        str(p.relative_to(ROOT)): digest(p)
                        for p in [
                            *sorted((ROOT / "research").glob("*.py")),
                            ROOT / "research/input_manifest.json",
                            ROOT / "research/results/run_metadata.json",
                            ROOT / "pyproject.toml",
                            ROOT / "uv.lock",
                        ]
                    },
                    "artifacts": {
                        str(p.relative_to(ROOT)): digest(p) for p in artifacts if p.is_file()
                    },
                },
                indent=2,
            )
            + "\n"
        )


if __name__ == "__main__":
    main()
