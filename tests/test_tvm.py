import math

import pytest

from nexus import tvm


def test_fv_pv_roundtrip():
    fv = tvm.future_value(1000, 0.05, 10)
    assert fv == pytest.approx(1628.894627)
    assert tvm.present_value(fv, 0.05, 10) == pytest.approx(1000)


def test_annuities():
    assert tvm.annuity_pv(100, 0.05, 10) == pytest.approx(772.173493)
    assert tvm.annuity_fv(100, 0.05, 10) == pytest.approx(1257.789254)
    assert tvm.annuity_pv(100, 0.05, 10, due=True) == pytest.approx(810.782168)
    assert tvm.annuity_pv(100, 0, 10) == 1000


def test_payment_matches_mortgage_formula():
    assert tvm.payment(200_000, 0.06 / 12, 360) == pytest.approx(1199.101050)
    assert tvm.payment(1200, 0, 12) == 100


def test_npv_irr_consistent():
    flows = [-1000, 300, 400, 500]
    rate = tvm.irr(flows)
    assert rate == pytest.approx(0.0889633947, abs=1e-6)
    assert tvm.npv(rate, flows) == pytest.approx(0, abs=1e-6)


def test_irr_requires_sign_change():
    with pytest.raises(ValueError):
        tvm.irr([100, 200, 300])


def test_payback():
    assert tvm.payback_period([-1000, 400, 400, 400]) == pytest.approx(2.5)
    assert math.isinf(tvm.payback_period([-1000, 100, 100]))


def test_profitability_index():
    assert tvm.profitability_index(0.1, [-1000, 1100]) == pytest.approx(1.0)


def test_ear():
    assert tvm.effective_annual_rate(0.12, 12) == pytest.approx(0.126825030)


def test_amortization_pays_off():
    rows = tvm.amortization_schedule(10_000, 0.06, 2)
    assert len(rows) == 24
    assert rows[-1].balance == pytest.approx(0, abs=1e-6)
    assert sum(r.principal for r in rows) == pytest.approx(10_000)
