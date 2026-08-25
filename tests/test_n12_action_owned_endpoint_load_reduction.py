from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_action_owned_endpoint_load_reduction.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_ACTION_OWNED_ENDPOINT_LOAD_REDUCTION.json"
)


def _payload() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_endpoint_domain_is_owned_without_a_new_boundary_choice() -> None:
    payload = _payload()
    endpoint = payload["endpoint_load_adjudication"]
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["endpoint_domain_ownership"] == "CLOSED"
    assert endpoint["additional_boundary_action_or_selector_required"] is False
    assert endpoint["arbitrary_regular_cover_endpoint"] == "FORBIDDEN_NOT_ACTION_OWNED"


def test_proper_time_form_is_not_a_separate_missing_oracle() -> None:
    payload = _payload()
    owned = payload["dependency_reduction"]["already_action_owned"]
    assert "D_tau" in owned
    assert "Delta_tau=D_tau^star*D_tau_WITH_THE_RETAINED_ENDPOINT_FORM" in owned
    assert payload["dependency_reduction"]["current_dynamic_coefficient"] == "log_R4(tau)"


def test_minimal_theorem_requires_family_or_fiber_invariance() -> None:
    payload = _payload()
    theorem = payload["minimal_maximal_history_theorem"]
    assert theorem["quantifier"].startswith("NONEMPTY_REGULAR_FORWARD_REACHABLE")
    assert "FAMILY_ON_THE_FIXED_STRATUM_OR_PROVE_ACTION_DERIVED_FIBER_INVARIANCE" in theorem[
        "reset_fiber_statement"
    ]
    assert theorem["universal_terminal_reachability_required"] is False
    assert payload["claim_boundary"]["actual_projected_force"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False
