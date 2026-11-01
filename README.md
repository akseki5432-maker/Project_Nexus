# Project Nexus

**Nexus is a calculator for money decisions.** It answers questions like:

- Is this investment worth the money?
- How much will this loan really cost me?
- How many products do I need to sell to stop losing money?
- What is this company worth, and how sure can we be?
- How much does inflation shrink my savings?

It's written so that anyone with high school math can use it and understand
the answers. Every result ends with a plain-English **Takeaway**, and
`nexus explain <word>` defines any term in simple language.

New to these ideas? Start with **[LEARN.md](LEARN.md)**, a short guide with
everyday examples and practice questions.

## Three ways to use it

### 1. In your browser (easiest)

Open `web/index.html` in any web browser. **Nexus Studio** has sliders for
four models: what a company is worth, the risk of a project, the cost of a
loan, and break-even. The answers update as you move the sliders. Each view
has a plain-English summary and a "Words to know" box.

### 2. From the command line

Install once (needs Python 3.9 or newer):

```bash
pip install -e ".[dev]"
```

Then ask questions:

| Question | Command |
| --- | --- |
| What does a word mean? | `nexus explain npv` (or `nexus explain` for the list) |
| Is this project worth it? | `nexus npv --rate 0.08 --cash-flows=-500000,120000,150000,170000,180000,160000` |
| What will my loan cost? | `nexus loan --principal 250000 --rate 0.065 --years 30` |
| How many must I sell to break even? | `nexus breakeven --fixed 200000 --price 50 --variable 30` |
| What is this company worth? | `nexus forecast examples/acme_assumptions.json --rate 0.09 --growth 0.025 --net-debt 4e6 --shares 1e6` |
| How much do my guesses matter? | `nexus sensitivity examples/acme_assumptions.json --net-debt 4e6 --shares 1e6` |
| What are the odds of losing money? | `nexus montecarlo --investment 500000 --cash-flow 150000 --cash-flow-sd 40000 --years 5 --rate-low 0.06 --rate-high 0.12` |
| How healthy is this company? | `nexus ratios examples/acme_financials.json` |
| How fast are prices rising? | `nexus inflation --cpi-old 300 --cpi-new 309 --nominal-rate 0.05` |
| How much do buyers react to price? | `nexus elasticity --q1 100 --q2 80 --p1 10 --p2 12` |
| What return should projects beat? | `nexus wacc --risk-free 0.04 --beta 1.2 --market-return 0.09 --equity 6e6 --debt 4e6 --cost-of-debt 0.06 --tax 0.25` |

Tips:
- Write percentages as decimals: 8% is `0.08`.
- Money you spend is negative and money you receive is positive. When the
  first number is negative, use the `=` form: `--cash-flows=-500000,...`
- Add `--csv file.csv` to `loan` or `forecast` to open the table in a spreadsheet.

Example output:

```text
$ nexus loan --principal 250000 --rate 0.065 --years 30
Payment:        1,580.17 x 360
Total interest: 318,861.22

Takeaway: you'll pay back 568,861.22 in total; 318,861.22 of that is the cost of borrowing.
```

### 3. In your own Python code

```python
from nexus import tvm, economics, glossary

tvm.npv(0.08, [-500_000, 120_000, 150_000, 170_000, 180_000, 160_000])  # 115862.10
economics.break_even(fixed_costs=200_000, price=50, variable_cost=30).units  # 10000.0
print(glossary.lookup("inflation").meaning)
```

`examples/project_appraisal.py` walks through a full decision from start to finish.

## What's inside

| Part | What it helps with |
| --- | --- |
| `nexus.tvm` | Money over time: interest, savings growth, loans, and whether a project pays off (NPV, IRR, payback) |
| `nexus.valuation` | What a company or bond is worth (DCF, WACC, CAPM) |
| `nexus.forecast` | Turning guesses about sales and costs into a five-year cash forecast |
| `nexus.ratios` | A company's report card: can it pay its bills, how profitable is it |
| `nexus.economics` | Inflation, growth, supply and demand, price sensitivity, break-even, GDP |
| `nexus.scenarios` | What-if tables, best and worst cases, and Monte Carlo simulation |
| `nexus.glossary` | Plain-English definitions of every term |
| `nexus.export` | Saving results as spreadsheet (CSV) files |

## Checking the math

```bash
pytest
```

The tests compare results with standard textbook answers. GitHub Actions runs
them on Python 3.9, 3.11 and 3.13 for every change.

Results are for learning and planning. They are only as good as the guesses
you put in, and they are not financial advice.
