from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_gate7_normalized_field_common_frame_identity.py"


def _module():
    spec = importlib.util.spec_from_file_location("normalized_field_identity", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_normalized_field_identity_and_radii_bridge() -> None:
    payload = _module().build_payload()
    assert payload["validation_passed"] is True
    assert payload["identities"]["D2_f_majorant"] == "||D2f||<=A2/g0+3*A1^2/g0^2"
    assert payload["common_frame_bridge"]["Z2"].startswith("Z2<=C_A")
    assert payload["claim_boundary"]["numerical_common_frame_majorants"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False
