"""US federal income tax estimator for tax years 2025 and 2026.

Works out roughly what a household owes the IRS (or gets back) when it files:
income tax from the brackets, the lower rates on long-term gains, the child
tax credit, self-employment tax, the Additional Medicare Tax and the Net
Investment Income Tax, minus what was already paid through withholding and
estimated payments.

Figures follow IRS Rev. Proc. 2024-40 and 2025-32 as changed by the 2025
tax law (P.L. 119-21). It's an estimate for planning: it leaves out state
tax, AMT, most credits other than the child tax credit, and special cases.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

INF = float("inf")

STATUSES = ("single", "married-joint", "married-separate", "head-of-household")
STATUS_NAMES = {
    "single": "Single",
    "married-joint": "Married filing jointly",
    "married-separate": "Married filing separately",
    "head-of-household": "Head of household",
}
RATES = (0.10, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37)


@dataclass(frozen=True)
class YearRules:
    standard_deduction: Dict[str, float]
    # Top of each bracket for RATES[0..5]; the 37% bracket has no top.
    bracket_tops: Dict[str, Tuple[float, ...]]
    # Top of the 0% and 15% long-term capital gains brackets.
    gains_tops: Dict[str, Tuple[float, float]]
    child_credit: float
    child_credit_refundable: float
    social_security_wage_base: float


YEARS: Dict[int, YearRules] = {
    2025: YearRules(
        standard_deduction={"single": 15_750, "married-joint": 31_500,
                            "married-separate": 15_750, "head-of-household": 23_625},
        bracket_tops={
            "single": (11_925, 48_475, 103_350, 197_300, 250_525, 626_350),
            "married-joint": (23_850, 96_950, 206_700, 394_600, 501_050, 751_600),
            "married-separate": (11_925, 48_475, 103_350, 197_300, 250_525, 375_800),
            "head-of-household": (17_000, 64_850, 103_350, 197_300, 250_500, 626_350),
        },
        gains_tops={"single": (48_350, 533_400), "married-joint": (96_700, 600_050),
                    "married-separate": (48_350, 300_000),
                    "head-of-household": (64_750, 566_700)},
        child_credit=2_200,
        child_credit_refundable=1_700,
        social_security_wage_base=176_100,
    ),
    2026: YearRules(
        standard_deduction={"single": 16_100, "married-joint": 32_200,
                            "married-separate": 16_100, "head-of-household": 24_150},
        bracket_tops={
            "single": (12_400, 50_400, 105_700, 201_775, 256_225, 640_600),
            "married-joint": (24_800, 100_800, 211_400, 403_550, 512_450, 768_700),
            "married-separate": (12_400, 50_400, 105_700, 201_775, 256_225, 384_350),
            "head-of-household": (17_700, 67_450, 105_700, 201_750, 256_200, 640_600),
        },
        gains_tops={"single": (49_450, 545_500), "married-joint": (98_900, 613_700),
                    "married-separate": (49_450, 306_850),
                    "head-of-household": (66_200, 579_600)},
        child_credit=2_200,
        child_credit_refundable=1_700,
        social_security_wage_base=184_500,
    ),
}

# Not adjusted for inflation by law.
CHILD_CREDIT_PHASEOUT = {"single": 200_000, "married-joint": 400_000,
                         "married-separate": 200_000, "head-of-household": 200_000}
SURTAX_THRESHOLD = {"single": 200_000, "married-joint": 250_000,
                    "married-separate": 125_000, "head-of-household": 200_000}


@dataclass
class TaxInput:
    """One year of a household's numbers. Money amounts are yearly dollars."""

    year: int = 2026
    status: str = "single"
    wages: float = 0.0                 # W-2 box 1 pay
    self_employment: float = 0.0       # net profit from your own business
    investment_income: float = 0.0     # interest, ordinary dividends, short-term gains
    long_term_gains: float = 0.0       # long-term gains + qualified dividends
    other_income: float = 0.0          # anything else taxable (e.g. unemployment)
    adjustments: float = 0.0           # e.g. IRA, HSA, student loan interest
    itemized: float = 0.0              # used only if bigger than the standard deduction
    children: int = 0                  # under 17, with Social Security numbers
    withholding: float = 0.0           # federal income tax already taken from pay
    estimated_payments: float = 0.0    # quarterly payments already sent

    def validate(self) -> None:
        if self.year not in YEARS:
            raise ValueError(f"tax year must be one of {sorted(YEARS)}")
        if self.status not in STATUSES:
            raise ValueError(f"filing status must be one of {', '.join(STATUSES)}")
        for name in ("wages", "investment_income", "long_term_gains", "other_income",
                     "adjustments", "itemized", "withholding", "estimated_payments"):
            if getattr(self, name) < 0:
                raise ValueError(f"{name.replace('_', ' ')} can't be negative")
        if self.children < 0:
            raise ValueError("number of children can't be negative")


@dataclass
class BracketSlice:
    rate: float
    amount: float      # income taxed at this rate
    tax: float


@dataclass
class TaxResult:
    total_income: float
    adjustments: float                 # includes half of self-employment tax
    agi: float
    deduction: float
    deduction_kind: str                # "standard" or "itemized"
    taxable_income: float
    ordinary_brackets: List[BracketSlice]
    gains_brackets: List[BracketSlice]
    income_tax_before_credits: float
    child_credit_used: float
    income_tax: float
    self_employment_tax: float
    additional_medicare_tax: float
    net_investment_income_tax: float
    total_tax: float
    refundable_credits: float
    payments: float
    balance_due: float                 # positive = you owe; negative = refund
    marginal_rate: float
    effective_rate: float              # total tax / total income
    payroll_taxes_withheld: float = 0.0  # employee Social Security + Medicare (already paid)
    notes: List[str] = field(default_factory=list)

    @property
    def refund(self) -> float:
        return max(0.0, -self.balance_due)

    @property
    def owed(self) -> float:
        return max(0.0, self.balance_due)


def _overlap(lo: float, hi: float, band_lo: float, band_hi: float) -> float:
    return max(0.0, min(hi, band_hi) - max(lo, band_lo))


def bracket_tax(taxable: float, year: int = 2026, status: str = "single") -> List[BracketSlice]:
    """Split ordinary taxable income across the brackets."""
    tops = YEARS[year].bracket_tops[status] + (INF,)
    out, lo = [], 0.0
    for rate, top in zip(RATES, tops):
        amount = _overlap(0.0, max(taxable, 0.0), lo, top)
        if amount > 0:
            out.append(BracketSlice(rate, amount, amount * rate))
        lo = top
    return out


def _gains_tax(ordinary: float, gains: float, year: int, status: str) -> List[BracketSlice]:
    """Long-term gains sit on top of ordinary income and fill the 0/15/20% bands."""
    zero_top, fifteen_top = YEARS[year].gains_tops[status]
    lo, hi = ordinary, ordinary + gains
    out = []
    for rate, band_lo, band_hi in ((0.0, 0.0, zero_top), (0.15, zero_top, fifteen_top),
                                   (0.20, fifteen_top, INF)):
        amount = _overlap(lo, hi, band_lo, band_hi)
        if amount > 0:
            out.append(BracketSlice(rate, amount, amount * rate))
    return out


def marginal_rate(taxable: float, year: int = 2026, status: str = "single") -> float:
    """Rate on the next dollar of ordinary income."""
    for rate, top in zip(RATES, YEARS[year].bracket_tops[status] + (INF,)):
        if taxable < top:
            return rate
    return RATES[-1]


def estimate(inp: TaxInput) -> TaxResult:
    """Estimate federal tax owed (or refunded) for one year."""
    inp.validate()
    rules, status = YEARS[inp.year], inp.status
    notes: List[str] = []

    # Self-employment tax: Social Security (up to the wage base, shared with
    # W-2 wages) plus Medicare, on 92.35% of net profit.
    se_earnings = inp.self_employment * 0.9235 if inp.self_employment >= 400 else 0.0
    ss_room = max(0.0, rules.social_security_wage_base - inp.wages)
    se_tax = min(se_earnings, ss_room) * 0.124 + se_earnings * 0.029
    half_se = se_tax / 2

    total_income = (inp.wages + inp.self_employment + inp.investment_income
                    + inp.long_term_gains + inp.other_income)
    adjustments = inp.adjustments + half_se
    agi = max(0.0, total_income - adjustments)

    standard = rules.standard_deduction[status]
    if inp.itemized > standard:
        deduction, kind = inp.itemized, "itemized"
    else:
        deduction, kind = standard, "standard"
    taxable = max(0.0, agi - deduction)

    gains = min(inp.long_term_gains, taxable)
    ordinary = taxable - gains
    ordinary_slices = bracket_tax(ordinary, inp.year, status)
    gains_slices = _gains_tax(ordinary, gains, inp.year, status)
    tax_before = sum(s.tax for s in ordinary_slices) + sum(s.tax for s in gains_slices)

    # Child tax credit: shrinks by $50 per $1,000 (or part) of AGI over the limit.
    over = max(0.0, agi - CHILD_CREDIT_PHASEOUT[status])
    reduction = 50 * -(-over // 1000)
    child_credit = max(0.0, inp.children * rules.child_credit - reduction)
    credit_used = min(child_credit, tax_before)
    earned = inp.wages + max(0.0, inp.self_employment - half_se)
    refundable = min(child_credit - credit_used,
                     inp.children * rules.child_credit_refundable,
                     0.15 * max(0.0, earned - 2_500))
    income_tax = tax_before - credit_used

    threshold = SURTAX_THRESHOLD[status]
    addl_medicare = 0.009 * max(0.0, inp.wages + se_earnings - threshold)
    niit_base = inp.investment_income + inp.long_term_gains
    niit = 0.038 * min(niit_base, max(0.0, agi - threshold))

    total_tax = income_tax + se_tax + addl_medicare + niit
    payments = inp.withholding + inp.estimated_payments + refundable
    balance = total_tax - payments
    payroll = min(inp.wages, rules.social_security_wage_base) * 0.062 + inp.wages * 0.0145

    if balance > 1_000 and inp.self_employment > 0:
        notes.append("Owing more than $1,000 can mean an underpayment penalty; "
                     "self-employed people usually pay estimated tax each quarter.")
    if child_credit < inp.children * rules.child_credit:
        notes.append("Your income is high enough that the child tax credit is reduced.")
    if kind == "standard" and inp.itemized > 0:
        notes.append("Your itemized deductions are less than the standard deduction, "
                     "so the standard deduction is used.")

    return TaxResult(
        total_income=total_income,
        adjustments=adjustments,
        agi=agi,
        deduction=deduction,
        deduction_kind=kind,
        taxable_income=taxable,
        ordinary_brackets=ordinary_slices,
        gains_brackets=gains_slices,
        income_tax_before_credits=tax_before,
        child_credit_used=credit_used,
        income_tax=income_tax,
        self_employment_tax=se_tax,
        additional_medicare_tax=addl_medicare,
        net_investment_income_tax=niit,
        total_tax=total_tax,
        refundable_credits=refundable,
        payments=payments,
        balance_due=balance,
        marginal_rate=marginal_rate(ordinary, inp.year, status) if taxable > 0 else 0.0,
        effective_rate=total_tax / total_income if total_income > 0 else 0.0,
        payroll_taxes_withheld=payroll,
        notes=notes,
    )
