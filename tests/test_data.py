from zipfile import ZipFile

import numpy as np
import pandas as pd
import pytest

from research.data import french_monthly, monthly_simple_returns


def test_french_percent_conversion_excludes_annual_table(tmp_path):
    path = tmp_path / "fixture.zip"
    with ZipFile(path, "w") as z:
        z.writestr(
            "test.csv",
            "Description\n,Mkt-RF,RF\n202001,2.00,0.30\n202002,-1.0,0.2\n Annual Factors:\n2020,99,99\n",
        )
    f = french_monthly(path, ["Mkt-RF", "RF"])
    assert len(f) == 2
    np.testing.assert_allclose(f.iloc[0], [0.02, 0.003])


@pytest.mark.parametrize("rows", ["202001,2\n202001,3", "202001,2\n202003,3", "202001,-99.99"])
def test_french_rejects_duplicates_gaps_and_missing_sentinel(tmp_path, rows):
    path = tmp_path / "bad.zip"
    with ZipFile(path, "w") as z:
        z.writestr("test.csv", "Description\n,Mom\n" + rows)
    with pytest.raises(ValueError):
        french_monthly(path, ["Mom"])


def test_complete_month_simple_returns_and_rf_units():
    sessions = pd.DatetimeIndex(["2019-12-30", "2019-12-31", "2020-01-02", "2020-01-31"])
    prices = pd.DataFrame({"fund": [98, 100, 101, 102]}, index=sessions)
    returns = monthly_simple_returns(prices, sessions)
    assert list(returns.index.astype(str)) == ["2020-01"]
    assert returns.iloc[0, 0] - 0.3 / 100 == pytest.approx(0.017)


def test_missing_session_and_nonpositive_price_fail():
    sessions = pd.DatetimeIndex(["2019-12-31", "2020-01-02", "2020-01-31"])
    prices = pd.DataFrame({"fund": [100, 101, 102]}, index=sessions)
    with pytest.raises(ValueError):
        monthly_simple_returns(prices.iloc[[0, 2]], sessions)
    prices.iloc[-1] = np.nan
    with pytest.raises(ValueError):
        monthly_simple_returns(prices, sessions)
