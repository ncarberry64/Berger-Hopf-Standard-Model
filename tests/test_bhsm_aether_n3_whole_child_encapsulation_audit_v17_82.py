from bhsm.interface.aether_n3_whole_child_encapsulation_audit_v17_82 import (
    completion_payload,
    deterministic_json,
    whole_child_encapsulation_audit,
)


def test_whole_child_is_owned_without_changing_the_376_state():
    audit = whole_child_encapsulation_audit()
    verdict = audit["rank_and_formulation_verdict"]
    assert verdict["whole_child_already_exists"] is True
    assert verdict["whole_child_should_be_added_to_376_now"] is False
    assert verdict["pre_event_KKT_remains"] == "376_UNKNOWNS_376_EQUATIONS"
    assert verdict["direct_N3_solve_authorized_next"] is False
    assert "SOLVABILITY_MAP" in verdict["direct_N3_solve_condition"]


def test_encapsulation_map_is_typed_but_not_claimed_as_derived():
    audit = whole_child_encapsulation_audit()
    correspondence = audit["minimal_encapsulation_correspondence"]
    assert correspondence["action_derived_now"] is False
    assert "E_boundary" in correspondence["required_map"]
    assert audit["obstruction_test"][
        "missing_pre_event_degree_of_freedom_demonstrated"
    ] is False


def test_whole_child_audit_validates_deterministically():
    first = completion_payload()
    second = completion_payload()
    assert first["validation_passed"] is True
    assert deterministic_json(first) == deterministic_json(second)
