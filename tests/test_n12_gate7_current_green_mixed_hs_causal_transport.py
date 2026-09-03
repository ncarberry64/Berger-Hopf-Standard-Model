from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
from flint import arb


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/certify_n12_gate7_current_green_mixed_hs_causal_transport.py"


def _module():
    spec = importlib.util.spec_from_file_location("mixed_hs_causal", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_ball_kernel_source_changes_only_declared_contracts():
    module = _module()
    source = module._kernel_source()
    assert "def _mixed_axis_map_preserving_balls(" in source
    assert source.count("isinstance(value, arb)") == 2
    assert "return result, jets" in source


def test_export_contains_input_balls():
    module = _module()
    values = np.asarray([[arb(2, 0.25), arb(-3, 0.5)]], dtype=object)
    midpoint, radius = module._export(values)
    reconstructed = module._ball(midpoint, radius)
    for original, enclosed in zip(values.ravel(), reconstructed.ravel(), strict=True):
        assert (original - enclosed).contains(0)


def test_fingerprints_separate_endpoint_and_midpoint():
    module = _module()
    assert module._fingerprint("endpoint", 192) != module._fingerprint("midpoint", 192)
