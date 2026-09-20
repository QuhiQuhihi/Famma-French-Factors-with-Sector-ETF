# Stable exposures, honest attribution

Initial iShares design specified 20 September 2026. **Issuer amendment on the same
date:** at the user's request, replace the iShares universe with State Street Select
Sector SPDR ETFs and use sector names in figures. This amendment follows inspection
of the iShares results and precedes the State Street evaluation. The prior protocol,
results and notebooks remain at commit `5926897c8ac815133e96afb265b39ba25513d9f3`
on `ishares-study`; its input manifest is retained as `input_manifest_ishares.json`.
This is a retrospective research design, not an independently registered experiment
or an untouched historical holdout. The issuer change is a user preference, not a
performance-selected universe revision.

## Question and economic mechanism

Do regularized six-factor exposures reconstruct subsequent sector ETF excess returns
more accurately than rolling OLS, and what is sacrificed in economic interpretation?
Correlated factor returns can make individual coefficients unstable even when their
combined fitted return is stable. Ridge attenuates weak directions continuously;
principal-component regression (PCR) discards them. Neither mechanism guarantees
improved reconstruction, reliable alpha, or an investable forecast.

Primary comparison: fixed ridge penalty 0.1 against OLS, both with Fama–French five
factors plus momentum and an intercept. Endpoint: mean across months of the equally
weighted mean squared reconstruction error across the nine primary ETFs. Report ridge-minus-OLS
in squared percentage points, its percentage reduction relative to OLS, and a paired
95% circular moving-block bootstrap interval (2,000 resamples, 12 months, seed 20260920).
Resample whole monthly vectors, preserving sector dependence. A negative difference
whose interval excludes zero supports lower error in this sample; report magnitude
and coefficient stability separately. Do not infer equivalence from a wide interval.

## Universe and information

Use State Street's nine original Select Sector funds: Consumer Discretionary (XLY),
Consumer Staples (XLP), Energy (XLE), Financials (XLF), Health Care (XLV), Industrials
(XLI), Materials (XLB), Technology (XLK), and Utilities (XLU). All launched in 1998,
so they support the retained January 2007–July 2026 sample and 120-month sensitivity.
The primary comparison is conditional on these surviving funds and their changing
historical sector definitions. Tickers identify inputs; readers see sector names.

Real Estate (XLRE, launched October 2015) and Communication Services (XLC, June 2018)
enter a **separate eleven-sector supplement**. Acquire their prices from XLC's first
listed session, 19 June 2018; June month-end supplies July's denominator. The common
sample July 2018–July 2026 contains 97 monthly returns and only 37 subsequent months
after 60-month fits. Show an eleven-sector descriptive exposure map and the same five
primary estimator summaries on those dates. Report a paired ridge-minus-OLS interval
as supporting evidence with explicitly limited precision; do not replace the long
sample, add a 120-month fit, or backfill either fund. Also score the original nine on
these same recent dates to separate the sample-period change from adding two funds.
Do not extend the nine-intercept inferential family to exploratory eleven-sector fits.

The 2016 Real Estate separation and 2018 Communication Services reclassification
alter sector definitions. Preserve actual fund histories, not backcast contemporary
holdings. XLF's September 2016 distribution of XLRE shares requires checking vendor
adjusted-price behavior; a distribution-related raw-price drop must not be called a
sector loss, and distributions already reflected in adjusted prices must not be added
again. Save an event-window source snapshot and an explicit adjustment diagnostic.

Daily Yahoo adjusted closes start December 2006; take actual final exchange sessions
of each complete calendar month. Monthly arithmetic returns start January 2007.
Align with the intersection of official French monthly FF5 and momentum files, currently
documented through July 2026. Download ETF prices through 31 July 2026 (exclusive end
1 August), so every evaluated month has both factor and fund observations. Monthly RF
and all factors are supplied in percent: divide by 100 once, subtract RF from each ETF's
simple return. Never fill missing prices, factors, returns, or fabricated ETF history.
Keep raw snapshots local and pin checksums, retrieval timestamps and actual coverage.

The source vintage is retrospective and revisable. Adjusted close approximates total
return, not independently reconciled fund NAV total return. French factors are research
portfolios, not frictionless instruments available to replicate these ETF exposures.
Factor observation month does not establish publication availability.

## Estimation and evaluation

Primary rolling window: 60 months. Every month, fit only the preceding 60 observations.
Center predictors and target and scale predictors by training standard deviations
(ddof 0); leave the intercept unpenalized. Report betas in original decimal-return units.
OLS uses a numerical SVD pseudoinverse with explicit rank tolerance. Ridge minimizes
mean squared training error plus lambda times squared standardized slopes. PCR retains
the leading four singular directions; do not choose rank by ETF performance. Also
report market-only OLS as an economic baseline and FF5 OLS as a momentum diagnostic.

At month t, apply the coefficients estimated through t−1 to the **realized** factors
of t. This is subsequent-month conditional reconstruction, not a forecast available
at t−1: factor t and RF t were not known then. Revised prior observations mean it is
also not a point-in-time deployment simulation. There is no portfolio, trading-cost
deduction, Sharpe ratio, or claimed alpha strategy in this experiment.

Supporting evidence: full-sample FF6 economic exposure map; rolling condition numbers
and singular-value spectra; raw-beta changes; effective degrees of freedom; reconstruction
RMSE by ETF and method; cumulative paired loss; SVD filter comparison. Report full-sample
OLS intercepts with six-lag Newey–West covariance, n/(n−p) finite-sample correction,
normal-approximation 95% intervals and Holm p-values over the nine primary ETF intercepts.
These are descriptive, model-conditional intercepts, not causal skill estimates.

## Bounded challenges

Retain the primary result regardless of sensitivities. Compare ridge lambda 0.01 and
1, PCR ranks 3 and 5, windows 36 and 120, and bootstrap blocks 6 as explicitly supporting
diagnostics. Compare windows on common dates beginning after 120 months; separately
retain each available sample. No cross-validation or data-selected winning estimator.
No confidence claim for a best sector, sensitivity, or model selected after inspection.

Use a fixed constructed collinearity example to explain small singular values and
perturbation amplification. It is a numerical mechanism demonstration, not financial
evidence. Include independent direct linear-algebra checks, units/month-end alignment
tests, future-data perturbation tests, and reconstruction of the reported endpoint
from saved local monthly errors. Numerical tolerances: 1e−10 for well-conditioned
regression identities and 1e−8 where independent floating-point paths differ.

## Recovery and outputs

Source acquisition checkpoints each file under ignored `research/data/raw/`; rerun
`uv run python -m research.acquire` to resume and verify. Existing pins are immutable:
changed downloads fail rather than silently changing the study. Explicit new vintages
require a dated protocol amendment and retained original manifest/results.
`uv run python -m research.run_study` recreates summary tables and figures in
`research/results/` and `research/figures/`, plus ignored monthly paths in
`research/results/private/`. `uv run python -m research.build_notebooks` executes
the central report and mechanism notebooks in fresh kernels. These small regressions
should take minutes; rerunning derives all outputs from the pinned local cache.
