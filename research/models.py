"""Training-only factor fits and dependence-aware descriptive inference.

Frozen loadings multiplied by realized later factors reconstruct returns
conditionally; this operation is not an implementable return forecast.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import norm


@dataclass(frozen=True)
class FactorModel:
    """Coefficients are in original input units; diagnostics use standardized X.

    ``shrink_filters`` are the fitted-value multipliers in descending singular
    directions. ``effective_df`` includes the unpenalized intercept. Rank refers
    only to the centered feature design, excluding that intercept.
    """

    method: str
    beta: np.ndarray
    intercept: float
    feature_mean: np.ndarray
    feature_scale: np.ndarray
    standardized_beta: np.ndarray
    singular_values: np.ndarray
    standardized_condition: float
    rank: int
    rank_tolerance: float
    shrink_filters: np.ndarray
    effective_df: float
    nobs: int
    ridge_lambda: float | None
    n_components: int | None

    def predict(self, X):
        """Apply frozen raw coefficients to finite two-dimensional observations."""
        values = np.asarray(X, dtype=float)
        if values.ndim != 2 or values.shape[1] != len(self.beta):
            raise ValueError("Prediction design must be 2D with the fitted feature count")
        if not np.isfinite(values).all():
            raise ValueError("Prediction design contains nonfinite observations")
        return self.intercept + values @ self.beta


@dataclass(frozen=True)
class HACResult:
    """OLS inference in raw units, with the intercept first in every array.

    P-values use a two-sided asymptotic normal approximation, not a Student-t
    reference. ``degenerate`` marks an effectively exact fit: its z-statistics
    and p-values are NaN because residual-based uncertainty is uninformative.
    """

    coefficients: np.ndarray
    covariance: np.ndarray
    standard_errors: np.ndarray
    z_statistics: np.ndarray
    p_values: np.ndarray
    nobs: int
    rank: int
    df_resid: int
    lags: int
    degenerate: bool


def _training_arrays(X, y):
    values = np.asarray(X, dtype=float)
    target = np.asarray(y, dtype=float)
    if values.ndim != 2 or values.shape[0] < 2 or values.shape[1] < 1:
        raise ValueError("Training design must have at least two rows and one column")
    if target.ndim != 1 or target.shape[0] != values.shape[0]:
        raise ValueError("Target must be a one-dimensional vector matching training rows")
    if not np.isfinite(values).all() or not np.isfinite(target).all():
        raise ValueError("Training observations must be finite; no rows are silently removed")
    if (np.ptp(values, axis=0) == 0).any():
        raise ValueError("Constant predictor columns are not identified with an intercept")
    means = values.mean(axis=0)
    scales = values.std(axis=0, ddof=0)
    if not np.isfinite(means).all() or not np.isfinite(scales).all() or (scales <= 0).any():
        raise ValueError("Feature centering or scaling is not finite and positive")
    return values, target, means, scales


def fit_factor_model(X, y, method="ols", ridge_lambda=0.1, n_components=4):
    """Fit OLS, ridge, PCR or one-factor market OLS with a free intercept.

    Center X on this training sample and divide by its population (ddof=0)
    standard deviation. Ridge minimizes RSS/n + ridge_lambda * ||b||^2 in those
    standardized units, hence its SVD denominator is s^2 + n*ridge_lambda.
    PCR retains the requested leading singular directions; it does not choose k
    using y or later observations. For market OLS, pass ONLY the market column.

    OLS truncates singular values below eps*max(n,p)*s_max and reports its rank.
    This is the minimum-norm solution in standardized coordinates. Individual
    raw betas in rank-deficient designs are not uniquely identified. PCR refuses
    to retain unidentified directions. Ridge accepts collinearity with lambda>0.
    """
    values, target, means, scales = _training_arrays(X, y)
    if method not in {"ols", "ridge", "pcr", "market"}:
        raise ValueError("Unknown method; choose ols, ridge, pcr, or market")
    if method == "market" and values.shape[1] != 1:
        raise ValueError("Market OLS requires an explicitly selected single market column")
    nobs, nfeatures = values.shape
    standardized = (values - means) / scales
    left, singular, right = np.linalg.svd(standardized, full_matrices=False)
    tolerance = np.finfo(float).eps * max(standardized.shape) * singular[0]
    identified = singular > tolerance
    rank = int(identified.sum())
    condition = float(singular[0] / singular[-1]) if rank == nfeatures else float("inf")
    filters = identified.astype(float)
    gains = np.zeros_like(singular)
    selected_lambda, selected_components = None, None
    if method == "ridge":
        if not np.isscalar(ridge_lambda) or not np.isfinite(ridge_lambda) or ridge_lambda <= 0:
            raise ValueError("Ridge requires a finite positive lambda; use OLS for zero")
        selected_lambda = float(ridge_lambda)
        denominator = singular**2 + nobs * selected_lambda
        gains = singular / denominator
        filters = singular**2 / denominator
    elif method == "pcr":
        if (
            not isinstance(n_components, (int, np.integer))
            or isinstance(n_components, (bool, np.bool_))
            or not 1 <= n_components <= rank
        ):
            raise ValueError("PCR components must be an integer between one and numerical rank")
        selected_components = int(n_components)
        filters = (np.arange(len(singular)) < n_components).astype(float)
        gains[:n_components] = 1 / singular[:n_components]
    else:
        gains[identified] = 1 / singular[identified]
    standardized_beta = right.T @ (gains * (left.T @ (target - target.mean())))
    raw_beta = standardized_beta / scales
    intercept = float(target.mean() - means @ raw_beta)
    return FactorModel(
        method=method,
        beta=raw_beta,
        intercept=intercept,
        feature_mean=means,
        feature_scale=scales,
        standardized_beta=standardized_beta,
        singular_values=singular,
        standardized_condition=condition,
        rank=rank,
        rank_tolerance=float(tolerance),
        shrink_filters=filters,
        effective_df=float(1 + filters.sum()),
        nobs=nobs,
        ridge_lambda=selected_lambda,
        n_components=selected_components,
    )


def hac_ols(X, y, lags=6):
    """OLS Newey-West covariance: Bartlett lags and n/(n-p) correction.

    Here p counts ALL estimated coefficients including the intercept. Rows must
    be consecutive equally spaced observations in their original time order;
    the caller owns date validation. Computation uses standardized coordinates
    and then transforms the covariance back to raw coefficient units.
    """
    model = fit_factor_model(X, y, method="ols")
    values, target = np.asarray(X, dtype=float), np.asarray(y, dtype=float)
    nobs, nfeatures = values.shape
    nparameters = nfeatures + 1
    if model.rank != nfeatures or nobs <= nparameters:
        raise ValueError("HAC coefficient inference requires full column rank and n > p")
    if (
        not isinstance(lags, (int, np.integer))
        or isinstance(lags, (bool, np.bool_))
        or not 0 <= lags < nobs
    ):
        raise ValueError("HAC lags must be an integer between zero and n-1")
    design = np.column_stack([np.ones(nobs), (values - model.feature_mean) / model.feature_scale])
    residuals = target - model.predict(values)
    scores = design * residuals[:, None]
    meat = scores.T @ scores
    for lag in range(1, lags + 1):
        cross = scores[lag:].T @ scores[:-lag]
        meat += (1 - lag / (lags + 1)) * (cross + cross.T)
    # Invert through singular values instead of forming normal equations, which
    # would square the design's condition number before the numerical solve.
    _, design_singular, design_right = np.linalg.svd(design, full_matrices=False)
    bread = (design_right.T / design_singular**2) @ design_right
    covariance_scaled = bread @ meat @ bread * nobs / (nobs - nparameters)
    transform = np.zeros((nparameters, nparameters))
    transform[0, 0] = 1
    transform[0, 1:] = -model.feature_mean / model.feature_scale
    transform[1:, 1:] = np.diag(1 / model.feature_scale)
    covariance = transform @ covariance_scaled @ transform.T
    covariance = (covariance + covariance.T) / 2
    standard_errors = np.sqrt(np.maximum(np.diag(covariance), 0))
    coefficients = np.r_[model.intercept, model.beta]
    reference_scale = max(float(np.max(np.abs(target))), np.finfo(float).tiny)
    degenerate = bool(np.max(np.abs(residuals)) <= np.finfo(float).eps * nobs * reference_scale)
    z_statistics = np.full(nparameters, np.nan)
    if not degenerate:
        positive = standard_errors > 0
        z_statistics[positive] = coefficients[positive] / standard_errors[positive]
    p_values = 2 * norm.sf(np.abs(z_statistics))
    return HACResult(
        coefficients=coefficients,
        covariance=covariance,
        standard_errors=standard_errors,
        z_statistics=z_statistics,
        p_values=p_values,
        nobs=nobs,
        rank=nparameters,
        df_resid=nobs - nparameters,
        lags=int(lags),
        degenerate=degenerate,
    )


def holm_adjust(p_values):
    """Holm step-down familywise adjustment, returned in the original order."""
    p_values = np.asarray(p_values, dtype=float)
    if (
        p_values.ndim != 1
        or len(p_values) == 0
        or not np.isfinite(p_values).all()
        or ((p_values < 0) | (p_values > 1)).any()
    ):
        raise ValueError("Supply a nonempty one-dimensional family of finite p-values in [0,1]")
    order = np.argsort(p_values, kind="stable")
    adjusted_sorted = np.minimum(
        1, np.maximum.accumulate(p_values[order] * np.arange(len(p_values), 0, -1))
    )
    adjusted = np.empty_like(adjusted_sorted)
    adjusted[order] = adjusted_sorted
    return adjusted


def paired_block_mean_difference(loss_a, loss_b, block=12, draws=2000, seed=20260920):
    """Paired circular-block percentile interval for mean(loss_a - loss_b).

    Both inputs must have the SAME complete monthly DatetimeIndex. Dates are
    never sorted, dropped or independently sampled. Consecutive date positions
    are sampled in common blocks, wrapping the final date back to the first.
    The interval is conditional on the retained models and evaluation sample;
    it does not include model-selection or vintage uncertainty. Negative means
    the first series has lower loss. At least two complete blocks are required.
    """
    if not isinstance(loss_a, pd.Series) or not isinstance(loss_b, pd.Series):
        raise ValueError("Paired losses must be pandas Series with explicit monthly dates")
    dates = loss_a.index
    if (
        not isinstance(dates, pd.DatetimeIndex)
        or not dates.equals(loss_b.index)
        or dates.has_duplicates
        or dates.hasnans
        or not dates.is_monotonic_increasing
    ):
        raise ValueError("Loss dates must be identical, ordered, unique and nonmissing")
    month_numbers = dates.year * 12 + dates.month
    if len(dates) < 2 or not np.all(np.diff(month_numbers) == 1):
        raise ValueError("Paired monthly observations must be consecutive without missing months")
    if (
        not isinstance(block, (int, np.integer))
        or isinstance(block, (bool, np.bool_))
        or block < 1
        or len(dates) < 2 * block
    ):
        raise ValueError("Block length must be a positive integer with at least two blocks of data")
    if not isinstance(draws, (int, np.integer)) or isinstance(draws, (bool, np.bool_)) or draws < 1:
        raise ValueError("Bootstrap draws must be a positive integer")
    first, second = loss_a.to_numpy(dtype=float), loss_b.to_numpy(dtype=float)
    if not np.isfinite(first).all() or not np.isfinite(second).all():
        raise ValueError("Losses must be finite; no paired observations are removed")
    difference = first - second
    nobs = len(difference)
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, nobs, size=(draws, int(np.ceil(nobs / block))))
    indices = ((starts[:, :, None] + np.arange(block)) % nobs).reshape(draws, -1)[:, :nobs]
    means = difference[indices].mean(axis=1)
    low, high = np.quantile(means, [0.025, 0.975])
    return {
        "estimate": float(difference.mean()),
        "lower95": float(low),
        "upper95": float(high),
        "n": nobs,
        "block": int(block),
        "draws": int(draws),
        "seed": int(seed),
        "first_date": dates[0].isoformat(),
        "last_date": dates[-1].isoformat(),
    }
