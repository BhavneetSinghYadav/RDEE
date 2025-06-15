"""Sanity check utilities for RDEE parameters."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from typing import Any

from interface.parameter_schema import RDEEParameterSchema, ParameterSpec


class SanityCheckError(Exception):
    """Exception raised when a sanity check fails."""


def _validate_spec_types(schema: RDEEParameterSchema) -> None:
    """Validate individual parameter specification types."""
    for group_field in fields(schema):
        group = getattr(schema, group_field.name)
        if not is_dataclass(group):
            continue
        for param_field in fields(group):
            spec = getattr(group, param_field.name)
            if not isinstance(spec, ParameterSpec):
                raise SanityCheckError(
                    f"Invalid parameter specification for {group_field.name}.{param_field.name}"
                )
            if spec.default is not None:
                _assert_dtype(spec.default, spec.dtype, spec.name)


def _assert_dtype(value: Any, dtype: type, name: str) -> None:
    """Assert that value is instance of dtype allowing ints for floats."""
    if dtype is float:
        if not isinstance(value, (int, float)):
            raise SanityCheckError(
                f"Parameter '{name}' expects float-compatible value, got {type(value).__name__}"
            )
    else:
        if not isinstance(value, dtype):
            raise SanityCheckError(
                f"Parameter '{name}' expects {dtype.__name__}, got {type(value).__name__}"
            )


def check_parameter_sanity(parameters: RDEEParameterSchema) -> bool:
    """Perform high-level sanity checks on a parameter schema.

    Parameters
    ----------
    parameters:
        Fully populated :class:`RDEEParameterSchema` instance.

    Returns
    -------
    bool
        ``True`` if all sanity checks pass.

    Raises
    ------
    SanityCheckError
        If any sanity rule is violated.
    """

    _validate_spec_types(parameters)

    planetary = parameters.planetary
    prebiotic = parameters.prebiotic
    evolutionary = parameters.evolutionary
    habitability = parameters.habitability

    # Planetary system multiplicity must be >= 1
    mult = planetary.planetary_system_multiplicity.default
    if mult is None or mult < 1:
        raise SanityCheckError("Planetary system multiplicity must be >= 1")

    # Prebiotic synthesis success probability must be non-zero
    syn_prob = prebiotic.prebiotic_synthesis_success_probability.default
    if syn_prob is None or syn_prob <= 0:
        raise SanityCheckError(
            "Prebiotic synthesis success probability must be greater than zero"
        )

    # Evolutionary complexity threshold must be at least 1
    evo_thresh = evolutionary.evolutionary_complexity_threshold.default
    if evo_thresh is None or evo_thresh < 1:
        raise SanityCheckError(
            "Evolutionary complexity threshold must be at least 1"
        )

    # If liquid water zone is specified, planet distance should not deviate
    # more than 2x from its bounds
    lw_zone = habitability.liquid_water_zone_range
    planet_dist = planetary.planet_distance.default
    if planet_dist is not None:
        if lw_zone.min_value is not None and lw_zone.max_value is not None:
            if planet_dist < lw_zone.min_value / 2 or planet_dist > lw_zone.max_value * 2:
                raise SanityCheckError(
                    "Planet distance deviates more than 2x from liquid water zone bounds"
                )
        elif lw_zone.default is not None:
            center = lw_zone.default
            if planet_dist < center / 2 or planet_dist > center * 2:
                raise SanityCheckError(
                    "Planet distance deviates more than 2x from liquid water zone"
                )

    # Mass extinction frequency must be non-negative if provided
    mass_ext_freq = evolutionary.mass_extinction_frequency.default
    if mass_ext_freq is not None and mass_ext_freq < 0:
        raise SanityCheckError(
            "Mass extinction frequency must be non-negative when provided"
        )

    return True

