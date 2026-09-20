"""Build and freshly execute the central research report and five focused chapters."""

import argparse
import json

import nbformat as nbf
from nbclient import NotebookClient
from nbconvert import HTMLExporter

from research.data import ROOT, TICKERS, digest
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


def comparison_text(head):
    """Describe the saved comparison without assuming its sign or significance."""
    reduction = head["relative_mse_reduction_pct"]
    change = (
        f"{abs(reduction):.2f}% lower"
        if reduction > 0
        else f"{abs(reduction):.2f}% higher"
        if reduction < 0
        else "unchanged"
    )
    if head["upper95"] < 0:
        conclusion = (
            "The paired interval supports lower reconstruction error for ridge in this panel."
        )
    elif head["lower95"] > 0:
        conclusion = (
            "The paired interval supports higher reconstruction error for ridge in this panel."
        )
    else:
        conclusion = "The paired interval includes zero and does not resolve a difference."
    return (
        f"Ridge's reconstruction MSE is **{change}** relative to OLS on the point estimate. "
        f"The paired ridge-minus-OLS difference is **{head['estimate']:.3f} pp²**, "
        f"with a 95% block interval **[{head['lower95']:.3f}, {head['upper95']:.3f}]**. "
        + conclusion
    )


def evidence_specs():
    head = json.loads((ROOT / "research/results/headline.json").read_text())
    primary_count = len(TICKERS)
    return [
        {
            "slug": "04-economic-exposures",
            "title": "Read the economic exposure map",
            "intro": "A sector name is not a factor portfolio. Compare market, size, value, profitability, investment and momentum sensitivities in their original units, then separate fitted contributions from residual risk.",
            "cells": [
                M(
                    f"## Question\nWhat does a technology or utilities label tell us about the fund's economic risks? The primary panel uses {primary_count} original State Street Select Sector SPDR funds over January 2007–July 2026. A separate, shorter panel includes all eleven current sectors. Full-sample estimates describe their stated samples; they do not reconstruct historical holdings or backcast today's sector definitions."
                ),
                C(
                    "from research.data import FACTORS, SECTORS, load_panel\nfrom research.models import fit_factor_model, hac_ols\nx, y, audit = load_panel()\nexposures = pd.read_csv(RESULTS / 'exposures.csv').drop(columns='ticker').set_index('sector')\ndisplay(exposures.round(3))"
                ),
                M(
                    "## Compare the factor sensitivities\nBeta 1 means a one-percentage-point factor return contributes one percentage point to the fitted ETF excess return, conditional on the other factors. A coefficient is not a portfolio weight."
                ),
                C("display(Image(filename=str(FIGURES / 'factor_map.png')))"),
                M(
                    "## Reconcile the Technology sector in arithmetic return units\nTechnology is a fixed teaching example. The intercept, factor contributions and mean residual must reconcile to the mean ETF excess return. These annual arithmetic quantities do not compound to a wealth path. The sector fund's composition can change even when its current display name stays the same."
                ),
                C(
                    "ticker = 'XLK'\nfit = fit_factor_model(x.to_numpy(), y[ticker].to_numpy())\ncontributions = pd.Series(fit.beta * x.mean().to_numpy(), index=FACTORS)\ncontributions['Intercept'] = fit.intercept\nresidual = y[ticker].to_numpy() - fit.predict(x.to_numpy())\ncontributions['Mean residual'] = residual.mean()\nassert np.isclose(contributions.sum(), y[ticker].mean(), atol=1e-12)\ndisplay((contributions * 1200).rename(f'{SECTORS[ticker]}: annual arithmetic contribution (%)').round(3).to_frame())"
                ),
                M(
                    "## How much precision does the value loading have?\nThe HAC interval is model-conditional and pointwise. Correlated factors can make one coefficient imprecise even when the fitted total return is useful."
                ),
                C(
                    "inference = hac_ols(x.to_numpy(), y[ticker].to_numpy(), lags=6)\nj = FACTORS.index('HML') + 1\nvalue_beta = inference.coefficients[j]\nvalue_se = inference.standard_errors[j]\ndisplay(pd.DataFrame({'HML beta': [value_beta], 'Pointwise lower 95%': [value_beta - 1.96*value_se], 'Pointwise upper 95%': [value_beta + 1.96*value_se]}).round(3))"
                ),
                M(
                    "## Include all eleven sectors without inventing their histories\nReal Estate and Communication Services began trading later than the original nine funds. The common eleven-sector sample begins with July 2018 returns and ends in July 2026: 97 monthly observations. The next map estimates every sector on those same dates. It supplements the longer primary panel; comparisons between the maps combine a universe change with a sample-period change."
                ),
                C(
                    "extended_x, extended_y, extended_audit = load_panel(extended=True)\nassert len(extended_x) == 97 and extended_y.shape[1] == 11\ndisplay(Image(filename=str(FIGURES / 'extended_factor_map.png')))\nextended_exposures = pd.read_csv(RESULTS / 'extended_exposures.csv').drop(columns='ticker').set_index('sector')\ndisplay(extended_exposures.round(3))"
                ),
                M(
                    "## Read the shorter reconstruction comparison in its own scope\nA 60-month fit leaves only 37 evaluation months, July 2023–July 2026, in this eleven-sector panel. The table also includes the original nine sectors on those same recent dates. This recent-nine control separates the effect of adding Real Estate and Communication Services from the change in evaluation dates. Neither recent-panel estimate is directly comparable with the long-sample primary headline. These are equally weighted sector error summaries, not portfolio weights. A 120-month fitting window is infeasible, and no pre-inception ETF returns are supplied."
                ),
                C(
                    "extended_head = json.loads((RESULTS / 'extended_headline.json').read_text())\nrecent_nine = extended_head['recent_nine']\nassert extended_head['n'] == recent_nine['n'] == 37\ndisplay(pd.read_csv(RESULTS / 'extended_summary.csv').round(4))\ndisplay(pd.DataFrame([extended_head, recent_nine], index=['All eleven sectors, recent dates', 'Original nine sectors, same recent dates'])[['estimate', 'lower95', 'upper95', 'relative_mse_reduction_pct', 'n']].rename(columns={'estimate': 'Ridge minus OLS MSE (pp²)', 'n': 'Evaluation months'}).round(4))"
                ),
                M(
                    "## Interpretation\nEnergy exposure is not an oil futures position, utilities are not duration alone, and profitability beta is not an accounting screen applied to today's holdings. The fixed model and changing benchmark history limit those interpretations. [Data and fund identity](../../docs/01-data.md) discusses the 2016 Real Estate separation and 2018 Communication Services reclassification. Current sector names aid reading; they do not imply an unchanged historical mandate."
                ),
            ],
        },
        {
            "slug": "05-rolling-attribution",
            "title": "Do the exposures travel to the next month?",
            "intro": "Freeze a 60-month exposure estimate, supply the next month's realized factors, and measure reconstruction error. Compare coefficient movement with tracking accuracy, then examine the bias introduced by shrinkage and discarded directions.",
            "cells": [
                M(
                    "## Question and timing\nThe coefficients are fitted through t−1. Factor returns for t are observed afterward and enter the reconstruction. This is a test of exposure portability conditional on realized factors, not an ex ante return forecast. The source files are also revised vintages."
                ),
                C(
                    "from research.data import load_panel\nfrom research.run_study import rolling_reconstruction, comparison, summarize\nx, y, audit = load_panel()\npaths = rolling_reconstruction(x, y)\nassert (paths.train_end < paths.month).all()\ndisplay(summarize(paths).round(4))"
                ),
                M(
                    f"## Paired panel comparison\nAverage squared percentage-point errors equally across the {primary_count} primary State Street sector funds within each month. Resample those paired months in common 12-month blocks, retaining sector dependence."
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
                    "## Research decision\n"
                    + comparison_text(head)
                    + " Coefficient stability and bounded sensitivities describe other aspects of the fit; none replaces this primary endpoint. The eleven-sector extension has a shorter evaluation period and remains supplemental. [Full results](../../docs/03-results.md) retain the complete record."
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
            f"## Findings\nThe primary experiment covers {h['sector_count']} original State Street Select Sector SPDR funds. "
            + comparison_text(h)
            + "\n\nAn eleven-sector extension includes Real Estate and Communication Services on a shorter common sample. The contribution is a disciplined comparison of attribution methods; no trading strategy is evaluated."
        ),
        M(
            "## Context and methods\nThe response is monthly simple ETF return less RF; the regressors are FF5 plus momentum in consistent decimal units. Full-sample fits describe history. Rolling estimates use only preceding observations, then reconstruct the next return with its **realized factors**. The primary window is 60 months, ridge lambda is 0.1 in mean-loss units, and PCR retains four singular directions.\n\n### Key assumptions\nYahoo adjusted close is a total-return proxy. Current-vintage factors and evolving fund benchmarks prevent a point-in-time holdings or deployment interpretation. The nine long-history funds are selected survivors; their past holdings need not match today's sector definitions. The switch to State Street funds follows inspection of the earlier iShares result. The [protocol](research/PROTOCOL.md) records the amended universe and bounded comparisons."
        ),
        C(SETUP),
        M(
            f"## Data\nThe primary sample has {h['sample_months']} months, January 2007–July 2026. December 2006 supplies the first return denominator. Its 60-month windows leave {h['evaluation_months']} evaluation months, January 2012–July 2026. Raw downloads stay local; source URLs, retrieval timestamps and checksums are public."
        ),
        C(
            "from research.data import load_panel\nx, y, audit = load_panel()\ndisplay(pd.Series({k: audit[k] for k in ['etfs','price_rows_per_etf','monthly_observations','first_month','last_month','missing_prices','missing_factors','fills']}).to_frame('Validated panel'))"
        ),
        M(
            "## Economic exposures\nThese are economic regression coefficients, not holdings weights. Market exposure differs across sectors; the remaining factors refine rather than replace that common equity risk."
        ),
        C(
            "display(Image(filename=str(FIGURES / 'factor_map.png')))\ndisplay(pd.read_csv(RESULTS / 'exposures.csv')[['sector','r_squared','residual_vol_annual_pct']].set_index('sector').round(3))"
        ),
        M(
            f"## SVD diagnoses the problem before changing the estimator\nThe median rolling condition number is **{h['condition_median']:.2f}**, ranging from **{h['condition_min']:.2f} to {h['condition_max']:.2f}**. These diagnostics describe the factor design rather than the issuer's labels. In the final training window, ridge attenuates each singular direction continuously; PCR deletes two directions. Small factor variance does not imply little information about a particular ETF."
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
            "## Coefficient stability and reconstruction accuracy are different\nCompare the measured RMS change in all six economic betas with reconstruction error. Shrinkage may reduce coefficient movement, while PCR's truncated subspace can itself move between fits. Neither smoothness nor explained factor variance is sufficient evidence of better attribution. The Technology example retains actual historical changes to the fund's composition."
        ),
        C("display(Image(filename=str(FIGURES / 'stability.png')))"),
        M(
            f"## Residual means and uncertainty\nThe intervals are six-lag HAC, pointwise and normal-approximation. **{h['holm_rejections_5pct']} of {h['sector_count']}** primary-panel intercepts have Holm-adjusted p-values below 5%. The testing family contains these {h['sector_count']} descriptive intercepts. Rejection remains model-relative, and non-rejection does not prove zero alpha; precision, omitted factors and changing betas matter."
        ),
        C(
            "display(Image(filename=str(FIGURES / 'alpha_intervals.png')))\ndisplay(pd.read_csv(RESULTS / 'alpha.csv')[['sector','alpha_arithmetic_annual_pct','lower95_arithmetic_annual_pct','upper95_arithmetic_annual_pct','holm_p_value']].set_index('sector').round(3))"
        ),
        M(
            "## Sensitivities without choosing a winner\nKeep the stronger and weaker penalties, all retained ranks, and windows on common dates. Each favorable or unfavorable sensitivity remains supporting evidence; it does not rewrite the fixed primary comparison."
        ),
        C(
            "display(pd.read_csv(RESULTS / 'estimator_sensitivity.csv').round(4))\nwindows = pd.read_csv(RESULTS / 'window_sensitivity.csv')\ndisplay(windows[windows.scope.eq('common dates')][['window','estimate','lower95','upper95','relative_mse_reduction_pct']].round(4))"
        ),
        M(
            "## All eleven sectors on their common observed history\nReal Estate and Communication Services have shorter ETF histories. This supplemental panel therefore uses July 2018–July 2026: 97 complete monthly returns for every sector. The map uses the same dates for all eleven funds; no earlier observations are backfilled. Its estimates cannot be compared with the long-panel map as though only the universe changed."
        ),
        C(
            "extended_x, extended_y, extended_audit = load_panel(extended=True)\nassert len(extended_x) == 97 and extended_y.shape[1] == 11\ndisplay(Image(filename=str(FIGURES / 'extended_factor_map.png')))\ndisplay(pd.read_csv(RESULTS / 'extended_exposures.csv').drop(columns='ticker').set_index('sector').round(3))"
        ),
        M(
            "## A shorter supplemental reconstruction window\nThe eleven-sector extension leaves 37 evaluation months, July 2023–July 2026, after the same 60-month fitting window. The original nine sectors are also evaluated on those same recent dates, providing a control that separates adding sectors from changing the evaluation period. The two recent-panel estimates are not directly comparable with the long-sample primary headline and do not replace it. Each panel averages sector errors; these are not portfolio allocations. There are too few observations for a 120-month fit."
        ),
        C(
            "extended_head = json.loads((RESULTS / 'extended_headline.json').read_text())\nrecent_nine = extended_head['recent_nine']\nassert extended_head['n'] == recent_nine['n'] == 37\ndisplay(pd.read_csv(RESULTS / 'extended_summary.csv').round(4))\ndisplay(pd.DataFrame([extended_head, recent_nine], index=['All eleven sectors, recent dates', 'Original nine sectors, same recent dates'])[['estimate', 'lower95', 'upper95', 'relative_mse_reduction_pct', 'n']].rename(columns={'estimate': 'Ridge minus OLS MSE (pp²)', 'n': 'Evaluation months'}).round(4))"
        ),
        M(
            "## Takeaways\n"
            + comparison_text(h)
            + " Use SVD to understand identification, preserve economic units, and test whether regularization earns its bias. The eleven-sector extension broadens coverage while shortening the observed history. More reliable attribution would require independent price reconciliation, dated holdings and a genuinely later evaluation period.\n\nExplore the [five chapters](README.md#explore-the-research), [sources](research/SOURCES.md), [full evidence](docs/03-results.md), and [next experiments](research/RESEARCH_AGENDA.md)."
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
            "04-economic-exposures": ["factor_map.png", "extended_factor_map.png"],
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
