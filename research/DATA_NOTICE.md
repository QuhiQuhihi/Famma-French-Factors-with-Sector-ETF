# Data provenance and distribution

This repository publishes research code, original explanations, executed notebooks,
and derived summary tables and figures. It does not grant a license to third-party
market observations or factor archives. Readers obtaining source files must follow
their providers' applicable access and use terms.

## What stays local

Downloaded French factor ZIP files and Yahoo ETF observations belong under ignored
`research/data/raw/`. Cleaned observation-level inputs and monthly error paths also
remain in ignored data or `research/results/private/` locations. Source downloads,
embedded vendor response bodies and complete input tables must not be added to
notebook outputs. Public summaries expose the research conclusions without shipping
the underlying source histories.

Hashes, retrieval timestamps, source URLs, requested coverage and observed coverage
record the provenance of each local snapshot. A checksum identifies bytes; it does
not establish accuracy, a redistribution right or historical publication availability.
The exact accepted input vintage is the one recorded by the acquisition manifest,
not whichever file a provider serves when a reader next downloads it.

## What these observations mean

- French monthly factor and RF values arrive in **percent per month** and are
  converted once to decimal returns. Factors are research portfolios; their
  published returns do not constitute a costless trading implementation.
- Yahoo adjusted closes account for distributions and splits according to the
  provider's adjustment method. The resulting simple-return series is a total
  return proxy, with market-price effects and potential provider revisions. It is
  not independently reconciled issuer NAV performance.
- Current downloads contain retrospectively revised history. The French CIZ
  transition affects the source construction, and RF changes provider in June
  2024. Fund benchmarks also change over time. A frozen download makes a numerical
  result repeatable without making it point-in-time data.
- The primary sample contains the original nine State Street Select Sector funds.
  Real Estate and Communication Services enter a separate eleven-fund extension
  beginning in July 2018. Their pre-inception history is never filled. Current
  sector labels do not erase the 2016 and 2018 reclassifications.
- Financials' September 2016 distribution of Real Estate shares is a corporate
  action, not simply a negative investment return. The adjusted-price series is
  used without adding the distribution a second time. Vendor adjustments remain
  an input dependency; issuer-NAV reconciliation is not implied.

The study evaluates return reconstruction conditional on realized factor returns.
It does not simulate an investor who knew those returns before the month began.

## State Street amendment and later updates

The switch from iShares to State Street reuses the exact pinned French factor ZIP
vintage and acquires a separately recorded ETF panel. The earlier full study remains
on branch `ishares-study` at `5926897`; `research/input_manifest_ishares.json` retains
its source metadata. That earlier result had been observed before this change of
universe, so the State Street version is not presented as an untouched experiment.

Acquisition verifies existing pins and fails if their contents differ. An intentional
refresh requires a dated amendment, a separate recorded input vintage, and rerun
results. Preserve the original manifest and outputs so changes in the input history
can be distinguished from changes in the method. Do not combine an older factor
snapshot with a newer ETF history without recording that choice.

See the [data design](../docs/01-data.md), [source bibliography](SOURCES.md), and
[protocol](PROTOCOL.md) for the sample, economic definitions and evaluation boundary.
