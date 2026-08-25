from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "derive_n12_c2_noncompact_reset_form_jet_kill_screen.py"
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_NONCOMPACT_RESET_FORM_JET_KILL_SCREEN.json"
)


def test_n12_c2_noncompact_reset_form_jet_kill_screen() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["noncompact_reset_form_jet_criterion"] == "DERIVED"
    assert payload["claim_boundary"]["actual_noncompact_reset_form_jet"] == "OPEN_NOT_CERTIFIED"
    assert payload["actual_C2_evidence"]["finite_prefix_segment_count"] == 98
    assert payload["adjudication"]["maximal_Weyl_value"] == "CLOSED_DO_NOT_REOPEN"
    assert payload["adjudication"]["actual_joint_replacement_force_tail"] == "OPEN_CURRENT_OWNER"
    assert payload["claim_boundary"]["chord_03_authorized"] is False


def test_value_limit_is_not_promoted_to_form_jet() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    witness = payload["sharpness_witnesses"]["value_convergence_does_not_imply_jet_convergence"]
    rows = witness["rows"]
    assert rows[-1]["uniform_value_error_upper"] < rows[0]["uniform_value_error_upper"]
    assert rows[-1]["derivative_at_xi_zero"] > rows[0]["derivative_at_xi_zero"]
    verdicts = {row["diagram_slot"]: row["verdict"] for row in payload["matching_audit"]}
    assert verdicts["FINITE_CORE_WEYL_VALUE_M_T"] == "VALID_MATCH_VALUE_LIMIT_DERIVED"
    assert verdicts["NONCOMPACT_RESET_JACOBI_FIELD"] == "ACTUALLY_MISSING_ON_MAXIMAL_TAIL"
    assert verdicts["FULL_NONCOMPACT_OPERATOR_FORM_JET_CAUCHY_TAIL"] == "ACTUALLY_MISSING_STRONG_OPERATOR_ROUTE"
    assert verdicts["SOURCE_CONTRACTED_COMBINED_REPLACEMENT_FORCE_TAIL"] == "ACTUALLY_MISSING_CURRENT_GATE_OWNER"
