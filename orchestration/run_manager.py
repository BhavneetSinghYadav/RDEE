from __future__ import annotations

"""Simulation run manager for the Orchestration Layer."""

from typing import Dict

from interface.parameter_schema import RDEEParameterSchema
from simulation_engine.core import collapse_logger, recursion_engine


def execute_simulation_run(parameters: RDEEParameterSchema) -> Dict[str, object]:
    """Execute a single simulation run and return its trace.

    Parameters
    ----------
    parameters : RDEEParameterSchema
        Parameter schema describing the simulation configuration.

    Returns
    -------
    dict
        Fully populated trace object capturing the simulation execution.
    """
    if not isinstance(parameters, RDEEParameterSchema):
        raise TypeError("parameters must be an RDEEParameterSchema instance")

    trace = collapse_logger.initialize_trace(parameters)

    recursion_trace = recursion_engine.run_recursive_simulation(parameters)

    for entry in recursion_trace.get("stages", []):
        stage = entry.get("stage", "")
        survived = bool(entry.get("survived"))
        collapse_logger.record_stage(trace, stage, survived)

    final_survival = all(entry.get("survived", False) for entry in recursion_trace.get("stages", []))

    collapse_logger.finalize_trace(trace, final_survival)

    return trace
