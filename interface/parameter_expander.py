from __future__ import annotations

"""Utilities for expanding parameter sweep configurations."""

from copy import deepcopy
from dataclasses import replace
from itertools import product
from typing import Any, List

from .parameter_schema import RDEEParameterSchema, ParameterSpec


def get_nested_field(dataclass_obj: Any, field_path: str) -> Any:
    """Retrieve a nested field value from a dataclass via dot notation.

    Parameters
    ----------
    dataclass_obj : Any
        The dataclass instance to traverse.
    field_path : str
        Dot separated path of attributes to access.

    Returns
    -------
    Any
        The value at the specified location.

    Raises
    ------
    AttributeError
        If any component of the path does not exist.
    """
    current = dataclass_obj
    for part in field_path.split('.'):
        if not hasattr(current, part):
            msg = f"Invalid field path '{field_path}' at '{part}'"
            raise AttributeError(msg)
        current = getattr(current, part)
    return current


def set_nested_field(dataclass_obj: Any, field_path: str, value: Any) -> None:
    """Set a nested field on a dataclass via dot notation.

    If the terminal attribute resolves to a ``ParameterSpec`` instance and the
    path does not explicitly specify one of its attributes, the ``default``
    attribute of that ``ParameterSpec`` will be updated.

    Parameters
    ----------
    dataclass_obj : Any
        Dataclass instance to update.
    field_path : str
        Dot separated attribute path.
    value : Any
        Value to assign.

    Raises
    ------
    AttributeError
        If any component of the path does not exist.
    """
    parts = field_path.split('.')
    current = dataclass_obj
    for idx, part in enumerate(parts):
        is_last = idx == len(parts) - 1
        if not hasattr(current, part):
            msg = f"Invalid field path '{field_path}' at '{part}'"
            raise AttributeError(msg)
        if is_last:
            attr = getattr(current, part)
            if isinstance(attr, ParameterSpec) and len(parts) - idx == 1:
                setattr(current, part, replace(attr, default=value))
            else:
                setattr(current, part, value)
        else:
            current = getattr(current, part)


def generate_parameter_grid(
    base_schema: RDEEParameterSchema, sweep_config: dict
) -> List[RDEEParameterSchema]:
    """Generate a list of schemas for all combinations in ``sweep_config``.

    Parameters
    ----------
    base_schema : RDEEParameterSchema
        Starting schema providing default values.
    sweep_config : dict
        Mapping of parameter paths to lists of values to sweep.

    Returns
    -------
    list[RDEEParameterSchema]
        Schema instances populated with each combination of sweep values.
    """
    if not sweep_config:
        return [deepcopy(base_schema)]

    param_paths = list(sweep_config.keys())
    value_lists = [sweep_config[path] for path in param_paths]

    grid: List[RDEEParameterSchema] = []
    for combo in product(*value_lists):
        schema_copy = deepcopy(base_schema)
        for path, val in zip(param_paths, combo):
            set_nested_field(schema_copy, path, val)
        grid.append(schema_copy)

    return grid
