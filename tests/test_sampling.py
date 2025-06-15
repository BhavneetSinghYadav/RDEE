import random
import sys
import types
from dataclasses import fields
from pathlib import Path
from typing import List

import importlib.util
import dataclasses
import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]

# Load interface.parameter_schema as a module without package wrappers
interface_pkg = types.ModuleType("interface")
param_spec = importlib.util.spec_from_file_location(
    "interface.parameter_schema", ROOT_DIR / "interface" / "parameter_schema.py"
)
parameter_schema = importlib.util.module_from_spec(param_spec)
sys.modules["interface.parameter_schema"] = parameter_schema
sys.modules["interface"] = interface_pkg
_orig_dataclass = dataclasses.dataclass

def _patched_dataclass(*args, **kwargs):
    kwargs.setdefault("unsafe_hash", True)
    return _orig_dataclass(*args, **kwargs)

dataclasses.dataclass = _patched_dataclass
param_spec.loader.exec_module(parameter_schema)
dataclasses.dataclass = _orig_dataclass
interface_pkg.parameter_schema = parameter_schema

# Load sampling.sampling_controller with dependencies resolved
sampling_pkg = types.ModuleType("sampling")
sampling_spec = importlib.util.spec_from_file_location(
    "sampling.sampling_controller", ROOT_DIR / "sampling" / "sampling_controller.py"
)
sampling_controller = importlib.util.module_from_spec(sampling_spec)
sys.modules["sampling"] = sampling_pkg
sys.modules["sampling.sampling_controller"] = sampling_controller
sampling_spec.loader.exec_module(sampling_controller)

generate_initial_samples = sampling_controller.generate_initial_samples
sample_parameter_value = sampling_controller.sample_parameter_value
ParameterSpec = parameter_schema.ParameterSpec
RDEEParameterSchema = parameter_schema.RDEEParameterSchema


# Set deterministic randomness for reproducibility
random.seed(1234)


def collect_specs(schema: RDEEParameterSchema) -> List[ParameterSpec]:
    """Helper to collect all ParameterSpec objects in a schema."""
    specs = []
    for group_name in (
        "cosmological",
        "stellar",
        "planetary",
        "habitability",
        "prebiotic",
        "evolutionary",
        "sampling",
    ):
        group = getattr(schema, group_name)
        for field in fields(group):
            specs.append(getattr(group, field.name))
    return specs


def test_sample_parameter_value_float_range() -> None:
    random.seed(1)
    spec = ParameterSpec(
        name="test_float",
        dtype=float,
        units="unit",
        min_value=0.0,
        max_value=1.0,
        default=None,
    )
    value = sample_parameter_value(spec)
    assert isinstance(value, float)
    assert 0.0 <= value <= 1.0


def test_sample_parameter_value_int_range() -> None:
    random.seed(2)
    spec = ParameterSpec(
        name="test_int",
        dtype=int,
        units="unit",
        min_value=1,
        max_value=10,
        default=None,
    )
    value = sample_parameter_value(spec)
    assert isinstance(value, int)
    assert 1 <= value <= 10


def test_sample_parameter_value_equal_bounds() -> None:
    random.seed(3)
    float_spec = ParameterSpec(
        name="const_float",
        dtype=float,
        units="u",
        min_value=0.5,
        max_value=0.5,
        default=None,
    )
    int_spec = ParameterSpec(
        name="const_int",
        dtype=int,
        units="u",
        min_value=7,
        max_value=7,
        default=None,
    )
    assert sample_parameter_value(float_spec) == 0.5
    assert sample_parameter_value(int_spec) == 7


def test_generate_initial_samples_correct_types_and_ranges() -> None:
    random.seed(4)
    samples = generate_initial_samples(3)
    assert len(samples) == 3
    for schema in samples:
        assert isinstance(schema, RDEEParameterSchema)
        for spec in collect_specs(schema):
            assert isinstance(spec, ParameterSpec)
            if spec.min_value is not None and spec.max_value is not None:
                assert spec.min_value <= spec.default <= spec.max_value


def test_generate_initial_samples_independent_objects() -> None:
    random.seed(5)
    samples = generate_initial_samples(2)
    assert samples[0] is not samples[1]
    specs_0 = collect_specs(samples[0])
    specs_1 = collect_specs(samples[1])
    for s0, s1 in zip(specs_0, specs_1):
        assert s0 is not s1
    # ensure at least one parameter differs to confirm random sampling
    differences = [s0.default != s1.default for s0, s1 in zip(specs_0, specs_1)]
    assert any(differences)

