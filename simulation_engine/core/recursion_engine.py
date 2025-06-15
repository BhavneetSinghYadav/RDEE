from __future__ import annotations

"""Recursion orchestration layer for RDEE."""

from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Callable, Iterable, List
from uuid import uuid4

from interface.parameter_schema import RDEEParameterSchema
from . import stage_handlers, survival_filter, collapse_logger, bifurcation_handler


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
    max_depth = current_parameters.sampling.recursive_depth_limit.default or 0
    stages: Iterable[tuple[str, Callable[[RDEEParameterSchema], bool]]] = getattr(
        stage_handlers, "STAGE_HANDLERS", {}
    ).items()

    for name, handler in stages:
        try:
            survived = bool(handler(current_parameters))
        except Exception:
            survived = False
        record_trace(trace, name, survived)
        if terminate_if_collapse(name, survived):
            if hasattr(collapse_logger, "log_collapse"):
                try:
                    collapse_logger.log_collapse(trace, name)
                except Exception:
                    pass
            return False
        if hasattr(survival_filter, "apply_survival_filter"):
            try:
                survival_filter.apply_survival_filter(name, survived, current_parameters)
            except Exception:
                pass

    if current_depth + 1 >= max_depth:
        return True

    children: List[RDEEParameterSchema]
    if hasattr(bifurcation_handler, "generate_branches"):
        try:
            children = list(
                bifurcation_handler.generate_branches(current_parameters, current_depth + 1)
            )
        except Exception:
            children = []
    else:
        children = []

    if not children:
        return recursive_step(current_depth + 1, current_parameters, trace)

    for child in children:
        recursive_step(current_depth + 1, child, trace)
    return True


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
    trace = initialize_trace_object(parameters)
    recursive_step(0, parameters, trace)
    return trace
