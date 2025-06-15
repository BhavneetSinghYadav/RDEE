import io
from pathlib import Path
from typing import Any, Dict

import sys
import types
import pathlib
from dataclasses import dataclass, field
from typing import Optional, Type

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
    cosmological_constant: ParameterSpec = field(default_factory=lambda: spec("Cosmological Constant", float, "1/s²", 1e-56, 1e-52, 1e-54))
    baryon_to_photon_ratio: ParameterSpec = field(default_factory=lambda: spec("Baryon-to-photon ratio", float, "dimensionless", 1e-10, 1e-9, 6e-10))

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
import pytest
from dataclasses import replace

from interface.parameter_schema import ParameterSpec, RDEEParameterSchema
from interface.user_input import load_user_parameters, recursive_update
from interface.parameter_expander import generate_parameter_grid


class DummyPath(Path):
    """Path subclass returning predefined in-memory file data."""

    _flavour = type(Path())._flavour

    def __new__(cls, path: str, *, data: str) -> "DummyPath":
        obj = super().__new__(cls, path)
        obj._data = data
        return obj

    def is_file(self) -> bool:  # type: ignore[override]
        return True

    def open(self, mode: str = "r", encoding: str | None = None):  # type: ignore[override]
        return io.StringIO(self._data)


def test_schema_instantiation_and_defaults() -> None:
    schema = RDEEParameterSchema()
    assert isinstance(schema.cosmological.hubble_constant, ParameterSpec)
    assert schema.cosmological.hubble_constant.default == 70.0
    assert schema.stellar.stellar_mass.default == 1.0
    assert schema.sampling.recursive_depth_limit.default == 1


def test_schema_clone_independence() -> None:
    schema = RDEEParameterSchema()
    clone = schema.clone()
    clone.stellar.stellar_mass = replace(
        clone.stellar.stellar_mass, default=2.5
    )
    assert schema.stellar.stellar_mass.default == 1.0
    assert clone.stellar.stellar_mass.default == 2.5


def test_schema_instances_are_independent() -> None:
    first = RDEEParameterSchema()
    second = RDEEParameterSchema()
    first.cosmological.hubble_constant = replace(
        first.cosmological.hubble_constant, default=65.0
    )
    assert second.cosmological.hubble_constant.default == 70.0


def test_recursive_update_partial_and_full(monkeypatch: pytest.MonkeyPatch) -> None:
    yaml_data = "cosmological:\n  hubble_constant: 72.0\n"
    dummy = DummyPath("config.yaml", data=yaml_data)
    monkeypatch.setattr(Path, "__new__", lambda cls, path: dummy)
    schema = load_user_parameters("config.yaml")
    assert schema.cosmological.hubble_constant.default == 72.0
    assert schema.stellar.stellar_mass.default == 1.0

    full_dict: Dict[str, Any] = {
        "cosmological": {
            "hubble_constant": 68.0,
            "cosmological_constant": 1e-53,
            "baryon_to_photon_ratio": 5e-10,
        },
        "stellar": {"stellar_metallicity": 0.02, "stellar_mass": 0.9},
        "planetary": {
            "planet_mass": 2.0,
            "planet_distance": 2.5,
            "planetary_system_multiplicity": 3,
        },
        "habitability": {
            "liquid_water_zone_range": 1.0,
            "stellar_uv_flux_range": 2.0,
            "tidal_locking_probability": 0.2,
        },
        "prebiotic": {
            "prebiotic_synthesis_success_probability": 0.9,
            "uv_catalysis_efficiency": 0.7,
            "polymerization_failure_rate": 0.05,
        },
        "evolutionary": {
            "evolutionary_complexity_threshold": 8,
            "evolutionary_fragility_multiplier": 0.6,
            "mass_extinction_frequency": 2.0,
        },
        "sampling": {
            "recursive_depth_limit": 4,
            "survival_corridor_sensitivity_window": 0.1,
        },
    }
    recursive_update(schema, full_dict)
    assert schema.stellar.stellar_mass.default == 0.9
    assert schema.planetary.planet_mass.default == 2.0
    assert schema.habitability.tidal_locking_probability.default == 0.2


def test_recursive_update_type_and_key_errors() -> None:
    schema = RDEEParameterSchema()
    with pytest.raises(KeyError):
        recursive_update(schema, {"unknown_group": {"value": 1}})
    with pytest.raises(TypeError):
        recursive_update(schema, {"cosmological": {"hubble_constant": "bad"}})


def test_generate_parameter_grid_and_expansion() -> None:
    base = RDEEParameterSchema()
    sweep = {
        "cosmological.hubble_constant": [60.0, 70.0],
        "stellar.stellar_mass": [0.8, 1.2],
    }
    grid = generate_parameter_grid(base, sweep)
    assert len(grid) == 4
    values = {g.cosmological.hubble_constant.default for g in grid}
    assert values == {60.0, 70.0}
    assert all(isinstance(g, RDEEParameterSchema) for g in grid)

from interface.earth_parameter_instance import get_earth_parameters


def test_get_earth_parameters() -> None:
    params = get_earth_parameters()
    assert isinstance(params, RDEEParameterSchema)
    assert params.cosmological.hubble_constant.default == 70.0
    assert params.cosmological.cosmological_constant.default == 1e-54
    assert params.stellar.stellar_mass.default == 1.0
    assert params.planetary.planet_distance.default == 1.0
    assert params.habitability.liquid_water_zone_range.min_value == 0.95
    assert params.habitability.liquid_water_zone_range.max_value == 1.37
    assert params.evolutionary.mass_extinction_frequency.default == 0.5
    assert params.sampling.recursive_depth_limit.default == 10
