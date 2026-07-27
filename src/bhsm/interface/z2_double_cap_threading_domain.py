"""BHSM v6.15.0 Z2 double-cap scalar-threading domain audit.

The module keeps three orientation conventions separate:

* each cap's pole-to-junction coordinate and outward normal;
* one common normal across the glued interface;
* the signed coordinate obtained from the two stored cap coordinates.

It records the reflection and symplectic-domain consequences of the frozen
P1+GHY+B1+matching action.  It does not add an interface condition or build a
constraint Green operator.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import sympy as sp


VERSION = "v6.15.0"
SPRINT = "bhsm-z2-double-cap-threading-domain-v6-15-0"
SOURCE_MAIN_SHA = "d859a321b5f44b5966853bd922d2d27487238644"
V614_HEAD_SHA = "79531131fd3f3ab16e4690f5e2202c97e7e2c10b"

PRIMARY_RESULT = "BHSM_Z2_SYMPLECTIC_FLUX_LEAVES_ONE_INTERFACE_TRACE"
SHIFT_PARITY_RESULT = "BHSM_Z2_SHIFT_PARITY_DERIVED"
SOURCE_PARITY_RESULT = "BHSM_TWO_CAP_SHIFT_SOURCE_PARITY_DERIVED"
SYMPLECTIC_RESULT = "BHSM_Z2_INTERFACE_SYMPLECTIC_FORM_DERIVED"
SHORTCUT_RESULT = "BHSM_ADAPTED_REFLECTION_ZERO_THREADING_SHORTCUT_REJECTED"
MOVING_RESULT = "BHSM_MOVING_Z2_REFLECTION_REQUIRES_DOMAIN_EXTENSION"

ARTIFACT_FILES = {
    "parity": "BHSM_Z2_double_cap_parity_and_gauge_domain_v6_15_0.json",
    "flux": "BHSM_Z2_interface_symplectic_flux_and_threading_v6_15_0.json",
    "verdict": "BHSM_v6_15_0_fold_domain_verdict.json",
}

GUARDS = {
    "new_action_term": False,
    "new_coefficient": False,
    "new_dimensionful_primitive": False,
    "arbitrary_threading_condition": False,
    "boundary_tension": False,
    "tau_J": False,
    "radion_potential": False,
    "measured_input": False,
    "neutral_work": False,
    "physical_bulk_Dirac_law": False,
    "pseudoinverse": False,
    "Green_operator_constructed": False,
    "complete_fold_kinetic_calculation": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
}

T = sp.symbols("t", real=True)
TAU = sp.symbols("tau", integer=True, nonzero=True)
CHI_1 = sp.symbols("chi_1", real=True, positive=True)
B = sp.symbols("B", real=True)
ZETA = sp.symbols("zeta", real=True)
E_NORMAL = sp.symbols("E_normal", real=True)
N0 = sp.symbols("N_0", real=True, positive=True)
A0 = sp.symbols("a_0", real=True, positive=True)


def _cap(cap: str) -> str:
    if cap not in {"+", "-"}:
        raise ValueError("cap must be '+' or '-'")
    return cap


def signed_coordinate(cap: str, rho: sp.Expr, rho_j: sp.Expr) -> sp.Expr:
    """Return signed y for a stored pole-to-junction cap coordinate.

    M_+ occupies y<=0 and M_- occupies y>=0.  The labels are tied to the
    declared common-normal orientation, not to the sign of y.
    """
    return rho - rho_j if _cap(cap) == "+" else rho_j - rho


def cap_derivative_to_common_factor(cap: str) -> int:
    """Factor converting partial_rho on a cap to partial_y."""
    return 1 if _cap(cap) == "+" else -1


def outward_to_common_factor(cap: str) -> int:
    """Factor converting an outward-normal-oriented object to n_common."""
    return 1 if _cap(cap) == "+" else -1


def reflection_component_parity(normal_index_count: int) -> int:
    """Parity of a covariant tensor component under y -> -y."""
    if normal_index_count < 0:
        raise ValueError("normal_index_count must be nonnegative")
    return -1 if normal_index_count % 2 else 1


def one_cap_shift_source(t: sp.Expr = T, tau: sp.Expr = TAU) -> sp.Expr:
    """Stored v6.12/v6.13 one-cap zero-shift momentum source."""
    return sp.simplify(
        -3 * tau * CHI_1 * t / (4 * sp.sin(sp.pi * t / 4) ** 2)
    )


def reflected_shift_source(
    cap: str,
    *,
    orientation: str = "common",
    t: sp.Expr = T,
    tau: sp.Expr = TAU,
) -> sp.Expr:
    """Two-cap source in outward-cap or common-normal orientation."""
    source = one_cap_shift_source(t=t, tau=tau)
    if orientation == "outward":
        return source
    if orientation == "common":
        return outward_to_common_factor(cap) * source
    raise ValueError("orientation must be 'outward' or 'common'")


def threading_trace(
    *,
    shift: sp.Expr = B,
    displacement: sp.Expr = ZETA,
    normal_E: sp.Expr = E_NORMAL,
) -> sp.Expr:
    """Gauge-invariant endpoint threading in one oriented convention."""
    return sp.expand(shift + N0**2 * displacement - A0**2 * normal_E)


def common_threading_from_outward(cap: str, trace: sp.Expr) -> sp.Expr:
    """Convert the orientation-odd threading trace to n_common."""
    return outward_to_common_factor(cap) * trace


def orientation_ledger() -> dict[str, Any]:
    return {
        "stored_cap_coordinates": (
            "rho_+,rho_- in [0,rho_J], each increasing from its regular pole "
            "toward the common junction"
        ),
        "signed_coordinate": {
            "M_+": "y=rho_+-rho_J in [-rho_J,0]",
            "M_-": "y=rho_J-rho_- in [0,rho_J]",
        },
        "reflection": "R:(y,x^mu)->(-y,x^mu), equivalently rho_+<->rho_-",
        "derivatives": {
            "partial_rho,+": "+partial_y",
            "partial_rho,-": "-partial_y",
        },
        "normals": {
            "n_+": "+N^-1 partial_y=+N^-1 partial_rho,+",
            "n_-": "-N^-1 partial_y=+N^-1 partial_rho,-",
            "n_common": "+N^-1 partial_y=n_+=-n_-",
            "required_check": "n_-=-n_+ under the interface identification",
        },
        "extrinsic_curvature": {
            "definition": "K_mu_nu=(1/2)L_n gamma_mu_nu",
            "common": "K_common,-=-K_common,+",
            "outward": "K_out,-=K_out,+ for reflection-copied caps",
            "trace": "K reverses with the chosen normal",
            "Q": "Q_common,-=-Q_common,+ and [Q]=2Q_common,+",
            "nonzero_allowed": True,
            "K_zero_inferred": False,
        },
        "scalar_normal_derivative": {
            "background": "sigma_-(rho)=-sigma_+(rho)",
            "signed_y": "partial_y sigma is reflection even",
            "common": "(n_common sigma)_-=(n_common sigma)_+",
            "outward": "(n_- sigma)_-=-(n_+ sigma)_+",
        },
        "lapse": "N_-(rho)=N_+(rho); N is positive and reflection even",
        "radial_shift": {
            "signed": "N_y(0+)=-N_y(0-)",
            "outward_cap": "N_rho,-=N_rho,+ after the coordinate Jacobian",
        },
        "longitudinal_derivative": {
            "signed": "partial_y E(0+)=-partial_y E(0-)",
            "outward_cap": "partial_rho,- E=partial_rho,+ E",
        },
        "endpoint_displacement": {
            "homogeneous_copied_caps": "zeta_out,-=zeta_out,+",
            "common_conversion": "zeta_common,-=-zeta_common,+",
            "single_moving_center": (
                "one zeta(x) in y-zeta(x) changes the reflection map and is "
                "not the stored copywise homogeneous cap-length variation"
            ),
        },
        "status": "Derived consequence",
    }


def z2_notions_ledger() -> dict[str, Any]:
    return {
        "A_background_cap_exchange": {
            "contained": True,
            "meaning": "two identical static regular caps are exchanged by R",
        },
        "B_fixed_support_orbifold_parity": {
            "contained": True,
            "meaning": "the frozen gluing map has fixed set Sigma at y=0",
        },
        "C_moving_covariant_reflection": {
            "contained": False,
            "meaning": (
                "R_zeta:y-zeta(x)->-[y-zeta(x)] is an x-dependent change of "
                "the fixed-set/gluing datum"
            ),
        },
        "homogeneous_family": (
            "rho_J(q) labels separately solved doubled backgrounds; it does "
            "not promote R to an x-dependent varied reflection"
        ),
        "composite_support": (
            "sigma_hat can determine a moving center only after the additional "
            "v6.14 center-manifold domain identification is adopted"
        ),
        "result": MOVING_RESULT,
    }


def parity_ledger() -> dict[str, Any]:
    return {
        "derivation": (
            "R has Jacobian diag(-1,1,1,1,1); every covariant y index "
            "contributes one minus sign in R^*g"
        ),
        "metric_pullback": {
            "g_yy": "even",
            "g_y_mu": "odd",
            "g_mu_nu": "even",
        },
        "ADM_fields_signed_y": {
            "N": "even (positive lapse branch)",
            "N_mu": "odd",
            "B": "odd",
            "psi": "even",
            "E": "even",
        },
        "scalar": {
            "background": "odd: sigma_-(rho)=-sigma_+(rho)",
            "fold_amplitude_perturbation": "odd",
            "sigma_hat": "odd on every fixed (tau,s) center sheet",
            "orbifold_admissible_arbitrary_perturbation": "odd and Dirichlet",
            "unrestricted_cover_perturbation": (
                "decomposes into even and odd sectors; background parity alone "
                "does not silently admit the even sector"
            ),
            "pure_radial_gauge_perturbation": (
                "-sigma_0' xi^y is odd because sigma_0' is even and xi^y is odd"
            ),
        },
        "endpoint": {
            "fixed_support": "zeta=0",
            "copywise_outward": "even across cap labels",
            "copywise_common_normal": "odd across cap labels",
            "moving_reflection_center": "not assigned frozen-domain parity",
        },
        "gauge_parameters": {
            "xi^y": "odd for a continuous fixed-gluing diffeomorphism",
            "xi^y_at_Sigma": 0,
            "xi": "even tangential scalar",
        },
        "gauge_invariants": {
            "Psi_Sigma": "even",
            "delta_sigma_Sigma": "odd (and zero in the stored Dirichlet domain)",
            "delta_X_Sigma": "even",
            "S_Sigma_common": "odd one-sided trace",
            "S_Sigma_outward": "equal on the two copied caps",
        },
        "threading_relations": {
            "common": "S_common,-=-S_common,+",
            "outward": "S_out,-=S_out,+",
            "zero_forced_by_parity": False,
        },
        "result": SHIFT_PARITY_RESULT,
    }


def regularity_ledger() -> dict[str, Any]:
    return {
        "geometry_class": (
            "piecewise C^2 bulk metric with continuous induced metric and an "
            "intentional one-sided first-normal-derivative jump at Sigma"
        ),
        "h_mu_nu": "continuous trace; piecewise C^2; normal derivative may jump",
        "N": "reflection-even one-sided traces; positive lapse may be continuous",
        "N_mu_and_B": (
            "one-sided multiplier traces obey reflection parity; neither the "
            "induced-metric matcher nor the stored action establishes their "
            "signed-coordinate continuity"
        ),
        "psi_and_E": "continuous as induced-metric scalars; piecewise C^2",
        "normal_E": "one-sided odd relation; a jump is allowed",
        "sigma": "continuous odd Dirichlet trace sigma_Sigma=0; piecewise C^2",
        "normal_sigma": (
            "common-normal derivative even; outward derivatives opposite"
        ),
        "K_and_Q": "finite one-sided traces with the B1-supported jump",
        "odd_trace_rule": (
            "odd parity implies a zero fixed-set value only after continuity "
            "of that field is established"
        ),
        "B_zero_from_parity": False,
        "partial_y_E_zero_from_parity": False,
        "erroneous_smoothness_condition": "K=0 is rejected",
    }


def diffeomorphism_ledger() -> dict[str, Any]:
    return {
        "cap_preserving": (
            "piecewise diffeomorphisms related by R and preserving pole regularity"
        ),
        "cap_exchanging": "composition of an allowed map with the fixed R",
        "gluing_preserving": (
            "xi^y odd and continuous, hence xi^y|Sigma=0; xi tangential and even"
        ),
        "interface_moving": (
            "xi^y|Sigma!=0 changes the declared fixed set unless the embedding/"
            "reflection map is added to the domain"
        ),
        "tangential_B1": "even xi generates intrinsic reparameterizations",
        "forbidden_current_domain": (
            "independent changes of the two pole-to-junction domains or of R"
        ),
        "gauge_choices": {
            "zeta_zero": "already fixed in Case I; not a removal of S_Sigma",
            "E_zero": "allowed with even xi",
            "B_zero": (
                "may be imposed locally only with compensating E/zeta data; "
                "it cannot change the invariant S_Sigma"
            ),
            "all_three_zero": (
                "possible only when S_Sigma was already zero or after an extra "
                "domain restriction"
            ),
        },
        "S_Sigma_gauge_invariant": True,
        "global_Z2_removes_trace_as_gauge": False,
    }


def constraint_source_ledger() -> dict[str, Any]:
    return {
        "one_cap": "J_tau(t)=-3 tau chi_1 t/[4 sin^2(pi t/4)]",
        "outward_caps": {
            "J_+": "J_tau(t)",
            "J_-": "J_tau(t)",
        },
        "common_normal": {
            "J_+": "J_tau(t)",
            "J_-": "-J_tau(t)",
        },
        "signed_interval_sector": "odd",
        "derivation": (
            "the copied outward-cap geometry gives equal sources; converting "
            "the minus cap to n_common contributes the normal-orientation sign"
        ),
        "tau_dependence": "tau reverses the source on both caps",
        "scalar_sign_dependence": False,
        "sheet_dependence": True,
        "even_weight_integral": 0,
        "automatic_compatibility": (
            "oddness makes the symmetric weighted integral vanish against an "
            "even constant test mode"
        ),
        "full_Fredholm_compatibility_certified": False,
        "reason_full_compatibility_open": (
            "the exact coupled radial operator and all adjoint kernels are not stored"
        ),
        "result": SOURCE_PARITY_RESULT,
    }


def canonical_pairing_ledger() -> dict[str, Any]:
    return {
        "total_potential": (
            "Theta_Sigma,total=Theta_+^out+Theta_-^out+Theta_B1+"
            "Theta_match"
        ),
        "cap_metric_pair": {
            "configuration": "gamma_mu_nu",
            "momentum": "pi_out^mu_nu=(kappa_1/2)Q_out^mu_nu",
        },
        "common_orientation_metric_sum": (
            "(kappa_1/2)[Q_mu_nu] delta gamma^mu_nu"
        ),
        "B1_metric_coefficient": (
            "(C_partial G_mu_nu^(4)-T_partial,mu_nu/2)delta gamma^mu_nu"
        ),
        "matcher": (
            "Lambda pairs with h-iota^*g algebraically and cancels from the "
            "combined junction equation after exact matching"
        ),
        "scalar_pair": {
            "configuration": "delta sigma_Sigma",
            "momentum": "-Z5(n_out sigma) on each cap",
        },
        "endpoint_displacement": (
            "absent as an independent configuration in the frozen fixed-iota action"
        ),
        "threading": {
            "classification": (
                "gauge-invariant radial-shift/longitudinal multiplier trace"
            ),
            "canonical_momentum": 0,
            "Euler_Lagrange_partner": "bulk longitudinal momentum constraint",
            "independent_interface_conjugate": None,
            "present_in_symplectic_form": False,
        },
        "on_shell_metric_coefficient": (
            "one half of J_mu_nu delta gamma^mu_nu, with "
            "J_mu_nu=kappa_1[Q_mu_nu]+2C_partial G_mu_nu-T_partial,mu_nu"
        ),
        "result": SYMPLECTIC_RESULT,
    }


def junction_projection_ledger() -> dict[str, Any]:
    return {
        "equation": (
            "J_mu_nu=kappa_1[Q_mu_nu]+2C_partial G_mu_nu^(4)"
            "-T_partial,mu_nu=0"
        ),
        "scalar_projections": [
            "Hamiltonian scalar J_00",
            "longitudinal momentum scalar D^i J_0i",
            "spatial trace scalar gamma^ij J_ij",
            "traceless-longitudinal scalar D^iD^j J_ij^TL",
        ],
        "raw_projection_count": 4,
        "scalar_Ward_relations": 2,
        "independent_scalar_equation_count": 2,
        "dependencies": {
            "longitudinal": (
                "Codazzi plus the bulk momentum constraint equals the intrinsic "
                "Bianchi/stress-conservation identity"
            ),
            "temporal": (
                "the remaining scalar divergence is fixed by the bulk "
                "Hamiltonian/evolution identities and intrinsic conservation"
            ),
        },
        "longitudinal_counted_twice": False,
        "S_occurrence": (
            "any raw longitudinal shift dependence lies in the constraint/Ward "
            "combination; no independent scalar projection supplies an "
            "interface equation for S_Sigma"
        ),
        "condition_on_S_Sigma": None,
    }


def symplectic_flux_ledger() -> dict[str, Any]:
    return {
        "boundary_form": (
            "Omega_Sigma(delta1,delta2)=delta1 Theta_Sigma,total(delta2)"
            "-delta2 Theta_Sigma,total(delta1)"
        ),
        "metric_term": (
            "(1/2) integral_Sigma [delta1 J_mu_nu delta2 gamma^mu_nu"
            "-delta2 J_mu_nu delta1 gamma^mu_nu]"
        ),
        "scalar_term": (
            "-Z5 sum_caps integral_Sigma [delta1(n_out sigma)"
            " delta2 sigma-delta2(n_out sigma) delta1 sigma]"
        ),
        "matcher_term": "zero after h=iota^*g and Lambda elimination",
        "conditions_applied": [
            "cap reflection parity",
            "induced-metric matching",
            "odd scalar Dirichlet matching",
            "intrinsic B1 equations",
            "linearized metric junction",
            "allowed fixed-gluing gauge quotient",
        ],
        "metric_flux_on_domain": 0,
        "scalar_flux_on_fixed_Dirichlet_domain": 0,
        "S_Sigma_term": None,
        "vanishing_flux_requires": (
            "no condition on the surviving reflection-compatible S_Sigma trace"
        ),
        "options": {
            "S_zero": False,
            "common_orientation_relation": "S_common,-=-S_common,+",
            "outward_orientation_relation": "S_out,-=S_out,+",
            "momentum_matching_for_S": False,
            "Robin_relation": False,
            "cap_flux_cancellation_for_arbitrary_common_trace": True,
            "additional_reflection_domain_declaration": (
                "required only to impose stronger continuity/zero-trace data"
            ),
        },
        "parity_allowed_null_trace_dimension": 1,
        "Robin_family_parameter_dimension": None,
        "maximal_isotropic_conclusion": (
            "S_Sigma is a presymplectic null direction, so flux does not select "
            "a Lagrangian slope or a value on its one-dimensional trace line"
        ),
        "result": PRIMARY_RESULT,
    }


def support_domain_ledger() -> dict[str, Any]:
    return {
        "Case_I_fixed_iota": {
            "adopted": True,
            "zeta": 0,
            "trace_relation_common": "S_common,-=-S_common,+",
            "trace_relation_outward": "S_out,-=S_out,+",
            "symplectic_condition_on_S": None,
            "unresolved_interface_traces": 1,
        },
        "Case_II_composite_support": {
            "adopted": False,
            "zeta": "-delta sigma_hat/(n partial sigma_hat)",
            "scope": "fixed (tau,s) center-manifold tangent",
            "trace_relation_common": "S_common,-=-S_common,+",
            "trace_relation_outward": "S_out,-=S_out,+",
            "symplectic_condition_on_S": None,
            "unresolved_interface_traces": 1,
            "closes_domain": False,
            "required_axiom": (
                "identify iota off shell with the regular center-manifold "
                "level set of sigma_hat and vary the induced pullbacks"
            ),
        },
        "moving_reflection_center": {
            "adopted": False,
            "adapted_coordinate": "y_tilde=y-zeta(x)",
            "classification": (
                "an x-dependent change of the reflection/gluing map; arbitrary "
                "zeta is an additional orbifold datum, while composite zeta "
                "would be a dependent datum under the unadopted v6.14 axiom"
            ),
            "fixed_double_diffeomorphism": False,
            "S_in_adapted_coordinate": (
                "B_tilde-a0^2 partial_y_tilde E; equal to the original "
                "gauge-invariant S_Sigma"
            ),
        },
        "zero_threading_shortcut": {
            "argument": "B=0, partial_y E=0, zeta=0 therefore S_Sigma=0",
            "accepted": False,
            "failures": [
                "the moving reflection is absent from the frozen action domain",
                "continuity of B is not supplied by induced-metric matching",
                "partial_y E is allowed a junction jump",
                "S_Sigma is unchanged by the proposed gauge choices",
                "setting the remaining trace to zero deletes domain data",
            ],
            "result": SHORTCUT_RESULT,
        },
    }


def domain_count_ledger() -> dict[str, Any]:
    return {
        "bulk_scalar_metric_functions": [
            "lapse A",
            "radial shift B",
            "Weyl scalar psi",
            "longitudinal scalar E",
        ],
        "bulk_scalar_metric_function_count": 4,
        "endpoint_representative": "zeta (diagnostic; not a Case-I action variable)",
        "scalar_source_profile": "delta sigma or the fold tangent",
        "differential_order_each_cap": None,
        "order_status": (
            "the exact coupled reduced radial operator was not derived in the "
            "stored ADM sprint and is not invented here"
        ),
        "pole_regularity": {
            "M_+": "regular at rho_+=0",
            "M_-": "regular at rho_-=0",
            "independent_conditions": "one stored regular-pole condition per cap",
        },
        "interface_matching": [
            "continuous induced metric",
            "reflection parity relations",
            "odd scalar Dirichlet trace",
            "linearized metric junction modulo two scalar Ward identities",
        ],
        "gauge_kernels": [
            "continuous odd xi^y preserving y=0",
            "even tangential scalar xi",
        ],
        "physical_homogeneous_kernel_dimension": None,
        "kernel_status": (
            "S_Sigma is not gauge, but is not promoted to a physical radion "
            "without an embedding/domain variational rule"
        ),
        "free_trace": (
            "one common outward-cap value S_out,+ = S_out,-, equivalently one "
            "odd common-normal amplitude S_common,-=-S_common,+"
        ),
        "unresolved_interface_trace_count": 1,
        "Green_ready": False,
        "boundary_operator_for_next_sprint": None,
        "adjoint_interface_operator": None,
        "pseudoinverse_used": False,
    }


def provenance_ledger() -> list[dict[str, str]]:
    return [
        {
            "item": "tensor pullback and oriented-boundary symplectic formulas",
            "status": "Adopted from established physics/mathematics",
        },
        {
            "item": "provisional B1 and exact metric matcher",
            "status": "Adopted BHSM axiom",
        },
        {
            "item": "fixed signed-coordinate orientation ledger",
            "status": "BHSM identification",
        },
        {
            "item": "Z2 threading parity and source parity",
            "status": "Derived consequence",
        },
        {
            "item": "one surviving presymplectic-null interface trace",
            "status": "Derived consequence",
        },
        {
            "item": "adapted-reflection zero-threading shortcut",
            "status": "Rejected by calculation",
        },
        {
            "item": "constraint Green operator after a domain theorem",
            "status": "Active construction target",
        },
    ]


def verdict_ledger() -> dict[str, Any]:
    return {
        "primary_theorem": PRIMARY_RESULT,
        "selected_threading_condition": None,
        "Z2_supplies_relation_not_value": True,
        "relation_outward": "S_out,-=S_out,+",
        "relation_common": "S_common,-=-S_common,+",
        "unresolved_interface_trace_count": 1,
        "coefficient_free_closure_achieved": False,
        "composite_support_closes_domain": False,
        "moving_Z2_requires_domain_extension": True,
        "constraint_source_compatibility_violation": False,
        "full_solvability_certified": False,
        "Green_operator_ready": False,
        "fold_route_decision": (
            "C. One invariant trace remains: pause the fold kinetic route and "
            "do not select a convenient condition"
        ),
        "exact_remaining_input": (
            "an action-derived or explicitly adopted BHSM interface-domain "
            "axiom fixing the single gauge-invariant threading trace; only then "
            "derive L_C, its adjoint domain, kernels, and solvability condition"
        ),
        "k_q_E_certified": False,
    }


def integrity_ledger() -> dict[str, Any]:
    return {
        "preserved": {
            "v6_13": (
                "BHSM_EXISTING_B1_VARIATION_DOES_NOT_SUPPLY_SHIFT_BOUNDARY_DATA"
            ),
            "v6_14": (
                "BHSM_COMPOSITE_B1_SUPPORT_LEAVES_ENDPOINT_THREADING_OPEN"
            ),
            "endpoint_response": "partial_q rho_J,tau=-tau chi_1/4",
            "fold_displacement": "zeta_0=-tau chi_1 delta q/4",
            "F0_equals_M4_squared": "pi/2",
            "K_scalar": ">=2>0",
            "K_Weyl": "3 chi_1^2(4-pi)^2/(16 pi)>0",
            "kinetic_decomposition": (
                "k_q^E=K_scalar+K_shift+endpoint^red+K_Weyl"
            ),
            "J_shift": "-3 tau chi_1 t/[4 sin^2(pi t/4)]",
        },
        "new_terms": [],
        "new_coefficients": [],
        "new_primitives": [],
        "measured_inputs": [],
        "guards": dict(GUARDS),
    }


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "v6_14_head_sha": V614_HEAD_SHA,
        "primary_result": PRIMARY_RESULT,
        **GUARDS,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "parity": {
            **_common("BHSM_Z2_double_cap_parity_and_gauge_domain_v6_15_0"),
            "orientation": orientation_ledger(),
            "Z2_notions": z2_notions_ledger(),
            "parity": parity_ledger(),
            "regularity": regularity_ledger(),
            "diffeomorphisms": diffeomorphism_ledger(),
            "provenance": provenance_ledger(),
        },
        "flux": {
            **_common(
                "BHSM_Z2_interface_symplectic_flux_and_threading_v6_15_0"
            ),
            "constraint_source": constraint_source_ledger(),
            "canonical_pairing": canonical_pairing_ledger(),
            "junction_projections": junction_projection_ledger(),
            "symplectic_flux": symplectic_flux_ledger(),
        },
        "verdict": {
            **_common("BHSM_v6_15_0_fold_domain_verdict"),
            "support_domains": support_domain_ledger(),
            "domain_count": domain_count_ledger(),
            "verdict": verdict_ledger(),
            "integrity": integrity_ledger(),
        },
    }


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


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
