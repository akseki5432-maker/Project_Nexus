import pytest

from nexus import tax
from nexus.cli import main


def test_single_wage_earner_2026():
    # 75,000 - 16,100 standard deduction = 58,900 taxable.
    # 10% x 12,400 + 12% x 38,000 + 22% x 8,500 = 1,240 + 4,560 + 1,870 = 7,670
    r = tax.estimate(tax.TaxInput(year=2026, wages=75_000, withholding=7_000))
    assert r.taxable_income == pytest.approx(58_900)
    assert r.total_tax == pytest.approx(7_670)
    assert r.balance_due == pytest.approx(670)
    assert r.marginal_rate == 0.22
    assert r.payroll_taxes_withheld == pytest.approx(75_000 * 0.0765)


def test_2025_brackets_and_deduction():
    # 60,000 - 15,750 = 44,250 -> 10% x 11,925 + 12% x 32,325 = 1,192.50 + 3,879 = 5,071.50
    r = tax.estimate(tax.TaxInput(year=2025, wages=60_000))
    assert r.total_tax == pytest.approx(5_071.50)


def test_married_joint_with_children_refund():
    # 100,000 - 32,200 = 67,800 -> 2,480 + 12% x 43,000 = 7,640; less 2 x 2,200 credit
    r = tax.estimate(tax.TaxInput(status="married-joint", wages=100_000, children=2,
                                  withholding=5_000))
    assert r.income_tax_before_credits == pytest.approx(7_640)
    assert r.child_credit_used == pytest.approx(4_400)
    assert r.total_tax == pytest.approx(3_240)
    assert r.refund == pytest.approx(1_760)


def test_refundable_child_credit_for_low_income():
    # 20,000 wages, HoH: taxable 0, so the credit can only come back as a refund,
    # capped at 15% of (20,000 - 2,500) = 2,625.
    r = tax.estimate(tax.TaxInput(status="head-of-household", wages=20_000, children=2))
    assert r.income_tax == 0
    assert r.refundable_credits == pytest.approx(2_625)
    assert r.balance_due == pytest.approx(-2_625)


def test_child_credit_phases_out():
    # AGI 210,500 single -> 10,500 over -> 11 x 50 = 550 off one 2,200 credit.
    r = tax.estimate(tax.TaxInput(wages=210_500, children=1))
    assert r.child_credit_used == pytest.approx(1_650)


def test_long_term_gains_stack_on_ordinary_income():
    # Single, wages 40,000 -> ordinary taxable 23,900; 30,000 of gains fill the
    # 0% band up to 49,450 (25,550) and the rest (4,450) is taxed at 15%.
    r = tax.estimate(tax.TaxInput(wages=40_000, long_term_gains=30_000))
    rates = {s.rate: s.amount for s in r.gains_brackets}
    assert rates[0.0] == pytest.approx(25_550)
    assert rates[0.15] == pytest.approx(4_450)


def test_self_employment_tax():
    # 50,000 profit -> 46,175 SE earnings x 15.3% = 7,064.775; half is deducted.
    r = tax.estimate(tax.TaxInput(self_employment=50_000))
    assert r.self_employment_tax == pytest.approx(7_064.775)
    assert r.agi == pytest.approx(50_000 - 7_064.775 / 2)


def test_self_employment_social_security_capped_by_wages():
    # Wages already over the wage base: only the 2.9% Medicare part applies.
    r = tax.estimate(tax.TaxInput(wages=190_000, self_employment=10_000))
    assert r.self_employment_tax == pytest.approx(10_000 * 0.9235 * 0.029)


def test_high_income_surtaxes():
    r = tax.estimate(tax.TaxInput(wages=300_000, investment_income=20_000))
    assert r.additional_medicare_tax == pytest.approx(0.009 * 100_000)
    assert r.net_investment_income_tax == pytest.approx(0.038 * 20_000)


def test_itemized_used_only_when_larger():
    assert tax.estimate(tax.TaxInput(wages=90_000, itemized=10_000)).deduction_kind == "standard"
    r = tax.estimate(tax.TaxInput(wages=90_000, itemized=25_000))
    assert r.deduction_kind == "itemized" and r.deduction == 25_000


def test_top_bracket():
    slices = tax.bracket_tax(1_000_000, 2026, "single")
    assert slices[-1].rate == 0.37
    assert slices[-1].amount == pytest.approx(1_000_000 - 640_600)


def test_validation():
    with pytest.raises(ValueError):
        tax.estimate(tax.TaxInput(year=2019))
    with pytest.raises(ValueError):
        tax.estimate(tax.TaxInput(status="married"))
    with pytest.raises(ValueError):
        tax.estimate(tax.TaxInput(wages=-1))


def test_tax_command(capsys):
    assert main(["tax", "--wages", "75000", "--withholding", "7000"]) == 0
    out = capsys.readouterr().out
    assert "AMOUNT YOU OWE" in out and "670.00" in out
    assert "Takeaway: your total federal tax is about 7,670.00" in out
    assert main(["tax", "--wages", "-5"]) == 1
