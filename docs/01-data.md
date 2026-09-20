# Which sector exposures are being explained?

The empirical panel retains ten broad iShares exposures from the original project.
Using one issuer preserves the original research setting while separating broad
sector questions from the many overlapping specialist funds in the legacy universe.
The list is fixed before the renovated evaluation; it is not selected by regression
fit or subsequent performance.

| Ticker | Current broad exposure | Reading the history |
| --- | --- | --- |
| IYW | Technology | Holdings and benchmark rules evolve. |
| IYF | Financials | A broad financial-sector exposure, not just banks. |
| IYZ | Telecommunications | Sector definitions differ from other issuers' communication-services indexes. |
| IYH | Healthcare | Broad healthcare, distinct from a biotechnology sleeve. |
| IYE | Energy | An equity-sector fund, not a direct oil-price return. |
| IYK | Consumer staples | Previously followed a consumer-goods benchmark. |
| IYJ | Industrials | The historical fund need not match today's constituent mix. |
| IDU | Utilities | A sector equity exposure, not a bond substitute. |
| IYM | Basic materials | Company returns include risks beyond commodity prices. |
| IYC | Consumer discretionary | Previously followed a consumer-services benchmark. |

Current labels help orient the reader; they do not reconstruct historical holdings.
The panel is a surviving fund sample rather than an exhaustive, point-in-time industry
universe. The omitted specialist ETFs remain relevant extensions, but mixing them into
the aggregate endpoint would give overlapping industries additional representation.

## Calendar and return units

The requested price history runs from December 2006 through July 2026, with an
exclusive acquisition end of 1 August 2026. December supplies the denominator for
January 2007's return. For each month use the adjusted close on its actual final
exchange session, not an arbitrary last nonmissing observation or the calendar
month-end date interpreted as a trading session.

The validated analysis interval is **January 2007–July 2026: 235 monthly returns**.
All ten funds have all **4,945 expected daily exchange-session observations**, with
no missing prices, duplicate dates, or missing matched factor months. Both downloaded
French monthly archives end in July 2026; a newer ETF price alone cannot extend this
matched panel. The [input manifest](../research/input_manifest.json) records accepted
coverage, source retrieval times and checksums; the [data audit](../research/results/data_audit.json)
records the completed checks. No observations were filled or excluded within the core.

For adjusted month-end price $P_{i,t}$, calculate

$$r_{i,t}=P_{i,t}/P_{i,t-1}-1,\qquad y_{i,t}=r_{i,t}-RF_t.$$

Every return in the model is decimal. French values such as `1.25` mean 1.25%, so
divide the factors and RF by 100 once. Do not mix ETF log returns with arithmetic
factor returns. `Mkt-RF` already subtracts RF; SMB, HML, RMW, CMA and momentum are
long-short returns. Subtract RF from the ETF return, not again from each factor.

| Regressor | Economic contrast |
| --- | --- |
| Mkt-RF | Broad US equity market return above the one-month risk-free return |
| SMB | Smaller-company portfolios relative to larger-company portfolios |
| HML | Higher book-to-market portfolios relative to lower book-to-market portfolios |
| RMW | More profitable companies relative to less profitable companies |
| CMA | Conservative investment relative to aggressive investment |
| Mom | High prior months 2–12 returns relative to low prior returns |

The last five are portfolio contrasts, not company accounting variables directly
observed for each ETF. A positive estimated coefficient describes covariance with
that contrast after conditioning on the other regressors; it does not prove that
every holding shares the corresponding characteristic. Definitions come from the
[five-factor](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_5_factors_2x3.html)
and [momentum](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/det_mom_factor.html)
documentation.

## What must survive the data checks

The factor archives contain explanatory headers and separate annual sections.
Accept monthly records by their six-digit year-month key, parse the expected columns,
and reject duplicates, nonfinite values and missing factor observations. Annual rows
must never enter a monthly join. Preserve a unique, sorted and contiguous month index.

For ETF observations, validate positive finite adjusted closes, unique exchange dates,
and the required month-end sessions for all ten funds. Do not forward-fill a missing
month, substitute another ticker, or manufacture a pre-inception price. Match complete
months across all factors and ETFs and report any coverage rejection explicitly.

An acquisition checksum detects changes to accepted source bytes. Alignment and
units checks detect implementation errors. Neither replaces reconciliation to an
independent institutional price source; that further check remains an extension.

## Three reasons historical exposures can change

**The funds can change.** Several broad iShares sector funds switched from Dow Jones
to Russell benchmarks in September 2021. The changes to IYK and IYC also affect how
their earlier sector labels should be interpreted. The [issuer prospectus](https://www.ishares.com/us/literature/prospectus/p-ishares-trust-us-sector-4-30.pdf)
documents these histories; the [other sector prospectus](https://www.ishares.com/us/literature/prospectus/p-ishares-trust-other-us-sector-3-31.pdf)
documents IYZ. A smoother estimated loading can suppress a real mandate change as
well as reduce noise.

**The source vintage can change.** French US research returns switched from CRSP FIZ
to CIZ construction beginning with January 2025 releases. CIZ compounds daily returns
and reinvests distributions on ex-dates, whereas FIZ used month-end reinvestment.
This is a revision/construction issue for the historical file, not proof of an economic
break at January 2025. RF separately changes provider in June 2024. See the
[French library notice](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)
and [RF definition](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_5_factors_2x3.html).

**The estimates can change.** A rolling sample replaces old observations with new
ones, while correlated factor returns leave some combinations of exposures weakly
identified. The SVD analysis addresses this third mechanism. It cannot by itself
separate genuine economic change from data revisions or omitted risks.

The study uses a retrospective vintage. Its rolling fits respect observation order,
but published factor releases and later revisions are not reconstructed. See the
[estimation design](02-methods.md) for why the resulting evaluation is conditional
return reconstruction rather than an implementable return forecast, and the
[data notice](../research/DATA_NOTICE.md) for distribution boundaries.
