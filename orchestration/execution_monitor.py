from __future__ import annotations

"""Execution monitoring utilities for orchestration layer."""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class ExecutionMonitor:
    """Track high-level execution statistics across simulation batches."""

    total_runs: int = field(init=False, default=0)
    valid_runs: int = field(init=False, default=0)
    failed_validations: int = field(init=False, default=0)
    successful_storage: int = field(init=False, default=0)
    storage_failures: int = field(init=False, default=0)
    recursion_depths: List[int] = field(init=False, default_factory=list)

    def __init__(self) -> None:
        """Initialize all counters and storage containers."""
        self.total_runs = 0
        self.valid_runs = 0
        self.failed_validations = 0
        self.successful_storage = 0
        self.storage_failures = 0
        self.recursion_depths = []

    def register_validation(self, success: bool) -> None:
        """Record the result of a validation step.

        Parameters
        ----------
        success:
            ``True`` if validation succeeded, ``False`` otherwise.
        """
        if not isinstance(success, bool):
            raise TypeError("success must be a bool")
        self.total_runs += 1
        if success:
            self.valid_runs += 1
        else:
            self.failed_validations += 1

    def register_storage(self, success: bool) -> None:
        """Record the outcome of a storage operation.

        Parameters
        ----------
        success:
            ``True`` if the operation succeeded, ``False`` otherwise.
        """
        if not isinstance(success, bool):
            raise TypeError("success must be a bool")
        if success:
            self.successful_storage += 1
        else:
            self.storage_failures += 1

    def register_depth(self, depth: int) -> None:
        """Store the recursion depth for a completed run.

        Parameters
        ----------
        depth:
            The recursion depth reached during execution.

        Raises
        ------
        ValueError
            If ``depth`` is negative.
        """
        if depth < 0:
            raise ValueError("depth must be non-negative")
        self.recursion_depths.append(depth)

    def report(self) -> Dict[str, float | int]:
        """Return a summary of the current monitoring statistics."""
        if self.recursion_depths:
            average_depth = sum(self.recursion_depths) / len(self.recursion_depths)
        else:
            average_depth = 0.0
        return {
            "total_runs": self.total_runs,
            "valid_runs": self.valid_runs,
            "failed_validations": self.failed_validations,
            "successful_storage": self.successful_storage,
            "storage_failures": self.storage_failures,
            "average_recursion_depth": float(average_depth),
        }
