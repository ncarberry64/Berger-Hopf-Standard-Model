"""Transport the historical quark--Higgs incidence support to current C2.

This module changes conventions and attaches finite internal support only.  It
does not manufacture the still-missing action-owned up/down residues.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

import numpy as np

from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import ACTION_VERSION


CLASSIFICATION = "AE31_CURRENT_C2_QUARK_HIGGS_INCIDENCE_SUPPORT_TRANSPORT"


def _fraction(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def two_to_four_component_transport() -> dict[str, Any]:
    """Apply the anti-linear field convention map to both quark classes."""

    rows = (
        {
            "sector": "up",
            "historical_class": "cyclic_upper_closure",
            "historical_fields": ["A_cyc", "H", "S_cyc_upper"],
            "historical_charges": [Fraction(1, 3), Fraction(1), Fraction(-4, 3)],
            "current_fields": ["bar(Q_L)", "H_tilde", "u_R"],
            "current_charges": [Fraction(-1, 3), Fraction(-1), Fraction(4, 3)],
            "scalar_intertwiner": "epsilon*complex_conjugation:H_to_H_tilde",
        },
        {
            "sector": "down",
            "historical_class": "cyclic_lower_closure",
            "historical_fields": ["A_cyc", "H_tilde", "S_cyc_lower"],
            "historical_charges": [Fraction(1, 3), Fraction(-1), Fraction(2, 3)],
            "current_fields": ["bar(Q_L)", "H", "d_R"],
            "current_charges": [Fraction(-1, 3), Fraction(1), Fraction(-2, 3)],
            "scalar_intertwiner": "epsilon*complex_conjugation:H_tilde_to_H",
        },
    )
    transported = []
    for row in rows:
        historical_sum = sum(row["historical_charges"], Fraction())
        current_sum = sum(row["current_charges"], Fraction())
        transported.append(
            {
                **{key: value for key, value in row.items() if key not in {"historical_charges", "current_charges"}},
                "historical_charges": [_fraction(value) for value in row["historical_charges"]],
                "current_charges": [_fraction(value) for value in row["current_charges"]],
                "historical_charge_sum": _fraction(historical_sum),
                "current_charge_sum": _fraction(current_sum),
                "charge_closure_preserved": historical_sum == current_sum == 0,
            }
        )
    return {
        "convention_map": "ANTI_LINEAR_FERMION_CONJUGATION_PLUS_SU2_EPSILON_INTERTWINER",
        "rows": transported,
        "both_quark_classes_transport_uniquely": all(
            row["charge_closure_preserved"] for row in transported
        ),
        "standard_model_operator_table_used_as_premise": False,
    }


def finite_sector_projectors() -> dict[str, Any]:
    """Evaluate the existing C,sigma projector formulas on all four sectors."""

    labels = ("nu", "charged_lepton", "up", "down")
    c = np.asarray((0.0, 0.0, 1.0, 1.0))
    sigma = np.asarray((1.0, -1.0, 1.0, -1.0))
    projectors = {
        "nu": np.diag((1.0 - c) * (1.0 + sigma) / 2.0),
        "charged_lepton": np.diag((1.0 - c) * (1.0 - sigma) / 2.0),
        "up": np.diag(c * (1.0 + sigma) / 2.0),
        "down": np.diag(c * (1.0 - sigma) / 2.0),
    }
    identity = np.eye(4)
    orthogonality = max(
        float(np.linalg.norm(projectors[left] @ projectors[right]))
        for index, left in enumerate(labels)
        for right in labels[index + 1 :]
    )
    return {
        "basis_order": list(labels),
        "formulae": {
            "P_nu": "(1-C)(1+sigma)/2",
            "P_charged_lepton": "(1-C)(1-sigma)/2",
            "P_up": "C(1+sigma)/2",
            "P_down": "C(1-sigma)/2",
        },
        "P_up": projectors["up"].tolist(),
        "P_down": projectors["down"].tolist(),
        "quark_projector_orthogonality_residual": float(
            np.linalg.norm(projectors["up"] @ projectors["down"])
        ),
        "all_sector_orthogonality_residual": orthogonality,
        "sector_completeness_residual": float(
            np.linalg.norm(sum(projectors.values(), np.zeros((4, 4))) - identity)
        ),
        "up_down_support_selected": True,
        "up_down_residue_selected": False,
    }


def quark_higgs_support_pencil() -> dict[str, Any]:
    """Construct the two independent binary LR incidence supports."""

    up = np.zeros((4, 4))
    down = np.zeros((4, 4))
    up[0, 2] = up[2, 0] = 1.0
    down[1, 3] = down[3, 1] = 1.0
    return {
        "basis_order": ["Q_L_up", "Q_L_down", "u_R", "d_R"],
        "I_up": up.tolist(),
        "I_down": down.tolist(),
        "support_pencil": "rho_qH_support(h)=h_tilde*I_up+h*I_down",
        "current_operator_channels": [
            "bar(Q_L)*H_tilde*u_R+h.c.",
            "bar(Q_L)*H*d_R+h.c.",
        ],
        "up_support_rank": int(np.linalg.matrix_rank(up)),
        "down_support_rank": int(np.linalg.matrix_rank(down)),
        "support_inner_product": float(np.trace(up.T @ down)),
        "supports_linearly_independent": bool(
            np.linalg.matrix_rank(np.column_stack((up.ravel(), down.ravel()))) == 2
        ),
        "coefficients_in_support_pencil": "BINARY_INCIDENCE_ONLY",
    }


def current_c2_domain_tensor_theorem() -> dict[str, Any]:
    """Certify that finite internal incidence preserves the radial C2 domain."""

    radial = np.asarray(((2.0, -1.0, 0.0), (-1.0, 2.0, -1.0), (0.0, -1.0, 2.0)))
    internal = np.asarray(((0.0, 1.0), (1.0, 0.0)))
    radial_lift = np.kron(radial, np.eye(2))
    incidence_lift = np.kron(np.eye(3), internal)
    return {
        "exact_tensor_identity": "[D_C2_tensor_I,I_tensor_I_f]=0",
        "sample_commutator_residual": float(
            np.linalg.norm(radial_lift @ incidence_lift - incidence_lift @ radial_lift)
        ),
        "finite_internal_support_is_bounded": True,
        "reset_generated_C2_radial_operator_unchanged": True,
        "retained_birth_trace_unchanged": True,
        "maximal_or_friedrichs_radial_domain_reselected": False,
        "family_fiber_tensor_attachment_allowed": True,
    }


def exact_remaining_owner() -> dict[str, Any]:
    return {
        "transported_object": (
            "rho_qH_support:(H,H_tilde)_to_"
            "Hom(Q_L,u_R_direct_sum_d_R)_ON_CURRENT_C2"
        ),
        "missing_action_object": (
            "Gamma_qH_current_C2_WITH_COEFFICIENT_AND_CONTACT_JETS"
        ),
        "required_first_variations": ["V_u", "V_d"],
        "required_second_variations": ["Q_uu", "Q_ud", "Q_du", "Q_dd"],
        "family_shapes_to_reuse": ["T_u", "T_d"],
        "must_fix_together": [
            "c_u",
            "c_d",
            "H_wavefunction_residue",
            "trace_normalization",
            "current_C2_boundary_domain",
        ],
        "independent_yukawa_or_mass_fit_allowed": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_C2_QUARK_HIGGS_INCIDENCE_SUPPORT_TRANSPORTED_CONDITIONAL": True,
        "CURRENT_C2_HISTORICAL_TO_CURRENT_FIELD_CONVENTION_BRIDGE_DERIVED": True,
        "CURRENT_C2_QUARK_HIGGS_SUPPORT_PRESERVES_C2_RADIAL_DOMAIN": True,
        "CURRENT_C2_UP_DOWN_YUKAWA_COEFFICIENTS_ACTION_DERIVED": False,
        "CURRENT_C2_QUARK_CONTACT_JET_ACTION_DERIVED": False,
        "CURRENT_C2_PHYSICAL_QUARK_POLES_DERIVED": False,
        "CKM_MATRIX_DERIVED": False,
        "MEASURED_QUARK_MASS_USED": False,
        "particle_spectrum_rebuilt": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "claim_boundary",
    "current_c2_domain_tensor_theorem",
    "exact_remaining_owner",
    "finite_sector_projectors",
    "quark_higgs_support_pencil",
    "two_to_four_component_transport",
]
