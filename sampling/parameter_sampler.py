from __future__ import annotations

"""Stochastic parameter sampling for RDEE."""

from dataclasses import replace
from typing import Optional

import numpy as np

from interface.parameter_schema import (
    ParameterSpec,
    RDEEParameterSchema,
)


class ParameterSampler:
    """Generate fully randomized :class:`RDEEParameterSchema` instances."""

    @staticmethod
    def _clip(value: float, spec: ParameterSpec) -> float:
        """Return ``value`` constrained to ``spec`` bounds."""
        if spec.min_value is not None:
            value = max(value, float(spec.min_value))
        if spec.max_value is not None:
            value = min(value, float(spec.max_value))
        return value

    @classmethod
    def _assign(cls, group: object, name: str, value: float) -> None:
        spec = getattr(group, name)
        clipped = cls._clip(value, spec)
        if spec.dtype is int:
            clipped = int(round(clipped))
        else:
            clipped = float(clipped)
        setattr(group, name, replace(spec, default=clipped))

    @staticmethod
    def generate_sample(seed: Optional[int] = None) -> RDEEParameterSchema:
        """Return a fully randomized ``RDEEParameterSchema``.

        Parameters
        ----------
        seed:
            Optional seed for deterministic sampling.
        """
        rng = np.random.default_rng(seed)
        schema = RDEEParameterSchema()

        cosmo = schema.cosmological
        ParameterSampler._assign(cosmo, "hubble_constant", rng.normal(70.0, 1.5))
        ParameterSampler._assign(
            cosmo,
            "cosmological_constant",
            rng.lognormal(mean=np.log(1e-54), sigma=0.1),
        )
        ParameterSampler._assign(
            cosmo,
            "baryon_to_photon_ratio",
            rng.normal(6e-10, 5e-11),
        )

        stellar = schema.stellar
        ParameterSampler._assign(stellar, "stellar_mass", rng.lognormal(np.log(1.0), 0.1))
        metallicity = rng.beta(2.0, 5.0) * (0.03 - 0.0001) + 0.0001
        ParameterSampler._assign(stellar, "stellar_metallicity", metallicity)

        planetary = schema.planetary
        ParameterSampler._assign(planetary, "planet_mass", rng.lognormal(np.log(1.0), 0.3))
        ParameterSampler._assign(planetary, "planet_distance", rng.uniform(0.8, 1.5))
        mult = rng.poisson(3.0)
        mult = max(1, min(20, mult))
        ParameterSampler._assign(planetary, "planetary_system_multiplicity", mult)

        habitability = schema.habitability
        ParameterSampler._assign(habitability, "liquid_water_zone_range", rng.uniform(0.95, 1.37))
        ParameterSampler._assign(habitability, "stellar_uv_flux_range", rng.normal(1361.0, 50.0))
        ParameterSampler._assign(habitability, "tidal_locking_probability", rng.uniform(0.0, 1.0))

        prebiotic = schema.prebiotic
        ParameterSampler._assign(prebiotic, "prebiotic_synthesis_success_probability", rng.beta(5.0, 3.0))
        ParameterSampler._assign(prebiotic, "uv_catalysis_efficiency", rng.beta(3.0, 3.0))
        ParameterSampler._assign(prebiotic, "polymerization_failure_rate", rng.beta(2.0, 5.0))

        evolutionary = schema.evolutionary
        ParameterSampler._assign(
            evolutionary,
            "evolutionary_complexity_threshold",
            rng.integers(3, 8),
        )
        ParameterSampler._assign(
            evolutionary,
            "evolutionary_fragility_multiplier",
            rng.beta(4.0, 3.0),
        )
        ParameterSampler._assign(
            evolutionary,
            "mass_extinction_frequency",
            rng.exponential(1.0 / 2.0),
        )

        sampling = schema.sampling
        ParameterSampler._assign(sampling, "recursive_depth_limit", 10)
        ParameterSampler._assign(
            sampling,
            "survival_corridor_sensitivity_window",
            rng.uniform(0.05, 0.2),
        )

        return schema
