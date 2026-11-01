"""Time value of money: present/future value, annuities, NPV, IRR and loans.

Rates are per-period decimals (0.05 == 5%). Cash outflows are negative.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence


def future_value(pv: float, rate: float, periods: int) -> float:
    """Future value of a single lump sum."""
    return pv * (1 + rate) ** periods


def present_value(fv: float, rate: float, periods: int) -> float:
    """Present value of a single future amount."""
    return fv / (1 + rate) ** periods


def annuity_pv(payment: float, rate: float, periods: int, due: bool = False) -> float:
    """Present value of a level annuity (ordinary by default, or annuity due)."""
    if rate == 0:
        value = payment * periods
    else:
        value = payment * (1 - (1 + rate) ** -periods) / rate
    return value * (1 + rate) if due else value


def annuity_fv(payment: float, rate: float, periods: int, due: bool = False) -> float:
    """Future value of a level annuity."""
    if rate == 0:
        value = payment * periods
    else:
        value = payment * ((1 + rate) ** periods - 1) / rate
    return value * (1 + rate) if due else value


def payment(principal: float, rate: float, periods: int) -> float:
    """Level payment that amortizes ``principal`` over ``periods``."""
    if periods <= 0:
        raise ValueError("periods must be positive")
    if rate == 0:
        return principal / periods
    return principal * rate / (1 - (1 + rate) ** -periods)


def npv(rate: float, cash_flows: Sequence[float]) -> float:
    """Net present value; ``cash_flows[0]`` occurs today (t=0)."""
    return sum(cf / (1 + rate) ** t for t, cf in enumerate(cash_flows))


def irr(cash_flows: Sequence[float], low: float = -0.9999, high: float = 10.0,
        tol: float = 1e-10, max_iter: int = 500) -> float:
    """Internal rate of return via bisection.

    Raises ``ValueError`` if NPV does not change sign over ``[low, high]``.
    """
    f_low, f_high = npv(low, cash_flows), npv(high, cash_flows)
    if f_low * f_high > 0:
        raise ValueError("IRR not bracketed; cash flows may lack a sign change")
    for _ in range(max_iter):
        mid = (low + high) / 2
        f_mid = npv(mid, cash_flows)
        if abs(f_mid) < tol or (high - low) / 2 < tol:
            return mid
        if f_low * f_mid < 0:
            high, f_high = mid, f_mid
        else:
            low, f_low = mid, f_mid
    return (low + high) / 2


def payback_period(cash_flows: Sequence[float]) -> float:
    """Years until cumulative cash flow turns non-negative (interpolated).

    Returns ``float('inf')`` if the investment never pays back.
    """
    cumulative = 0.0
    for t, cf in enumerate(cash_flows):
        previous = cumulative
        cumulative += cf
        if cumulative >= 0 and t > 0:
            return (t - 1) + (-previous / cf if cf else 0.0)
    return float("inf")


def profitability_index(rate: float, cash_flows: Sequence[float]) -> float:
    """PV of future cash flows divided by the initial investment."""
    initial = -cash_flows[0]
    if initial <= 0:
        raise ValueError("first cash flow must be an outflow (negative)")
    return npv(rate, [0.0, *cash_flows[1:]]) / initial


def effective_annual_rate(nominal: float, compounding: int) -> float:
    """Convert a nominal annual rate compounded ``compounding`` times to an EAR."""
    return (1 + nominal / compounding) ** compounding - 1


@dataclass(frozen=True)
class AmortizationRow:
    period: int
    payment: float
    interest: float
    principal: float
    balance: float


def amortization_schedule(principal: float, annual_rate: float, years: int,
                          payments_per_year: int = 12) -> List[AmortizationRow]:
    """Full loan amortization schedule."""
    rate = annual_rate / payments_per_year
    n = years * payments_per_year
    pmt = payment(principal, rate, n)
    balance = principal
    rows = []
    for period in range(1, n + 1):
        interest = balance * rate
        principal_paid = pmt - interest
        balance -= principal_paid
        if period == n:
            balance = 0.0 if abs(balance) < 1e-6 else balance
        rows.append(AmortizationRow(period, pmt, interest, principal_paid, balance))
    return rows
