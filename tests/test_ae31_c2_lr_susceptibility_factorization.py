import hashlib
import math

import numpy as np
import pytest

from bhsm.interface.ae31_c2_lr_susceptibility_factorization import (
    claim_boundary,
    composite_hessian_decomposition,
    current_c2_slice_susceptibility,
    exact_remaining_owner,
    finite_state_remainder_witness,
    hadamard_pole_factorization,
)
from scripts.materialize_ae31_c2_lr_susceptibility_factorization import (
    TARGET,
    build_payload,
    main,
)


def test_current_c2_slice_sum_scales_as_inverse_radius_squared():
    first = current_c2_slice_susceptibility(8, 1.0)
    second = current_c2_slice_susceptibility(8, 2.0)
    assert first["positive"]
    assert math.isclose(first["susceptibility"], 4.0 * second["susceptibility"])
    assert not first["global_frequency_diagonalization_used"]
    assert not first["slice_sum_promoted_to_Feynman_loop"]
    with pytest.raises(ValueError):
        current_c2_slice_susceptibility(8, 0.0)


def test_hadamard_pole_is_identity_in_unit_incidence_coordinates():
    result = hadamard_pole_factorization()
    assert result["incidence_Gram_matrix"] == [[2.0, 0.0], [0.0, 2.0]]
    assert result["normalized_channel_pole_matrix"] == [[1.0, 0.0], [0.0, 1.0]]
    assert result["pole_is_state_independent_within_Hadamard_class"]
    assert not result["physical_intrinsic_Higgs_residues_inserted"]
    assert not result["finite_local_HdaggerH_subtraction_selected"]


def test_exact_gauge_inverse_trace_traceless_decomposition():
    result = composite_hessian_decomposition()
    assert result["inverse_kernel_trace_coefficient"] == "135/364/G_C2"
    assert result["inverse_kernel_traceless_coefficient"] == "-5/364/G_C2"
    assert result["inverse_kernel_up_minus_down"] == "-5/182/G_C2"
    assert np.asarray(result["universal_Hadamard_pole_traceless_projection"]).shape == (2, 2)
    assert not result["universal_pole_changes_relative_channel_direction"]
    assert result["gauge_inverse_curvature_orders_up_below_down_for_positive_G_C2"]


def test_finite_smooth_remainder_can_still_rotate_direction():
    result = finite_state_remainder_witness()
    assert result["finite_response_difference_norm"] > 0.0
    assert result["traceless_finite_difference_norm"] > 0.0
    assert result["finite_remainder_can_change_channel_eigenvectors"]
    assert not result["witness_is_BHSM_physical_covariance"]
    assert not result["universal_pole_factorization_selects_physical_direction"]


def test_claim_boundary_and_remaining_owner_are_conservative():
    claims = claim_boundary()
    assert claims["CURRENT_C2_LR_HADAMARD_UV_POLE_FACTOR_DERIVED"]
    assert claims["CURRENT_C2_LR_COMMON_POLE_TRACeless_CANCELLATION_DERIVED"]
    assert not claims["CURRENT_C2_FULL_RENORMALIZED_LR_HESSIAN_DERIVED"]
    assert not claims["CURRENT_C2_COMPOSITE_GAP_DERIVED"]
    owner = exact_remaining_owner()
    assert not owner["cutoff_or_fitted_subtraction_allowed"]
    assert not owner["arbitrary_Hadamard_state_allowed"]


def test_materialized_factorization_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
