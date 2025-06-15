from __future__ import annotations

"""Master batch orchestration controller for RDEE."""

from dataclasses import dataclass
from typing import List
from uuid import uuid4

from interface.parameter_schema import RDEEParameterSchema
from orchestration import sampling_adapter, validator_adapter, run_manager, execution_monitor
from storage import data_pipeline


@dataclass
class BatchContext:
    """Context object holding batch execution state."""

    output_dir: str
    monitor: execution_monitor.ExecutionMonitor


def execute_batch_unit(parameters: RDEEParameterSchema, output_dir: str, monitor: execution_monitor.ExecutionMonitor) -> None:
    """Execute one simulation cycle for ``parameters`` and update ``monitor``.

    Parameters
    ----------
    parameters:
        Validated :class:`RDEEParameterSchema` instance to simulate.
    output_dir:
        Directory where simulation results will be stored.
    monitor:
        Execution monitor instance to update with run status.
    """

    success = False
    try:
        validator_adapter.validate_full_parameters(parameters)
        result = run_manager.execute_simulation_run(parameters)
        run_id = result.get("trace_id", uuid4().hex)
        data_pipeline.save_simulation_run(run_id, parameters, result, output_dir)
        success = True
    except Exception:
        success = False
    finally:
        try:
            monitor.register_run(success)
        except Exception:
            pass


def run_full_batch(batch_size: int, sample_config: dict, output_dir: str) -> None:
    """Run a full batch of recursive simulations deterministically.

    Parameters
    ----------
    batch_size:
        Number of parameter samples to generate and execute.
    sample_config:
        Configuration dictionary forwarded to the sampling adapter.
    output_dir:
        Path to the directory for persisted run outputs.
    """

    monitor = execution_monitor.ExecutionMonitor()
    if hasattr(monitor, "set_batch_id"):
        try:
            monitor.set_batch_id(batch_size)
        except Exception:
            pass

    try:
        samples: List[RDEEParameterSchema] = sampling_adapter.generate_batch_samples(batch_size, sample_config)
    except Exception:
        samples = []

    for sample in samples:
        execute_batch_unit(sample, output_dir, monitor)

