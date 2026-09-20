# Which sector exposures are being explained?

The project studies State Street's Select Sector SPDR funds. Charts and research
tables identify **sectors by name**, with tickers retained as instrument identifiers.
The primary panel uses the original nine funds, giving a long common history for
estimating and challenging factor exposures. A separate eleven-sector extension
includes the newer Real Estate and Communication Services funds without inventing
their earlier returns.

| Sector | Ticker | Fund inception | Study panel |
| --- | --- | --- | --- |
| [Communication Services](https://www.ssga.com/us/en/institutional/etfs/state-street-communication-services-select-sector-spdr-etf-xlc) | XLC | 2018-06-18 | Eleven-sector extension |
| [Consumer Discretionary](https://www.ssga.com/us/en/institutional/etfs/state-street-consumer-discretionary-select-sector-spdr-etf-xly) | XLY | 1998-12-16 | Primary and extension |
| [Consumer Staples](https://www.ssga.com/us/en/intermediary/etfs/state-street-consumer-staples-select-sector-spdr-etf-xlp) | XLP | 1998-12-16 | Primary and extension |
| [Energy](https://www.ssga.com/us/en/institutional/etfs/state-street-energy-select-sector-spdr-etf-xle) | XLE | 1998-12-16 | Primary and extension |
| [Financials](https://www.ssga.com/us/en/individual/etfs/state-street-financial-select-sector-spdr-etf-xlf) | XLF | 1998-12-16 | Primary and extension |
| [Health Care](https://www.ssga.com/us/en/individual/etfs/state-street-health-care-select-sector-spdr-etf-xlv) | XLV | 1998-12-16 | Primary and extension |
| [Industrials](https://www.ssga.com/mainfund/XLI) | XLI | 1998-12-16 | Primary and extension |
| [Materials](https://www.ssga.com/us/en/intermediary/etfs/state-street-materials-select-sector-spdr-etf-xlb) | XLB | 1998-12-16 | Primary and extension |
| [Real Estate](https://www.ssga.com/us/en/institutional/etfs/state-street-real-estate-select-sector-spdr-etf-xlre) | XLRE | 2015-10-07 | Eleven-sector extension |
| [Technology](https://www.ssga.com/mainfund/XLK) | XLK | 1998-12-16 | Primary and extension |
| [Utilities](https://www.ssga.com/us/en/intermediary/etfs/state-street-utilities-select-sector-spdr-etf-xlu) | XLU | 1998-12-16 | Primary and extension |

Inception dates above come from the linked issuer pages; exchange listing dates can
differ. Today's eleven Select Sector indexes divide the S&P 500's companies by sector,
but the nine-fund primary sample is not complete coverage of the present eleven-sector
classification. Earlier Financials and Technology holdings also followed different
sector boundaries. The study follows actual fund histories, not today's classification
backcast over the full sample.

The earlier iShares study is retained on the `ishares-study` branch at `5926897`, with
its [input manifest](../research/input_manifest_ishares.json). The switch to State
Street is an explicit research-scope amendment after that analysis was observed. It
does not provide a new untouched validation sample.

## Calendar and return units

The primary price request runs from December 2006 through July 2026, with an exclusive
end of 1 August 2026. December supplies the denominator for January 2007's return.
The validated interval is **January 2007–July 2026: 235 monthly returns**, leaving
**175 subsequent-month evaluations** after the first 60-month training window.
Each of the nine funds has **4,945 daily exchange-session observations** in the
accepted primary input, with no missing prices, duplicate dates or missing factors.

The extension requests the two newer funds from 19 June 2018, then uses 29 June 2018
as the common month-end price baseline. Its return sample is **July 2018–July 2026:
97 months**, leaving only **37 evaluations** after 60 months of training. It supports
an eleven-sector exposure map and a shorter reconstruction comparison. A 120-month
window does not fit this sample; there is no synthetic extension or backfill.
The common eleven-fund daily panel contains **2,040 observations per fund**, also
without missing prices, duplicate dates or missing factors. The
[extension data audit](../research/results/extended_data_audit.json) records these
checks separately from the primary sample.

For each panel take adjusted closes on the actual final exchange session of each
month, not an arbitrary last nonmissing observation or a calendar month-end treated
as a trading session. Reuse the exact pinned French ZIP files from the earlier study,
both ending in July 2026, alongside separately recorded State Street ETF downloads.
A newer ETF price alone cannot extend a matched factor panel. The
[input manifest](../research/input_manifest.json) records **14 source pins**: the two
factor ZIPs, eleven ETF downloads and a separate Financials corporate-action snapshot.
It includes accepted coverage, source
retrieval times and checksums; the [data audit](../research/results/data_audit.json)
records completed observation and alignment checks for the accepted files.

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
and the required month-end sessions for every fund in its designated panel. Do not
forward-fill a missing month, substitute another ticker, or manufacture a pre-inception
price. Match complete months across all factors and ETFs within each panel and report
any coverage rejection explicitly.

An acquisition checksum detects changes to accepted source bytes. Alignment and
units checks detect implementation errors. Neither replaces reconciliation to an
independent institutional price source; that further check remains an extension.

## Sector boundaries and the Financials distribution

**Real Estate separated from Financials in 2016.** GICS changed after 31 August's
close; S&P implemented the classification at its 16 September rebalance. Equity REITs
and real estate management/development companies moved, while mortgage REITs stayed
in Financials. These dates concern classification and index implementation; they
are not Real Estate's 2015 fund inception date. The [joint S&P/MSCI notice](https://www.msci.com/downloads/documents/press-releases/media-room/37f69ddd-2fa0-4b95-9970-5e929a97f7b8.pdf)
and [issuer supplement](https://www.sec.gov/Archives/edgar/data/1064641/000119312516699787/d246445d497.htm)
document the distinction.

Financials transferred its real estate holdings to Real Estate and distributed shares
of that fund to its own holders. The special distribution's ex-date was 19 September
2016, with record date 21 September and payment 22 September, according to the
[exchange/OCC notice](https://boxoptions.com/assets/BOXOnnMemo203915.pdf). The documented
distribution was 0.139146 Real Estate shares per Financials share, valued at $4.44356
in the issuer announcement reproduced in [S&P's methodology](https://www.spglobal.com/spdji/jp/documents/methodologies/methodology-enhanced-cov-call-strat-indices.pdf).
A distribution-related fall in Financials' unadjusted price is not an equivalent loss
of shareholder wealth.

The [corporate-action audit](../research/results/corporate_action_audit.json) checks
a separately pinned Yahoo event snapshot against the main download. Yahoo records
19 September's event with `Stock Splits = 1.231`; its historical `Close` is already
split-adjusted, not an unadjusted trade-price record. The event snapshot's adjusted
daily return is **+0.637658%**, versus **+0.637634%** in the main snapshot, a difference
of **0.002381 basis points**. Neither produces an artificial distribution-sized crash,
and the study adds no separate Real Estate distribution to these adjusted returns.

This establishes consistency between the provider's two snapshots. It does not
independently reconcile the distribution to issuer NAV returns or establish any
additional data rights. That distinction remains material when interpreting
Financials' exposure around the change of sector boundaries.

**Communication Services changed the 2018 sector map.** The Select Sector rebalance
after 21 September's close moved companies from Technology and Consumer Discretionary
into the broadened communication-services grouping. The [CME description](https://www.cmegroup.com/education/articles-and-reports/faq-e-mini-sp-communication-services-select-sector-futures.html)
documents the implementation date and affected sectors. Communication Services had
already launched in June. The extension's July and August returns precede this
reclassification, and September spans its implementation; it is not a constant
classification panel even over that shorter history.

Both events can change factor exposures for economic reasons. Regularization may
suppress a real change as well as sampling noise.

## Source vintages and estimated exposures

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
