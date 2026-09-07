"""Local electromagnetic Ward identity for the current-C2 lepton block.

The structural neutral current and the family-noncentral charged-lepton mass
operator already coexist on current C2.  Their local tangent-frame vertex
satisfies the exact tree Ward--Takahashi identity because electric charge is
family central and commutes with the mass endomorphism.  This identity does
not normalize the photon or determine the transverse Pauli form factor.
"""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np

from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import (
    conditional_tree_mass_operator,
)
from bhsm.interface.ae31_c2_neutral_connection_hessian import (
    neutral_field_current_rotation,
)


ACTION_VERSION = "BHSM-AE-3.1.0"
CLASSIFICATION = "CURRENT_C2_LOCAL_ELECTROMAGNETIC_WARD_PAULI_DECOMPOSITION"


def _gamma_matrices() -> list[np.ndarray]:
    """Return Dirac gamma matrices for signature ``(+---)``."""

    sigma = [
        np.asarray(((0.0, 1.0), (1.0, 0.0)), dtype=complex),
        np.asarray(((0.0, -1.0j), (1.0j, 0.0)), dtype=complex),
        np.asarray(((1.0, 0.0), (0.0, -1.0)), dtype=complex),
    ]
    identity = np.eye(2, dtype=complex)
    zero = np.zeros((2, 2), dtype=complex)
    gamma_zero = np.block([[identity, zero], [zero, -identity]])
    gamma_space = [np.block([[zero, item], [-item, zero]]) for item in sigma]
    return [gamma_zero, *gamma_space]


def _slash(momentum: Sequence[float]) -> np.ndarray:
    value = np.asarray(momentum, dtype=float)
    if value.shape != (4,) or not np.all(np.isfinite(value)):
        raise ValueError("momentum must be a finite four-vector")
    gamma = _gamma_matrices()
    return gamma[0] * value[0] - sum(
        matrix * component for matrix, component in zip(gamma[1:], value[1:])
    )


def charged_lepton_qem_ledger() -> dict[str, Any]:
    """Attach the structural ``Q_em`` generator to the physical Dirac field."""

    rotation = neutral_field_current_rotation()
    return {
        "left_component": {
            "field": "e_L_in_L_L",
            "T3": -0.5,
            "Y_BH": -0.5,
            "Q_em": -1.0,
        },
        "left_handed_conjugate_ledger_component": {
            "field": "e_c",
            "T3": 0.0,
            "Y_BH": 1.0,
            "Q_em": 1.0,
        },
        "physical_right_component": {
            "field": "e_R=charge_conjugate(e_c)",
            "Q_em": -1.0,
        },
        "Dirac_charge_operator": "Q_l=-I4_spinor tensor I3_family",
        "Higgs_vacuum_charge": 0.0,
        "mass_term_charge_balance": "Q(bar(e_L))+Q(H_0)+Q(e_R)=1+0-1=0",
        "mass_endomorphism_commutes_with_Qem": True,
        "current_source": rotation["Q_em_current"],
        "current_C2_source_domain_attached": rotation["same_current_C2_source_domain"],
        "photon_normalization_used": False,
    }


def local_ward_identity_witness(
    momentum: Sequence[float] = (3.0, 0.4, -0.2, 0.7),
    transfer: Sequence[float] = (0.3, -0.1, 0.5, 0.2),
) -> dict[str, Any]:
    """Verify ``q.Gamma=Q S^-1(p+q)-S^-1(p) Q`` for three families."""

    p = np.asarray(momentum, dtype=float)
    q = np.asarray(transfer, dtype=float)
    if p.shape != (4,) or q.shape != (4,):
        raise ValueError("momentum and transfer must be four-vectors")
    masses = np.asarray(
        conditional_tree_mass_operator()["eigenvalues_GeV_heavy_middle_light"],
        dtype=float,
    )
    family_identity = np.eye(masses.size, dtype=complex)
    spin_identity = np.eye(4, dtype=complex)
    mass = np.kron(spin_identity, np.diag(masses))
    charge = -np.eye(4 * masses.size, dtype=complex)
    inverse_p = np.kron(_slash(p), family_identity) - mass
    inverse_pq = np.kron(_slash(p + q), family_identity) - mass
    contracted_vertex = charge @ np.kron(_slash(q), family_identity)
    right_hand_side = charge @ inverse_pq - inverse_p @ charge
    gamma = _gamma_matrices()
    metric = np.diag((1.0, -1.0, -1.0, -1.0))
    clifford_residual = max(
        float(
            np.linalg.norm(
                gamma[mu] @ gamma[nu] + gamma[nu] @ gamma[mu]
                - 2.0 * metric[mu, nu] * np.eye(4),
                ord=2,
            )
        )
        for mu in range(4)
        for nu in range(4)
    )
    return {
        "family_order": ["heavy", "middle", "light"],
        "conditional_mass_eigenvalues_GeV": masses.tolist(),
        "charge_eigenvalue_each_family": -1.0,
        "Clifford_residual": clifford_residual,
        "mass_charge_commutator_residual": float(
            np.linalg.norm(mass @ charge - charge @ mass, ord=2)
        ),
        "Ward_Takahashi_residual": float(
            np.linalg.norm(contracted_vertex - right_hand_side, ord=2)
        ),
        "identity": "q_mu*Gamma_Q^mu=Q*S_inv(p+q)-S_inv(p)*Q",
        "vertex": "Gamma_Q^mu=Q_l*gamma^mu",
        "same_identity_for_all_three_family_projectors": True,
        "measured_mass_used": False,
        "canonical_photon_residue_used": False,
    }


def pauli_transversality_witness(
    transfer: Sequence[float] = (0.3, -0.1, 0.5, 0.2)
) -> dict[str, Any]:
    """Prove that the Pauli tensor is invisible to the Ward contraction."""

    q = np.asarray(transfer, dtype=float)
    if q.shape != (4,) or not np.all(np.isfinite(q)):
        raise ValueError("transfer must be a finite four-vector")
    gamma = _gamma_matrices()
    q_covariant = np.asarray((q[0], -q[1], -q[2], -q[3]))
    sigma = np.empty((4, 4, 4, 4), dtype=complex)
    for mu in range(4):
        for nu in range(4):
            sigma[mu, nu] = 0.5j * (
                gamma[mu] @ gamma[nu] - gamma[nu] @ gamma[mu]
            )
    contraction = sum(
        q_covariant[mu] * sigma[mu, nu] * q_covariant[nu]
        for mu in range(4)
        for nu in range(4)
    )
    return {
        "antisymmetry_residual": max(
            float(np.linalg.norm(sigma[mu, nu] + sigma[nu, mu], ord=2))
            for mu in range(4)
            for nu in range(4)
        ),
        "q_sigma_q_residual": float(np.linalg.norm(contraction, ord=2)),
        "on_shell_vertex_decomposition": (
            "Gamma^mu=F1(q^2)*gamma^mu+i*sigma^(mu nu)*q_nu*F2(q^2)/(2m)"
        ),
        "Ward_identity_constrains_longitudinal_vertex": True,
        "Ward_identity_determines_F2": False,
        "why": "q_mu*sigma^(mu nu)*q_nu=0_BY_ANTISYMMETRY",
        "minimal_tree_vertex_F1": -1.0,
        "minimal_tree_vertex_F2": 0.0,
        "tree_F2_is_quantum_muon_anomaly": False,
    }


def local_em_claim_boundary() -> dict[str, Any]:
    """Separate the exact local identity from physical photon promotion."""

    return {
        "CURRENT_C2_LOCAL_STRUCTURAL_QEM_VERTEX_DERIVED": True,
        "CURRENT_C2_LOCAL_TREE_WARD_TAKAHASHI_IDENTITY_DERIVED": True,
        "CURRENT_C2_PAULI_FORM_FACTOR_TRANSVERSALITY_DERIVED": True,
        "CURRENT_C2_MINIMAL_TREE_F2_ZERO_DERIVED": True,
        "CURRENT_C2_CANONICALLY_NORMALIZED_PHOTON_VERTEX_DERIVED": False,
        "CURRENT_C2_PHYSICAL_PHOTON_POLE_DERIVED": False,
        "CURRENT_C2_RENORMALIZED_MUON_VERTEX_DERIVED": False,
        "MUON_MAGNETIC_MOMENT_DERIVED": False,
        "interpretation": (
            "THE_LOCAL_CHARGE_IDENTITY_IS_CLOSED_BUT_F2_IS_A_TRANSVERSE_"
            "DYNAMICAL_FORM_FACTOR_REQUIRING_THE_PHYSICAL_PHOTON_AND_"
            "RENORMALIZED_STATE_DEPENDENT_VERTEX"
        ),
        "particle_spectrum_rebuilt": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "charged_lepton_qem_ledger",
    "local_em_claim_boundary",
    "local_ward_identity_witness",
    "pauli_transversality_witness",
]
