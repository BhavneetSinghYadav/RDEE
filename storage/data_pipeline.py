"""Data pipeline utilities for simulation run storage."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass, fields
from typing import Any, Dict, Tuple, Type, TypeVar
import os
import json
import h5py

from interface.parameter_schema import RDEEParameterSchema, ParameterSpec

T = TypeVar("T")


def _type_to_string(tp: Type[Any]) -> str:
    """Convert a Python type to its string representation."""
    return tp.__name__


def _string_to_type(name: str) -> Type[Any]:
    """Map a stored type name back to the Python type object."""
    mapping = {"float": float, "int": int, "str": str, "bool": bool}
    return mapping.get(name, str)


def _dataclass_to_dict(obj: Any) -> Dict[str, Any]:
    """Convert dataclass object to a fully serializable dictionary."""
    if not is_dataclass(obj):
        raise TypeError("Object for serialization must be a dataclass instance")

    def _convert(value: Any) -> Any:
        if is_dataclass(value):
            return {k: _convert(v) for k, v in asdict(value).items()}
        if isinstance(value, type):
            return _type_to_string(value)
        return value

    return {k: _convert(v) for k, v in asdict(obj).items()}


def _dict_to_dataclass(data: Dict[str, Any], cls: Type[T]) -> T:
    """Reconstruct dataclass `cls` from dictionary data."""
    kwargs: Dict[str, Any] = {}
    for field in fields(cls):
        value = data.get(field.name)
        if value is None:
            kwargs[field.name] = None
            continue
        if is_dataclass(field.type):
            kwargs[field.name] = _dict_to_dataclass(value, field.type)  # type: ignore[arg-type]
        elif field.type is Type[Any] or field.type is type:
            kwargs[field.name] = _string_to_type(value)
        else:
            kwargs[field.name] = value
    return cls(**kwargs)  # type: ignore[return-value]


def _write_json_dataset(group: h5py.Group, name: str, obj: Any) -> None:
    """Helper to write JSON-serialized object to dataset."""
    json_str = json.dumps(obj)
    dtype = h5py.string_dtype(encoding="utf-8")
    group.create_dataset(name, data=json_str, dtype=dtype)


def _read_json_dataset(group: h5py.Group, name: str) -> Any:
    """Helper to read JSON-serialized object from dataset."""
    data = group[name][()]
    if isinstance(data, bytes):
        data = data.decode("utf-8")
    return json.loads(data)


def save_simulation_run(
    run_id: str,
    parameters: RDEEParameterSchema,
    result: dict,
    output_dir: str,
) -> None:
    """Save a simulation run to an HDF5 file.

    Parameters
    ----------
    run_id : str
        Unique identifier for the simulation run.
    parameters : RDEEParameterSchema
        Parameter schema used for the run.
    result : dict
        Resulting output from the simulation.
    output_dir : str
        Directory where the HDF5 file will be stored.
    """
    if not run_id:
        raise ValueError("run_id must be a non-empty string")

    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{run_id}.h5")

    param_dict = _dataclass_to_dict(parameters)

    with h5py.File(file_path, "w") as h5f:
        _write_json_dataset(h5f, "parameters", param_dict)
        _write_json_dataset(h5f, "result", result)


def load_simulation_run(run_id: str, output_dir: str) -> Tuple[RDEEParameterSchema, dict]:
    """Load a simulation run from disk.

    Parameters
    ----------
    run_id : str
        Identifier of the run to load.
    output_dir : str
        Directory containing the HDF5 file.

    Returns
    -------
    Tuple[RDEEParameterSchema, dict]
        Reconstructed parameter schema and simulation result.
    """
    file_path = os.path.join(output_dir, f"{run_id}.h5")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Simulation run file '{file_path}' does not exist")

    with h5py.File(file_path, "r") as h5f:
        param_dict = _read_json_dataset(h5f, "parameters")
        result = _read_json_dataset(h5f, "result")

    parameters = _dict_to_dataclass(param_dict, RDEEParameterSchema)
    return parameters, result
