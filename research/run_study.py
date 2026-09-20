"""Frozen comparisons of economic exposures and subsequent conditional reconstruction."""

from datetime import datetime, timezone
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from research.data import ALL_TICKERS, FACTORS, RAW, ROOT, SECTORS, TICKERS, digest, load_panel
from research.models import fit_factor_model, hac_ols, holm_adjust, paired_block_mean_difference

RESULTS = ROOT / "research/results"
FIGURES = ROOT / "research/figures"
PRIMARY = {
    "Market": ("market", 1, {}),
    "FF5": ("ols", 5, {}),
    "OLS": ("ols", 6, {}),
    "Ridge 0.1": ("ridge", 6, {"ridge_lambda": 0.1}),
    "PCR 4": ("pcr", 6, {"n_components": 4}),
}
SENSITIVITY = {
    "Ridge 0.01": ("ridge", 6, {"ridge_lambda": 0.01}),
    "Ridge 1": ("ridge", 6, {"ridge_lambda": 1}),
    "PCR 3": ("pcr", 6, {"n_components": 3}),
    "PCR 5": ("pcr", 6, {"n_components": 5}),
}
COLORS = {
    "Market": "#777777",
    "FF5": "#b88427",
    "OLS": "#275f9b",
    "Ridge 0.1": "#177b68",
    "PCR 4": "#b65258",
}


def rolling_reconstruction(factors, excess, window=60, specifications=None):
    """Fit only prior months. Prediction uses realized test-month factors deliberately."""
    if not factors.index.equals(excess.index) or not factors.index.is_unique:
        raise ValueError("Factor/target months must align uniquely")
    if not factors.index.is_monotonic_increasing or window < 8 or window >= len(factors):
        raise ValueError("Invalid chronological sample or window")
    specs = PRIMARY if specifications is None else specifications
    rows = []
    for pos in range(window, len(factors)):
        train_x = factors.iloc[pos - window : pos]
        train_y = excess.iloc[pos - window : pos]
        test_x = factors.iloc[pos : pos + 1]
        for label, (method, width, kwargs) in specs.items():
            for ticker in excess.columns:
                fit = fit_factor_model(
                    train_x.iloc[:, :width].to_numpy(),
                    train_y[ticker].to_numpy(),
                    method=method,
                    **kwargs,
                )
                prediction = float(fit.predict(test_x.iloc[:, :width].to_numpy())[0])
                actual = float(excess[ticker].iloc[pos])
                row = {
                    "month": str(factors.index[pos]),
                    "train_start": str(train_x.index[0]),
                    "train_end": str(train_x.index[-1]),
                    "ticker": ticker,
                    "sector": SECTORS.get(ticker, ticker),
                    "model": label,
                    "window": window,
                    "prediction": prediction,
                    "actual": actual,
                    "squared_error_pp2": ((actual - prediction) * 100) ** 2,
                    "intercept": fit.intercept,
                    "condition": fit.standardized_condition,
                    "rank": fit.rank,
                    "effective_df": fit.effective_df,
                }
                row.update(
                    {
                        f"beta_{name}": float(fit.beta[j]) if j < width else 0.0
                        for j, name in enumerate(factors.columns)
                    }
                )
                rows.append(row)
    return pd.DataFrame(rows)


def csv(frame, filename):
    frame.to_csv(RESULTS / filename, index=False, float_format="%.12g", lineterminator="\n")


def write_json(value, path):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def loss_series(paths):
    losses = paths.groupby(["month", "model"]).squared_error_pp2.mean().unstack()
    losses.index = pd.PeriodIndex(losses.index, freq="M").to_timestamp("M")
    return losses


def comparison(paths, block=12):
    losses = loss_series(paths)
    ci = paired_block_mean_difference(losses["Ridge 0.1"], losses["OLS"], block=block)
    return {
        **ci,
        "ols_mse_pp2": float(losses.OLS.mean()),
        "ridge_mse_pp2": float(losses["Ridge 0.1"].mean()),
        "relative_mse_reduction_pct": float(
            100 * (1 - losses["Ridge 0.1"].mean() / losses.OLS.mean())
        ),
        "first_month": str(losses.index[0].to_period("M")),
        "last_month": str(losses.index[-1].to_period("M")),
    }


def summarize(paths):
    rows = []
    for model, g in paths.groupby("model", sort=False):
        changes = (
            g.sort_values(["ticker", "month"])
            .groupby("ticker")[[f"beta_{f}" for f in FACTORS]]
            .diff()
        )
        rows.append(
            {
                "model": model,
                "months": g.month.nunique(),
                "etfs": g.ticker.nunique(),
                "rmse_pct_monthly": float(np.sqrt(g.squared_error_pp2.mean())),
                "mse_pp2": float(g.squared_error_pp2.mean()),
                "rms_beta_monthly_change": float(np.sqrt(changes.pow(2).mean().mean())),
                "mean_effective_df_including_intercept": float(g.effective_df.mean()),
            }
        )
    return pd.DataFrame(rows)


def corporate_action_diagnostic():
    event = pd.read_csv(RAW / "XLF_2016_event.csv", index_col=0)
    prices = pd.read_csv(RAW / "XLF.csv", index_col=0)
    before, after = "2016-09-16", "2016-09-19"
    adjusted = event.loc[after, "Adj Close"] / event.loc[before, "Adj Close"] - 1
    close_change = event.loc[after, "Close"] / event.loc[before, "Close"] - 1
    main_return = prices.loc[after, "XLF"] / prices.loc[before, "XLF"] - 1
    # Yahoo encodes this historical in-kind distribution as a split-like action.
    # Its Close field is already split-adjusted: it is not an unadjusted trade tape.
    if not np.isclose(event.loc[after, "Stock Splits"], 1.231, atol=1e-10):
        raise ValueError("Financials distribution representation changed; investigate source")
    if abs(adjusted - main_return) > 1e-6:
        raise ValueError("Corporate-action window differs from main prices by more than 0.01 bp")
    return {
        "sector": "Financials",
        "ticker": "XLF",
        "event_date": after,
        "vendor_split_like_factor": float(event.loc[after, "Stock Splits"]),
        "provider_close_change_pct": float(close_change * 100),
        "event_adjusted_return_pct": float(adjusted * 100),
        "main_adjusted_return_pct": float(main_return * 100),
        "two_downloads_return_difference_bps": float((adjusted - main_return) * 10000),
        "manual_distribution_added": False,
        "scope": "Vendor internal consistency only; historical Close is split-adjusted. Independent issuer NAV reconciliation remains unrun.",
    }


def factor_map(exposures, tickers, period, filename):
    fig, ax = plt.subplots(figsize=(12, 6.5), layout="constrained")
    values = exposures.set_index("ticker").loc[tickers, FACTORS].to_numpy()
    limit = max(1.0, float(np.abs(values).max()))
    im = ax.imshow(values, cmap="RdBu_r", vmin=-limit, vmax=limit, aspect="auto")
    ax.set_xticks(range(6), FACTORS)
    ax.set_yticks(range(len(tickers)), [SECTORS[t] for t in tickers])
    for i in range(len(tickers)):
        for j in range(6):
            ax.text(
                j,
                i,
                f"{values[i, j]:.2f}",
                ha="center",
                va="center",
                color="white" if abs(values[i, j]) > limit * 0.65 else "#202020",
            )
    ax.set_title(
        f"State Street sector funds: economic factor exposures\nFF5 + momentum OLS · {period}",
        pad=12,
    )
    fig.colorbar(im, ax=ax, label="Economic beta: ETF excess return per unit factor return")
    fig.savefig(FIGURES / filename, bbox_inches="tight")
    plt.close(fig)


def figures(exposures, alpha, primary, summary, singular, headline):
    plt.rcParams.update(
        {"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 140}
    )
    factor_map(
        exposures, TICKERS, "January 2007–July 2026 · original nine sectors", "factor_map.png"
    )

    fig, axs = plt.subplots(1, 2, figsize=(11, 4.4), layout="constrained")
    axs[0].plot(singular.direction, singular.singular_value, "o-", color=COLORS["OLS"])
    axs[0].set(
        xlabel="Ordered singular direction",
        ylabel="Singular value of standardized design",
        title="How weak is the weakest direction?",
    )
    for label, column in [
        ("OLS", "ols_filter"),
        ("Ridge 0.1", "ridge_filter"),
        ("PCR 4", "pcr_filter"),
    ]:
        axs[1].plot(singular.direction, singular[column], "o-", label=label, color=COLORS[label])
    axs[1].set(
        xlabel="Ordered singular direction",
        ylabel="Fitted-response attenuation",
        ylim=(-0.04, 1.08),
        title="Ridge shrinks; truncation removes",
    )
    axs[1].legend(loc="lower left")
    fig.suptitle("Factor geometry in the final training window · July 2021–June 2026")
    fig.savefig(FIGURES / "singular_geometry.png", bbox_inches="tight")
    plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(11.5, 4.8), layout="constrained")
    ordered = summary.set_index("model").loc[list(PRIMARY)]
    axs[0].barh(ordered.index, ordered.rmse_pct_monthly, color=[COLORS[x] for x in ordered.index])
    axs[0].invert_yaxis()
    axs[0].set(
        xlabel="Pooled monthly reconstruction RMSE (%)",
        title="Does added structure improve tracking?",
    )
    for i, value in enumerate(ordered.rmse_pct_monthly):
        axs[0].text(value + 0.025, i, f"{value:.2f}", va="center")
    axs[0].set_xlim(0, ordered.rmse_pct_monthly.max() * 1.2)
    losses = loss_series(primary)
    diff = losses["Ridge 0.1"] - losses.OLS
    axs[1].plot(diff.index, diff.cumsum(), color=COLORS["Ridge 0.1"])
    axs[1].axhline(0, color="#666666", linewidth=0.8)
    axs[1].set(ylabel="Cumulative ridge − OLS squared error (pp²)", title="Below zero favors ridge")
    fig.suptitle(
        "Frozen exposures × realized factors · January 2012–July 2026\nNine State Street sector funds, 60-month fits; conditional reconstruction"
    )
    fig.savefig(FIGURES / "reconstruction.png", bbox_inches="tight")
    plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(11.5, 4.5), layout="constrained")
    subset = ordered.loc[["OLS", "Ridge 0.1", "PCR 4"]]
    axs[0].bar(
        subset.index, subset.rms_beta_monthly_change, color=[COLORS[x] for x in subset.index]
    )
    axs[0].set(
        ylabel="RMS monthly change in economic beta", title="Smoothness is a separate objective"
    )
    for label in subset.index:
        g = primary[(primary.ticker == "XLK") & (primary.model == label)]
        axs[1].plot(
            pd.PeriodIndex(g.month, freq="M").to_timestamp("M"),
            g["beta_HML"],
            label=label,
            color=COLORS[label],
            linestyle={"OLS": "-", "Ridge 0.1": "--", "PCR 4": "-."}[label],
            linewidth=1.3,
        )
    axs[1].axvline(
        pd.Timestamp("2018-09-24"),
        color="#777777",
        linestyle=":",
        label="2018 sector reclassification",
    )
    axs[1].set(
        ylabel="Technology: value-factor beta", title="Sector definitions and exposures can change"
    )
    axs[1].legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2)
    fig.suptitle(
        "Attribution stability · January 2012–July 2026\nAll six slopes enter the left summary; Technology is a fixed illustrative case"
    )
    fig.savefig(FIGURES / "stability.png", bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 5.5), layout="constrained")
    a = alpha.set_index("ticker").loc[TICKERS]
    pos = np.arange(len(a))
    ax.errorbar(
        a.alpha_arithmetic_annual_pct,
        pos,
        xerr=1.96 * a.se_arithmetic_annual_pct,
        fmt="o",
        capsize=3,
        color=COLORS["OLS"],
    )
    ax.axvline(0, color="#777777", linewidth=0.8)
    ax.set_yticks(pos, [SECTORS[t] for t in TICKERS])
    ax.invert_yaxis()
    ax.set(
        xlabel="12 × monthly intercept (%) · pointwise 95% HAC interval",
        title="Unexplained mean return is model-relative\nFF5 + momentum OLS · January 2007–July 2026",
    )
    fig.savefig(FIGURES / "alpha_intervals.png", bbox_inches="tight")
    plt.close(fig)


def main():
    RESULTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    (RESULTS / "private").mkdir(exist_ok=True)
    x, y, audit = load_panel()
    write_json(audit, RESULTS / "data_audit.json")
    write_json(corporate_action_diagnostic(), RESULTS / "corporate_action_audit.json")
    exposure_rows, alpha_rows = [], []
    for ticker in TICKERS:
        fit = fit_factor_model(x.to_numpy(), y[ticker].to_numpy())
        inference = hac_ols(x.to_numpy(), y[ticker].to_numpy(), lags=6)
        residual = y[ticker].to_numpy() - fit.predict(x.to_numpy())
        exposure_rows.append(
            {
                "ticker": ticker,
                "sector": SECTORS[ticker],
                **dict(zip(FACTORS, fit.beta, strict=True)),
                "r_squared": float(
                    1 - residual @ residual / np.sum((y[ticker] - y[ticker].mean()) ** 2)
                ),
                "residual_vol_annual_pct": float(np.std(residual, ddof=1) * np.sqrt(12) * 100),
            }
        )
        alpha_rows.append(
            {
                "ticker": ticker,
                "sector": SECTORS[ticker],
                "alpha_arithmetic_annual_pct": float(inference.coefficients[0] * 1200),
                "se_arithmetic_annual_pct": float(inference.standard_errors[0] * 1200),
                "p_value": float(inference.p_values[0]),
            }
        )
    exposures = pd.DataFrame(exposure_rows)
    alpha = pd.DataFrame(alpha_rows)
    alpha["holm_p_value"] = holm_adjust(alpha.p_value.to_numpy())
    alpha["lower95_arithmetic_annual_pct"] = (
        alpha.alpha_arithmetic_annual_pct - 1.96 * alpha.se_arithmetic_annual_pct
    )
    alpha["upper95_arithmetic_annual_pct"] = (
        alpha.alpha_arithmetic_annual_pct + 1.96 * alpha.se_arithmetic_annual_pct
    )
    csv(exposures, "exposures.csv")
    csv(alpha, "alpha.csv")
    all60 = rolling_reconstruction(x, y, specifications=PRIMARY | SENSITIVITY)
    primary = all60[all60.model.isin(PRIMARY)].copy()
    all60.to_csv(RESULTS / "private/rolling_60.csv", index=False, lineterminator="\n")
    summary = summarize(primary)
    csv(summary, "model_summary.csv")
    by_etf = primary.groupby(["ticker", "model"], as_index=False).squared_error_pp2.mean()
    by_etf["rmse_pct_monthly"] = np.sqrt(by_etf.squared_error_pp2)
    by_etf.insert(1, "sector", by_etf.ticker.map(SECTORS))
    csv(by_etf, "sector_errors.csv")
    csv(summarize(all60), "estimator_sensitivity.csv")
    head = comparison(primary)
    block6 = comparison(primary, block=6)
    csv(pd.DataFrame([head, block6]), "paired_intervals.csv")
    windows = {60: primary[primary.model.isin(["OLS", "Ridge 0.1"])]}
    for window in (36, 120):
        frame = rolling_reconstruction(
            x, y, window=window, specifications={k: PRIMARY[k] for k in ["OLS", "Ridge 0.1"]}
        )
        frame.to_csv(RESULTS / f"private/rolling_{window}.csv", index=False, lineterminator="\n")
        windows[window] = frame
    common_start = max(frame.month.min() for frame in windows.values())
    window_rows = []
    for window, frame in windows.items():
        for scope in ["all available", "common dates"]:
            sample = frame if scope == "all available" else frame[frame.month >= common_start]
            window_rows.append({"window": window, "scope": scope, **comparison(sample)})
    csv(pd.DataFrame(window_rows), "window_sensitivity.csv")
    geometry = primary[(primary.model == "OLS") & (primary.ticker == TICKERS[0])]
    final_x = x.iloc[-61:-1].to_numpy()
    final_y = y[TICKERS[0]].iloc[-61:-1].to_numpy()
    f_ols = fit_factor_model(final_x, final_y)
    f_ridge = fit_factor_model(final_x, final_y, method="ridge", ridge_lambda=0.1)
    f_pcr = fit_factor_model(final_x, final_y, method="pcr", n_components=4)
    singular = pd.DataFrame(
        {
            "direction": np.arange(1, 7),
            "singular_value": f_ols.singular_values,
            "ols_filter": f_ols.shrink_filters,
            "ridge_filter": f_ridge.shrink_filters,
            "pcr_filter": f_pcr.shrink_filters,
        }
    )
    csv(singular, "final_singular_values.csv")
    head.update(
        training_months=60,
        sample_months=len(x),
        evaluation_months=primary.month.nunique(),
        sector_count=len(TICKERS),
        condition_min=float(geometry.condition.min()),
        condition_median=float(geometry.condition.median()),
        condition_max=float(geometry.condition.max()),
        final_condition=float(f_ols.standardized_condition),
        holm_rejections_5pct=int((alpha.holm_p_value < 0.05).sum()),
        interpretation="Retrospective conditional reconstruction using realized test-month factors; not an ex ante forecast",
    )
    write_json(head, RESULTS / "headline.json")
    figures(exposures, alpha, primary, summary, singular, head)
    extended_x, extended_y, extended_audit = load_panel(extended=True)
    write_json(extended_audit, RESULTS / "extended_data_audit.json")
    extended_exposures = []
    for ticker in ALL_TICKERS:
        fit = fit_factor_model(extended_x.to_numpy(), extended_y[ticker].to_numpy())
        extended_exposures.append(
            {
                "ticker": ticker,
                "sector": SECTORS[ticker],
                **dict(zip(FACTORS, fit.beta, strict=True)),
            }
        )
    extended_exposures = pd.DataFrame(extended_exposures)
    csv(extended_exposures, "extended_exposures.csv")
    factor_map(
        extended_exposures,
        ALL_TICKERS,
        "July 2018–July 2026 · all eleven sectors",
        "extended_factor_map.png",
    )
    extended_paths = rolling_reconstruction(extended_x, extended_y)
    extended_paths.to_csv(
        RESULTS / "private/extended_rolling_60.csv", index=False, lineterminator="\n"
    )
    recent_nine = extended_paths[extended_paths.ticker.isin(TICKERS)]
    extended_summary = pd.concat(
        [
            summarize(extended_paths).assign(universe="All eleven sectors"),
            summarize(recent_nine).assign(universe="Original nine on the same recent dates"),
        ],
        ignore_index=True,
    )
    csv(extended_summary, "extended_summary.csv")
    extended_headline = {
        **comparison(extended_paths),
        "sample_months": len(extended_x),
        "sector_count": len(ALL_TICKERS),
        "evaluation_months": extended_paths.month.nunique(),
        "recent_nine": comparison(recent_nine),
        "interpretation": "Supporting shorter sample: only 37 evaluation months; no replacement of primary result",
    }
    write_json(extended_headline, RESULTS / "extended_headline.json")
    outcome = (
        "supports lower conditional reconstruction error"
        if head["upper95"] < 0
        else (
            "supports higher conditional reconstruction error"
            if head["lower95"] > 0
            else "does not resolve a difference in conditional reconstruction error"
        )
    )
    report = f"""# What the evidence permits

The primary comparison **{outcome}** for fixed ridge against OLS.
The paired mean difference is **{head["estimate"]:.4f} squared percentage points**
(ridge minus OLS; 95% 12-month block interval **{head["lower95"]:.4f} to {head["upper95"]:.4f}**).
The relative reduction in mean squared error is **{head["relative_mse_reduction_pct"]:.2f}%**.
These are historical reconstruction errors, not strategy returns.

## Common experiment

Nine original State Street sector funds, 235 monthly returns from January 2007 to July 2026;
60-month rolling fits leave {head["evaluation_months"]} evaluation months, January 2012–July 2026.
The revised factor files and adjusted prices are a single retrospective vintage.
Each target month's realized factors enter its reconstruction; no before-month factor
forecast or historical publication calendar is supplied.

{summary.to_html(index=False, float_format=lambda value: f"{value:.4f}", border=0)}

![Reconstruction comparison](../research/figures/reconstruction.png)

## Conditioning and the bias–variance trade-off

The standardized six-factor design has median rolling condition number
**{head["condition_median"]:.2f}**, range **{head["condition_min"]:.2f}–{head["condition_max"]:.2f}**.
This diagnoses observed factor geometry; it does not justify presuming catastrophic
multicollinearity. The constructed SVD chapter deliberately illustrates a much more
extreme case. Ridge shrinks all directions; PCR rank four throws two directions away
even when their factor variance is small but economically relevant.

![Stability and changing exposures](../research/figures/stability.png)

Compare the [estimator sensitivities](../research/results/estimator_sensitivity.csv),
[window comparisons](../research/results/window_sensitivity.csv), and
[6/12-month block intervals](../research/results/paired_intervals.csv).
The window table includes both each available sample and **common dates beginning
{common_start}**. No sensitivity replaces the fixed primary result. Bootstrap intervals
resample realized loss paths without refitting models and assume useful within-sample
dependence stability; they neither correct research selection nor establish performance
under a new structural break.

## Intercepts and economic interpretation

{head["holm_rejections_5pct"]} of nine full-sample OLS intercepts have Holm-adjusted
p-values below 0.05. The [complete table](../research/results/alpha.csv) includes annual
arithmetic intercepts, six-lag HAC standard errors, pointwise intervals and adjusted
p-values. Annualization here is 12 times a monthly coefficient, not a compounded return.
Ridge coefficients receive no reused OLS p-values. An intercept is conditional on this
factor model, constant-beta approximation, source vintage and selected ETF universe;
it does not establish manager skill, mispricing or implementable hedged profit.

## All eleven sectors, with their actual history

The shorter supplement adds Real Estate and Communication Services from their common
available window, July 2018–July 2026. Its 97 return months leave only **37 evaluation
months**, July 2023–July 2026, after the unchanged 60-month fit. No fund is backfilled.
The [eleven-sector exposure map](../research/figures/extended_factor_map.png) is descriptive.
The nine-sector headline above retains the longer sample and is not interchangeable
with this shorter result.

The supplemental ridge-minus-OLS MSE difference is **{extended_headline["estimate"]:.4f} pp²**,
95% block interval **[{extended_headline["lower95"]:.4f}, {extended_headline["upper95"]:.4f}]**.
Only about three 12-month blocks are represented; precision and dependence estimation
are limited. The original nine scored on these same recent dates have a difference
of **{extended_headline["recent_nine"]["estimate"]:.4f} pp²**. The
[complete supplemental summaries](../research/results/extended_summary.csv) separate
changing the evaluation period from adding two sectors; neither is a new primary test.

The universe change follows the user's issuer preference after viewing the initial
iShares results. The previous study is preserved on
[`ishares-study`](https://github.com/QuhiQuhihi/Famma-French-Factors-with-Sector-ETF/tree/ishares-study).

## What would change the assessment?

An independent later period, point-in-time factor releases and independently reconciled
fund total returns would strengthen a portability claim. Holdings and dated benchmark
constituents would help distinguish estimation noise from genuine mandate changes.
Transaction-level hedge construction and costs would be necessary for a strategy claim.
See the [research agenda](../research/RESEARCH_AGENDA.md).
"""
    (ROOT / "docs/03-results.md").write_text(report)
    source_paths = [
        ROOT / "pyproject.toml",
        ROOT / "uv.lock",
        ROOT / "research/PROTOCOL.md",
        ROOT / "research/input_manifest.json",
        *sorted((ROOT / "research").glob("*.py")),
    ]
    artifacts = (
        sorted(RESULTS.glob("*.csv"))
        + sorted(RESULTS.glob("*.json"))
        + sorted(FIGURES.glob("*.png"))
    )
    artifacts = [
        p for p in artifacts if p.name != "run_metadata.json" and not p.name.startswith("topic_")
    ]
    artifacts += sorted((RESULTS / "private").glob("*.csv")) + [ROOT / "docs/03-results.md"]
    write_json(
        {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "source_and_code": {str(p.relative_to(ROOT)): digest(p) for p in source_paths},
            "artifacts": {str(p.relative_to(ROOT)): digest(p) for p in artifacts},
        },
        RESULTS / "run_metadata.json",
    )
    print(json.dumps(head, indent=2))


if __name__ == "__main__":
    main()
