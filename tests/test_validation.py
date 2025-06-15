"""Unit tests for RDEE validation layer."""

from __future__ import annotations

import sys
import types
import pathlib
from dataclasses import dataclass, field
from typing import Optional, Type

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@dataclass
class ParameterSpec:
    name: str
    dtype: Type
    units: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    default: Optional[float] = None


def spec(name: str, dtype: Type, units: str, min_v=None, max_v=None, default=None) -> ParameterSpec:
    return ParameterSpec(name, dtype, units, min_v, max_v, default)


@dataclass
class CosmologicalParameters:
    hubble_constant: ParameterSpec = field(default_factory=lambda: spec("Hubble Constant", float, "km/s/Mpc", 60.0, 75.0, 70.0))


@dataclass
class StellarParameters:
    stellar_metallicity: ParameterSpec = field(default_factory=lambda: spec("Stellar metallicity", float, "fraction", 0.0001, 0.03, 0.014))
    stellar_mass: ParameterSpec = field(default_factory=lambda: spec("Stellar mass", float, "Msun", 0.1, 100.0, 1.0))


@dataclass
class PlanetaryParameters:
    planet_mass: ParameterSpec = field(default_factory=lambda: spec("Planet mass", float, "Mearth", 0.1, 10.0, 1.0))
    planet_distance: ParameterSpec = field(default_factory=lambda: spec("Planet distance", float, "AU", 0.1, 10.0, 1.0))
    planetary_system_multiplicity: ParameterSpec = field(default_factory=lambda: spec("Planetary system multiplicity", int, "count", 1, 20, 1))


@dataclass
class HabitabilityParameters:
    liquid_water_zone_range: ParameterSpec = field(default_factory=lambda: spec("Liquid water zone range", float, "AU"))
    stellar_uv_flux_range: ParameterSpec = field(default_factory=lambda: spec("Stellar UV flux range", float, "W/m²"))
    tidal_locking_probability: ParameterSpec = field(default_factory=lambda: spec("Tidal locking probability", float, "probability", 0.0, 1.0, 0.5))


@dataclass
class PrebioticChemistryParameters:
    prebiotic_synthesis_success_probability: ParameterSpec = field(default_factory=lambda: spec("Prebiotic synthesis success probability", float, "probability", 0.001, 1.0, 0.5))
    uv_catalysis_efficiency: ParameterSpec = field(default_factory=lambda: spec("UV catalysis efficiency", float, "probability", 0.0, 1.0, 0.5))
    polymerization_failure_rate: ParameterSpec = field(default_factory=lambda: spec("Polymerization failure rate", float, "probability", 0.0, 1.0, 0.1))


@dataclass
class EvolutionaryParameters:
    evolutionary_complexity_threshold: ParameterSpec = field(default_factory=lambda: spec("Evolutionary complexity threshold", int, "dimensionless", 1, 10, 5))
    evolutionary_fragility_multiplier: ParameterSpec = field(default_factory=lambda: spec("Evolutionary fragility multiplier", float, "multiplier", 0.0, 1.0, 0.5))
    mass_extinction_frequency: ParameterSpec = field(default_factory=lambda: spec("Mass extinction frequency", float, "events per 100 Myr"))


@dataclass
class SamplingControlParameters:
    recursive_depth_limit: ParameterSpec = field(default_factory=lambda: spec("Recursive depth limit", int, "count", None, None, 1))
    survival_corridor_sensitivity_window: ParameterSpec = field(default_factory=lambda: spec("Survival corridor sensitivity window", float, "unitless"))


@dataclass
class RDEEParameterSchema:
    cosmological: CosmologicalParameters = field(default_factory=CosmologicalParameters)
    stellar: StellarParameters = field(default_factory=StellarParameters)
    planetary: PlanetaryParameters = field(default_factory=PlanetaryParameters)
    habitability: HabitabilityParameters = field(default_factory=HabitabilityParameters)
    prebiotic: PrebioticChemistryParameters = field(default_factory=PrebioticChemistryParameters)
    evolutionary: EvolutionaryParameters = field(default_factory=EvolutionaryParameters)
    sampling: SamplingControlParameters = field(default_factory=SamplingControlParameters)

    def clone(self) -> "RDEEParameterSchema":
        import copy
        return copy.deepcopy(self)


stub = types.ModuleType("interface.parameter_schema")
stub.ParameterSpec = ParameterSpec
stub.CosmologicalParameters = CosmologicalParameters
stub.StellarParameters = StellarParameters
stub.PlanetaryParameters = PlanetaryParameters
stub.HabitabilityParameters = HabitabilityParameters
stub.PrebioticChemistryParameters = PrebioticChemistryParameters
stub.EvolutionaryParameters = EvolutionaryParameters
stub.SamplingControlParameters = SamplingControlParameters
stub.RDEEParameterSchema = RDEEParameterSchema
sys.modules["interface.parameter_schema"] = stub

from validation.constraints import ValidationError, validate_physical_constraints
from validation.sanity_checks import SanityCheckError, check_parameter_sanity
from validation.validator import ValidationPipelineError, validate_parameters


def valid_schema() -> RDEEParameterSchema:
    return RDEEParameterSchema().clone()


def test_constraints_valid() -> None:
    assert validate_physical_constraints(valid_schema()) is True


def test_constraints_stellar_mass() -> None:
    p = valid_schema()
    p.stellar.stellar_mass.default = 200.0
    with pytest.raises(ValidationError):
        validate_physical_constraints(p)


def test_constraints_stellar_metallicity() -> None:
    p = valid_schema()
    p.stellar.stellar_metallicity.default = 0.1
    with pytest.raises(ValidationError):
        validate_physical_constraints(p)


def test_constraints_habitable_zone() -> None:
    p = valid_schema()
    p.habitability.liquid_water_zone_range.default = (0.5, 1.5)
    p.planetary.planet_distance.default = 2.5
    with pytest.raises(ValidationError):
        validate_physical_constraints(p)


def test_constraints_tidal_locking() -> None:
    p = valid_schema()
    p.habitability.tidal_locking_probability.default = -0.1
    with pytest.raises(ValidationError):
        validate_physical_constraints(p)


def test_constraints_polymer_failure() -> None:
    p = valid_schema()
    p.prebiotic.polymerization_failure_rate.default = 1.5
    with pytest.raises(ValidationError):
        validate_physical_constraints(p)


def test_constraints_depth_limit() -> None:
    p = valid_schema()
    p.sampling.recursive_depth_limit.default = 0
    with pytest.raises(ValidationError):
        validate_physical_constraints(p)


def test_constraints_sensitivity_window() -> None:
    p = valid_schema()
    p.sampling.survival_corridor_sensitivity_window.default = -1.0
    with pytest.raises(ValidationError):
        validate_physical_constraints(p)


def test_sanity_valid() -> None:
    assert check_parameter_sanity(valid_schema()) is True


def test_sanity_multiplicity() -> None:
    p = valid_schema()
    p.planetary.planetary_system_multiplicity.default = 0
    with pytest.raises(SanityCheckError):
        check_parameter_sanity(p)


def test_sanity_synthesis_prob() -> None:
    p = valid_schema()
    p.prebiotic.prebiotic_synthesis_success_probability.default = 0.0
    with pytest.raises(SanityCheckError):
        check_parameter_sanity(p)


def test_sanity_complexity_threshold() -> None:
    p = valid_schema()
    p.evolutionary.evolutionary_complexity_threshold.default = 0
    with pytest.raises(SanityCheckError):
        check_parameter_sanity(p)


def test_sanity_distance_edge() -> None:
    p = valid_schema()
    p.habitability.liquid_water_zone_range.min_value = 0.5
    p.habitability.liquid_water_zone_range.max_value = 1.5
    p.planetary.planet_distance.default = 0.1
    with pytest.raises(SanityCheckError):
        check_parameter_sanity(p)


def test_sanity_negative_extinction() -> None:
    p = valid_schema()
    p.evolutionary.mass_extinction_frequency.default = -1.0
    with pytest.raises(SanityCheckError):
        check_parameter_sanity(p)


def test_validator_success() -> None:
    assert validate_parameters(valid_schema()) is True


def test_validator_constraint_fail() -> None:
    p = valid_schema()
    p.stellar.stellar_mass.default = 200.0
    with pytest.raises(ValidationPipelineError):
        validate_parameters(p)


def test_validator_sanity_fail() -> None:
    p = valid_schema()
    p.planetary.planetary_system_multiplicity.default = 0
    with pytest.raises(ValidationPipelineError):
        validate_parameters(p)


def test_validator_both_fail() -> None:
    p = valid_schema()
    p.stellar.stellar_mass.default = 200.0
    p.planetary.planetary_system_multiplicity.default = 0
    with pytest.raises(ValidationPipelineError) as exc:
        validate_parameters(p)
    assert len(exc.value.errors) == 2

