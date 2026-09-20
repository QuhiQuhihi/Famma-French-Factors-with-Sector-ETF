# Research handoff

## Initial iShares revision (preserved on ishares-study)

- 20 September 2026: inspected original main `3e275dca416327b8e708b3fdc50e788adf138389`;
  clean checkout, remote main identical. Created local `old` at that commit and
  `renovation` for all updates. Original substantive files also copied to ignored
  `research/private-legacy/`. MIT attribution retained.
- Reference inspected: corporate-bond README and protocol at
  `1f565f6d7010274ff8feb333b9c05be11ba1dcfa`.
- Primary design fixed before updated evaluation: ten original broad iShares funds,
  FF5 plus momentum, rolling 60-month OLS/ridge/PCR conditional reconstruction.
- Outputs/restart commands: see PROTOCOL.md. Acquisition is per-file resumable;
  generated tables/figures are replaceable, source pins are not silently updated.
- Acquired official FF5 and momentum archives through July 2026, plus all 4,945
  daily adjusted-close observations for each of ten original broad iShares funds.
  Verified 235 complete monthly returns, with zero missing observations or fills.
- Implemented and independently tested standardized SVD OLS, ridge, fixed-rank PCR,
  HAC intercept inference, Holm adjustment and paired circular-block uncertainty.
  Fixed primary result: MSE difference −0.1771978913 pp², interval
  [−0.3978191025, 0.0282447807]; interpretation remains inconclusive.
- Built five illustrated chapter notes and notebooks plus the combined report.
  All six execute in fresh kernels; 26 focused tests pass. Independent review
  reconciled selected OLS/ridge fits, saved monthly losses and bootstrap endpoints.
- Final presentation changes add explicit preview figures to chapter notes and
  redundant line styles to the changing-exposure chart; complete evidence rebuilt.
- Recovery commands and validation boundaries: see docs/04-reproduction.md and
  research/ACCEPTANCE.md. Reproduction uses the original pinned local cache.
- Publication sequence: review staged bytes, ordinary commit on renovation,
  fast-forward main, atomic non-force push of old/renovation/main, verify remote refs.

## State Street issuer amendment — 20 September 2026

- User requested State Street sector ETFs and sector-name charts. Preserved the
  initial renovation on `ishares-study` at `5926897`; original `old` stays unchanged.
  Renamed the earlier public input manifest to `input_manifest_ishares.json`.
- Kept the exact French factor ZIPs and fixed estimator settings. Downloaded the
  original nine sector funds from December 2006; Real Estate and Communication
  Services enter a separate common panel from June 19, 2018. Fourteen source pins
  include an extra Financials 2016 corporate-action snapshot.
- Primary panel: 235 monthly observations and 175 evaluations. Eleven-sector
  supplement: 97 observations and 37 evaluations. No synthetic or pre-inception
  history. The recent-nine control uses identical evaluation dates and fits.
- Primary mean squared error difference: -0.2066525632 pp²; paired interval
  [-0.4256448749, -0.0142815312]; relative reduction 2.2409%. The shorter supplement
  remains supporting evidence. All empirical figures use sector names.
- Financials event diagnostic: Yahoo records a split-like factor of 1.231; event
  adjusted return +0.637658%, bulk return +0.637634%, difference 0.002381 bp.
  No distribution added again. This is vendor consistency, not independent NAV proof.
- 26 tests pass. Independent review reconciled all saved errors, three panel
  bootstrap intervals, new-fund fits and identical recent-nine predictions.
- Rebuild sequence: run_study, build_notebooks, check_artifacts --full; source and
  notebook manifests must agree after final code changes. Outputs/recovery follow
  docs/04-reproduction.md. Publish main/renovation and preserved ishares-study with
  a non-force push after staged-byte review.
