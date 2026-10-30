"""Financial statement analysis: ratios grouped by liquidity, leverage,
profitability and efficiency, plus a DuPont decomposition."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Dict


def _div(a: float, b: float) -> float:
    return a / b if b else float("nan")


@dataclass
class Financials:
    """Minimal set of income statement and balance sheet line items."""

    revenue: float
    cogs: float
    operating_income: float
    net_income: float
    interest_expense: float
    total_assets: float
    total_equity: float
    total_debt: float
    current_assets: float
    current_liabilities: float
    inventory: float = 0.0
    cash: float = 0.0
    receivables: float = 0.0

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "Financials":
        names = {f.name for f in fields(cls)}
        return cls(**{k: float(v) for k, v in data.items() if k in names})


def liquidity(f: Financials) -> Dict[str, float]:
    return {
        "current_ratio": _div(f.current_assets, f.current_liabilities),
        "quick_ratio": _div(f.current_assets - f.inventory, f.current_liabilities),
        "cash_ratio": _div(f.cash, f.current_liabilities),
    }


def leverage(f: Financials) -> Dict[str, float]:
    return {
        "debt_to_equity": _div(f.total_debt, f.total_equity),
        "debt_to_assets": _div(f.total_debt, f.total_assets),
        "equity_multiplier": _div(f.total_assets, f.total_equity),
        "interest_coverage": _div(f.operating_income, f.interest_expense),
    }


def profitability(f: Financials) -> Dict[str, float]:
    return {
        "gross_margin": _div(f.revenue - f.cogs, f.revenue),
        "operating_margin": _div(f.operating_income, f.revenue),
        "net_margin": _div(f.net_income, f.revenue),
        "roa": _div(f.net_income, f.total_assets),
        "roe": _div(f.net_income, f.total_equity),
    }


def efficiency(f: Financials) -> Dict[str, float]:
    return {
        "asset_turnover": _div(f.revenue, f.total_assets),
        "inventory_turnover": _div(f.cogs, f.inventory),
        "days_sales_outstanding": _div(f.receivables, f.revenue) * 365,
    }


def dupont(f: Financials) -> Dict[str, float]:
    """ROE = net margin x asset turnover x equity multiplier."""
    margin = _div(f.net_income, f.revenue)
    turnover = _div(f.revenue, f.total_assets)
    multiplier = _div(f.total_assets, f.total_equity)
    return {
        "net_margin": margin,
        "asset_turnover": turnover,
        "equity_multiplier": multiplier,
        "roe": margin * turnover * multiplier,
    }


def analyze(f: Financials) -> Dict[str, Dict[str, float]]:
    """All ratio groups in one report."""
    return {
        "liquidity": liquidity(f),
        "leverage": leverage(f),
        "profitability": profitability(f),
        "efficiency": efficiency(f),
        "dupont": dupont(f),
    }
