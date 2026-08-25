from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_c2_finite_connection_residual.py"
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_FINITE_CONNECTION_RESIDUAL.json"


def test_n12_c2_finite_connection_residual_contract() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["finite_connection_residual"] == "DERIVED_EXECUTABLE"
    assert payload["claim_boundary"]["actual_finite_connection_solution"] == "OPEN"
    assert payload["dimension_ledger"]["raw_child_reset_fiber"] == 67
    assert payload["dimension_ledger"]["physical_endpoint_stratum"] == 66
    assert payload["dimension_ledger"]["common_scale"] == "RETAINED_PHYSICAL_DIRECTION"
    assert payload["actual_prefix"]["segment_count"] == 98
    assert payload["actual_prefix"]["physical_endpoint_reached"] is False
    assert payload["claim_boundary"]["chord_03_authorized"] is False


def test_actual_matching_audit_does_not_promote_prefix() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    verdicts = {row["diagram_slot"]: row["verdict"] for row in payload["matching_audit"]}
    assert verdicts["FIXED_EVENT_CHILD_RESET_ROWS"] == "VALID_MATCH"
    assert verdicts["C2_FORWARD_VECTOR_FIELD"] == "ACTUALLY_MISSING_AS_CERTIFIED_CONTINUOUS_CALLBACK_BEYOND_PREFIX"
    assert verdicts["ENDPOINT_GRAPH"] == "ACTUALLY_MISSING_AS_REACHED_LATER_ENDPOINT"
    assert payload["algebraic_assembly_witness"]["total_residual_norm"] == 0.0
