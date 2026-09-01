import hashlib

import pytest

from bhsm.interface.ae31_c2_universal_scalar_profile_transport import (
    canonical_discrete_normalization,
    claim_boundary,
    conjugate_channel_universality,
    current_c2_tensor_domain_transport,
    exact_remaining_owner,
    finite_projector_response_bound,
    provenance_and_action_gate,
    universal_profile_operator,
)
from scripts.materialize_ae31_c2_universal_scalar_profile_transport import (
    TARGET,
    build_payload,
    main,
)


def test_universal_profile_is_bounded_multiplication_operator():
    result = universal_profile_operator(distances=(0, 0.5, 1), sigma=1.25, phi0=2)
    assert result["operator_norm"] == 2.0
    assert result["bound_residual"] == 0.0
    assert not result["flavor_dependent_width_inserted"]


def test_universal_profile_rejects_invalid_domain_data():
    with pytest.raises(ValueError):
        universal_profile_operator(distances=(-1, 0), sigma=1, phi0=1)
    with pytest.raises(ValueError):
        universal_profile_operator(distances=(0, 1), sigma=-1, phi0=1)


def test_canonical_amplitude_has_unit_weighted_norm():
    result = canonical_discrete_normalization(
        distances=(0, 0.5, 1), measure_weights=(0.2, 0.5, 0.3), sigma=1.25
    )
    assert result["unit_norm_residual"] < 1e-12
    assert not result["independent_amplitude_after_canonical_normalization"]
    assert not result["BHSM_profile_measure_numerically_evaluated"]


def test_bounded_internal_profile_preserves_current_c2_domain():
    theorem = current_c2_tensor_domain_transport(profile_values=(1, 0.7, 0.2))
    assert theorem["sample_commutator_residual"] == 0.0
    assert theorem["bounded_internal_multiplier_preserves_Domain_D_C2_tensor_I"]
    assert theorem["retained_birth_trace_unchanged"]
    assert not theorem["endpoint_boundary_condition_reselected"]


def test_finite_projector_response_has_exact_bound():
    result = finite_projector_response_bound(
        active_projector=((1, 0, 0), (0, 1, 0), (0, 0, 0)),
        scalar_map=((2, 0, 0), (0, 1, 0), (0, 0, 0.5)),
        singlet_projector=((0, 0, 0), (0, 1, 0), (0, 0, 1)),
    )
    assert result["bound_residual"] == 0.0
    assert result["compressed_operator_is_hilbert_schmidt"]
    assert not result["global_uncompressed_trace_class_assumed"]


def test_profile_conjugation_does_not_force_equal_sector_responses():
    theorem = conjugate_channel_universality()
    assert theorem["one_universal_profile"]
    assert theorem["equal_operator_norms_for_conjugate_profile"]
    assert not theorem["equal_up_down_projector_responses_forced"]


def test_action_gate_preserves_conditional_status():
    gate = provenance_and_action_gate()
    assert gate["conditional_transport_is_not_action_ownership"]
    assert not gate["sigma_action_derived_in_current_AE31"]
    assert not gate["intrinsic_M4_H_to_internal_profile_attachment_action_derived"]
    owner = exact_remaining_owner()
    assert not owner["m_weight_required_if_full_multiplet_trace_selected"]
    boundary = claim_boundary()
    assert boundary["CURRENT_C2_FINITE_PROJECTOR_OVERLAP_TRACE_FINITE"]
    assert not boundary["CURRENT_C2_UP_DOWN_YUKAWA_VERTEX_RESIDUES_ACTION_DERIVED"]


def test_materialized_profile_transport_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
