from __future__ import annotations

import sys
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from visualization.visualization_engine import generate_existence_heatmap

from visualization.visualization_engine import generate_existence_heatmap


@pytest.fixture(autouse=True)
def _cleanup_plots(monkeypatch: pytest.MonkeyPatch) -> None:
    """Suppress plot display and clean up after tests."""
    monkeypatch.setattr(plt, "show", lambda: None)
    yield
    plt.close("all")


def _build_data(x_vals: List[float], y_vals: List[float], survived: List[bool]):
    return [
        ({"stellar": {"stellar_mass": x}, "planetary": {"planet_mass": y}}, s)
        for x, y, s in zip(x_vals, y_vals, survived)
    ]


def _assert_single_image() -> None:
    fig = plt.gcf()
    assert fig.axes, "No axes created"
    ax = fig.axes[0]
    assert len(ax.images) == 1


def test_generate_existence_heatmap_valid() -> None:
    data = _build_data([1.0, 2.0, 3.0], [2.0, 3.0, 4.0], [True, False, True])
    generate_existence_heatmap(data, "stellar.stellar_mass", "planetary.planet_mass")
    _assert_single_image()


def test_generate_existence_heatmap_empty_data() -> None:
    with pytest.raises(ValueError):
        generate_existence_heatmap([], "stellar.stellar_mass", "planetary.planet_mass")


def test_generate_existence_heatmap_all_success() -> None:
    data = _build_data([1.0, 1.5, 2.0], [0.5, 0.7, 0.9], [True, True, True])
    generate_existence_heatmap(data, "stellar.stellar_mass", "planetary.planet_mass")
    _assert_single_image()


def test_generate_existence_heatmap_all_failure() -> None:
    data = _build_data([1.0, 2.0, 3.0], [1.0, 2.0, 3.0], [False, False, False])
    generate_existence_heatmap(data, "stellar.stellar_mass", "planetary.planet_mass")
    _assert_single_image()


def test_generate_existence_heatmap_constant_x() -> None:
    data = _build_data([1.0, 1.0, 1.0], [0.2, 0.4, 0.6], [True, False, True])
    generate_existence_heatmap(data, "stellar.stellar_mass", "planetary.planet_mass")
    _assert_single_image()


def test_generate_existence_heatmap_constant_y() -> None:
    data = _build_data([0.2, 0.4, 0.6], [1.0, 1.0, 1.0], [True, False, True])
    generate_existence_heatmap(data, "stellar.stellar_mass", "planetary.planet_mass")
    _assert_single_image()


def test_generate_existence_heatmap_bins_argument() -> None:
    data = _build_data([1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0], [True, False, True, False])
    generate_existence_heatmap(
        data,
        "stellar.stellar_mass",
        "planetary.planet_mass",
        bins=10,
    )
    _assert_single_image()
