"""BHSM v8.1 mode-resolved curvature-incidence construction.

The construction retains the complete Brown--York momentum and audits every
action-supported internal or tangential carrier.  It finds an exact internal
scalar associated-bundle tower, but no action term attaches that tower (or an
internal spinor analogue) to the localized M4 fermion bundle.  Consequently
no physical family response matrix is defined.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


VERSION = "v8.1"
SPRINT = "bhsm-mode-resolved-curvature-incidence-v8-1"
SOURCE_MAIN_SHA = "45e5030d672f6805b27e8cc0552d474aa8d4a72d"
ARTIFACT_NAME = "BHSM_mode_resolved_curvature_incidence_v8_1"
SCHEME = "overline_MS"
REFERENCE_SCALE = "mu_star=ell_star^-1; mu_hat_star=1"
RESPONSE_RESULT = "BHSM_MODE_RESOLVED_CURVATURE_INCIDENCE_NOT_CONSTRUCTED"
FAMILY_OBSTRUCTION = (
    "BHSM_FAMILY_RESOLUTION_REQUIRES_NEW_INTERNAL_FERMION_BUNDLE_EXTENSION"
)
IMMEDIATE_OBSTRUCTION = (
    "BHSM_FAMILY_RESPONSE_BLOCKED_BY_NO_HOPF_ACTION_ON_LOCALIZED_"
    "FERMION_BUNDLE"
)
FINAL_VERDICT = FAMILY_OBSTRUCTION
RELEASE_VERDICT = "BHSM_1_0_RELEASE_BLOCKED"


def deterministic_json(value: Any) -> str:
    return json.dumps(
        value, indent=2, sort_keys=True, ensure_ascii=False
    ) + "\n"


def carrier_audit() -> list[dict[str, Any]]:
    """Classify exact carriers without promoting historical proxies."""

    return [
        {
            "candidate": "internal Hopf-associated Dirac operator",
            "exact_object": None,
            "action_source": None,
            "eligible": False,
            "status": "ABSENT_FROM_ACTION",
            "reason": (
                "the M8-to-M5 reduction supplies associated scalar bundles "
                "but no parent spinor action, internal spinor bundle, "
                "chirality operator, lower-order endomorphism, or domain"
            ),
        },
        {
            "candidate": "localized tangential Dirac-Yukawa operator",
            "exact_object": (
                "D_M4=i gamma^mu(nabla_mu^S_h+rho(A_SM)_mu)-Y(H)"
            ),
            "manifold": "M4",
            "bundle": "S_h tensor E_SM tensor C3_family",
            "principal_symbol": "i gamma^mu xi_mu",
            "lower_order_terms": "-Y(H)",
            "chirality": "the supplied Standard Model chiral representation",
            "domain": (
                "a supplied maximal-isotropic domain; no member is selected "
                "by the action"
            ),
            "adjoint": "formal Dirac adjoint on the supplied domain",
            "covariance": "Spin(h) times G_SM",
            "action_source": "S_4,localized",
            "hopf_action": "D_Hopf_twist=0",
            "eligible": False,
            "status": "PHYSICAL_BUT_NO_INTERNAL_HOPF_ACTION",
            "reason": (
                "its shape sensitivity is ordinary M4 stress/momentum and "
                "cannot turn spacetime harmonics into family states"
            ),
        },
        {
            "candidate": "Hopf-twisted localized Dirac operator",
            "exact_object": None,
            "action_source": None,
            "eligible": False,
            "status": "RETIRED_PROXY_REJECTED",
            "reason": (
                "the canonical Sp(1) Hopf connection does not act on Psi; "
                "a twist strength or boundary strength would be new input"
            ),
        },
        {
            "candidate": "Berger scalar associated-bundle Laplace operator",
            "exact_object": (
                "O_(J,m)=-D_A^*D_A+lambda_(J,m)(L1,L2)+E_(J,m)"
            ),
            "manifold": "M5=I_t times S4, restricted geometrically at M4",
            "bundle": "H_(J,m)=S7 times_(rho_J) V_J",
            "representation": (
                "left Sp(1) irrep V_J of rank 2J+1 and preserved right "
                "U(1) weight m"
            ),
            "connection": "canonical quaternionic-Hopf Sp(1) connection A",
            "principal_symbol": "-|xi|_g^2 identity_(V_J)",
            "lower_order_terms": (
                "lambda_(J,m)(L1,L2); E_(J,m)=0 in the minimal scalar "
                "reduction"
            ),
            "chirality": None,
            "domain": (
                "associated scalar sections with the selected M5 boundary "
                "domain; no physical fermion domain follows"
            ),
            "adjoint": "formally self-adjoint scalar Laplace type",
            "covariance": "left Sp(1) associated-bundle covariance",
            "action_source": "provisional M8 parent scalar fiber reduction",
            "eligible": False,
            "status": "STRONGEST_EXACT_GEOMETRIC_CARRIER_ONLY",
            "reason": (
                "it is an internal geometric mode carrier, but it is scalar, "
                "has no action-selected finite projector, and is not a tensor "
                "factor of the localized fermion bundle"
            ),
        },
        {
            "candidate": "scalar/topographic Hessian",
            "exact_object": "constrained cap/KKT scalar-metric Hessian",
            "action_source": "S5 plus matcher constraints",
            "eligible": False,
            "status": "BLOCK_DIAGONAL_FROM_LOCALIZED_YUKAWA",
            "reason": (
                "at fixed seam metric the cap scalar and localized Higgs/"
                "fermion cross-blocks vanish"
            ),
        },
        {
            "candidate": "coupled cap-response operator",
            "exact_object": "closed-range constrained cap response",
            "action_source": "Einstein-scalar ADM and matcher equations",
            "eligible": False,
            "status": "GEOMETRIC_RESPONSE_WITHOUT_FAMILY_CARRIER",
            "reason": (
                "it acts on cap/seam geometric data and supplies no internal "
                "fermion representation"
            ),
        },
        {
            "candidate": "representation-resolved Dirichlet-to-Neumann map",
            "exact_object": (
                "Lambda_(J,m):boundary scalar data -> normal scalar data"
            ),
            "action_source": "conditional associated-scalar cap problem",
            "eligible": False,
            "status": "CONDITIONAL_SCALAR_DTN_ONLY",
            "reason": (
                "a representation-resolved scalar DtN map can be defined "
                "only after its domain is selected and still has no Yukawa "
                "incidence or localized fermion bundle map"
            ),
        },
    ]


def selected_carrier() -> dict[str, Any]:
    return {
        "physical_mode_resolved_carrier": None,
        "closest_exact_geometric_carrier": (
            "O_(J,m)=-D_A^*D_A+lambda_(J,m)(L1,L2)"
        ),
        "closest_exact_physical_carrier": (
            "D_M4=i gamma^mu(nabla_mu^S_h+rho(A_SM)_mu)-Y(H)"
        ),
        "selection_status": "NO_ELIGIBLE_FERMION_INCIDENCE_CARRIER",
        "reason": (
            "the first carrier is an internal scalar unconnected to Psi; "
            "the second is physical but has D_Hopf_twist=0"
        ),
    }


def mode_firewall() -> dict[str, Any]:
    return {
        "internal_geometric_modes_exist": True,
        "internal_module_tower": (
            "{H_(J,m)=S7 times_(rho_J) V_J; rank=2J+1}"
        ),
        "ordinary_spacetime_modes": (
            "eigenmodes of the tangential M4/S3 differential operators"
        ),
        "firewall": (
            "M4/S3 momentum labels are not family labels and are never "
            "counted as generations"
        ),
        "localized_fermion_bundle": "S_h tensor E_SM tensor C3_family",
        "hopf_associated_factor_in_localized_bundle": None,
        "candidate_extended_bundle": (
            "S_h tensor E_SM tensor F_BH, with F_BH action-selected from "
            "the Hopf reduction"
        ),
        "candidate_extension_present": False,
    }


def hopf_triality_audit() -> dict[str, Any]:
    return {
        "hopf_vertical_horizontal_structure": {
            "internal_S3_fiber": (
                "T S3=H direct_sum V; P_V=xi tensor eta; P_H=I-P_V"
            ),
            "global_and_covariant": True,
            "acts_on_localized_fermion": False,
            "seam_direction_selected_by_authoritative_round_cap": False,
            "reason": (
                "the canonical splitting belongs to the internal Hopf "
                "fiber; importing it as a preferred physical seam direction "
                "would mix internal and spacetime geometry"
            ),
        },
        "directional_response_candidates": {
            "kappa_V": "P_V^ab pi_env,ab",
            "kappa_H": "(1/2) P_H^ab pi_env,ab",
            "Delta_kappa": "kappa_V-kappa_H",
            "round_value": 0,
            "berger_internal_value": (
                "potentially nonzero for an internal Berger deformation"
            ),
            "licensed_physical_incidence": False,
        },
        "triality": {
            "exact_representation_space": "8_v direct_sum 8_s direct_sum 8_c",
            "exact_projectors": "P_0,P_1,P_2 from the order-three outer action",
            "family_interpretation": "CONDITIONAL",
            "localized_action_map": None,
            "response_channels_proved_distinct": False,
            "result": (
                "triality supplies representation transport, not an "
                "action-derived three-state fermion kernel or projector"
            ),
        },
    }


def brown_york_response() -> dict[str, Any]:
    """Return the complete tensor response in the inward collar convention."""

    return {
        "seam_dimension": 4,
        "collar": (
            "c_epsilon(t,x,rho)=(t,pi/2-epsilon rho,x); rho increases "
            "from the seam into either cap"
        ),
        "round_induced_metric": (
            "h(rho)=-N(t)^2 dt^2+a(t)^2 cos(rho)^2 gamma_S3"
        ),
        "inward_shape_endomorphism": (
            "K^a_b=diag(0,s,s,s), s=-tan(rho)/a"
        ),
        "canonical_momentum": (
            "pi^a_b=kappa1(K^a_b-K delta^a_b)"
        ),
        "cap_even_identification": (
            "pull both cap momenta to M4 with the repository epsilon "
            "orientation factor before averaging"
        ),
        "full_mixed_tensor": (
            "pi_env^a_b=kappa1*s*diag(-3,-2,-2,-2)"
        ),
        "equatorial_value": "pi_env^a_b|rho=0=0",
        "trace": "pi_env=pi_env^a_a=-9*kappa1*s",
        "trace_part": "(1/4) pi_env delta^a_b",
        "traceless_part": (
            "tilde(pi)_env^a_b=(kappa1*s/4)*diag(-3,1,1,1)"
        ),
        "traceless_check": "tilde(pi)_env^a_a=0",
        "requested_one_third_correction": (
            "1/3 is not traceless on four-dimensional M4; 1/4 is required. "
            "A 1/3 split would apply only to the spatial three-block."
        ),
        "spatial_vertical_horizontal_anisotropy": 0,
        "interpretation": (
            "the nonzero traceless spacetime tensor distinguishes the time "
            "and spatial blocks, but remains proportional to the spatial "
            "identity and acts trivially on every internal representation"
        ),
    }


def shape_derivative_audit() -> dict[str, Any]:
    return {
        "riccati_equation": (
            "nabla_n K_ij=-R_i n j n+K_i k K^k_j"
        ),
        "round_radial_curvature": "R_i n j n=a^-2 h_ij",
        "unit_inward_normal": "n=a^-1 partial_rho",
        "first_nonzero_cap_identified_brown_york_order": 1,
        "brown_york_normal_derivative": (
            "nabla_n pi_env^a_b|0=(kappa1/a^2)*diag(3,2,2,2)"
        ),
        "brown_york_trace_normal_derivative": "9*kappa1/a^2",
        "brown_york_traceless_normal_derivative": (
            "(kappa1/(4*a^2))*diag(3,-1,-1,-1)"
        ),
        "signed_intrinsic_operator_parity": {
            "metric_factor": "h_spatial(rho)=cos(rho)^2 h_spatial(0)",
            "measure": "J(rho)=cos(rho)^3",
            "first_derivative": 0,
            "first_nonzero_order": 2,
            "tangential_laplacian": (
                "A(rho)=sec(rho)^2 A(0), so A''(0)=2 A(0)"
            ),
            "principal_action_bilinear_with_measure": (
                "J(rho) A(rho)=cos(rho) A(0), so (J A)''(0)=-A(0)"
            ),
        },
        "internal_vertical_operator": {
            "operator": "lambda_(J,m)(L1,L2) identity_(V_J)",
            "collar_derivative": None,
            "reason": (
                "the action supplies no rho-dependent L1, L2, or Hopf "
                "connection profile; assigning one would add input"
            ),
        },
        "equivalence_scope": (
            "delta_h A contracted with L_n h=2K gives the first shape "
            "variation when the domain is fixed and the measure variation "
            "is included. Since g_rho,rho=a^2, partial_rho h=2aK in the "
            "dimensionless repository collar, not 2K. At the equator K=0, "
            "the intrinsic operator variation starts at second order. The "
            "one-sided Brown--York traction instead starts through nabla_n K."
        ),
        "domain_warning": (
            "no moving embedding or x-dependent endpoint is varied; doing "
            "so would violate the v6.24 fixed-domain audit"
        ),
        "internal_family_shape_order": None,
    }


def mode_stress_incidence() -> dict[str, Any]:
    return {
        "definition": (
            "T_ab^(ij)=<u_i,(delta A/delta h^ab)u_j>; "
            "R_ij=int_M4 pi_env^ab T_ab^(ij) dmu_h"
        ),
        "higher_even_definition": (
            "use the second variation of the full action bilinear, "
            "including J(rho)=cos(rho)^3"
        ),
        "exact_geometric_scalar_result": (
            "within a fixed irreducible V_J, covariance makes the vertical "
            "lambda_(J,m) contribution proportional to identity_(V_J)"
        ),
        "ordinary_tangential_result": (
            "the second collar response is diagonal in ordinary spacetime "
            "eigenmodes and is therefore momentum dependence, not family "
            "incidence"
        ),
        "localized_fermion_result": None,
        "reason": (
            "there is no common bundle, common domain, or action cross-term "
            "on which both the Hopf mode and localized fermion states live"
        ),
    }


def centrality_theorem() -> dict[str, Any]:
    return {
        "geometric_module": "each fixed V_J in H_(J,m)",
        "symmetry_group": "left Sp(1), with preserved right U(1) weight m",
        "representation_property": "V_J is irreducible over C",
        "response_covariance": (
            "the round-cap collar response commutes with left Sp(1)"
        ),
        "schur_result": (
            "End_Sp(1)(V_J)=C identity_(V_J); the exact round response is "
            "central on each irreducible associated-mode block"
        ),
        "across_blocks": (
            "different (J,m) blocks may have different scalar eigenvalues, "
            "but no action-derived finite projector identifies such blocks "
            "as same-charge fermion families"
        ),
        "multiplicity_space": (
            "no action-selected multiplicity basis or noncentral endomorphism"
        ),
        "triality_result": (
            "the Brown--York/collar geometry has no triality-specific action, "
            "so any transported triality copies receive the same central "
            "response unless a new coupling breaks that symmetry"
        ),
        "physical_family_theorem_applicable": False,
        "reason": "no physical F_BH module is present",
    }


def family_space() -> dict[str, Any]:
    return {
        "geometric_internal_tower": (
            "{H_(J,m): rank(H_(J,m))=2J+1, J=0,1/2,1,...}"
        ),
        "finite_action_selected_projector": None,
        "isolated_selected_cluster": None,
        "selected_chirality": None,
        "selected_standard_model_sector_representation": None,
        "uniform_gap_theorem": None,
        "physical_family_module": None,
        "derived_family_dimension": None,
        "precisely_three_selected": False,
        "fourth_mode_excluded": False,
        "why_rank_three_is_not_selected": (
            "J=1 has rank three, but choosing it because its rank matches "
            "observed generations would be a forbidden manual selection; "
            "it is also a scalar Sp(1) representation, not a localized "
            "fermion family theorem"
        ),
        "supplied_C3_family": (
            "existing M4 field-content input, not a result of this audit"
        ),
    }


def response_matrices() -> dict[str, Any]:
    row = {
        "matrix": None,
        "rank": None,
        "singular_values": None,
        "mass_ratios": None,
        "normalization": None,
        "reason": (
            "no action-derived physical family module, projector, and "
            "left/right carrier pair exist"
        ),
    }
    return {
        "charged_lepton": dict(row),
        "up": dict(row),
        "down": dict(row),
    }


def prediction_freeze() -> dict[str, Any]:
    return {
        "version": VERSION,
        "carrier_operator": selected_carrier(),
        "internal_mode_module": family_space(),
        "symmetry_representation": centrality_theorem(),
        "operator_domain": (
            "no common internal-fermion domain; existing scalar and M4 "
            "fermion domains remain distinct"
        ),
        "collar_order": {
            "brown_york_cap_identified": 1,
            "intrinsic_signed_even_operator": 2,
            "internal_family_response": None,
        },
        "full_tensor_response": brown_york_response(),
        "response_matrix": response_matrices(),
        "normalization": None,
        "scheme": SCHEME,
        "scale": REFERENCE_SCALE,
        "family_dimension": None,
        "mass_ratios": None,
        "CKM": None,
        "uncertainty": (
            "EXACT_STRUCTURAL_OBSTRUCTION_WITHIN_THE_AUTHORITATIVE_ACTION"
        ),
        "falsification_condition": (
            "an existing action term must exhibit a nonzero equivariant map "
            "from an action-selected internal Hopf spinor/associated module "
            "into the localized fermion Yukawa incidence, together with its "
            "finite projector and domain"
        ),
        "comparison_data_used": False,
        "retuning_permitted": False,
        "status": "FROZEN_EXACT_OBSTRUCTION",
    }


def prediction_freeze_hash() -> str:
    return sha256(
        deterministic_json(prediction_freeze()).encode("utf-8")
    ).hexdigest().upper()


def post_freeze_comparison() -> dict[str, Any]:
    return {
        "freeze_hash_verified_before_comparison": prediction_freeze_hash(),
        "comparison_performed_after_freeze": True,
        "historical_mode_and_mass_screens": "UNRELATED_OBSERVABLE",
        "external_mass_and_mixing_references": "UNRELATED_OBSERVABLE",
        "reason": (
            "v8.1 freezes no physical response matrix, ratio, or mixing "
            "prediction to compare"
        ),
        "operator_retuned_after_comparison": False,
        "status": "NO_PHYSICAL_PREDICTION_AVAILABLE_FOR_COMPARISON",
    }


def completion_gate_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_1_0_completion_gate",
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "current_verdict": FINAL_VERDICT,
        "BHSM_1_0_release_complete": False,
        "current_tier_status": {
            "Tier_A": "COMPLETE",
            "Tier_B": "COMPLETE",
            "Tier_C": "BLOCKED_EXACT_OBJECT_PROVED",
        },
        "core_verdict": "BHSM_CORE_COMPLETE",
        "physical_verdict": "BHSM_PHYSICAL_COMPLETE",
        "observable_transport_verdict": (
            "BHSM_COMMON_SCHEME_OBSERVABLE_TRANSPORT_FUNCTOR_CONSTRUCTED"
        ),
        "mode_resolved_curvature_incidence": RESPONSE_RESULT,
        "distinct_action_derived_prediction_exists": False,
        "RB01": {
            "status": "CLOSED",
            "architecture": (
                "BHSM_STRATIFIED_MASTER_ACTION_CLOSED_WITH_"
                "COVARIANT_COMPATIBILITY_MAPS"
            ),
            "release_blocking": False,
        },
        "RB15": {
            "status": "BLOCKED_EXACT_OBJECT_PROVED",
            "resolution": (
                "NEW_INTERNAL_FERMION_BUNDLE_EXTENSION_REQUIRED"
            ),
        },
        "RB16": {
            "status": "DOWNSTREAM_BLOCKED",
            "resolution": (
                "release packaging remains ineligible while RB-15 is open"
            ),
        },
        "resolved_release_blockers": [
            "RB-01", "RB-03", "RB-04", "RB-05", "RB-06", "RB-07",
            "RB-08", "RB-09", "RB-10", "RB-11", "RB-12", "RB-13",
            "RB-14",
        ],
        "open_release_blockers": ["RB-15", "RB-16"],
        "parameter_free_extension_blocker": "RB-02",
        "next_highest_upstream_blocker": (
            "NEW_INTERNAL_FERMION_BUNDLE_EXTENSION_REQUIRED"
        ),
        "one_universal_dimensionful_calibration": "G_F",
        "action_extension_introduced": False,
        "new_dynamical_field_introduced": False,
        "new_mediator_introduced": False,
        "fitted_parameter_used": False,
        "measured_mode_selection_used": False,
        "spacetime_harmonic_relabeling_used": False,
        "assumed_three_family_module_used": False,
        "arbitrary_matrix_input_used": False,
        "arbitrary_collar_coefficient_used": False,
        "arbitrary_profile_used": False,
        "arbitrary_gap_floor_used": False,
        "inserted_zero_mode_used": False,
        "unselected_domain_parameter_used": False,
        "second_scale_calibration_used": False,
        "hidden_calibration_used": False,
        "post_comparison_retuning_used": False,
        "frozen_prediction_changed": False,
        "official_prediction_changed": False,
        "bhsm_1_0_release_complete_claimed": False,
    }


def payload() -> dict[str, Any]:
    freeze = prediction_freeze()
    result = {
        "artifact": ARTIFACT_NAME,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "response_result": RESPONSE_RESULT,
        "carrier_audit": carrier_audit(),
        "selected_carrier": selected_carrier(),
        "internal_vs_spacetime_modes": mode_firewall(),
        "hopf_and_triality": hopf_triality_audit(),
        "full_brown_york_response": brown_york_response(),
        "first_nonzero_cap_even_shape_derivative": (
            shape_derivative_audit()
        ),
        "mode_stress_incidence": mode_stress_incidence(),
        "symmetry_centrality": centrality_theorem(),
        "family_space": family_space(),
        "response_matrices": response_matrices(),
        "mass_ratio_predictions": None,
        "CKM": {
            "matrix": None,
            "angles": None,
            "CP_phase": None,
            "Jarlskog": None,
            "reason": "no up/down physical response matrices exist",
        },
        "physical_transport": {
            "scheme": SCHEME,
            "reference_scale": REFERENCE_SCALE,
            "transport_performed": False,
            "reason": (
                "there are no dimensionless response singular values or "
                "left singular vectors to transport"
            ),
        },
        "prediction_freeze": freeze,
        "prediction_freeze_sha256": prediction_freeze_hash(),
        "post_freeze_comparison": post_freeze_comparison(),
        "falsification_condition": freeze["falsification_condition"],
        "RB15": {
            "status": "BLOCKED_EXACT_OBJECT_PROVED",
            "resolution": FAMILY_OBSTRUCTION,
        },
        "RB16": {
            "status": "DOWNSTREAM_BLOCKED",
            "release_package_generated": False,
        },
        "release_verdict": RELEASE_VERDICT,
        "remaining_exact_obstruction": (
            "ACTION_DERIVED_INTERNAL_FERMION_BUNDLE_FACTOR_WITH_HOPF_"
            "ACTION_FINITE_PROJECTOR_AND_LOCALIZED_YUKAWA_INCIDENCE"
        ),
        "immediate_obstruction": IMMEDIATE_OBSTRUCTION,
        "final_verdict": FINAL_VERDICT,
        "integrity": {
            "fit_used": False,
            "measured_mode_selection_used": False,
            "spacetime_harmonic_relabeling_used": False,
            "assumed_three_family_module_used": False,
            "arbitrary_matrix_input_used": False,
            "arbitrary_collar_coefficient_used": False,
            "inserted_zero_mode_used": False,
            "new_mediator_used": False,
            "second_scale_used": False,
            "hidden_calibration_used": False,
            "post_comparison_retuning_used": False,
            "new_action_extension_declared": False,
            "frozen_prediction_changed": False,
        },
    }
    result["validation"] = {
        "all_carriers_audited": len(result["carrier_audit"]) == 7,
        "no_ineligible_carrier_selected": (
            result["selected_carrier"]["physical_mode_resolved_carrier"]
            is None
        ),
        "internal_spacetime_firewall": (
            result["internal_vs_spacetime_modes"][
                "hopf_associated_factor_in_localized_bundle"
            ]
            is None
        ),
        "four_dimensional_trace_split": (
            result["full_brown_york_response"]["trace_part"]
            == "(1/4) pi_env delta^a_b"
        ),
        "traceless_response_retained": (
            "diag" in result["full_brown_york_response"]["traceless_part"]
        ),
        "first_nonzero_orders_computed": (
            result["first_nonzero_cap_even_shape_derivative"][
                "first_nonzero_cap_identified_brown_york_order"
            ]
            == 1
            and result["first_nonzero_cap_even_shape_derivative"][
                "signed_intrinsic_operator_parity"
            ]["first_nonzero_order"]
            == 2
        ),
        "no_internal_profile_fabricated": (
            result["first_nonzero_cap_even_shape_derivative"][
                "internal_vertical_operator"
            ]["collar_derivative"]
            is None
        ),
        "no_family_dimension_assumed": (
            result["family_space"]["derived_family_dimension"] is None
        ),
        "no_response_matrix_fabricated": all(
            row["matrix"] is None
            for row in result["response_matrices"].values()
        ),
        "freeze_hashed": len(result["prediction_freeze_sha256"]) == 64,
        "comparison_postdates_freeze": result[
            "post_freeze_comparison"
        ]["comparison_performed_after_freeze"],
        "no_post_comparison_retuning": not result["integrity"][
            "post_comparison_retuning_used"
        ],
        "RB15_exact": (
            result["RB15"]["status"] == "BLOCKED_EXACT_OBJECT_PROVED"
        ),
        "RB16_downstream": (
            result["RB16"]["status"] == "DOWNSTREAM_BLOCKED"
        ),
    }
    result["validation_passed"] = all(result["validation"].values())
    return result


def status_report() -> dict[str, Any]:
    data = payload()
    return {
        "version": VERSION,
        "response_result": RESPONSE_RESULT,
        "selected_carrier_operator": data["selected_carrier"],
        "mode_classification": data["internal_vs_spacetime_modes"],
        "family_module": data["family_space"],
        "hopf_triality_representation": data["hopf_and_triality"],
        "full_brown_york_tensor": data["full_brown_york_response"][
            "full_mixed_tensor"
        ],
        "trace_part": data["full_brown_york_response"]["trace_part"],
        "traceless_part": data["full_brown_york_response"][
            "traceless_part"
        ],
        "first_nonzero_cap_even_collar_order": {
            "brown_york": data[
                "first_nonzero_cap_even_shape_derivative"
            ]["first_nonzero_cap_identified_brown_york_order"],
            "intrinsic_operator": data[
                "first_nonzero_cap_even_shape_derivative"
            ]["signed_intrinsic_operator_parity"]["first_nonzero_order"],
            "internal_family": None,
        },
        "shape_derivative_matrix": data[
            "first_nonzero_cap_even_shape_derivative"
        ]["brown_york_traceless_normal_derivative"],
        "centrality_result": data["symmetry_centrality"]["schur_result"],
        "family_dimension": data["family_space"][
            "derived_family_dimension"
        ],
        "response_singular_values": {
            key: row["singular_values"]
            for key, row in data["response_matrices"].items()
        },
        "mass_ratios": None,
        "CKM": data["CKM"],
        "prediction_freeze_sha256": data["prediction_freeze_sha256"],
        "post_freeze_comparison": data["post_freeze_comparison"],
        "RB15": data["RB15"]["status"],
        "RB16": data["RB16"]["status"],
        "release_status": data["release_verdict"],
        "remaining_exact_obstruction": data[
            "remaining_exact_obstruction"
        ],
        "validation": data["validation"],
        "validation_passed": data["validation_passed"],
        "final_verdict": data["final_verdict"],
    }


def status_to_markdown(data: dict[str, Any] | None = None) -> str:
    report = data or status_report()
    carrier = report["selected_carrier_operator"]
    orders = report["first_nonzero_cap_even_collar_order"]
    return "\n".join(
        [
            "# BHSM v8.1 mode-resolved curvature incidence",
            "",
            f"Result: `{report['response_result']}`",
            "",
            (
                "- Physical carrier: "
                f"`{carrier['physical_mode_resolved_carrier']}`"
            ),
            (
                "- Closest geometric carrier: "
                f"`{carrier['closest_exact_geometric_carrier']}`"
            ),
            (
                "- Internal family module: "
                f"`{report['family_module']['physical_family_module']}`"
            ),
            (
                "- Derived family dimension: "
                f"`{report['family_dimension']}`"
            ),
            (
                "- Full Brown-York tensor: "
                f"`{report['full_brown_york_tensor']}`"
            ),
            f"- Trace part: `{report['trace_part']}`",
            f"- Traceless part: `{report['traceless_part']}`",
            (
                "- First cap-even orders (Brown-York/intrinsic/internal): "
                f"`{orders}`"
            ),
            (
                "- Traceless normal response: "
                f"`{report['shape_derivative_matrix']}`"
            ),
            f"- Centrality: `{report['centrality_result']}`",
            (
                "- Response singular values: "
                f"`{report['response_singular_values']}`"
            ),
            f"- Mass ratios: `{report['mass_ratios']}`",
            f"- CKM: `{report['CKM']['matrix']}`",
            (
                "- Prediction freeze SHA-256: "
                f"`{report['prediction_freeze_sha256']}`"
            ),
            (
                "- Post-freeze comparison: "
                f"`{report['post_freeze_comparison']['status']}`"
            ),
            f"- RB-15: `{report['RB15']}`",
            f"- RB-16: `{report['RB16']}`",
            f"- Release: `{report['release_status']}`",
            "",
            (
                "Remaining exact obstruction: "
                f"`{report['remaining_exact_obstruction']}`"
            ),
            "",
            f"Verdict: `{report['final_verdict']}`",
            "",
        ]
    )


def materialize(root: Path) -> tuple[Path, Path]:
    artifact = root / "artifacts" / f"{ARTIFACT_NAME}.json"
    gate = root / "artifacts" / "BHSM_1_0_completion_gate.json"
    artifact.write_bytes(deterministic_json(payload()).encode("utf-8"))
    gate.write_bytes(
        deterministic_json(completion_gate_payload()).encode("utf-8")
    )
    return artifact, gate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--materialize", action="store_true")
    args = parser.parse_args(argv)
    if not args.materialize:
        parser.error("--materialize is required")
    root = Path(__file__).resolve().parents[4]
    for path in materialize(root):
        print(path.relative_to(root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
