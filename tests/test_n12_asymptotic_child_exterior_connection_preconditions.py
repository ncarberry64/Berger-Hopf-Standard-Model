from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_asymptotic_child_exterior_connection_preconditions.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_ASYMPTOTIC_CHILD_EXTERIOR_CONNECTION_PRECONDITIONS.json"
)


def _payload() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_local_asymptotic_branch_is_not_a_reset_connected_oracle() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    assert payload["adjudication"]["analytic_branch_is_current_exterior_oracle"] is False
    assert payload["nonpromotion"]["one_stored_reset_state_is_on_asymptotic_branch"] is False
    assert payload["validation"]["backward_connection_is_not_proved"] is True


def test_no_unstable_root_does_not_remove_center_basin_obligation() -> None:
    payload = _payload()
    counts = payload["available_asymptotic_data"]["finite_mode_counts"]
    assert counts == {"stable": 25, "center": 25, "unstable": 0}
    assert payload["nonpromotion"][
        "no_unstable_linear_root_implies_open_nonlinear_basin"
    ] is False
    assert payload["nonpromotion"]["one_Briot_Bouquet_branch_is_a_center_stable_manifold"] is False


def test_both_maximal_exterior_routes_remain_valid() -> None:
    payload = _payload()
    adjudication = payload["adjudication"]
    assert adjudication["infinite_Friedrichs_route_invalid_in_principle"] is False
    assert adjudication["finite_endpoint_route_invalid_in_principle"] is False
    assert adjudication["retained_action_incompatibility_proved"] is False
    assert adjudication["chord_03_has_finite_proof_obligation"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
