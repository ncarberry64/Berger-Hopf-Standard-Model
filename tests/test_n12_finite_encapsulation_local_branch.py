from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

from scripts.derive_n12_finite_encapsulation_local_branch import build_payload


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_finite_encapsulation_local_branch.py"
TARGET = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_FINITE_ENCAPSULATION_LOCAL_BRANCH.json"
)


def test_singular_flow_is_regular_in_lambda_parameter() -> None:
    payload = build_payload()
    theorem = payload["desingularized_branch_theorem"]
    assert theorem["lambda_parameter_equation"].startswith(
        "dY/dlambda=(b_psi*Psi+lambda*V_hard)"
    )
    assert theorem["terminal_tangent"] == "dY/dlambda|_E=Psi_E/c_psi(E)"
    assert theorem["free_physical_threshold_inserted"] is False
    assert payload["validation"][
        "terminal_hitting_product_is_strictly_negative"
    ] is True


def test_branch_hits_event_in_finite_positive_forward_time() -> None:
    payload = build_payload()
    theorem = payload["desingularized_branch_theorem"]
    assert theorem["finite_time_asymptotic"].endswith("+o(lambda^2)>0")
    assert payload["adjudication"][
        "finite_positive_time_completed_encapsulation_exists"
    ] is True
    assert payload["adjudication"]["proof_scope"] == (
        "LOCAL_EXISTENCE_NEAR_THE_CERTIFIED_EVENT"
    )


def test_reset_and_post_event_child_complete_the_chronology() -> None:
    payload = build_payload()
    assert payload["chronology"] == {
        "formation": "PRE_EVENT_TERMINAL_SIDE_HISTORY",
        "encapsulation_completion": "CERTIFIED_SINGULAR_EVENT_HIT",
        "birth_reset": "CERTIFIED_EVENT_TO_COMPLETE_CHILD_RELATION",
        "decay_or_evolution": "POST_EVENT_POSITIVE_DURATION_CHILD_FLOW",
        "post_event_child_return_required": False,
    }
    completion = payload["event_to_child_completion"]
    assert completion["reset_relation_regular"] is True
    assert completion["fixed_event_child_fiber_dimension"] == 67
    assert completion["at_least_one_complete_child_exists"] is True
    assert completion["N12_positive_duration_proper_time"] > 0.0


def test_no_recurrence_or_universal_reachability_is_claimed() -> None:
    payload = build_payload()
    adjudication = payload["adjudication"]
    assert adjudication["universal_formation_reachability"] is False
    assert adjudication["current_complete_child_returns_to_event"] is False
    assert adjudication["return_or_recurrence_required"] is False
    assert adjudication["infinite_nonencapsulating_histories_falsified"] is False
    assert payload["claim_boundary"]["zero_source_force"] == "NEXT_CURRENT_OWNER"


def test_artifact_is_validated_and_deterministic() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    payload = json.loads(TARGET.read_text(encoding="utf-8"))
    assert first == second
    assert payload["validation_passed"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
