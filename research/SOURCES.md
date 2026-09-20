# Sources and what they support

Sources were checked on 20 September 2026. The [protocol](PROTOCOL.md) fixes the
study's choices; the references below explain the data and methods, rather than
establishing that those choices must work in this sample. Source snapshots and
retrieval hashes remain separate from this bibliography.

## Factor returns

- **Kenneth R. French, [US five-factor definitions](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_5_factors_2x3.html)**
  and [monthly CSV archive](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_CSV.zip).
  Defines market excess return, size, value, profitability, investment and the
  one-month risk-free return. The documentation currently reports monthly data
  through July 2026. RF changes source from Ibbotson to the ICE BofA US 1-Month
  Treasury Bill Index in June 2024.
- **Kenneth R. French, [monthly momentum definitions](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/det_mom_factor.html)**
  and [monthly CSV archive](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Momentum_Factor_CSV.zip).
  Momentum uses long and short portfolios formed from prior months 2–12 returns.
  Its documented endpoint is also July 2026. Momentum is an additional regressor:
  this project's six-factor specification is **FF5 + momentum**, not the original
  five-factor model with a renamed component.
- **Kenneth R. French, [Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)**.
  Documents the change from CRSP FIZ to CIZ files starting with January 2025
  releases. CIZ monthly returns compound daily returns and reinvest dividends on
  ex-dates; FIZ monthly returns used month-end dividend reinvestment. This concerns
  the construction of the downloaded historical vintage, not simply observations
  dated after January 2025.
- **Kenneth R. French, [historical five-factor archives](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_5_factors_2x3_archive.html)**.
  Annual July data cuts show why observation dates and retrieval vintages are
  distinct. These archives do not supply the complete monthly release history
  needed to recreate every historical information set.
- **Fama and French (2015), [A Five-Factor Asset Pricing Model](https://doi.org/10.1016/j.jfineco.2014.10.010)**,
  *Journal of Financial Economics*, 116, 1–22. Provides the economic model and
  time-series regression context. The model's intercept is conditional on its
  factors and assumptions; fitting it to an ETF does not establish manager skill.

## ETF observations and fund identity

- **Yahoo Finance, [adjusted-close definition](https://help.yahoo.com/kb/SLN28256.html)**.
  The provider adjusts historical closing prices for splits and distributions.
  Ratios of these observations provide the study's return proxy. They are not an
  independent reconciliation of issuer NAV total returns or historical executable
  trade prices.
- **iShares, [US sector fund prospectus](https://www.ishares.com/us/literature/prospectus/p-ishares-trust-us-sector-4-30.pdf)**.
  Documents fund objectives and benchmark histories, including September 2021
  changes from Dow Jones to Russell indexes. IYK's earlier Consumer Goods mandate
  and IYC's earlier Consumer Services mandate make current labels imperfect
  descriptions of the entire history. These changes can alter estimated exposures.
- **iShares, [other US sector fund prospectus](https://www.ishares.com/us/literature/prospectus/p-ishares-trust-other-us-sector-3-31.pdf)**.
  Includes IYZ's switch to a Russell telecommunications benchmark in September
  2021. The study follows actual fund returns across documented benchmark changes,
  rather than backcasting today's index rules.
- **BlackRock, [March 2024 annual financial statements](https://www.blackrock.com/us/individual/literature/annual-financial-statements/afs-ishares-nasdaq-s-and-p-phlx-etfs-03-31-en.pdf)**.
  Documents the former IGN fund's changed objective, benchmark, name and IDGT
  ticker in December 2023. This is one reason the retained broad-sector panel does
  not silently substitute current tickers for every legacy specialist fund.

## Estimation and uncertainty

- **Golub and Reinsch (1970), [Singular Value Decomposition and Least Squares Solutions](https://doi.org/10.1007/BF02163027)**,
  *Numerische Mathematik*, 14, 403–420. SVD supplies a stable least-squares
  representation and reveals weakly identified directions. Its numerical rank
  does not measure economic importance or predictive usefulness.
- **Hoerl and Kennard (1970), [Ridge Regression: Biased Estimation for Nonorthogonal Problems](https://doi.org/10.1080/00401706.1970.10488634)**,
  *Technometrics*, 12, 55–67. Motivates biased coefficient estimation when
  regressors overlap. Here the fixed penalty applies to standardized slopes and
  the loss is divided by the training sample size; that normalization matters
  when comparing implementations.
- **Newey and West (1987), [A Simple, Positive Semi-Definite, Heteroskedasticity and Autocorrelation Consistent Covariance Matrix](https://www.nber.org/papers/t0055)**,
  *Econometrica*, 55, 703–708; linked working paper issued in 1986. Supports the
  covariance estimator used for descriptive OLS intercept uncertainty. Six lags,
  a finite-sample adjustment and a normal approximation are this study's declared
  implementation choices, not universal prescriptions from the paper.
- **Politis and Romano, [A Circular Block-Resampling Procedure for Stationary Data](https://statistics.stanford.edu/technical-reports/circular-block-resampling-procedure-stationary-data)**,
  Stanford technical report, March 1991. Supports resampling consecutive blocks
  with circular endpoint treatment. The study resamples paired monthly errors
  jointly across ETFs, using fixed blocks of 12 months. Stationarity and adequate
  representation of dependence remain approximations.
- **Künsch (1989), [The Jackknife and the Bootstrap for General Stationary Observations](https://doi.org/10.1214/aos/1176347265)**,
  *Annals of Statistics*, 17, 1217–1241. Gives the dependent-data rationale for
  block resampling instead of treating individual months as independent draws.
- **Holm (1979), [A Simple Sequentially Rejective Multiple Test Procedure](https://www.jstor.org/stable/4615733)**,
  *Scandinavian Journal of Statistics*, 6, 65–70. The ten descriptive OLS
  intercept p-values form the declared family. Correcting these ten tests does
  not correct unreported searches, data revisions or model misspecification.

The SVD demonstration and all research figures are generated for this project.
Published source figures and full paper text are not copied into the repository.
