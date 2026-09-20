# Read the economic exposure map

A sector name is not a factor portfolio. Compare market, size, value, profitability, investment and momentum sensitivities in their original units, then separate fitted contributions from residual risk.

[Open the executed notebook](study.ipynb) · [Research overview](../../README.md)

This note outlines the research argument. Worked calculations and tables referenced below are in the linked notebook; selected figures are reproduced at the end of this note.

## Question
What does a technology or utilities label tell us about the fund's economic risks? This chapter uses the historical ten-fund panel, January 2007–July 2026. Full-sample estimates describe that sample; they do not reconstruct historical holdings.

## Compare the factor sensitivities
Beta 1 means a one-percentage-point factor return contributes one percentage point to the fitted ETF excess return, conditional on the other factors. A coefficient is not a portfolio weight.

## Reconcile one fund in arithmetic return units
IYW is a fixed teaching example, not the best-looking intercept selected from the table. The intercept, factor contributions and mean residual must reconcile to the mean ETF excess return. These annual arithmetic quantities do not compound to a wealth path.

## How much precision does the value loading have?
The HAC interval is model-conditional and pointwise. Correlated factors can make one coefficient imprecise even when the fitted total return is useful.

## Interpretation
Energy exposure is not an oil futures position, utilities are not duration alone, and profitability beta is not an accounting screen applied to today's holdings. The fixed model and changing benchmark history limit those interpretations. [Data and fund identity](../../docs/01-data.md) explains the September 2021 changes.

## Evidence preview

![Read the economic exposure map](../../research/figures/factor_map.png)

## Further reading
[Data](../../docs/01-data.md) · [Methods](../../docs/02-methods.md) · [Source register](../../research/SOURCES.md)
