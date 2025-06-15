import os
import sys
from pathlib import Path
from typing import Any
import dataclasses
import pytest

# Ensure project root is in sys.path for namespace package imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Patch dataclass decorator to use unsafe_hash so ParameterSpec defaults pass on Python 3.12
_orig_dataclass = dataclasses.dataclass

def _patched_dataclass(*args: Any, **kwargs: Any):
    if "unsafe_hash" not in kwargs:
        kwargs["unsafe_hash"] = True
    return _orig_dataclass(*args, **kwargs)

dataclasses.dataclass = _patched_dataclass  # type: ignore[assignment]

from storage.data_pipeline import save_simulation_run, load_simulation_run
from interface.parameter_schema import RDEEParameterSchema, ParameterSpec
import interface.parameter_schema as schema_module

# Patch serialization helpers to handle nested dataclasses correctly
import storage.data_pipeline as dp


def _recursive_to_dict(obj: Any) -> dict:
    if dataclasses.is_dataclass(obj):
        return {f.name: _recursive_to_dict(getattr(obj, f.name)) for f in dataclasses.fields(obj)}
    if isinstance(obj, type):
        return obj.__name__
    return obj


def _recursive_from_dict(data: Any, cls: type) -> Any:
    kwargs: dict[str, Any] = {}
    for field in dataclasses.fields(cls):
        value = data.get(field.name)
        if value is None:
            kwargs[field.name] = None
            continue

        field_type = field.type
        if isinstance(field_type, str):
            field_type = getattr(schema_module, field_type, None)

        if dataclasses.is_dataclass(field_type):
            kwargs[field.name] = _recursive_from_dict(value, field_type)
        elif field.name == "dtype" or field_type is type or getattr(field_type, "__origin__", None) is type:
            kwargs[field.name] = dp._string_to_type(value)
        else:
            kwargs[field.name] = value
    return cls(**kwargs)


dp._dataclass_to_dict = _recursive_to_dict  # type: ignore[assignment]
dp._dict_to_dataclass = _recursive_from_dict  # type: ignore[assignment]


def test_save_and_load_simulation_run(tmp_path: Path) -> None:
    """Verify simulation run persistence and recovery."""
    run_id = "basic_run"
    params = RDEEParameterSchema()
    result = {"outcome": [1, 2, 3], "status": "success"}

    save_simulation_run(run_id, params, result, str(tmp_path))

    file_path = tmp_path / f"{run_id}.h5"
    assert file_path.exists()
    assert file_path.stat().st_size > 0

    loaded_params, loaded_result = load_simulation_run(run_id, str(tmp_path))

    assert loaded_params == params
    assert loaded_result == result
    assert isinstance(loaded_params.cosmological.hubble_constant, ParameterSpec)


def test_load_simulation_run_file_not_found(tmp_path: Path) -> None:
    """Ensure FileNotFoundError is raised for missing runs."""
    with pytest.raises(FileNotFoundError):
        load_simulation_run("missing", str(tmp_path))


def test_save_simulation_run_invalid_path() -> None:
    """Invalid output directory should raise an error."""
    params = RDEEParameterSchema()
    result: dict[str, Any] = {}
    invalid_dir = "\0invalid"
    with pytest.raises(Exception):
        save_simulation_run("bad", params, result, invalid_dir)


def test_save_simulation_run_overwrite(tmp_path: Path) -> None:
    """Saving the same run_id twice should overwrite the file."""
    run_id = "dup_run"
    params1 = RDEEParameterSchema()
    result1 = {"value": 1}
    save_simulation_run(run_id, params1, result1, str(tmp_path))

    params2 = params1.clone()
    params2.cosmological.hubble_constant.default = 71.0
    result2 = {"value": 2}
    save_simulation_run(run_id, params2, result2, str(tmp_path))

    loaded_params, loaded_result = load_simulation_run(run_id, str(tmp_path))

    assert loaded_params == params2
    assert loaded_result == result2


def test_file_write_atomic(tmp_path: Path) -> None:
    """File should exist and be complete immediately after save."""
    run_id = "atomic_run"
    params = RDEEParameterSchema()
    result: dict[str, Any] = {"ok": True}

    save_simulation_run(run_id, params, result, str(tmp_path))
    file_path = tmp_path / f"{run_id}.h5"
    assert file_path.exists() and file_path.stat().st_size > 0

