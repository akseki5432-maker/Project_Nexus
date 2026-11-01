"""CSV export helpers for schedules and forecasts."""

from __future__ import annotations

import csv
from dataclasses import asdict, is_dataclass
from typing import Any, Iterable, TextIO


def _clean(value: Any, digits: int) -> Any:
    return round(value, digits) if isinstance(value, float) else value


def write_csv(rows: Iterable[Any], out: TextIO, digits: int = 6) -> int:
    """Write dataclass instances or dicts as CSV; returns rows written.

    Floats are rounded to ``digits`` places to drop floating-point noise.
    """
    writer = None
    count = 0
    for row in rows:
        raw = asdict(row) if is_dataclass(row) else dict(row)
        data = {k: _clean(v, digits) for k, v in raw.items()}
        if writer is None:
            writer = csv.DictWriter(out, fieldnames=list(data))
            writer.writeheader()
        writer.writerow(data)
        count += 1
    return count
