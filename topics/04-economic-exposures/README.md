# Read the economic exposure map

A sector name is not a factor portfolio. Compare market, size, value, profitability, investment and momentum sensitivities in their original units, then separate fitted contributions from residual risk.

[Open the executed notebook](study.ipynb) · [Research overview](../../README.md)

This note outlines the research argument. Worked calculations and tables referenced below are in the linked notebook; selected figures are reproduced at the end of this note.

## Question
What does a technology or utilities label tell us about the fund's economic risks? The primary panel uses 9 original State Street Select Sector SPDR funds over January 2007–July 2026. A separate, shorter panel includes all eleven current sectors. Full-sample estimates describe their stated samples; they do not reconstruct historical holdings or backcast today's sector definitions.

## Compare the factor sensitivities
Beta 1 means a one-percentage-point factor return contributes one percentage point to the fitted ETF excess return, conditional on the other factors. A coefficient is not a portfolio weight.

## Reconcile the Technology sector in arithmetic return units
Technology is a fixed teaching example. The intercept, factor contributions and mean residual must reconcile to the mean ETF excess return. These annual arithmetic quantities do not compound to a wealth path. The sector fund's composition can change even when its current display name stays the same.

## How much precision does the value loading have?
The HAC interval is model-conditional and pointwise. Correlated factors can make one coefficient imprecise even when the fitted total return is useful.

## Include all eleven sectors without inventing their histories
Real Estate and Communication Services began trading later than the original nine funds. The common eleven-sector sample begins with July 2018 returns and ends in July 2026: 97 monthly observations. The next map estimates every sector on those same dates. It supplements the longer primary panel; comparisons between the maps combine a universe change with a sample-period change.

## Read the shorter reconstruction comparison in its own scope
A 60-month fit leaves only 37 evaluation months, July 2023–July 2026, in this eleven-sector panel. The table also includes the original nine sectors on those same recent dates. This recent-nine control separates the effect of adding Real Estate and Communication Services from the change in evaluation dates. Neither recent-panel estimate is directly comparable with the long-sample primary headline. These are equally weighted sector error summaries, not portfolio weights. A 120-month fitting window is infeasible, and no pre-inception ETF returns are supplied.

## Interpretation
Energy exposure is not an oil futures position, utilities are not duration alone, and profitability beta is not an accounting screen applied to today's holdings. The fixed model and changing benchmark history limit those interpretations. [Data and fund identity](../../docs/01-data.md) discusses the 2016 Real Estate separation and 2018 Communication Services reclassification. Current sector names aid reading; they do not imply an unchanged historical mandate.

## Evidence preview

![Read the economic exposure map](../../research/figures/factor_map.png)

![Read the economic exposure map](../../research/figures/extended_factor_map.png)

## Further reading
[Data](../../docs/01-data.md) · [Methods](../../docs/02-methods.md) · [Source register](../../research/SOURCES.md)
