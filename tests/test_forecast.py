import json
from pathlib import Path

import pytest

from nexus import forecast

EXAMPLE = Path(__file__).parent.parent / "examples" / "acme_assumptions.json"


def test_project_year_one():
    a = forecast.Assumptions(base_revenue=1000, growth=[0.10], ebit_margin=0.20,
                             tax_rate=0.25, depreciation_pct=0.05, capex_pct=0.06,
                             nwc_pct=0.10)
    y = forecast.project(a).years[0]
    assert y.revenue == pytest.approx(1100)
    assert y.ebit == pytest.approx(220)
    assert y.change_in_nwc == pytest.approx(10)
    # 220*0.75 + 55 - 66 - 10
    assert y.fcf == pytest.approx(144)


def test_example_file_values():
    a = forecast.Assumptions.from_dict(json.loads(EXAMPLE.read_text()))
    fc = forecast.project(a)
    assert len(fc.years) == 5
    assert fc.free_cash_flows[0] == pytest.approx(1_200_000)
    res = forecast.value(a, 0.09, 0.025, net_debt=4e6, shares_outstanding=1e6)
    assert res.per_share == pytest.approx(18.95, abs=0.01)


def test_rows_are_dicts():
    a = forecast.Assumptions(1000, [0.05, 0.05], 0.1, 0.2)
    rows = forecast.project(a).rows()
    assert rows[1]["year"] == 2 and "fcf" in rows[1]
