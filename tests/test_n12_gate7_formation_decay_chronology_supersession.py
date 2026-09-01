from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_gate7_formation_decay_chronology_supersession.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_FORMATION_DECAY_CHRONOLOGY_SUPERSESSION.json"
)


def _payload() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_finite_encapsulation_does_not_require_finite_child_end() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    assert payload["chronology"]["finite_condition_transfers_to_post_event_child"] is False
    assert payload["adjudication"]["post_event_finite_terminal_reachability_required"] is False
    assert payload["adjudication"]["infinite_Friedrichs_child_exterior_allowed"] is True


def test_finite_endpoint_kkt_is_preserved_as_sufficient_subroute() -> None:
    payload = _payload()
    assert payload["adjudication"]["finite_endpoint_BVP_route_remains_valid"] is True
    assert "VALID_SUFFICIENT_SUBROUTE" in payload["supersession"][
        "finite_endpoint_forward_adjoint_KKT_system"
    ]
    assert payload["claim_boundary"]["finite_endpoint_KKT_root"] == (
        "OPTIONAL_SUFFICIENT_SUBROUTE_OPEN"
    )


def test_current_owner_is_maximal_child_exterior_oracle() -> None:
    payload = _payload()
    assert payload["claim_boundary"]["Gate7"] == (
        "ACTIVE_MAXIMAL_CHILD_EXTERIOR_ORACLE_CURRENT_OWNER"
    )
    assert payload["claim_boundary"]["maximal_child_exterior_oracle"] == (
        "OPEN_CURRENT_OWNER"
    )
    assert payload["adjudication"]["retained_action_incompatibility_proved"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
