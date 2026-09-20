# What the evidence permits

The primary comparison **supports lower conditional reconstruction error** for fixed ridge against OLS.
The paired mean difference is **-0.2067 squared percentage points**
(ridge minus OLS; 95% 12-month block interval **-0.4256 to -0.0143**).
The relative reduction in mean squared error is **2.24%**.
These are historical reconstruction errors, not strategy returns.

## Common experiment

Nine original State Street sector funds, 235 monthly returns from January 2007 to July 2026;
60-month rolling fits leave 175 evaluation months, January 2012–July 2026.
The revised factor files and adjusted prices are a single retrospective vintage.
Each target month's realized factors enter its reconstruction; no before-month factor
forecast or historical publication calendar is supplied.

<table class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>model</th>
      <th>months</th>
      <th>etfs</th>
      <th>rmse_pct_monthly</th>
      <th>mse_pp2</th>
      <th>rms_beta_monthly_change</th>
      <th>mean_effective_df_including_intercept</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Market</td>
      <td>175</td>
      <td>9</td>
      <td>3.4769</td>
      <td>12.0887</td>
      <td>0.0094</td>
      <td>2.0000</td>
    </tr>
    <tr>
      <td>FF5</td>
      <td>175</td>
      <td>9</td>
      <td>3.0371</td>
      <td>9.2243</td>
      <td>0.0412</td>
      <td>6.0000</td>
    </tr>
    <tr>
      <td>OLS</td>
      <td>175</td>
      <td>9</td>
      <td>3.0368</td>
      <td>9.2219</td>
      <td>0.0436</td>
      <td>7.0000</td>
    </tr>
    <tr>
      <td>Ridge 0.1</td>
      <td>175</td>
      <td>9</td>
      <td>3.0025</td>
      <td>9.0153</td>
      <td>0.0348</td>
      <td>6.1530</td>
    </tr>
    <tr>
      <td>PCR 4</td>
      <td>175</td>
      <td>9</td>
      <td>3.3216</td>
      <td>11.0331</td>
      <td>0.0881</td>
      <td>5.0000</td>
    </tr>
  </tbody>
</table>

![Reconstruction comparison](../research/figures/reconstruction.png)

## Conditioning and the bias–variance trade-off

The standardized six-factor design has median rolling condition number
**2.94**, range **2.42–3.74**.
This diagnoses observed factor geometry; it does not justify presuming catastrophic
multicollinearity. The constructed SVD chapter deliberately illustrates a much more
extreme case. Ridge shrinks all directions; PCR rank four throws two directions away
even when their factor variance is small but economically relevant.

![Stability and changing exposures](../research/figures/stability.png)

Compare the [estimator sensitivities](../research/results/estimator_sensitivity.csv),
[window comparisons](../research/results/window_sensitivity.csv), and
[6/12-month block intervals](../research/results/paired_intervals.csv).
The window table includes both each available sample and **common dates beginning
2017-01**. No sensitivity replaces the fixed primary result. Bootstrap intervals
resample realized loss paths without refitting models and assume useful within-sample
dependence stability; they neither correct research selection nor establish performance
under a new structural break.

## Intercepts and economic interpretation

0 of nine full-sample OLS intercepts have Holm-adjusted
p-values below 0.05. The [complete table](../research/results/alpha.csv) includes annual
arithmetic intercepts, six-lag HAC standard errors, pointwise intervals and adjusted
p-values. Annualization here is 12 times a monthly coefficient, not a compounded return.
Ridge coefficients receive no reused OLS p-values. An intercept is conditional on this
factor model, constant-beta approximation, source vintage and selected ETF universe;
it does not establish manager skill, mispricing or implementable hedged profit.

## All eleven sectors, with their actual history

The shorter supplement adds Real Estate and Communication Services from their common
available window, July 2018–July 2026. Its 97 return months leave only **37 evaluation
months**, July 2023–July 2026, after the unchanged 60-month fit. No fund is backfilled.
The [eleven-sector exposure map](../research/figures/extended_factor_map.png) is descriptive.
The nine-sector headline above retains the longer sample and is not interchangeable
with this shorter result.

The supplemental ridge-minus-OLS MSE difference is **-0.6428 pp²**,
95% block interval **[-1.0775, -0.1711]**.
Only about three 12-month blocks are represented; precision and dependence estimation
are limited. The original nine scored on these same recent dates have a difference
of **-0.7666 pp²**. The
[complete supplemental summaries](../research/results/extended_summary.csv) separate
changing the evaluation period from adding two sectors; neither is a new primary test.

The universe change follows the user's issuer preference after viewing the initial
iShares results. The previous study is preserved on
[`ishares-study`](https://github.com/QuhiQuhihi/Famma-French-Factors-with-Sector-ETF/tree/ishares-study).

## What would change the assessment?

An independent later period, point-in-time factor releases and independently reconciled
fund total returns would strengthen a portability claim. Holdings and dated benchmark
constituents would help distinguish estimation noise from genuine mandate changes.
Transaction-level hedge construction and costs would be necessary for a strategy claim.
See the [research agenda](../research/RESEARCH_AGENDA.md).
