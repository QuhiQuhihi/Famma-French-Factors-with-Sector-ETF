# Research handoff

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
