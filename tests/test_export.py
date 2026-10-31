import csv
import io

from nexus import export, tvm


def test_write_csv_dataclasses():
    rows = tvm.amortization_schedule(1200, 0.0, 1)
    buf = io.StringIO()
    assert export.write_csv(rows, buf) == 12
    parsed = list(csv.DictReader(io.StringIO(buf.getvalue())))
    assert parsed[0]["payment"] == "100.0"
    assert parsed[-1]["balance"] == "0.0"


def test_write_csv_rounds_floats():
    buf = io.StringIO()
    export.write_csv([{"a": 0.1 + 0.2, "b": "x"}], buf)
    assert buf.getvalue().splitlines()[1] == "0.3,x"
