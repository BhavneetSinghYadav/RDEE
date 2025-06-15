from __future__ import annotations

"""Launcher for Earth parameter simulation batches."""

from uuid import uuid4

from interface.earth_parameter_instance import get_earth_parameters
from interface.parameter_schema import RDEEParameterSchema
from orchestration import validator_adapter, run_manager, execution_monitor
from storage import data_pipeline


def run_earth_simulation(batch_size: int, output_dir: str) -> None:
    """Execute the Earth simulation batch and store results.

    Parameters
    ----------
    batch_size:
        Number of identical Earth parameter runs to execute.
    output_dir:
        Directory where simulation outputs will be stored.
    """
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")

    monitor = execution_monitor.ExecutionMonitor()
    base_parameters = get_earth_parameters()

    for _ in range(batch_size):
        parameters: RDEEParameterSchema = base_parameters.clone()
        valid = False
        try:
            validator_adapter.validate_full_parameters(parameters)
            valid = True
        except Exception:
            valid = False
        monitor.register_validation(valid)
        if not valid:
            continue
        try:
            result = run_manager.execute_simulation_run(parameters)
        except Exception:
            monitor.register_storage(False)
            continue

        run_id = result.get("trace_id", uuid4().hex)
        depth = int(result.get("recursion_depth", 0))
        try:
            data_pipeline.save_simulation_run(run_id, parameters, result, output_dir)
            monitor.register_storage(True)
        except Exception:
            monitor.register_storage(False)
        monitor.register_depth(depth)


def main() -> None:
    """Main execution for direct CLI invocation."""
    run_earth_simulation(100, "./earth_simulation_output/")


if __name__ == "__main__":
    main()
