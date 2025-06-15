"""Earth Visualization utilities for RDEE results."""

from __future__ import annotations

from typing import List
import os
import h5py
import matplotlib.pyplot as plt

from storage import data_pipeline


def load_traces(trace_files: List[str]) -> List[dict]:
    """Load trace dictionaries from a list of HDF5 files.

    Parameters
    ----------
    trace_files:
        Paths to HDF5 files produced by the simulation runs.

    Returns
    -------
    List[dict]
        List of trace dictionaries loaded from disk.
    """
    traces: List[dict] = []
    for path in trace_files:
        if not os.path.isfile(path):
            continue
        try:
            with h5py.File(path, "r") as h5f:
                trace = data_pipeline._read_json_dataset(h5f, "result")
                if isinstance(trace, dict):
                    traces.append(trace)
        except Exception:
            continue
    return traces


def plot_survival_distribution(trace_files: List[str]) -> None:
    """Plot survival and recursion depth distributions from trace files.

    Parameters
    ----------
    trace_files:
        Paths to persisted trace HDF5 files.
    """
    traces = load_traces(trace_files)
    if not traces:
        raise ValueError("No valid trace data provided")

    survival_flags = [1 if t.get("final_survival") else 0 for t in traces]
    depths = [int(t.get("recursion_depth", 0)) for t in traces]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    ax1.hist(survival_flags, bins=[-0.5, 0.5, 1.5], rwidth=0.8, color="tab:blue")
    ax1.set_xticks([0, 1])
    ax1.set_xticklabels(["Collapsed", "Survived"])
    ax1.set_ylabel("Count")
    ax1.set_title("Survival Outcomes")

    ax2.hist(depths, bins=max(1, min(20, len(set(depths)))), color="tab:green", edgecolor="black")
    ax2.set_xlabel("Recursion Depth")
    ax2.set_ylabel("Count")
    ax2.set_title("Recursion Depth Distribution")

    plt.tight_layout()
    plt.show()
