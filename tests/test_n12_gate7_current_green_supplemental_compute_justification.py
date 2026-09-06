from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / (
    "scripts/materialize_n12_gate7_current_green_supplemental_compute_justification.py"
)


def _module():
    spec = importlib.util.spec_from_file_location("supplemental_compute", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_estimate_uses_slower_full_width_normalized_pilot() -> None:
    module = _module()
    estimate = module._estimate({0: 198.0, 25: 222.0})
    assert estimate["row_0_seconds_per_right_direction"] == 2.0
    assert estimate["row_25_seconds_per_right_direction"] == 3.0
    expected = 1.25 * 3.0 * 2249 * 370 / 3600.0
    assert estimate["projected_full_campaign_CPU_hours"] == expected


def test_estimate_rejects_missing_or_nonpositive_pilots() -> None:
    module = _module()
    with pytest.raises(ValueError, match="both complement pilot"):
        module._estimate({0: 1.0})
    with pytest.raises(ValueError, match="positive and finite"):
        module._estimate({0: 1.0, 25: 0.0})

