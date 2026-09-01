"""Current-C2 coexact SU(2)_L charged current and family-kernel theorem."""

from __future__ import annotations

from typing import Any

import numpy as np

from bhsm.interface.ae3_c2_coexact_hypercharge import (
    lowest_weyl_coexact_hypercharge_source_jet,
)
from bhsm.interface.ae3_c2_hopf_semigroup_transport import (
    frozen_internal_semigroup_attachment,
)


ACTION_VERSION = "BHSM-AE-3.1.0"
CLASSIFICATION = "CURRENT_C2_COEXACT_SU2L_CHARGED_CURRENT_AND_FAMILY_KERNEL"


def weak_charged_representation_ledger() -> dict[str, Any]:
    """Return the exact raising/lowering action on retained SM doublets."""

    t_plus = np.asarray(((0.0, 1.0), (0.0, 0.0)), dtype=complex)
    t_minus = t_plus.conjugate().T
    t1 = 0.5 * (t_plus + t_minus)
    t2 = (t_plus - t_minus) / (2.0j)
    one_family_trace = 3.0 + 1.0
    return {
        "doublet_order": {
            "Q_L": ["u_L", "d_L"],
            "L_L": ["nu_L", "e_L"],
        },
        "singlets_annihilated": ["u_c", "d_c", "e_c", "nu_c"],
        "T_plus": "[[0,1],[0,0]]",
        "T_minus": "[[0,0],[1,0]]",
        "T1": "(T_plus+T_minus)/2",
        "T2": "(T_plus-T_minus)/(2i)",
        "T_minus_is_T_plus_adjoint": bool(np.array_equal(t_minus, t_plus.conjugate().T)),
        "commutator_Tplus_Tminus": (
            t_plus @ t_minus - t_minus @ t_plus
        ).real.tolist(),
        "one_family_trace_Tminus_Tplus": one_family_trace,
        "three_family_trace_Tminus_Tplus": 3.0 * one_family_trace,
        "family_action": "I3",
        "color_action": "I3_color_ON_Q_L",
        "charged_current": (
            "J_plus^mu=sum_family[sum_color(bar(u_L)gamma^mu d_L)+"
            "bar(nu_L)gamma^mu e_L]"
        ),
        "independent_family_matrix_inserted": False,
    }


def lowest_weyl_coexact_su2l_charged_source_jets(
    *,
    proper_durations: np.ndarray,
    inverse_radii: np.ndarray,
    source_profile: np.ndarray,
    chirality: int,
) -> dict[str, Any]:
    """Attach the two Hermitian coexact coordinates whose complex pair is W+/-.

    The C2 finite-element coordinate jet is the already derived unit coexact
    shape.  T1 and T2 are orthogonal equal-norm SU(2) generators, so the same
    shape applies to both.  Their complex recombination defines the adjoint
    W+ and W- source pair without introducing a new normalization.
    """

    base = lowest_weyl_coexact_hypercharge_source_jet(
        proper_durations=proper_durations,
        inverse_radii=inverse_radii,
        source_profile=source_profile,
        chirality=chirality,
    )
    return {
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "source_kind": "SPATIAL_COEXACT_SU2L_CHARGED_W1_W2",
        "chirality": int(chirality),
        "segments": base["segments"],
        "W1_vertex_elements": base["vertex_elements"],
        "W2_vertex_elements": base["vertex_elements"].copy(),
        "W1_contact_elements": base["contact_elements"],
        "W2_contact_elements": base["contact_elements"].copy(),
        "complex_pair": "W_plus=(W1-i*W2)/sqrt(2);_W_minus=W_plus_dagger",
        "current_pair": "J_plus=bar(Psi_L)*gamma*T_plus*Psi_L;_J_minus=J_plus_dagger",
        "equal_coordinate_normalization_inherited": True,
        "new_g2_or_source_coefficient_added": False,
        "physical_W_pole_derived": False,
    }


def canonical_quark_family_kernel() -> dict[str, Any]:
    """Evaluate the family action of the current on attached up/down shapes."""

    attachment = frozen_internal_semigroup_attachment()["sectors"]
    up = np.asarray(attachment["up"]["family_operator"], dtype=float)
    down = np.asarray(attachment["down"]["family_operator"], dtype=float)
    identity = np.eye(3, dtype=complex)
    h_up = up @ up.T
    h_down = down @ down.T
    commutator = h_up @ h_down - h_down @ h_up
    return {
        "common_left_handed_family_space": "C3_family",
        "raising_current_family_kernel": identity.real.tolist(),
        "kernel_rank": int(np.linalg.matrix_rank(identity)),
        "kernel_unitary": True,
        "up_response_shape": up.tolist(),
        "down_response_shape": down.tolist(),
        "response_commutator": commutator.tolist(),
        "response_commutator_norm": float(np.linalg.norm(commutator)),
        "canonical_response_basis_CKM": identity.real.tolist(),
        "canonical_response_basis_Jarlskog": 0.0,
        "nontrivial_CKM_generated_by_current_family_identity": False,
        "why": (
            "THE_CURRENT_ACTS_AS_I3_ON_FAMILY_AND_BOTH_ATTACHED_RESPONSE_"
            "OPERATORS_ARE_DIAGONAL_IN_THE_SAME_FROZEN_PROJECTOR_BASIS"
        ),
        "middle_up_half_dressing_inserted": False,
        "why_half_excluded": (
            "Z_virt_u2=1/2_REMAINS_A_FROZEN_CONDITIONAL_DRESSING_OUTPUT_NOT_"
            "A_CURRENT_AE31_ACTION_TERM"
        ),
        "sector_absolute_prefactors_required_for_eigenvectors": False,
        "sector_absolute_prefactors_derived": False,
        "physical_CKM_matrix_derived": False,
        "nontrivial_CKM_requires": (
            "FAMILY_NONCENTRAL_ACTION_DRESSING_OF_THE_UP_DOWN_LEFT_EMBEDDINGS_"
            "OR_AN_EQUIVALENT_MIXED_SECOND_VARIATION"
        ),
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "current_C2_coexact_SU2L_charged_source_pair_derived": True,
        "current_C2_SU2L_raising_current_family_kernel_is_I3": True,
        "current_C2_canonical_quark_response_basis_CKM_is_I3": True,
        "present_action_nontrivial_CKM_derived": False,
        "physical_CKM_matrix_derived": False,
        "middle_up_virtual_dressing_promoted": False,
        "up_down_absolute_Yukawa_prefactors_derived": False,
        "physical_W_pole_derived": False,
        "measured_CKM_or_quark_mass_used": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "canonical_quark_family_kernel",
    "claim_boundary",
    "lowest_weyl_coexact_su2l_charged_source_jets",
    "weak_charged_representation_ledger",
]
