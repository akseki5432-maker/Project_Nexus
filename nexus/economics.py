"""Applied economics: growth, inflation, elasticity, market equilibrium,
break-even analysis and macro identities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


def cagr(begin: float, end: float, years: float) -> float:
    """Compound annual growth rate."""
    if begin <= 0 or years <= 0:
        raise ValueError("begin value and years must be positive")
    return (end / begin) ** (1 / years) - 1


def growth_rates(series: Sequence[float]) -> list[float]:
    """Period-over-period growth rates."""
    return [(b - a) / a for a, b in zip(series, series[1:])]


def inflation_rate(cpi_old: float, cpi_new: float) -> float:
    return cpi_new / cpi_old - 1


def to_real(nominal_value: float, cpi_then: float, cpi_base: float) -> float:
    """Express a nominal amount in base-period prices."""
    return nominal_value * cpi_base / cpi_then


def fisher_real_rate(nominal_rate: float, inflation: float) -> float:
    """Exact Fisher equation: (1 + i) = (1 + r)(1 + pi)."""
    return (1 + nominal_rate) / (1 + inflation) - 1


def rule_of_70(growth_rate_pct: float) -> float:
    """Approximate years to double at ``growth_rate_pct`` percent."""
    return 70 / growth_rate_pct


def arc_elasticity(q1: float, q2: float, p1: float, p2: float) -> float:
    """Midpoint (arc) price elasticity of demand."""
    dq = (q2 - q1) / ((q1 + q2) / 2)
    dp = (p2 - p1) / ((p1 + p2) / 2)
    if dp == 0:
        raise ValueError("price must change to compute elasticity")
    return dq / dp


def classify_elasticity(e: float) -> str:
    m = abs(e)
    if m > 1:
        return "elastic"
    if m < 1:
        return "inelastic"
    return "unit elastic"


@dataclass(frozen=True)
class Equilibrium:
    price: float
    quantity: float
    consumer_surplus: float
    producer_surplus: float


def linear_equilibrium(demand_intercept: float, demand_slope: float,
                       supply_intercept: float, supply_slope: float) -> Equilibrium:
    """Equilibrium for Qd = a - b*P and Qs = c + d*P (slopes given as positive b, d)."""
    a, b, c, d = demand_intercept, demand_slope, supply_intercept, supply_slope
    if b + d == 0:
        raise ValueError("curves are parallel")
    price = (a - c) / (b + d)
    quantity = a - b * price
    choke_price = a / b                      # price where Qd = 0
    min_supply_price = max(-c / d, 0.0)      # price where Qs = 0
    cs = 0.5 * quantity * (choke_price - price)
    ps = 0.5 * (quantity + max(c, 0.0)) * (price - min_supply_price)
    return Equilibrium(price, quantity, cs, ps)


@dataclass(frozen=True)
class BreakEven:
    units: float
    revenue: float
    contribution_margin: float
    contribution_margin_ratio: float


def break_even(fixed_costs: float, price: float, variable_cost: float,
               target_profit: float = 0.0) -> BreakEven:
    """Units and revenue needed to cover fixed costs (plus a target profit)."""
    cm = price - variable_cost
    if cm <= 0:
        raise ValueError("price must exceed variable cost per unit")
    units = (fixed_costs + target_profit) / cm
    return BreakEven(units, units * price, cm, cm / price)


def operating_leverage(quantity: float, price: float, variable_cost: float,
                       fixed_costs: float) -> float:
    """Degree of operating leverage: % change in EBIT per % change in sales."""
    contribution = quantity * (price - variable_cost)
    ebit = contribution - fixed_costs
    if ebit == 0:
        raise ValueError("EBIT is zero at this volume (break-even)")
    return contribution / ebit


def gdp_expenditure(consumption: float, investment: float, government: float,
                    exports: float, imports: float) -> float:
    """GDP = C + I + G + (X - M)."""
    return consumption + investment + government + exports - imports


def keynesian_multiplier(mpc: float, tax_rate: float = 0.0,
                         mpi: float = 0.0) -> float:
    """Spending multiplier 1 / (1 - MPC(1 - t) + MPI)."""
    denom = 1 - mpc * (1 - tax_rate) + mpi
    if denom <= 0:
        raise ValueError("multiplier undefined for these parameters")
    return 1 / denom
