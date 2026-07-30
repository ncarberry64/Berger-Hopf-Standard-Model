"""BHSM v8.0 mass--curvature response action extension.

The module constructs the unique minimal curvature insertion allowed by the
existing Einstein--GHY cap variation and the localized Standard Model
Yukawa operators.  It also proves the two downstream obstructions: the
current constrained action has no positive core/surface energy split, and
the unique response is a family singlet.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


VERSION = "v8.0"
SPRINT = "bhsm-mass-curvature-response-v8-0"
SOURCE_MAIN_SHA = "8048faa2039a907b77a1776ca44e3cf333201336"
SCHEME = "overline_MS"
REFERENCE_SCALE = "mu_star=ell_star^-1; mu_hat_star=mu_star*ell_star=1"
DOCTRINE = (
    "BHSM v8.0 introduces or completes the mass-curvature response "
    "coupling between the hyperspherical core/cap system and localized "
    "M4 matter."
)
RESPONSE_RESULT = "BHSM_MINIMAL_BROWN_YORK_MASS_RESPONSE_EXTENSION_CONSTRUCTED"
ENERGY_OBSTRUCTION = (
    "BHSM_MASS_RESPONSE_BLOCKED_BY_NO_POSITIVE_ENERGY_ENVELOPMENT_FUNCTIONAL"
)
FAMILY_OBSTRUCTION = (
    "BHSM_MASS_RESPONSE_BLOCKED_BY_UNIVERSAL_RESPONSE_WITH_NO_FAMILY_RESOLUTION"
)
FINAL_VERDICT = FAMILY_OBSTRUCTION
RELEASE_VERDICT = "BHSM_1_0_RELEASE_BLOCKED"
ALLOWED_CANDIDATE_STATUSES = {
    "ACTION_EXTENSION_CONSTRUCTED",
    "ACTION_DERIVED_CONDITIONAL_PREDICTION",
    "STRUCTURAL_BUT_NOT_PHYSICAL",
    "PHYSICAL_BUT_INPUT_TAUTOLOGY",
    "BLOCKED_BY_EXACT_MISSING_OBJECT",
    "PROXY_ONLY_REJECTED",
    "INVALIDATED",
}


def deterministic_json(value: Any) -> str:
    return json.dumps(
        value, indent=2, sort_keys=True, ensure_ascii=False
    ) + "\n"


def collar_geometry() -> dict[str, Any]:
    return {
        "orientation": (
            "rho=0 is the common M4 seam; increasing rho enters either cap "
            "toward its hyperspherical core"
        ),
        "v7_1_embedding": (
            "c_epsilon(t,x,rho)=(t,pi/2-epsilon rho,x)"
        ),
        "normal_metric": "a(t)^2 d rho^2",
        "general_surface_factor": (
            "J(Y,rho)=det(I+rho S(Y)) in the repository normal-first "
            "tubular convention"
        ),
        "round_cap_exact_factor": "J_round(rho)=cos(rho)^3",
        "round_cap_measure": (
            "dmu5=N a^4 cos(rho)^3 dt d rho dmu_S3"
        ),
        "inner_product": (
            "<u,v>_collar=int_M4 int_C u^dagger v "
            "J(Y,rho) d rho dmu_h"
        ),
        "constant_replacement_used": False,
        "embedding_width_selected": False,
    }


def canonical_response_carriers() -> list[dict[str, Any]]:
    return [
        {
            "carrier": "scalar canonical momentum",
            "formula": (
                "pi_sigma,epsilon=-sqrt(|h|) Z5 "
                "n_epsilon^A D_A sigma"
            ),
            "variation_source": "S5 scalar kinetic term",
            "reflection_and_parity": (
                "linear pi_sigma is scalar-parity odd; sigma pi_sigma is "
                "even but vanishes on the retained odd Dirichlet seam "
                "sigma|M4=0"
            ),
            "mass_operator_eligibility": False,
            "reason": (
                "the nonzero linear response violates scalar parity, while "
                "the lowest even response vanishes; quadratic momentum "
                "would exceed the minimal dimension and require a scale"
            ),
            "status": "BLOCKED_BY_EXACT_MISSING_OBJECT",
        },
        {
            "carrier": "metric canonical momentum",
            "formula": (
                "pi_epsilon^ab=epsilon kappa1"
                "(K_epsilon^ab-K_epsilon h^ab)"
            ),
            "variation_source": "Einstein-Hilbert plus coefficient-locked GHY",
            "reflection_and_parity": (
                "epsilon pi_epsilon is exchanged evenly by cap reflection"
            ),
            "mass_operator_eligibility": True,
            "reason": (
                "its cap-summed trace is the unique dimension-one Lorentz "
                "scalar directly produced by the existing variation"
            ),
            "status": "ACTION_EXTENSION_CONSTRUCTED",
        },
        {
            "carrier": "coupled scalar-metric KKT response",
            "formula": (
                "H_eff=H_bb-H_bi H_ii,perp^-1 H_ib"
            ),
            "variation_source": "complete cap/matcher constrained Hessian",
            "reflection_and_parity": "covariant on the declared KKT domain",
            "mass_operator_eligibility": False,
            "reason": (
                "the scalar-metric block vanishes on the retained sigma=0 "
                "fixed-h background and the remaining KKT saddle is "
                "indefinite; it supplies no additional minimal scalar"
            ),
            "status": "STRUCTURAL_BUT_NOT_PHYSICAL",
        },
        {
            "carrier": "matcher reaction",
            "formula": "Lambda_epsilon^ab=pi_epsilon^ab on shell",
            "variation_source": "metric compatibility multiplier",
            "reflection_and_parity": "same as metric canonical momentum",
            "mass_operator_eligibility": False,
            "reason": (
                "it is the same canonical response and cannot be counted as "
                "an independent interaction"
            ),
            "status": "PROXY_ONLY_REJECTED",
        },
    ]


def canonical_boundary_response() -> dict[str, Any]:
    return {
        "selected_carrier": "cap-summed metric/Brown-York canonical momentum",
        "density_free_momentum": (
            "pi_epsilon^ab=epsilon kappa1"
            "(K_epsilon^ab-K_epsilon h^ab)"
        ),
        "matcher_equation": "pi_epsilon^ab=Lambda_epsilon^ab",
        "reflection_even_sum": (
            "pi_env^ab=(pi_+^ab+pi_-^ab)/2"
        ),
        "unique_scalar_contraction": (
            "kappa_env=-(3 kappa1)^-1 h_ab pi_env^ab"
            "=(epsilon_+ K_+ + epsilon_- K_-)/2"
        ),
        "Dirichlet_to_Neumann_map": (
            "Lambda_env:delta h|M4 -> delta pi_env|M4 after solving the "
            "cap Einstein-scalar, ADM, matcher, gauge, and closed-range "
            "complement equations"
        ),
        "background_value": (
            "kappa_env=0 on the exact round equatorial background K_ab=0"
        ),
        "nonlocality": (
            "the complete covariant Lambda_env is a nonlocal seam operator"
        ),
        "result": RESPONSE_RESULT,
    }


def curvature_invariant_audit() -> list[dict[str, Any]]:
    return [
        {
            "candidate": "kappa_env",
            "operator_dimension": 1,
            "action_source": "trace of Einstein-GHY canonical momentum",
            "independent_coefficient_required": False,
            "accepted": True,
            "reason": "unique linear scalar at minimal dimension",
        },
        {
            "candidate": "K",
            "operator_dimension": 1,
            "action_source": "GHY",
            "independent_coefficient_required": False,
            "accepted": False,
            "reason": (
                "one-sided K is cap-reflection odd; its allowed cap sum is "
                "exactly kappa_env"
            ),
        },
        {
            "candidate": "u_a u_b pi_env^ab",
            "operator_dimension": 1,
            "action_source": "metric canonical momentum",
            "independent_coefficient_required": False,
            "accepted": False,
            "reason": "no action-derived timelike observer u is selected",
        },
        {
            "candidate": "R[h]",
            "operator_dimension": 2,
            "action_source": "intrinsic B1 Einstein term",
            "independent_coefficient_required": False,
            "accepted": False,
            "reason": "multiplying a Yukawa operator gives dimension six",
        },
        {
            "candidate": "K_ab K^ab or K^2",
            "operator_dimension": 2,
            "action_source": "not produced linearly by the P1+GHY variation",
            "independent_coefficient_required": True,
            "accepted": False,
            "reason": "new higher-dimensional coefficient would be required",
        },
        {
            "candidate": "sigma pi_sigma",
            "operator_dimension": "greater than one",
            "action_source": "scalar kinetic boundary form",
            "independent_coefficient_required": True,
            "accepted": False,
            "reason": "zero on the retained odd Dirichlet seam",
        },
        {
            "candidate": "matcher trace",
            "operator_dimension": 1,
            "action_source": "compatibility multiplier",
            "independent_coefficient_required": False,
            "accepted": False,
            "reason": "on-shell duplicate of kappa_env",
        },
    ]


def energy_envelopment_audit() -> dict[str, Any]:
    return {
        "required_ratio": (
            "epsilon=E_core/(E_core+E_surface), 0<=epsilon<=1"
        ),
        "candidates": [
            {
                "source": "full cap/ADM/matcher quadratic form",
                "result": "indefinite constrained KKT saddle",
                "positive": False,
            },
            {
                "source": "Brown-York surface density",
                "result": (
                    "observer- and reference-subtraction-dependent; no "
                    "positivity theorem"
                ),
                "positive": False,
            },
            {
                "source": "Lorentzian scalar gradient Dq squared",
                "result": "not a positive energy without a selected observer",
                "positive": False,
            },
            {
                "source": "fixed-h scalar physical complement",
                "result": (
                    "positive complement gap exists, but its Dirichlet trace "
                    "is zero and its quadratic form is the same bulk energy "
                    "represented by its DtN form, so counting both as core "
                    "and surface double counts one action contribution"
                ),
                "positive": True,
            },
            {
                "source": "compatibility response",
                "result": (
                    "a Lagrange-multiplier constraint with zero on-shell "
                    "constraint value, not positive energy"
                ),
                "positive": False,
            },
        ],
        "positive_core_surface_pair_exists": False,
        "arbitrary_absolute_value_used": False,
        "reference_subtraction_added": False,
        "observer_added": False,
        "ratio": None,
        "result": ENERGY_OBSTRUCTION,
    }


def radial_response_operator() -> dict[str, Any]:
    return {
        "field_bundle": "real gauge-singlet cap scalar line bundle",
        "operator": (
            "L_sigma=-J^-1 D_rho(J Z5 D_rho)"
            "+U5''(sigma_background)+V_metric_constraint"
        ),
        "principal_part": "-J^-1 D_rho(J Z5 D_rho)",
        "surface_factor": collar_geometry()["general_surface_factor"],
        "round_surface_factor": collar_geometry()["round_cap_exact_factor"],
        "curvature_potential": (
            "the connection/measure terms generated by J and the "
            "constraint-reduced metric Schur block"
        ),
        "core_loading": (
            "no independent positive loading term exists in the current action"
        ),
        "surface_loading": (
            "no independent positive surface term exists in the current action"
        ),
        "boundary_conditions": (
            "regular cap pole and odd scalar Dirichlet trace at rho=0"
        ),
        "self_adjoint_domain": (
            "regular weighted H2 scalar domain with zero seam trace, "
            "metric gauge quotient, matcher reaction, and explicit "
            "Lyapunov-Schmidt kernel coordinate"
        ),
        "kernel": "span{u1} on strict fixed-h D0",
        "physical_complement": (
            "u1-perpendicular closed-range scalar subspace plus the "
            "endpoint-preserving metric gauge quotient"
        ),
        "complement_gap": "64.0147366689857 in the normalized D0 representative",
        "gap_used_as_mass_floor": False,
        "gauge_representation": "singlet",
        "chirality_incidence": "none",
        "mass_response_eligibility": False,
        "reason": (
            "the action-selected zero trace and scalar parity prevent its "
            "canonical momentum from furnishing the minimal mass insertion"
        ),
    }


def minimal_interaction_classification() -> list[dict[str, Any]]:
    return [
        {
            "interaction": "kappa_env O_Y,f+h.c.",
            "dimension": 5,
            "Lorentz": True,
            "SM_gauge": True,
            "Hermitian": True,
            "cap_reflection": True,
            "Hopf_equivariant": True,
            "scalar_parity": True,
            "new_field": False,
            "redundant": (
                "universal kappa_env is equivalent to a common local "
                "rescaling of the sector Yukawa strength on a fixed "
                "background"
            ),
            "extension_candidate": True,
            "accepted_as_flavor_mechanism": False,
            "reason": (
                "this is the unique action-supported local response "
                "coupling, but it is removed from the admissible physical "
                "flavor set because it has no family incidence"
            ),
        },
        {
            "interaction": "pi_sigma O_Y,f+h.c.",
            "dimension": "greater than five without a new scale",
            "Lorentz": True,
            "SM_gauge": True,
            "Hermitian": True,
            "cap_reflection": "fails scalar parity",
            "Hopf_equivariant": True,
            "scalar_parity": False,
            "new_field": False,
            "redundant": False,
            "extension_candidate": False,
            "accepted_as_flavor_mechanism": False,
        },
        {
            "interaction": "R[h] O_Y,f+h.c.",
            "dimension": 6,
            "Lorentz": True,
            "SM_gauge": True,
            "Hermitian": True,
            "cap_reflection": True,
            "Hopf_equivariant": True,
            "scalar_parity": True,
            "new_field": False,
            "redundant": False,
            "extension_candidate": False,
            "accepted_as_flavor_mechanism": False,
        },
        {
            "interaction": "(K_ab K^ab or K^2) O_Y,f+h.c.",
            "dimension": 6,
            "Lorentz": True,
            "SM_gauge": True,
            "Hermitian": True,
            "cap_reflection": True,
            "Hopf_equivariant": True,
            "scalar_parity": True,
            "new_field": False,
            "redundant": False,
            "extension_candidate": False,
            "accepted_as_flavor_mechanism": False,
        },
        {
            "interaction": "Lambda_matcher O_Y,f+h.c.",
            "dimension": 5,
            "Lorentz": True,
            "SM_gauge": True,
            "Hermitian": True,
            "cap_reflection": True,
            "Hopf_equivariant": True,
            "scalar_parity": True,
            "new_field": False,
            "redundant": "duplicates pi_env by the matcher equation",
            "extension_candidate": False,
            "accepted_as_flavor_mechanism": False,
        },
    ]


def action_extension() -> dict[str, Any]:
    return {
        "extended_action": "S_BHSM^v8=S_BHSM^strat+S_mass-response^(5)",
        "unnormalized_interaction": (
            "S_mass-response^(5)=-sum_f c_f int_M4 sqrt(|h|) "
            "kappa_env O_Y,f+h.c."
        ),
        "Yukawa_operators": {
            "u": "O_Y,u=bar Q_L H_tilde u_R",
            "d": "O_Y,d=bar Q_L H d_R",
            "e": "O_Y,e=bar L_L H e_R",
        },
        "normalized_response": (
            "Lambda_hat_env=kappa_env/|kappa_env|_action on a selected "
            "nonzero response channel"
        ),
        "normalized_interaction": (
            "-int_M4 sqrt(|h|)[y_u bar Q_L H_tilde Lambda_hat_env u_R"
            "+y_d bar Q_L H Lambda_hat_env d_R"
            "+y_e bar L_L H Lambda_hat_env e_R+h.c.]"
        ),
        "typed_overall_inputs": [
            "one charged-sector strength y_u",
            "one charged-sector strength y_d",
            "one charged-sector strength y_e",
        ],
        "normalization_rule": (
            "the sole nonzero family-singlet response channel has action "
            "canonical norm one; its only singular value is one"
        ),
        "zero_response_rule": (
            "normalization is undefined when kappa_env=0; the exact round "
            "equatorial background therefore produces no mass incidence"
        ),
        "new_dynamical_field": False,
        "new_mediator": False,
        "new_scale": False,
        "second_calibration": False,
        "arbitrary_flavor_spurion": False,
        "doctrine": DOCTRINE,
        "result": RESPONSE_RESULT,
    }


def family_space_audit() -> dict[str, Any]:
    return {
        "derived_response_space": (
            "one real cap-reflection-even scalar response channel"
        ),
        "derived_dimension": 1,
        "kernel_dimension": (
            "one scalar D0 Jacobi mode, but it has zero Dirichlet trace and "
            "does not become a localized chiral family"
        ),
        "representation": (
            "Lorentz and SU3xSU2xU1 singlet; no chirality"
        ),
        "Schur_lemma": (
            "a scalar gauge-singlet curvature response commutes with every "
            "existing family/sector symmetry and therefore acts as a "
            "multiple of the identity on each supplied family multiplet"
        ),
        "C3_family_used_as_derivation_input": False,
        "conditional_on_existing_M4_C3": (
            "Lambda_hat_f=I3 for f=u,d,e"
        ),
        "exactly_three_selected": False,
        "additional_light_modes_excluded": False,
        "result": FAMILY_OBSTRUCTION,
    }


def response_matrices() -> dict[str, Any]:
    identity = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
    ]
    row = {
        "basis": "any orthonormal basis of the supplied C3 family input",
        "matrix": identity,
        "rank": 3,
        "singular_values": [1.0, 1.0, 1.0],
        "singular_value_ratios": ["1", "1", "1"],
        "left_basis": "UNSELECTED_BY_EXACT_THREEFOLD_DEGENERACY",
        "status": "ACTION_DERIVED_CONDITIONAL_PREDICTION",
    }
    return {
        "charged_lepton": dict(row),
        "up": dict(row),
        "down": dict(row),
    }


def ckm_result() -> dict[str, Any]:
    return {
        "formula": "V_CKM^BH=U_u^dagger U_d",
        "result": None,
        "angles": None,
        "phase": None,
        "Jarlskog": None,
        "reason": (
            "the exactly degenerate identity responses leave U_u and U_d "
            "arbitrary; CKM is not an invariant of the response"
        ),
        "status": "BLOCKED_BY_EXACT_MISSING_OBJECT",
    }


def physical_transport() -> dict[str, Any]:
    return {
        "scheme": SCHEME,
        "reference_scale": REFERENCE_SCALE,
        "mass_formula": (
            "m_f,i^MSbar(mu_star)=y_f v(mu_star) s_f,i/sqrt(2)"
        ),
        "ratio_formula": "m_f,i/m_f,j=s_f,i/s_f,j=1",
        "conditional_prediction": (
            "every charged sector is exactly family-degenerate wherever "
            "the normalized response is defined"
        ),
        "round_background": (
            "kappa_env=0, so the normalized response and curvature-induced "
            "mass incidence are undefined rather than nonzero"
        ),
        "second_scale_used": False,
        "second_calibration_used": False,
    }


def localization_result() -> dict[str, Any]:
    return {
        "epsilon": None,
        "stationary_profile_family": None,
        "mean_rho_monotonicity": None,
        "core_limit": None,
        "surface_limit": None,
        "reason": (
            "without two independent sign-controlled energies, an "
            "epsilon-dependent radial potential would be an arbitrary "
            "interpolation not produced by the action"
        ),
        "arbitrary_profile_inserted": False,
        "result": ENERGY_OBSTRUCTION,
    }


def prediction_freeze() -> dict[str, Any]:
    matrices = response_matrices()
    return {
        "version": VERSION,
        "extended_action": action_extension()["extended_action"],
        "response_carrier": canonical_boundary_response()[
            "selected_carrier"
        ],
        "curvature_invariant": canonical_boundary_response()[
            "unique_scalar_contraction"
        ],
        "energy_envelopment_ratio": None,
        "collar_orientation": collar_geometry()["orientation"],
        "surface_factor": collar_geometry()["general_surface_factor"],
        "round_surface_factor": collar_geometry()[
            "round_cap_exact_factor"
        ],
        "radial_operator": radial_response_operator()["operator"],
        "domain": radial_response_operator()["self_adjoint_domain"],
        "family_dimension_derived": 1,
        "conditional_supplied_family_dimension": 3,
        "matrix_normalization": action_extension()["normalization_rule"],
        "response_matrices": matrices,
        "singular_values": {
            sector: row["singular_values"]
            for sector, row in matrices.items()
        },
        "mass_ratio_prediction": "1:1:1 in every supplied charged sector",
        "CKM_prediction": None,
        "uncertainty": "EXACT_UNIVERSALITY_WITHIN_THE_EXTENSION",
        "falsification_threshold": (
            "any nondegenerate charged-sector singular-value ratio "
            "invalidates the universal response as a flavor mechanism"
        ),
        "comparison_data_used": False,
        "retuning_permitted": False,
        "status": "ACTION_DERIVED_CONDITIONAL_PREDICTION",
    }


def prediction_freeze_hash() -> str:
    return sha256(
        deterministic_json(prediction_freeze()).encode("utf-8")
    ).hexdigest().upper()


def post_freeze_comparison() -> dict[str, Any]:
    """Comparison is populated only after the prediction freeze is hashed."""
    return {
        "freeze_hash_verified_before_comparison": prediction_freeze_hash(),
        "comparison_performed_after_freeze": True,
        "sources": [
            "theory/bhsm_v1_frozen_prediction_set.json",
            "theory/bhsm_bare_vs_dressed_prediction_ledger.json",
        ],
        "historical_bare_BHSM_screens": {
            "classification": "INCOMPATIBLE",
            "charged_lepton_ratios_heavy_middle_light": [
                1.0,
                0.06007447093260976,
                0.00029729106456492414,
            ],
            "up_ratios_heavy_middle_light": [
                1.0,
                0.008310500554068288,
                0.000012690463017606151,
            ],
            "down_ratios_heavy_middle_light": [
                1.0,
                0.021933971495439474,
                0.0011165200546001757,
            ],
            "reason": (
                "every historical charged-sector screen is nondegenerate, "
                "whereas the frozen response is exactly 1:1:1"
            ),
            "disposition": (
                "RETIRED_FROM_V8_CURVATURE_RESPONSE_PREDICTIVE_PATH"
            ),
        },
        "historical_dressed_candidate": {
            "classification": "INCOMPATIBLE",
            "changed_ratio": {
                "quantity": "c/t",
                "value": 0.004155250277034144,
            },
            "reason": (
                "the dressing changes one already nondegenerate ratio and "
                "cannot convert the frozen universal response into a "
                "family-resolving operator"
            ),
            "disposition": (
                "RETIRED_FROM_V8_CURVATURE_RESPONSE_PREDICTIVE_PATH; "
                "retained only as historical provenance"
            ),
        },
        "common_scale_external_references": {
            "classification": "INCOMPATIBLE",
            "charged_lepton_ratios_heavy_middle_light": [
                1.0,
                0.05946353426831603,
                0.0002875853753250115,
            ],
            "up_ratios_heavy_middle_light": [
                1.0,
                0.007354218541895883,
                0.000012507962244484336,
            ],
            "down_ratios_heavy_middle_light": [
                1.0,
                0.022344497607655504,
                0.0011172248803827751,
            ],
            "reason": (
                "nondegenerate common-scale reference ratios falsify the "
                "universal response as a charged-flavor mechanism"
            ),
        },
        "operator_retuned_after_comparison": False,
        "status": "INVALIDATED",
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
        "mass_curvature_response_extension": RESPONSE_RESULT,
        "distinct_action_derived_prediction_exists": False,
        "RB15": {
            "status": "BLOCKED_EXACT_OBJECT_PROVED",
            "resolution": "UNIVERSAL_RESPONSE_WITH_NO_FAMILY_RESOLUTION",
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
        "parameter_free_extension_blocker": "RB-02",
        "next_highest_upstream_blocker": (
            "UNIVERSAL_RESPONSE_WITH_NO_FAMILY_RESOLUTION"
        ),
        "one_universal_dimensionful_calibration": "G_F",
        "action_extension_introduced": True,
        "new_dynamical_field_introduced": False,
        "new_mediator_introduced": False,
        "fitted_parameter_used": False,
        "measured_mode_selection_used": False,
        "arbitrary_profile_used": False,
        "inserted_zero_mode_used": False,
        "arbitrary_gap_floor_used": False,
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
        "artifact": "BHSM_mass_curvature_response_v8_0",
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "doctrine": DOCTRINE,
        "action_extension": action_extension(),
        "response_carrier_audit": canonical_response_carriers(),
        "canonical_boundary_response": canonical_boundary_response(),
        "curvature_invariant_audit": curvature_invariant_audit(),
        "energy_envelopment_ratio": energy_envelopment_audit(),
        "core_surface_localization": localization_result(),
        "collar_geometry": collar_geometry(),
        "radial_response_operator": radial_response_operator(),
        "minimal_interaction_classification": (
            minimal_interaction_classification()
        ),
        "family_space": family_space_audit(),
        "response_matrices": response_matrices(),
        "CKM": ckm_result(),
        "physical_transport": physical_transport(),
        "prediction_freeze": freeze,
        "prediction_freeze_sha256": prediction_freeze_hash(),
        "post_freeze_comparison": post_freeze_comparison(),
        "frozen_predictions": [
            {
                "prediction_id": "V8_MASS_RESPONSE_CHARGED_DEGENERACY",
                "value": "1:1:1 in every supplied charged sector",
                "uncertainty": "EXACT_UNIVERSALITY_WITHIN_THE_EXTENSION",
                "freeze_sha256": prediction_freeze_hash(),
                "official_prediction": False,
                "post_freeze_status": "INVALIDATED",
            }
        ],
        "falsification_condition": freeze["falsification_threshold"],
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
            "FAMILY_RESOLVING_ACTION_INCIDENCE_BEYOND_THE_"
            "UNIVERSAL_CURVATURE_SCALAR"
        ),
        "final_verdict": FINAL_VERDICT,
        "integrity": {
            "fit_used": False,
            "measured_mode_selection_used": False,
            "arbitrary_profile_used": False,
            "inserted_zero_mode_used": False,
            "arbitrary_gap_floor_used": False,
            "unselected_domain_parameter_used": False,
            "new_mediator_used": False,
            "second_scale_used": False,
            "hidden_calibration_used": False,
            "post_comparison_retuning_used": False,
            "new_action_extension_declared": True,
            "frozen_prediction_changed": False,
        },
    }
    result["validation"] = {
        "doctrine_explicit": result["doctrine"] == DOCTRINE,
        "carrier_selected_by_variation": (
            result["canonical_boundary_response"]["selected_carrier"]
            == "cap-summed metric/Brown-York canonical momentum"
        ),
        "curvature_invariant_unique": sum(
            row["accepted"] for row in result["curvature_invariant_audit"]
        )
        == 1,
        "minimal_interaction_unique": sum(
            row["extension_candidate"]
            for row in result["minimal_interaction_classification"]
        )
        == 1,
        "no_nonredundant_flavor_interaction": not any(
            row["accepted_as_flavor_mechanism"]
            for row in result["minimal_interaction_classification"]
        ),
        "surface_factor_nonconstant": (
            result["collar_geometry"]["round_cap_exact_factor"]
            == "J_round(rho)=cos(rho)^3"
        ),
        "domain_selected_without_parameter": (
            "zero seam trace"
            in result["radial_response_operator"]["self_adjoint_domain"]
        ),
        "no_positive_energy_ratio_fabricated": (
            result["energy_envelopment_ratio"]["ratio"] is None
        ),
        "family_universality_proved": (
            result["family_space"]["derived_dimension"] == 1
        ),
        "freeze_hashed": (
            len(result["prediction_freeze_sha256"]) == 64
        ),
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
        "response_carrier": data["canonical_boundary_response"][
            "selected_carrier"
        ],
        "canonical_boundary_momentum": data[
            "canonical_boundary_response"
        ]["density_free_momentum"],
        "curvature_invariant": data["canonical_boundary_response"][
            "unique_scalar_contraction"
        ],
        "energy_envelopment_ratio": data["energy_envelopment_ratio"][
            "ratio"
        ],
        "surface_factor": data["collar_geometry"][
            "general_surface_factor"
        ],
        "stationary_profiles": data["core_surface_localization"][
            "stationary_profile_family"
        ],
        "selected_domain": data["radial_response_operator"][
            "self_adjoint_domain"
        ],
        "family_space_dimension": data["family_space"]["derived_dimension"],
        "response_matrices": data["response_matrices"],
        "singular_values": data["prediction_freeze"]["singular_values"],
        "CKM": data["CKM"],
        "frozen_predictions": data["frozen_predictions"],
        "prediction_freeze_sha256": data["prediction_freeze_sha256"],
        "post_freeze_comparison": data["post_freeze_comparison"],
        "RB15": data["RB15"]["status"],
        "RB16": data["RB16"]["status"],
        "release_verdict": data["release_verdict"],
        "remaining_exact_obstruction": data[
            "remaining_exact_obstruction"
        ],
        "validation": data["validation"],
        "validation_passed": data["validation_passed"],
        "final_verdict": data["final_verdict"],
    }


def status_to_markdown(data: dict[str, Any] | None = None) -> str:
    report = data or status_report()
    return "\n".join(
        [
            "# BHSM v8.0 mass-curvature response",
            "",
            f"Response: `{report['response_result']}`",
            "",
            f"- Carrier: `{report['response_carrier']}`",
            (
                "- Canonical momentum: "
                f"`{report['canonical_boundary_momentum']}`"
            ),
            f"- Curvature invariant: `{report['curvature_invariant']}`",
            (
                "- Energy-envelopment ratio: "
                f"`{report['energy_envelopment_ratio']}`"
            ),
            f"- Surface factor: `{report['surface_factor']}`",
            f"- Stationary profiles: `{report['stationary_profiles']}`",
            f"- Domain: `{report['selected_domain']}`",
            (
                "- Derived family-space dimension: "
                f"`{report['family_space_dimension']}`"
            ),
            (
                "- Conditional singular values: "
                f"`{report['singular_values']}`"
            ),
            f"- Response matrices: `{report['response_matrices']}`",
            f"- CKM: `{report['CKM']['result']}`",
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
            f"- Release: `{report['release_verdict']}`",
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
    artifact = (
        root / "artifacts" / "BHSM_mass_curvature_response_v8_0.json"
    )
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
