from __future__ import annotations

"""Launcher for Earth parameter simulation batches."""

import os

from interface.earth_parameter_instance import get_earth_parameters
from orchestration.execution_monitor import ExecutionMonitor
from orchestration import validator_adapter, run_manager
from storage import data_pipeline


def run_earth_simulation(batch_size: int, output_dir: str) -> ExecutionMonitor:
    """Execute a batch of Earth-parameter simulations and store results.

    Parameters
    ----------
    batch_size:
        Number of identical Earth parameter runs to execute.
    output_dir:
        Directory where simulation outputs will be stored.

    Returns
    -------
    ExecutionMonitor
        Monitoring object summarizing the execution outcome.
    """
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")

    mon = ExecutionMonitor()
    os.makedirs(output_dir, exist_ok=True)

    for idx in range(batch_size):
        params = get_earth_parameters()
        mon.register_validation(True)

        try:
            validator_adapter.validate_full_parameters(params)
        except Exception as e:
            mon.failed_validations += 1
            mon.register_validation(False)
            print(f"[{idx}] validation failed:", e)
            continue

        try:
            trace = run_manager.execute_simulation_run(params)
            depth = int(trace.get("recursion_depth", 0))
            mon.register_depth(depth)

            data_pipeline.save_simulation_run(
                run_id=trace["trace_id"],
                parameters=params,
                result=trace,
                output_dir=output_dir,
            )
            mon.register_storage(True)

        except Exception as e:
            mon.register_storage(False)
            print(f"[{idx}] storage or recursion failed:", e)

    return mon


def main() -> None:
    """Main execution for direct CLI invocation."""
    run_earth_simulation(100, "./earth_simulation_output/")


if __name__ == "__main__":
    main()
