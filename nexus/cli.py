"""Command-line interface: ``nexus <command> [options]``."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from . import economics, export, forecast, glossary, ratios, scenarios, tax, tvm, valuation


def _floats(text: str) -> List[float]:
    return [float(x) for x in text.split(",") if x.strip()]


def _pct(x: float) -> str:
    return f"{x * 100:.2f}%"


def _money(x: float) -> str:
    return f"{x:,.2f}"


def _takeaway(text: str) -> None:
    """Print a one-line, plain-English reading of the result."""
    print(f"\nTakeaway: {text}")


def cmd_npv(a: argparse.Namespace) -> None:
    flows = _floats(a.cash_flows)
    print(f"NPV @ {_pct(a.rate)}: {_money(tvm.npv(a.rate, flows))}")
    try:
        print(f"IRR:            {_pct(tvm.irr(flows))}")
    except ValueError as exc:
        print(f"IRR:            n/a ({exc})")
    print(f"Payback:        {tvm.payback_period(flows):.2f} periods")
    value = tvm.npv(a.rate, flows)
    if value >= 0:
        _takeaway(f"the project earns more than your {_pct(a.rate)} required return, "
                  f"adding {_money(value)} of value in today's money. Worth considering.")
    else:
        _takeaway(f"the project falls short of your {_pct(a.rate)} required return by "
                  f"{_money(-value)} in today's money. Probably not worth it.")


def cmd_loan(a: argparse.Namespace) -> None:
    rows = tvm.amortization_schedule(a.principal, a.rate, a.years, a.per_year)
    total_interest = sum(r.interest for r in rows)
    print(f"Payment:        {_money(rows[0].payment)} x {len(rows)}")
    print(f"Total interest: {_money(total_interest)}")
    _takeaway(f"you'll pay back {_money(a.principal + total_interest)} in total; "
              f"{_money(total_interest)} of that is the cost of borrowing.")
    if a.csv:
        with open(a.csv, "w", newline="") as fh:
            export.write_csv(rows, fh)
        print(f"Schedule written to {a.csv}")
    if a.schedule:
        print(f"{'#':>4} {'payment':>12} {'interest':>12} {'principal':>12} {'balance':>14}")
        for r in rows:
            print(f"{r.period:>4} {r.payment:>12,.2f} {r.interest:>12,.2f} "
                  f"{r.principal:>12,.2f} {r.balance:>14,.2f}")


def cmd_dcf(a: argparse.Namespace) -> None:
    res = valuation.dcf(_floats(a.cash_flows), a.rate, a.growth, a.net_debt, a.shares)
    print(f"PV of forecast:   {_money(res.pv_forecast)}")
    print(f"PV of terminal:   {_money(res.pv_terminal)}")
    print(f"Enterprise value: {_money(res.enterprise_value)}")
    print(f"Equity value:     {_money(res.equity_value)}")
    if res.per_share is not None:
        print(f"Value per share:  {_money(res.per_share)}")
    _takeaway(_value_sentence(res))


def _value_sentence(res: valuation.DCFResult) -> str:
    worth = (f"one share is worth about {_money(res.per_share)}" if res.per_share is not None
             else f"the owners' stake is worth about {_money(res.equity_value)}")
    share = res.pv_terminal / res.enterprise_value if res.enterprise_value else 0.0
    return (f"based on these guesses, {worth}. {_pct(share)} of the value comes from "
            "years after the forecast, so check that the long-run growth guess is realistic.")


def cmd_wacc(a: argparse.Namespace) -> None:
    ke = valuation.capm(a.risk_free, a.beta, a.market_return)
    w = valuation.wacc(a.equity, a.debt, ke, a.cost_of_debt, a.tax)
    print(f"Cost of equity (CAPM): {_pct(ke)}")
    print(f"WACC:                  {_pct(w)}")
    _takeaway(f"new projects should earn at least {_pct(w)} a year to be worth funding.")


def cmd_ratios(a: argparse.Namespace) -> None:
    with open(a.file) as fh:
        f = ratios.Financials.from_dict(json.load(fh))
    for group, values in ratios.analyze(f).items():
        print(group.upper())
        for name, value in values.items():
            print(f"  {name:<24}{value:>10.3f}")
    _takeaway("run `nexus explain ratios` or `nexus explain roe` for what these mean.")


def cmd_breakeven(a: argparse.Namespace) -> None:
    be = economics.break_even(a.fixed, a.price, a.variable, a.target)
    print(f"Contribution margin: {_money(be.contribution_margin)} "
          f"({_pct(be.contribution_margin_ratio)})")
    print(f"Break-even units:    {be.units:,.1f}")
    print(f"Break-even revenue:  {_money(be.revenue)}")
    goal = "reach your profit target" if a.target else "stop losing money"
    _takeaway(f"each sale leaves {_money(be.contribution_margin)} toward fixed costs, "
              f"so you need to sell about {be.units:,.0f} units to {goal}.")


def cmd_elasticity(a: argparse.Namespace) -> None:
    e = economics.arc_elasticity(a.q1, a.q2, a.p1, a.p2)
    print(f"Arc elasticity: {e:.3f} ({economics.classify_elasticity(e)})")
    reaction = "react strongly to" if abs(e) > 1 else "barely react to" if abs(e) < 1 else "react evenly to"
    direction = "cuts" if e < 0 else "raises"
    _takeaway(f"buyers {reaction} price: a 1% price rise {direction} the amount bought "
              f"by about {abs(e):.1f}%.")


def cmd_inflation(a: argparse.Namespace) -> None:
    pi = economics.inflation_rate(a.cpi_old, a.cpi_new)
    print(f"Inflation:  {_pct(pi)}")
    if a.nominal_rate is not None:
        print(f"Real rate:  {_pct(economics.fisher_real_rate(a.nominal_rate, pi))}")
    if a.amount is not None:
        real = economics.to_real(a.amount, a.cpi_new, a.cpi_old)
        print(f"{_money(a.amount)} today = {_money(real)} in base-period prices")
    _takeaway(f"prices rose {_pct(pi)}, so each dollar buys about {_pct(1 - 1 / (1 + pi))} less.")


def _load_assumptions(path: str) -> forecast.Assumptions:
    with open(path) as fh:
        return forecast.Assumptions.from_dict(json.load(fh))


def cmd_forecast(a: argparse.Namespace) -> None:
    assumptions = _load_assumptions(a.file)
    fc = forecast.project(assumptions)
    print(f"{'year':>4} {'revenue':>14} {'ebit':>12} {'capex':>12} {'d_nwc':>10} {'fcf':>12}")
    for y in fc.years:
        print(f"{y.year:>4} {y.revenue:>14,.0f} {y.ebit:>12,.0f} {y.capex:>12,.0f} "
              f"{y.change_in_nwc:>10,.0f} {y.fcf:>12,.0f}")
    if a.csv:
        with open(a.csv, "w", newline="") as fh:
            export.write_csv(fc.years, fh)
        print(f"Forecast written to {a.csv}")
    if a.rate is not None:
        res = valuation.dcf(fc.free_cash_flows, a.rate, a.growth, a.net_debt, a.shares)
        print(f"\nEnterprise value: {_money(res.enterprise_value)}")
        print(f"Equity value:     {_money(res.equity_value)}")
        if res.per_share is not None:
            print(f"Value per share:  {_money(res.per_share)}")
        print(f"Terminal share of EV: {_pct(res.pv_terminal / res.enterprise_value)}")
        _takeaway(_value_sentence(res))


def cmd_sensitivity(a: argparse.Namespace) -> None:
    assumptions = _load_assumptions(a.file)
    flows = forecast.project(assumptions).free_cash_flows

    def model(rate: float, growth: float) -> float:
        res = valuation.dcf(flows, rate, growth, a.net_debt, a.shares)
        return res.per_share if res.per_share is not None else res.equity_value

    rates, growths = _floats(a.rates), _floats(a.growths)
    grid = scenarios.two_way(model, {}, "rate", rates, "growth", growths)
    label = "value/share" if a.shares else "equity value"
    print(f"{label}: rows = discount rate, columns = terminal growth")
    print(f"{'':>8}" + "".join(f"{g:>14.2%}" for g in growths))
    for r, row in zip(rates, grid):
        print(f"{r:>8.2%}" + "".join(f"{v:>14,.2f}" for v in row))
    flat = [v for row in grid for v in row]
    _takeaway(f"small changes in these two guesses move the answer from {_money(min(flat))} "
              f"to {_money(max(flat))}. Treat any single value as a rough estimate.")


def cmd_montecarlo(a: argparse.Namespace) -> None:
    def model(cash_flow: float, rate: float) -> float:
        return tvm.npv(rate, [-a.investment] + [cash_flow] * a.years)

    samplers = {
        "cash_flow": scenarios.normal(a.cash_flow, a.cash_flow_sd),
        "rate": scenarios.uniform(a.rate_low, a.rate_high),
    }
    result = scenarios.monte_carlo(model, samplers, a.trials, a.seed)
    s = result.summary()
    print(f"Simulated NPV over {a.trials:,} trials")
    print(f"  mean      {_money(s['mean'])}")
    print(f"  stdev     {_money(s['stdev'])}")
    print(f"  5th pct   {_money(s['p5'])}")
    print(f"  median    {_money(s['p50'])}")
    print(f"  95th pct  {_money(s['p95'])}")
    print(f"  P(NPV<0)  {_pct(s['prob_negative'])}")
    _takeaway(f"in about {s['prob_negative'] * 10:.0f} out of 10 simulated futures this project "
              f"loses money; on average it adds {_money(s['mean'])}.")


def cmd_tax(a: argparse.Namespace) -> None:
    inp = tax.TaxInput(
        year=a.year, status=a.status, wages=a.wages, self_employment=a.self_employment,
        investment_income=a.investment_income, long_term_gains=a.long_term_gains,
        other_income=a.other_income, adjustments=a.adjustments, itemized=a.itemized,
        children=a.children, withholding=a.withholding, estimated_payments=a.estimated,
    )
    r = tax.estimate(inp)
    print(f"{a.year} federal tax estimate ({tax.STATUS_NAMES[a.status]})")
    rows = [
        ("Total income", r.total_income),
        ("- Adjustments", r.adjustments),
        ("Adjusted gross income", r.agi),
        (f"- {r.deduction_kind.capitalize()} deduction", r.deduction),
        ("Taxable income", r.taxable_income),
    ]
    for label, value in rows:
        print(f"  {label:<38}{value:>14,.2f}")
    print("  Tax by bracket:")
    for s in r.ordinary_brackets:
        print(f"    {s.rate:>4.0%} on {s.amount:>12,.2f}  = {s.tax:>12,.2f}")
    for s in r.gains_brackets:
        print(f"    {s.rate:>4.0%} on {s.amount:>12,.2f}  = {s.tax:>12,.2f}  (long-term gains)")
    rows = [
        ("Income tax before credits", r.income_tax_before_credits),
        ("- Child tax credit", r.child_credit_used),
        ("Income tax", r.income_tax),
        ("+ Self-employment tax", r.self_employment_tax),
        ("+ Additional Medicare tax", r.additional_medicare_tax),
        ("+ Net investment income tax", r.net_investment_income_tax),
        ("Total tax", r.total_tax),
        ("- Paid already and refundable credits", r.payments),
    ]
    for label, value in rows:
        print(f"  {label:<38}{value:>14,.2f}")
    print(f"  {'AMOUNT YOU OWE' if r.balance_due > 0 else 'REFUND':<38}{abs(r.balance_due):>14,.2f}")
    print(f"\nEffective rate: {_pct(r.effective_rate)} of total income")
    print(f"Marginal rate:  {r.marginal_rate:.0%} on your next dollar of ordinary income")
    for note in r.notes:
        print(f"Note: {note}")
    if r.balance_due > 0:
        verdict = f"you still owe about {_money(r.owed)} when you file."
    elif r.balance_due < 0:
        verdict = f"you've paid more than enough, so expect a refund of about {_money(r.refund)}."
    else:
        verdict = "what you paid matches what you owe."
    _takeaway(f"your total federal tax is about {_money(r.total_tax)} "
              f"({_pct(r.effective_rate)} of your income); {verdict}")


def cmd_explain(a: argparse.Namespace) -> None:
    if not a.term:
        print("Terms you can look up (nexus explain <term>):")
        for key in glossary.keys():
            print(f"  {key:<22}{glossary.TERMS[key].name}")
        return
    term = glossary.lookup(" ".join(a.term))
    if term is None:
        raise ValueError(f"no entry for {' '.join(a.term)!r}; run `nexus explain` to list terms")
    print(term.name)
    print(f"  What it means: {term.meaning}")
    print(f"  Example:       {term.example}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="nexus", description="Business finance & economics toolkit")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("npv", help="NPV, IRR and payback for a cash flow series")
    s.add_argument("--rate", type=float, required=True, help="discount rate, e.g. 0.08")
    s.add_argument("--cash-flows", required=True, help="comma separated, t=0 first; use --cash-flows=-1000,... for a negative first value")
    s.set_defaults(func=cmd_npv)

    s = sub.add_parser("loan", help="loan payment and amortization")
    s.add_argument("--principal", type=float, required=True)
    s.add_argument("--rate", type=float, required=True, help="annual rate")
    s.add_argument("--years", type=int, required=True)
    s.add_argument("--per-year", type=int, default=12)
    s.add_argument("--schedule", action="store_true", help="print full schedule")
    s.add_argument("--csv", help="write the schedule to this CSV file")
    s.set_defaults(func=cmd_loan)

    s = sub.add_parser("dcf", help="discounted cash flow valuation")
    s.add_argument("--cash-flows", required=True, help="forecast FCF years 1..N")
    s.add_argument("--rate", type=float, required=True, help="discount rate (WACC)")
    s.add_argument("--growth", type=float, required=True, help="terminal growth")
    s.add_argument("--net-debt", type=float, default=0.0)
    s.add_argument("--shares", type=float)
    s.set_defaults(func=cmd_dcf)

    s = sub.add_parser("wacc", help="CAPM cost of equity and WACC")
    s.add_argument("--risk-free", type=float, required=True)
    s.add_argument("--beta", type=float, required=True)
    s.add_argument("--market-return", type=float, required=True)
    s.add_argument("--equity", type=float, required=True, help="market value of equity")
    s.add_argument("--debt", type=float, required=True, help="market value of debt")
    s.add_argument("--cost-of-debt", type=float, required=True)
    s.add_argument("--tax", type=float, required=True)
    s.set_defaults(func=cmd_wacc)

    s = sub.add_parser("ratios", help="financial ratio report from a JSON file")
    s.add_argument("file")
    s.set_defaults(func=cmd_ratios)

    s = sub.add_parser("breakeven", help="break-even analysis")
    s.add_argument("--fixed", type=float, required=True)
    s.add_argument("--price", type=float, required=True)
    s.add_argument("--variable", type=float, required=True)
    s.add_argument("--target", type=float, default=0.0, help="target profit")
    s.set_defaults(func=cmd_breakeven)

    s = sub.add_parser("elasticity", help="arc price elasticity of demand")
    for name in ("q1", "q2", "p1", "p2"):
        s.add_argument(f"--{name}", type=float, required=True)
    s.set_defaults(func=cmd_elasticity)

    s = sub.add_parser("inflation", help="inflation, real rates and real values")
    s.add_argument("--cpi-old", type=float, required=True)
    s.add_argument("--cpi-new", type=float, required=True)
    s.add_argument("--nominal-rate", type=float)
    s.add_argument("--amount", type=float)
    s.set_defaults(func=cmd_inflation)

    s = sub.add_parser("forecast", help="driver-based FCF forecast (optionally valued)")
    s.add_argument("file", help="JSON assumptions file")
    s.add_argument("--rate", type=float, help="discount rate; enables valuation")
    s.add_argument("--growth", type=float, default=0.02, help="terminal growth")
    s.add_argument("--net-debt", type=float, default=0.0)
    s.add_argument("--shares", type=float)
    s.add_argument("--csv", help="write the forecast to this CSV file")
    s.set_defaults(func=cmd_forecast)

    s = sub.add_parser("sensitivity", help="valuation grid: discount rate x terminal growth")
    s.add_argument("file", help="JSON assumptions file")
    s.add_argument("--rates", default="0.07,0.08,0.09,0.10,0.11")
    s.add_argument("--growths", default="0.01,0.02,0.03")
    s.add_argument("--net-debt", type=float, default=0.0)
    s.add_argument("--shares", type=float)
    s.set_defaults(func=cmd_sensitivity)

    s = sub.add_parser("montecarlo", help="simulate project NPV under uncertainty")
    s.add_argument("--investment", type=float, required=True, help="initial outlay")
    s.add_argument("--cash-flow", type=float, required=True, help="mean annual cash flow")
    s.add_argument("--cash-flow-sd", type=float, required=True)
    s.add_argument("--years", type=int, required=True)
    s.add_argument("--rate-low", type=float, required=True)
    s.add_argument("--rate-high", type=float, required=True)
    s.add_argument("--trials", type=int, default=10_000)
    s.add_argument("--seed", type=int)
    s.set_defaults(func=cmd_montecarlo)

    s = sub.add_parser("tax", help="estimate US federal income tax owed or refunded")
    s.add_argument("--year", type=int, default=2026, choices=sorted(tax.YEARS))
    s.add_argument("--status", default="single", choices=tax.STATUSES, help="filing status")
    s.add_argument("--wages", type=float, default=0.0, help="W-2 wages (box 1)")
    s.add_argument("--self-employment", type=float, default=0.0, help="net self-employment profit")
    s.add_argument("--investment-income", type=float, default=0.0,
                   help="interest, ordinary dividends, short-term gains")
    s.add_argument("--long-term-gains", type=float, default=0.0,
                   help="long-term capital gains plus qualified dividends")
    s.add_argument("--other-income", type=float, default=0.0, help="other taxable income")
    s.add_argument("--adjustments", type=float, default=0.0,
                   help="above-the-line deductions, e.g. IRA, HSA, student loan interest")
    s.add_argument("--itemized", type=float, default=0.0,
                   help="itemized deductions (used if more than the standard deduction)")
    s.add_argument("--children", type=int, default=0, help="children under 17")
    s.add_argument("--withholding", type=float, default=0.0, help="federal tax withheld (W-2 box 2)")
    s.add_argument("--estimated", type=float, default=0.0, help="estimated tax payments made")
    s.set_defaults(func=cmd_tax)

    s = sub.add_parser("explain", help="plain-English meaning of a finance or economics term")
    s.add_argument("term", nargs="*", help="e.g. npv, inflation, break-even (omit to list all)")
    s.set_defaults(func=cmd_explain)
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
