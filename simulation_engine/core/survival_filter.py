"""Generalized survival filter functions for RDEE."""

from __future__ import annotations

from typing import Optional
import random


def threshold_pass(value: float, min_value: Optional[float], max_value: Optional[float]) -> bool:
    """Return True if ``value`` falls within the inclusive range.

    Parameters
    ----------
    value:
        Value to evaluate.
    min_value:
        Lower bound of acceptable values. ``None`` indicates no lower bound.
    max_value:
        Upper bound of acceptable values. ``None`` indicates no upper bound.

    Returns
    -------
    bool
        ``True`` if ``value`` satisfies the bounds, ``False`` otherwise.
    """
    if min_value is not None and value < min_value:
        return False
    if max_value is not None and value > max_value:
        return False
    return True


def probabilistic_survival(success_probability: float, rng: Optional[random.Random] = None) -> bool:
    """Stochastically evaluate survival based on ``success_probability``.

    Parameters
    ----------
    success_probability:
        Probability of a successful outcome. Must lie within ``[0.0, 1.0]``.
    rng:
        Optional random number generator for deterministic sampling.

    Returns
    -------
    bool
        ``True`` with probability ``success_probability``.
    """
    if not 0.0 <= success_probability <= 1.0:
        raise ValueError("success_probability must be within [0.0, 1.0]")

    generator = rng if rng is not None else random
    return generator.random() < success_probability


def survival_window(reference_value: float, target_value: float, window_ratio: float) -> bool:
    """Evaluate whether ``target_value`` falls within a window around ``reference_value``.

    Parameters
    ----------
    reference_value:
        Central value defining the window center.
    target_value:
        Value to compare against the window.
    window_ratio:
        Fractional size of the window relative to ``reference_value``. Must be non-negative.

    Returns
    -------
    bool
        ``True`` if ``target_value`` is within the window, ``False`` otherwise.
    """
    if window_ratio < 0.0:
        raise ValueError("window_ratio must be non-negative")

    lower = reference_value * (1.0 - window_ratio)
    upper = reference_value * (1.0 + window_ratio)
    if lower > upper:
        lower, upper = upper, lower
    return lower <= target_value <= upper


def scaled_fragility(threshold: float, fragility_factor: float) -> bool:
    """Apply fragility scaling to a survival threshold.

    Parameters
    ----------
    threshold:
        Base value representing successful survival prior to fragility scaling. Values ``<= 0`` fail immediately.
    fragility_factor:
        Multiplier in ``[0.0, 1.0]`` representing additional chance of failure. ``1.0`` indicates guaranteed failure.

    Returns
    -------
    bool
        Survival outcome after applying fragility scaling.
    """
    if not 0.0 <= fragility_factor <= 1.0:
        raise ValueError("fragility_factor must be within [0.0, 1.0]")
    if threshold <= 0.0:
        return False

    probability = 1.0 - fragility_factor
    return random.random() < probability


class SurvivalEvaluator:
    """Utility class providing deterministic survival evaluations."""

    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = random.Random(seed)

    def threshold_pass(self, value: float, min_value: Optional[float], max_value: Optional[float]) -> bool:
        return threshold_pass(value, min_value, max_value)

    def probabilistic_survival(self, success_probability: float) -> bool:
        return probabilistic_survival(success_probability, self._rng)

    def survival_window(self, reference_value: float, target_value: float, window_ratio: float) -> bool:
        return survival_window(reference_value, target_value, window_ratio)

    def scaled_fragility(self, threshold: float, fragility_factor: float) -> bool:
        if not 0.0 <= fragility_factor <= 1.0:
            raise ValueError("fragility_factor must be within [0.0, 1.0]")
        if threshold <= 0.0:
            return False
        probability = 1.0 - fragility_factor
        return self._rng.random() < probability
