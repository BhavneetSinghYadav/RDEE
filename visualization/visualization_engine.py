"""Visualization utilities for RDEE simulation results."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

import json
import os
from dataclasses import is_dataclass, fields

import h5py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


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


def _flatten_parameters(data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    """Return a flattened mapping of parameter defaults."""
    flat: Dict[str, Any] = {}
    for name, value in data.items():
        key = f"{prefix}{name}" if not prefix else f"{prefix}.{name}"
        if isinstance(value, dict):
            if "default" in value:
                flat[key] = value.get("default")
            else:
                flat.update(_flatten_parameters(value, key))
        elif is_dataclass(value):
            # dataclass objects from schema; recurse using field values
            nested: Dict[str, Any] = {f.name: getattr(value, f.name) for f in fields(value)}
            flat.update(_flatten_parameters(nested, key))
        else:
            flat[key] = value
    return flat


def load_all_traces(trace_files: List[str]) -> pd.DataFrame:
    """Load trace files into a flattened :class:`pandas.DataFrame`."""
    records: List[Dict[str, Any]] = []
    for path in trace_files:
        if not os.path.isfile(path):
            continue
        try:
            with h5py.File(path, "r") as h5f:
                trace_group = h5f["trace"]
                param_raw = trace_group["parameters_json"][()]
                result_raw = trace_group["result_json"][()]
        except Exception:
            continue

        param_str = (
            param_raw.decode("utf-8") if isinstance(param_raw, bytes) else str(param_raw)
        )
        result_str = (
            result_raw.decode("utf-8") if isinstance(result_raw, bytes) else str(result_raw)
        )

        try:
            param_dict = json.loads(param_str)
            result_dict = json.loads(result_str)
        except Exception:
            continue

        flat_params = _flatten_parameters(param_dict)

        record: Dict[str, Any] = {
            "trace_id": os.path.splitext(os.path.basename(path))[0],
            "final_survival": int(bool(result_dict.get("final_survival"))),
            "collapse_stage": result_dict.get("collapse_stage"),
            "recursion_depth": result_dict.get("recursion_depth"),
            "random_seed": result_dict.get("random_seed"),
        }
        record.update(flat_params)
        records.append(record)

    return pd.DataFrame(records)


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


def plot_survival_distribution(df: pd.DataFrame) -> None:
    """Display a bar plot of survival outcomes."""
    counts = df["final_survival"].value_counts().sort_index()
    counts.plot(kind="bar")
    plt.xlabel("Final Survival")
    plt.ylabel("Count")
    plt.xticks([0, 1], ["Collapsed", "Survived"])
    plt.title("Survival Distribution")
    plt.tight_layout()
    plt.show()


def plot_collapse_stage_distribution(df: pd.DataFrame) -> None:
    """Display a horizontal bar plot of collapse stages."""
    df["collapse_stage"].value_counts().plot(kind="barh")
    plt.xlabel("Count")
    plt.ylabel("Collapse Stage")
    plt.title("Collapse Stage Distribution")
    plt.tight_layout()
    plt.show()


def plot_recursion_depth_distribution(df: pd.DataFrame) -> None:
    """Display a histogram of recursion depths."""
    bins = range(df["recursion_depth"].max() + 2)
    df["recursion_depth"].hist(bins=bins)
    plt.xlabel("Recursion Depth")
    plt.ylabel("Count")
    plt.title("Recursion Depth Distribution")
    plt.tight_layout()
    plt.show()


def plot_parameter_sensitivity(df: pd.DataFrame, parameter_key: str) -> None:
    """Display a boxplot of a parameter's distribution by survival outcome."""
    sns.boxplot(x="final_survival", y=parameter_key, data=df)
    plt.xlabel("Final Survival")
    plt.xticks([0, 1], ["Collapsed", "Survived"])
    plt.ylabel(parameter_key)
    plt.title(f"Parameter Sensitivity: {parameter_key}")
    plt.tight_layout()
    plt.show()


def plot_bifurcation_heatmap(df: pd.DataFrame, param_x: str, param_y: str) -> None:
    """Display a scatter plot of survival across two parameters."""
    sns.scatterplot(x=df[param_x], y=df[param_y], hue=df["final_survival"], alpha=0.5)
    plt.xlabel(param_x)
    plt.ylabel(param_y)
    plt.title("Bifurcation Map")
    plt.tight_layout()
    plt.show()


def compute_collapse_entropy(df: pd.DataFrame) -> float:
    """Return the entropy of collapse stages."""
    collapse_counts = df["collapse_stage"].value_counts()
    probabilities = collapse_counts / len(df)
    entropy = -np.sum(probabilities * np.log2(probabilities))
    return float(entropy)


