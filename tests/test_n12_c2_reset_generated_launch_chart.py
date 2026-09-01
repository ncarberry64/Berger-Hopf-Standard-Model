import numpy as np

from scripts.derive_n12_c2_reset_generated_launch_chart import build_payload


def test_reset_generated_launch_dimension_is_72_plus_1() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    dimensions = payload["dimension_theorem"]
    assert dimensions["reset_tangent"] == 139
    assert dimensions["swapped_C2_seed_image"] == 72
    assert dimensions["fixed_C2_seed_lift_kernel"] == 67
    assert dimensions["outgoing_descriptor_amplitude"] == 1
    assert dimensions["C2_launch_manifold"] == 73


def test_outgoing_field_is_exactly_the_missing_transverse_direction() -> None:
    payload = build_payload()
    witness = payload["numerical_coordinate_witness"]
    assert payload["validation"]["exact_descriptor_identity_is_one"] is True
    assert payload["validation"]["outgoing_field_is_transverse_to_event_image"] is True
    assert witness["event_projection_smallest_nonzero_singular_value"] > 0.4
    assert witness["event_projection_largest_null_singular_value"] < 1.0e-12
    assert witness["outgoing_transverse_component_norm_after_unit_normalization"] > 1.0e-5


def test_launch_chart_preserves_claim_boundary() -> None:
    payload = build_payload()
    assert payload["adjudication"]["reset_member_selected"] is False
    assert payload["adjudication"]["stored_proof_center_promoted_to_physical_history"] is False
    assert payload["claim_boundary"]["maximal_C2_response"] == "OPEN"
    assert payload["claim_boundary"]["actual_projected_zero_source_force"] == "OPEN"
    assert payload["claim_boundary"]["FULL_BHSM_COMPLETE"] is False
