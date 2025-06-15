"""Data pipeline utilities for simulation run storage."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass, fields
from typing import Any, Dict, Tuple, Type, TypeVar
import dataclasses
import os
import json
import h5py
import interface.parameter_schema as schema_module

from interface.parameter_schema import RDEEParameterSchema, ParameterSpec

T = TypeVar("T")


def _string_to_type(name: str) -> Type[Any]:
    """Map a stored type name back to the Python type object."""
    mapping = {"float": float, "int": int, "str": str, "bool": bool}
    return mapping.get(name, str)


def _spec_to_dict(spec: ParameterSpec) -> dict:
    """Convert :class:`ParameterSpec` to a JSON-friendly dictionary."""
    d = dataclasses.asdict(spec)
    d["dtype"] = spec.dtype.__name__
    return d


def _schema_to_dict(obj: Any) -> Any:
    """Recursively convert nested dataclasses to dictionaries."""
    if is_dataclass(obj):
        if isinstance(obj, ParameterSpec):
            return _spec_to_dict(obj)
        return {f.name: _schema_to_dict(getattr(obj, f.name)) for f in fields(obj)}
    return obj


def _dataclass_to_dict(obj: Any) -> Dict[str, Any]:
    """Backward-compatible wrapper for dataclass conversion."""
    if not is_dataclass(obj):
        raise TypeError("Object for serialization must be a dataclass instance")
    return _schema_to_dict(obj)


def _dict_to_schema(d: Dict[str, Any]) -> RDEEParameterSchema:
    """Convert a dictionary back into :class:`RDEEParameterSchema`."""

    def _build(cls: Type[Any], data: Dict[str, Any]) -> Any:
        if cls is ParameterSpec:
            conv = dict(data)
            dt = conv.get("dtype")
            if isinstance(dt, str):
                conv["dtype"] = _string_to_type(dt)
            return ParameterSpec(**conv)
        kwargs: Dict[str, Any] = {}
        for f in fields(cls):
            value = data.get(f.name)
            field_type = f.type
            if isinstance(field_type, str):
                field_type = getattr(schema_module, field_type, None)
            if field_type and is_dataclass(field_type):
                kwargs[f.name] = _build(field_type, value)
            else:
                kwargs[f.name] = value
        return cls(**kwargs)

    return _build(RDEEParameterSchema, d)


def _dict_to_dataclass(data: Dict[str, Any], cls: Type[T]) -> T:
    """Backward-compatible wrapper for dataclass reconstruction."""
    return _dict_to_schema(data)  # type: ignore[return-value]


def _write_json_dataset(group: h5py.Group, name: str, obj: Any) -> None:
    """Write a JSON-serialized representation of ``obj`` to ``name``."""
    json_str = json.dumps(obj)
    dtype = h5py.string_dtype(encoding="utf-8")
    group.create_dataset(name, data=json_str, dtype=dtype)


def _read_json_dataset(group: h5py.Group, name: str) -> Any:
    """Read a JSON-serialized object stored under ``name``."""
    data = group[name][()]
    if isinstance(data, bytes):
        data = data.decode("utf-8")
    return json.loads(data)


def _schema_dict_to_object(d: Dict[str, Any]) -> RDEEParameterSchema:
    """Rebuild ``RDEEParameterSchema`` from a plain dictionary."""
    return _dict_to_dataclass(d, RDEEParameterSchema)


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

    param_dict = _schema_to_dict(parameters)
    param_json = json.dumps(param_dict)
    result_json = json.dumps(result)

    with h5py.File(file_path, "w") as h5f:
        trace = h5f.create_group("trace")
        trace.attrs["schema_version"] = "1"
        dtype = h5py.string_dtype("utf-8")
        trace.create_dataset("parameters_json", data=param_json, dtype=dtype)
        trace.create_dataset("result_json", data=result_json, dtype=dtype)


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
        trace = h5f["trace"]
        param_data = trace["parameters_json"][()]
        result_data = trace["result_json"][()]

    if isinstance(param_data, bytes):
        param_data = param_data.decode("utf-8")
    if isinstance(result_data, bytes):
        result_data = result_data.decode("utf-8")

    param_dict = json.loads(param_data)
    result = json.loads(result_data)

    parameters = _dict_to_schema(param_dict)
    return parameters, result
