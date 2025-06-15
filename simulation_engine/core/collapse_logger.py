# collapse_logger.py

"""Survival trace logging utilities for the RDEE simulation core."""

from __future__ import annotations

from dataclasses import is_dataclass, fields
from typing import Any, Dict, List, Optional
import copy
import uuid

from interface.parameter_schema import RDEEParameterSchema


def generate_trace_id() -> str:
    """Generate a unique identifier for a trace object."""
    return str(uuid.uuid4())


def _serialize(obj: Any) -> Any:
    """Recursively convert dataclasses to dictionaries."""
    if is_dataclass(obj):
        return {f.name: _serialize(getattr(obj, f.name)) for f in fields(obj)}
    if isinstance(obj, type):
        return obj.__name__
    return copy.deepcopy(obj)


def serialize_parameters(parameters: RDEEParameterSchema) -> Dict[str, Any]:
    """Flatten a :class:`RDEEParameterSchema` into a plain dictionary.

    Parameters
    ----------
    parameters : RDEEParameterSchema
        Parameter schema to serialize.

    Returns
    -------
    dict
        Fully expanded dictionary representation of ``parameters``.
    """
    if not is_dataclass(parameters):
        raise TypeError("parameters must be a dataclass instance")
    return _serialize(parameters)


def initialize_trace(parameters: RDEEParameterSchema) -> Dict[str, Any]:
    """Create a new survival trace object.

    Parameters
    ----------
    parameters : RDEEParameterSchema
        Parameter schema for the simulation run.

    Returns
    -------
    dict
        Initialized trace dictionary with a unique ID and serialized parameters.
    """
    trace = {
        "trace_id": generate_trace_id(),
        "parameters": serialize_parameters(parameters),
        "recursion_depth": 0,
        "path": [],
    }
    return trace


def record_stage(trace: Dict[str, Any], stage: str, result: bool) -> None:
    """Record a survival stage result in the trace.

    Parameters
    ----------
    trace : dict
        Existing trace dictionary to update.
    stage : str
        Name of the stage being recorded.
    result : bool
        Outcome of the stage (``True`` if survived, ``False`` if collapsed).
    """
    path: List[Dict[str, Any]] = trace.setdefault("path", [])
    path.append({"stage": stage, "result": result})


def increment_depth(trace: Dict[str, Any]) -> None:
    """Increment the recursion depth counter for ``trace``."""
    trace["recursion_depth"] = trace.get("recursion_depth", 0) + 1


def finalize_trace(trace: Dict[str, Any], final_survival: bool) -> None:
    """Finalize a trace with survival outcome information.

    Parameters
    ----------
    trace : dict
        Trace dictionary to finalize.
    final_survival : bool
        ``True`` if the simulation survived all stages; ``False`` otherwise.
    """
    trace["final_survival"] = final_survival
    collapse_stage: Optional[str] = None
    if not final_survival:
        for entry in trace.get("path", []):
            if not entry.get("result", True):
                collapse_stage = entry.get("stage")
                break
    trace["collapse_stage"] = collapse_stage

