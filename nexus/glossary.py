"""Plain-English definitions of every idea in Nexus, written for someone
meeting them for the first time (about a high school level)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Term:
    name: str
    meaning: str
    example: str


TERMS: Dict[str, Term] = {
    "interest": Term(
        "Interest",
        "The price of using someone else's money. Savers earn it; borrowers pay it.",
        "Put $100 in a bank paying 5% a year and you have $105 after one year.",
    ),
    "compounding": Term(
        "Compounding",
        "Earning interest on your interest. Money grows faster the longer it stays put.",
        "$100 at 5% becomes $105, then $110.25, because year two pays 5% on $105.",
    ),
    "present-value": Term(
        "Present value",
        "What money you'll get in the future is worth today. Money later is worth "
        "less than money now, because money now could be earning interest.",
        "$110 a year from now is worth $100 today if you could earn 10% elsewhere.",
    ),
    "discount-rate": Term(
        "Discount rate",
        "The yearly return you require before an investment is worth it. It's what "
        "you use to turn future money into today's money.",
        "If you could safely earn 8% somewhere else, a new project should beat 8%.",
    ),
    "npv": Term(
        "Net present value (NPV)",
        "All of a project's future money brought back to today's value, minus what it "
        "costs to start. Positive means it beats your required return; negative means it doesn't.",
        "Spend $1,000 today to get $1,200 next year. At a 10% discount rate the $1,200 "
        "is worth $1,091 today, so NPV = +$91. Good deal.",
    ),
    "irr": Term(
        "Internal rate of return (IRR)",
        "The yearly return a project actually earns. If it's higher than your discount "
        "rate, the project is worth doing.",
        "Spend $1,000, get $1,100 back in a year: the IRR is 10%.",
    ),
    "payback": Term(
        "Payback period",
        "How long until you earn back what you spent. Simple, but it ignores the time value of money.",
        "Spend $1,000 and earn $400 a year: you're paid back in 2.5 years.",
    ),
    "loan": Term(
        "Loan payment and amortization",
        "Paying a loan off with equal payments. Early payments are mostly interest; "
        "later ones are mostly paying down what you owe. The table of payments is the "
        "amortization schedule.",
        "On a 30-year home loan, about two thirds of the first payment is interest.",
    ),
    "revenue": Term(
        "Revenue",
        "All the money a business takes in from selling things, before any costs.",
        "A lemonade stand selling 100 cups at $2 has $200 of revenue.",
    ),
    "profit-margin": Term(
        "Profit margin",
        "How many cents of each dollar of sales the business keeps as profit.",
        "A 20% margin means $20 of profit on every $100 of sales.",
    ),
    "ebit": Term(
        "EBIT (operating profit)",
        "Profit from running the business, before paying interest on loans and taxes.",
        "Sales $500, costs $400: EBIT is $100.",
    ),
    "depreciation": Term(
        "Depreciation",
        "Spreading the cost of equipment over the years it's used, since it wears out slowly.",
        "A $5,000 oven that lasts 5 years counts as $1,000 of cost each year.",
    ),
    "capex": Term(
        "Capital spending (capex)",
        "Money spent on long-lasting things like machines, buildings or computers.",
        "A bakery buying a new oven.",
    ),
    "working-capital": Term(
        "Working capital",
        "Money tied up in day-to-day running: stock on shelves and bills customers "
        "haven't paid yet. A growing business needs more of it.",
        "A shop must buy its stock before it can sell it.",
    ),
    "free-cash-flow": Term(
        "Free cash flow",
        "Cash the business actually has left each year after paying its costs, taxes "
        "and investments. It's what owners and lenders could take out.",
        "Profit after tax $80, plus depreciation $10, minus new equipment $20 = $70.",
    ),
    "dcf": Term(
        "Discounted cash flow (DCF) valuation",
        "Valuing a business by forecasting its future free cash flows and adding up "
        "what they're worth today.",
        "Like NPV, but for a whole company instead of one project.",
    ),
    "terminal-value": Term(
        "Terminal value",
        "The value of all the years after the forecast ends, assuming the business "
        "keeps growing slowly forever. It's often most of a company's value, so it's worth questioning.",
        "If 75% of the value is terminal value, most of the price depends on the far future.",
    ),
    "enterprise-value": Term(
        "Enterprise value",
        "What the whole business is worth to everyone who funds it: owners and lenders together.",
        "Like a house's full price, before taking off the mortgage.",
    ),
    "equity-value": Term(
        "Equity value and value per share",
        "What's left for the owners after paying off debt. Divide it by the number of "
        "shares to get the value of one share.",
        "House worth $300k with a $200k mortgage: the owner's equity is $100k.",
    ),
    "net-debt": Term(
        "Net debt",
        "What a company owes, minus the cash it holds.",
        "Owe $5M, hold $1M cash: net debt is $4M.",
    ),
    "wacc": Term(
        "WACC (weighted average cost of capital)",
        "The average yearly return a company must pay its owners and lenders. It's the "
        "usual discount rate for valuing a company.",
        "Owners want 10% and lenders want 6%: the average is somewhere between.",
    ),
    "capm": Term(
        "CAPM and beta",
        "A formula for the return owners expect. Riskier shares (higher beta, meaning they "
        "swing more than the market) must offer more.",
        "Beta 1.5 means the share tends to move 1.5 times as much as the overall market.",
    ),
    "bond": Term(
        "Bond",
        "A loan you make to a company or government. It pays you interest, then returns your money at the end.",
        "A $1,000 bond paying 5% gives you $50 a year until it ends.",
    ),
    "ratios": Term(
        "Financial ratios",
        "Comparisons between numbers on a company's reports that show its health at a glance.",
        "Current ratio 1.8: the company has $1.80 of short-term assets for each $1 it owes soon.",
    ),
    "roe": Term(
        "Return on equity (ROE)",
        "Profit compared with the owners' money in the business.",
        "Owners put in $1,000 and the business earns $150: ROE is 15%.",
    ),
    "inflation": Term(
        "Inflation",
        "Prices going up over time, so each dollar buys a bit less.",
        "If a $1.00 candy bar costs $1.03 next year, inflation is 3%.",
    ),
    "real-vs-nominal": Term(
        "Real vs nominal",
        "Nominal means the plain number. Real means after taking out inflation, so it "
        "shows what you can actually buy.",
        "Your savings grow 7% but prices rise 3%: your real gain is about 4%.",
    ),
    "growth-rate": Term(
        "Growth rate (CAGR)",
        "The steady yearly growth that would take something from its starting value to its ending value.",
        "$100 that becomes $200 in 10 years grew about 7.2% a year.",
    ),
    "supply-demand": Term(
        "Supply and demand",
        "Buyers want less as the price rises; sellers offer more. The market price "
        "settles where the two amounts match (equilibrium).",
        "Concert tickets: too cheap and they sell out with people left over; too pricey and seats sit empty.",
    ),
    "elasticity": Term(
        "Price elasticity",
        "How strongly buyers react to a price change. Elastic means they react a lot; "
        "inelastic means they keep buying anyway.",
        "Gasoline is inelastic (people still need to drive); one brand of cereal is elastic.",
    ),
    "break-even": Term(
        "Break-even point",
        "How many units you must sell so that money in equals money out: no profit, no loss.",
        "Rent is $200 a month and each cup earns $1 after ingredients: sell 200 cups to break even.",
    ),
    "fixed-variable-costs": Term(
        "Fixed and variable costs",
        "Fixed costs stay the same however much you sell (rent). Variable costs rise "
        "with each unit (ingredients).",
        "A pizza shop's rent is fixed; its cheese is variable.",
    ),
    "contribution-margin": Term(
        "Contribution margin",
        "What each sale leaves over after its own variable cost, to help pay fixed costs and then make profit.",
        "Sell a shirt for $20 that costs $12 to make: each one contributes $8.",
    ),
    "operating-leverage": Term(
        "Operating leverage",
        "How much profit swings when sales change. High fixed costs make profit swing more.",
        "Leverage 3.5x: sales up 10% means profit up about 35% (and down 35% if sales fall 10%).",
    ),
    "sensitivity": Term(
        "Sensitivity analysis",
        "Changing one or two guesses at a time to see how much the answer moves.",
        "What's the company worth if the discount rate is 8% instead of 9%?",
    ),
    "scenario": Term(
        "Scenarios",
        "Running the numbers for a few whole stories, such as a bad year, a normal year and a great year.",
        "Bear case: fewer sales and lower prices. Bull case: more sales.",
    ),
    "monte-carlo": Term(
        "Monte Carlo simulation",
        "Running a model thousands of times with random but realistic guesses to see "
        "the full range of outcomes, not just one answer.",
        "Like rolling dice 10,000 times to learn how often you'd lose money.",
    ),
    "standard-deviation": Term(
        "Standard deviation and percentiles",
        "Standard deviation measures how spread out results are. The 5th percentile "
        "means only 5% of outcomes were worse.",
        "A 90% range from -$177K to +$348K means 9 in 10 outcomes landed in between.",
    ),
    "tax-bracket": Term(
        "Tax bracket and marginal rate",
        "A band of income taxed at one rate. Your marginal rate is the rate on your "
        "next dollar. Moving into a higher bracket only raises the tax on the dollars "
        "inside that bracket, never on all your income.",
        "Single in 2026 with $58,900 taxable: 10% on the first $12,400, 12% on the next "
        "$38,000 and 22% on the last $8,500.",
    ),
    "effective-tax-rate": Term(
        "Effective tax rate",
        "Your total tax divided by your total income. It's lower than your bracket "
        "because the first dollars are taxed lightly or not at all.",
        "$7,670 of tax on $75,000 of income is an effective rate of about 10%, even in the 22% bracket.",
    ),
    "deduction": Term(
        "Tax deduction",
        "An amount taken off your income before tax is worked out. Everyone gets the "
        "standard deduction, or can itemize if their own deductions add up to more.",
        "A $1,000 deduction in the 22% bracket saves you $220.",
    ),
    "tax-credit": Term(
        "Tax credit",
        "An amount taken straight off your tax bill, dollar for dollar. Worth more than "
        "a deduction of the same size.",
        "The $2,200 child tax credit cuts your tax by $2,200 for each child under 17.",
    ),
    "withholding": Term(
        "Withholding and refunds",
        "Tax your employer takes from each paycheck and sends to the government for you. "
        "When you file, you get back anything paid beyond what you owe, or pay the gap.",
        "Owe $7,670 but had $8,000 withheld: you get a $330 refund.",
    ),
    "gdp": Term(
        "GDP and the multiplier",
        "GDP is the value of everything a country produces in a year. The multiplier "
        "says one dollar of new spending can grow GDP by more than a dollar, because "
        "it gets spent again.",
        "If people spend 80 cents of each extra dollar, $1 of new spending can add $5 to GDP.",
    ),
}


def lookup(query: str) -> Optional[Term]:
    """Find a term by key or by a word in its name (case-insensitive)."""
    q = query.strip().lower().replace(" ", "-")
    if q in TERMS:
        return TERMS[q]
    plain = q.replace("-", " ")
    for term in TERMS.values():
        if plain in term.name.lower():
            return term
    return None


def keys() -> List[str]:
    return sorted(TERMS)
