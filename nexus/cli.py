"""Command-line interface: ``nexus <command> [options]``."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from . import economics, ratios, tvm, valuation


def _floats(text: str) -> List[float]:
    return [float(x) for x in text.split(",") if x.strip()]


def _pct(x: float) -> str:
    return f"{x * 100:.2f}%"


def _money(x: float) -> str:
    return f"{x:,.2f}"


def cmd_npv(a: argparse.Namespace) -> None:
    flows = _floats(a.cash_flows)
    print(f"NPV @ {_pct(a.rate)}: {_money(tvm.npv(a.rate, flows))}")
    try:
        print(f"IRR:            {_pct(tvm.irr(flows))}")
    except ValueError as exc:
        print(f"IRR:            n/a ({exc})")
    print(f"Payback:        {tvm.payback_period(flows):.2f} periods")


def cmd_loan(a: argparse.Namespace) -> None:
    rows = tvm.amortization_schedule(a.principal, a.rate, a.years, a.per_year)
    total_interest = sum(r.interest for r in rows)
    print(f"Payment:        {_money(rows[0].payment)} x {len(rows)}")
    print(f"Total interest: {_money(total_interest)}")
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


def cmd_wacc(a: argparse.Namespace) -> None:
    ke = valuation.capm(a.risk_free, a.beta, a.market_return)
    w = valuation.wacc(a.equity, a.debt, ke, a.cost_of_debt, a.tax)
    print(f"Cost of equity (CAPM): {_pct(ke)}")
    print(f"WACC:                  {_pct(w)}")


def cmd_ratios(a: argparse.Namespace) -> None:
    with open(a.file) as fh:
        f = ratios.Financials.from_dict(json.load(fh))
    for group, values in ratios.analyze(f).items():
        print(group.upper())
        for name, value in values.items():
            print(f"  {name:<24}{value:>10.3f}")


def cmd_breakeven(a: argparse.Namespace) -> None:
    be = economics.break_even(a.fixed, a.price, a.variable, a.target)
    print(f"Contribution margin: {_money(be.contribution_margin)} "
          f"({_pct(be.contribution_margin_ratio)})")
    print(f"Break-even units:    {be.units:,.1f}")
    print(f"Break-even revenue:  {_money(be.revenue)}")


def cmd_elasticity(a: argparse.Namespace) -> None:
    e = economics.arc_elasticity(a.q1, a.q2, a.p1, a.p2)
    print(f"Arc elasticity: {e:.3f} ({economics.classify_elasticity(e)})")


def cmd_inflation(a: argparse.Namespace) -> None:
    pi = economics.inflation_rate(a.cpi_old, a.cpi_new)
    print(f"Inflation:  {_pct(pi)}")
    if a.nominal_rate is not None:
        print(f"Real rate:  {_pct(economics.fisher_real_rate(a.nominal_rate, pi))}")
    if a.amount is not None:
        real = economics.to_real(a.amount, a.cpi_new, a.cpi_old)
        print(f"{_money(a.amount)} today = {_money(real)} in base-period prices")


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
