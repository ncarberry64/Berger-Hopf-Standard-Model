from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_gate7_signed_common_frame_data_matching.py"


def _payload():
    spec = importlib.util.spec_from_file_location("common_frame_matching", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.build_payload()


def test_common_frame_slots_and_missing_interval_adapters() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    assert payload["new_action_or_operator_required"] is False
    assert payload["new_theory_choice_required"] is False
    assert payload["literal_definitions"]["Y"] == "||A*(-d)||_P"
    assert len(payload["actual_missing_interval_adapters"]) == 3
    assert payload["downstream_physical_quotient_adapter"].startswith("COUPLED_HYBRID_TIME_GENERATOR")
    slots = {row["slot"]: row for row in payload["matching_audit"]}
    assert slots["BORDERED_RESPONSE_VECTOR_AND_PATH_DERIVATIVE"]["match"] == "VALID_CERTIFIED_MATCH"
    assert slots["LITERAL_Y"]["match"].startswith("ACTUALLY_MISSING")
    assert slots["LITERAL_Z1"]["match"].startswith("ACTUALLY_MISSING")
    assert slots["LITERAL_Z2"]["match"].startswith("ACTUALLY_MISSING")
    assert slots["FINAL_WHOLE_SYSTEM_TIME_QUOTIENT"]["match"].startswith("ACTUALLY_MISSING")
    assert payload["claim_boundary"]["Gate7"] == "ACTIVE"
    assert all("HALF_STEP" not in path for path in payload["inputs"])
    assert any("QUARTER_STEP_GRAPH_JACOBIAN" in path for path in payload["inputs"])
    assert any("QUARTER_STEP_DENSE_DESCRIPTOR_FIRST_HIT" in path for path in payload["inputs"])
    assert payload["FULL_BHSM_COMPLETE"] is False
