from __future__ import annotations

"""Recursive simulation engine implementing bifurcation logic for RDEE."""

from typing import Any, Dict, Callable, List

from interface.parameter_schema import RDEEParameterSchema
from simulation_engine.core import (
    stage_handlers,
    collapse_logger,
    bifurcation_handler,
)


def run_recursive_simulation(parameters: RDEEParameterSchema) -> Dict[str, Any]:
    """Run the full recursive simulation.

    Parameters
    ----------
    parameters:
        Root :class:`RDEEParameterSchema` defining the simulation configuration.

    Returns
    -------
    dict
        Fully populated trace object recording all stage outcomes.
    """

    trace = collapse_logger.initialize_trace(parameters)
    result = recursive_step(0, parameters, trace)
    collapse_logger.finalize_trace(trace, result)
    return trace


def recursive_step(
    current_depth: int,
    parameters: RDEEParameterSchema,
    trace: Dict[str, Any],
) -> bool:
    """Evaluate survival stages and branch recursively.

    Parameters
    ----------
    current_depth:
        Current recursion depth.
    parameters:
        Parameter schema for this branch of the recursion tree.
    trace:
        Trace dictionary capturing stage outcomes.

    Returns
    -------
    bool
        ``True`` if the branch survives through all required stages.
    """

    stages: List[tuple[str, Callable[[RDEEParameterSchema], bool]]] = [
        ("cosmological", stage_handlers.evaluate_cosmological),
        ("stellar", stage_handlers.evaluate_stellar),
        ("planetary", stage_handlers.evaluate_planetary),
        ("habitability", stage_handlers.evaluate_habitability),
        ("prebiotic", stage_handlers.evaluate_prebiotic),
        ("evolutionary", stage_handlers.evaluate_evolutionary),
    ]

    for stage_name, stage_func in stages:
        result = stage_func(parameters)
        collapse_logger.record_stage(trace, stage_name, result)
        if not result:
            return False

    collapse_logger.increment_depth(trace)

    depth_limit = parameters.sampling.recursive_depth_limit.default
    if current_depth + 1 >= depth_limit:
        return True

    children = bifurcation_handler.generate_bifurcations(
        parameters, branching_factor=2, perturbation_scale=0.05
    )

    return any(
        recursive_step(current_depth + 1, child, trace) for child in children
    )
