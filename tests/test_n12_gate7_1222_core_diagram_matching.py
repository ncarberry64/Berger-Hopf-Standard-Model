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
    assert verdicts["C2_NON_SCALE_RESET_QUOTIENT_FIRST_JET"].startswith("VALID_MATCH_FINITE_CORE_FIRST_JET_NORM")
    assert verdicts["C2_EXACT_FIXED_s_STATE_GENERATOR"] == "VALID_MATCH_LOCAL_73_PARAMETER_BASE_FAMILY_THROUGH_1222"
    assert verdicts["COMMON_SCALE_HEAT_MINUS_ZETA_SOURCE_CONTRACTION"].startswith(
        "VALID_MATCH_FORMULA_CLOSED"
    )
    assert verdicts["C2_STORED_FIXED_CHANNEL_FINITE_CORE_HEAT_INCREMENT"].startswith(
        "VALID_MATCH_REPRESENTATIVE_INCREMENT_SUPPRESSED"
    )
    assert verdicts["INCOMING_C1_RESPONSE_M_f"].startswith(
        "VALID_MATCH_INCOMING_M_f_PARAMETRICALLY_ENCLOSED"
    )
    assert verdicts["PAIR_CONTACT_AND_GRADED_INTERNAL_INCIDENCE"].startswith("VALID_MATCH_INTERNAL")
    assert verdicts["ZERO_EXTERNAL_BIRTH_CAUCHY_SOURCE"] == "VALID_MATCH_ONLY_J_ext_IS_ZEROED"
    assert verdicts["COMPLETE_JOINT_HEAT_COTANGENT_REVERSE_SEED"].startswith("VALID_MATCH_SEED_CLOSED")
    assert payload["adjudication"]["finite_event_or_canonical_stop"] == "NOT_REACHED"
    assert payload["adjudication"]["stored_fixed_channel_1064_to_1222_heat_increment"] == "CERTIFIED_SUPPRESSED_IN_LOG_SPACE"
    assert payload["adjudication"]["non_scale_fixed_node_radius_reset_pullback"] == "CERTIFIED_ON_1222_FINITE_CORE"
    assert payload["adjudication"]["non_scale_moving_duration_reset_pullback_norm"] == "CERTIFIED_ON_1222_FINITE_CORE"
    assert payload["adjudication"]["signed_non_scale_backward_center_adjoint_value"].startswith("ACTUALLY_MISSING")
    assert payload["adjudication"]["exact_fixed_s_state_generator"] == "CERTIFIED"
    assert payload["adjudication"]["local_73_parameter_reset_family_through_1222"] == "CLOSED_EXISTENCE_ONLY"
    assert payload["adjudication"]["all_1222_interval_transposed_duration_actions"] == "CERTIFIED"
    assert payload["adjudication"]["joint_heat_cotangent_reverse_seed"] == "CLOSED"
    assert payload["adjudication"]["incoming_M_f_identity_and_action_owned_germ"].startswith("CLOSED")
    assert payload["adjudication"]["incoming_normalized_coefficient_path_quadratic_germ"] == "CLOSED_INVERSE_FREE"
    assert payload["claim_boundary"]["zero_source_force"] == "OPEN"
