import numpy as np
import pytest

from bhsm.interface.completion.driver_bhsm_exchange_traction_no_go_v14_89 import (
    NEXT_CANONICAL_OBJECT,
    completion_payload,
    decoupled_sector_ward_identity,
    deterministic_witness,
    driver_coupling_provenance_audit,
    driver_representation_kill_screen,
    exchange_conservation_residual,
    finite_difference_shape_vertex,
    hodge_decompose,
    interface_tangential_traction,
    isotropic_scalar_traction,
    materialize,
    zero_coupling_exchange_current,
)


def test_provenance_audit_finds_no_driver_interaction_but_preserves_internal_attachment() -> None:
    rows = driver_coupling_provenance_audit()
    assert len(rows) >= 23
    assert rows[-1]["object"] == "direct_driver_field"
    assert rows[-1]["status"] == "ABSENT"
    attachment = next(row for row in rows if row["object"] == "reciprocal_attachment_v11_3")
    assert attachment["interaction_term"] is True
    assert attachment["status"] == "REAL_INTERNAL_BHSM_COUPLING_NOT_DRIVER_BHSM"
    v1482 = next(row for row in rows if row["object"] == "v14_82_BH_susceptibility")
    assert v1482["status"] == "SOURCE_FUNCTIONAL_EXPLICITLY_ABSENT"


def test_decoupled_ward_identity_and_formal_exchange_conservation() -> None:
    ward = decoupled_sector_ward_identity(np.zeros(4), np.zeros(4))
    assert ward["total_residual"] == 0.0
    assert exchange_conservation_residual([-0.3, 0.2], [0.3, -0.2]) == 0.0
    with pytest.raises(ValueError):
        exchange_conservation_residual([1.0], [1.0, 2.0])


def test_isotropic_scalar_pressure_has_zero_tangential_traction_for_all_shapes() -> None:
    normal = np.array([1.0, 0.0, 0.0, 0.0])
    tangents = np.eye(4)[1:]
    response = np.arange(1.0, 10.0)
    current = lambda q: isotropic_scalar_traction(q, normal, tangents, pressure_shape_response=response)
    assert np.array_equal(current(np.arange(9.0)), np.zeros(3))
    assert np.array_equal(finite_difference_shape_vertex(current, 9), np.zeros((3, 9)))


def test_general_tangential_traction_detects_real_offdiagonal_momentum_flux() -> None:
    normal = np.array([1.0, 0.0, 0.0])
    tangents = np.eye(3)[1:]
    stress = np.array([[2.0, 0.4, -0.7], [0.4, 1.0, 0.0], [-0.7, 0.0, 1.0]])
    assert np.allclose(interface_tangential_traction(stress, normal, tangents), [0.4, -0.7])


def test_exact_and_coexact_hodge_components_are_orthogonal() -> None:
    basis = np.eye(6)
    decomposition = hodge_decompose(
        np.array([1.0, -2.0, 0.0, 0.0, 0.0, 0.0]),
        basis[:, :2],
        basis[:, 2:5],
        basis[:, 5:],
    )
    assert np.allclose(decomposition["coexact"], 0.0)
    assert decomposition["reconstruction_residual"] == 0.0
    assert decomposition["exact_coexact_inner_product"] == 0.0


def test_round_scalar_driver_representation_cannot_produce_coexact_l2() -> None:
    screen = driver_representation_kill_screen()
    assert screen["product"] == [(2, 2)]
    assert screen["contains_coexact_L2"] is False
    assert screen["scalar_gradient_channel"].startswith("EXACT")


def test_zero_coupling_current_vertex_and_schur_response_vanish() -> None:
    current = lambda q: zero_coupling_exchange_current(q, 8)
    vertex = finite_difference_shape_vertex(current, 9)
    assert vertex.shape == (8, 9)
    assert np.allclose(vertex, 0.0)
    witness = deterministic_witness()
    assert witness["zero_coupling_schur_norm"] == 0.0
    assert witness["zero_coupling_relative_reflection_vertex_norm"] == 0.0
    assert witness["conditional_positive_K_schur_max_eigenvalue"] <= 1e-12
    assert witness["general_schur_finite_difference_error"] < 2e-6
    assert witness["basis_covariance_residual"] < 1e-12


def test_payload_returns_outcome_c_and_preserves_completion_boundaries() -> None:
    payload = completion_payload()
    assert payload["validation_passed"] is True
    assert payload["retained_coupled_functional"]["S_driver"] == "ABSENT"
    assert payload["retained_coupled_functional"]["S_driver_BHSM_interaction"] == "ABSENT"
    assert payload["derived_exchange_current"]["physical_Q_ex_nu"] is None
    assert payload["current_shape_vertex"]["physical_B_ex_L2"] is None
    assert payload["v14_83_R7_bridge"]["exact_R7_derivation"] is False
    assert payload["next_canonical_object"] == NEXT_CANONICAL_OBJECT
    assert payload["completion_status"]["FULL_BHSM_COMPLETE"] is False
    assert payload["completion_status"]["USB_SYNCHRONIZATION_ELIGIBLE"] is False


def test_materialization_is_deterministic(tmp_path) -> None:
    first = materialize(tmp_path).read_bytes()
    second = materialize(tmp_path).read_bytes()
    assert first == second
