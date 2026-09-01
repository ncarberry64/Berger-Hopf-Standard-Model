import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT / "artifacts" / "flagship_integration"
    / "BHSM_N12_C2_SUPPRESSED_HARD_RESPONSE_ROW_CERTIFICATE.json"
)


def payload() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_complete_product_rule_row_is_certified_below_unchanged_ceiling() -> None:
    record = payload()
    assert record["validation_passed"] is True
    assert record["status"] == "C2_COMPLETE_SIGNED_D2DELTA_DOMINANT_ROW_CERTIFIED"
    assert len(record["raw_R_second_row_term_norm_uppers"]) == 18
    assert math.fsum(record["raw_R_second_row_term_norm_uppers"].values()) <= (
        record["raw_R_second_row_2_norm_upper"]
    )
    assert record["s_suppressed_R_second_row_2_norm_upper"] <= (
        record["signed_descriptor_absolute_upper"]
        * record["raw_R_second_row_2_norm_upper"]
        * (1.0 + 1.0e-15)
    )
    assert record["complete_signed_D2Delta_row_2_norm_upper"] < (
        record["rigorous_resolving_row_norm_ceiling"]
    )
    assert record["remaining_row_budget"] > 11.9


def test_local_duration_closure_does_not_promote_gate_or_force() -> None:
    adjudication = payload()["adjudication"]
    assert adjudication["s_suppressed_hard_response_row"] == "CERTIFIED"
    assert adjudication["signed_D_Y_Delta_on_exact_node_1214_family"] == (
        "ZERO_EXCLUDED"
    )
    assert adjudication["local_duration_denominator_data"] == "CERTIFIED"
    assert adjudication["transposed_exact_segment_map_action"] == "OPEN"
    assert adjudication["complete_upstream_heat_minus_zeta_covector"] == "OPEN"
    assert adjudication["maximal_projected_tail"] == "OPEN"
    assert adjudication["Gate7"] == "OPEN"
    assert adjudication["Gate8"] == "LOCKED"
    assert adjudication["chord_03_authorized"] is False
