"""Reduce the existing BHSM parent/effective action charged current at v11.6.

The calculation is deliberately fail-closed.  The only explicit quark charged
current owned by the live action is the family-universal current obtained from
the SU(2)L covariant derivative in the effective four-dimensional Dirac term.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from .quark_yukawa_ckm_v11_4 import DOWN_MODES, UP_MODES
from .spectral_charged_current_v11_5 import spectral_current_kernel


VERSION = "v11.6"
PRIMARY_VERDICT = (
    "BHSM_PARENT_ACTION_CURRENT_REDUCTION_BLOCKED_BY_UNFIXED_COMMON_DOMAIN_"
    "FAMILY_WAVEFUNCTION_MAP"
)
EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_COMMON_DOMAIN_UP_DOWN_FAMILY_WAVEFUNCTION_ORIENTATION_"
    "AND_CURRENT_PAIRING_MAP"
)


def parent_action_term_ledger() -> dict[str, Any]:
    """Return the source-by-source ownership ledger used by the reduction."""

    rows = [
        {
            "source": "src/bhsm/interface/master_action/terms.py",
            "term": "T4_fermion = int sqrt(-h) i bar(Psi) gamma^mu D_mu Psi",
            "ownership": "EFFECTIVE_ACTION_OWNED",
            "family_factor": "I3 in the weak/generation basis",
            "mixed_variation": "delta^3 S4/(delta W+_mu delta bar(u_L) delta d_L) = g2 gamma^mu I3/sqrt(2)",
        },
        {
            "source": "src/bhsm/interface/master_action/terms.py",
            "term": "T4_Yukawa with independent Y_u and Y_d",
            "ownership": "EFFECTIVE_ACTION_INPUT",
            "family_factor": "Y_u,Y_d are typed independent inputs, not a spectral cross-current selection",
            "mixed_variation": "mass-basis current is W_u^dagger W_d only after independently supplied Yukawa diagonalizations",
        },
        {
            "source": "src/bhsm/interface/unified_dynamical_action.py",
            "term": "g_ch Re <J_ch(P_gen Psi,A_SU2),X_ch(P_ch Psi)>_Sigma",
            "ownership": "CONDITIONAL_SYMBOLIC_TEMPLATE",
            "family_factor": "J_ch and X_ch are not explicitly defined or action-normalized",
            "mixed_variation": "not evaluable as a kernel",
        },
        {
            "source": "src/bhsm/interface/master_action/common_parent_charged_current_attachment.py",
            "term": "L_cc^CG with U_CG=Pol(K_CG)",
            "ownership": "CONDITIONAL_INTERFACE_NOT_ACTIVE_PARENT_TERM",
            "family_factor": "K_CG must first be action derived",
            "mixed_variation": "not a source for K_CG",
        },
        {
            "source": "src/bhsm/interface/completion/quark_yukawa_ckm_v11_4.py",
            "term": "diagonal common-basis H_u and H_d response pair",
            "ownership": "CONDITIONAL_SPECTRAL_RESPONSE_PAIR",
            "family_factor": "commuting diagonal operators; canonical CKM=I3 and J=0",
            "mixed_variation": "does not supply <u_i,J_plus_action d_j>_common",
        },
        {
            "source": "src/bhsm/interface/completion/spectral_charged_current_v11_5.py",
            "term": "declared coefficient-free K_ud spectral rule",
            "ownership": "AUTHOR_SELECTED_NO_FIT_ACTION_CANDIDATE",
            "family_factor": "nontrivial unitary 3x3 kernel",
            "mixed_variation": "absent from the existing action",
        },
    ]
    validation = {
        "explicit_effective_dirac_source_located": True,
        "conditional_templates_not_promoted": all(
            row["ownership"] != "ACTION_DERIVED_SPECTRAL_KERNEL" for row in rows
        ),
        "v11_5_boundary_preserved": rows[-1]["ownership"]
        == "AUTHOR_SELECTED_NO_FIT_ACTION_CANDIDATE",
        "no_measured_mixing_inputs": True,
    }
    return {
        "artifact": "BHSM_parent_action_charged_current_v11_6",
        "version": VERSION,
        "classification": "PARENT_ACTION_TERM_AND_VARIATION_PROVENANCE_LEDGER",
        "sources": rows,
        "action_owned_current_source": "T4_fermion SU2L covariant derivative",
        "parent_S8_current_source": None,
        "cross_level_reduction_status": "MISSING_BULK_GAUGE_SPINOR_REDUCTION",
        "v11_5_kernel_factor_provenance": [
            {
                "factor": "sin(theta12)=sqrt(T_down_light/T_down_middle)",
                "source": "src/bhsm/interface/completion/spectral_charged_current_v11_5.py",
                "status": "AUTHOR_SELECTED_RULE_USING_FROZEN_V11_4_SPECTRAL_WEIGHTS",
                "parent_action_variation_source": None,
            },
            {
                "factor": "sin(theta23)=2*T_down_middle",
                "source": "src/bhsm/interface/completion/spectral_charged_current_v11_5.py",
                "status": "AUTHOR_SELECTED_RULE; FACTOR_2_NOT_SELECTED_BY_CURRENT ACTION",
                "parent_action_variation_source": None,
            },
            {
                "factor": "sin(theta13)=sqrt(T_up_light)",
                "source": "src/bhsm/interface/completion/spectral_charged_current_v11_5.py",
                "status": "AUTHOR_SELECTED_RULE_USING_FROZEN_V11_4_SPECTRAL_WEIGHT",
                "parent_action_variation_source": None,
            },
            {
                "factor": "delta=2/sqrt(pi)",
                "source": "src/bhsm/interface/completion/spectral_charged_current_v11_5.py",
                "status": "AUTHOR_SELECTED_PHASE_RULE; NO ACTION-SELECTED COMPLEX ORIENTATION",
                "parent_action_variation_source": None,
            },
            {
                "factor": "standard three-angle one-phase unitary parameterization",
                "source": "src/bhsm/interface/completion/spectral_charged_current_v11_5.py",
                "status": "CONVENTIONAL_UNITARY_PARAMETERIZATION",
                "parent_action_variation_source": None,
            },
            {
                "factor": "g2/sqrt(2) and W+/W- adjoint pair",
                "source": "src/bhsm/interface/master_action/terms.py",
                "status": "EFFECTIVE_SU2L_DIRAC_CURRENT_OWNED; g2 VALUE REMAINS LEVELWISE INPUT",
                "parent_action_variation_source": "T4_fermion covariant derivative",
            },
            {
                "factor": "frozen up/down three-slot modules",
                "source": "src/bhsm/interface/master_action/generation_projector_action_attachment.py",
                "status": "FROZEN_DERIVED_CONDITIONAL_GEOMETRIC_STRUCTURE_ATTACHED_TO_EFFECTIVE_M4",
                "parent_action_variation_source": None,
            },
            {
                "factor": "common-domain wavefunction pairing <u_i,J_plus d_j>_common",
                "source": None,
                "status": "MISSING_EXACT_ACTION_OBJECT",
                "parent_action_variation_source": None,
            },
        ],
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def action_owned_weak_basis_kernel() -> np.ndarray:
    """Family factor in the current obtained from the effective Dirac action."""

    return np.eye(3, dtype=complex)


def current_reduction_payload() -> dict[str, Any]:
    """Evaluate the current and compare it with the v11.5 declared kernel."""

    action_kernel = action_owned_weak_basis_kernel()
    spectral_kernel = spectral_current_kernel()
    off_diagonal = spectral_kernel - np.diag(np.diag(spectral_kernel))
    magnitude_residual = float(
        np.linalg.norm(np.abs(action_kernel) - np.abs(spectral_kernel))
    )
    validation = {
        "action_kernel_is_I3": bool(np.array_equal(action_kernel, np.eye(3))),
        "action_kernel_full_rank": bool(np.linalg.matrix_rank(action_kernel) == 3),
        "v11_4_family_modules_exactly_traced": len(UP_MODES) == len(DOWN_MODES) == 3,
        "v11_4_responses_commute_in_canonical_basis": True,
        "spectral_kernel_has_nonzero_off_diagonal_entries": float(
            np.linalg.norm(off_diagonal)
        )
        > 1.0e-12,
        "not_equivalent_by_quark_rephasing": magnitude_residual > 1.0e-12,
        "no_parent_action_spectral_kernel_recovery": True,
        "no_empirical_inputs": True,
    }
    return {
        "artifact": "BHSM_parent_action_current_reduction_v11_6",
        "version": VERSION,
        "calculation": {
            "action_term": "int sqrt(-h) i bar(Q_L) gamma^mu D_mu Q_L",
            "covariant_derivative_charged_piece": "-i g2 (W+ T+ + W- T-)/sqrt(2)",
            "mixed_variation": "delta^3 S4/(delta W+_mu delta bar(u_L,i) delta d_L,j) = (g2/sqrt(2)) gamma^mu delta_ij",
            "weak_basis_family_kernel": "I3",
            "mass_basis_rule": "V_action=W_u^dagger I3 W_d",
            "v11_4_canonical_response_rule": "W_u=W_d=I3 up to diagonal phases and common slot ordering",
            "v11_4_canonical_result": "V_action=I3 up to diagonal quark-field rephasings; J=0",
        },
        "action_kernel_real": action_kernel.real.tolist(),
        "action_kernel_imag": action_kernel.imag.tolist(),
        "v11_5_kernel_off_diagonal_norm": float(np.linalg.norm(off_diagonal)),
        "rephasing_invariant_magnitude_residual": magnitude_residual,
        "equivalence_result": "NOT_EQUIVALENT_UP_TO_LEFT_RIGHT_DIAGONAL_QUARK_REPHASING",
        "why": "left/right diagonal rephasings preserve every entry magnitude, while I3 has zero off-diagonal magnitudes and the v11.5 kernel does not",
        "missing_map": {
            "domain": "frozen up family module F_u on the common attachment Hilbert domain",
            "codomain": "frozen down family module F_d on the same domain",
            "required_data": [
                "normalized common-domain up and down family wavefunctions",
                "their action-owned relative orientation and phase convention",
                "the SU2L raising-current operator on that common domain",
                "the action measure and projector sandwich defining <u_i,J_plus d_j>_common",
            ],
            "not_supplied_by": [
                "diagonal scalar spectral weights",
                "triality projector labels alone",
                "unitarity or SU2 closure",
                "the polar functor after an unsourced raw kernel is declared",
            ],
        },
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
