import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"


def _load(name: str) -> dict:
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def test_global_stop_reconnaissance_has_finite_bracket_and_open_margins() -> None:
    record = _load("BHSM_N12_C2_GLOBAL_CANONICAL_STOP_RECONNAISSANCE.json")
    bracket = record["candidate_first_stop_bracket"]
    margins = record["domain_trends"]
    assert record["status"] == "FINITE_GLOBAL_s_ZERO_BRACKET_RECONNAISSANCE_ONLY"
    assert bracket["action_length_left"] == 92.0
    assert bracket["action_length_trial"] == 94.0
    assert bracket["signed_descriptor_left"] > 0.0
    assert bracket["signed_descriptor_trial"] < 0.0
    assert bracket["Delta_left"] < 0.0
    assert margins["minimum_selected_eigenline_gap"] > 0.0
    assert margins["minimum_boundary_lapse"] > 0.0
    assert margins["minimum_boundary_radius"] > 0.0
    assert margins["minimum_cancelled_field_action_norm"] > 0.0
    assert record["candidate_stop_is_certified"] is False
    assert record["validation_passed"] is False
    assert record["FULL_BHSM_COMPLETE"] is False


def test_sampled_delta_concavity_is_strict_but_not_promoted() -> None:
    record = _load("BHSM_N12_C2_GLOBAL_DELTA_CONCAVITY_RECONNAISSANCE.json")
    rows = record["rows"]
    assert [row["index"] for row in rows] == [0, 12, 24, 27, 36, 46]
    assert all(row["selected_branch"] == 24 for row in rows)
    assert all(row["selected_eigenline_gap"] > 0.0 for row in rows)
    assert all(row["dDelta_da_interval"][1] < 0.0 for row in rows)
    assert record["sampled_center_concavity"][
        "every_outward_rounded_point_interval_is_strictly_negative"
    ] is True
    boundary = record["claim_boundary"]
    assert boundary["motion_between_sample_centers_interval_certified"] is False
    assert boundary["uniform_dDelta_da_negative_on_global_tube"] is False
    assert boundary["canonical_s_zero_first_hit_certified"] is False
    assert record["validation_passed"] is False
    assert record["FULL_BHSM_COMPLETE"] is False
