"""Worked example: appraise an expansion project and value the firm.

Run with:  python examples/project_appraisal.py
"""

from nexus import economics, tvm, valuation

# 1. Cost of capital
ke = valuation.capm(risk_free=0.04, beta=1.2, market_return=0.09)
rate = valuation.wacc(equity_value=6e6, debt_value=4e6, cost_of_equity=ke,
                      cost_of_debt=0.06, tax_rate=0.25)
print(f"Cost of equity {ke:.2%}, WACC {rate:.2%}")

# 2. Capital budgeting for a new production line
flows = [-500_000, 120_000, 150_000, 170_000, 180_000, 160_000]
print(f"NPV {tvm.npv(rate, flows):,.0f} | IRR {tvm.irr(flows):.2%} | "
      f"PI {tvm.profitability_index(rate, flows):.2f} | "
      f"payback {tvm.payback_period(flows):.2f} yrs")

# 3. Unit economics of the product it makes
be = economics.break_even(fixed_costs=200_000, price=50, variable_cost=30)
print(f"Break-even at {be.units:,.0f} units ({be.revenue:,.0f} revenue)")

# 4. Firm valuation
res = valuation.dcf([900_000, 980_000, 1_050_000, 1_110_000, 1_160_000],
                    discount_rate=rate, terminal_growth=0.025,
                    net_debt=4e6, shares_outstanding=1e6)
print(f"Enterprise value {res.enterprise_value:,.0f}, "
      f"equity/share {res.per_share:,.2f}")

# 5. Real returns
real = economics.fisher_real_rate(nominal_rate=0.07, inflation=0.03)
print(f"A 7% nominal return with 3% inflation is {real:.2%} real")
