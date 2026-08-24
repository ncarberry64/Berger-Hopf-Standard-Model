from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_joint_finite_history_operator_data_gate.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_JOINT_FINITE_HISTORY_OPERATOR_DATA_GATE.json"
)


def _payload() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_endpoint_checkpoint_inventory_does_not_fabricate_history() -> None:
    payload = _payload()
    inventory = payload["data_inventories"]["endpoint_checkpoint"]
    assert inventory["single_event_child_state_present"] is True
    assert inventory["first_constraint_jacobian_present"] is True
    assert inventory["required_history_or_operator_arrays_present"] == []
    assert "endpoint_form" in inventory[
        "required_history_or_operator_arrays_absent"
    ]
    assert "geometry_reset_hessian" in inventory[
        "required_history_or_operator_arrays_absent"
    ]


def test_persistence_validation_end_is_not_promoted_to_physical_endpoint() -> None:
    payload = _payload()
    persistence = payload["data_inventories"][
        "positive_duration_persistence"
    ]
    assert persistence["completed_as_persistence_test"] is True
    assert persistence["per_node_state_or_radius_keys"] == []
    assert persistence[
        "physical_terminal_or_canonical_stop_field_present"
    ] is False
    assert payload["logical_boundary"][
        "persistence_validation_endpoint_may_be_promoted"
    ] is False


def test_single_highest_dependency_is_action_operator_oracle() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"][
        "complete_action_owned_exterior_oracle"
    ] == "OPEN_CURRENT_OWNER"
    assert payload["claim_boundary"]["projected_KKT_solver"] == "DERIVED"
    assert payload["logical_boundary"][
        "failure_is_not_a_numerical_linear_solver_gap"
    ] is True
    assert payload["logical_boundary"][
        "infinite_nonencapsulating_formation_tail_reopened"
    ] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
