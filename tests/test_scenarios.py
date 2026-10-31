import pytest

from nexus import scenarios, tvm


def profit(price, volume, unit_cost, fixed_cost):
    return (price - unit_cost) * volume - fixed_cost


BASE = {"price": 10.0, "volume": 1000.0, "unit_cost": 6.0, "fixed_cost": 2000.0}


def test_one_way():
    out = scenarios.one_way(profit, BASE, "price", [9, 10, 11])
    assert [v for _, v in out] == [1000, 2000, 3000]


def test_two_way_shape_and_values():
    grid = scenarios.two_way(profit, BASE, "price", [10, 12], "volume", [500, 1000, 1500])
    assert len(grid) == 2 and len(grid[0]) == 3
    assert grid[1][2] == pytest.approx((12 - 6) * 1500 - 2000)


def test_tornado_sorted_by_swing():
    bars = scenarios.tornado(profit, BASE, {
        "price": (9, 11),            # swing 2000
        "fixed_cost": (1500, 2500),  # swing 1000
        "volume": (500, 1500),       # swing 4000
    })
    assert [b.name for b in bars] == ["volume", "price", "fixed_cost"]
    assert bars[0].swing == pytest.approx(4000)


def test_run_scenarios():
    res = scenarios.run_scenarios(profit, BASE, {
        "base": {}, "bear": {"volume": 600, "price": 9}, "bull": {"volume": 1400}})
    assert res == {"base": 2000, "bear": -200, "bull": 3600}


def test_monte_carlo_reproducible_and_sane():
    def model(cf, rate):
        return tvm.npv(rate, [-1000, cf, cf, cf])

    samplers = {"cf": scenarios.normal(450, 50), "rate": scenarios.fixed(0.1)}
    a = scenarios.monte_carlo(model, samplers, trials=5000, seed=7)
    b = scenarios.monte_carlo(model, samplers, trials=5000, seed=7)
    assert a.outcomes == b.outcomes
    expected = tvm.npv(0.1, [-1000, 450, 450, 450])
    assert a.mean == pytest.approx(expected, rel=0.02)
    s = a.summary()
    assert s["p5"] < s["p50"] < s["p95"]
    assert 0 <= s["prob_negative"] <= 1


def test_percentile_interpolation():
    r = scenarios.SimulationResult([1.0, 2.0, 3.0, 4.0])
    assert r.percentile(0) == 1 and r.percentile(100) == 4
    assert r.percentile(50) == pytest.approx(2.5)
    assert r.prob_below(3) == 0.5


def test_samplers_in_range():
    import random
    rng = random.Random(1)
    assert all(2 <= scenarios.uniform(2, 3)(rng) <= 3 for _ in range(100))
    assert all(1 <= scenarios.triangular(1, 2, 5)(rng) <= 5 for _ in range(100))
    with pytest.raises(ValueError):
        scenarios.monte_carlo(lambda: 0.0, {}, trials=0)
