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
