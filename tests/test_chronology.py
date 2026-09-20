import numpy as np
import pandas as pd

from research.run_study import rolling_reconstruction


def test_future_observations_cannot_change_earlier_fits_or_reconstruction():
    rng = np.random.default_rng(891)
    dates = pd.period_range("2000-01", periods=40, freq="M")
    x = pd.DataFrame(
        rng.normal(size=(40, 6)) * 0.03,
        index=dates,
        columns=["Mkt-RF", "SMB", "HML", "RMW", "CMA", "Mom"],
    )
    y = pd.DataFrame({"fund": x.iloc[:, 0] + rng.normal(size=40) * 0.01}, index=dates)
    specs = {"OLS": ("ols", 6, {}), "Ridge 0.1": ("ridge", 6, {"ridge_lambda": 0.1})}
    baseline = rolling_reconstruction(x, y, window=12, specifications=specs)
    x.iloc[30:] += 100
    y.iloc[30:] -= 100
    changed = rolling_reconstruction(x, y, window=12, specifications=specs)
    pd.testing.assert_frame_equal(
        baseline[baseline.month < str(dates[30])], changed[changed.month < str(dates[30])]
    )
    assert (baseline.train_end < baseline.month).all()
    # At the changed month, exposure estimates remain unchanged, but supplied factors
    # and the response change: this deliberately is conditional reconstruction.
    cols = [c for c in baseline if c.startswith("beta_")] + ["intercept"]
    np.testing.assert_allclose(
        baseline.loc[baseline.month == str(dates[30]), cols],
        changed.loc[changed.month == str(dates[30]), cols],
    )
