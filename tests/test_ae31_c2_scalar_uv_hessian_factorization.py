import hashlib

import numpy as np
import pytest

from bhsm.interface.ae31_c2_scalar_uv_hessian_factorization import (
    claim_boundary,
    exact_remaining_owner,
    full_zero_momentum_hadamard_pole,
    renormalized_generalized_eigenproblem,
    uv_shape_proportionality_theorem,
)
from scripts.materialize_ae31_c2_scalar_uv_hessian_factorization import (
    TARGET,
    build_payload,
    main,
)


def test_full_zero_momentum_pole_has_complete_gram_shape():
    result = full_zero_momentum_hadamard_pole(
        radius=2.0, mass_laurent_coordinate=0.5
    )
    gram = np.asarray(result["vertex_Gram_matrix"])
    pole = np.asarray(result["full_susceptibility_pole_matrix"])
    assert gram.shape == pole.shape == (4, 4)
    assert np.linalg.matrix_rank(gram) == 4
    assert np.all(pole.diagonal() < 0.0)
    assert not result["positive_mode_cutoff_interpretation"]
    with pytest.raises(ValueError):
        full_zero_momentum_hadamard_pole(radius=0.0)


def test_masslike_and_derivative_uv_shapes_are_identical():
    result = uv_shape_proportionality_theorem()
    assert result["normalized_shape_residual"] < 1.0e-15
    assert result["generalized_operator_identity_residual"] < 1.0e-12
    assert np.allclose(result["shape_generalized_eigenvalues"], np.ones(4))
    assert result["UV_singular_generalized_eigenspace_dimension"] == 4
    assert not result["UV_poles_select_scalar_channel_direction"]


def test_finite_generalized_problem_remains_explicitly_open():
    result = renormalized_generalized_eigenproblem()
    assert result["universal_UV_shape_cancels_from_direction_selector"]
    assert result["finite_state_or_boundary_data_required"]
    assert not result["physical_generalized_eigenproblem_evaluable"]
    assert not result["minimal_subtraction_or_cutoff_chosen_as_physics"]


def test_claim_boundary_and_materialization_are_conservative():
    claims = claim_boundary()
    assert claims["CURRENT_C2_FULL_SCALAR_ZERO_MOMENTUM_HADAMARD_POLE_SHAPE_DERIVED"]
    assert claims["CURRENT_C2_SCALAR_MASSLIKE_DERIVATIVE_UV_GRAM_FACTORIZATION_DERIVED"]
    assert claims["CURRENT_C2_SCALAR_UV_GENERALIZED_DIRECTION_DEGENERACY_DERIVED"]
    assert not claims["CURRENT_C2_FINITE_ZERO_MOMENTUM_SCALAR_HESSIAN_DERIVED"]
    assert not claims["CURRENT_C2_PHYSICAL_SINGLE_HIGGS_DIRECTION_SELECTED"]
    assert not exact_remaining_owner()["fitted_finite_matrix_allowed"]
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
