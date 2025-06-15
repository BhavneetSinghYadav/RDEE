from __future__ import annotations

"""Validation tests for RDEE Phase II full system behavior."""

import sys
from pathlib import Path
import importlib.util
import types
from dataclasses import replace

import pytest

# Ensure project root is available for imports
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Remove potential sampling stubs injected by other tests
for name in ["sampling", "sampling.parameter_sampler"]:
    if name in sys.modules:
        del sys.modules[name]

# Dynamically load parameter_sampler and expose it under the ``sampling`` namespace
spec = importlib.util.spec_from_file_location(
    "sampling.parameter_sampler", ROOT / "sampling" / "parameter_sampler.py"
)
parameter_sampler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parameter_sampler)
sampling_pkg = types.ModuleType("sampling")
sampling_pkg.parameter_sampler = parameter_sampler
sys.modules["sampling"] = sampling_pkg
sys.modules["sampling.parameter_sampler"] = parameter_sampler


# --- Structural Imports Test ---

def test_imports() -> None:
    """Verify core modules can be imported without error."""
    from sampling import parameter_sampler  # noqa: F401
    from simulation_engine.core import (  # noqa: F401
        stage_handlers,
        recursion_engine,
        bifurcation_handler,
    )
    from storage import data_pipeline  # noqa: F401


# --- Seeded Sampling Consistency Test ---

def test_sampling_determinism() -> None:
    """Identical seeds should produce identical parameter sets."""
    from sampling import parameter_sampler

    s1 = parameter_sampler.ParameterSampler.generate_sample(seed=42)
    s2 = parameter_sampler.ParameterSampler.generate_sample(seed=42)
    assert s1 == s2


# --- Small Batch Recursive Execution Test ---

def test_recursive_batch_small() -> None:
    """Ensure recursive engine returns a valid trace for sampled parameters."""
    from sampling import parameter_sampler
    from simulation_engine.core import recursion_engine

    for _ in range(10):
        params = parameter_sampler.ParameterSampler.generate_sample()
        params.sampling.recursive_depth_limit = replace(
            params.sampling.recursive_depth_limit, default=1
        )
        trace = recursion_engine.run_recursive_simulation(params)
        assert isinstance(trace, dict)
        assert "final_survival" in trace
        assert "path" in trace


# --- Depth Non-Triviality Test ---

def test_nonzero_depth() -> None:
    """At least one run should exceed zero recursion depth."""
    from sampling import parameter_sampler
    from simulation_engine.core import recursion_engine

    nonzero_depth = False
    for _ in range(100):
        params = parameter_sampler.ParameterSampler.generate_sample()
        params.sampling.recursive_depth_limit = replace(
            params.sampling.recursive_depth_limit, default=1
        )
        trace = recursion_engine.run_recursive_simulation(params)
        if trace.get("recursion_depth", 0) > 0:
            nonzero_depth = True
            break
    assert nonzero_depth


# --- Collapse Diversity Test ---

def test_collapse_diversity() -> None:
    """Multiple collapse stages should appear across many runs."""
    from sampling import parameter_sampler
    from simulation_engine.core import recursion_engine

    collapse_stages: set[str | None] = set()
    for _ in range(100):
        params = parameter_sampler.ParameterSampler.generate_sample()
        params.sampling.recursive_depth_limit = replace(
            params.sampling.recursive_depth_limit, default=1
        )
        trace = recursion_engine.run_recursive_simulation(params)
        collapse_stages.add(trace.get("collapse_stage"))
    assert len(collapse_stages) > 1


# --- Data Pipeline Round-Trip Test ---

def test_storage_roundtrip(tmp_path: Path) -> None:
    """Simulation run should persist and load correctly via data pipeline."""
    from sampling import parameter_sampler
    from simulation_engine.core import recursion_engine
    from storage import data_pipeline
    import numpy as np

    params = parameter_sampler.ParameterSampler.generate_sample()
    params.sampling.recursive_depth_limit = replace(
        params.sampling.recursive_depth_limit, default=1
    )
    trace = recursion_engine.run_recursive_simulation(params)
    run_id = trace["trace_id"]

    def _normalize(obj: object) -> object:
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, (np.floating, np.integer)):
            return obj.item()
        if isinstance(obj, dict):
            return {k: _normalize(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_normalize(v) for v in obj]
        return obj

    clean_trace = _normalize(trace)
    sanitized = data_pipeline._dict_to_schema(data_pipeline._schema_to_dict(params))
    data_pipeline.save_simulation_run(run_id, sanitized, clean_trace, str(tmp_path))

    loaded_params, loaded_trace = data_pipeline.load_simulation_run(
        tmp_path / f"{run_id}.h5"
    )
    assert loaded_trace["trace_id"] == run_id
