from nexus.cli import main


def test_npv_command(capsys):
    assert main(["npv", "--rate", "0.1", "--cash-flows=-1000,300,400,500"]) == 0
    out = capsys.readouterr().out
    assert "NPV" in out and "IRR" in out


def test_breakeven_error_returns_1(capsys):
    assert main(["breakeven", "--fixed", "100", "--price", "5", "--variable", "6"]) == 1
    assert "error" in capsys.readouterr().err


def test_ratios_command(capsys):
    assert main(["ratios", "examples/acme_financials.json"]) == 0
    assert "current_ratio" in capsys.readouterr().out


def test_forecast_command_writes_csv(tmp_path, capsys):
    out = tmp_path / "fc.csv"
    assert main(["forecast", "examples/acme_assumptions.json", "--rate", "0.09",
                 "--growth", "0.025", "--shares", "1e6", "--csv", str(out)]) == 0
    assert "Enterprise value" in capsys.readouterr().out
    assert out.read_text().startswith("year,revenue")


def test_sensitivity_command(capsys):
    assert main(["sensitivity", "examples/acme_assumptions.json",
                 "--rates", "0.08,0.1", "--growths", "0.02"]) == 0
    assert "terminal growth" in capsys.readouterr().out


def test_montecarlo_command(capsys):
    assert main(["montecarlo", "--investment", "1000", "--cash-flow", "400",
                 "--cash-flow-sd", "50", "--years", "3", "--rate-low", "0.05",
                 "--rate-high", "0.1", "--trials", "500", "--seed", "1"]) == 0
    assert "P(NPV<0)" in capsys.readouterr().out


def test_loan_csv(tmp_path):
    out = tmp_path / "loan.csv"
    assert main(["loan", "--principal", "1000", "--rate", "0.05", "--years", "1",
                 "--csv", str(out)]) == 0
    assert len(out.read_text().splitlines()) == 13
