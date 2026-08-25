from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_c2_projected_adjoint_cauchy_criterion.py"
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_PROJECTED_ADJOINT_CAUCHY_CRITERION.json"
)


def test_c2_projected_adjoint_cauchy_criterion() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["projected_Cauchy_criterion"] == "DERIVED"
    assert payload["claim_boundary"]["actual_projected_Cauchy_tail"] == "OPEN_CURRENT_OWNER"
    assert payload["theorem"]["strong_sufficient_condition"].startswith("integral_0")
    assert payload["logical_witnesses"]["absolute_norm_not_necessary"]["projected_force_for_every_T"] == 0.0
    assert payload["logical_witnesses"]["regular_factors_not_sufficient"]["maximal_projected_limit_exists"] is False
    assert payload["finite_prefix_evidence"]["segment_count"] == 98
    assert payload["adjudication"]["fixed_channel_source_Dini_slot"] == "CLOSED_DO_NOT_REOPEN"
    assert payload["adjudication"]["actual_maximal_state_propagator_tail"] == "OPEN"
    assert payload["claim_boundary"]["chord_03_authorized"] is False


def test_matching_audit_has_no_false_complete_maximal_slot() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    verdicts = {row["diagram_slot"]: row["verdict"] for row in payload["matching_audit"]}
    assert verdicts["PHYSICAL_RESET_PULLBACK"] == "VALID_MATCH"
    assert verdicts["STATE_PROPAGATOR_U"] == "ACTUALLY_MISSING_ON_MAXIMAL_TAIL"
    assert verdicts["NUMERICAL_ZERO_SOURCE_FORCE"] == "ACTUALLY_MISSING"

