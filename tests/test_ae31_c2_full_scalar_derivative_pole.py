import hashlib

import numpy as np
import pytest

from bhsm.interface.ae31_c2_full_scalar_derivative_pole import (
    claim_boundary,
    derivative_eigenmode_boundary,
    exact_remaining_owner,
    family_noncentral_rank_theorem,
    full_lorentzian_derivative_symbol,
    scalar_vertex_gram_matrix,
)
from scripts.materialize_ae31_c2_full_scalar_derivative_pole import (
    TARGET,
    build_payload,
    main,
)


def test_vertex_gram_matrix_is_full_rank_and_positive():
    result = scalar_vertex_gram_matrix()
    gram = np.asarray(result["Gram_matrix"])
    assert gram.shape == (4, 4)
    assert result["Gram_rank"] == 4
    assert result["positive_definite"]
    assert np.all(np.asarray(result["Gram_eigenvalues"]) > 0.0)
    assert gram[2, 2] == gram[3, 3] == 9.0
    assert np.allclose(gram[:2, 2:], 0.0)


def test_family_noncentrality_lifts_intrinsic_auxiliary_null_direction():
    result = family_noncentral_rank_theorem()
    assert result["strictly_positive"]
    assert result["current_family_noncentral_block_rank"] == 2
    assert result["full_four_field_pole_rank"] == 4
    assert not result["intrinsic_and_charged_lepton_HS_directions_redundant"]
    gram = scalar_vertex_gram_matrix()
    assert gram["variance_identity_residual"] < 1.0e-18


def test_full_symbol_has_matching_temporal_spatial_matrix():
    result = full_lorentzian_derivative_symbol(
        omega=0.5, spatial_eigenvalue=1.25, epsilon_uv=2.0
    )
    assert result["Lorentzian_covector_square"] == 1.0
    assert result["same_temporal_spatial_matrix"]
    tree = np.asarray(result["tree_derivative_matrix"])
    assert np.array_equal(tree, np.diag((1.0, 0.0, 0.0, 0.0)))
    with pytest.raises(ValueError):
        full_lorentzian_derivative_symbol(omega=0.0, spatial_eigenvalue=-1.0)


def test_uv_derivative_modes_are_not_physical_mass_modes():
    result = derivative_eigenmode_boundary()
    assert result["UV_derivative_eigendirections_action_derived"]
    assert not result["finite_canonical_fields_derived"]
    assert not result["zero_momentum_masslike_Hessian_derived"]
    assert not result["physical_lightest_or_broken_scalar_selected"]


def test_claim_boundary_and_materialization_are_conservative():
    claims = claim_boundary()
    assert claims["CURRENT_C2_FULL_FOUR_FIELD_DERIVATIVE_PRINCIPAL_POLE_DERIVED"]
    assert claims["CURRENT_C2_FAMILY_NONCENTRAL_LEPTON_KINETIC_RANK_TWO_DERIVED"]
    assert not claims["CURRENT_C2_FINITE_FULL_SCALAR_KINETIC_MATRIX_DERIVED"]
    assert not claims["CURRENT_C2_PHYSICAL_SINGLE_HIGGS_DIRECTION_SELECTED"]
    assert not exact_remaining_owner()["old_EC_residue_or_fitted_scalar_normalization_allowed"]
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
