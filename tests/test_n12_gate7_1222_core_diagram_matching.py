import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_1222_CORE_DIAGRAM_MATCHING_AUDIT.json"


def test_gate7_1222_core_diagram_matching() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    verdicts = {row["diagram_slot"]: row["verdict"] for row in payload["matching_audit"]}
    assert verdicts["C2_COEFFICIENT_FORM_PREFIX"] == "VALID_MATCH_FINITE_PREFIX"
    assert verdicts["C2_FINITE_CORE_BACKWARD_OPERATOR_COTANGENT"].startswith(
        "VALID_MATCH_OPERATOR_COTANGENT"
    )
    assert verdicts["C2_RESET_QUOTIENT_FIRST_JET"].startswith("ACTUALLY_MISSING")
    assert verdicts["PAIR_CONTACT_AND_GRADED_SOURCE_INCIDENCE"] == "VALID_MATCH_CONDITIONAL_CONSUMER"
    assert payload["adjudication"]["finite_event_or_canonical_stop"] == "NOT_REACHED"
    assert payload["claim_boundary"]["zero_source_force"] == "OPEN"
