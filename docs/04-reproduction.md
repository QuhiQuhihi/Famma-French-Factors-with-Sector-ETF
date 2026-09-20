# Reproduce the evidence

The maintained path uses Python 3.12 and `uv`. The central report and five chapter
notebooks are already executed for readers; the steps below rebuild their evidence.

```bash
uv sync --locked
uv run python -m research.acquire
uv run pytest -q
uv run python -m research.run_study
uv run python -m research.build_notebooks
uv run python -m research.check_artifacts --full
uv run ruff check research tests
uv run ruff format --check research tests
```

Acquisition downloads official monthly factor ZIPs and daily adjusted State Street
ETF closes, plus a Financials corporate-action snapshot. The nine original funds use
the long history; Real Estate and Communication Services enter a shorter common panel.
It reuses a file only when its checksum matches the manifest. Each completed file
has a local recovery checkpoint; rerun the same command after an interrupted download.
Temporary `.partial` files never replace a verified source on a checksum mismatch.

Raw vendor histories are mutable. A later download may differ even for the same date
range. The workflow deliberately fails on that difference. It cannot promise recovery
of this exact vendor vintage from a future public download. Restore an authorized
copy of the original cache instead:

```bash
uv run python -m research.acquire --from-cache /path/to/original/raw
```

To study a new vintage, keep the original manifest and evidence, document a dated
amendment and rerun the full path. Do not merely edit hashes to bypass verification.
There is no silent refresh option. January 2007–July 2026 is intentionally fixed for
the primary nine; July 2018–July 2026 is fixed for the eleven-sector supplement.
The user-requested issuer amendment retains the earlier iShares manifest and full
study on `ishares-study`. The exact French factor ZIPs are reused across those studies.

## Outputs and recovery

| Path | Role |
| --- | --- |
| `research/data/raw/` | Ignored source ZIPs, prices and acquisition checkpoints |
| `research/input_manifest.json` | Public source identity, coverage, timestamps and SHA-256 pins |
| `research/results/` | Summary statistics, paired intervals and data-quality evidence |
| `research/results/private/` | Ignored month-by-fund fitted values, losses and frozen betas |
| `research/figures/` | Original empirical and constructed-example charts |
| `study.ipynb`, `topics/*/study.ipynb` | Fresh-kernel executed reports |
| `research/preview/` | Ignored self-contained HTML previews for local review |

Study generation takes minutes on a typical laptop. Tables and figures are derived;
the entire computation can restart from the verified source cache. Notebook writes
replace their destination only after successful execution. To rebuild one chapter
while editing, use `--only 02-svd-geometry`; use `--only study` for the main report.
Run the builder without `--only` to refresh the complete notebook manifest afterward.

The offline checks validate independent numerical identities, chronology, parsing,
units, the public file set, links, saved execution and artifact hashes. `--full` also
requires local inputs and saved monthly outputs, independently refits selected OLS
and ridge cases and reconciles the headline endpoint. GitHub Actions runs the offline
checks and source-free constructed chapters; it does not redownload licensed data
or independently execute the empirical study without its original cache.

Source logic changes invalidate provenance: rerun study generation and all notebooks
before the artifact check. Formatting changes to that code also change its checksum.
