"""Sampling Adapter Layer for orchestration.

This module exposes utilities for batch parameter sampling that
integrate with the lower level sampling controller.
"""

from __future__ import annotations

from typing import Any, Dict, List

from interface.parameter_schema import RDEEParameterSchema, ParameterSpec
from sampling import sampling_controller


def _resolve_spec(path: str) -> ParameterSpec:
    """Resolve a ``ParameterSpec`` object from ``RDEEParameterSchema`` via dot path."""
    current: Any = RDEEParameterSchema()
    for part in path.split("."):
        if not hasattr(current, part):
            raise KeyError(f"Invalid parameter path: {path}")
        current = getattr(current, part)
    if not isinstance(current, ParameterSpec):
        raise TypeError(f"Path '{path}' does not resolve to a ParameterSpec")
    return current


def generate_batch_samples(batch_size: int, sample_config: Dict[str, Dict[str, float]] | None = None) -> List[RDEEParameterSchema]:
    """Generate a batch of parameter samples.

    Parameters
    ----------
    batch_size:
        Number of samples to generate.
    sample_config:
        Optional mapping of parameter paths to ``{"min": float, "max": float}``
        overrides. Keys use dot notation to address nested parameters.

    Returns
    -------
    List[RDEEParameterSchema]
        Newly sampled parameter schemas.
    """
    overrides: List[tuple[ParameterSpec, float | None, float | None]] = []

    if sample_config:
        for path, bounds in sample_config.items():
            spec = _resolve_spec(path)
            overrides.append((spec, spec.min_value, spec.max_value))
            if "min" in bounds:
                spec.min_value = bounds["min"]
            if "max" in bounds:
                spec.max_value = bounds["max"]

    try:
        samples = sampling_controller.generate_initial_samples(batch_size)
    finally:
        for spec, old_min, old_max in overrides:
            spec.min_value = old_min
            spec.max_value = old_max

    return samples
