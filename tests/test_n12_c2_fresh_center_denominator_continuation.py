import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_FRESH_CENTER_DENOMINATOR_CONTINUATION.json"
)


def _payload() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_fresh_center_denominator_extension_is_certified() -> None:
    payload = _payload()
    continuation = payload["continuation"]
    assert payload["validation_passed"] is True
    assert continuation["prior_total_segments"] == 1064
    assert continuation["additional_certified_segments"] == 64
    assert continuation["total_certified_segments"] == 1128
    assert continuation["exhaustion_is_event_or_canonical_stop"] is False


def test_first_new_ball_strictly_crosses_old_half_margin() -> None:
    row = _payload()["continuation"]["rows"][0]
    assert 0.5 < row["hard_self_consistency"] < 1.0
    assert row["hard_denominator_lower"] > 0.0
    assert row["b_fixed_point_denominator_lower"] > 0.0
    assert row["incoming_tube_upper"] < row["selected_ball_radius"]
    assert row["root_use_inside_selected_ball"] < row["selected_ball_radius"]
    assert row["Delta_lower"] > 0.0


def test_proof_exhaustion_is_not_promoted_to_physics() -> None:
    payload = _payload()
    assert payload["adjudication"]["actual_later_event_or_canonical_stop"] == "NOT_REACHED"
    assert payload["adjudication"]["mathematical_history_termination_claimed"] is False
    assert payload["proof_reserve_adjudication"]["physical_parameter_added"] is False
    assert payload["claim_boundary"]["Gate8"] == "LOCKED"
    assert payload["FULL_BHSM_COMPLETE"] is False
