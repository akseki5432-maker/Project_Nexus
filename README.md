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
```

Use the `--cash-flows=...` form when the first value is negative.

## Tests

```bash
pytest
```
