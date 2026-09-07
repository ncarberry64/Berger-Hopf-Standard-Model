from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/materialize_n12_gate7_current_green_mixed_hs_causal_compute_justification.py"


def _module():
    spec = importlib.util.spec_from_file_location("mixed_hs_compute", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_compute_audit_authorizes_only_bounded_vectorized_campaign():
    payload = _module().build_payload()
    assert payload["validation_passed"] is True
    assert payload["campaign_authorized"] is True
    assert payload["cost"]["projected_CPU_hours_at_eight_workers"] < 160.0
    assert payload["benchmark"]["midpoint_maximum_scaled_component_radius"] < 1.0e-8
    assert payload["FULL_BHSM_COMPLETE"] is False
