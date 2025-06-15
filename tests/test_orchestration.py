import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from orchestration.execution_monitor import ExecutionMonitor


def test_initialization() -> None:
    monitor = ExecutionMonitor()
    assert monitor.total_runs == 0
    assert monitor.valid_runs == 0
    assert monitor.failed_validations == 0
    assert monitor.successful_storage == 0
    assert monitor.storage_failures == 0
    assert monitor.recursion_depths == []
    report = monitor.report()
    assert report["total_runs"] == 0
    assert report["average_recursion_depth"] == 0.0


def test_register_validation() -> None:
    monitor = ExecutionMonitor()
    monitor.register_validation(True)
    monitor.register_validation(False)
    assert monitor.total_runs == 2
    assert monitor.valid_runs == 1
    assert monitor.failed_validations == 1


def test_register_storage() -> None:
    monitor = ExecutionMonitor()
    monitor.register_storage(True)
    monitor.register_storage(False)
    assert monitor.successful_storage == 1
    assert monitor.storage_failures == 1


def test_register_depth_and_report() -> None:
    monitor = ExecutionMonitor()
    monitor.register_depth(2)
    monitor.register_depth(4)
    assert monitor.recursion_depths == [2, 4]
    report = monitor.report()
    assert report["average_recursion_depth"] == pytest.approx(3.0)


def test_invalid_inputs() -> None:
    monitor = ExecutionMonitor()
    with pytest.raises(TypeError):
        monitor.register_validation(1)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        monitor.register_storage(0)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        monitor.register_depth(-1)
