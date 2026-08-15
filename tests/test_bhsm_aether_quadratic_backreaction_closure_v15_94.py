from bhsm.interface.aether_quadratic_backreaction_closure_v15_94 import (
    block_matrix_witness,
    common_boundary_term_no_repair,
    completion_payload,
    constrained_schur_theorem,
    field_degree_selection_rule,
)


def test_zero_background_kills_all_geometry_matter_mixed_hessians():
    result = field_degree_selection_rule()
    assert all(value == 0.0 for value in result["mixed_quadratic_blocks"].values())
    assert result["constraint_projection_changes_this_degree_count"] is False


def test_constraint_schur_complement_leaves_two_points_unchanged():
    theorem = constrained_schur_theorem()
    witness = block_matrix_witness()
    assert theorem["gauge_two_point_changed_by_classical_geometry_elimination"] is False
    assert theorem["fermion_two_point_changed_by_classical_geometry_elimination"] is False
    assert witness["Schur_minus_direct_matter_norm"] == 0.0


def test_common_lorentz_boundary_term_cannot_repair_anisotropic_difference():
    result = common_boundary_term_no_repair()
    assert result["difference_K_electric_minus_K_magnetic"] > 1900.0
    assert result["finite_common_DeltaK_can_match_cones"] is False
    assert result["classical_action_owned_quadratic_correction_remaining"] is False


def test_payload_validates():
    assert completion_payload()["validation_passed"]
