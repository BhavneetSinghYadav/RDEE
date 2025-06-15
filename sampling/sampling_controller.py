"""Sampling utilities for generating initial parameter sets."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
import random
from typing import Any, List

from interface.parameter_schema import ParameterSpec, RDEEParameterSchema


def sample_parameter_value(spec: ParameterSpec) -> Any:
    """Sample a value for a given :class:`ParameterSpec`.

    Parameters
    ----------
    spec:
        The specification describing bounds and type for the parameter.

    Returns
    -------
    Any
        A randomly sampled value within the provided range or the default if
        no range is defined.
    """

    if spec.min_value is not None and spec.max_value is not None:
        if spec.dtype is int:
            return int(random.randint(int(spec.min_value), int(spec.max_value)))
        if spec.dtype is float:
            return float(random.uniform(float(spec.min_value), float(spec.max_value)))
    if spec.default is not None:
        return spec.default
    return None


def _sample_dataclass(instance: Any) -> Any:
    """Recursively sample all ``ParameterSpec`` fields of a dataclass."""

    if isinstance(instance, ParameterSpec):
        sampled_value = sample_parameter_value(instance)
        return ParameterSpec(
            name=instance.name,
            dtype=instance.dtype,
            units=instance.units,
            min_value=instance.min_value,
            max_value=instance.max_value,
            default=sampled_value,
        )

    if is_dataclass(instance):
        kwargs = {}
        for field in fields(instance):
            value = getattr(instance, field.name)
            kwargs[field.name] = _sample_dataclass(value)
        return type(instance)(**kwargs)

    return instance


def generate_initial_samples(sample_size: int) -> List[RDEEParameterSchema]:
    """Generate a list of initial parameter samples for the engine.

    Parameters
    ----------
    sample_size:
        Number of parameter sets to create.

    Returns
    -------
    List[RDEEParameterSchema]
        A list of ``RDEEParameterSchema`` instances with sampled default values.
    """

    samples: List[RDEEParameterSchema] = []
    base_schema = RDEEParameterSchema()

    for _ in range(sample_size):
        sampled_schema = _sample_dataclass(base_schema)
        samples.append(sampled_schema)

    return samples

