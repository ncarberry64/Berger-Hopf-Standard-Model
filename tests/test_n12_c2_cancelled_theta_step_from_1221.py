from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "certify_n12_c2_1221_cancelled_theta_step.py"


def _payload() -> dict:
    spec = importlib.util.spec_from_file_location("cancelled_theta_step", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_payload()


def test_cancelled_theta_step_strictly_extends_tracked_prefix() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    segment = payload["segment"]
    assert segment["theta_step"] > 0.0
    assert segment["signed_descriptor_center_end"] > segment["signed_descriptor_start"]
    assert segment["joint_domain_use_upper"] < payload["domain"]["selected_radius"]
    assert segment["proper_time_increment_lower"] > 0.0


def test_cancelled_theta_step_preserves_claim_boundary() -> None:
    payload = _payload()
    assert payload["validation"]["Delta_sign_not_required_as_domain_condition"] is True
    assert payload["validation"]["binary64_eigenvalue_not_used_as_descriptor"] is True
    assert payload["segment"]["proof_center_is_physical_endpoint"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False

