from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_force_first_jet_critical_path.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/BHSM_N12_FORCE_FIRST_JET_CRITICAL_PATH.json"
)


def _payload() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_first_force_does_not_wait_for_second_operator_jet() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    later = payload["critical_path"]["not_required_before_first_force"]
    assert "D_xi2_K" in later
    assert "D2_C_RESET_STRATUM_CURVATURE" in later
    assert "D4_L_AND_MIXED_SECOND_STATE_JACOBI" in later
    assert payload["action_derivative_critical_path"][
        "first_jet_highest_action_derivative"
    ] == "D3_L"
    assert payload["claim_boundary"]["G7_08_actual_projected_force"] == "OPEN_CURRENT_OWNER"


def test_nonzero_force_branch_retains_second_jet_and_kkt_hessian() -> None:
    payload = _payload()
    branch = payload["critical_path"]["conditional_branch_after_force"]
    assert "D_xi2_K" in branch["if_projected_force_nonzero"]
    assert "GEOMETRY_RESET_KKT_HESSIAN" in branch["if_projected_force_nonzero"]
    assert payload["claim_boundary"]["second_operator_jet"].startswith("PENDING")
    assert payload["action_derivative_critical_path"][
        "mixed_second_highest_action_derivative"
    ] == "D4_L"
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_no_single_reset_representative_is_selected() -> None:
    payload = _payload()
    assert payload["critical_path"]["single_reset_representative_sufficient"] is False
    assert payload["critical_path"][
        "all_physical_tangent_directions_or_equivalent_covector_required"
    ] is True
