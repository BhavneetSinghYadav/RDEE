from __future__ import annotations

"""Bifurcation utilities for parameter perturbations in recursive branching."""

from dataclasses import asdict, fields, is_dataclass
from typing import Any, List, get_type_hints
import numpy as np

from interface.parameter_schema import ParameterSpec, RDEEParameterSchema


def _dict_to_dataclass(data: Any, cls: type) -> Any:
    """Recursively rebuild dataclasses from ``data``.

    Parameters
    ----------
    data:
        Dictionary or primitive produced by :func:`dataclasses.asdict`.
    cls:
        Target dataclass type for reconstruction.

    Returns
    -------
    Any
        Instance of ``cls`` populated with ``data``.
    """
    if cls is ParameterSpec:
        return ParameterSpec(**data)

    if is_dataclass(cls):
        type_hints = get_type_hints(cls)
        kwargs = {}
        for f in fields(cls):
            resolved_type = type_hints.get(f.name, f.type)
            kwargs[f.name] = _dict_to_dataclass(data[f.name], resolved_type)
        return cls(**kwargs)

    return data


def _clone_schema(schema: RDEEParameterSchema) -> RDEEParameterSchema:
    """Deep clone ``schema`` using :func:`dataclasses.asdict`."""
    return _dict_to_dataclass(asdict(schema), RDEEParameterSchema)


def _perturb_spec(spec: ParameterSpec, rng: np.random.Generator, scale: float) -> ParameterSpec:
    """Return a copy of ``spec`` with its default value perturbed."""
    default = spec.default
    if default is None:
        return spec
    if spec.dtype not in (int, float):
        raise TypeError(f"Unsupported dtype {spec.dtype!r} for parameter '{spec.name}'")

    noise = rng.normal(0.0, scale)
    perturbed = default * (1.0 + noise)

    if spec.min_value is not None:
        perturbed = max(spec.min_value, perturbed)
    if spec.max_value is not None:
        perturbed = min(spec.max_value, perturbed)

    if spec.dtype is int:
        perturbed = int(round(perturbed))
        if spec.min_value is not None:
            perturbed = max(int(spec.min_value), perturbed)
        if spec.max_value is not None:
            perturbed = min(int(spec.max_value), perturbed)
    else:
        perturbed = float(perturbed)

    return ParameterSpec(
        name=spec.name,
        dtype=spec.dtype,
        units=spec.units,
        min_value=spec.min_value,
        max_value=spec.max_value,
        default=perturbed,
    )


def _apply_perturbations(obj: Any, rng: np.random.Generator, scale: float) -> Any:
    """Recursively perturb ``ParameterSpec`` defaults within ``obj``."""
    if isinstance(obj, ParameterSpec):
        return _perturb_spec(obj, rng, scale)
    if is_dataclass(obj):
        for f in fields(obj):
            value = getattr(obj, f.name)
            new_value = _apply_perturbations(value, rng, scale)
            setattr(obj, f.name, new_value)
        return obj
    raise TypeError(f"Unsupported object type {type(obj).__name__} encountered")


def generate_bifurcations(
    parameters: RDEEParameterSchema,
    branching_factor: int,
    perturbation_scale: float,
) -> List[RDEEParameterSchema]:
    """Generate perturbed child parameter schemas from ``parameters``.

    Each child is a deep clone of ``parameters`` with every numeric
    :class:`ParameterSpec` default value perturbed by a multiplicative factor
    drawn from a normal distribution with scale ``perturbation_scale``.

    Parameters
    ----------
    parameters:
        Base parameter schema to branch from.
    branching_factor:
        Number of child schemas to create. Must be positive.
    perturbation_scale:
        Standard deviation of the perturbation factor.

    Returns
    -------
    list[RDEEParameterSchema]
        Independent parameter sets with stochastic perturbations applied.
    """
    if branching_factor <= 0:
        raise ValueError("branching_factor must be positive")
    if perturbation_scale < 0.0:
        raise ValueError("perturbation_scale must be non-negative")

    children: List[RDEEParameterSchema] = []
    for _ in range(branching_factor):
        rng = np.random.default_rng()
        child = _clone_schema(parameters)
        child = _apply_perturbations(child, rng, perturbation_scale)
        children.append(child)

    return children
