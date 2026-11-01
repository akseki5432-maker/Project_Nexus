"""Driver-based pro forma forecast that produces free cash flows for a DCF.

Revenue grows by a per-year rate; costs, capex and working capital are
expressed as percentages of revenue.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Sequence

from . import valuation


@dataclass
class Assumptions:
    base_revenue: float
    growth: Sequence[float]            # one rate per forecast year
    ebit_margin: float
    tax_rate: float
    depreciation_pct: float = 0.03     # of revenue
    capex_pct: float = 0.04            # of revenue
    nwc_pct: float = 0.10              # net working capital as % of revenue

    @classmethod
    def from_dict(cls, data: Dict) -> "Assumptions":
        return cls(**data)


@dataclass(frozen=True)
class ForecastYear:
    year: int
    revenue: float
    ebit: float
    nopat: float
    depreciation: float
    capex: float
    change_in_nwc: float
    fcf: float


@dataclass
class Forecast:
    years: List[ForecastYear] = field(default_factory=list)

    @property
    def free_cash_flows(self) -> List[float]:
        return [y.fcf for y in self.years]

    def rows(self) -> List[Dict[str, float]]:
        return [asdict(y) for y in self.years]


def project(a: Assumptions) -> Forecast:
    """Build the year-by-year forecast."""
    revenue = a.base_revenue
    nwc = revenue * a.nwc_pct
    out = Forecast()
    for year, g in enumerate(a.growth, 1):
        revenue *= 1 + g
        ebit = revenue * a.ebit_margin
        dep = revenue * a.depreciation_pct
        capex = revenue * a.capex_pct
        new_nwc = revenue * a.nwc_pct
        d_nwc = new_nwc - nwc
        nwc = new_nwc
        fcf = valuation.free_cash_flow(ebit, a.tax_rate, dep, capex, d_nwc)
        out.years.append(ForecastYear(year, revenue, ebit, ebit * (1 - a.tax_rate),
                                      dep, capex, d_nwc, fcf))
    return out


def value(a: Assumptions, discount_rate: float, terminal_growth: float,
          net_debt: float = 0.0, shares_outstanding: float | None = None
          ) -> valuation.DCFResult:
    """Forecast and value the business in one step."""
    return valuation.dcf(project(a).free_cash_flows, discount_rate, terminal_growth,
                         net_debt, shares_outstanding)
