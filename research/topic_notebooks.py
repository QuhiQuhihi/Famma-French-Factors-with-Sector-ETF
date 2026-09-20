"""Canonical, constructed tutorials accompanying the empirical attribution study."""

from textwrap import dedent

import nbformat


def _markdown(source: str):
    return nbformat.v4.new_markdown_cell(dedent(source).strip())


def _code(source: str):
    return nbformat.v4.new_code_cell(dedent(source).strip())


def topic_specs() -> list[dict]:
    """Return fresh notebook cells; the builder prepends repository-root setup."""
    return [
        {
            "slug": "01-return-alignment",
            "title": "Getting excess returns right",
            "intro": (
                "A factor regression starts with an economic measurement contract: "
                "complete months, simple ETF returns, consistent percentage units, and "
                "one subtraction of the risk-free rate. This constructed example makes "
                "the original unit and partial-month errors visible before any model is fitted."
            ),
            "cells": [
                _markdown(r"""
                    ## Goal

                    Follow a price move from 100 to 102 through month selection, return
                    calculation, percentage conversion, and excess-return construction.
                    Every price and factor value below is **constructed**, not market data.
                    The three declared month-end sessions are a small fixture; they do not
                    substitute for the production workflow's complete daily-session checks.

                    A date label is not evidence that a month is complete. Likewise,
                    an observation month does not establish when a factor was published.
                    """),
                _code("""
                    import numpy as np
                    import pandas as pd
                    import matplotlib.pyplot as plt
                    from IPython.display import display, Markdown
                    from matplotlib.ticker import PercentFormatter

                    FIGURES = ROOT / "research" / "figures"
                    FIGURES.mkdir(parents=True, exist_ok=True)
                    plt.rcParams.update({
                        "figure.dpi": 120, "font.size": 11,
                        "axes.spines.top": False, "axes.spines.right": False,
                    })
                    prices = pd.Series(
                        [100.0, 100.5, 102.0, 101.0, 103.02, 102.8, 104.0],
                        index=pd.to_datetime([
                            "2024-12-31", "2025-01-02", "2025-01-31", "2025-02-03",
                            "2025-02-28", "2025-03-03", "2025-03-14",
                        ]), name="Constructed adjusted close",
                    )
                    expected_end = pd.Series(
                        pd.to_datetime(["2024-12-31", "2025-01-31", "2025-02-28", "2025-03-31"]),
                        index=pd.period_range("2024-12", "2025-03", freq="M"),
                    )
                    display(prices.to_frame())
                    """),
                _markdown(r"""
                    ### 1. Keep only completed months

                    December supplies January's starting price. The latest March quote
                    is dated March 14, before the declared March 31 session; it cannot be
                    treated as a full March observation. No absent price is forward filled.
                    """),
                _code("""
                    month_key = prices.index.to_period("M")
                    observed_end = pd.Series(prices.index, index=month_key).groupby(level=0).last()
                    month_prices = prices.groupby(month_key).last()
                    complete = observed_end.eq(expected_end)
                    coverage = pd.DataFrame({
                        "Last observed date": observed_end,
                        "Required month end": expected_end,
                        "Complete month": complete,
                        "Last constructed price": month_prices,
                    })
                    complete_prices = month_prices.loc[complete]
                    simple_returns = complete_prices.pct_change(fill_method=None).dropna()
                    assert simple_returns.index.tolist() == list(pd.period_range("2025-01", "2025-02", freq="M"))
                    np.testing.assert_allclose(simple_returns.to_numpy(), [0.02, 0.01], atol=1e-14)
                    display(coverage)
                    """),
                _markdown(r"""
                    ### 2. Convert the supplied percentages once

                    For an ETF, $y_t=P_t/P_{t-1}-1-RF_t$. The French `Mkt-RF`
                    column is **already** an excess return; SMB, HML, RMW, CMA, and
                    momentum are long–short factor returns. Do not subtract RF again
                    from these regressors. The factor table here is an illustrative fixture.
                    """),
                _code("""
                    source_percent = pd.DataFrame(
                        {"Mkt-RF": [1.7, 0.8], "RF": [0.3, 0.2]},
                        index=pd.period_range("2025-01", "2025-02", freq="M"),
                    )
                    factors = source_percent / 100.0
                    assert simple_returns.index.equals(factors.index)
                    excess = simple_returns - factors["RF"]
                    log_returns = np.log(complete_prices / complete_prices.shift(1)).dropna()
                    legacy_expression = log_returns - source_percent["RF"]
                    comparison = pd.DataFrame({
                        "ETF simple return (%)": simple_returns * 100,
                        "RF (%)": source_percent["RF"],
                        "Correct excess return (%)": excess * 100,
                        "Legacy expression (inconsistent units)": legacy_expression,
                    })
                    np.testing.assert_allclose(excess.to_numpy(), [0.017, 0.008], atol=1e-14)
                    display(comparison.round(6))
                    """),
                _markdown(r"""
                    ### 3. Separate a unit error from a return-definition choice

                    The January excess return is 1.7%, obtained from 2.0% minus 0.3%.
                    Log returns are also legitimate quantities, but they do not equal
                    simple returns and cannot silently replace them in this model.
                    The second panel shows their difference for constructed price shocks.
                    """),
                _code("""
                    shocks = np.linspace(-0.4, 0.4, 161)
                    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.3), layout="constrained")
                    values = [simple_returns.iloc[0], factors["RF"].iloc[0], excess.iloc[0]]
                    bars = axes[0].bar(["ETF total", "Risk-free", "ETF excess"], values,
                                       color=["#335C81", "#B07828", "#567044"])
                    axes[0].bar_label(bars, labels=[f"{x:.1%}" for x in values], padding=4)
                    axes[0].set(ylim=(0, 0.024), title="Constructed January return", ylabel="Monthly return")
                    axes[0].yaxis.set_major_formatter(PercentFormatter(1))
                    axes[1].plot(shocks, shocks, color="#335C81", label="Simple return")
                    axes[1].plot(shocks, np.log1p(shocks), color="#B07828", linestyle="--", label="Log return")
                    axes[1].axhline(0, color="0.7", linewidth=0.8)
                    axes[1].set(title="Same price shock, different definitions", xlabel="Simple price return",
                                ylabel="Return or log price relative")
                    axes[1].xaxis.set_major_formatter(PercentFormatter(1))
                    axes[1].yaxis.set_major_formatter(PercentFormatter(1))
                    axes[1].legend(frameon=False)
                    fig.savefig(FIGURES / "topic_return_alignment.png", dpi=160, bbox_inches="tight")
                    plt.show()
                    """),
                _markdown(r"""
                    ### 4. Keep the economic checks beside the arithmetic

                    These two constructed months make the ETF excess return equal to the
                    market excess return. Subtracting RF a second time from `Mkt-RF`
                    breaks that identity. Missing a required month must fail a production
                    calculation; dropping a broken middle month and taking the next price
                    ratio would create a multi-month return with a misleading monthly label.
                    """),
                _code("""
                    np.testing.assert_allclose(excess, factors["Mkt-RF"], atol=1e-14)
                    assert not complete.loc[pd.Period("2025-03", freq="M")]
                    assert np.diff(complete_prices.index.asi8).tolist() == [1, 1]
                    np.testing.assert_allclose(
                        log_returns, np.log1p(simple_returns), atol=1e-14
                    )
                    display(pd.DataFrame({
                        "Correct Mkt-RF (%)": factors["Mkt-RF"] * 100,
                        "Incorrect second RF subtraction (%)": (factors["Mkt-RF"] - factors["RF"]) * 100,
                    }))
                    display(Markdown(
                        "**Result:** the constructed January excess return is **1.7%**; "
                        "the partial March observation is excluded. These checks establish "
                        "the arithmetic contract, not the quality or historical availability "
                        "of any downloaded data."
                    ))
                    """),
                _markdown("""
                    ## Takeaway

                    A regression cannot repair incompatible units or a partial-month return.
                    The empirical study applies this contract to pinned data and validates
                    actual exchange-session coverage. Continue to the
                    [SVD geometry notebook](../02-svd-geometry/study.ipynb), or inspect the
                    [data sources](../../research/SOURCES.md) and [protocol](../../research/PROTOCOL.md).
                    """),
            ],
        },
        {
            "slug": "02-svd-geometry",
            "title": "Why unstable betas can still fit returns",
            "intro": (
                "SVD separates well-observed combinations of factors from weakly identified "
                "directions. A controlled three-factor example compares OLS, ridge, and "
                "two-component PCR after a small, deliberately aligned response perturbation. "
                "The example explains a mechanism; actual factor conditioning is measured separately."
            ),
            "cells": [
                _markdown(r"""
                    ## Goal

                    Two nearly identical regressors identify their **combined** exposure
                    much better than their separate coefficients. We construct that
                    geometry, add a small response perturbation along its weakest direction,
                    and compare coefficient changes with reconstruction changes.

                    All observations are constructed. The planted response has zero intercept
                    and slopes $(0.7,0.7,-0.3)$. Its noise and the later perturbation are
                    explicitly supplied; neither is estimated from market history.
                    """),
                _code("""
                    import numpy as np
                    import pandas as pd
                    import matplotlib.pyplot as plt
                    from IPython.display import display, Markdown
                    from research.models import fit_factor_model

                    FIGURES = ROOT / "research" / "figures"
                    FIGURES.mkdir(parents=True, exist_ok=True)
                    plt.rcParams.update({"figure.dpi": 120, "font.size": 11,
                                         "axes.spines.top": False, "axes.spines.right": False})
                    rng = np.random.default_rng(20260920)
                    n = 120
                    latent = rng.normal(size=(n, 3))
                    X = 0.03 * np.column_stack([
                        latent[:, 0], latent[:, 0] + 0.001 * latent[:, 1], latent[:, 2]
                    ])
                    planted_beta = np.array([0.7, 0.7, -0.3])
                    y = X @ planted_beta + rng.normal(0, 0.003, size=n)
                    standardized = (X - X.mean(axis=0)) / X.std(axis=0, ddof=0)
                    U, singular, Vt = np.linalg.svd(standardized, full_matrices=False)
                    display(pd.DataFrame({"Singular value": singular,
                                          "Design variance share": singular**2 / np.sum(singular**2)},
                                         index=["Direction 1", "Direction 2", "Direction 3"]))
                    """),
                _markdown(r"""
                    ### 1. Three ways to treat the same singular directions

                    OLS uses every numerically identified direction. Ridge solves
                    $\|y_c-Z\gamma\|^2/n+\lambda\|\gamma\|^2$, with
                    $\lambda=0.1$ and unpenalized intercept. Its fitted-response filter
                    is $s_j^2/(s_j^2+n\lambda)$. PCR keeps two directions and gives
                    the third a zero filter. Centering and scaling use only this fitting
                    sample; output slopes are returned to the original factor units.
                    """),
                _code("""
                    options = {"OLS": {"method": "ols"},
                               "Ridge": {"method": "ridge", "ridge_lambda": 0.1},
                               "PCR (2)": {"method": "pcr", "n_components": 2}}
                    fits = {name: fit_factor_model(X, y, **kwargs) for name, kwargs in options.items()}
                    coefficient_table = pd.DataFrame(
                        {name: fit.beta for name, fit in fits.items()}, index=["Factor 1", "Factor 2", "Factor 3"]
                    )
                    coefficient_table["Planted slope"] = planted_beta
                    display(coefficient_table.round(6))
                    display(pd.DataFrame({name: {"Condition number": fit.standardized_condition,
                                                       "Effective df including intercept": fit.effective_df}
                                          for name, fit in fits.items()}).T.round(4))
                    """),
                _markdown(r"""
                    ### 2. Inspect the filters before interpreting the coefficients

                    The small singular value measures weak support for one combination of
                    named factors. Its squared value, not its value alone, determines its
                    share of design variance. Dropping a low-variance direction may remove
                    useful response information; explained variance is not predictive merit.
                    """),
                _code("""
                    palette = {"OLS": "#335C81", "Ridge": "#B07828", "PCR (2)": "#567044"}
                    positions = np.arange(1, 4)
                    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.3), layout="constrained")
                    axes[0].semilogy(positions, singular, "o-", color="#335C81")
                    axes[0].set(xticks=positions, xlabel="Ordered singular direction",
                                ylabel="Singular value, log scale", title="Constructed factor design, 120 observations")
                    for name, fit in fits.items():
                        axes[1].plot(positions, fit.shrink_filters, marker="o", color=palette[name], label=name,
                                     linestyle={"OLS": "-", "Ridge": "--", "PCR (2)": ":"}[name])
                    axes[1].set(xticks=positions, xlabel="Ordered singular direction",
                                ylabel="Fitted-response filter", ylim=(-0.04, 1.08), title="Attenuation under the fixed estimators")
                    axes[1].legend(frameon=False, loc="lower left")
                    fig.savefig(FIGURES / "topic_svd_filters.png", dpi=160, bbox_inches="tight")
                    plt.show()
                    """),
                _markdown(r"""
                    ### 3. Add a known perturbation and keep the comparison paired

                    The response perturbation has RMS **0.5 basis points** and is
                    deliberately aligned with the smallest left singular vector. This is
                    a sensitivity construction, not a typical-noise claim. Independently
                    generated probe factors either preserve the original near-collinearity
                    or increase the difference between factors 1 and 2. Probe results measure
                    changes caused by the perturbation, not total forecast error.
                    """),
                _code("""
                    perturbation = 0.00005 * np.sqrt(n) * U[:, -1]
                    altered = {name: fit_factor_model(X, y + perturbation, **kwargs)
                               for name, kwargs in options.items()}
                    probe_latent = rng.normal(size=(300, 3))
                    probe = 0.03 * np.column_stack([
                        probe_latent[:, 0], probe_latent[:, 0] + 0.001 * probe_latent[:, 1], probe_latent[:, 2]
                    ])
                    changed_geometry = 0.03 * np.column_stack([
                        probe_latent[:, 0], probe_latent[:, 0] + 0.3 * probe_latent[:, 1], probe_latent[:, 2]
                    ])
                    rows = []
                    for name, fit in fits.items():
                        changed = altered[name]
                        rows.append({"Estimator": name,
                                     "Slope change, L2": np.linalg.norm(changed.beta - fit.beta),
                                     "Same-geometry RMS change (bps)": np.sqrt(np.mean((changed.predict(probe) - fit.predict(probe))**2)) * 10000,
                                     "Changed-geometry RMS change (bps)": np.sqrt(np.mean((changed.predict(changed_geometry) - fit.predict(changed_geometry))**2)) * 10000})
                    stability = pd.DataFrame(rows).set_index("Estimator")
                    display(stability.round(6))
                    fig, axes = plt.subplots(1, 3, figsize=(12, 4), sharey=True, layout="constrained")
                    for ax, (name, fit) in zip(axes, fits.items()):
                        ax.plot(positions, fit.beta, "o-", color=palette[name], label="Original response")
                        ax.plot(positions, altered[name].beta, "s--", color="0.2", label="Perturbed response")
                        ax.axhline(0, color="0.7", linewidth=0.8)
                        ax.set(title=name, xticks=positions, xticklabels=["Factor 1", "Factor 2", "Factor 3"])
                    axes[0].set_ylabel("Slope in original factor units")
                    axes[1].legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.12))
                    fig.suptitle("Constructed response perturbation: 0.5 bps RMS")
                    fig.savefig(FIGURES / "topic_svd_stability.png", dpi=160, bbox_inches="tight")
                    plt.show()
                    """),
                _markdown(r"""
                    ### 4. Verify the algebra along an independent path

                    A direct least-squares solve supplies an OLS check. A direct penalized
                    normal-equation solve checks ridge on this controlled design. The latter
                    is a validation identity, not a recommendation to form normal equations
                    for ill-conditioned unregularized production regressions.
                    """),
                _code("""
                    direct_ols = np.linalg.lstsq(np.column_stack([np.ones(n), X]), y, rcond=None)[0]
                    np.testing.assert_allclose(np.r_[fits["OLS"].intercept, fits["OLS"].beta],
                                               direct_ols, atol=1e-8)
                    direct_ridge = np.linalg.solve(
                        standardized.T @ standardized + n * 0.1 * np.eye(3),
                        standardized.T @ (y - y.mean()),
                    )
                    np.testing.assert_allclose(fits["Ridge"].beta, direct_ridge / X.std(axis=0), atol=1e-10)
                    np.testing.assert_allclose(np.sqrt(np.mean(perturbation**2)), 0.00005, atol=1e-15)
                    np.testing.assert_allclose(fits["Ridge"].shrink_filters,
                                               singular**2 / (singular**2 + n * 0.1), atol=1e-12)
                    display(Markdown(
                        f"**Result:** the constructed standardized condition number is "
                        f"**{fits['OLS'].standardized_condition:,.0f}**. The paired OLS slope change "
                        f"has L2 norm **{stability.loc['OLS', 'Slope change, L2']:.3f}**, while its "
                        f"same-geometry reconstruction changes by **{stability.loc['OLS', 'Same-geometry RMS change (bps)']:.3f} bps RMS**. "
                        "The changed-geometry probe shows why stable fitted values on one design "
                        "do not guarantee stable attribution when factor relationships change."
                    ))
                    """),
                _markdown("""
                    ## Takeaway

                    SVD explains where the sensitivity comes from. Ridge and PCR trade that
                    sensitivity for bias; neither creates additional economic information.
                    Using SVD to solve ordinary least squares does not itself regularize the
                    model. The empirical study must measure actual conditioning and compare
                    reconstruction losses before drawing a conclusion about sector ETFs.

                    Continue to [alpha and uncertainty](../03-alpha-uncertainty/study.ipynb),
                    or read the [empirical protocol](../../research/PROTOCOL.md).
                    """),
            ],
        },
        {
            "slug": "03-alpha-uncertainty",
            "title": "An intercept is an estimate, not evidence of skill",
            "intro": (
                "Ten constructed portfolios share factor and residual shocks but have no "
                "planted alpha. Estimate intercepts with serial-dependence-aware uncertainty, "
                "compare 60 versus 240 observations, and account for the declared family of "
                "ten tests. One realization illustrates interpretation; it does not validate test coverage."
            ),
            "cells": [
                _markdown(r"""
                    ## Goal

                    A fitted intercept can be nonzero even when the data-generating model's
                    intercept is zero. This constructed ten-portfolio panel has six factor
                    exposures, correlated residual shocks, and AR(1) residual persistence.
                    Its population intercepts are all zero by construction; sample residual
                    means are not forced to zero before fitting.

                    We report six-lag Newey–West intervals with the study's finite-sample
                    correction and normal approximation. Multiplying intercepts and standard
                    errors by 12 expresses **annualized arithmetic alpha**, not compounded
                    returns. These are approximate intervals, especially in the short sample.
                    """),
                _code("""
                    import numpy as np
                    import pandas as pd
                    import matplotlib.pyplot as plt
                    from IPython.display import display, Markdown
                    from research.models import hac_ols, holm_adjust

                    FIGURES = ROOT / "research" / "figures"
                    FIGURES.mkdir(parents=True, exist_ok=True)
                    plt.rcParams.update({"figure.dpi": 120, "font.size": 11,
                                         "axes.spines.top": False, "axes.spines.right": False})
                    rng = np.random.default_rng(20260921)
                    n, burn, portfolios = 240, 120, 10
                    draws = rng.normal(size=(n + burn, 6))
                    factor_map = np.eye(6)
                    factor_map[1, 0], factor_map[2, 0] = 0.35, -0.25
                    factors = 0.025 * draws @ factor_map.T + 0.002
                    beta = rng.normal(0, 0.25, size=(6, portfolios))
                    beta[0] = np.linspace(0.6, 1.5, portfolios)
                    innovations = 0.009 * rng.normal(size=(n + burn, 1)) + 0.012 * rng.normal(size=(n + burn, portfolios))
                    residuals = np.zeros_like(innovations)
                    for t in range(1, n + burn):
                        residuals[t] = 0.35 * residuals[t - 1] + innovations[t]
                    X = factors[burn:]
                    Y = (factors @ beta + residuals)[burn:]
                    names = [f"Portfolio {i + 1:02d}" for i in range(portfolios)]
                    display(pd.DataFrame({"Population alpha": np.zeros(portfolios),
                                          "Planted market-factor slope": beta[0]}, index=names))
                    """),
                _markdown(r"""
                    ### 1. Estimate a declared family of ten intercepts

                    Fit all six regressors with an intercept. Serial correlation motivates
                    HAC rather than an independent-observation standard error. The ten
                    full-sample intercepts form one testing family; the short-sample
                    diagnostic forms a separate, explicitly labeled family. Selecting
                    whichever sample appears most significant would require a wider family.
                    """),
                _code("""
                    results = {}
                    fits = {}
                    for sample_size in [240, 60]:
                        current = [hac_ols(X[-sample_size:], Y[-sample_size:, j], lags=6)
                                   for j in range(portfolios)]
                        fits[sample_size] = current
                        alpha = np.array([fit.coefficients[0] for fit in current])
                        se = np.array([fit.standard_errors[0] for fit in current])
                        p_values = np.array([fit.p_values[0] for fit in current])
                        results[sample_size] = pd.DataFrame({
                            "Alpha (%/year)": alpha * 1200,
                            "Lower 95% (%/year)": (alpha - 1.96 * se) * 1200,
                            "Upper 95% (%/year)": (alpha + 1.96 * se) * 1200,
                            "Raw p-value": p_values,
                            "Holm p-value, family of 10": holm_adjust(p_values),
                        }, index=names)
                    display(results[240].round(4))
                    """),
                _markdown(r"""
                    ### 2. Keep the interval with the estimate

                    Each point is an estimated intercept; each line is its **pointwise**
                    95% normal-approximation HAC interval. They are not simultaneous
                    confidence intervals. Both panels use the same units, portfolio order,
                    and horizontal scale. Shorter histories can change estimates as well
                    as precision; the effect is measured here rather than guaranteed.
                    """),
                _code("""
                    fig, axes = plt.subplots(1, 2, figsize=(12, 5.8), sharex=True, sharey=True, layout="constrained")
                    positions = np.arange(portfolios)
                    for ax, sample_size, color in zip(axes, [240, 60], ["#335C81", "#B07828"]):
                        table = results[sample_size]
                        width = table["Upper 95% (%/year)"] - table["Alpha (%/year)"]
                        ax.errorbar(table["Alpha (%/year)"], positions, xerr=width, fmt="o", color=color,
                                    capsize=3, markersize=5)
                        ax.axvline(0, color="0.35", linestyle="--", linewidth=1)
                        ax.set(yticks=positions, yticklabels=names, title=f"Last {sample_size} constructed observations",
                               xlabel="Annualized arithmetic alpha (%/year)")
                        ax.grid(axis="x", alpha=0.15)
                    axes[0].invert_yaxis()
                    fig.suptitle("Zero planted alpha; estimated intercepts with pointwise 95% HAC intervals")
                    fig.savefig(FIGURES / "topic_alpha_uncertainty.png", dpi=160, bbox_inches="tight")
                    plt.show()
                    """),
                _markdown(r"""
                    ### 3. Do not search ten intercepts and report one as a single test

                    Holm's adjustment is a step-down familywise procedure and does not
                    require independent tests when the underlying p-values are valid.
                    Here the raw HAC p-values themselves rely on an asymptotic approximation;
                    the adjustment does not repair poor small-sample inference. The counts
                    below describe this one fixed realization, not a simulated rejection rate.
                    """),
                _code("""
                    summaries = []
                    for sample_size, table in results.items():
                        summaries.append({
                            "Constructed observations": sample_size,
                            "Median 95% interval width (%/year)": np.median(table["Upper 95% (%/year)"] - table["Lower 95% (%/year)"]),
                            "Raw p below 0.05, out of 10": int((table["Raw p-value"] < 0.05).sum()),
                            "Holm p below 0.05, out of 10": int((table["Holm p-value, family of 10"] < 0.05).sum()),
                        })
                    summary = pd.DataFrame(summaries).set_index("Constructed observations")
                    display(summary.round(4))
                    display(results[60].round(4))
                    """),
                _markdown(r"""
                    ### 4. Reconcile the intercept and the adjustment

                    A separate least-squares call checks the point estimates. Sorting and
                    cumulatively maximizing the scaled p-values independently reconstructs
                    the Holm step-down adjustment. These are numerical identities, not
                    validation of nominal confidence-interval coverage under every process.
                    """),
                _code("""
                    direct = np.linalg.lstsq(np.column_stack([np.ones(n), X]), Y[:, 0], rcond=None)[0]
                    np.testing.assert_allclose(fits[240][0].coefficients, direct, atol=1e-10)
                    for sample_size, table in results.items():
                        p_values = table["Raw p-value"].to_numpy()
                        order = np.argsort(p_values)
                        independent = np.empty(portfolios)
                        independent[order] = np.minimum(1, np.maximum.accumulate(
                            (portfolios - np.arange(portfolios)) * p_values[order]
                        ))
                        np.testing.assert_allclose(table["Holm p-value, family of 10"], independent, atol=1e-14)
                        assert np.all(independent >= p_values - 1e-14)
                    full_width = summary.loc[240, "Median 95% interval width (%/year)"]
                    short_width = summary.loc[60, "Median 95% interval width (%/year)"]
                    display(Markdown(
                        f"**Result for this constructed realization:** median interval width is "
                        f"**{full_width:.2f} percentage points/year** with 240 observations and "
                        f"**{short_width:.2f}** with 60. All ten population intercepts were set "
                        "to zero, even though fitted intercepts differ. This example does not "
                        "estimate a false-positive rate or prove that the HAC intervals have "
                        "their nominal coverage."
                    ))
                    """),
                _markdown("""
                    ## Takeaway

                    Interpret an ETF intercept together with its benchmark model, time
                    sample, uncertainty, and the family of questions examined. An omitted
                    exposure, changing mandate, or estimation error can all affect a fitted
                    intercept. A model-relative unexplained mean is not demonstrated skill
                    or an executable hedged return.

                    Read the [empirical protocol](../../research/PROTOCOL.md) and
                    [method references](../../research/SOURCES.md), then return to the
                    [combined study](../../study.ipynb).
                    """),
            ],
        },
    ]
