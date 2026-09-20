# When Can We Trust a Sector ETF's Factor Exposures?

**Fama–French factors, SVD geometry, and robust attribution.**

Sector labels tell us what a fund owns in broad terms. Factor exposures ask a different
question: which common return patterns explain its behavior, and how reliably can we
separate those patterns? Technology, financials and utilities can share market risk
while responding very differently to value, profitability, investment and momentum.

This project develops that question through ten broad iShares ETFs from the original
sector study. It connects economic interpretation to the geometry of regression:
**when factors overlap, does regularizing their exposures improve attribution—or
merely make the coefficients look calmer?**

![Economic factor exposures across sector ETFs](research/figures/factor_map.png)

*Full-sample FF5 + momentum OLS, January 2007–July 2026. Coefficients are in economic
return units, not portfolio weights or causal explanations of holdings.*

## Explore the research

Each chapter has a short research note and an executed notebook. The first three
isolate mechanisms with constructed examples; the last two apply them to the observed
ETF panel. Start with the question that interests you, or follow the sequence.

| Idea | What you can investigate | Read and experiment |
| --- | --- | --- |
| **Get excess returns right** | Why percentage points, log returns, incomplete months and RF alignment can change the question before a regression starts | [Note](topics/01-return-alignment/README.md) · [Notebook](topics/01-return-alignment/study.ipynb) |
| **See regression through SVD** | How small singular directions amplify perturbations, why SVD OLS is still OLS, and how ridge differs from truncation | [Note](topics/02-svd-geometry/README.md) · [Notebook](topics/02-svd-geometry/study.ipynb) |
| **Challenge apparent alpha** | What a residual intercept means, how dependence affects uncertainty, and why ten ETF tests form a testing family | [Note](topics/03-alpha-uncertainty/README.md) · [Notebook](topics/03-alpha-uncertainty/study.ipynb) |
| **Read the economic exposure map** | Compare sector sensitivities and reconcile factor contributions, the intercept and residual return in consistent units | [Note](topics/04-economic-exposures/README.md) · [Notebook](topics/04-economic-exposures/study.ipynb) |
| **Test whether exposures travel** | Freeze earlier estimates, reconstruct the next month with realized factors, and compare stability, error and bounded sensitivities | [Note](topics/05-rolling-attribution/README.md) · [Notebook](topics/05-rolling-attribution/study.ipynb) |

[Combined research notebook](study.ipynb) · [Data and fund identity](docs/01-data.md) ·
[Methods](docs/02-methods.md) · [Detailed findings](docs/03-results.md)

## What survives the comparison?

The fixed experiment uses 60-month rolling windows and 175 subsequent months,
January 2012–July 2026. OLS, ridge and principal-component regression (PCR) receive
the same six factors, dates and unpenalized intercept. Market-only and FF5 regressions
provide simpler economic baselines.

| Observation | Research implication |
| --- | --- |
| Ridge reduces mean squared reconstruction error by **1.93%**; paired difference **−0.177 pp²**, 95% block interval **[−0.398, +0.028]** | A modest point-estimate improvement; the primary evidence remains inconclusive |
| Ridge reduces RMS monthly beta movement from **0.0434 to 0.0347** | Smoother exposures are measurable, but smoothness alone does not establish accuracy |
| Four-component PCR has **3.30%** monthly reconstruction RMSE, versus **3.03%** for OLS | Discarding low-variance factor directions can discard useful information |
| Median rolling condition number is **2.94** | Diagnose actual factor geometry before presuming a severe numerical problem |
| **0 of 10** intercepts survive Holm adjustment at 5% | These regressions do not establish a sector-alpha discovery |

![Conditional reconstruction and paired error path](research/figures/reconstruction.png)

The evaluation supplies each target month's **realized factor returns** after fitting
the exposures. It measures conditional reconstruction, **not a return forecast known
before the month or a trading strategy**. The block interval resamples paired monthly
losses and preserves common sector shocks; it remains conditional on this historical
sample and research design.

## Where robustness matters

The study keeps return units consistent, fits transformations inside each training
window, preserves the fixed primary comparison and reports unfavorable sensitivities.
Stronger shrinkage performs worse here; a shorter-window comparison is more favorable
to ridge but does not replace the primary result. The full tables remain available
in [research/results](research/results/).

Changing exposures also have economic causes. Several funds changed benchmarks in
September 2021; today's sector label does not describe every historical holding.
French factors and adjusted prices are retrospective vintages, and the universe
contains surviving funds. Those limits prevent a point-in-time deployment claim.

The contribution is an inspectable link between **economic factor interpretation,
numerical identification, and empirical validation**. The [next experiments](research/RESEARCH_AGENDA.md)
explain what holdings, independent price data and later observations could resolve.

## Research record

[Protocol](research/PROTOCOL.md) · [Sources](research/SOURCES.md) ·
[Input manifest](research/input_manifest.json) · [Legacy audit](research/AUDIT.md) ·
[Validation](research/ACCEPTANCE.md) · [Reproduction](docs/04-reproduction.md) · [Publication and data rights](PUBLICATION.md)

The original implementation is preserved on [`old`](https://github.com/QuhiQuhihi/Famma-French-Factors-with-Sector-ETF/tree/old).
The maintained version replaces its mixed return units and annual seven-parameter
fits based on only 12 observations. Code retains the original [MIT license](LICENSE);
external data have separate terms and raw downloads stay outside the public tree.

Research revision: **20 September 2026**. Matched data end **July 2026**.
