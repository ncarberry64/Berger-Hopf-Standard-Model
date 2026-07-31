from __future__ import annotations

import numpy as np
import pytest

from bhsm.interface.master_action import automatic_geometric_lens_theorem as v89
from bhsm.interface.master_action import complex_profile_isospectral_attachment as v86


def sample_forms():
    G = np.array([[2.0, 0.1j, 0.05], [-0.1j, 1.5, 0.08], [0.05, 0.08, 1.2]], complex)
    Q = np.array([[0.7, 0.12j, 0.03], [-0.12j, 1.8, 0.16], [0.03, 0.16, 3.1]], complex)
    return G, Q


def test_lens_canonical_normalization_and_diagonalization():
    G, Q = sample_forms()
    lens = v89.sector_lens(G, Q)
    assert lens["kinetic_orthonormality_residual"] < 1e-11
    assert lens["response_diagonalization_residual"] < 1e-11


def test_positive_square_root_is_unique_and_reconstructs():
    G, _ = sample_forms()
    root = v89.positive_sqrt(G)
    inv = v89.positive_inverse_sqrt(G)
    assert np.linalg.norm(root @ root - G) < 1e-11
    assert np.linalg.norm(inv @ G @ inv - np.eye(3)) < 1e-11


def test_rank_or_positivity_failure_is_fail_closed():
    with pytest.raises(ValueError):
        v89.positive_inverse_sqrt(np.diag([1.0, 1.0, 0.0]))


def test_degenerate_response_is_fail_closed():
    with pytest.raises(ValueError):
        v89.sector_lens(np.eye(3), np.diag([1.0, 1.0, 2.0]))


def test_physical_current_is_unitary():
    G, Q = sample_forms()
    K = np.array([[1, 0.2j, 0.1], [0.1, 1, -0.15j], [0.05j, 0.2, 1]], complex)
    result = v89.physical_current_from_action_forms(G, Q, K, G, Q + np.diag([0.1, 0.2, 0.4]))
    assert result["current_unitarity_residual"] < 1e-11


def test_phase_free_projector_moduli_match_frame_matrix():
    G, Q = sample_forms()
    K = np.array([[1, 0.2j, 0.1], [0.1, 1, -0.15j], [0.05j, 0.2, 1]], complex)
    result = v89.physical_current_from_action_forms(G, Q, K, G, Q + np.diag([0.1, 0.2, 0.4]))
    audit = v89.phase_free_audit(result)
    assert audit["moduli_residual"] < 1e-10
    assert audit["jarlskog_residual"] < 1e-10


def test_commutator_jarlskog_identity():
    Hu = np.diag([0.4, 1.3, 3.2])
    Hd = np.diag([0.2, 1.1, 2.5])
    U = v86.polar_unitary(
        np.array([[1, 0.2j, 0.1], [0.2, 1, -0.3j], [0.1j, 0.25, 1]], complex)
    )
    invariant = v89.invariant_jarlskog(Hu, U, Hd)
    frame = v86.jarlskog(U)
    assert abs(invariant - frame) < 1e-10


def test_basis_invariant_observables():
    audit = v89.basis_covariance_audit()
    assert audit["basis_invariant_observables"]


def test_proxy_theorem_domain_passes_without_promotion():
    payload = v89.payload()
    assert payload["validation"]["all_passed"]
    assert not payload["validation"]["physical_CKM_promoted"]
    assert not payload["validation"]["new_continuous_parameter"]

