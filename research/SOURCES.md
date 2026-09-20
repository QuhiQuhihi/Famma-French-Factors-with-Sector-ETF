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
- **State Street, official fund pages linked in the [sector table](../docs/01-data.md)**.
  Verify sector names, tickers and fund inception dates. The original nine funds
  began on 16 December 1998; Real Estate began on 7 October 2015 and Communication
  Services on 18 June 2018. Inception and exchange listing are distinct dates.
  These pages describe current fund mandates, not point-in-time historical holdings.
- **S&P Dow Jones Indices and MSCI, [March 2016 GICS implementation notice](https://www.msci.com/downloads/documents/press-releases/media-room/37f69ddd-2fa0-4b95-9970-5e929a97f7b8.pdf)**.
  Establishes Real Estate's separation from Financials, excluding mortgage REITs,
  with different dates for GICS classification and S&P index implementation.
- **Select Sector SPDR Trust, [September 2016 prospectus supplement](https://www.sec.gov/Archives/edgar/data/1064641/000119312516699787/d246445d497.htm)**.
  Describes removing the relevant real estate holdings from Financials, exchanging
  them for Real Estate fund shares and distributing those shares to investors.
- **BOX/OCC, [Financials distribution notice](https://boxoptions.com/assets/BOXOnnMemo203915.pdf)**
  and **S&P Dow Jones Indices, [Enhanced Covered Call Strategy Indices methodology](https://www.spglobal.com/spdji/jp/documents/methodologies/methodology-enhanced-cov-call-strat-indices.pdf)**.
  The exchange notice identifies the 19 September 2016 ex-date. S&P's corporate-action
  example records the issuer's distribution of 0.139146 Real Estate shares per
  Financials share, valued at $4.44356 in the announcement. These sources establish
  an adjustment event; they do not verify Yahoo's treatment of that event.
- **CME Group, [Communication Services Select Sector futures FAQ](https://www.cmegroup.com/education/articles-and-reports/faq-e-mini-sp-communication-services-select-sector-futures.html)**.
  Describes the Select Sector rebalance after the close on 21 September 2018 and
  movement into Communication Services from the existing technology, consumer
  discretionary and telecommunications groupings. Sector names are not immutable
  economic exposures through this change.

The earlier iShares sources and complete results remain on the `ishares-study`
branch. The State Street amendment retains the same French ZIP vintage and records
its new ETF downloads separately; the [data notice](DATA_NOTICE.md) explains this
boundary.

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
  *Scandinavian Journal of Statistics*, 6, 65–70. The nine primary-panel OLS
  intercept p-values form the declared family. Correcting these nine tests does
  not correct unreported searches, data revisions or model misspecification.

The SVD demonstration and all research figures are generated for this project.
Published source figures and full paper text are not copied into the repository.
