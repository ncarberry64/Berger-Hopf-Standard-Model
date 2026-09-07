"""Versioned transport of the retained BHSM charged-lepton M4 action.

This composes the historical intrinsic M4 lepton--Higgs term with the AE3 C2
carrier and the newly attached frozen internal semigroup operator.  It derives
the action variation and conditional tree-level operator, but it does not
claim a same-C2 fermion pole or an absolute-unit derivation.
"""

from __future__ import annotations

from math import exp, pi, sqrt
from typing import Any

import numpy as np

from constants import PLANCK_ENERGY_GEV
from bhsm.interface.ae3_c2_hopf_semigroup_transport import (
    ACTION_VERSION as PREDECESSOR_ACTION_VERSION,
    FROZEN_INTERNAL_BERGER_SHAPE,
    frozen_internal_semigroup_attachment,
)


ACTION_VERSION = "BHSM-AE-3.1.0"
CLASSIFICATION = "CURRENT_C2_INTRINSIC_M4_CHARGED_LEPTON_ACTION_TRANSPORT"
TRACE_NORMALIZED_YUKAWA_PREFACTOR = 16.0 * sqrt(2.0 * pi) / 3969.0


def action_composition_contract() -> dict[str, Any]:
    """State the additive action composition and its no-double-counting rule."""

    return {
        "action_version": ACTION_VERSION,
        "predecessor_action_version": PREDECESSOR_ACTION_VERSION,
        "composition": "S_AE3_1=S_AE3_0+S_4_lH_BHSM",
        "imported_term_source": (
            "V11_3_FINAL_PARENT_ACTION_LEPTON_MASS_COMPLETION_INTRINSIC_M4_BLOCK"
        ),
        "field_ownership": {
            "H": "INTRINSIC_M4_ACTIVE_FIELD",
            "L_L": "INTRINSIC_M4_ACTIVE_FIELD",
            "e_R": "INTRINSIC_M4_ACTIVE_FIELD",
            "T_l": "FIXED_INTERNAL_FAMILY_OPERATOR",
            "C2_carrier": "AE3_PREDECESSOR_DOMAIN_FACTOR",
        },
        "action_term": (
            "S_4_lH=integral_M4[|D H|^2-V_BH(H)+i*bar(L_L)*slash(D)*L_L+"
            "i*bar(e_R)*slash(D)*e_R-(bar(L_L)*Y_l_BH*H*e_R+h.c.)]"
        ),
        "potential": "V_BH=lambda_H*(H_dagger*H-nu_BH^2)^2,_lambda_H>0",
        "independent_Y_e_retained": False,
        "separate_post_EWSB_mass_term_added": False,
        "new_field_added_by_transport": False,
        "new_family_coefficient_added_by_transport": False,
        "inherited_positive_radial_stiffness": "lambda_H>0",
        "up_down_Yukawa_terms_added": False,
        "why_up_down_untouched": (
            "THE_FROZEN_RATIO_OPERATORS_ARE_ATTACHED_BUT_NO_MATCHING_"
            "HISTORICAL_ACTION_OWNED_UP_DOWN_PREFACTORS_ARE_TRANSPORTED_HERE"
        ),
        "stratum_moved": False,
        "same_C2_carrier_preserved": True,
    }


def charged_lepton_yukawa_operator() -> dict[str, Any]:
    """Return the inherited no-lepton-input family Yukawa operator."""

    attachment = frozen_internal_semigroup_attachment()
    response = np.asarray(
        attachment["sectors"]["charged_lepton"]["family_operator"], dtype=float
    )
    yukawa = TRACE_NORMALIZED_YUKAWA_PREFACTOR * response
    eigenvalues = np.diag(yukawa)
    return {
        "action_version": ACTION_VERSION,
        "formula": "Y_l=(16*sqrt(2*pi)/3969)*T_l",
        "scalar_prefactor": TRACE_NORMALIZED_YUKAWA_PREFACTOR,
        "family_operator": yukawa.tolist(),
        "eigenvalues_heavy_middle_light": eigenvalues.tolist(),
        "Hermitian": bool(np.allclose(yukawa, yukawa.T, atol=0.0, rtol=0.0)),
        "positive_definite": bool(np.all(eigenvalues > 0.0)),
        "family_noncentral": len(set(eigenvalues.tolist())) == 3,
        "commutes_with_family_projectors": True,
        "standard_SM_gauge_contraction_preserved": True,
        "measured_lepton_mass_used": False,
        "independent_Yukawa_matrix_used": False,
    }


def conditional_higgs_saddle() -> dict[str, Any]:
    """Evaluate the inherited conditional universal-scale Higgs saddle."""

    action_cost = 4.0 * pi**2 + (
        FROZEN_INTERNAL_BERGER_SHAPE - 1.0
    ) / (4.0 * pi**2)
    v_bh = 2.0 * sqrt(2.0) * PLANCK_ENERGY_GEV * exp(-action_cost)
    nu_squared = 0.5 * v_bh**2
    return {
        "action_version": ACTION_VERSION,
        "universal_energy_calibration_GeV": PLANCK_ENERGY_GEV,
        "universal_energy_calibration_action_derived": False,
        "measured_Higgs_VEV_used": False,
        "action_cost": action_cost,
        "action_cost_formula": "4*pi^2+(a-1)/(4*pi^2)",
        "nu_BH_squared_GeV2": nu_squared,
        "v_BH_GeV": v_bh,
        "stationarity_equation": "(H_dagger*H-nu_BH^2)*H=0",
        "nonzero_branch": "H_vac=(0,v_BH/sqrt(2))",
        "radial_Hessian": "2*lambda_H*v_BH^2>0_for_lambda_H>0",
        "classification": "CONDITIONAL_ON_INHERITED_UNIVERSAL_UNIT_CALIBRATION",
    }


def conditional_tree_mass_operator() -> dict[str, Any]:
    """Derive ``M_l=v_BH*Y_l/sqrt(2)`` from the composed action."""

    yukawa = charged_lepton_yukawa_operator()
    saddle = conditional_higgs_saddle()
    matrix = (
        saddle["v_BH_GeV"]
        * np.asarray(yukawa["family_operator"], dtype=float)
        / sqrt(2.0)
    )
    eigenvalues = np.diag(matrix)
    return {
        "action_version": ACTION_VERSION,
        "formula": "M_l=(v_BH/sqrt(2))*Y_l",
        "equivalent_formula": (
            "M_l=4*pi^2*v_BH*(beta_l*tau/3)*exp[-L_a,l/(4*pi)]"
        ),
        "matrix_GeV": matrix.tolist(),
        "eigenvalues_GeV_heavy_middle_light": eigenvalues.tolist(),
        "ratios_to_heavy": (eigenvalues / eigenvalues[0]).tolist(),
        "tree_level_local_M4_pole_template": "det(slash(p)-M_l)=0",
        "conditional_tree_pole_equations": [
            f"p^2={value**2:.17g}_GeV^2" for value in eigenvalues
        ],
        "current_C2_finite_core_poles_evaluated": False,
        "absolute_unit_action_derived": False,
        "measured_lepton_mass_used": False,
        "classification": (
            "ACTION_COMPOSED_CONDITIONAL_TREE_LEVEL_CHARGED_LEPTON_MASS_OPERATOR"
        ),
    }


def first_variation_and_pole_gate() -> dict[str, Any]:
    """Record the derived Euler variations and the exact remaining pole join."""

    return {
        "action_version": ACTION_VERSION,
        "Euler_L_L": "i*slash(D)*L_L-Y_l*H*e_R=0",
        "Euler_e_R": "i*slash(D)*e_R-Y_l_dagger*H_dagger*L_L=0",
        "Euler_H": (
            "-D^2*H-2*lambda_H*(H_dagger*H-nu_BH^2)*H-"
            "bar(e_R)*Y_l_dagger*L_L=0"
        ),
        "variation_is_family_noncentral": True,
        "same_current_C2_first_order_LR_block_assembled": False,
        "same_current_C2_domain_determinant_evaluated": False,
        "simple_pole_residues_evaluated": False,
        "matched_parent_Delta_H_xi_evaluated": False,
        "exact_next_operator": (
            "CURRENT_C2_FIRST_ORDER_CHIRAL_BLOCK_[[D_L,M_l],[M_l_DAGGER,D_R]]_"
            "ON_THE_RETAINED_MAXIMAL_ISOTROPIC_DOMAIN_WITH_ITS_SIMPLE_POLES"
        ),
        "do_not_use": [
            "THE_SEPARATE_CHIRAL_SQUARED_PENCILS_AS_IF_THEY_ALREADY_CONTAIN_M_l",
            "A_FITTED_WAVEFUNCTION_RESIDUE",
            "AN_OBSERVED_LEPTON_MASS_TO_SELECT_THE_BRANCH",
        ],
    }


def local_tangent_frame_poles() -> dict[str, Any]:
    """Derive the local Lorentzian tree poles inside the smooth enclosure.

    At any regular interior point, choose the action-selected orthonormal
    tetrad for the induced Lorentzian metric.  Freezing lower-order connection
    coefficients gives the standard local symbol ``gamma.p-M``.  This is a
    local principal/pole statement, not a global stationary Green function.
    """

    mass = conditional_tree_mass_operator()
    values = mass["eigenvalues_GeV_heavy_middle_light"]
    roles = ("heavy", "middle", "light")
    rows = []
    for index, (role, value) in enumerate(zip(roles, values)):
        projector = np.zeros((3, 3), dtype=float)
        projector[index, index] = 1.0
        rows.append(
            {
                "role": role,
                "family_projector": projector.tolist(),
                "tree_mass_GeV": value,
                "mass_squared_GeV2": value**2,
                "dispersion": f"omega^2=|k|^2+{value**2:.17g}_GeV^2",
                "rest_frequency_poles_GeV": [-value, value],
                "positive_pole_denominator_derivative": 2.0 * value,
                "positive_pole_scalar_residue_GeV_inverse": 1.0 / (2.0 * value),
                "spinor_residue_formula": "(gamma.p+m_f)/(2*E_f)",
                "pole_order": 1,
            }
        )
    return {
        "action_version": ACTION_VERSION,
        "domain": "REGULAR_INTERIOR_POINT_OF_AE3_ENCLOSURE_D_enc",
        "metric": "ACTION_SELECTED_INDUCED_LORENTZIAN_METRIC_h=X_star_g",
        "local_symbol": "D_l(x,p)=gamma^a*e_a^mu(x)*p_mu-M_l",
        "determinant_per_family": "det(D_f)=(h_inverse(p,p)-m_f^2)^2",
        "propagator_per_family": "S_f=i*(gamma.p+m_f)/(p^2-m_f^2+i0)",
        "continuous_frequency": True,
        "rows": rows,
        "three_distinct_positive_local_mass_shells": len(set(values)) == 3,
        "all_energy_poles_simple": all(row["pole_order"] == 1 for row in rows),
        "independent_wavefunction_residue_fitted": False,
        "canonical_tree_kinetic_residue_used": True,
        "global_time_translation_invariance_claimed": False,
        "global_current_C2_Green_function_derived": False,
        "curvature_and_connection_lower_order_dressing_derived": False,
        "absolute_unit_remains_conditional": True,
        "result": "LOCAL_CURRENT_C2_ENCLOSURE_TREE_MASS_SHELLS_AND_SIMPLE_POLES_DERIVED_CONDITIONALLY",
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "versioned_successor_action_composed": True,
        "charged_lepton_M4_semigroup_coupling_action_owned_in_successor": True,
        "charged_lepton_family_noncentral_Yukawa_operator_derived": True,
        "conditional_tree_level_charged_lepton_mass_operator_derived": True,
        "current_C2_local_tangent_frame_tree_poles_derived": True,
        "local_enclosure_particle_identification_bridge_closed_conditionally": True,
        "current_C2_physical_charged_lepton_poles_derived": False,
        "global_or_dressed_current_C2_charged_lepton_poles_derived": False,
        "absolute_unit_first_principles_derived": False,
        "up_down_action_prefactors_derived": False,
        "muon_magnetic_moment_derived": False,
        "measured_mass_used": False,
        "particle_spectrum_rebuilt": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "PREDECESSOR_ACTION_VERSION",
    "TRACE_NORMALIZED_YUKAWA_PREFACTOR",
    "action_composition_contract",
    "charged_lepton_yukawa_operator",
    "claim_boundary",
    "conditional_higgs_saddle",
    "conditional_tree_mass_operator",
    "first_variation_and_pole_gate",
    "local_tangent_frame_poles",
]
