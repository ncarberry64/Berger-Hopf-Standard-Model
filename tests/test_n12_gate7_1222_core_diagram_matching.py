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
    assert verdicts["C2_PHYSICAL_COMMON_SCALE_FIRST_JET"].startswith("VALID_MATCH_CLOSED")
    assert verdicts["C2_NON_SCALE_RESET_QUOTIENT_FIRST_JET"].startswith("ACTUALLY_MISSING")
    assert verdicts["COMMON_SCALE_HEAT_MINUS_ZETA_SOURCE_CONTRACTION"].startswith(
        "VALID_MATCH_FORMULA_CLOSED"
    )
    assert verdicts["C2_STORED_FIXED_CHANNEL_FINITE_CORE_HEAT_INCREMENT"].startswith(
        "VALID_MATCH_REPRESENTATIVE_INCREMENT_SUPPRESSED"
    )
    assert verdicts["INCOMING_C1_RESPONSE_M_f"].startswith(
        "VALID_MATCH_IDENTITY_AND_ACTION_OWNED_GERM"
    )
    assert verdicts["PAIR_CONTACT_AND_GRADED_SOURCE_INCIDENCE"] == "VALID_MATCH_CONDITIONAL_CONSUMER"
    assert payload["adjudication"]["finite_event_or_canonical_stop"] == "NOT_REACHED"
    assert payload["adjudication"]["stored_fixed_channel_1064_to_1222_heat_increment"] == "CERTIFIED_SUPPRESSED_IN_LOG_SPACE"
    assert payload["adjudication"]["incoming_M_f_identity_and_action_owned_germ"].startswith("CLOSED")
    assert payload["claim_boundary"]["zero_source_force"] == "OPEN"
