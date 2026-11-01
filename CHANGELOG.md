# Changelog

## 0.4.0

- US federal tax estimator for 2025 and 2026 (`nexus.tax`): brackets, standard or
  itemized deduction, long-term gains rates, child tax credit, self-employment tax,
  Additional Medicare Tax and Net Investment Income Tax, then the amount owed or refunded.
- `nexus tax` command.
- Nexus Studio: new Taxes view (now the opening view) with a step-by-step breakdown
  and a bar showing how each slice of income is taxed.
- Five new glossary terms on tax.

## 0.3.0

- Rewritten for a high school reader: plain-English README and a new `LEARN.md`
  guide with everyday examples and practice questions.
- `nexus explain <term>`: plain-English definitions of 39 terms (`nexus.glossary`).
- Every command now ends with a one-line plain-English Takeaway.
- Nexus Studio: plain labels with hints, a live summary sentence and a
  "Words to know" box on each view.

## 0.2.0

- Driver-based free cash flow forecast with one-step DCF valuation (`nexus.forecast`).
- Sensitivity tables, tornado analysis, named scenarios and Monte Carlo simulation (`nexus.scenarios`).
- CSV export for loan schedules and forecasts (`nexus.export`).
- CLI commands `forecast`, `sensitivity` and `montecarlo`; `--csv` on `loan`.
- Nexus Studio: interactive browser dashboard in `web/index.html`.
- GitHub Actions CI on Python 3.9, 3.11 and 3.13.

## 0.1.0

- Time value of money, valuation, financial ratios and applied economics modules.
- `nexus` command-line interface and worked example.
