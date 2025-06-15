"""Data pipeline utilities for persistent trace storage."""

from __future__ import annotations

import dataclasses
import json
import os
from dataclasses import fields, is_dataclass
from typing import Any, Dict, Type, TypeVar

import h5py

from interface.parameter_schema import ParameterSpec, RDEEParameterSchema
import interface.parameter_schema as schema_module

T = TypeVar("T")


def _string_to_type(name: str) -> Type[Any]:
    """Return Python type from its name."""
    mapping = {"float": float, "int": int, "str": str, "bool": bool}
    return mapping.get(name, str)


def _spec_to_dict(spec: ParameterSpec) -> dict:
    """Convert ``ParameterSpec`` to a serializable dictionary."""
    return {
        "name": spec.name,
        "dtype": spec.dtype.__name__,
        "units": spec.units,
        "min_value": spec.min_value,
        "max_value": spec.max_value,
        "default": spec.default,
    }


def _schema_to_dict(obj: Any) -> Any:
    """Recursively convert nested dataclasses to dictionaries."""
    if isinstance(obj, ParameterSpec):
        return _spec_to_dict(obj)
    if is_dataclass(obj):
        return {f.name: _schema_to_dict(getattr(obj, f.name)) for f in fields(obj)}
    return obj


def _dataclass_to_dict(obj: Any) -> Dict[str, Any]:
    """Compatibility wrapper delegating to :func:`_schema_to_dict`."""
    if not is_dataclass(obj):
        raise TypeError("Object for serialization must be a dataclass")
    return _schema_to_dict(obj)


def _dict_to_schema(data: Dict[str, Any]) -> RDEEParameterSchema:
    """Reconstruct :class:`RDEEParameterSchema` from a dictionary."""

    def _build(cls: Type[Any], fragment: Dict[str, Any]) -> Any:
        kwargs: Dict[str, Any] = {}
        for f in fields(cls):
            value = fragment.get(f.name)
            field_type = f.type
            if isinstance(field_type, str):
                field_type = getattr(schema_module, field_type, None)
            if field_type and dataclasses.is_dataclass(field_type):
                kwargs[f.name] = _build(field_type, value)
            elif f.name == "dtype" or field_type is type or getattr(field_type, "__origin__", None) is type:
                kwargs[f.name] = _string_to_type(value)
            else:
                kwargs[f.name] = value
        return cls(**kwargs)

    return _build(RDEEParameterSchema, data)


def _dict_to_dataclass(data: Dict[str, Any], cls: Type[T]) -> T:
    """Compatibility wrapper for deserialization."""
    if cls is not RDEEParameterSchema:
        raise TypeError("Only RDEEParameterSchema deserialization supported")
    return _dict_to_schema(data)  # type: ignore[return-value]


def save_simulation_run(run_id: str, parameters: RDEEParameterSchema, result: dict, output_dir: str) -> None:
    """Persist a simulation run to an HDF5 file."""
    if not run_id:
        raise ValueError("run_id must be provided")
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{run_id}.h5")

    try:
        param_json = json.dumps(_schema_to_dict(parameters))
    except Exception as exc:  # pragma: no cover - protective
        raise ValueError("Failed to serialize parameters") from exc
    try:
        result_json = json.dumps(result)
    except Exception as exc:  # pragma: no cover - protective
        raise ValueError("Failed to serialize result") from exc

    with h5py.File(file_path, "w") as h5f:
        trace = h5f.require_group("trace")
        trace.attrs["schema_version"] = "2"
        dtype = h5py.string_dtype("utf-8")
        trace.create_dataset("parameters_json", data=param_json, dtype=dtype)
        trace.create_dataset("result_json", data=result_json, dtype=dtype)


def load_simulation_run(filepath: str, output_dir: str | None = None) -> tuple[RDEEParameterSchema, dict]:
    """Load a simulation run from ``filepath``.

    Parameters
    ----------
    filepath:
        Path to the ``.h5`` file. When ``output_dir`` is provided, this
        argument is treated as ``run_id`` for backward compatibility.
    output_dir:
        Optional directory for legacy two-argument calls.
    """

    if output_dir is not None:
        filepath = os.path.join(output_dir, f"{filepath}.h5")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Simulation run '{filepath}' not found")

    with h5py.File(filepath, "r") as h5f:
        trace = h5f["trace"]
        param_raw = trace["parameters_json"][()]
        result_raw = trace["result_json"][()]

    param_str = param_raw.decode("utf-8") if isinstance(param_raw, bytes) else str(param_raw)
    result_str = result_raw.decode("utf-8") if isinstance(result_raw, bytes) else str(result_raw)

    try:
        param_dict = json.loads(param_str)
        result_dict = json.loads(result_str)
    except Exception as exc:  # pragma: no cover - protective
        raise ValueError("Failed to deserialize run data") from exc

    parameters = _dict_to_schema(param_dict)
    return parameters, result_dict
