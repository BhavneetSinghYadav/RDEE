"""Sampling Adapter Layer for orchestration.

This module exposes utilities for batch parameter sampling that
integrate with the lower level sampling controller.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Dict, List

from interface.parameter_schema import RDEEParameterSchema, ParameterSpec
from sampling import sampling_controller
from sampling.sampling_controller import _sample_dataclass


def _resolve_spec(schema: RDEEParameterSchema, path: str) -> ParameterSpec:
    """Resolve a ``ParameterSpec`` object from ``RDEEParameterSchema`` via dot path."""
    current: Any = schema
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
    if not sample_config:
        return sampling_controller.generate_initial_samples(batch_size)

    base = RDEEParameterSchema()
    for path, bounds in sample_config.items():
        spec = _resolve_spec(base, path)
        new_min = bounds.get("min", spec.min_value)
        new_max = bounds.get("max", spec.max_value)
        parent: Any = base
        parts = path.split(".")
        for part in parts[:-1]:
            parent = getattr(parent, part)
        field = parts[-1]
        setattr(parent, field, replace(spec, min_value=new_min, max_value=new_max))

    samples: List[RDEEParameterSchema] = []
    for _ in range(batch_size):
        samples.append(_sample_dataclass(base))

    return samples
