"""Corporate valuation: cost of capital, DCF and dividend models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence


def capm(risk_free: float, beta: float, market_return: float) -> float:
    """Cost of equity under the Capital Asset Pricing Model."""
    return risk_free + beta * (market_return - risk_free)


def wacc(equity_value: float, debt_value: float, cost_of_equity: float,
         cost_of_debt: float, tax_rate: float) -> float:
    """Weighted average cost of capital."""
    total = equity_value + debt_value
    if total <= 0:
        raise ValueError("total capital must be positive")
    return (equity_value / total) * cost_of_equity + \
        (debt_value / total) * cost_of_debt * (1 - tax_rate)


def gordon_growth(next_cash_flow: float, discount_rate: float, growth: float) -> float:
    """Value of a perpetuity growing at ``growth`` (Gordon growth model)."""
    if discount_rate <= growth:
        raise ValueError("discount rate must exceed growth rate")
    return next_cash_flow / (discount_rate - growth)


def free_cash_flow(ebit: float, tax_rate: float, depreciation: float,
                   capex: float, change_in_nwc: float) -> float:
    """Unlevered free cash flow to the firm."""
    return ebit * (1 - tax_rate) + depreciation - capex - change_in_nwc


@dataclass(frozen=True)
class DCFResult:
    enterprise_value: float
    pv_forecast: float
    pv_terminal: float
    terminal_value: float
    equity_value: float
    per_share: float | None
    discounted_flows: List[float]


def dcf(cash_flows: Sequence[float], discount_rate: float, terminal_growth: float,
        net_debt: float = 0.0, shares_outstanding: float | None = None) -> DCFResult:
    """Discounted cash flow valuation with a Gordon-growth terminal value.

    ``cash_flows`` are forecast free cash flows for years 1..N.
    """
    if not cash_flows:
        raise ValueError("need at least one forecast cash flow")
    discounted = [cf / (1 + discount_rate) ** t for t, cf in enumerate(cash_flows, 1)]
    pv_forecast = sum(discounted)
    terminal = gordon_growth(cash_flows[-1] * (1 + terminal_growth), discount_rate,
                             terminal_growth)
    pv_terminal = terminal / (1 + discount_rate) ** len(cash_flows)
    ev = pv_forecast + pv_terminal
    equity = ev - net_debt
    per_share = equity / shares_outstanding if shares_outstanding else None
    return DCFResult(ev, pv_forecast, pv_terminal, terminal, equity, per_share, discounted)


def bond_price(face: float, coupon_rate: float, ytm: float, years: int,
               frequency: int = 2) -> float:
    """Price of a fixed-coupon bond."""
    n = years * frequency
    coupon = face * coupon_rate / frequency
    y = ytm / frequency
    if y == 0:
        return coupon * n + face
    return coupon * (1 - (1 + y) ** -n) / y + face / (1 + y) ** n


def bond_duration(face: float, coupon_rate: float, ytm: float, years: int,
                  frequency: int = 2) -> tuple[float, float]:
    """Return (Macaulay duration, modified duration) in years."""
    n = years * frequency
    coupon = face * coupon_rate / frequency
    y = ytm / frequency
    price = bond_price(face, coupon_rate, ytm, years, frequency)
    weighted = sum(
        t * (coupon + (face if t == n else 0)) / (1 + y) ** t for t in range(1, n + 1)
    )
    macaulay = weighted / price / frequency
    return macaulay, macaulay / (1 + y)
