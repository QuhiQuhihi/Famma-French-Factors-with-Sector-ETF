# Stable exposures, honest attribution

A factor model can reconstruct a sector's return reasonably well while its individual
loadings move substantially between samples. The central question is whether
regularization improves subsequent-month reconstruction, and how much economic
detail it gives up. The [protocol](../research/PROTOCOL.md) and its State Street
amendment fix the comparison for the revised fund universe. Historical data, the
original implementation and the earlier iShares results were already observed, so
this is not an untouched or independently registered experiment.

The primary panel contains the original nine Select Sector SPDR funds over January
2007–July 2026: 235 return observations and 175 evaluation months after the 60-month
training window. Research displays use sector names. Real Estate and Communication
Services join the separate eleven-sector extension described below.

## What the equation does

For ETF $i$ and month $t$,

$$r_{i,t}-RF_t=\alpha_i+\beta_i^\top f_t+\epsilon_{i,t},$$

where $f_t$ contains the five Fama–French returns and momentum, all in decimal units.
The intercept and slopes explain a conditional relationship in the selected sample.
They do not identify causal exposures or a guaranteed expected return.

Given a fixed fitted model, $\alpha_i$, the six $\beta_{i,j}f_{j,t}$ terms, and the
residual sum to the realized excess return for month $t$. These contributions are
arithmetic attribution. Adding contributions across months does not produce a
compounded wealth decomposition. An annualized monthly intercept, if displayed as
$12\alpha$, is an arithmetic rate rather than a compounded investment return.

## Three estimates of the same six-factor relationship

Each primary rolling fit uses the preceding 60 months. Center each factor and the
target using that training window, then divide factor columns by training standard
deviations with `ddof=0`. Let $Z$ be this standardized design and $y_c$ the centered
target. Compute its reduced SVD,

$$Z=UDV^\top.$$

The columns of $V$ describe combinations of the six named factors. A small singular
value means that the sample contains little independent variation along a particular
combination. It is a statement about this design matrix, not a new economic factor.

| Estimator | Standardized slope estimate | Treatment of weak directions |
| --- | --- | --- |
| OLS | $V D^+ U^\top y_c$ | Inverts singular values above the numerical rank tolerance. |
| Ridge | $V\operatorname{diag}(d_j/(d_j^2+n\lambda))U^\top y_c$ | Attenuates directions continuously. |
| PCR | $V_kD_k^{-1}U_k^\top y_c$ | Retains only the leading $k$ directions. |

Here $n=60$ in the primary rolling window. The ridge objective is

$$\min_b\;\frac{1}{n}\lVert y_c-Zb\rVert_2^2+\lambda\lVert b\rVert_2^2.$$

The primary penalty is fixed at $\lambda=0.1$; its normal equations therefore use
$n\lambda$, not $\lambda$, alongside $Z^\top Z$. PCR retains four directions.
Neither value is selected using evaluation performance. OLS uses the numerical
pseudoinverse tolerance to handle rank, not a performance-selected truncation rank.

Convert the standardized slopes back to economic factor units:

$$\beta_j=b_j/s_j,\qquad\alpha=\bar y-\bar f^\top\beta.$$

This leaves the intercept unpenalized. Displaying standardized slopes as raw factor
betas would confound exposure size with factor volatility. Fitting transformations
on the complete history would also leak future information into every rolling fit.

The fitted-value attenuation along SVD direction $j$ is 1 for an OLS retained
direction, $d_j^2/(d_j^2+n\lambda)$ for ridge, and 1 or 0 for PCR. Summing these
attenuations and adding the intercept gives effective degrees of freedom. Lower
degrees of freedom and smaller coefficient movement describe shrinkage; neither
alone establishes lower reconstruction error.

The numerical rationale follows [Golub and Reinsch](https://doi.org/10.1007/BF02163027)
and the bias–variance motivation follows [Hoerl and Kennard](https://doi.org/10.1080/00401706.1970.10488634).
The constructed collinearity example demonstrates the mechanism separately from
the ETF evidence. It is not a simulated historical market result.

## What the next month evaluates

At month $t$, coefficients use observations through $t-1$. Apply those frozen
coefficients to the **realized** factors of $t$:

$$\widehat y_{i,t}=\widehat\alpha_{i,t-1}+\widehat\beta_{i,t-1}^\top f_t.$$

This tests whether estimated exposures transfer to another observation. It is
conditional reconstruction: $f_t$ was unknown before the month, and the current
download does not recreate historical factor publication vintages. It is consequently
neither a tradeable forecast nor a point-in-time deployment simulation. There is no
portfolio whose turnover, fees or Sharpe ratio could be interpreted here.

Market-only OLS provides a simpler economic baseline. Five-factor OLS describes the
increment associated with adding momentum. Those comparisons and PCR are supporting
diagnostics; the declared primary comparison remains ridge versus six-factor OLS.

For reconstruction error $e_{i,t}^{(m)}=y_{i,t}-\widehat y_{i,t}^{(m)}$, define

$$L_t^{(m)}=\frac{1}{9}\sum_i(e_{i,t}^{(m)})^2,\qquad
\Delta=\frac{1}{T}\sum_t\left(L_t^{(ridge)}-L_t^{(OLS)}\right).$$

Negative $\Delta$ favors ridge. Decimal squared errors multiplied by $10{,}000$
are **squared percentage points**; multiplying their square roots by 100 produces
RMSE in monthly percentage points. Relative error reduction is
$-100\Delta/\overline L^{(OLS)}$. Equal weighting is an evaluation choice across
nine sectors, not a portfolio allocation.

## Uncertainty and the limits of stability

The primary interval resamples circular blocks of 12 consecutive monthly error
vectors, keeping all funds and both methods together. Concatenate sampled blocks,
truncate to the original evaluation length, and recalculate the mean paired loss
difference. Use 2,000 resamples, seed `20260920`, and the 2.5%/97.5% quantiles. The
[circular-block method](https://statistics.stanford.edu/technical-reports/circular-block-resampling-procedure-stationary-data)
retains local temporal dependence and simultaneous sector shocks within each block.

This interval is conditional on the observed error path and the fitted research
workflow. It does not refit models inside each bootstrap sample or capture uncertainty
from choosing a universe, revising inputs or searching additional specifications.
The approximation that blocks can represent the relevant dependence can fail around
structural breaks. Six-month blocks are a declared sensitivity; an interval spanning
zero is inconclusive, not evidence of equivalence.

Full-sample OLS intercepts are a separate descriptive analysis. Their covariance uses
six-lag Newey–West weights and an $n/(n-p)$ finite-sample adjustment, with $p=7$ for
six slopes and an intercept. Normal-approximation intervals accompany the estimates;
Holm adjustment applies to the family of nine primary-panel intercept p-values. These controls do
not make alpha causal, remove specification error, or supply valid OLS inference for
biased ridge/PCR coefficients. See [Newey and West](https://www.nber.org/papers/t0055)
and [Holm](https://www.jstor.org/stable/4615733).

## The eleven-sector extension

The extension adds Real Estate and Communication Services on a common July
2018–July 2026 return sample. Its 97 months support an eleven-sector descriptive
six-factor exposure map and the same 60-month rolling reconstruction methods.
Only 37 subsequent months remain for evaluation, with shared sector shocks and
overlapping training windows. Report exposures and errors as descriptive evidence;
do not create a second alpha-testing family or claim stronger statistical conclusions
from this short panel.

For extension error summaries replace the denominator nine by eleven and use the
extension's common dates. This is a different sample and endpoint composition, so
its aggregate error is not directly comparable with the primary aggregate. No
120-month fit can be estimated from 97 months, and missing older fund history is
neither substituted with an index nor extrapolated. Historical sector boundaries
still matter: July and August precede the September 2018 reclassification, while
September spans its implementation.

## Challenges fixed before evaluation

Primary-panel supporting runs use ridge penalties 0.01 and 1, PCR ranks 3 and 5, windows of 36 and
120 months, and six-month bootstrap blocks. Window comparisons share dates beginning
after 120 observations, while each window's available sample is also retained. None
of these runs replaces the primary result or licenses a claim about a winning sector.

Interpret the endpoint alongside coefficient movement, condition numbers and
ETF-level errors. Ridge may stabilize a redundant factor direction while introducing
bias; PCR may remove a low-variance direction that still matters for a particular
fund. Real changes to holdings and mandates can also make a moving beta economically
appropriate. Robustness here means exposing those tradeoffs, not ensuring that a
preferred estimator wins.
