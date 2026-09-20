"""Independent linear algebra, covariance arithmetic and pairing checks."""

import numpy as np
import pandas as pd
import pytest
from scipy.stats import norm

from research.models import (
    fit_factor_model,
    hac_ols,
    holm_adjust,
    paired_block_mean_difference,
)


@pytest.fixture
def sample():
    rng = np.random.default_rng(20260920)
    X = rng.normal(size=(84, 6)) * np.array([1, 0.02, 4, 0.3, 2, 0.08])
    X += np.array([0.2, -0.01, 1, 0.05, -0.1, 0.01])
    y = 0.012 + X @ np.array([0.1, 0.3, -0.2, 0.05, 0.08, -0.4]) + rng.normal(0, 0.08, 84)
    return X, y


def test_ols_matches_independent_raw_lstsq(sample):
    X, y = sample
    expected = np.linalg.lstsq(np.column_stack([np.ones(len(y)), X]), y, rcond=None)[0]
    fitted = fit_factor_model(X, y)
    np.testing.assert_allclose(np.r_[fitted.intercept, fitted.beta], expected, rtol=1e-11)
    assert fitted.rank == 6
    assert fitted.effective_df == 7
    np.testing.assert_allclose(fitted.feature_scale, np.std(X, axis=0, ddof=0))


def test_ridge_matches_direct_penalized_normal_equations(sample):
    X, y = sample
    Z = (X - X.mean(axis=0)) / X.std(axis=0, ddof=0)
    design = np.column_stack([np.ones(len(y)), Z])
    penalty = np.diag(np.r_[0, np.repeat(0.1, X.shape[1])])
    expected = np.linalg.solve(design.T @ design / len(y) + penalty, design.T @ y / len(y))
    fitted = fit_factor_model(X, y, method="ridge", ridge_lambda=0.1)
    np.testing.assert_allclose(fitted.predict(X), design @ expected, atol=1e-13)
    np.testing.assert_allclose(fitted.standardized_beta, expected[1:], atol=1e-13)
    assert fitted.intercept + X.mean(axis=0) @ fitted.beta == pytest.approx(y.mean())
    s = fitted.singular_values
    np.testing.assert_allclose(fitted.shrink_filters, s**2 / (s**2 + len(y) * 0.1))
    assert 1 < fitted.effective_df < 7


def test_full_pcr_is_ols_and_truncation_retains_exactly_k_directions(sample):
    X, y = sample
    ols = fit_factor_model(X, y)
    full = fit_factor_model(X, y, method="pcr", n_components=6)
    partial = fit_factor_model(X, y, method="pcr", n_components=4)
    np.testing.assert_allclose(full.beta, ols.beta, atol=1e-13)
    assert full.intercept == pytest.approx(ols.intercept)
    assert partial.effective_df == 5
    np.testing.assert_array_equal(partial.shrink_filters, [1, 1, 1, 1, 0, 0])


@pytest.mark.parametrize("method", ["ols", "ridge", "pcr"])
def test_predictions_are_invariant_to_predictor_units_and_offsets(sample, method):
    X, y = sample
    multipliers = np.array([100, 0.1, 0.01, 4, 8, 0.5])
    offsets = np.array([0.2, 0.1, -0.3, 1.1, -0.4, 0.5])
    original = fit_factor_model(X, y, method=method)
    changed = fit_factor_model(X * multipliers + offsets, y, method=method)
    test = X[:9] + np.array([0.02, 0.01, -0.1, 0.2, 0.03, -0.01])
    np.testing.assert_allclose(
        original.predict(test), changed.predict(test * multipliers + offsets), atol=2e-13
    )
    np.testing.assert_allclose(original.beta, changed.beta * multipliers, atol=2e-12)


def test_later_inputs_do_not_refit_training_means_or_scales(sample):
    X, y = sample
    fitted = fit_factor_model(X[:60], y[:60], method="ridge")
    original_beta = fitted.beta.copy()
    original_mean = fitted.feature_mean.copy()
    fitted.predict(X[60:])
    fitted.predict(X[60:] * 100)
    np.testing.assert_array_equal(fitted.beta, original_beta)
    np.testing.assert_array_equal(fitted.feature_mean, original_mean)
    np.testing.assert_allclose(fitted.feature_mean, X[:60].mean(axis=0))


def test_market_model_requires_explicit_market_column(sample):
    X, y = sample
    fitted = fit_factor_model(X[:, :1], y, method="market")
    expected = np.linalg.lstsq(np.column_stack([np.ones(len(y)), X[:, 0]]), y, rcond=None)[0]
    np.testing.assert_allclose(np.r_[fitted.intercept, fitted.beta], expected)
    with pytest.raises(ValueError, match="single market"):
        fit_factor_model(X, y, method="market")


def test_rank_deficiency_is_reported_and_not_hidden(sample):
    X, y = sample
    collinear = np.column_stack([X[:, 0], X[:, 0], X[:, 1]])
    ols = fit_factor_model(collinear, y)
    ridge = fit_factor_model(collinear, y, method="ridge")
    expected = np.linalg.lstsq(np.column_stack([np.ones(len(y)), collinear]), y, rcond=None)[0]
    np.testing.assert_allclose(ols.predict(collinear), np.c_[np.ones(len(y)), collinear] @ expected)
    assert ols.rank == ridge.rank == 2
    assert np.isinf(ols.standardized_condition)
    assert ols.effective_df == 3
    assert np.isfinite(ridge.predict(collinear)).all()
    with pytest.raises(ValueError, match="numerical rank"):
        fit_factor_model(collinear, y, method="pcr", n_components=3)
    with pytest.raises(ValueError, match="full column rank"):
        hac_ols(collinear, y)


def test_hac_matches_explicit_raw_coordinate_double_sum(sample):
    X, y = sample
    nobs = len(y)
    design = np.column_stack([np.ones(nobs), X])
    coef = np.linalg.lstsq(design, y, rcond=None)[0]
    residuals = y - design @ coef
    meat = np.zeros((7, 7))
    for i in range(nobs):
        for j in range(nobs):
            lag = abs(i - j)
            if lag <= 6:
                meat += (1 - lag / 7) * residuals[i] * residuals[j] * np.outer(design[i], design[j])
    inverse = np.linalg.inv(design.T @ design)
    expected = inverse @ meat @ inverse * nobs / (nobs - 7)
    result = hac_ols(X, y, lags=6)
    np.testing.assert_allclose(result.coefficients, coef, rtol=1e-11)
    np.testing.assert_allclose(result.covariance, expected, rtol=1e-10, atol=1e-14)
    np.testing.assert_allclose(
        result.p_values, 2 * norm.sf(np.abs(coef / np.sqrt(np.diag(expected))))
    )
    assert result.df_resid == nobs - 7
    assert not result.degenerate


def test_hac_zero_lag_is_corrected_white_covariance(sample):
    X, y = sample
    design = np.c_[np.ones(len(y)), X]
    coef = np.linalg.lstsq(design, y, rcond=None)[0]
    residuals = y - design @ coef
    inv = np.linalg.inv(design.T @ design)
    expected = inv @ (design.T @ np.diag(residuals**2) @ design) @ inv * len(y) / (len(y) - 7)
    np.testing.assert_allclose(hac_ols(X, y, lags=0).covariance, expected, rtol=1e-10, atol=1e-14)


def test_constant_target_has_an_intercept_but_degenerate_inference(sample):
    X, _ = sample
    y = np.repeat(0.125, len(X))
    fit = fit_factor_model(X, y, method="ridge")
    np.testing.assert_allclose(fit.beta, 0)
    np.testing.assert_allclose(fit.predict(X), y)
    assert hac_ols(X, y).degenerate
    assert np.isnan(hac_ols(X, y).p_values).all()


def test_holm_known_case_restores_original_order_and_ties():
    np.testing.assert_allclose(holm_adjust([0.04, 0.01, 0.03, 0.20]), [0.09, 0.04, 0.09, 0.20])
    np.testing.assert_allclose(holm_adjust([0.02, 0.02, 0.01]), [0.04, 0.04, 0.03])
    np.testing.assert_array_equal(holm_adjust([0, 1]), [0, 1])


def test_bootstrap_matches_independent_circular_sampling_and_is_deterministic():
    dates = pd.date_range("2000-01-31", periods=30, freq="ME")
    a = pd.Series(np.arange(30) ** 2 / 1000, index=dates)
    b = pd.Series(np.arange(30) / 100, index=dates)
    actual = paired_block_mean_difference(a, b, block=6, draws=40, seed=37)
    rng = np.random.default_rng(37)
    means = []
    for _ in range(40):
        positions = []
        for start in rng.integers(0, 30, 5):
            positions.extend((start + offset) % 30 for offset in range(6))
        means.append(np.mean([a.iloc[i] - b.iloc[i] for i in positions]))
    low, high = np.quantile(means, [0.025, 0.975])
    assert actual["estimate"] == pytest.approx((a - b).mean())
    assert actual["lower95"] == pytest.approx(low)
    assert actual["upper95"] == pytest.approx(high)
    assert actual == paired_block_mean_difference(a, b, block=6, draws=40, seed=37)
    assert actual["first_date"] == dates[0].isoformat()
    constant = paired_block_mean_difference(a + 0.25, a, block=6, draws=20)
    np.testing.assert_allclose(
        [constant["estimate"], constant["lower95"], constant["upper95"]], 0.25
    )


def test_bootstrap_rejects_mispairing_and_missing_months():
    dates = pd.date_range("2000-01-31", periods=30, freq="ME")
    losses = pd.Series(np.arange(30), index=dates)
    with pytest.raises(ValueError, match="identical"):
        paired_block_mean_difference(losses, losses.iloc[::-1], block=6)
    missing = losses.drop(dates[12])
    with pytest.raises(ValueError, match="missing months"):
        paired_block_mean_difference(missing, missing, block=6)
    with pytest.raises(ValueError, match="two blocks"):
        paired_block_mean_difference(losses, losses, block=16)


@pytest.mark.parametrize("problem", ["constant", "missing", "target_shape", "predict_shape"])
def test_invalid_inputs_fail_without_silent_repairs(sample, problem):
    X, y = (array.copy() for array in sample)
    with pytest.raises(ValueError):
        if problem == "constant":
            X[:, 0] = 1
        elif problem == "missing":
            y[3] = np.nan
        elif problem == "target_shape":
            y = y[:, None]
        else:
            fit_factor_model(X, y).predict(X[:, :2])
        fit_factor_model(X, y)
