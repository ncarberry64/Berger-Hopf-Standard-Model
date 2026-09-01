from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_forward_adjoint_kkt_existence_gate.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/BHSM_N12_FORWARD_ADJOINT_KKT_EXISTENCE_GATE.json"
)


def _payload() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_equations_are_closed_but_root_existence_is_not() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    assert payload["closed_inputs"]["forward_adjoint_quotient_KKT_equations"] == "DERIVED"
    assert payload["claim_boundary"]["finite_endpoint_KKT_root"] == "OPEN_CURRENT_OWNER"


def test_local_formation_and_two_chords_are_not_mispromoted() -> None:
    payload = _payload()
    rows = payload["nonpromotion_results"]
    assert rows["local_formation_branch_is_post_reset_terminal_stratum"] is False
    assert rows["two_chord_core_is_complete_operator_domain"] is False
    assert rows["chord_03_has_finite_proof_obligation"] is False
    assert payload["sufficient_completion_routes"]["universal_terminal_reachability_required"] is False


def test_gap_is_existence_not_action_incompatibility() -> None:
    payload = _payload()
    failure = payload["failure_classification"]
    assert failure["missing_existential_or_validated_global_temporal_control"] is True
    assert failure["missing_force_calculus"] is False
    assert failure["missing_endpoint_boundary_condition"] is False
    assert failure["retained_action_incompatibility_proved"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
