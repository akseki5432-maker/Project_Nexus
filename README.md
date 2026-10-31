# Project Nexus — Business Finance & Economics Toolkit

Nexus is a dependency-free Python library and command-line tool for everyday
business finance and applied economics: capital budgeting, loans, valuation,
financial statement analysis, unit economics and macro basics.

## Install

```bash
pip install -e ".[dev]"
```

## Modules

| Module | What it covers |
| --- | --- |
| `nexus.tvm` | Future/present value, annuities, loan payments, NPV, IRR, payback, profitability index, effective annual rate, amortization schedules |
| `nexus.valuation` | CAPM, WACC, free cash flow, Gordon growth, DCF valuation, bond pricing, Macaulay/modified duration |
| `nexus.ratios` | Liquidity, leverage, profitability and efficiency ratios, DuPont ROE decomposition |
| `nexus.forecast` | Driver-based pro forma forecast (revenue growth, margins, capex, working capital) producing free cash flows, with one-step valuation |
| `nexus.scenarios` | One-way and two-way sensitivity tables, tornado analysis, named scenarios, Monte Carlo simulation (normal, uniform, triangular inputs) |
| `nexus.export` | CSV export for schedules, forecasts and any list of records |
| `nexus.economics` | CAGR, inflation and real values, Fisher equation, price elasticity, supply/demand equilibrium and surplus, break-even, operating leverage, GDP identity, Keynesian multiplier |

Conventions: rates are decimals (`0.05` = 5%), and cash outflows are negative.

## Library usage

```python
from nexus import tvm, valuation, economics

tvm.npv(0.08, [-500_000, 120_000, 150_000, 170_000, 180_000, 160_000])
tvm.irr([-1000, 300, 400, 500])                       # 0.0890
valuation.dcf([900e3, 980e3, 1.05e6], 0.078, 0.025, net_debt=4e6, shares_outstanding=1e6)
economics.break_even(fixed_costs=200_000, price=50, variable_cost=30).units  # 10000
```

See `examples/project_appraisal.py` for an end-to-end project appraisal.

### Risk and scenario analysis

Any function that takes keyword inputs and returns a number can be stress-tested:

```python
from nexus import scenarios

def profit(price, volume, unit_cost, fixed_cost):
    return (price - unit_cost) * volume - fixed_cost

base = {"price": 10, "volume": 1000, "unit_cost": 6, "fixed_cost": 2000}

scenarios.run_scenarios(profit, base, {"bear": {"volume": 600}, "bull": {"volume": 1400}})
scenarios.tornado(profit, base, {"price": (9, 11), "volume": (500, 1500)})
sim = scenarios.monte_carlo(profit, {
    "price": scenarios.triangular(8, 10, 12),
    "volume": scenarios.normal(1000, 150),
    "unit_cost": scenarios.fixed(6),
    "fixed_cost": scenarios.fixed(2000),
}, trials=10_000, seed=1)
sim.summary()   # mean, stdev, p5, p50, p95, prob_negative
```

### Forecasting

Put the operating assumptions in a JSON file (see `examples/acme_assumptions.json`):
base revenue, a growth rate per year, EBIT margin, tax rate, and depreciation,
capex and net working capital as a share of revenue. `forecast.project()`
turns them into a year-by-year free cash flow forecast, and `forecast.value()`
runs the DCF on it.

## CLI

```bash
nexus npv --rate 0.08 --cash-flows=-500000,120000,150000,170000,180000,160000
nexus loan --principal 250000 --rate 0.065 --years 30 --schedule
nexus wacc --risk-free 0.04 --beta 1.2 --market-return 0.09 --equity 6e6 --debt 4e6 --cost-of-debt 0.06 --tax 0.25
nexus dcf --cash-flows 900000,980000,1050000 --rate 0.078 --growth 0.025 --net-debt 4e6 --shares 1e6
nexus ratios examples/acme_financials.json
nexus breakeven --fixed 200000 --price 50 --variable 30 --target 50000
nexus elasticity --q1 100 --q2 80 --p1 10 --p2 12
nexus inflation --cpi-old 300 --cpi-new 309 --nominal-rate 0.05 --amount 1000

# Forecast free cash flows, value the firm and export to CSV
nexus forecast examples/acme_assumptions.json --rate 0.09 --growth 0.025 --net-debt 4e6 --shares 1e6 --csv forecast.csv
# Value per share across discount rates (rows) and terminal growth rates (columns)
nexus sensitivity examples/acme_assumptions.json --rates 0.07,0.08,0.09,0.10,0.11 --growths 0.01,0.02,0.03 --net-debt 4e6 --shares 1e6
# Probability distribution of a project's NPV
nexus montecarlo --investment 500000 --cash-flow 150000 --cash-flow-sd 40000 --years 5 --rate-low 0.06 --rate-high 0.12 --seed 42
# Export a loan schedule
nexus loan --principal 250000 --rate 0.065 --years 30 --csv loan.csv
```

Use the `--cash-flows=...` form when the first value is negative.

## Tests

```bash
pytest
```

GitHub Actions runs the test suite on Python 3.9, 3.11 and 3.13 for every push and pull request.
