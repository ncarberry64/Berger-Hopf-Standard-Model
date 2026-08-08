from pathlib import Path
import json
import numpy as np

from bhsm.interface.completion.second_shape_jacobi_triplet_v14_70 import (
    VERSION, PRIMARY_VERDICT, EXACT_NEXT_OBJECT,
    round_graph_metric_second_variation, round_graph_metric_second_bilinear,
    constant_displacement_second_fd_residual, jacobi_eigenvalue,
    scalar_harmonic_multiplicity, scalar_laplacian_eigenvalue, jacobi_spectrum,
    no_exact_threefold_scalar_eigenspace, l2_diagonal_su2_projectors,
    projector_quality, reflection_stationarity_payload, second_shape_metric_payload,
    jacobi_spectrum_payload, l2_triplet_decomposition_payload,
    three_shape_channel_gate_payload, provenance_gate_payload,
    neutrino_kill_screen_payload, status_payload, completion_gate_payload,
    next_object_payload, artifact_payloads, materialize,
)


def test_version_and_verdict():
    assert VERSION == "v14.70"
    assert "SECOND" in PRIMARY_VERDICT
    assert "SECOND_SHAPE_HESSIAN" in EXACT_NEXT_OBJECT


def test_quadratic_second_variation_is_symmetric():
    h2 = round_graph_metric_second_variation(0.3, [0.1, -0.2, 0.05], 1.4)
    assert h2.shape == (3, 3)
    assert np.linalg.norm(h2 - h2.T) < 1e-14


def test_bilinear_second_variation_is_symmetric_in_arguments():
    a = round_graph_metric_second_bilinear(0.3, [0.1,-0.2,0.05], -0.4, [0.03,0.07,-0.09], 1.2)
    b = round_graph_metric_second_bilinear(-0.4, [0.03,0.07,-0.09], 0.3, [0.1,-0.2,0.05], 1.2)
    assert np.linalg.norm(a-b) < 1e-14


def test_polarization_identity():
    p = second_shape_metric_payload()
    assert p["polarization_identity_residual"] < 1e-12


def test_trace_gives_jacobi_bilinear_identity():
    p = second_shape_metric_payload()
    assert p["trace_jacobi_identity_residual"] < 1e-12


def test_constant_displacement_matches_exact_round_graph():
    assert constant_displacement_second_fd_residual() < 1e-7


def test_scalar_laplacian_formula():
    assert scalar_laplacian_eigenvalue(0, 2.0) == 0.0
    assert scalar_laplacian_eigenvalue(1, 2.0) == 3.0/4.0
    assert scalar_laplacian_eigenvalue(2, 2.0) == 2.0


def test_jacobi_formula_low_modes():
    assert jacobi_eigenvalue(0, 1.0) == -3.0
    assert jacobi_eigenvalue(1, 1.0) == 0.0
    assert jacobi_eigenvalue(2, 1.0) == 5.0
    assert jacobi_eigenvalue(3, 1.0) == 12.0


def test_harmonic_multiplicities():
    assert [scalar_harmonic_multiplicity(l) for l in range(5)] == [1,4,9,16,25]


def test_no_threefold_scalar_eigenspace():
    assert no_exact_threefold_scalar_eigenspace(128)


def test_jacobi_spectrum_rows():
    rows = jacobi_spectrum(4, 1.0)
    assert rows[0]["classification"] == "HOMOGENEOUS_NEGATIVE_GEOMETRIC_AREA_MODE"
    assert rows[1]["classification"] == "AMBIENT_ISOMETRY_ZERO_MODE"
    assert rows[2]["classification"] == "POSITIVE_ROUND_AREA_JACOBI_MODE"
    assert rows[2]["multiplicity"] == 9


def test_l2_projector_ranks_1_3_5():
    p1,p3,p5 = l2_diagonal_su2_projectors()
    assert np.linalg.matrix_rank(p1,tol=1e-11) == 1
    assert np.linalg.matrix_rank(p3,tol=1e-11) == 3
    assert np.linalg.matrix_rank(p5,tol=1e-11) == 5


def test_l2_projectors_are_orthogonal_and_complete():
    p1,p3,p5 = l2_diagonal_su2_projectors()
    assert np.linalg.norm(p1+p3+p5-np.eye(9)) < 1e-13
    assert np.linalg.norm(p1@p3) < 1e-13
    assert np.linalg.norm(p1@p5) < 1e-13
    assert np.linalg.norm(p3@p5) < 1e-13


def test_projectors_idempotent_selfadjoint():
    for p in l2_diagonal_su2_projectors():
        q=projector_quality(p)
        assert q["idempotence_residual"] < 1e-13
        assert q["self_adjoint_residual"] < 1e-13


def test_reflection_stationarity_fails_closed_on_nonround():
    p=reflection_stationarity_payload()
    assert p["v14_69_first_shape_response_norm"] == 0.0
    assert p["fallback_to_second_shape_required"] is True
    assert p["nonround_action_stationary_branch_constructed"] is False
    assert p["full_global_background_stationarity_under_all_bulk_variations_proved_here"] is False


def test_second_shape_payload():
    p=second_shape_metric_payload()
    assert p["constant_displacement_finite_difference_residual"] < 1e-7
    assert p["second_shape_is_bilinear_not_a_first_order_linear_incidence_map"] is True
    assert p["full_BHSM_second_shape_hessian_complete"] is False


def test_jacobi_payload_exact_counts():
    p=jacobi_spectrum_payload()
    assert p["homogeneous_l0_eigenvalue"] == -3.0
    assert p["l1_zero_mode_multiplicity"] == 4
    assert p["first_positive_ell"] == 2
    assert p["first_positive_eigenvalue"] == 5.0
    assert p["first_positive_multiplicity"] == 9
    assert p["no_exact_threefold_scalar_eigenspace_through_ell64"] is True
    assert p["area_jacobi_operator_equals_full_BHSM_shape_hessian"] is False


def test_triplet_decomposition_payload():
    p=l2_triplet_decomposition_payload()
    assert p["triplet_rank"] == 3
    assert p["projector_sum_identity_residual"] < 1e-12
    assert p["pairwise_orthogonality_residual"] < 1e-12
    assert p["triplet_mathematically_available"] is True
    assert p["diagonal_SU2_selected_by_current_global_BHSM_action"] is False
    assert p["predeclared_three_shape_channels_identified_with_this_triplet"] is False


def test_three_shape_channel_gate_blocks_physical_selection():
    p=three_shape_channel_gate_payload()
    assert p["round_scalar_second_shape_spectrum_supplies_exact_threefold_eigenspace"] is False
    assert p["l2_contains_rank_three_subrepresentation_after_diagonal_SU2_choice"] is True
    assert p["action_owned_selection_of_diagonal_SU2_or_Hopf_polarization"] is False
    assert p["physical_three_nonuniform_shape_derivatives_available"] is False


def test_provenance_gate_fail_closed():
    p=provenance_gate_payload()
    assert p["universal_round_graph_second_metric_variation_derived"] is True
    assert p["universal_round_area_jacobi_spectrum_derived"] is True
    assert p["complete_BHSM_second_shape_Hessian_bulk_GHY_KKT_nonlocal"] is False
    assert p["all_physical_provenance_inputs_present"] is False


def test_neutrino_kill_screen_blocks():
    p=neutrino_kill_screen_payload()
    assert p["current_result"] == "PHYSICAL_EXECUTION_BLOCKED"
    assert p["physical_execution_allowed"] is False
    assert p["physical_mass_PMNS_splitting_or_probability_emitted"] is False


def test_status_ledger():
    p=status_payload()
    assert len(p["validated"]) >= 12
    assert len(p["invalidated"]) >= 4
    assert len(p["reclassified"]) >= 4
    assert len(p["open"]) >= 10
    assert p["FULL_BHSM_COMPLETE"] is False
    assert p["MARK_III"] == "NOT_REACHED"
    assert p["USB_touched"] is False


def test_completion_gate_internal_pass_physical_fail():
    p=completion_gate_payload()
    assert p["validation_passed"] is True
    assert p["FULL_BHSM_COMPLETE"] is False
    assert p["physical_execution_allowed"] is False


def test_next_object_requires_action_owned_polarization():
    p=next_object_payload()
    text=" ".join(p["why"]).lower()
    assert "triplet" in text
    assert "action-owned" in text
    assert "second shape" in text


def test_artifact_count_and_names():
    p=artifact_payloads()
    assert len(p)==10
    assert "BHSM_round_jacobi_spectrum_v14_70.json" in p
    assert "BHSM_l2_triplet_decomposition_v14_70.json" in p
    assert "BHSM_completion_gate_v14_70.json" in p


def test_materialization_byte_deterministic(tmp_path: Path):
    a=tmp_path/"a"; b=tmp_path/"b"
    pa=materialize(a); pb=materialize(b)
    assert [x.name for x in pa] == [x.name for x in pb]
    for x,y in zip(pa,pb):
        assert x.read_bytes() == y.read_bytes()
        json.loads(x.read_text())
