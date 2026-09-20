# Do the exposures travel to the next month?

Freeze a 60-month exposure estimate, supply the next month's realized factors, and measure reconstruction error. Compare coefficient movement with tracking accuracy, then examine the bias introduced by shrinkage and discarded directions.

[Open the executed notebook](study.ipynb) · [Research overview](../../README.md)

This note outlines the research argument. Worked calculations and tables referenced below are in the linked notebook; selected figures are reproduced at the end of this note.

## Question and timing
The coefficients are fitted through t−1. Factor returns for t are observed afterward and enter the reconstruction. This is a test of exposure portability conditional on realized factors, not an ex ante return forecast. The source files are also revised vintages.

## Paired panel comparison
Average squared percentage-point errors equally across the 9 primary State Street sector funds within each month. Resample those paired months in common 12-month blocks, retaining sector dependence.

## Stable is not necessarily more accurate
The next figure uses all six raw slopes for the change statistic. PCR's lower dimensional subspace can move from one rolling fit to the next, so lower rank need not give smoother economic betas.

## Retain the unfavorable sensitivities
Larger shrinkage can remove useful exposures. Compare every fixed penalty/rank, then compare windows on the same January 2017–July 2026 dates. These diagnostics do not replace the primary 60-month specification.

## Research decision
Ridge's reconstruction MSE is **2.24% lower** relative to OLS on the point estimate. The paired ridge-minus-OLS difference is **-0.207 pp²**, with a 95% block interval **[-0.426, -0.014]**. The paired interval supports lower reconstruction error for ridge in this panel. Coefficient stability and bounded sensitivities describe other aspects of the fit; none replaces this primary endpoint. The eleven-sector extension has a shorter evaluation period and remains supplemental. [Full results](../../docs/03-results.md) retain the complete record.

## Evidence preview

![Do the exposures travel to the next month?](../../research/figures/reconstruction.png)

![Do the exposures travel to the next month?](../../research/figures/stability.png)

## Further reading
[Data](../../docs/01-data.md) · [Methods](../../docs/02-methods.md) · [Source register](../../research/SOURCES.md)
