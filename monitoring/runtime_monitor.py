from __future__ import annotations

"""Runtime monitoring utilities for local simulation runs."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RuntimeMonitor:
    """Track runtime statistics for simulation execution.

    This monitor maintains counters for overall runs and their outcomes. It can
    report the current batch identifier along with a survival ratio computed
    from successful runs over total runs.
    """

    total_runs: int = field(init=False, default=0)
    successful_runs: int = field(init=False, default=0)
    failed_runs: int = field(init=False, default=0)
    current_batch_id: Optional[int] = field(init=False, default=None)

    def __init__(self) -> None:
        """Initialize a new :class:`RuntimeMonitor` with zeroed counters."""
        self.total_runs = 0
        self.successful_runs = 0
        self.failed_runs = 0
        self.current_batch_id = None

    def register_run(self, success: bool) -> None:
        """Update counters after a single run completes.

        Parameters
        ----------
        success:
            ``True`` if the run completed successfully, ``False`` otherwise.

        Raises
        ------
        TypeError
            If ``success`` is not of type :class:`bool`.
        """
        if not isinstance(success, bool):
            raise TypeError("success must be a bool")

        self.total_runs += 1
        if success:
            self.successful_runs += 1
        else:
            self.failed_runs += 1

    def set_batch_id(self, batch_id: int) -> None:
        """Set the current batch identifier for subsequent runs.

        Parameters
        ----------
        batch_id:
            Identifier of the batch being executed.

        Raises
        ------
        ValueError
            If ``batch_id`` is negative.
        """
        if batch_id < 0:
            raise ValueError("batch_id must be non-negative")
        self.current_batch_id = batch_id

    def get_survival_ratio(self) -> float:
        """Return the survival ratio of successful runs to total runs."""
        if self.total_runs == 0:
            return 0.0
        return self.successful_runs / self.total_runs

    def report(self) -> str:
        """Return a formatted status report of current monitoring state."""
        batch_display = self.current_batch_id if self.current_batch_id is not None else "N/A"
        ratio = self.get_survival_ratio()
        return (
            f"Batch ID: {batch_display} | Total Runs: {self.total_runs} | "
            f"Successful: {self.successful_runs} | Failed: {self.failed_runs} | "
            f"Survival Ratio: {ratio:.2f}"
        )
