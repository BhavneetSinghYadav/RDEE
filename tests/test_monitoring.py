import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from monitoring.runtime_monitor import RuntimeMonitor


def test_initialization() -> None:
    monitor = RuntimeMonitor()
    assert monitor.total_runs == 0
    assert monitor.successful_runs == 0
    assert monitor.failed_runs == 0
    assert monitor.current_batch_id is None
    assert monitor.get_survival_ratio() == 0.0


def test_register_runs_and_set_batch() -> None:
    monitor = RuntimeMonitor()
    monitor.set_batch_id(3)
    assert monitor.current_batch_id == 3

    monitor.register_run(True)
    monitor.register_run(False)
    monitor.register_run(True)

    assert monitor.total_runs == 3
    assert monitor.successful_runs == 2
    assert monitor.failed_runs == 1


def test_survival_ratio_no_runs() -> None:
    monitor = RuntimeMonitor()
    assert monitor.get_survival_ratio() == 0.0


def test_survival_ratio_only_failures() -> None:
    monitor = RuntimeMonitor()
    for _ in range(5):
        monitor.register_run(False)

    assert monitor.total_runs == 5
    assert monitor.successful_runs == 0
    assert monitor.failed_runs == 5
    assert monitor.get_survival_ratio() == 0.0


def test_survival_ratio_only_successes() -> None:
    monitor = RuntimeMonitor()
    for _ in range(4):
        monitor.register_run(True)

    assert monitor.total_runs == 4
    assert monitor.successful_runs == 4
    assert monitor.failed_runs == 0
    assert monitor.get_survival_ratio() == 1.0


def test_survival_ratio_mixed() -> None:
    monitor = RuntimeMonitor()
    sequence = [True, False, True, True, False]
    for result in sequence:
        monitor.register_run(result)

    assert monitor.total_runs == len(sequence)
    assert monitor.successful_runs == 3
    assert monitor.failed_runs == 2
    assert monitor.get_survival_ratio() == pytest.approx(3 / 5)


def test_report_output() -> None:
    monitor = RuntimeMonitor()
    monitor.set_batch_id(42)
    monitor.register_run(True)
    monitor.register_run(False)

    expected_ratio = monitor.get_survival_ratio()
    expected = (
        "Batch ID: 42 | Total Runs: 2 | Successful: 1 | Failed: 1 | "
        f"Survival Ratio: {expected_ratio:.2f}"
    )
    assert monitor.report() == expected
