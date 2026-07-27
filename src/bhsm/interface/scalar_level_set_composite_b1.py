"""BHSM v6.14.0 scalar-level-set and blow-up composite-B1 theorem."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import sympy as sp


VERSION = "v6.14.0"
SPRINT = "bhsm-scalar-level-set-composite-b1-blowup-v6-14-0"
SOURCE_MAIN_SHA = "b5e926245ba49510e84b03060ec17a1170f9f3ee"
V613_HEAD_SHA = "50ddd8bfb22931d8d914de620ae112ac2a746da3"

PRIMARY_RESULT = "BHSM_COMPOSITE_B1_SUPPORT_LEAVES_ENDPOINT_THREADING_OPEN"
DIRECT_RESULT = "BHSM_DIRECT_SCALAR_LEVEL_SET_IS_SINGULAR_AT_THE_FOLD"
CHART_RESULT = "BHSM_B1_LEVEL_SET_IS_ONLY_A_CENTER_MANIFOLD_CHART"
DOMAIN_RESULT = "BHSM_PROJECTIVE_SCALAR_SUPPORT_REQUIRES_AN_ADDITIONAL_DOMAIN_AXIOM"

CHI_1_DECIMAL = "5.268307871542"
NU_1_DECIMAL = "109.666681740423"
U1_JUNCTION_DERIVATIVE_DECIMAL = "-9.124976903426"
U1_CAP_DECIMAL = "8.923902707116"
MU_C_DECIMAL = "29.430918352947"

ARTIFACT_FILES = {
    "geometry": "BHSM_scalar_wall_level_set_and_blowup_geometry_v6_14_0.json",
    "variation": "BHSM_composite_B1_variation_and_threading_domain_v6_14_0.json",
    "verdict": "BHSM_v6_14_0_scalar_level_set_composite_B1_verdict.json",
}

GUARDS = {
    "composite_support_adopted": False,
    "sigma_identified_with_sigma_partial": False,
    "sigma_hat_promoted_to_field": False,
    "fixed_and_composite_Dirichlet_double_imposed": False,
    "arbitrary_threading_condition_added": False,
    "pseudoinverse_constructed": False,
    "Green_operator_constructed": False,
    "new_action_term_introduced": False,
    "new_action_coefficient_introduced": False,
    "new_primitive_introduced": False,
    "boundary_tension_introduced": False,
    "tau_J_introduced": False,
    "radion_potential_introduced": False,
    "measured_input_used": False,
    "neutral_work_performed": False,
    "physical_bulk_Dirac_law_introduced": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
}

Q, ALPHA, BETA = sp.symbols("q alpha beta", real=True)
S, TAU = sp.symbols("s tau", real=True, nonzero=True)
U1, U2 = sp.symbols("u_1 u_2_tau", real=True)
U1_PRIME = sp.symbols("u_1_prime", real=True, nonzero=True)
DELTA_Q = sp.symbols("delta_q", real=True)
DELTA_F, NORMAL_F = sp.symbols("delta_f normal_f", real=True)
B_SHIFT, N0, ZETA, A0, E_RHO = sp.symbols(
    "B N_0 zeta a_0 E_rho", real=True
)
DELTA_HAT, NORMAL_HAT = sp.symbols(
    "delta_sigma_hat normal_sigma_hat", real=True
)
CHI_1 = sp.symbols("chi_1", real=True, positive=True)


def amplitude_squared_series() -> sp.Expr:
    """Stored per-cap scalar norm through the first unknown correction."""
    return sp.expand(Q**2 * (1 + 2 * ALPHA * Q + BETA * Q**2))


def amplitude_series() -> sp.Expr:
    """Positive square root Q[sigma]=q+alpha q^2+O(q^3)."""
    return Q + ALPHA * Q**2


def blowup_profile_series() -> sp.Expr:
    """sigma/Q[sigma] on one fixed scalar-sign and sheet branch."""
    return sp.expand(S * (U1 + Q * (U2 - ALPHA * U1)))


def direct_normal_derivative_series() -> sp.Expr:
    return sp.expand(S * (Q * U1_PRIME + Q**2 * sp.Symbol("u_2_prime")))


def composite_displacement(
    delta_f: sp.Expr = DELTA_F, normal_f: sp.Expr = NORMAL_F
) -> sp.Expr:
    return sp.simplify(-delta_f / normal_f)


def endpoint_slope(tau: int) -> sp.Expr:
    if tau not in (-1, 1):
        raise ValueError("tau must be +/-1")
    return sp.simplify(-tau * CHI_1 / 4)


def blowup_endpoint_q_derivative(tau: int, scalar_sign: int) -> sp.Expr:
    """Derivative forced by sigma_hat(q,rho_J(q))=0."""
    if tau not in (-1, 1) or scalar_sign not in (-1, 1):
        raise ValueError("tau and scalar_sign must be +/-1")
    return sp.simplify(
        -scalar_sign * U1_PRIME * endpoint_slope(tau)
    )


def recovered_endpoint_displacement(
    tau: int, scalar_sign: int
) -> sp.Expr:
    derivative = blowup_endpoint_q_derivative(tau, scalar_sign)
    normal = scalar_sign * U1_PRIME
    return sp.simplify(composite_displacement(derivative * DELTA_Q, normal))


def endpoint_threading_invariant(
    zeta: sp.Expr = ZETA,
) -> sp.Expr:
    return sp.expand(B_SHIFT + N0**2 * zeta - A0**2 * E_RHO)


def composite_threading_invariant() -> sp.Expr:
    zeta = composite_displacement(DELTA_HAT, NORMAL_HAT)
    return endpoint_threading_invariant(zeta)


def direct_level_set_ledger() -> dict[str, Any]:
    return {
        "branch_expansion": (
            "sigma_tau,s=s[q u1+q^2 u2_tau+O(q^3)]"
        ),
        "normal_derivative": (
            "partial_rho sigma|Sigma=s[q u1'(rho_J)+O(q^2)]"
        ),
        "u1_junction_value": 0,
        "u1_junction_derivative": U1_JUNCTION_DERIVATIVE_DECIMAL,
        "q_positive_regular_value": True,
        "regularity_scope": "all sufficiently small q>0 on either Puiseux sheet",
        "regularity_reason": (
            "u1'(rho_J) is nonzero, so the O(q) term dominates the O(q^2) "
            "profile correction"
        ),
        "junction_zero_locally_unique": True,
        "uniqueness_reason": "implicit-function theorem at the simple junction zero",
        "additional_cap_zeros": False,
        "additional_zero_reason": (
            "u1 is the lowest regular-pole/Dirichlet Sturm-Liouville mode and "
            "has no interior nodes; small branch corrections preserve this"
        ),
        "scalar_sign_independence": (
            "multiplication by s=+/-1 reverses orientation but not the zero set"
        ),
        "sheet_dependence": (
            "tau changes u2_tau and rho_J'(0)=-tau chi_1/4, not regularity"
        ),
        "Z2_caps": (
            "odd continuation reverses sigma across the two caps while retaining "
            "their common sigma=0 junction"
        ),
        "critical_sigma": "sigma_0(rho)=0 for every rho",
        "critical_gradient": 0,
        "critical_zero_set": "the entire cap, not a hypersurface",
        "q_zero_regular_value": False,
        "result": DIRECT_RESULT,
    }


def amplitude_and_blowup_ledger() -> dict[str, Any]:
    return {
        "proper_normal_measure": (
            "Q[sigma]^2=integral_0^rhoJ a^4 sigma^2 d rho"
        ),
        "fixed_domain_measure": (
            "Q[sigma]^2=integral_0^1 N a^4 sigma^2 dt"
        ),
        "cap_multiplicity": (
            "per-cap normalization; a two-cap norm differs by a fixed sqrt(2) "
            "and leaves the projective zero set unchanged"
        ),
        "stored_normalization": "integral_0^rhoJ a0^4 u1^2 d rho=1",
        "series": "Q[sigma]^2=q^2[1+2 alpha_tau q+O(q^2)]",
        "positive_root": "Q[sigma]=q+alpha_tau q^2+O(q^3)",
        "local_inverse": "q=Q-alpha_tau Q^2+O(Q^3)",
        "definition": "sigma_hat=sigma/Q[sigma] for Q>0",
        "limit": "sigma_hat -> s u1 along a fixed (tau,s) center-manifold branch",
        "critical_support": "Sigma_0={u1=0}={rho_J}",
        "critical_regular": True,
        "critical_witness": "u1'(rho_J)=-9.124976903426... !=0",
        "scalar_sign_support": "independent",
        "tau_support": (
            "same limiting support; tau enters the first q correction and "
            "rho_J'(0)"
        ),
        "radial_gauge_covariance": (
            "Q is an invariant scalar integral and sigma_hat is a scalar; "
            "its zero set is carried covariantly"
        ),
        "M4_diffeomorphism_covariance": (
            "Q is an M4 scalar collective norm and the zero set pulls back "
            "under tangential reparameterizations"
        ),
        "normalization_dependence": (
            "positive constant rescaling changes sigma_hat but not its zero set; "
            "Q=q+O(q^2) uses the stored unit norm"
        ),
        "cap_dependence": (
            "Z2-related caps reverse scalar/normal orientation but share support"
        ),
        "field_status": "nonlocal collective-coordinate chart, not a new field",
        "center_manifold_status": (
            "coefficient-free chart on the selected one-dimensional fold center "
            "manifold after the stored normalization"
        ),
        "off_center_status": (
            "undefined at sigma=0 without an approach direction; different "
            "orthogonal perturbations select different projective profiles and zeros"
        ),
        "valid_perturbation_space": "the one-dimensional fold mode only",
        "result": CHART_RESULT,
    }


def provenance_ledger() -> list[dict[str, str]]:
    return [
        {
            "ingredient": "regular-level-set normal, pullback, and shape formulas",
            "source": "PO-BH-58 and PO-BH-59",
            "status": "Adopted from established physics/mathematics",
            "scope": "conditional standard geometry; no old BHSM profile theorem",
        },
        {
            "ingredient": "normal displacement and surface shape variation",
            "source": "v5.11-v5.12 geometric Hessian/source ledgers",
            "status": "Adopted from established physics/mathematics",
            "scope": "formulas retained; old symbolic surface coefficients rejected here",
        },
        {
            "ingredient": "fixed-iota intrinsic B1 with exact metric matching",
            "source": "v6.1.3",
            "status": "Adopted BHSM axiom",
            "scope": "provisional boundary ontology, not parent-derived",
        },
        {
            "ingredient": "curved odd scalar and lowest Dirichlet mode",
            "source": "v6.1.5-v6.1.6",
            "status": "Numerically validated",
            "scope": "bulk sigma; not intrinsic sigma_partial",
        },
        {
            "ingredient": "two nonlinear Puiseux sheets and moving endpoint",
            "source": "v6.1.7",
            "status": "Derived consequence",
            "scope": "conditional frozen representative with numerical continuation",
        },
        {
            "ingredient": "direct sigma level-set degeneracy at q=0",
            "source": "v6.1.7 expansion evaluated at the fold",
            "status": "Rejected by calculation",
            "scope": "sigma_0=0 and grad sigma_0=0",
        },
        {
            "ingredient": "missing gauge-invariant endpoint threading domain",
            "source": "v6.12-v6.13",
            "status": "Active construction target",
            "scope": "preserved obstruction",
        },
        {
            "ingredient": "iota=iota[sigma_hat]",
            "source": "v6.14 test",
            "status": "BHSM identification",
            "scope": "candidate only; not adopted by the current action",
        },
    ]


def embedding_response_ledger() -> dict[str, Any]:
    return {
        "regular_formula": (
            "zeta=-delta f/(n^A partial_A f)|Sigma"
        ),
        "orientation": (
            "outward cap normal; reversing n reverses numerator convention "
            "consistently and leaves the geometric support fixed"
        ),
        "direct_q_positive": (
            "zeta=-delta sigma/(n partial sigma), valid only for q>0"
        ),
        "direct_fold_rejected": (
            "sigma'_Sigma=O(q), so division by sigma'_Sigma at q=0 is invalid"
        ),
        "blowup_fold": (
            "zeta_0=-delta sigma_hat/(n partial sigma_hat)|Sigma0"
        ),
        "endpoint_identity": (
            "partial_q sigma_hat+s u1'(rho_J) partial_q rho_J=0"
        ),
        "endpoint_slope_plus": "-chi_1/4",
        "endpoint_slope_minus": "+chi_1/4",
        "profile_derivative_at_J": (
            "partial_q sigma_hat|J=s tau chi_1 u1'(rho_J)/4"
        ),
        "recovered_displacement": (
            "zeta_0=-(tau chi_1/4)delta q"
        ),
        "v6_1_7_comparison": (
            "exactly reproduces ell_1=rho_J'(0)=-tau chi_1/4; "
            "the alpha_tau normalization term vanishes at J because u1(J)=0"
        ),
    }


def configuration_space_ledger() -> dict[str, Any]:
    return {
        "current_independent": [
            "bulk g",
            "bulk sigma",
            "intrinsic h",
            "intrinsic connection A",
            "intrinsic sigma_partial",
            "matching multiplier Lambda",
        ],
        "current_embedding": "fixed iota in the provisional B1 domain",
        "candidate_dependent_support": "iota=iota[sigma_hat]",
        "collective_amplitude": "Q>=0 (locally interchangeable with q)",
        "discrete_labels": ["scalar sign s", "sheet tau", "Z2 cap orientation"],
        "gauge": ["radial diffeomorphisms", "tangential B1 reparameterizations"],
        "sigma_partial_relation": "independent; never identified with bulk sigma",
        "required_by_current_action": False,
        "coefficient_free_on_center_manifold": True,
        "currently_adopted": False,
        "classification": (
            "additional off-shell domain restriction/BHSM identification, "
            "not a consequence of the fixed-iota action"
        ),
        "B1_ontology_compatibility": (
            "not algebraically incompatible with independent intrinsic fields, "
            "but it changes the frozen fixed-embedding variational domain"
        ),
    }


def action_and_variation_ledger() -> dict[str, Any]:
    return {
        "fixed_regular_surface_identity": (
            "integral_Sigma sqrt|gamma| L_B1"
            "=integral_M sqrt|g| delta(f)|grad f| L_B1"
        ),
        "distributional_role": "cross-check only; no duplicate action term",
        "orientation_independent": True,
        "scalar_sign_independent": True,
        "two_cap_count": (
            "the common Z2 junction is counted once; cap bulk terms retain "
            "their existing multiplicity"
        ),
        "regular_value_required": True,
        "direct_q_zero_failure": True,
        "fixed_f_equivalence": (
            "surface and delta-function representations are equivalent when f "
            "is fixed and regular"
        ),
        "varied_f_equivalence": False,
        "reason_varied_f_changes_domain": (
            "delta f moves support and induces shape, scalar-flux, B1, and "
            "matching-pullback terms absent from the fixed-iota variation"
        ),
        "new_local_term": False,
        "new_coefficient": False,
        "conditional_interaction": (
            "a composite domain would create a scalar-B1 coupling through "
            "restricted variations, not through a new density"
        ),
        "shape_variation": (
            "delta_iota S=integral_Sigma sqrt|gamma| zeta E_shape"
            "+tangential divergence+existing field equations"
        ),
        "composite_shape_variation": (
            "-integral_Sigma sqrt|gamma| "
            "[delta sigma_hat/(n partial sigma_hat)]E_shape"
        ),
        "shape_status_current_action": (
            "absent because composite support is not adopted"
        ),
        "shape_status_conditional": (
            "finite only after center-manifold projection; the covariant "
            "embedding equation is the normal diffeomorphism Ward combination "
            "of bulk equations and the metric junction, not an independent "
            "new force law"
        ),
        "Noether_identity": True,
        "domain_change_status": "BHSM identification if adopted",
        "result": DOMAIN_RESULT,
    }


def scalar_boundary_ledger() -> dict[str, Any]:
    return {
        "fixed_support": (
            "delta sigma_Sigma=0 is an independently imposed Dirichlet variation"
        ),
        "composite_support_identity": (
            "delta sigma_hat_Sigma+(n partial sigma_hat)zeta=0"
        ),
        "double_imposition_allowed": False,
        "scalar_flux_term": (
            "-Z5 integral_Sigma sqrt|gamma|(n sigma)delta sigma"
        ),
        "moving_domain_term": (
            "endpoint motion combines scalar flux/pressure with E_shape"
        ),
        "B1_and_matcher_term": (
            "their pullbacks contribute through the same induced zeta E_shape"
        ),
        "natural_flux_condition_derived": False,
        "new_wall_pressure_condition_derived": False,
        "current_action_result": (
            "only the fixed-support Dirichlet condition; the composite identity "
            "has no variational force until the domain identification is adopted"
        ),
        "conditional_result": (
            "level-set identity plus center-manifold-projected transversality, "
            "not simultaneous independent Dirichlet data"
        ),
    }


def threading_and_power_ledger() -> dict[str, Any]:
    return {
        "preserved_invariant": (
            "S_Sigma=[B+N0^2 zeta-a0^2 partial_rho E]_Sigma"
        ),
        "direct_q_positive": (
            "S_Sigma^comp=[B-N0^2 delta sigma/(n partial sigma)"
            "-a0^2 partial_rho E]_Sigma"
        ),
        "blowup_fold": (
            "S_Sigma^comp=[B-N0^2 delta sigma_hat/"
            "(n partial sigma_hat)-a0^2 partial_rho E]_Sigma0"
        ),
        "support_condition_supplies": "one relation fixing zeta from the scalar profile",
        "condition_on_S_Sigma": None,
        "threading_classification": (
            "one constraint on zeta but no condition on S_Sigma"
        ),
        "radial_constraint_order": (
            "not derived in the stored scalar ADM operator and not invented here"
        ),
        "pole_conditions": 1,
        "B1_conditions_on_invariant_threading": 0,
        "unresolved_endpoint_traces": 1,
        "residual_kernel_dimension": (
            "at least one boundary trace remains; exact operator kernel not computed"
        ),
        "power_counting": {
            "sigma_prime_Sigma": "O(q)",
            "sigma_hat_prime_Sigma": "O(1)",
            "zeta_direct_generic": "O(delta sigma/q)",
            "zeta_blowup_center_tangent": "O(delta sigma_hat)",
        },
        "finite_variations": [
            "tangent variations on a fixed (tau,s) fold center manifold",
            "the branch endpoint response recovered from delta q",
        ],
        "discrete_not_infinitesimal": ["scalar-sign flip", "sheet exchange"],
        "singular_or_ambiguous": [
            "arbitrary off-branch scalar fluctuations",
            "orthogonal directions with approach-dependent projective profile",
        ],
        "pseudoinverse": False,
        "Green_ready": False,
        "k_q_E_at_fold_calculable": False,
        "fold_route": (
            "viable only after an action-domain choice, preferably evaluated "
            "for q>0 followed by a controlled q->0 limit"
        ),
        "exact_remaining_input": (
            "adopt and vary a composite support domain with its projected "
            "transversality/threading operator, or derive a different "
            "action-selected endpoint condition for S_Sigma"
        ),
        "result": PRIMARY_RESULT,
    }


def integrity_ledger() -> dict[str, Any]:
    return {
        "preserved": {
            "F0_equals_M4_squared": "pi/2",
            "K_scalar": ">=2>0",
            "K_Weyl": "3 chi_1^2(4-pi)^2/(16 pi)>0",
            "J_shift": "-3 tau chi_1 t/[4 sin^2(pi t/4)]",
            "v6_13_result": (
                "BHSM_EXISTING_B1_VARIATION_DOES_NOT_SUPPLY_SHIFT_BOUNDARY_DATA"
            ),
        },
        "new_action_terms": [],
        "new_coefficients": [],
        "new_primitives": [],
        "measured_inputs": [],
    }


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "v6_13_head_sha": V613_HEAD_SHA,
        "primary_result": PRIMARY_RESULT,
        **GUARDS,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "geometry": {
            **_common("BHSM_scalar_wall_level_set_and_blowup_geometry_v6_14_0"),
            "status": CHART_RESULT,
            "fold_constants": {
                "chi_1": CHI_1_DECIMAL,
                "nu_1": NU_1_DECIMAL,
                "mu_c": MU_C_DECIMAL,
                "u1_cap": U1_CAP_DECIMAL,
                "u1_junction": 0,
                "u1_junction_derivative": U1_JUNCTION_DERIVATIVE_DECIMAL,
                "weighted_norm": 1,
            },
            "provenance": provenance_ledger(),
            "direct_level_set": direct_level_set_ledger(),
            "amplitude_and_blowup": amplitude_and_blowup_ledger(),
            "embedding_response": embedding_response_ledger(),
            "exact": {
                "Q_squared": sp.sstr(amplitude_squared_series()),
                "Q_series": sp.sstr(amplitude_series()),
                "sigma_hat_series": sp.sstr(blowup_profile_series()),
                "rhoJ1_plus": sp.sstr(endpoint_slope(1)),
                "rhoJ1_minus": sp.sstr(endpoint_slope(-1)),
                "zeta_plus": sp.sstr(recovered_endpoint_displacement(1, 1)),
                "zeta_minus": sp.sstr(recovered_endpoint_displacement(-1, 1)),
            },
        },
        "variation": {
            **_common("BHSM_composite_B1_variation_and_threading_domain_v6_14_0"),
            "status": PRIMARY_RESULT,
            "configuration_space": configuration_space_ledger(),
            "action_and_variation": action_and_variation_ledger(),
            "scalar_boundary": scalar_boundary_ledger(),
            "threading_and_power": threading_and_power_ledger(),
            "exact_composite_threading": sp.sstr(composite_threading_invariant()),
        },
        "verdict": {
            **_common("BHSM_v6_14_0_scalar_level_set_composite_B1_verdict"),
            "status": PRIMARY_RESULT,
            "direct_q_positive": "regular, unique branchwise support",
            "direct_q_zero": DIRECT_RESULT,
            "blowup_profile": CHART_RESULT,
            "composite_embedding": DOMAIN_RESULT,
            "scalar_Dirichlet": (
                "kinematic identity if composite support is adopted; not also "
                "an independent Dirichlet variation"
            ),
            "shape_equation": (
                "Noether-dependent and center-manifold projected only under "
                "the unadopted composite domain"
            ),
            "endpoint_threading": PRIMARY_RESULT,
            "fold_kinetic_relevance": (
                "insufficient for k_q^E(0); one invariant endpoint trace remains"
            ),
            "integrity": integrity_ledger(),
        },
    }


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def artifact_bytes() -> dict[str, bytes]:
    payloads = artifact_payloads()
    return {
        ARTIFACT_FILES[key]: deterministic_json(payload).encode("utf-8")
        for key, payload in payloads.items()
    }


def materialize_artifacts(root: Path) -> list[Path]:
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for filename, content in artifact_bytes().items():
        path = target / filename
        path.write_bytes(content)
        paths.append(path)
    return paths
