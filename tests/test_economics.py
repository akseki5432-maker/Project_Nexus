import pytest

from nexus import economics


def test_cagr_and_growth():
    assert economics.cagr(100, 200, 10) == pytest.approx(0.071773463)
    assert economics.growth_rates([100, 110, 99]) == pytest.approx([0.1, -0.1])


def test_inflation_and_fisher():
    assert economics.inflation_rate(100, 103) == pytest.approx(0.03)
    assert economics.fisher_real_rate(0.0815, 0.05) == pytest.approx(0.03)
    assert economics.to_real(110, 110, 100) == pytest.approx(100)


def test_elasticity():
    e = economics.arc_elasticity(100, 80, 10, 12)
    assert e == pytest.approx(-1.2222222)
    assert economics.classify_elasticity(e) == "elastic"
    assert economics.classify_elasticity(-0.5) == "inelastic"


def test_linear_equilibrium():
    eq = economics.linear_equilibrium(100, 2, 10, 1)  # Qd=100-2P, Qs=10+P
    assert eq.price == pytest.approx(30)
    assert eq.quantity == pytest.approx(40)
    assert eq.consumer_surplus == pytest.approx(0.5 * 40 * (50 - 30))
    assert eq.producer_surplus == pytest.approx(0.5 * (40 + 10) * 30)


def test_break_even_and_leverage():
    be = economics.break_even(10_000, 50, 30)
    assert be.units == pytest.approx(500)
    assert be.revenue == pytest.approx(25_000)
    assert economics.break_even(10_000, 50, 30, target_profit=2_000).units == pytest.approx(600)
    assert economics.operating_leverage(1000, 50, 30, 10_000) == pytest.approx(2.0)
    with pytest.raises(ValueError):
        economics.break_even(1, 10, 10)


def test_macro():
    assert economics.gdp_expenditure(70, 20, 15, 10, 15) == 100
    assert economics.keynesian_multiplier(0.8) == pytest.approx(5)
    assert economics.rule_of_70(7) == pytest.approx(10)
