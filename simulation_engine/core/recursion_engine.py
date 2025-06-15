from __future__ import annotations

"""Recursion orchestration layer for RDEE."""

from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Callable, Iterable, List
from uuid import uuid4

from interface.parameter_schema import RDEEParameterSchema
from . import stage_handlers, collapse_logger, bifurcation_handler


def _serialize(obj: Any) -> Any:
    """Recursively serialize dataclass objects to primitives."""
    if is_dataclass(obj):
        return {k: _serialize(v) for k, v in asdict(obj).items()}
    if isinstance(obj, type):
        return obj.__name__
    if isinstance(obj, (list, tuple)):
        return [_serialize(v) for v in obj]
    return obj


def initialize_trace_object(parameters: RDEEParameterSchema) -> Dict[str, Any]:
    """Initialize a trace dictionary for a simulation run."""
    return {
        "trace_id": uuid4().hex,
        "parameters": _serialize(parameters),
        "stages": [],
    }


def record_trace(trace: Dict[str, Any], stage: str, survived: bool) -> None:
    """Record the survival result for a stage."""
    trace.setdefault("stages", []).append({"stage": stage, "survived": survived})


def terminate_if_collapse(stage: str, result: bool) -> bool:
    """Return ``True`` if recursion should collapse after ``stage``."""
    return not result


def recursive_step(
    current_depth: int, current_parameters: RDEEParameterSchema, trace: Dict[str, Any]
) -> bool:
    """Execute a single recursion step.

    Parameters
    ----------
    current_depth:
        Current recursion depth.
    current_parameters:
        Parameter schema for this branch.
    trace:
        Trace dictionary being populated.

    Returns
    -------
    bool
        ``True`` if the branch survives through all stages.
    """
    ordered_stages: List[tuple[str, Callable[[RDEEParameterSchema], bool]]] = [
        ("cosmological", stage_handlers.evaluate_cosmological),
        ("stellar", stage_handlers.evaluate_stellar),
        ("planetary", stage_handlers.evaluate_planetary),
        ("habitability", stage_handlers.evaluate_habitability),
        ("prebiotic", stage_handlers.evaluate_prebiotic),
        ("evolutionary", stage_handlers.evaluate_evolutionary),
    ]

    for name, func in ordered_stages:
        result = func(current_parameters)
        collapse_logger.record_stage(trace, name, result)
        if not result:
            return False

    depth_limit = current_parameters.sampling.recursive_depth_limit.default
    if current_depth + 1 >= depth_limit:
        return True

    collapse_logger.increment_depth(trace)
    children = bifurcation_handler.generate_bifurcations(
        current_parameters, branching_factor=2, perturbation_scale=0.05
    )
    return any(
        recursive_step(current_depth + 1, child, trace) for child in children
    )


def run_recursive_simulation(parameters: RDEEParameterSchema) -> Dict[str, Any]:
    """Run the full recursive simulation using ``parameters``.

    Parameters
    ----------
    parameters:
        Validated ``RDEEParameterSchema`` instance.

    Returns
    -------
    dict
        Trace dictionary containing survival information for all stages.
    """
    trace = collapse_logger.initialize_trace(parameters)
    survived = recursive_step(0, parameters, trace)
    collapse_logger.finalize_trace(trace, final_survival=survived)
    return trace
