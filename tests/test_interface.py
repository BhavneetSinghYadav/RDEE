import io
from pathlib import Path
from typing import Any, Dict

import pytest

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
    clone.stellar.stellar_mass.default = 2.5
    assert schema.stellar.stellar_mass.default == 1.0
    assert clone.stellar.stellar_mass.default == 2.5


def test_schema_instances_are_independent() -> None:
    first = RDEEParameterSchema()
    second = RDEEParameterSchema()
    first.cosmological.hubble_constant.default = 65.0
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
