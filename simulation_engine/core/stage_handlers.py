from __future__ import annotations

"""Stage evaluation handlers implementing stochastic survival logic."""

from dataclasses import dataclass
import numpy as np

from interface.parameter_schema import RDEEParameterSchema
from simulation_engine.core.survival_filter import (
    threshold_pass,
    survival_window,
    scaled_fragility,
)


__all__ = [
    "evaluate_cosmological",
    "evaluate_stellar",
    "evaluate_planetary",
    "evaluate_habitability",
    "evaluate_prebiotic",
    "evaluate_evolutionary",
]


@dataclass(slots=True)
class _Range:
    """Internal helper for numeric ranges."""

    lower: float
    upper: float

    def contains(self, value: float) -> bool:
        """Return ``True`` if ``value`` lies within ``[lower, upper]``."""
        return threshold_pass(value, self.lower, self.upper)


# Predefined parameter ranges for deterministic checks
COSMOLOGY_RANGES = {
    "hubble_constant": _Range(60.0, 75.0),
    "cosmological_constant": _Range(1e-56, 1e-52),
    "baryon_to_photon_ratio": _Range(1e-10, 1e-9),
}

STELLAR_RANGES = {
    "stellar_mass": _Range(0.5, 1.5),
    "stellar_metallicity": _Range(0.001, 0.03),
}

PLANETARY_RANGES = {
    "planet_mass": _Range(0.5, 5.0),
    "planet_distance": _Range(0.7, 2.0),
}


def evaluate_cosmological(parameters: RDEEParameterSchema) -> bool:
    """Return ``True`` if cosmological constants fall within survival ranges."""

    cosmo = parameters.cosmological
    return (
        COSMOLOGY_RANGES["hubble_constant"].contains(cosmo.hubble_constant.default)
        and COSMOLOGY_RANGES["cosmological_constant"].contains(
            cosmo.cosmological_constant.default
        )
        and COSMOLOGY_RANGES["baryon_to_photon_ratio"].contains(
            cosmo.baryon_to_photon_ratio.default
        )
    )


def evaluate_stellar(parameters: RDEEParameterSchema) -> bool:
    """Return ``True`` if host star parameters are within survival ranges."""

    stellar = parameters.stellar
    return (
        STELLAR_RANGES["stellar_mass"].contains(stellar.stellar_mass.default)
        and STELLAR_RANGES["stellar_metallicity"].contains(
            stellar.stellar_metallicity.default
        )
    )


def evaluate_planetary(parameters: RDEEParameterSchema) -> bool:
    """Return ``True`` if planetary formation values fall within survival ranges."""

    planet = parameters.planetary
    multiplicity = planet.planetary_system_multiplicity.default
    return (
        PLANETARY_RANGES["planet_mass"].contains(planet.planet_mass.default)
        and PLANETARY_RANGES["planet_distance"].contains(planet.planet_distance.default)
        and multiplicity >= 1
    )


def evaluate_habitability(parameters: RDEEParameterSchema) -> bool:
    """Stochastically evaluate basic planetary habitability."""

    ref = parameters.planetary.planet_distance.default
    target = parameters.habitability.liquid_water_zone_range.default
    window = parameters.sampling.survival_corridor_sensitivity_window.default

    if None in (ref, target, window):
        return False

    habitable_window_score = survival_window(ref, target, window)
    survival_chance = float(habitable_window_score)
    return np.random.rand() < survival_chance


def evaluate_prebiotic(parameters: RDEEParameterSchema) -> bool:
    """Stochastically evaluate viability of prebiotic chemistry."""

    chem = parameters.prebiotic
    synth = chem.prebiotic_synthesis_success_probability.default
    uv_eff = chem.uv_catalysis_efficiency.default
    failure_rate = chem.polymerization_failure_rate.default

    composite_success = synth * uv_eff * (1.0 - failure_rate)
    composite_success = max(0.0, min(1.0, composite_success))
    return np.random.rand() < composite_success


def evaluate_evolutionary(parameters: RDEEParameterSchema) -> bool:
    """Stochastically evaluate evolutionary survival parameters."""

    evo = parameters.evolutionary
    complexity = evo.evolutionary_complexity_threshold.default
    fragility_factor = evo.evolutionary_fragility_multiplier.default
    extinction_freq = evo.mass_extinction_frequency.default or 0.0

    ok_complexity = complexity >= 3
    fragility_survival = 1.0 - fragility_factor
    ok_fragility = np.random.rand() < fragility_survival
    extinction_prob = 1.0 - np.exp(-extinction_freq / 100.0)
    ok_extinction = np.random.rand() > extinction_prob

    return ok_complexity and ok_fragility and ok_extinction
