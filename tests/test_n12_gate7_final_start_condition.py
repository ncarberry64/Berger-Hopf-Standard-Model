import json
from pathlib import Path

from bhsm.interface.gate7_final_start_condition import (
    adjudicate_track1_start_condition,
)


ROOT = Path(__file__).resolve().parents[1]
F = ROOT / "artifacts/flagship_integration"
RESULT = F / "BHSM_N12_GATE7_FINAL_START_CONDITION.json"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_final_start_condition_is_valid_and_fail_closed():
    payload = _load(RESULT)
    assert payload["validation_passed"] is True
    assert payload["status"] == "TRACK1_INCOMPLETE_AT_TRANSVERSE_OUTWARD_REMAINDER"
    assert payload["track1_final_start_condition_met"] is False
    assert payload["Track2_final_integration_authorized"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_all_expensive_shards_and_aggregate_are_retained():
    payload = _load(RESULT)
    shards = payload["shards"]
    assert shards["valid_endpoint_shards"] == shards["expected_endpoint_shards"] == 370
    assert shards["valid_midpoint_shards"] == shards["expected_midpoint_shards"] == 370
    assert shards["missing_shards"] == 0
    assert shards["invalid_shards"] == 0
    assert payload["aggregate"]["materialized"] is True
    assert payload["aggregate"]["validation_passed"] is True


def test_pointwise_center_majorant_is_not_promoted_to_outward_authority():
    payload = _load(RESULT)
    transverse = payload["full_transverse"]
    assert transverse["center_operator_derived"] is True
    assert transverse["unit_sphere_center_majorant_derived"] is True
    assert transverse["outward_neighborhood_remainder_derived"] is False
    assert transverse["full_operator_bound_derived"] is False
    assert payload["two_radius_Volterra_screen"] == "NOT_DERIVED"
    assert payload["Gate7_mathematical_verdict"] == "OPEN"
    assert payload["first_irreducible_blocker"]["id"] == (
        "G7_CURRENT_GREEN_TRANSVERSE_OUTWARD_NEIGHBORHOOD_REMAINDER"
    )


def test_pure_adjudicator_reproduces_committed_verdict():
    center = _load(F / "BHSM_N12_GATE7_CURRENT_GREEN_FULL_TRANSVERSE_QUADRATIC_CENTER.json")
    mixed = _load(F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_HS_CAUSAL_TRANSPORT.json")
    verdict = adjudicate_track1_start_condition(center, mixed)
    committed = _load(RESULT)
    for key in (
        "campaign_fingerprint",
        "shard_manifest_SHA256",
        "full_transverse",
        "mixed_causal_operator",
        "two_radius_Volterra_screen",
        "Gate7_mathematical_verdict",
        "track1_final_start_condition_met",
        "first_irreducible_blocker",
    ):
        assert verdict[key] == committed[key]
