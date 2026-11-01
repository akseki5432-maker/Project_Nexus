"""Risk analysis: sensitivity tables, tornado charts, named scenarios and
Monte Carlo simulation over any model expressed as ``f(**inputs) -> float``."""

from __future__ import annotations

import random
import statistics
from dataclasses import dataclass
from typing import Callable, Dict, List, Mapping, Sequence, Tuple

Model = Callable[..., float]


def one_way(model: Model, base: Mapping[str, float], name: str,
            values: Sequence[float]) -> List[Tuple[float, float]]:
    """Output of ``model`` as one input varies, others held at base."""
    return [(v, model(**{**base, name: v})) for v in values]


def two_way(model: Model, base: Mapping[str, float], row: str, row_values: Sequence[float],
            col: str, col_values: Sequence[float]) -> List[List[float]]:
    """Grid of outputs: ``grid[i][j]`` uses ``row_values[i]`` and ``col_values[j]``."""
    return [[model(**{**base, row: r, col: c}) for c in col_values] for r in row_values]


@dataclass(frozen=True)
class TornadoBar:
    name: str
    low_input: float
    high_input: float
    low_output: float
    high_output: float

    @property
    def swing(self) -> float:
        return abs(self.high_output - self.low_output)


def tornado(model: Model, base: Mapping[str, float],
            ranges: Mapping[str, Tuple[float, float]]) -> List[TornadoBar]:
    """Swing in output for each input's (low, high) range, largest first."""
    bars = []
    for name, (lo, hi) in ranges.items():
        bars.append(TornadoBar(name, lo, hi, model(**{**base, name: lo}),
                               model(**{**base, name: hi})))
    return sorted(bars, key=lambda b: b.swing, reverse=True)


def run_scenarios(model: Model, base: Mapping[str, float],
                  scenarios: Mapping[str, Mapping[str, float]]) -> Dict[str, float]:
    """Evaluate named scenarios, each overriding some base inputs."""
    return {name: model(**{**base, **overrides}) for name, overrides in scenarios.items()}


# --- Monte Carlo -----------------------------------------------------------

Sampler = Callable[[random.Random], float]


def normal(mean: float, sd: float) -> Sampler:
    return lambda rng: rng.gauss(mean, sd)


def uniform(low: float, high: float) -> Sampler:
    return lambda rng: rng.uniform(low, high)


def triangular(low: float, mode: float, high: float) -> Sampler:
    return lambda rng: rng.triangular(low, high, mode)


def fixed(value: float) -> Sampler:
    return lambda rng: value


@dataclass(frozen=True)
class SimulationResult:
    outcomes: List[float]

    @property
    def mean(self) -> float:
        return statistics.fmean(self.outcomes)

    @property
    def stdev(self) -> float:
        return statistics.stdev(self.outcomes) if len(self.outcomes) > 1 else 0.0

    def percentile(self, p: float) -> float:
        """Linear-interpolated percentile, ``p`` in [0, 100]."""
        data = sorted(self.outcomes)
        k = (len(data) - 1) * p / 100
        lo, hi = int(k), min(int(k) + 1, len(data) - 1)
        return data[lo] + (data[hi] - data[lo]) * (k - lo)

    def prob_below(self, threshold: float = 0.0) -> float:
        return sum(x < threshold for x in self.outcomes) / len(self.outcomes)

    def summary(self) -> Dict[str, float]:
        return {
            "mean": self.mean,
            "stdev": self.stdev,
            "p5": self.percentile(5),
            "p50": self.percentile(50),
            "p95": self.percentile(95),
            "prob_negative": self.prob_below(0.0),
        }


def monte_carlo(model: Model, samplers: Mapping[str, Sampler], trials: int = 10_000,
                seed: int | None = None) -> SimulationResult:
    """Draw inputs from ``samplers`` ``trials`` times and collect model outputs."""
    if trials < 1:
        raise ValueError("trials must be at least 1")
    rng = random.Random(seed)
    outcomes = [model(**{k: s(rng) for k, s in samplers.items()}) for _ in range(trials)]
    return SimulationResult(outcomes)
