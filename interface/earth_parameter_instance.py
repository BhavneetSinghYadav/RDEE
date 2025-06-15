from __future__ import annotations

"""Predefined Earth parameter instance for RDEE."""

from dataclasses import replace

from .parameter_schema import RDEEParameterSchema


def get_earth_parameters() -> RDEEParameterSchema:
    """Return an Earth-specific :class:`RDEEParameterSchema`.

    The returned schema contains best-estimate values for all parameter groups
    representing the contemporary Earth system.
    """
    schema = RDEEParameterSchema()

    # Cosmological parameters
    schema.cosmological.hubble_constant = replace(
        schema.cosmological.hubble_constant, default=70.0
    )
    schema.cosmological.cosmological_constant = replace(
        schema.cosmological.cosmological_constant, default=1e-54
    )
    schema.cosmological.baryon_to_photon_ratio = replace(
        schema.cosmological.baryon_to_photon_ratio, default=6e-10
    )

    # Stellar parameters
    schema.stellar.stellar_mass = replace(
        schema.stellar.stellar_mass, default=1.0
    )
    schema.stellar.stellar_metallicity = replace(
        schema.stellar.stellar_metallicity, default=0.014
    )

    # Planetary parameters
    schema.planetary.planet_mass = replace(
        schema.planetary.planet_mass, default=1.0
    )
    schema.planetary.planet_distance = replace(
        schema.planetary.planet_distance, default=1.0
    )
    schema.planetary.planetary_system_multiplicity = replace(
        schema.planetary.planetary_system_multiplicity, default=1
    )

    # Habitability parameters
    zone = schema.habitability.liquid_water_zone_range
    schema.habitability.liquid_water_zone_range = replace(
        zone,
        default=1.0,
        min_value=0.95,
        max_value=1.37,
    )
    schema.habitability.stellar_uv_flux_range = replace(
        schema.habitability.stellar_uv_flux_range, default=1361.0
    )
    schema.habitability.tidal_locking_probability = replace(
        schema.habitability.tidal_locking_probability, default=0.0
    )

    # Prebiotic chemistry parameters
    schema.prebiotic.prebiotic_synthesis_success_probability = replace(
        schema.prebiotic.prebiotic_synthesis_success_probability, default=0.7
    )
    schema.prebiotic.uv_catalysis_efficiency = replace(
        schema.prebiotic.uv_catalysis_efficiency, default=0.6
    )
    schema.prebiotic.polymerization_failure_rate = replace(
        schema.prebiotic.polymerization_failure_rate, default=0.1
    )

    # Evolutionary parameters
    schema.evolutionary.evolutionary_complexity_threshold = replace(
        schema.evolutionary.evolutionary_complexity_threshold, default=5
    )
    schema.evolutionary.evolutionary_fragility_multiplier = replace(
        schema.evolutionary.evolutionary_fragility_multiplier, default=0.4
    )
    schema.evolutionary.mass_extinction_frequency = replace(
        schema.evolutionary.mass_extinction_frequency, default=0.5
    )

    # Sampling control parameters
    schema.sampling.recursive_depth_limit = replace(
        schema.sampling.recursive_depth_limit, default=10
    )
    schema.sampling.survival_corridor_sensitivity_window = replace(
        schema.sampling.survival_corridor_sensitivity_window, default=0.1
    )

    return schema
