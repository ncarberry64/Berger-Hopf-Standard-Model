from __future__ import annotations

import json
from pathlib import Path

from scripts.derive_n12_c2_exact_fixed_s_field_oracle import build_payload


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts" / "flagship_integration" / "BHSM_N12_C2_EXACT_FIXED_S_FIELD_ORACLE.json"


def test_exact_fixed_s_field_oracle() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["exact_fixed_s_field_oracle"] == "CERTIFIED"
    assert payload["claim_boundary"]["actual_parametric_base_history"] == "OPEN"
    verdicts = {row["diagram_slot"]: row["verdict"] for row in payload["matching_audit"]}
    assert verdicts["EXACT_C2_FIXED_s_STATE_GENERATOR"] == "VALID_MATCH"
    assert verdicts["SIGNED_1222_BACKWARD_CENTER_ADJOINT_BASE"].startswith("ACTUALLY_MISSING")


def test_stored_exact_field_oracle_matches_builder() -> None:
    assert json.loads(RESULT.read_text(encoding="utf-8")) == build_payload()
