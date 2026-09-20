# Publication record and boundaries

The maintained tree contains original explanatory text, code, derived summary tables,
original charts and executed notebooks. The original MIT license and copyright remain
intact. Third-party data and literature retain their own rights; see the
[data notice](research/DATA_NOTICE.md) and [source register](research/SOURCES.md).

Raw price series, downloaded factor archives, row-level reconstruction paths, local
instructions, environments and notebook previews are excluded from the public tree.
The input manifest discloses source URLs and checksums, not credentials or raw panels.
The empirical notebooks show bounded summaries and original figures; the teaching
chapters label constructed observations explicitly.

The original commit `3e275dca416327b8e708b3fdc50e788adf138389` is preserved on `old`.
The completed iShares revision `5926897c8ac815133e96afb265b39ba25513d9f3` is preserved
on `ishares-study`, with its original input manifest retained in this tree. The current
State Street study is an explicit later universe amendment, not a replacement history.
Original code and saved notebook outputs can therefore be inspected there. Ignoring
source downloads in the renovated tree does not erase historical notebook excerpts
or rewrite earlier commits. No full-history privacy or security audit is claimed.

## Release checks

Before committing a new research revision, rebuild the study and all notebooks, run
the tests, formatting and artifact checks in [reproduction](docs/04-reproduction.md),
and review the staged file list. Keep source pins stable unless a documented vintage
change warrants a new study. Confirm local instruction files and raw inputs are ignored.

The `renovation` branch carries the research revision, and `main` is the public reading
version after review. Updates use ordinary commits and fast-forward pushes while
preserving `old` and `ishares-study`; no force push or history replacement is needed.

GitHub Actions validates the locked environment, offline numerical tests, saved
artifacts and three source-free teaching chapters. It does not assert current-vendor
data equality, independently reproduce empirical results without their pinned cache,
or establish that historical factor inputs were available in real time.
