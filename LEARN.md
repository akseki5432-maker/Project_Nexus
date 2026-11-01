# Learn the Ideas Behind Nexus

This guide explains every idea in Nexus with everyday examples. You only need
basic algebra: percentages, multiplying and dividing. Each section ends with a
command you can run to try it yourself.

To look up any word while you work, run `nexus explain <word>`, for example
`nexus explain npv`. Run `nexus explain` on its own to see the full list.

---

## 1. Money has a time value

Would you rather have $100 today or $100 a year from now? Today, because you
could put it in the bank and have *more* than $100 next year. That simple idea
drives almost all of finance.

**Interest** is the price of using money. At 5% a year, $100 becomes $105.

**Compounding** means you also earn interest on past interest:

| Year | Balance at 5% |
| --- | --- |
| 0 | $100.00 |
| 1 | $105.00 |
| 2 | $110.25 |
| 10 | $162.89 |

The formula is `future value = today's amount × (1 + rate) ^ years`.

**Present value** runs the other way: what is future money worth today?
`present value = future amount ÷ (1 + rate) ^ years`. If you can earn 10%,
then $110 next year is worth $100 today.

The rate you use for this is called the **discount rate**. Think of it as
"the return I could get somewhere else."

## 2. Is a project worth doing?

Say a business can buy a machine for $500,000 that will bring in extra cash
for five years.

- **Net present value (NPV):** turn every future year's cash into today's
  dollars, add them up, and subtract the $500,000. If the answer is positive,
  the project earns more than your discount rate. Do it.
- **Internal rate of return (IRR):** the yearly return the project actually
  earns. Compare it with your discount rate.
- **Payback period:** how many years until you've earned your money back.
  It's easy to understand, but it ignores the time value of money.

```bash
nexus npv --rate 0.08 --cash-flows=-500000,120000,150000,170000,180000,160000
```

The output says NPV is about +$115,862 and IRR is about 16%. The project beats
an 8% required return, so it's worth considering.

## 3. Borrowing money

A loan is paid back in equal payments. Each payment covers that month's
interest first, and the rest pays down what you owe. Early on, most of the
payment is interest. Near the end, most of it is paying off the loan.

```bash
nexus loan --principal 250000 --rate 0.065 --years 30
```

A $250,000 home loan at 6.5% for 30 years costs $1,580.17 a month. Over 30
years you pay about $318,861 in interest, more than the amount you borrowed.

## 4. How a business makes money

| Word | Meaning | Lemonade stand example |
| --- | --- | --- |
| Revenue | All money from sales | 100 cups × $2 = $200 |
| Variable cost | Cost that grows with each sale | Lemons and cups: $0.50 a cup |
| Fixed cost | Cost that stays the same | Stand rental: $50 a week |
| Profit | Revenue minus all costs | $200 − $50 − $50 = $100 |
| Profit margin | Profit as a share of revenue | $100 ÷ $200 = 50% |

**Break-even point:** each cup leaves $1.50 after its own cost (this is the
**contribution margin**). To cover $50 of rent you must sell $50 ÷ $1.50 ≈ 34
cups. Below that you lose money; above it you profit.

```bash
nexus breakeven --fixed 200000 --price 50 --variable 30
```

**Operating leverage:** when fixed costs are high, profit swings a lot when
sales change. A leverage of 3.5 means a 10% rise in sales lifts profit about
35%, and a 10% fall cuts it about 35%.

## 5. What is a company worth?

A company is worth the cash it will produce in the future, brought back to
today. This is called a **discounted cash flow (DCF)** valuation.

1. **Forecast revenue.** Start with this year's sales and guess the growth
   rate for each of the next five years.
2. **Work out free cash flow** for each year: operating profit after tax, plus
   depreciation (a cost on paper that isn't cash), minus spending on new
   equipment, minus extra money tied up in stock and unpaid customer bills.
3. **Add the terminal value.** The company doesn't stop after year five, so
   we assume it grows slowly forever after that.
4. **Discount everything to today** and add it up. That's the **enterprise
   value**.
5. **Subtract net debt** (what it owes minus its cash) to get the owners'
   **equity value**, then divide by the number of shares.

```bash
nexus forecast examples/acme_assumptions.json --rate 0.09 --growth 0.025 --net-debt 4e6 --shares 1e6
```

For the example company, each share is worth about $18.95. But about 76% of
that comes from the terminal value (the years after the forecast), so the
answer depends heavily on guesses about the far future.

**Which discount rate?** Companies use the **WACC**, the average return their
owners and lenders expect. Owners expect more when a share is riskier.
**Beta** measures that risk: a beta of 1.5 means the share tends to move 1.5
times as much as the overall stock market.

## 6. Reading a company's report card

Financial ratios compare numbers from a company's reports:

| Ratio | Question it answers | Healthy sign |
| --- | --- | --- |
| Current ratio | Can it pay bills due this year? | Above 1 |
| Debt-to-equity | How much is borrowed vs owned? | Lower is safer |
| Profit margin | How much of each sale is kept? | Higher is better |
| Return on equity (ROE) | How well does it use owners' money? | Higher is better |

```bash
nexus ratios examples/acme_financials.json
```

## 7. Dealing with uncertainty

Every forecast is a guess. Nexus has three ways to see how much the guesses
matter:

- **Sensitivity table:** change one or two guesses and watch the answer move.
- **Scenarios:** run a bad, a normal and a great version of the story.
- **Monte Carlo simulation:** run the model 10,000 times with random but
  realistic guesses and count how often things go wrong. It's like rolling
  dice thousands of times to learn the odds.

```bash
nexus montecarlo --investment 500000 --cash-flow 150000 --cash-flow-sd 40000 --years 5 --rate-low 0.06 --rate-high 0.12 --seed 42
```

Result: on average the project adds about $83,000, but in about 3 out of 10
simulated futures it loses money. One number can hide that risk.

## 8. The bigger economy

- **Inflation:** prices rising over time. If a candy bar goes from $1.00 to
  $1.03, inflation is 3%.
- **Real vs nominal:** if your savings grow 7% but prices rise 3%, your
  *real* gain (what you can actually buy) is only about 4%.
- **Supply and demand:** buyers want less as price rises; sellers offer more.
  The price settles where the two match.
- **Price elasticity:** how much buyers react to price. People keep buying
  gasoline when it gets pricier (inelastic), but switch cereal brands easily
  (elastic).
- **GDP:** the value of everything a country produces in a year.

```bash
nexus inflation --cpi-old 300 --cpi-new 309 --nominal-rate 0.07
nexus elasticity --q1 100 --q2 80 --p1 10 --p2 12
```

## Try it without typing commands

Open `web/index.html` in any web browser. Nexus Studio lets you drag sliders
and watch the answers change, with a plain-English summary of each result.

## Practice questions

1. You can earn 5% at the bank. Is $1,000 in two years worth more or less
   than $900 today? (Hint: `1000 ÷ 1.05²`.)
2. A project costs $1,000 and pays $600 a year for two years. At a 10%
   discount rate, is its NPV positive?
3. A T-shirt sells for $20 and costs $12 to make. Rent is $400 a month. How
   many shirts must you sell each month to break even?
4. Your pay rises 4% and inflation is 6%. Did your real pay go up or down?

Answers: 1) $907.03, so more. 2) Yes, about +$41. 3) 50 shirts. 4) Down,
by about 1.9%.
