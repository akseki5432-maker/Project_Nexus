import pytest

from nexus import valuation


def test_capm_and_wacc():
    ke = valuation.capm(0.03, 1.5, 0.08)
    assert ke == pytest.approx(0.105)
    assert valuation.wacc(60, 40, ke, 0.05, 0.25) == pytest.approx(0.078)


def test_gordon_growth():
    assert valuation.gordon_growth(5, 0.10, 0.05) == pytest.approx(100)
    with pytest.raises(ValueError):
        valuation.gordon_growth(5, 0.05, 0.05)


def test_fcf():
    assert valuation.free_cash_flow(100, 0.25, 20, 30, 5) == pytest.approx(60)


def test_dcf():
    res = valuation.dcf([100, 100], 0.10, 0.0, net_debt=50, shares_outstanding=10)
    # A flat 100 perpetuity at 10% is worth 1000 regardless of the split.
    assert res.enterprise_value == pytest.approx(1000)
    assert res.equity_value == pytest.approx(950)
    assert res.per_share == pytest.approx(95)


def test_bond_at_par_and_duration():
    assert valuation.bond_price(1000, 0.05, 0.05, 10) == pytest.approx(1000)
    assert valuation.bond_price(1000, 0.05, 0.06, 10) < 1000
    mac, mod = valuation.bond_duration(1000, 0.0, 0.05, 5, frequency=1)
    assert mac == pytest.approx(5)  # zero-coupon duration equals maturity
    assert mod == pytest.approx(5 / 1.05)
