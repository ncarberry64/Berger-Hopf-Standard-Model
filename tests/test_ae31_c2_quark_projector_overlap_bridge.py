import hashlib

import pytest

from bhsm.interface.ae31_c2_quark_projector_overlap_bridge import (
    action_trace_bifurcation,
    basis_invariance_witness,
    claim_boundary,
    current_family_projector_contract,
    exact_remaining_owner,
    projector_overlap_response,
)
from scripts.materialize_ae31_c2_quark_projector_overlap_bridge import (
    TARGET,
    build_payload,
    main,
)


P_ACTIVE = ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0))
P_SINGLET = ((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))
M_H = ((0, 0, 1, 0), (0, 0, 0, 2), (0, 0, 0, 0), (0, 0, 0, 0))


def test_projector_overlap_is_nonnegative_hilbert_schmidt_norm():
    result = projector_overlap_response(
        active_projector=P_ACTIVE, scalar_map=M_H, singlet_projector=P_SINGLET
    )
    assert result["response"] == 5.0
    assert result["hilbert_schmidt_residual"] < 1e-12
    assert result["nonnegative"]
    assert not result["physical_yukawa_residue_promoted"]


def test_projector_overlap_rejects_nonprojectors():
    with pytest.raises(ValueError):
        projector_overlap_response(
            active_projector=((1, 0), (0, 2)),
            scalar_map=((0, 1), (0, 0)),
            singlet_projector=((0, 0), (0, 1)),
        )


def test_basis_rotation_changes_entry_not_projector_sum():
    witness = basis_invariance_witness()
    assert witness["single_vector_amplitude_basis_dependent"]
    assert witness["projector_sum_invariance_residual"] < 1e-12
    assert witness["projectors_unchanged_residual"] < 1e-12


def test_current_family_contract_reuses_exact_modes():
    contract = current_family_projector_contract()
    assert contract["up_modes_k_j"] == [[0, 0], [6, 0], [10, 1]]
    assert contract["down_modes_k_j"] == [[0, 0], [6, 3], [8, 2]]
    assert contract["remaining_m_basis_may_rotate"]
    assert not contract["particle_spectrum_rebuilt"]


def test_full_trace_and_selected_state_are_not_conflated():
    theorem = action_trace_bifurcation()
    assert theorem["full_multiplet_trace"]["basis_invariant"]
    assert not theorem["full_multiplet_trace"]["m_selection_required"]
    assert theorem["selected_vector_or_density"]["m_or_density_selection_required"]
    assert theorem["selected_vector_or_density"]["projector_trace_cannot_choose_the_state"]


def test_remaining_owner_does_not_relabel_historical_targets():
    owner = exact_remaining_owner()
    assert not owner["historical_boundary_targets_relabelled_as_residues"]
    assert not owner["individual_m_guessed_or_fitted"]
    boundary = claim_boundary()
    assert boundary["CURRENT_C2_QUARK_PROJECTOR_OVERLAP_FUNCTIONAL_DERIVED"]
    assert not boundary["CURRENT_C2_UP_DOWN_YUKAWA_VERTEX_RESIDUES_ACTION_DERIVED"]


def test_materialized_projector_bridge_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
