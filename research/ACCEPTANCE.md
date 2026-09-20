# Validation record — 20 September 2026

The maintained study is complete within its stated retrospective attribution scope.
This record covers the State Street issuer amendment. The prior iShares evidence
remains on `ishares-study`. The primary ridge-minus-OLS mean squared error difference
is −0.2066525632 pp², with 95% paired 12-month block interval
[−0.4256448749, −0.0142815312].
No claim of an ex ante forecast, point-in-time execution or investable alpha is made.

## Evidence actually checked

- All fourteen input files were acquired or reused, pinned and reverified offline.
  The exact earlier French archives end in July 2026. Each of nine primary ETFs has
  4,945 required daily observations and 235 complete monthly returns. The all-eleven
  panel has 2,040 common daily observations and 97 monthly returns. Both have zero
  fills and no missing or duplicate required observations. The extra source records
  Financials' September 2016 distribution window.
- **26 tests passed**: direct least-squares/ridge identities, full-rank PCR equivalence,
  scale invariance, independent HAC covariance, Holm examples, paired-block behavior,
  rank/input failures, French parsing, return units, missing-session rejection and
  a future-observation perturbation test.
- Six notebooks executed in fresh kernels: **41 code cells and 14 embedded figures**.
  Ten distinct original figures were visually inspected, including chart labels,
  units, legends and constructed-versus-empirical context. HTML previews were rendered
  and inspected for expected titles, image/table presence and bounded outputs; no
  full browser or external-site build is claimed.
- Saved rolling paths were checked for unique month/fund/model keys, nine funds per
  month, training endpoints at t−1, and exact squared-error units. Independent raw
  OLS and direct ridge solves reconcile January 2012/Technology, March 2020/Energy
  and July 2026/Consumer Discretionary. All economic betas in both descriptive panels
  reconcile to raw least squares.
- The supplement has exactly eleven funds and 37 evaluation months. Actual returns
  reconcile to the shorter panel, and original-nine predictions agree with the long
  run on those same dates. The eleven-sector and matched recent-nine bootstrap
  intervals were independently recomputed; new-fund fits at the first and last
  evaluation dates also received an independent review.
- The Financials source records Yahoo's split-like factor 1.231, with adjusted daily
  return +0.637658% versus +0.637634% in the main price history. The 0.002381 bp
  difference satisfies the stated 0.01 bp tolerance. No distribution is added again.
  This validates vendor consistency, not independent issuer NAV accounting.
- The primary mean difference and 2,000-resample interval were independently
  reconstructed from the saved monthly paths. The report notebook also reruns all
  primary models and asserts agreement with the saved headline.
- Source/code and artifact checksums, notebook execution order, chapter navigation,
  local links and proposed public file exclusions pass the artifact checker.
- Locked offline environment synchronization, Ruff lint, Ruff formatting and Git
  whitespace checks passed. A non-failing upstream NumPy timedelta deprecation
  warning from `exchange_calendars` remains; it does not invalidate the checked dates.

## Commands

```bash
uv sync --locked --offline
uv run python -m research.acquire
uv run pytest -q
uv run python -m research.run_study
uv run python -m research.build_notebooks
uv run python -m research.check_artifacts --full
uv run ruff check research tests
uv run ruff format --check research tests
git diff --check
```

The three source-free tutorials were additionally executed during their independent
review. The CI workflow repeats offline checks and those constructed examples;
its remote status is available in GitHub Actions and is not inferred from local passes.

The original version is recoverable on `old`, and the first renovated version on
`ishares-study`. No other project's implementation or
research results were changed as part of this fifth-project renovation.
