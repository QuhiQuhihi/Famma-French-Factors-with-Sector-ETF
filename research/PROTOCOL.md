# Stable exposures, honest attribution

Specified 20 September 2026 after inspecting the original implementation and source
availability, before the renovated evaluation. This is a retrospective research design,
not an independently registered experiment or an untouched historical holdout.

## Question and economic mechanism

Do regularized six-factor exposures reconstruct subsequent sector ETF excess returns
more accurately than rolling OLS, and what is sacrificed in economic interpretation?
Correlated factor returns can make individual coefficients unstable even when their
combined fitted return is stable. Ridge attenuates weak directions continuously;
principal-component regression (PCR) discards them. Neither mechanism guarantees
improved reconstruction, reliable alpha, or an investable forecast.

Primary comparison: fixed ridge penalty 0.1 against OLS, both with Fama–French five
factors plus momentum and an intercept. Endpoint: mean across months of the equally
weighted mean squared reconstruction error across the ten ETFs. Report ridge-minus-OLS
in squared percentage points, its percentage reduction relative to OLS, and a paired
95% circular moving-block bootstrap interval (2,000 resamples, 12 months, seed 20260920).
Resample whole monthly vectors, preserving sector dependence. A negative difference
whose interval excludes zero supports lower error in this sample; report magnitude
and coefficient stability separately. Do not infer equivalence from a wide interval.

## Universe and information

Use ten broad exposures from the original iShares universe: IYW, IYF, IYZ, IYH, IYE,
IYK, IYJ, IDU, IYM, IYC. This fixed subset keeps the original issuer identity and
avoids overlapping specialist sleeves (including the legacy IGN mandate/ticker change).
It is a selected surviving universe, not an exhaustive point-in-time industry panel.
Historical benchmark changes remain part of each actual fund's history.

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
normal-approximation 95% intervals and Holm p-values over the ten ETF intercepts.
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
