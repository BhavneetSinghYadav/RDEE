"""User configuration loading utilities for RDEE."""

from __future__ import annotations

from dataclasses import is_dataclass
from pathlib import Path
from typing import Any

import json

import yaml

try:
    from .parameter_schema import ParameterSpec, RDEEParameterSchema
except ImportError:  # pragma: no cover - fallback when not a package
    from parameter_schema import ParameterSpec, RDEEParameterSchema


def recursive_update(dataclass_obj: Any, update_dict: dict) -> None:
    """Recursively update dataclass attributes from a dictionary.

    Parameters
    ----------
    dataclass_obj:
        Target dataclass instance to update.
    update_dict:
        Dictionary containing new values keyed by field names.

    Raises
    ------
    KeyError
        If a provided key does not exist on the dataclass.
    TypeError
        If provided values are of incorrect type and cannot be converted.
    ValueError
        If provided numeric values violate defined bounds.
    """

    for key, value in update_dict.items():
        if not hasattr(dataclass_obj, key):
            raise KeyError(f"Unknown parameter group or field: {key}")

        attr = getattr(dataclass_obj, key)

        if isinstance(attr, ParameterSpec):
            expected_type = attr.dtype
            try:
                cast_value = expected_type(value)
            except (TypeError, ValueError) as exc:  # incorrect cast
                raise TypeError(
                    f"Invalid type for parameter '{key}': expected {expected_type.__name__}"
                ) from exc

            if attr.min_value is not None and cast_value < attr.min_value:
                raise ValueError(
                    f"Value for '{key}' below minimum of {attr.min_value}"
                )
            if attr.max_value is not None and cast_value > attr.max_value:
                raise ValueError(
                    f"Value for '{key}' above maximum of {attr.max_value}"
                )

            attr.default = cast_value
        elif is_dataclass(attr):
            if not isinstance(value, dict):
                raise TypeError(
                    f"Expected mapping for parameter group '{key}', got {type(value).__name__}"
                )
            recursive_update(attr, value)
        else:
            try:
                cast_value = type(attr)(value)
            except (TypeError, ValueError) as exc:
                raise TypeError(
                    f"Invalid type for attribute '{key}': expected {type(attr).__name__}"
                ) from exc
            setattr(dataclass_obj, key, cast_value)


def load_user_parameters(file_path: str) -> RDEEParameterSchema:
    """Load and validate user configuration parameters.

    Parameters
    ----------
    file_path:
        Path to a YAML or JSON configuration file specifying parameter values.

    Returns
    -------
    RDEEParameterSchema
        Schema instance populated with user-specified values and defaults.

    Raises
    ------
    FileNotFoundError
        If ``file_path`` does not exist.
    ValueError
        If the file format is not supported or content is malformed.
    KeyError, TypeError
        Propagated from :func:`recursive_update` for invalid parameters.
    """

    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Parameter file not found: {file_path}")

    if path.suffix.lower() in {".yaml", ".yml"}:
        with path.open("r", encoding="utf-8") as fh:
            try:
                raw_data = yaml.safe_load(fh) or {}
            except yaml.YAMLError as exc:
                raise ValueError("Invalid YAML format") from exc
    elif path.suffix.lower() == ".json":
        with path.open("r", encoding="utf-8") as fh:
            try:
                raw_data = json.load(fh)
            except json.JSONDecodeError as exc:
                raise ValueError("Invalid JSON format") from exc
    else:
        raise ValueError("Unsupported configuration file type")

    if not isinstance(raw_data, dict):
        raise ValueError("Configuration file must define a mapping of parameters")

    schema = RDEEParameterSchema()
    recursive_update(schema, raw_data)
    return schema

