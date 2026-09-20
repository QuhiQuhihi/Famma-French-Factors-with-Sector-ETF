# Research audit

Audit date: 20 September 2026. The starting checkout was clean on `main` at
`3e275dca416327b8e708b3fdc50e788adf138389` (`visualization added`). The original
tracked tree is preserved on `old`; the [file inventory](legacy_inventory.json)
records a SHA-256 hash and disposition for every original tracked file. Line
references below refer to that original commit, not the renovated implementation.

## Original question and inspected evidence

The project estimated annual Fama–French five-factor-plus-momentum exposures for
28 iShares sector and industry ETFs, then plotted the six coefficients through time.
This is a useful sector-attribution question. The original code also printed
“expected” monthly and annual returns, without establishing a forecasting design.

The audit read the entire README, three Python scripts, `.gitignore`, MIT license,
and all eight notebook cells, including saved table and stream outputs and the
figure-producing code. The notebook contained 28 embedded charts. Its outputs were
not accepted as evidence that the implementation was correct or reproducible.
The only tracked data file was an empty directory placeholder; no actual cached
inputs, environment specification, or tests were available. The three scripts were
checked for Python syntax without running their downloads or regressions.

The research benchmark was inspected locally at corporate-bond commit
`1f565f6d7010274ff8feb333b9c05be11ba1dcfa`, specifically its README and protocol.
The relevant standard is a traceable question, source vintage, controlled comparison,
uncertainty, executed evidence, and honest interpretation, adapted here to attribution.

## Verified defects and consequences

| Original location | Verified issue | Research consequence and replacement |
|---|---|---|
| `proc_rawdata.py:40`; `build_factor.py:38` | ETF data are transformed to `1 + log(P_t/P_{t-1})`, while French factors and RF remain in percentage points. | The response subtracts percentage-point RF from decimal log returns. Replace with simple ETF returns and factors/RF converted once to decimals. |
| Notebook cell 6, zero-based | Plotted coefficients are multiplied by 100. | This can disguise a scale error but cannot repair the inconsistent RF subtraction or return definition. Plot correctly estimated economic-unit coefficients. |
| `build_factor.py:40–64` | Six slopes plus intercept are estimated from 12 monthly observations per year, or ten in 2022. | Only five or three residual degrees of freedom remain. Replace disconnected annual fits with an explicitly specified rolling experiment; measure rank, conditioning, reconstruction loss, and coefficient movement. |
| `build_factor.py:27`; notebook cell 5 | `2011` appears twice; the saved result has 476 ETF/year rows. | There are only 448 distinct combinations for 28 funds over 2007–2022. Use unique chronological month keys and strict duplicate checks. |
| `get_rawdata.py:149,152`; `proc_rawdata.py:21` | Acquisition writes `.CSV`; processing opens `.csv`. | The pipeline fails on a case-sensitive filesystem. Use shared, explicit paths. |
| `build_factor.py:122` | The script calls undefined `factor_decompose()` rather than `FactorDecompose()`. | The command-line entry point fails. Replace it with the maintained research module. |
| `get_rawdata.py:26,70`; `proc_rawdata.py:33–37` | The initial January 2007 price is used as the monthly return baseline. | The first January return omits the move from the preceding month-end. Acquire December 2006 and use verified month-end exchange sessions. |
| `get_rawdata.py:27,70`; `proc_rawdata.py:34` | The declared end date is unused, and resampling does not exclude an incomplete latest month. | Price and factor periods can be incomparable. Pin the common complete-month interval. |
| `proc_rawdata.py:39–41` | Forward fill and missing-value replacement create zero log returns. | Missing observations are treated as measured unchanged prices. Reject missing required observations and explain exclusions. |
| `get_rawdata.py:129–143`; `proc_rawdata.py:66–74` | Header counts, exact footer text, whitespace, and factor labels control parsing without validation. | Source-format changes or mismatched months can silently alter inputs or cause failures. Validate monthly keys, schemas, numeric units, coverage, and hashes. |
| `build_factor.py:77–82` | “Expected” returns use same-year realized factor averages, omit the estimated intercept, and annualize by multiplication. | These are neither forecasts nor compounded annual returns. Withdraw those claims; report conditional reconstruction and properly defined descriptive intercepts. |
| `build_factor.py:34–37,100–109` | The supplied factor-list argument is ignored, and the fitted intercept is discarded from output. | Claimed model configuration and stored evidence can differ. Record actual model inputs and complete coefficient output. |
| Notebook cells 0, 3, and 6 | Warnings are suppressed; acquisition runs inside the notebook; charts depend on today's directory and existing objects. | Saved output cannot establish a fresh, bounded run. Separate pinned acquisition from deterministic analysis and execute reports in fresh kernels. |

An independent, constructed units check illustrates the central defect: a price move
from 100 to 102 with RF supplied as `0.3` percent should give excess return
`0.020 - 0.003 = 0.017`. The old expression gives approximately `-0.280197`.
This is a numerical example, not an observation from the missing legacy dataset.

The audit did not separately exercise the legacy pipeline against current Yahoo or
French APIs. API-default drift and ZIP member-name changes are reproducibility risks,
not additional claimed execution failures. The maintained acquisition code makes
adjustment treatment explicit and validates the acquired files directly.

## Universe decision

The original 28 tickers were IYW, IYF, IYZ, IYH, IYE, IYK, IYG, IYJ, IDU, IYM,
IYC, IBB, IGM, SOXX, IGV, IGN, IGE, IYT, IHI, ITA, IHF, IEO, ITB, IAT, IAI,
IAK, IHE, and IEZ. They mix broad sectors with narrower industries and overlapping
exposures. They are not 28 independent sectors or an exhaustive historical universe.

The [protocol](PROTOCOL.md) selects ten broad exposures before the renovated
evaluation: **IYW, IYF, IYZ, IYH, IYE, IYK, IYJ, IDU, IYM, and IYC**. The remaining
18 receive explicit ticker-level dispositions in the inventory. No omitted fund is
replaced on the basis of observed model performance. The empirical conclusion is
conditional on this selected surviving core.

Narrower financial, technology, health, energy, and other industry sleeves remain
documented extensions, not extra primary observations. IGN requires particular
care: its change to IDGT included a new mandate in December 2023, so silently
splicing ticker histories would misrepresent the original networking exposure.
Other funds also experienced benchmark changes. Actual fund histories retain those
changes; changing estimated betas need not arise solely from statistical noise.
See the issuer documents and source-vintage evidence in [SOURCES.md](SOURCES.md).

## Legacy disposition and publication boundary

The old acquisition, processing, and regression scripts are replaced. Their useful
research intent and ticker provenance are retained; their numerical outputs are not
carried into the revised evidence. The notebook is replaced with an executed report
and small constructed tutorials. Original code and notebook remain recoverable on
`old`, with an ignored local working copy under `research/private-legacy/`.
The MIT copyright and license are retained. The README and ignore policy are updated,
and the empty data placeholder is removed.

The original dataset cannot be reconstructed exactly: retrieval timestamps, source
hashes, dependencies, adjustment settings, and full cached observations were not
recorded. The revised study therefore uses a separately documented fresh vintage;
it does not claim numerical replication of the saved 2022 figures.

No embedded credentials were encountered in the inspected current source files.
This statement is not a full historical secret scan. Raw source data, local archives,
environments, and local agent instructions are excluded from the maintained public
tree. MIT licensing of project code does not extend to external datasets. The old
notebook contains provider-derived excerpts, so a clean current tree does not erase
historical copies or settle their redistribution rights. See [PUBLICATION.md](../PUBLICATION.md).

## Revised question and validity risks

**Do regularized six-factor exposures reconstruct subsequent sector ETF excess
returns more accurately than rolling OLS, and what is sacrificed in interpretation?**
The maintained protocol fixes a 60-month window, standardized ridge penalty 0.1,
and OLS comparator. Market-only OLS, FF5 OLS, and PCR provide bounded supporting
comparisons. SVD exposes the combinations that the data identify weakly; it is not
evidence that principal components are economic factors or predictive signals.

Coefficients fitted on prior months are applied to subsequently realized factors.
This tests conditional reconstruction, not a forecast available before those factors
occurred. Revised source history and unverified historical publication timing also
preclude a point-in-time deployment claim. Shared sector shocks require synchronized
month-level uncertainty, rather than treating funds as independent samples. An
improvement in coefficient smoothness can be mechanical shrinkage and must be read
alongside reconstruction error and possible exposure bias. Descriptive intercepts
remain conditional on the chosen factor model; they do not demonstrate investable alpha.
