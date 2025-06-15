from __future__ import annotations

"""Bifurcation control utilities for the RDEE recursion core."""

from dataclasses import fields, is_dataclass
from typing import Any, List, Optional
import copy
import random

from interface.parameter_schema import ParameterSpec, RDEEParameterSchema


def perturb_parameter(
    parameter_spec: ParameterSpec,
    perturbation_scale: float,
    rng: Optional[random.Random] = None,
) -> Any:
    """Return a perturbed value for ``parameter_spec``.

    Parameters
    ----------
    parameter_spec:
        Specification describing the parameter to perturb.
    perturbation_scale:
        Fraction of the parameter range used as perturbation magnitude.
    rng:
        Random number generator instance. If ``None``, the default ``random``
        module is used.

    Returns
    -------
    Any
        Perturbed value constrained within ``min_value`` and ``max_value``.
    """

    if rng is None:
        rng = random

    if parameter_spec.min_value is None or parameter_spec.max_value is None:
        return parameter_spec.default

    base_value = (
        parameter_spec.default
        if parameter_spec.default is not None
        else (parameter_spec.min_value + parameter_spec.max_value) / 2
    )

    full_range = float(parameter_spec.max_value - parameter_spec.min_value)
    magnitude = full_range * perturbation_scale
    delta = rng.uniform(-magnitude, magnitude)
    new_value = base_value + delta

    new_value = max(parameter_spec.min_value, min(parameter_spec.max_value, new_value))

    if parameter_spec.dtype is int:
        new_value = int(round(new_value))
        new_value = max(int(parameter_spec.min_value), min(int(parameter_spec.max_value), new_value))
    else:
        new_value = float(new_value)

    return new_value


def perturb_schema(
    base_schema: RDEEParameterSchema,
    perturbation_scale: float,
    rng: Optional[random.Random] = None,
) -> RDEEParameterSchema:
    """Return a perturbed clone of ``base_schema``.

    Parameters
    ----------
    base_schema:
        Schema providing parameter defaults to perturb.
    perturbation_scale:
        Fraction of parameter ranges used as perturbation magnitudes.
    rng:
        Random number generator instance. If ``None``, a new one is created.

    Returns
    -------
    RDEEParameterSchema
        Deep-copy of ``base_schema`` with perturbed ``ParameterSpec`` defaults.
    """

    if rng is None:
        rng = random.Random()

    schema_copy = copy.deepcopy(base_schema)

    def _apply(obj: Any) -> None:
        if isinstance(obj, ParameterSpec):
            if obj.min_value is None and obj.max_value is None:
                return
            obj.default = perturb_parameter(obj, perturbation_scale, rng)
            return
        if is_dataclass(obj):
            for field in fields(obj):
                _apply(getattr(obj, field.name))

    _apply(schema_copy)
    return schema_copy


def generate_bifurcations(
    parameters: RDEEParameterSchema,
    branching_factor: int,
    perturbation_scale: float,
) -> List[RDEEParameterSchema]:
    """Generate perturbed child schemas from a base set of parameters.

    Parameters
    ----------
    parameters:
        Base parameter schema to branch from.
    branching_factor:
        Number of child schemas to generate.
    perturbation_scale:
        Magnitude of perturbations as a fraction of parameter ranges.

    Returns
    -------
    list[RDEEParameterSchema]
        List of independent perturbed parameter schemas.
    """

    bifurcations: List[RDEEParameterSchema] = []
    for _ in range(branching_factor):
        rng = random.Random()
        child = perturb_schema(parameters, perturbation_scale, rng)
        bifurcations.append(child)

    return bifurcations

