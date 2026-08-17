import json

from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    completion_payload,
    deterministic_json,
)


def test_independent_cross_resolution_reconnaissance_contract():
    payload = completion_payload(points=32)
    result = payload["cross_resolution_reconnaissance"]
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["validation_passed"] is True
    assert [row["order"] for row in result["orders"]] == [3, 4, 5]
    assert all(
        not row["initialization"]["accepted_N3_trajectory_used"]
        for row in result["orders"]
    )
    assert [
        row["complete_child_structure"]["full_unreduced_child_row_count"]
        for row in result["orders"]
    ] == [14, 16, 18]
    assert result["questions"][
        "same_rank14_complete_child_reconstructs"
    ]["classification"] == "RECLASSIFIED"
    assert result["orders"][1]["initialization"]["eta_domain_admissible"] is True
    assert result["orders"][2]["initialization"]["eta_domain_admissible"] is False
    assert result["orders"][2]["local_flow"]["physical_probe_admissible"] is False
    assert result["questions"]["N5_confirms_or_contradicts_N4"][
        "answer"
    ] == "CONTRADICTS_AT_THE_CURRENT_DIRECT_RESET"


def test_reconnaissance_serialization_is_deterministic():
    payload = completion_payload(points=32)
    first = deterministic_json(payload)
    second = deterministic_json(payload)
    assert first == second
    assert json.loads(first)["validation_passed"] is True
