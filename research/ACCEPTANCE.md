# Validation record — 20 September 2026

The maintained study is complete within its stated retrospective attribution scope.
The primary ridge-minus-OLS mean squared error difference is −0.1771978913 pp²,
with 95% paired 12-month block interval [−0.3978191025, 0.0282447807].
No claim of an ex ante forecast, point-in-time execution or investable alpha is made.

## Evidence actually checked

- All twelve input files were acquired, pinned and subsequently reverified offline.
  Both French archives end in July 2026. Each of ten ETFs has 4,945 required daily
  observations; the joined panel has 235 complete months, zero fills and no missing
  or duplicate required observations.
- **26 tests passed**: direct least-squares/ridge identities, full-rank PCR equivalence,
  scale invariance, independent HAC covariance, Holm examples, paired-block behavior,
  rank/input failures, French parsing, return units, missing-session rejection and
  a future-observation perturbation test.
- Six notebooks executed in fresh kernels: **37 code cells and 12 embedded figures**.
  Nine distinct original figures were visually inspected, including chart labels,
  units, legends and constructed-versus-empirical context. HTML previews were rendered
  and inspected for expected titles, image/table presence and bounded outputs; no
  full browser or external-site build is claimed.
- Saved rolling paths were checked for unique month/fund/model keys, ten funds per
  month, training endpoints at t−1, and exact squared-error units. Independent raw
  OLS and direct ridge solves reconcile January 2012/IYW, March 2020/IYE and July
  2026/IYC. All full-sample economic betas reconcile to raw least squares.
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

The original version is recoverable on `old`. No other project's implementation or
research results were changed as part of this fifth-project renovation.
