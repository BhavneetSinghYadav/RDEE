from __future__ import annotations

"""Physical constraint validation for RDEE parameters."""

from typing import Iterable

from interface.parameter_schema import RDEEParameterSchema


class ValidationError(Exception):
    """Raised when parameter combinations violate physical constraints."""


def _ensure_in_range(value: float, min_value: float, max_value: float, name: str) -> None:
    """Helper to validate that a numeric value lies within a closed interval."""
    if value < min_value or value > max_value:
        raise ValidationError(f"{name} must be between {min_value} and {max_value}, got {value}.")


def validate_physical_constraints(parameters: RDEEParameterSchema) -> bool:
    """Validate cross-parameter physical feasibility constraints.

    Parameters
    ----------
    parameters:
        Populated :class:`RDEEParameterSchema` with parameter values stored in
        each ``ParameterSpec.default`` field.

    Returns
    -------
    bool
        ``True`` if all constraints pass. Raises :class:`ValidationError` on
        violations.
    """

    # Stellar constraints
    stellar_mass = parameters.stellar.stellar_mass.default
    if stellar_mass is None:
        raise ValidationError("Stellar mass must be provided.")
    _ensure_in_range(stellar_mass, 0.1, 100.0, "Stellar mass")

    stellar_metallicity = parameters.stellar.stellar_metallicity.default
    if stellar_metallicity is None:
        raise ValidationError("Stellar metallicity must be provided.")
    _ensure_in_range(stellar_metallicity, 0.0001, 0.03, "Stellar metallicity")

    # Habitability constraints
    planet_distance = parameters.planetary.planet_distance.default
    if planet_distance is None:
        raise ValidationError("Planet distance must be provided.")

    zone_range = parameters.habitability.liquid_water_zone_range.default
    if zone_range is not None:
        if isinstance(zone_range, Iterable) and not isinstance(zone_range, (str, bytes)):
            zone = list(zone_range)
            if len(zone) != 2:
                raise ValidationError(
                    "Liquid water zone range must contain two values: (min, max)."
                )
            zone_min, zone_max = zone
        elif isinstance(zone_range, (int, float)):
            zone_min, zone_max = 0.0, float(zone_range)
        else:
            raise ValidationError(
                "Liquid water zone range must be a float or an iterable of two floats."
            )
        if planet_distance < zone_min or planet_distance > zone_max:
            raise ValidationError("Planet distance is outside the liquid water zone range.")

    tidal_lock_prob = parameters.habitability.tidal_locking_probability.default
    if tidal_lock_prob is None:
        raise ValidationError("Tidal locking probability must be provided.")
    _ensure_in_range(tidal_lock_prob, 0.0, 1.0, "Tidal locking probability")

    # Evolutionary constraints
    evo_fragility = parameters.evolutionary.evolutionary_fragility_multiplier.default
    if evo_fragility is None:
        raise ValidationError("Evolutionary fragility multiplier must be provided.")
    _ensure_in_range(evo_fragility, 0.0, 1.0, "Evolutionary fragility multiplier")

    polymer_failure = parameters.prebiotic.polymerization_failure_rate.default
    if polymer_failure is None:
        raise ValidationError("Polymerization failure rate must be provided.")
    _ensure_in_range(polymer_failure, 0.0, 1.0, "Polymerization failure rate")

    # Sampling constraints
    depth_limit = parameters.sampling.recursive_depth_limit.default
    if depth_limit is None:
        raise ValidationError("Recursive depth limit must be provided.")
    if not isinstance(depth_limit, int) or depth_limit <= 0:
        raise ValidationError("Recursive depth limit must be a positive integer.")

    sensitivity_window = parameters.sampling.survival_corridor_sensitivity_window.default
    if sensitivity_window is not None:
        if not isinstance(sensitivity_window, (int, float)) or sensitivity_window < 0:
            raise ValidationError(
                "Survival corridor sensitivity window must be a non-negative float if defined."
            )

    return True
