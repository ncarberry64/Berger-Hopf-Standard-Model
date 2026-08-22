import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/qxi_relative_energy_preparation/"
    "BHSM_N12_MATCHED_PARENT_STATIONARY_SECTION_GATE.json"
)


def test_matched_parent_stationary_section_gate_is_fail_closed() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["CONTINUUM_EVENT_CHILD_CERTIFIED"] is True
    assert payload["R_P_executable"] is False
    assert payload["Q_xi_evaluated"] is False
    assert payload["Delta_H_evaluated"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["v7_1_correspondence"]["R_8to5_defined"] is True
    assert payload["v7_1_correspondence"]["R_5to4_defined"] is True
    assert payload["parent_domain_nonuniqueness_witness"][
        "parent_phase_choices"
    ] == [0.0, 1.0]
    assert payload["parent_only_typing"]["boundary_localized_field_maps"] == {
        "A_SM": None,
        "H": None,
        "Psi": None,
    }
    assert payload["implicit_function_audit"][
        "implicit_function_theorem_applicable"
    ] is False
    assert payload["implicit_function_audit"][
        "current_N12_inverse_can_be_reused_for_parent_section"
    ] is False
    assert payload["empty_child_identity_audit"][
        "abstract_event_identity_exists"
    ] is True
    assert payload["empty_child_identity_audit"][
        "abstract_identity_is_action_derived"
    ] is False
    assert payload["empty_child_identity_audit"][
        "conditional_parent_seed_action_selected"
    ] is False
    event_forward = payload["counterfactual_event_forward_audit"]
    assert event_forward["event_half_is_complete_reduced_N12_Cauchy_tuple"] is True
    assert event_forward["event_is_complete_global_v7_1_parent_state"] is False
    assert event_forward["nonlinear_response_fork"] == [
        "RESTORATION",
        "ENCAPSULATION",
    ]
    assert event_forward["encapsulation_selected_over_restoration"] is False
    assert event_forward["existing_positive_duration_diagnostic_is_forward_parent_proof"] is False
    assert event_forward["event_forward_R_P_executable"] is False
