import json
from pathlib import Path

import pytest

from nexus import ratios

EXAMPLE = Path(__file__).parent.parent / "examples" / "acme_financials.json"


@pytest.fixture
def fin():
    return ratios.Financials.from_dict(json.loads(EXAMPLE.read_text()))


def test_liquidity(fin):
    r = ratios.liquidity(fin)
    assert r["current_ratio"] == pytest.approx(1.8)
    assert r["quick_ratio"] == pytest.approx(1.2)


def test_profitability(fin):
    r = ratios.profitability(fin)
    assert r["gross_margin"] == pytest.approx(0.4)
    assert r["roe"] == pytest.approx(0.15)


def test_dupont_reconciles_to_roe(fin):
    d = ratios.dupont(fin)
    assert d["roe"] == pytest.approx(ratios.profitability(fin)["roe"])


def test_zero_denominator_is_nan(fin):
    fin.interest_expense = 0
    assert ratios.leverage(fin)["interest_coverage"] != ratios.leverage(fin)["interest_coverage"]


def test_analyze_groups(fin):
    assert set(ratios.analyze(fin)) == {"liquidity", "leverage", "profitability",
                                        "efficiency", "dupont"}
