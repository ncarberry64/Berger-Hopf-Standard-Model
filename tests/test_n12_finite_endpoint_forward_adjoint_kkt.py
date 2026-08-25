from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_finite_endpoint_forward_adjoint_kkt.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/BHSM_N12_FINITE_ENDPOINT_FORWARD_ADJOINT_KKT.json"
)


def _payload() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_joint_system_keeps_reset_parameter_and_endpoint_action_owned() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    assert payload["system"]["reset"].startswith("Y(0)=R_AE2(xi)")
    assert "FIRST_TRANSVERSE_RETAINED_EVENT" in payload["system"]["endpoint"]
    assert payload["claim_boundary"]["single_reset_representative_sufficient"] is False


def test_parametric_and_simultaneous_routes_are_equivalent_not_new_physics() -> None:
    payload = _payload()
    routes = payload["equivalent_routes"]
    assert routes["mathematically_equivalent_at_a_regular_root"] is True
    assert routes["new_physical_choice"] is False
    assert payload["claim_boundary"]["actual_finite_endpoint_stratum_solution"] == "OPEN_CURRENT_OWNER"


def test_later_hessians_are_not_collapsed_into_first_order_system() -> None:
    payload = _payload()
    boundary = payload["derivative_boundary"]
    assert boundary["residual_evaluation_highest_action_derivative"] == "D3_L"
    assert "D4_L" in boundary["Newton_or_KKT_linearization_for_nonzero_force_branch"]
    assert boundary["pair_plus_contact_source_Hessian_is_this_KKT_Jacobian"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
