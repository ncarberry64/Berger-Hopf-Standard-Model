import hashlib

import pytest

from bhsm.interface.ae31_c2_quark_higgs_contact_closure import (
    affine_first_order_contact_theorem,
    claim_boundary,
    determinant_hessian_reduction,
    exact_remaining_owner,
    squared_pencil_contact_closure,
)
from scripts.materialize_ae31_c2_quark_higgs_contact_closure import (
    TARGET,
    build_payload,
    main,
)


UP = (1.0, 0.008310500554068288, 1.2690463017606151e-05)
DOWN = (1.0, 0.021933971495439474, 0.0011165200546001757)


def test_affine_first_order_dirac_incidence_has_zero_contact():
    theorem = affine_first_order_contact_theorem()
    assert theorem["first_order_contact_jet_zero"]
    assert set(theorem["second_variations"].values()) == {"0"}
    assert not theorem["higher_dimension_scalar_fermion_contact_inserted"]


def test_squared_pencil_contact_is_fixed_by_first_vertices():
    theorem = squared_pencil_contact_closure(
        up_shape=UP, down_shape=DOWN, c_up=1.7, c_down=0.6
    )
    assert theorem["Q_up_up_residual"] == 0.0
    assert theorem["Q_down_down_residual"] == 0.0
    assert theorem["mixed_contact_zero_by_disjoint_support"]
    assert theorem["diagonal_contacts_positive_semidefinite"]
    assert theorem["contact_jet_fixed_once_vertices_are_fixed"]
    assert theorem["independent_contact_coefficient_count"] == 0


def test_contact_closure_requires_three_slot_finite_shapes():
    with pytest.raises(ValueError):
        squared_pencil_contact_closure(up_shape=(1.0,), down_shape=DOWN)
    with pytest.raises(ValueError):
        squared_pencil_contact_closure(
            up_shape=(1.0, float("nan"), 0.0), down_shape=DOWN
        )


def test_determinant_formula_preserves_state_obstruction():
    theorem = determinant_hessian_reduction()
    assert theorem["first_order_Q_fg_term"].startswith("ABSENT")
    assert not theorem["squared_pencil_contact_is_independent_input"]
    assert theorem["state_covariance_or_Feynman_inverse_still_required"]
    assert theorem["up_down_vertex_residues_still_required"]


def test_remaining_owner_has_no_independent_contact_coefficient():
    owner = exact_remaining_owner()
    assert owner["independent_missing_vertex_residues"] == ["c_u", "c_d"]
    assert owner["independent_missing_contact_coefficients"] == []
    assert owner["mixed_contact_on_transported_support"] == "Q_ud=Q_du=0"
    assert not owner["independent_yukawa_contact_or_mass_fit_allowed"]


def test_claim_boundary_promotes_contact_closure_only():
    boundary = claim_boundary()
    assert boundary["CURRENT_C2_QUARK_FIRST_ORDER_HIGGS_CONTACT_JET_ZERO_DERIVED_CONDITIONAL"]
    assert boundary["CURRENT_C2_QUARK_SQUARED_PENCIL_CONTACT_CLOSED_BY_FIRST_VERTICES"]
    assert not boundary["CURRENT_C2_INDEPENDENT_QUARK_CONTACT_COEFFICIENT_REQUIRED"]
    assert not boundary["CURRENT_C2_UP_DOWN_YUKAWA_VERTEX_RESIDUES_ACTION_DERIVED"]
    assert not boundary["CURRENT_C2_QUARK_QUANTUM_HESSIAN_DERIVED"]


def test_materialized_contact_closure_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
