from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Type
import copy


@dataclass(frozen=True, slots=True)
class ParameterSpec:
    """Metadata container for a simulation parameter."""

    name: str
    dtype: Type
    units: str
    min_value: Optional[float]
    max_value: Optional[float]
    default: Optional[float]


@dataclass
class CosmologicalParameters:
    """Cosmological constants controlling universe level behavior."""

    hubble_constant: ParameterSpec = ParameterSpec(
        name="Hubble Constant",
        dtype=float,
        units="km/s/Mpc",
        min_value=60.0,
        max_value=75.0,
        default=70.0,
    )
    cosmological_constant: ParameterSpec = ParameterSpec(
        name="Cosmological Constant",
        dtype=float,
        units="1/s²",
        min_value=1e-56,
        max_value=1e-52,
        default=1e-54,
    )
    baryon_to_photon_ratio: ParameterSpec = ParameterSpec(
        name="Baryon-to-photon ratio",
        dtype=float,
        units="dimensionless",
        min_value=1e-10,
        max_value=1e-9,
        default=6e-10,
    )


@dataclass
class StellarParameters:
    """Stellar formation variables for host stars."""

    stellar_metallicity: ParameterSpec = ParameterSpec(
        name="Stellar metallicity",
        dtype=float,
        units="fraction",
        min_value=0.0001,
        max_value=0.03,
        default=0.014,
    )
    stellar_mass: ParameterSpec = ParameterSpec(
        name="Stellar mass",
        dtype=float,
        units="Msun",
        min_value=0.1,
        max_value=100.0,
        default=1.0,
    )


@dataclass
class PlanetaryParameters:
    """Parameters governing initial planet formation."""

    planet_mass: ParameterSpec = ParameterSpec(
        name="Planet mass",
        dtype=float,
        units="Mearth",
        min_value=0.1,
        max_value=10.0,
        default=1.0,
    )
    planet_distance: ParameterSpec = ParameterSpec(
        name="Planet distance",
        dtype=float,
        units="AU",
        min_value=0.1,
        max_value=10.0,
        default=1.0,
    )
    planetary_system_multiplicity: ParameterSpec = ParameterSpec(
        name="Planetary system multiplicity",
        dtype=int,
        units="count",
        min_value=1,
        max_value=20,
        default=1,
    )


@dataclass
class HabitabilityParameters:
    """Variables determining potential planetary habitability."""

    liquid_water_zone_range: ParameterSpec = ParameterSpec(
        name="Liquid water zone range",
        dtype=float,
        units="AU",
        min_value=None,
        max_value=None,
        default=None,
    )
    stellar_uv_flux_range: ParameterSpec = ParameterSpec(
        name="Stellar UV flux range",
        dtype=float,
        units="W/m²",
        min_value=None,
        max_value=None,
        default=None,
    )
    tidal_locking_probability: ParameterSpec = ParameterSpec(
        name="Tidal locking probability",
        dtype=float,
        units="probability",
        min_value=0.0,
        max_value=1.0,
        default=0.5,
    )


@dataclass
class PrebioticChemistryParameters:
    """Chemical probabilities for prebiotic reactions."""

    prebiotic_synthesis_success_probability: ParameterSpec = ParameterSpec(
        name="Prebiotic synthesis success probability",
        dtype=float,
        units="probability",
        min_value=0.001,
        max_value=1.0,
        default=0.5,
    )
    uv_catalysis_efficiency: ParameterSpec = ParameterSpec(
        name="UV catalysis efficiency",
        dtype=float,
        units="probability",
        min_value=0.0,
        max_value=1.0,
        default=0.5,
    )
    polymerization_failure_rate: ParameterSpec = ParameterSpec(
        name="Polymerization failure rate",
        dtype=float,
        units="probability",
        min_value=0.0,
        max_value=1.0,
        default=0.1,
    )


@dataclass
class EvolutionaryParameters:
    """Parameters dictating evolutionary processes."""

    evolutionary_complexity_threshold: ParameterSpec = ParameterSpec(
        name="Evolutionary complexity threshold",
        dtype=int,
        units="dimensionless",
        min_value=1,
        max_value=10,
        default=5,
    )
    evolutionary_fragility_multiplier: ParameterSpec = ParameterSpec(
        name="Evolutionary fragility multiplier",
        dtype=float,
        units="multiplier",
        min_value=0.0,
        max_value=1.0,
        default=0.5,
    )
    mass_extinction_frequency: ParameterSpec = ParameterSpec(
        name="Mass extinction frequency",
        dtype=float,
        units="events per 100 Myr",
        min_value=None,
        max_value=None,
        default=None,
    )


@dataclass
class SamplingControlParameters:
    """Control parameters for recursive sampling."""

    recursive_depth_limit: ParameterSpec = ParameterSpec(
        name="Recursive depth limit",
        dtype=int,
        units="count",
        min_value=None,
        max_value=None,
        default=1,
    )
    survival_corridor_sensitivity_window: ParameterSpec = ParameterSpec(
        name="Survival corridor sensitivity window",
        dtype=float,
        units="unitless",
        min_value=None,
        max_value=None,
        default=None,
    )


@dataclass
class RDEEParameterSchema:
    """Root schema containing all parameter groups for RDEE."""

    cosmological: CosmologicalParameters = field(default_factory=CosmologicalParameters)
    stellar: StellarParameters = field(default_factory=StellarParameters)
    planetary: PlanetaryParameters = field(default_factory=PlanetaryParameters)
    habitability: HabitabilityParameters = field(default_factory=HabitabilityParameters)
    prebiotic: PrebioticChemistryParameters = field(default_factory=PrebioticChemistryParameters)
    evolutionary: EvolutionaryParameters = field(default_factory=EvolutionaryParameters)
    sampling: SamplingControlParameters = field(default_factory=SamplingControlParameters)

    def clone(self) -> "RDEEParameterSchema":
        """Return a deep-copy clone of the current parameter schema, safe for independent simulation mutation."""
        return copy.deepcopy(self)

