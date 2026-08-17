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
    ] == "CURRENT_BRANCH_INADMISSIBLE_NO_CROSS_RESOLUTION_VERDICT"
    ownership = payload["ingredient_process_ownership_audit"]
    assert ownership["validation_passed"] is True
    assert ownership["eta_audit"]["classification"] == "ETA-D"
    assert ownership["ordered_event_ownership"][
        "classification"
    ] == "EVENT_ENCLOSURE_EQUIVALENCE_OPEN"
    assert ownership["cross_resolution_stage_status"]["N5"][
        "EVENT_STATUS"
    ] == "NOT_YET_APPLICABLE"
    scale = payload["physical_scale_accessibility_audit"]
    assert scale["validation_passed"] is True
    assert scale["physical_scale_coordinate"][
        "numerical_resolution_N_is_rho"
    ] is False
    assert scale["action_sector_ownership"][
        "C_ES_status"
    ] == "OPEN_UNDEFINED_NOT_ZERO"
    assert scale["event_approach_metric_audit"][
        "chi_E_status"
    ] == "OPEN_UNDEFINED_UNTIL_G_IS_DERIVED"
    assert scale["scale_sweep_falsification_protocol"][
        "global_encapsulation_cost_implemented"
    ] is False
    network = payload["breadth_first_closure_network_audit"]
    assert network["validation_passed"] is True
    assert network["doctrine"][
        "observed_particle_values_may_select_upstream_branch"
    ] is False
    assert network["interfaces"]["event_child_reconstruction_return"][
        "equations"
    ]["row_count"] == "2N+8"
    assert network["interfaces"]["generic_family_children_mixing"][
        "current_child_export_is_sufficient"
    ] is False


def test_reconnaissance_serialization_is_deterministic():
    payload = completion_payload(points=32)
    first = deterministic_json(payload)
    second = deterministic_json(payload)
    assert first == second
    assert json.loads(first)["validation_passed"] is True
