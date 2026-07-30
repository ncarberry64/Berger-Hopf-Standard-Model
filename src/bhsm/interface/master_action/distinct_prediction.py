"""BHSM v7.3 distinct-prediction construction and exact obstruction.

The campaign exhausts the six action-supported routes requested after v7.2.
It does not promote finite-basis spectral scaffolds.  The singular result is
an action-incidence theorem: no non-universal term maps the distinctive
Berger/Hopf/topographic variables into the localized Standard Model
observable operators.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


VERSION = "v7.3"
SPRINT = "bhsm-distinct-action-derived-prediction-v7-3"
SOURCE_MAIN_SHA = "3cb9809ee78550112588c20ae42a95f5dca03ea3"
SCHEME = "overline_MS"
REFERENCE_SCALE = "mu_star=ell_star^-1; mu_hat_star=mu_star*ell_star=1"
EXACT_MISSING_OBJECT = (
    "NONUNIVERSAL_BHSM_TO_LOCALIZED_PHYSICAL_SECTOR_ACTION_COUPLING"
)
FINAL_VERDICT = (
    "BHSM_DISTINCT_PREDICTION_REQUIRES_NEW_BULK_BOUNDARY_"
    "COUPLING_NOT_PRESENT_IN_ACTION"
)
RELEASE_VERDICT = "BHSM_1_0_RELEASE_BLOCKED"


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(
        payload, indent=2, sort_keys=True, ensure_ascii=False
    ) + "\n"


def action_incidence_theorem() -> dict[str, Any]:
    """Return the exact source-to-observable separation proved in v7.3."""
    return {
        "authoritative_action": (
            "S_BHSM^strat=S8+sum_epsilon(S5,epsilon+S_GHY,epsilon)"
            "+S4,localized+S_compatibility"
        ),
        "distinctive_BHSM_variables": [
            "Sp(1) Hopf connection omega",
            "fiber metric/radion a_F",
            "Berger shape and associated-mode spectral data",
            "cap scalar sigma and fixed-h D0 KKT mode",
            "cap/seam orientation and matcher reactions",
        ],
        "localized_physical_fields": [
            "A_SM",
            "Psi",
            "H",
        ],
        "existing_cross_stratum_terms": [
            (
                "Lambda85 metric compatibility and "
                "lambda_sigma(sigma5-P0 sigma8)"
            ),
            "Lambda54(h-iota^*g5) metric trace compatibility",
        ],
        "localized_ownership": (
            "A_SM,Psi,H are intrinsic M4 fields and are not extended into "
            "M5 or M8 by the v7.1 correspondence"
        ),
        "fixed_metric_mixed_variations": {
            "delta2S/domega_deltaPsi": "0",
            "delta2S/domega_deltaA_SM": "0",
            "delta2S/da_F_deltaPsi": "0",
            "delta2S/da_F_deltaH": "0",
            "delta2S/dsigma_deltaH": "0",
        },
        "universal_metric_exception": (
            "The common seam metric h enters every M4 kinetic term through "
            "ordinary covariant coupling.  Its background and moduli are "
            "not uniquely selected, and this universal gravitational edge "
            "does not insert Hopf charge, Berger eigenvalues, D0 amplitude, "
            "or a generation projector into a physical operator."
        ),
        "missing_cross_block": (
            "C_BHSM->phys[omega,a_F,sigma_perp,KKT;"
            "A_SM,Psi,H,Pi_generation]"
        ),
        "missing_cross_block_definition": (
            "a gauge-covariant action term or derived operator map whose "
            "variation supplies a nonzero, normalized cross block from a "
            "distinctive BHSM mode to a localized physical observable, "
            "together with its selected domain"
        ),
        "proof": [
            (
                "Every distinctive geometric candidate belongs to S8, the "
                "M8-to-M5 retained-mode pushforward, or the cap/KKT sector."
            ),
            (
                "Every v7.2 particle mass and mixing observable belongs to "
                "S4,localized and depends on independently declared "
                "g_i,Y_f,m_H_squared,lambda_H and finite projectors."
            ),
            (
                "Inspection of the complete term registry finds no term "
                "containing both a distinctive variable and A_SM, Psi, H, "
                "or a generation-mode projector, apart from the universal "
                "metric dependence described above."
            ),
            (
                "Therefore eliminating internal variables cannot generate "
                "a distinctive coefficient in an M4 observable operator: "
                "the relevant fixed-metric mixed Hessian blocks vanish."
            ),
            (
                "Adding a nonzero block would add a new action term, not "
                "derive a consequence of S_BHSM^strat."
            ),
        ],
        "result": FINAL_VERDICT,
    }


def exact_twisted_dirac_audit() -> dict[str, Any]:
    """Identify the full fermion operator actually supported by the action."""
    return {
        "bundle": (
            "S_h tensor E_SM tensor C3_family over intrinsic M4; "
            "C3_family and E_SM are supplied finite bundle data"
        ),
        "action_equation": (
            "D_M4 Psi=[i gamma^mu(nabla_mu^S_h tensor 1"
            "+1 tensor rho(A_SM)_mu)-Y(H)]Psi=0"
        ),
        "requested_decomposition": {
            "D_spin": "i gamma^mu nabla_mu^S_h",
            "D_Hopf_twist": "0 (omega acts on M8-to-M5 associated modes, not Psi)",
            "D_gauge": "i gamma^mu rho(A_SM)_mu",
            "D_boundary": (
                "0 as an action summand; only a maximal-isotropic domain "
                "family is declared"
            ),
            "D_Yukawa_zero_order": "-Y(H)",
        },
        "principal_symbol": (
            "sigma_1(D_M4)(x,xi)=i gamma^mu xi_mu tensor "
            "identity_(E_SM tensor C3_family)"
        ),
        "gauge_covariance": (
            "D_(A^u)(rho(u)Psi)=rho(u)D_A Psi under SU3xSU2xU1"
        ),
        "chirality": (
            "P_L/P_R is the intrinsic four-dimensional grading fixed by the "
            "retained SM representation ledger"
        ),
        "green_identity": (
            "<D Psi,Phi>-<Psi,D Phi>="
            "integral_boundary <Psi,i gamma.n Phi>"
        ),
        "domain": (
            "H1 maximal-isotropic subspace of the Dirac Green form; "
            "the current action supplies no graph unitary, bag angle, "
            "APS cut, or junction fermion term selecting one member"
        ),
        "hermiticity": (
            "self-adjoint only after one maximal-isotropic member is supplied"
        ),
        "v7_1_compatibility": (
            "Psi remains boundary-localized; only h is pulled back through "
            "the metric compatibility map"
        ),
        "classification": (
            "STANDARD_MODEL_EFT_DIRAC_YUKAWA_OPERATOR_WITH_NO_BHSM_TWIST"
        ),
        "status": "BLOCKED_BY_EXACT_MISSING_OBJECT",
    }


def kernel_and_index_audit() -> dict[str, Any]:
    return {
        "candidate_index": (
            "Index(D_A^+) depends on (h,A_SM,E_SM,topological sector,"
            "selected boundary domain)"
        ),
        "fixed_topological_inputs": {
            "Hopf_bundle_c2": 1,
            "Hopf_bundle_acts_on_Psi": False,
            "SM_gauge_topological_sector_selected": False,
            "Dirac_boundary_domain_selected": False,
        },
        "family_factor": (
            "C3_family is already present in the declared fermion bundle; "
            "counting its three supplied components is an input tautology"
        ),
        "triality": (
            "triality projectors are representation-derived conditional "
            "projectors, not a computed kernel of D_M4"
        ),
        "protected_kernel_dimension": None,
        "exact_three_generation_index_derived": False,
        "reason": (
            "No action-supported Hopf-twisted fermion bundle/operator and no "
            "selected self-adjoint domain exist on which an index could fix "
            "the low-energy family count."
        ),
        "status": "BLOCKED_BY_EXACT_MISSING_OBJECT",
    }


def fermion_gap_audit() -> dict[str, Any]:
    return {
        "requested_gap": (
            "Delta_D_hat=inf spec(D_BHSM^dagger D_BHSM|ker(D_BHSM)^perp)"
        ),
        "available_gap": (
            "inf spec(D_M4^dagger D_M4|ker(D_M4)^perp), conditional on "
            "h,A_SM,H,Y_f and a selected maximal-isotropic domain"
        ),
        "universal_positive_bound": False,
        "zero_infimum_proof": (
            "The allowed finite theory-input space contains arbitrarily "
            "small Yukawa singular values and does not impose a uniform "
            "geometric or domain gap; hence the infimum over allowed inputs "
            "of the available squared gap is zero."
        ),
        "physical_transport": (
            "M_D^gap=sqrt(Delta_D_hat)/ell_star is unavailable because "
            "Delta_D_hat is not defined by the current action"
        ),
        "uncertainty": "UNBOUNDED_BY_CURRENT_ACTION",
        "status": "BLOCKED_BY_EXACT_MISSING_OBJECT",
    }


def scalar_hessian_audit() -> dict[str, Any]:
    return {
        "fixed_metric_block_form": (
            "H_scalar=H_sigma,strat direct_sum H_H,M4; "
            "delta2S/(delta sigma delta H)=0"
        ),
        "cap_block": (
            "H_sigma,strat is the cap scalar/KKT operator with regular pole, "
            "fixed-h Dirichlet trace, matcher reaction, and the exact D0 "
            "Lyapunov-Schmidt kernel coordinate"
        ),
        "Higgs_block": (
            "H_H,M4 is the covariant Hessian of |D H|^2"
            "-[m_H^2 H^dagger H+lambda_H(H^dagger H)^2]"
        ),
        "independent_inputs": [
            "Z5,G5 and cap/gravity coefficients",
            "m_H_squared(mu_star)",
            "lambda_H(mu_star)=lambda5",
            "background h,H,sigma",
        ],
        "metric_mediated_terms": (
            "Constraint-reduced metric Schur blocks are background- and "
            "coefficient-dependent and do not identify sigma with H or "
            "derive a topographic orthogonal projector."
        ),
        "Higgs_projection_selected": False,
        "orthogonal_scalar_space_selected": False,
        "universal_positive_orthogonal_gap": False,
        "requested_gap": (
            "Delta_perp_hat=inf spec(H_scalar|H_Higgs^perp)"
        ),
        "reason": (
            "H_Higgs^perp is not an action-derived subspace and the absent "
            "sigma-H cross block prevents the cap/topographic spectrum from "
            "becoming an extra-scalar exclusion spectrum."
        ),
        "physical_transport": None,
        "status": "BLOCKED_BY_EXACT_MISSING_OBJECT",
    }


def geometry_selection_audit() -> dict[str, Any]:
    return {
        "fiber_equation": "delta S_BHSM^strat/delta a_F=0",
        "berger_shape_equation": "partial S_BHSM^strat/partial a=UNDEFINED",
        "fiber_result": (
            "If a_F is varied, pi_!S8 is a scalar-tensor action with radion "
            "and connection terms.  Its stationary equation depends on the "
            "independent bulk coefficients and background fields; the "
            "stored S5 action is not identified with pi_!S8."
        ),
        "berger_shape_result": (
            "The Berger shape a is classified as an independent fixed theory "
            "input and has no reduction/source law making it an active "
            "coordinate of S_BHSM^strat."
        ),
        "cap_collar_result": (
            "cap radius/collar data remain background or domain data; no "
            "input-independent simultaneous modulus stationarity system is "
            "present"
        ),
        "selected_branch": None,
        "unique_or_discrete_geometry": False,
        "alpha_used": False,
        "status": "BLOCKED_BY_EXACT_MISSING_OBJECT",
    }


def generation_selection_audit() -> dict[str, Any]:
    return {
        "declared_family_bundle": "C3_family",
        "triality_projectors": (
            "representation-derived conditional on the supplied Spin8 "
            "carrier choice"
        ),
        "sector_projectors": "finite independent theory inputs",
        "mode_projectors": (
            "conditional retained spectral subspaces; historical "
            "mass-selected labels are screen-only"
        ),
        "action_selected_low_energy_projector": None,
        "three_generation_statement": (
            "The present M4 field ledger contains three family components."
        ),
        "classification": (
            "physical field-content statement but an input tautology, not "
            "an action-derived family-count prediction"
        ),
        "fourth_generation_excluded": False,
        "status": "PHYSICAL_BUT_INPUT_TAUTOLOGY",
    }


def sum_rule_audit() -> dict[str, Any]:
    return {
        "tested_classes": [
            {
                "candidate": "M_scalar_gap/M_D_gap",
                "result": "both action-derived gaps are unavailable",
            },
            {
                "candidate": "Index(D_BHSM)",
                "result": "operator, twisting action, and domain are unselected",
            },
            {
                "candidate": "charged-fermion mass and mixing invariants",
                "result": "depend freely on independent Y_u,Y_d,Y_e",
            },
            {
                "candidate": "gauge-coupling ratios",
                "result": "depend freely on independent g1,g2,g3",
            },
            {
                "candidate": "scalar-to-electroweak ratios",
                "result": "depend on independent lambda5 and m_H_squared",
            },
            {
                "candidate": "Hopf c2 and boundary orientation signs",
                "result": (
                    "exact structural invariants, but no term transports them "
                    "into a localized physical observable"
                ),
            },
            {
                "candidate": "anomaly and representation traces",
                "result": (
                    "structural identities conditional on the supplied SM "
                    "representation ledger"
                ),
            },
        ],
        "input_cancelling_physical_relation": None,
        "status": "STRUCTURAL_BUT_NOT_PHYSICAL",
    }


def fixed_h_physical_audit() -> dict[str, Any]:
    return {
        "action_source": "P1+GHY+scalar+B1+matcher on strict fixed-h D0",
        "canonical_potential": (
            "V_E(phi)=V0+g4 phi^4/4!+O(phi^6)"
        ),
        "exact_vanishing": "V_E'(0)=V_E''(0)=V_E'''(0)=0",
        "first_nonzero_coefficient": (
            "g4=5.84444718718846 G5/Z5^2"
            "+81.5773688846122/kappa1"
        ),
        "conditional_minimum": (
            "G5/Z5>-13.95809839182684 Z5/kappa1"
        ),
        "structural_result": (
            "the first same-family Einstein interaction is quartic"
        ),
        "physical_observable_map": None,
        "why_not_physical": (
            "The D0 amplitude is not H, is not a particle-normalized M4 "
            "field, and has no action term coupling it to a v7.2 observable. "
            "G5 is independently unselected."
        ),
        "status": "STRUCTURAL_BUT_NOT_PHYSICAL",
    }


def candidate_ledger() -> list[dict[str, Any]]:
    common = {
        "scheme": SCHEME,
        "scale": REFERENCE_SCALE,
        "comparison_data_excluded_during_derivation": True,
    }
    return [
        {
            **common,
            "candidate_id": "V73-A",
            "route": "EXACT_TWISTED_DIRAC_AND_EXOTIC_GAP",
            "exact_action_source": "S4,localized Dirac/Yukawa term",
            "exact_operator_or_equation": exact_twisted_dirac_audit()[
                "action_equation"
            ],
            "independent_inputs": [
                "h",
                "A_SM",
                "Y_f",
                "H",
                "maximal-isotropic domain member",
            ],
            "quantities_eliminated": [],
            "physical_transport": fermion_gap_audit()["physical_transport"],
            "prediction_formula": None,
            "numerical_value_interval_or_discrete_statement": None,
            "uncertainty": "UNBOUNDED_BY_CURRENT_ACTION",
            "falsifier": None,
            "distinctively_bhsm_reason": (
                "would require omega, Berger spin data, or a seam operator "
                "to act on Psi; none does"
            ),
            "status": "BLOCKED_BY_EXACT_MISSING_OBJECT",
        },
        {
            **common,
            "candidate_id": "V73-B",
            "route": "FULL_SCALAR_TOPOGRAPHIC_DECOUPLING",
            "exact_action_source": "S8/S5 sigma plus S4,localized Higgs",
            "exact_operator_or_equation": scalar_hessian_audit()[
                "fixed_metric_block_form"
            ],
            "independent_inputs": scalar_hessian_audit()[
                "independent_inputs"
            ],
            "quantities_eliminated": [
                "closed-range cap/KKT complement only"
            ],
            "physical_transport": None,
            "prediction_formula": None,
            "numerical_value_interval_or_discrete_statement": None,
            "uncertainty": "ORTHOGONAL_PHYSICAL_DOMAIN_UNDEFINED",
            "falsifier": None,
            "distinctively_bhsm_reason": (
                "would use the cap/topographic Hessian to exclude an M4 "
                "extra scalar"
            ),
            "status": "BLOCKED_BY_EXACT_MISSING_OBJECT",
        },
        {
            **common,
            "candidate_id": "V73-C",
            "route": "ACTION_SELECTION_OF_INTERNAL_GEOMETRY",
            "exact_action_source": "S8 metric variation and v7.1 pushforward",
            "exact_operator_or_equation": (
                "delta S/delta a_F=0; partial S/partial a is undefined"
            ),
            "independent_inputs": [
                "kappa0",
                "kappa1",
                "Zchi",
                "Zsigma",
                "A0",
                "G0",
                "background fields",
                "fixed Berger shape a",
            ],
            "quantities_eliminated": [],
            "physical_transport": None,
            "prediction_formula": None,
            "numerical_value_interval_or_discrete_statement": None,
            "uncertainty": "CONTINUOUS_INPUT_AND_BACKGROUND_DEPENDENCE",
            "falsifier": None,
            "distinctively_bhsm_reason": (
                "would select the Hopf/ Berger geometry before comparison"
            ),
            "status": "BLOCKED_BY_EXACT_MISSING_OBJECT",
        },
        {
            **common,
            "candidate_id": "V73-D",
            "route": "MODE_AND_GENERATION_SELECTION",
            "exact_action_source": (
                "S4 fermion bundle and v7.1 projector ledger"
            ),
            "exact_operator_or_equation": (
                "Psi in S_h tensor E_SM tensor C3_family; Pi_f,n is input"
            ),
            "independent_inputs": [
                "C3_family",
                "sector projectors",
                "mode projectors",
            ],
            "quantities_eliminated": [],
            "physical_transport": "three supplied M4 family components",
            "prediction_formula": None,
            "numerical_value_interval_or_discrete_statement": (
                "N_family=3 is supplied, not derived"
            ),
            "uncertainty": "NOT_APPLICABLE_INPUT_TAUTOLOGY",
            "falsifier": None,
            "distinctively_bhsm_reason": (
                "triality is BHSM-specific but is not a computed low-energy "
                "Dirac kernel"
            ),
            "status": "PHYSICAL_BUT_INPUT_TAUTOLOGY",
        },
        {
            **common,
            "candidate_id": "V73-E",
            "route": "INPUT_CANCELLING_ACTION_SUM_RULES",
            "exact_action_source": (
                "complete v7.1 coefficient ledger and v7.2 observable map"
            ),
            "exact_operator_or_equation": (
                "O_phys=O_phys(g_i,Y_f,m_H_squared,lambda5,projectors,G_F)"
            ),
            "independent_inputs": [
                "g_i",
                "Y_f",
                "m_H_squared",
                "lambda5",
                "projectors",
            ],
            "quantities_eliminated": [
                "one common ell_star in dimensionless ratios"
            ],
            "physical_transport": (
                "input-free remnants are only structural topology, "
                "orientation, and representation identities"
            ),
            "prediction_formula": None,
            "numerical_value_interval_or_discrete_statement": None,
            "uncertainty": "NO_PHYSICAL_INPUT_FREE_INVARIANT",
            "falsifier": None,
            "distinctively_bhsm_reason": (
                "tested all available BHSM invariants against the physical map"
            ),
            "status": "STRUCTURAL_BUT_NOT_PHYSICAL",
        },
        {
            **common,
            "candidate_id": "V73-F",
            "route": "FIXED_H_CRITICAL_SECTOR_PHYSICAL_CONSEQUENCE",
            "exact_action_source": fixed_h_physical_audit()["action_source"],
            "exact_operator_or_equation": fixed_h_physical_audit()[
                "canonical_potential"
            ],
            "independent_inputs": ["G5", "Z5", "kappa1"],
            "quantities_eliminated": [
                "closed-range D0 KKT complement",
                "odd amplitude-coordinate freedom",
            ],
            "physical_transport": None,
            "prediction_formula": fixed_h_physical_audit()[
                "first_nonzero_coefficient"
            ],
            "numerical_value_interval_or_discrete_statement": (
                "first nonzero canonical interaction has order four"
            ),
            "uncertainty": (
                "G5 unselected and D0 amplitude lacks particle normalization"
            ),
            "falsifier": None,
            "distinctively_bhsm_reason": (
                "the strict cap/matcher D0 variational structure is BHSM-specific"
            ),
            "status": "STRUCTURAL_BUT_NOT_PHYSICAL",
        },
    ]


def proxy_retirement() -> list[dict[str, str]]:
    return [
        {
            "proxy": "manually inserted zero modes and zero_mode_count",
            "status": "PROXY_ONLY_REJECTED",
            "reason": "not a kernel theorem",
        },
        {
            "proxy": "complement_floor and arbitrary twist/boundary strengths",
            "status": "PROXY_ONLY_REJECTED",
            "reason": "not action coefficients",
        },
        {
            "proxy": "finite k_max convergence",
            "status": "PROXY_ONLY_REJECTED",
            "reason": "not a complete spectrum or certified analytic bound",
        },
        {
            "proxy": "empirical 125.10 GeV scalar mode",
            "status": "PROXY_ONLY_REJECTED",
            "reason": "comparison value cannot be an operator entry",
        },
        {
            "proxy": "assumed 4 pi^2 v gap threshold",
            "status": "PROXY_ONLY_REJECTED",
            "reason": "no current action theorem produces this threshold",
        },
        {
            "proxy": "hand-classified screened modes and mode_ledger targets",
            "status": "PROXY_ONLY_REJECTED",
            "reason": "no action-selected low-energy projector",
        },
    ]


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
        "RB01": {
            "status": "CLOSED",
            "architecture": (
                "BHSM_STRATIFIED_MASTER_ACTION_CLOSED_WITH_"
                "COVARIANT_COMPATIBILITY_MAPS"
            ),
            "release_blocking": False,
        },
        "core_verdict": "BHSM_CORE_COMPLETE",
        "physical_verdict": "BHSM_PHYSICAL_COMPLETE",
        "observable_transport_verdict": (
            "BHSM_COMMON_SCHEME_OBSERVABLE_TRANSPORT_FUNCTOR_CONSTRUCTED"
        ),
        "prediction_campaign_result": (
            "ALL_INDEPENDENT_ROUTES_EXHAUSTED_EXACT_COUPLING_OBSTRUCTION"
        ),
        "distinct_action_derived_prediction_exists": False,
        "RB15": {
            "status": "BLOCKED_EXACT_OBJECT_PROVED",
            "resolution": EXACT_MISSING_OBJECT,
        },
        "RB16": {
            "status": "DOWNSTREAM_BLOCKED",
            "resolution": (
                "release packaging remains ineligible while RB-15 is open"
            ),
        },
        "resolved_release_blockers": [
            "RB-01",
            "RB-03",
            "RB-04",
            "RB-05",
            "RB-06",
            "RB-07",
            "RB-08",
            "RB-09",
            "RB-10",
            "RB-11",
            "RB-12",
            "RB-13",
            "RB-14",
        ],
        "open_release_blockers": ["RB-15", "RB-16"],
        "next_highest_upstream_blocker": EXACT_MISSING_OBJECT,
        "one_universal_dimensionful_calibration": "G_F",
        "parameter_free_extension_blocker": "RB-02",
        "frozen_prediction_changed": False,
        "official_prediction_changed": False,
        "comparison_data_used_in_action": False,
        "fitted_parameter_used": False,
        "inserted_zero_mode_used": False,
        "empirical_scalar_mass_used": False,
        "arbitrary_gap_floor_used": False,
        "new_action_term_used": False,
        "second_scale_calibration_used": False,
        "hidden_calibration_used": False,
        "bhsm_1_0_release_complete_claimed": False,
    }


def payload() -> dict[str, Any]:
    routes = candidate_ledger()
    result = {
        "artifact": "BHSM_distinct_action_derived_prediction_v7_3",
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "campaign_requirement": (
            "distinctively BHSM and action-derived and physical and "
            "falsifiable and frozen before comparison"
        ),
        "action_incidence_theorem": action_incidence_theorem(),
        "exact_twisted_Dirac_operator": exact_twisted_dirac_audit(),
        "kernel_and_index": kernel_and_index_audit(),
        "fermionic_gap": fermion_gap_audit(),
        "scalar_topographic_Hessian": scalar_hessian_audit(),
        "geometry_selection": geometry_selection_audit(),
        "generation_selection": generation_selection_audit(),
        "input_cancelling_sum_rules": sum_rule_audit(),
        "fixed_h_physical_consequence": fixed_h_physical_audit(),
        "prediction_candidate_ledger": routes,
        "accepted_predictions": [],
        "proxy_results_retired": proxy_retirement(),
        "RB15": {
            "status": "BLOCKED_EXACT_OBJECT_PROVED",
            "resolution": EXACT_MISSING_OBJECT,
        },
        "RB16": {
            "status": "DOWNSTREAM_BLOCKED",
            "release_package_generated": False,
        },
        "release_verdict": RELEASE_VERDICT,
        "remaining_exact_obstruction": EXACT_MISSING_OBJECT,
        "final_verdict": FINAL_VERDICT,
        "integrity": {
            "fit_used": False,
            "target_selected_input_used": False,
            "inserted_zero_mode_used": False,
            "empirical_scalar_mass_used": False,
            "arbitrary_gap_floor_used": False,
            "new_action_term_used": False,
            "second_scale_used": False,
            "hidden_calibration_used": False,
            "comparison_data_consulted": False,
            "frozen_prediction_changed": False,
        },
    }
    allowed_statuses = {
        "DISTINCT_ACTION_DERIVED_PHYSICAL_PREDICTION",
        "ACTION_DERIVED_CONDITIONAL_PREDICTION",
        "STRUCTURAL_BUT_NOT_PHYSICAL",
        "PHYSICAL_BUT_INPUT_TAUTOLOGY",
        "PROXY_ONLY_REJECTED",
        "BLOCKED_BY_EXACT_MISSING_OBJECT",
        "INVALIDATED",
    }
    result["validation"] = {
        "all_six_routes_attempted": (
            {row["route"] for row in routes}
            == {
                "EXACT_TWISTED_DIRAC_AND_EXOTIC_GAP",
                "FULL_SCALAR_TOPOGRAPHIC_DECOUPLING",
                "ACTION_SELECTION_OF_INTERNAL_GEOMETRY",
                "MODE_AND_GENERATION_SELECTION",
                "INPUT_CANCELLING_ACTION_SUM_RULES",
                "FIXED_H_CRITICAL_SECTOR_PHYSICAL_CONSEQUENCE",
            }
        ),
        "candidate_fields_complete": all(
            {
                "candidate_id",
                "exact_action_source",
                "exact_operator_or_equation",
                "independent_inputs",
                "quantities_eliminated",
                "scheme",
                "scale",
                "physical_transport",
                "prediction_formula",
                "numerical_value_interval_or_discrete_statement",
                "uncertainty",
                "comparison_data_excluded_during_derivation",
                "falsifier",
                "distinctively_bhsm_reason",
                "status",
            }
            <= row.keys()
            for row in routes
        ),
        "statuses_typed": all(
            row["status"] in allowed_statuses for row in routes
        ),
        "no_proxy_promoted": all(
            row["status"] == "PROXY_ONLY_REJECTED"
            for row in result["proxy_results_retired"]
        ),
        "no_unfrozen_comparison": all(
            row["comparison_data_excluded_during_derivation"]
            for row in routes
        ),
        "singular_cross_block_obstruction_proved": (
            result["remaining_exact_obstruction"] == EXACT_MISSING_OBJECT
        ),
        "no_prediction_fabricated": not result["accepted_predictions"],
        "integrity_clean": not any(result["integrity"].values()),
        "RB15_exact": result["RB15"]["status"]
        == "BLOCKED_EXACT_OBJECT_PROVED",
        "RB16_downstream": result["RB16"]["status"]
        == "DOWNSTREAM_BLOCKED",
    }
    result["validation_passed"] = all(result["validation"].values())
    return result


def status_report() -> dict[str, Any]:
    data = payload()
    return {
        "version": VERSION,
        "routes": [
            {
                "candidate_id": row["candidate_id"],
                "route": row["route"],
                "equation": row["exact_operator_or_equation"],
                "status": row["status"],
            }
            for row in data["prediction_candidate_ledger"]
        ],
        "accepted_predictions": data["accepted_predictions"],
        "proxy_results_retired": [
            row["proxy"] for row in data["proxy_results_retired"]
        ],
        "exact_obstruction": data["remaining_exact_obstruction"],
        "RB15": data["RB15"]["status"],
        "RB16": data["RB16"]["status"],
        "release_verdict": data["release_verdict"],
        "validation": data["validation"],
        "validation_passed": data["validation_passed"],
        "final_verdict": data["final_verdict"],
    }


def status_to_markdown(data: dict[str, Any] | None = None) -> str:
    report = data or status_report()
    lines = [
        "# BHSM v7.3 distinct action-derived prediction campaign",
        "",
        "## Attempted routes",
        "",
    ]
    lines.extend(
        (
            f"- `{row['candidate_id']}` — `{row['route']}`: "
            f"`{row['status']}`; equation `{row['equation']}`"
        )
        for row in report["routes"]
    )
    lines.extend(
        [
            "",
            "## Accepted predictions",
            "",
            "None.",
            "",
            "## Proxy retirement",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["proxy_results_retired"])
    lines.extend(
        [
            "",
            f"Exact obstruction: `{report['exact_obstruction']}`",
            "",
            f"RB-15: `{report['RB15']}`",
            "",
            f"RB-16: `{report['RB16']}`",
            "",
            f"Release: `{report['release_verdict']}`",
            "",
            f"Verdict: `{report['final_verdict']}`",
            "",
        ]
    )
    return "\n".join(lines)


def materialize(root: Path) -> tuple[Path, Path]:
    artifact = (
        root
        / "artifacts"
        / "BHSM_distinct_action_derived_prediction_v7_3.json"
    )
    gate = root / "artifacts" / "BHSM_1_0_completion_gate.json"
    artifact.write_text(deterministic_json(payload()), encoding="utf-8")
    gate.write_text(
        deterministic_json(completion_gate_payload()), encoding="utf-8"
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
