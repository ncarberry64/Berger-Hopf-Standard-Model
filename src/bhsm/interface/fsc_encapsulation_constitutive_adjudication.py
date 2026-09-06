"""Adjudicate the fine-structure yardstick against the P-A* interface class.

The owner rule introduced here is deliberately narrow: ``alpha_FSC`` is one
primitive dimensionless reference unit.  This module does not identify that
unit with a universal physical force, select its numerical value at an
unspecified scale, or promote historical gauge screens to action coefficients.
"""

from __future__ import annotations

import math
from typing import Any

from bhsm.interface.owner_authorized_encapsulation_interface_action import (
    active_encapsulation_differential,
    closure_and_rank_status as prior_closure_and_rank_status,
    invariant_density_ledger,
)


VERSION = "BHSM-FSC-ENC-1.0.0"
PRIMITIVE_CLASS = "FSC-P1"
EFFECTIVE_MAP_CLASS = "GEFF5"
SCALE_CLASS = "SCALE4"
INTERFACE_CLASS = "FSC-IF5"
EM_CLASS = "EM-FSC3"
GEOMETRIC_CLASS = "GEO-FSC3"
PREGEOMETRIC_CLASS = "GEO-FSC4"
LOOP_CLASS = "LOOP3"
RSP_CLASS = "RSP5"

EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_FSC_TO_INTERFACE_CONSTITUTIVE_MAP_FIXING_THE_REFERENCE_"
    "SCALE_AND_NORMALIZATION_CONVENTION_CHANNEL_EXPONENTS_AND_WEIGHTS_AND_"
    "THE_INVARIANT_OPERATOR_COEFFICIENTS_WITHOUT_FIT"
)


def fsc_historical_lineage() -> list[dict[str, Any]]:
    """Return the FSC/coupling lineage with present authority and disposition."""

    return [
        {
            "id": "LOW_ENERGY_ALPHA_EMPIRICAL",
            "object": "alpha_EM(0)^(-1)=137.035999084 in src/constants.py",
            "interpretation": "observed low-energy electromagnetic reference value",
            "classification": "FSC-P0",
            "disposition": "EMPIRICAL_REFERENCE_ONLY_NOT_A_BHSM_ACTION_INPUT",
            "action_derived": False,
        },
        {
            "id": "HISTORICAL_XI_GEOM",
            "object": "Xi_geom=1/(12*pi^2), inverse 12*pi^2=118.435...",
            "interpretation": "historical geometric candidate assembled from sphere/trace factors",
            "classification": "FSC-P2",
            "disposition": "QUARANTINED_CANDIDATE_NOT_ATTACHED_TO_AE2",
            "action_derived": False,
        },
        {
            "id": "HISTORICAL_XI_COUPLING_MAP",
            "object": "1/e^2=Xi/g^2 versus operational e^2=g^2*Xi",
            "interpretation": "internally contradictory historical coupling map",
            "classification": "SUPERSEDED",
            "disposition": "NORMALIZATION_CONTRADICTION",
            "action_derived": False,
        },
        {
            "id": "HISTORICAL_LOW_ENERGY_DRESSING_FIT",
            "object": "running coefficient fixed by the observed low-energy inverse coupling",
            "interpretation": "post-comparison calibration rather than upstream derivation",
            "classification": "SUPERSEDED",
            "disposition": "FORBIDDEN_AS_ACTION_OR_INTERFACE_INPUT",
            "action_derived": False,
        },
        {
            "id": "WEYL_3D_DENSITY",
            "object": "lambda_Weyl=1/(6*pi^2)=1/[3 Vol(S^3_unit)]",
            "interpretation": "exact normalized three-dimensional Weyl/sphere-volume factor",
            "classification": "FSC-P3",
            "disposition": "MATHEMATICAL_DENSITY_IDENTITY_ONLY",
            "action_derived": False,
        },
        {
            "id": "GAUGE_127_REGISTRY_SCREEN",
            "object": "alpha_i=w_i/(6*pi^2), w=(1,2,7)",
            "interpretation": "registered electroweak-scale matching screen",
            "classification": "FSC-P2",
            "disposition": "HISTORICAL_NOT_ACTION_DERIVED",
            "action_derived": False,
        },
        {
            "id": "CASIMIR_SHELL_RESIDUES",
            "object": "w=(1,dim(su2)-1,dim(su3)-1)=(1,2,7)",
            "interpretation": "candidate angular Casimir-shell spectral residues",
            "classification": "FSC-P2",
            "disposition": "ACTION_ATTACHMENT_AND_AD_INVARIANCE_NOT_ESTABLISHED",
            "action_derived": False,
        },
        {
            "id": "TRACE_RATIO_COUPLING_RELATION",
            "object": "K1:K2:K3=10/3:2:2 implies conditional g_i^2 ratio 3/5:1:1",
            "interpretation": "action-owned chiral-seam trace-ratio theorem in its declared domain",
            "classification": "FSC-P3",
            "disposition": "CONDITIONAL_RATIO_NOT_ABSOLUTE_PHYSICAL_COUPLINGS",
            "action_derived": True,
        },
        {
            "id": "GAUGE_INVARIANCE_6PI2_NO_GO",
            "object": "rank-(dim g-1) projectors are not Ad-invariant; 6*pi^2 is not a common coupling",
            "interpretation": "later theorem-level no-go on the historical physical identification",
            "classification": "FSC-P3",
            "disposition": "SUPERSEDES_6PI2_AND_127_AS_UNIVERSAL_ACTION_COUPLINGS",
            "action_derived": True,
        },
        {
            "id": "ELECTROWEAK_ALPHA_SCREEN",
            "object": "alpha_EM^(-1)(M_EW)=13*pi^2",
            "interpretation": "electroweak-scale matching screen, distinct from low-energy alpha",
            "classification": "FSC-P2",
            "disposition": "SCREEN_ONLY",
            "action_derived": False,
        },
        {
            "id": "ONE_LOOP_SM_RG_SCAFFOLD",
            "object": "alpha_i^(-1)(mu)=alpha_i^(-1)(mu0)-b_i log(mu/mu0)/(2*pi)",
            "interpretation": "implemented Standard Model one-loop comparison scaffold",
            "classification": "FSC-P2",
            "disposition": "EMPIRICAL_BOUNDARY_AND_INTERFACE_SCALE_MAP_OPEN",
            "action_derived": False,
        },
        {
            "id": "V14_79_ALPHA_SHAPE_CONTRACT",
            "object": "Q_b=alpha_FS Qhat_b and H_lift=alpha_FS Omega_b G_b",
            "interpretation": "architectural single-alpha rule with canonical action attachment still open",
            "classification": "FSC-P1",
            "disposition": "TYPED_DIRECTIVE_NOT_A_PHYSICAL_INTERFACE_LAW",
            "action_derived": False,
        },
        {
            "id": "CURRENT_FSC_YARDSTICK",
            "object": "alpha_FSC is the common primitive dimensionless constitutive unit",
            "interpretation": "owner-authorized reference yardstick with derived channel factors required",
            "classification": PRIMITIVE_CLASS,
            "disposition": "ACTIVE_OWNER_RULE_ACTION_ATTACHMENT_OPEN",
            "action_derived": False,
        },
    ]


def primitive_coupling_definition() -> dict[str, Any]:
    """Separate the symbolic owner primitive from observed electromagnetic alpha."""

    return {
        "primitive": "alpha_FSC",
        "classification": PRIMITIVE_CLASS,
        "mathematical_type": "positive dimensionless reference coupling unit",
        "owner_approximation": "alpha_FSC approximately 1/137",
        "exact_numeric_value_selected": False,
        "reference_scale_selected": False,
        "renormalization_scheme_selected": False,
        "physical_U1_projection_selected": False,
        "observed_low_energy_object": "alpha_EM(0) with empirical inverse 137.035999084",
        "observed_value_role": "downstream comparison only",
        "not_the_primitive": ["e", "g", "1/(6*pi^2)", "1/(12*pi^2)", "1/(13*pi^2)"],
        "conditional_canonical_conversion": {
            "condition": "canonically normalized electromagnetic channel with alpha=e^2/(4*pi)",
            "e_from_alpha": "e=sqrt(4*pi*alpha)",
            "yang_mills_density": "-Tr(F^2)/(4*e^2)=-Tr(F^2)/(16*pi*alpha)",
            "universal_interface_conversion": False,
        },
    }


def alpha_from_canonical_g(g: float) -> float:
    """Convert a positive canonical gauge coupling using alpha=g^2/(4*pi)."""

    if g <= 0.0:
        raise ValueError("g must be positive")
    return float(g * g / (4.0 * math.pi))


def canonical_g_from_alpha(alpha: float) -> float:
    """Convert positive alpha to canonical g; this is not a universal BHSM map."""

    if alpha <= 0.0:
        raise ValueError("alpha must be positive")
    return float(math.sqrt(4.0 * math.pi * alpha))


def canonical_yang_mills_prefactor(alpha: float) -> float:
    """Return 1/(4 g^2)=1/(16*pi*alpha) under the stated convention."""

    if alpha <= 0.0:
        raise ValueError("alpha must be positive")
    return float(1.0 / (16.0 * math.pi * alpha))


def coupling_authority_ledger() -> list[dict[str, str]]:
    return [
        {"object": "symbolic alpha_FSC yardstick", "authority": "FSC-P1", "use": "permitted as a reference unit"},
        {"object": "alpha_EM(0)^(-1)=137.035999084", "authority": "FSC-P0", "use": "empirical comparison only"},
        {"object": "1/(12*pi^2)", "authority": "FSC-P2", "use": "quarantined geometric candidate"},
        {"object": "1/(6*pi^2)", "authority": "FSC-P3_AS_DENSITY; SUPERSEDED_AS_COMMON_COUPLING", "use": "Weyl factor only"},
        {"object": "1:2:7", "authority": "FSC-P2", "use": "historical/spectral candidate, not action coefficients"},
        {"object": "3/5:1:1 squared-coupling ratio", "authority": "FSC-P3_CONDITIONAL", "use": "declared trace domain only"},
        {"object": "13*pi^2 electroweak inverse alpha", "authority": "FSC-P2", "use": "matching screen only"},
        {"object": "SM one-loop RG transport", "authority": "FSC-P2", "use": "comparison scaffold, not interface running"},
    ]


def channel_weight_ledger() -> list[dict[str, Any]]:
    """Classify every required channel without manufacturing a coefficient."""

    return [
        {
            "channel": "electromagnetic/U1-like",
            "weight": "1 by reference convention",
            "classification": "W1",
            "source": "owner FSC yardstick plus candidate C_U1=1 convention",
            "condition": "surviving physical U1 projection and canonical normalization",
            "selected_physical_weight": False,
        },
        {
            "channel": "weak",
            "weight": "5/3 relative to the trace-normalized U1 coefficient, conditionally",
            "classification": "W1",
            "source": "v14.19 K1:K2=10/3:2",
            "historical_alternative": "2 from 1:2:7 is W3 and not action-attached",
            "selected_physical_weight": False,
        },
        {
            "channel": "strong/color",
            "weight": "5/3 relative to the trace-normalized U1 coefficient, conditionally",
            "classification": "W1",
            "source": "v14.19 K1:K3=10/3:2",
            "historical_alternative": "7 from 1:2:7 is W3 and not action-attached",
            "selected_physical_weight": False,
        },
        {
            "channel": "scalar/topographic",
            "weight": None,
            "classification": "W4",
            "source": "no FSC-to-scalar interface coefficient theorem",
            "selected_physical_weight": False,
        },
        {
            "channel": "geometric/gravitational",
            "weight": None,
            "classification": "W4",
            "source": "no FSC-to-envelopment or curvature coefficient theorem",
            "selected_physical_weight": False,
        },
        {
            "channel": "pregeometric/emergent",
            "weight": None,
            "classification": "W4",
            "source": "no ordinary gauge normalization or carrier exists in C_A",
            "selected_physical_weight": False,
        },
    ]


def effective_coupling_map() -> dict[str, Any]:
    """State the maximal no-fit map allowed by current authority."""

    return {
        "classification": EFFECTIVE_MAP_CLASS,
        "unique_map": None,
        "linear_candidate": "alpha_eff^(r)=alpha_FSC*W_r",
        "linear_candidate_justified": False,
        "most_specific_current_form": (
            "alpha_eff^(r)(mu,Xi)=alpha_FSC^(p_r) W_r "
            "R_r(mu/mu_ref,I_event,I_environment,I_scale;discrete_data)"
        ),
        "p_r_status": "unselected except inside already-normalized sector-specific terms",
        "R_r_status": "arbitrary invariant scalar/matrix/operator-valued response remains",
        "no_new_fit_parameter": True,
        "why_GEFF5": (
            "dimensions and covariance type the arguments but do not select p_r, the physical W_r, "
            "the event-scale map, or the response operator/function"
        ),
    }


def scale_running_adjudication() -> dict[str, Any]:
    return {
        "classification": SCALE_CLASS,
        "primitive_role": "fixed symbolic reference yardstick",
        "interface_running_law_owned": False,
        "event_scale_map_owned": False,
        "reference_scale_owned": False,
        "boundary_value_owned": False,
        "conditional_SM_subledger": {
            "shape": "SCALE2_LIKE_COMPARISON_SCAFFOLD",
            "formula_implemented": True,
            "one_loop_only": True,
            "thresholds_complete": False,
            "may_be_used_as_interface_running": False,
        },
        "reason": "the registered SM scaffold does not attach alpha_FSC to P-A* or derive mu_s",
    }


def allowed_fsc_power_ledger() -> list[dict[str, Any]]:
    """Separate normalization-dependent powers from a universal power claim."""

    return [
        {"power": -2, "role": "higher inverse-stiffness constructions", "status": "NOT_SELECTED_FOR_ANY_INTERFACE_TERM"},
        {"power": -1, "role": "canonical Yang-Mills kinetic density after alpha=g^2/(4*pi)", "status": "CONDITIONAL_SECTOR_IDENTITY_NOT_INTERFACE_UNIVERSAL"},
        {"power": 0, "role": "unscaled or independently topological action term", "status": "ALLOWED_BY_TYPE_NOT_SELECTED"},
        {"power": "1/2", "role": "canonical gauge vertex g=sqrt(4*pi*alpha)", "status": "CONDITIONAL_PERTURBATIVE_PARAMETERIZATION"},
        {"power": 1, "role": "two-vertex strength or owner-authorized alpha-scaled shape/lift", "status": "ARCHITECTURAL_CANDIDATE_ACTION_ATTACHMENT_OPEN"},
        {"power": 2, "role": "second response order and v14.79 quadratic Landau correction", "status": "CONDITIONAL_DERIVED_AFTER_AN_ALPHA_SCALED_FIELD_IS_ASSUMED"},
        {"power": "other/nonpolynomial", "role": "effective response after elimination or RG", "status": "NOT_EXCLUDED_AND_NOT_SELECTED"},
    ]


def interface_invariant_coefficient_ledger() -> list[dict[str, Any]]:
    """Attach FSC status to every density family from the certified ORD1 ledger."""

    output: list[dict[str, Any]] = []
    for row in invariant_density_ledger():
        family = row["family"]
        if family == "owned_GHY_Hayward":
            fsc_status = "REDUNDANT_EXISTING_COEFFICIENT_NOT_REWEIGHTED_BY_FSC"
        elif family == "extrinsic_curvature_or_second_jet":
            fsc_status = "EXCLUDED_FROM_MINIMAL_ORD1_CLASS"
        elif family == "topological_holonomy":
            fsc_status = "LEVEL_MUST_BE_TOPOLOGICALLY_QUANTIZED_NOT_SET_BY_FSC"
        else:
            fsc_status = "NO_ACTION_DERIVED_P_r_W_r_OR_RESPONSE_COEFFICIENT"
        output.append(
            {
                "family": family,
                "prior_status": row["status"],
                "derivative_order": row["derivative_order"],
                "fsc_power": None,
                "channel_weight": None,
                "coefficient_selected": False,
                "fsc_status": fsc_status,
            }
        )
    return output


def constitutive_closure_test() -> dict[str, Any]:
    return {
        "classification": INTERFACE_CLASS,
        "selected_interface_density": None,
        "selected_coefficients": 0,
        "selected_functions": 0,
        "infinite_dimensional_freedom_removed": False,
        "factorization": "S_enc=alpha_FSC*S_hat_enc is a bookkeeping factorization for nonzero alpha_FSC",
        "factorization_has_decision_power": False,
        "reason": (
            "rescaling W_s to W_s/alpha_FSC is bijective and does not choose an invariant density, "
            "operator kernel, carrier, exponent, or relative coefficient"
        ),
    }


def electromagnetic_proof_of_concept() -> dict[str, Any]:
    return {
        "classification": EM_CLASS,
        "reference_channel_normalization": "alpha_FSC with W_EM=1 by conditional convention",
        "exact_strength_at_interface_scale_fixed": False,
        "tensor_operator_shape_fixed": False,
        "complete_first_order_response": False,
        "remaining_operator_classes": [
            "canonical generating contractions",
            "field and attachment first-jet invariants",
            "local matrix-valued multiplicity responses",
            "nonlocal boundary response kernels when a domain is selected",
        ],
        "reason": "the yardstick fixes a channel unit but multiple covariant operator laws remain",
    }


def weak_and_strong_result() -> dict[str, Any]:
    return {
        "weak": {
            "result": "NO_UNIQUE_ALPHA_FSC_TIMES_WEIGHT_COUPLING",
            "conditional_weight": "5/3 in the v14.19 trace convention",
            "historical_127_weight": 2,
            "historical_127_promoted": False,
        },
        "strong": {
            "result": "NO_UNIQUE_ALPHA_FSC_TIMES_WEIGHT_COUPLING",
            "conditional_weight": "5/3 in the v14.19 trace convention",
            "historical_127_weight": 7,
            "historical_127_promoted": False,
        },
        "nonlinear_or_RG_relation_selected": False,
        "standard_model_running_overwritten": False,
    }


def geometric_pregeometric_result() -> dict[str, Any]:
    return {
        "geometric_classification": GEOMETRIC_CLASS,
        "geometric_result": "alpha_FSC may label a normalization yardstick but is not the gravitational/envelopment coupling",
        "derived_geometric_channel_factor": None,
        "pregeometric_classification": PREGEOMETRIC_CLASS,
        "pregeometric_result": "no legitimate current map carries an electromagnetic-style coupling into C_A->G_A",
        "ordinary_carrier_in_C_A_asserted": False,
        "forced_universality": False,
    }


def energy_spacetime_ratio_adjudication() -> dict[str, Any]:
    return {
        "candidate": "chi_enc=alpha_eff^(r)*rho_E/ST",
        "multiplication_derived": False,
        "rho_E/ST_defined_by_FSC": False,
        "rho_E/ST_dimensionless_after_FSC": False,
        "reason": (
            "a dimensionless coupling cannot supply the missing common charge, reference, carrier measure, "
            "or covariant energy/spacetime contraction"
        ),
        "selected_control": None,
    }


def perturbative_hierarchy_adjudication() -> dict[str, Any]:
    return {
        "global_expansion_valid": False,
        "small_parameter_at_relevant_scale_proved": False,
        "asymptotic_or_convergent": None,
        "first_nonzero_allowed_order": None,
        "reason": (
            "canonical kinetic and vertex conventions expose alpha^-1 and alpha^(1/2), while the interface "
            "operator, scale, background, and geometric/pregeometric regime are unselected"
        ),
        "sector_specific_formal_orders": ["alpha^-1 kinetic", "alpha^(1/2) vertex", "alpha loop/response", "alpha^2 higher response"],
    }


def first_variation_and_rank_status() -> dict[str, Any]:
    prior = prior_closure_and_rank_status()
    return {
        "finite_density_fixed": False,
        "formal_prior_variation": active_encapsulation_differential()["definition_from_total_seam_equations"],
        "delta_S_enc_explicit": None,
        "delta_over_iota_enc": None,
        "delta_over_F_B": None,
        "delta_over_L_s": None,
        "Delta_enc": None,
        "N12_rank_added": 0,
        "N12_residual_before_time_quotient": prior["N12_residual_before_time_quotient"],
        "N12_residual_after_time_quotient": prior["N12_residual_after_time_quotient"],
        "loop": LOOP_CLASS,
        "RSP": RSP_CLASS,
        "cycle_rerun": False,
        "cycle_stop_reason": INTERFACE_CLASS,
    }


def closure_status() -> dict[str, Any]:
    return {
        "selected_S_enc": None,
        "selected_carrier": None,
        "selected_F_B": None,
        "selected_L_s": None,
        "selected_Delta_enc": None,
        "interface_class": INTERFACE_CLASS,
        "effective_map_class": EFFECTIVE_MAP_CLASS,
        "scale_class": SCALE_CLASS,
        "loop": LOOP_CLASS,
        "RSP": RSP_CLASS,
        "owner_question": None,
        "why_no_owner_question": "FSC-IF5 is a theorem deficit, not a small owner ambiguity",
        "exact_next_object": EXACT_NEXT_OBJECT,
    }


def frozen_prediction_cross_check() -> dict[str, Any]:
    return {
        "gauge_coupling_screens_changed": False,
        "family_mode_assignments_changed": False,
        "masses_changed": False,
        "CKM_changed": False,
        "neutrino_doctrine_changed": False,
        "collider_predictions_changed": False,
        "frozen_prediction_files_modified": False,
        "retrofitting_used": False,
    }


def claim_firewall() -> dict[str, bool]:
    return {
        "FSC_LITERAL_UNIVERSAL_FORCE_CLAIMED": False,
        "FSC_SCALE_INDEPENDENT_CLAIMED": False,
        "HISTORICAL_COUPLING_CANDIDATE_PROMOTED": False,
        "INTERFACE_COEFFICIENT_FITTED": False,
        "INTERFACE_FUNCTION_HAND_SELECTED": False,
        "FTL_NEUTRINO_CLAIMED": False,
        "NEW_PARTICLE_RESULT_CLAIMED": False,
        "GATE7_CLOSURE_CLAIMED": False,
        "FULL_BHSM_COMPLETION_CLAIMED": False,
    }


def adjudication_payload() -> dict[str, Any]:
    """Build the complete deterministic scientific adjudication payload."""

    return {
        "version": VERSION,
        "primary_verdict": (
            "PRIMITIVE_FSC_IS_AN_OWNER_AUTHORIZED_DIMENSIONLESS_YARDSTICK_BUT_"
            "EXISTING_BHSM_DOES_NOT_DERIVE_ALL_CHANNEL_WEIGHTS_POWERS_SCALE_MAPS_"
            "OR_INTERFACE_OPERATOR_COEFFICIENTS_SO_GEFF5_AND_FSC_IF5_REMAIN"
        ),
        "lineage": fsc_historical_lineage(),
        "primitive": primitive_coupling_definition(),
        "coupling_authority": coupling_authority_ledger(),
        "channel_weights": channel_weight_ledger(),
        "effective_map": effective_coupling_map(),
        "scale_running": scale_running_adjudication(),
        "power_ledger": allowed_fsc_power_ledger(),
        "invariant_coefficients": interface_invariant_coefficient_ledger(),
        "constitutive_closure": constitutive_closure_test(),
        "electromagnetic": electromagnetic_proof_of_concept(),
        "weak_strong": weak_and_strong_result(),
        "geometric_pregeometric": geometric_pregeometric_result(),
        "energy_spacetime_ratio": energy_spacetime_ratio_adjudication(),
        "perturbative_hierarchy": perturbative_hierarchy_adjudication(),
        "variation_rank_cycle": first_variation_and_rank_status(),
        "closure": closure_status(),
        "frozen_cross_check": frozen_prediction_cross_check(),
        "claim_firewall": claim_firewall(),
    }


__all__ = [
    "EFFECTIVE_MAP_CLASS", "EM_CLASS", "EXACT_NEXT_OBJECT", "GEOMETRIC_CLASS",
    "INTERFACE_CLASS", "LOOP_CLASS", "PREGEOMETRIC_CLASS", "PRIMITIVE_CLASS",
    "RSP_CLASS", "SCALE_CLASS", "VERSION", "adjudication_payload",
    "allowed_fsc_power_ledger", "alpha_from_canonical_g", "canonical_g_from_alpha",
    "canonical_yang_mills_prefactor", "channel_weight_ledger", "claim_firewall",
    "closure_status", "constitutive_closure_test", "coupling_authority_ledger",
    "effective_coupling_map", "electromagnetic_proof_of_concept",
    "energy_spacetime_ratio_adjudication", "first_variation_and_rank_status",
    "frozen_prediction_cross_check", "fsc_historical_lineage",
    "geometric_pregeometric_result", "interface_invariant_coefficient_ledger",
    "perturbative_hierarchy_adjudication", "primitive_coupling_definition",
    "scale_running_adjudication", "weak_and_strong_result",
]
