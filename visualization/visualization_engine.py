"""Visualization utilities for RDEE simulation results."""

from __future__ import annotations

from typing import List, Tuple, Any, Dict

import numpy as np
import matplotlib.pyplot as plt


def _extract_value(data: Dict[str, Any], key: str) -> Any:
    """Retrieve a value from possibly nested dictionaries using dot notation."""
    if key in data:
        return data[key]

    current: Any = data
    for part in key.split('.'):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def generate_existence_heatmap(
    survival_data: List[Tuple[dict, bool]],
    param_x: str,
    param_y: str,
    bins: int = 50,
) -> None:
    """Display a heatmap of survival ratios for two parameters.

    Parameters
    ----------
    survival_data:
        Sequence of tuples ``(parameter_dict, survived_bool)`` representing
        simulation runs.
    param_x:
        Parameter name for the x-axis. Supports dot notation.
    param_y:
        Parameter name for the y-axis. Supports dot notation.
    bins:
        Number of histogram bins along each axis.
    """

    if not survival_data:
        raise ValueError("survival_data must not be empty")

    x_values: List[float] = []
    y_values: List[float] = []
    survival_flags: List[int] = []

    for params, survived in survival_data:
        x_val = _extract_value(params, param_x)
        y_val = _extract_value(params, param_y)

        if x_val is None or y_val is None:
            continue

        try:
            x_values.append(float(x_val))
            y_values.append(float(y_val))
            survival_flags.append(int(bool(survived)))
        except (TypeError, ValueError):
            continue

    if not x_values or not y_values:
        raise ValueError(
            f"No valid parameter values found for '{param_x}' and '{param_y}'"
        )

    x_arr = np.array(x_values)
    y_arr = np.array(y_values)
    surv_arr = np.array(survival_flags)

    counts_total, xedges, yedges = np.histogram2d(x_arr, y_arr, bins=bins)
    counts_survived, _, _ = np.histogram2d(
        x_arr[surv_arr == 1],
        y_arr[surv_arr == 1],
        bins=[xedges, yedges],
    )

    with np.errstate(invalid="ignore", divide="ignore"):
        ratio = np.divide(
            counts_survived,
            counts_total,
            out=np.zeros_like(counts_survived, dtype=float),
            where=counts_total != 0,
        )

    fig, ax = plt.subplots()
    mesh = ax.imshow(
        ratio.T,
        origin="lower",
        extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]],
        aspect="auto",
        cmap="viridis",
    )
    cbar = fig.colorbar(mesh, ax=ax)
    cbar.set_label("Survival Ratio")

    ax.set_xlabel(param_x)
    ax.set_ylabel(param_y)
    ax.set_title("Existence Survival Heatmap")

    plt.tight_layout()
    plt.show()


