"""BHSM v6.12.0 Einstein-frame fold kinetic reduction.

The two-cap bulk action plus intrinsic B1 term fixes the four-dimensional
frame function through first order and therefore fixes the Weyl contribution
to the fold kinetic coefficient.  The zero-shift promotion of the v6.11
static tangent violates the radial momentum constraint.  The repository does
not supply the scalar radial-shift Green-function boundary condition at the
moving B1 endpoint, so the constraint Schur complement and total kinetic sign
are not defined.  In addition, the stored cusp is an on-shell, X-substituted
action rather than an off-shell Jordan potential; its Einstein-frame Hessian
requires the unavailable second profile response F_2[a_2,N_2].
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import sympy as sp


VERSION = "v6.12.0"
SPRINT = "bhsm-fold-einstein-frame-kinetic-reduction-v6-12-0"
SOURCE_MAIN_SHA = "f4816c03f531becdcbb5dde8f1b025b21eeb770e"
V611_HEAD_SHA = "3688995f49a77c270f20ccc9817e5a69a82a0a58"

PRIMARY_RESULT = (
    "BHSM_FOLD_KINETIC_SIGN_REQUIRES_MOVING_ENDPOINT_SHIFT_BOUNDARY_CONDITION"
)
FRAME_RESULT = "BHSM_FOUR_DIMENSIONAL_FRAME_FUNCTION_DERIVED_TO_FIRST_ORDER"
POTENTIAL_RESULT = (
    "BHSM_FOLD_EINSTEIN_CURVATURE_REQUIRES_OFFSHELL_JORDAN_POTENTIAL_AND_F2"
)
PHYSICAL_RESULT = "BHSM_FOLD_PHYSICAL_CLASSIFICATION_UNRESOLVED_CASE_E"

ARTIFACT_FILES = {
    "constraints": "BHSM_fold_radial_ADM_scalar_constraints_v6_12_0.json",
    "frame": "BHSM_fold_four_dimensional_frame_function_v6_12_0.json",
    "jordan": "BHSM_fold_Jordan_moduli_metric_v6_12_0.json",
    "einstein": "BHSM_fold_Einstein_frame_kinetic_norm_v6_12_0.json",
    "verdict": "BHSM_fold_physical_mass_and_sheet_verdict_v6_12_0.json",
    "report": "BHSM_v6_12_0_hidden_input_and_final_report.json",
}

GUARDS = {
    "new_action_term_introduced": False,
    "tau_J_introduced": False,
    "new_primitive_introduced": False,
    "neutral_transport_used": False,
    "fermion_loop_introduced": False,
    "measured_inputs_used": False,
    "physical_bulk_Dirac_law_introduced": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "lambda_geom_changed": False,
    "sheet_map_changed": False,
    "global_stability_claimed": False,
}

T = sp.symbols("t", real=True, nonnegative=True)
Q = sp.symbols("q", real=True, nonnegative=True)
CHI_1 = sp.symbols("chi_1", real=True, positive=True)
NU_1 = sp.symbols("nu_1", real=True, positive=True)
F2 = sp.symbols("F_2", real=True)
K_SCALAR = sp.symbols("K_scalar", real=True, positive=True)
K_UNRESOLVED = sp.symbols("K_shift_endpoint_red", real=True)
V0, V1, V2 = sp.symbols("V_0 V_1 V_2", real=True)


def a0(t: sp.Expr = T) -> sp.Expr:
    return sp.sqrt(2) * sp.sin(sp.pi * t / 4)


def lapse0() -> sp.Expr:
    return sp.pi / 4


def a1(t: sp.Expr = T) -> sp.Expr:
    return CHI_1 * (
        a0(t) / 4 - sp.sqrt(2) * t * sp.cos(sp.pi * t / 4) / 4
    )


def lapse1() -> sp.Expr:
    return -CHI_1 / 4


def one_cap_frame_integral_0() -> sp.Expr:
    return sp.simplify(sp.integrate(lapse0() * a0(T) ** 2, (T, 0, 1)))


def one_cap_frame_integral_1() -> sp.Expr:
    integrand = lapse1() * a0(T) ** 2 + 2 * lapse0() * a0(T) * a1(T)
    return sp.simplify(sp.integrate(integrand, (T, 0, 1)))


def frame_F0() -> sp.Expr:
    """F0=two-cap bulk coefficient plus B1 with C_partial=1/2."""
    kappa_1 = sp.Integer(1)
    c_partial = sp.Rational(1, 2)
    return sp.simplify(
        2 * kappa_1 * one_cap_frame_integral_0() + 2 * c_partial
    )


def frame_F1(tau: int) -> sp.Expr:
    """One-sided derivative of F on the tau sheet."""
    if tau not in (-1, 1):
        raise ValueError("tau must be +/-1")
    return sp.simplify(2 * tau * one_cap_frame_integral_1())


def frame_function(tau: int) -> sp.Expr:
    """Taylor form through the first unavailable second response."""
    return frame_F0() + frame_F1(tau) * Q + F2 * Q**2 / 2


def frame_F2_formula() -> sp.Expr:
    """Exact functional dependence on unavailable a2,N2 profiles."""
    a2 = sp.Function("a_2")(T)
    n2 = sp.Function("N_2")(T)
    integrand = (
        lapse0() * (a1(T) ** 2 + a0(T) * a2)
        + 2 * lapse1() * a0(T) * a1(T)
        + n2 * a0(T) ** 2 / 2
    )
    return sp.simplify(4 * sp.integrate(integrand, (T, 0, 1)))


def omega_squared(tau: int) -> sp.Expr:
    """g_E=Omega^2 h with constant Einstein coefficient F0."""
    return sp.simplify(frame_function(tau) / frame_F0())


def omega_linear(tau: int) -> sp.Expr:
    return sp.simplify(1 + frame_F1(tau) * Q / (2 * frame_F0()))


def weyl_kinetic_at_fold(tau: int) -> sp.Expr:
    """Four-dimensional Weyl contribution 3 F1^2/(2 F0)."""
    return sp.simplify(3 * frame_F1(tau) ** 2 / (2 * frame_F0()))


def frame_ledger() -> dict[str, Any]:
    return {
        "metric": "ds5^2=N(t,q)^2 dt^2+a(t,q)^2 h_mu_nu dx^mu dx^nu",
        "cap_multiplicity": 2,
        "bulk_R4_coefficient": (
            "F_bulk(q)=2 kappa_1 integral_0^1 N a^2 dt"
        ),
        "B1_R4_coefficient": "F_B1=2 C_partial=1",
        "GHY_R4_coefficient": 0,
        "endpoint_differentiation": (
            "included by fixed-domain N(q)=rho_J(q); equivalent to the moving "
            "upper-limit term"
        ),
        "F0": "pi/2",
        "F1_plus": "chi_1(pi-4)/4",
        "F1_minus": "-chi_1(pi-4)/4",
        "F2": (
            "4 integral[N0(a1^2+a0 a2)+2N1 a0 a1+(N2/2)a0^2]dt"
        ),
        "F2_status": "requires the analytic second profile response a2,N2",
        "Einstein_metric": "g_E=(F/F0)h",
        "Omega_squared": "F/F0",
        "Einstein_Planck_coefficient": "M4^2=F0=pi/2",
        "dimension": (
            "F has the four-dimensional Einstein coefficient dimension; "
            "normalized representative suppresses the common action unit"
        ),
        "result": FRAME_RESULT,
    }


def static_hubble0(t: sp.Expr = T) -> sp.Expr:
    return sp.simplify(sp.diff(a0(t), t) / (lapse0() * a0(t)))


def static_hubble1(t: sp.Expr = T) -> sp.Expr:
    """Variation of H=a_t/(Na) along the normalized fold tangent."""
    value = (
        sp.diff(a1(t), t) / (lapse0() * a0(t))
        - sp.diff(a0(t), t) * lapse1() / (lapse0() ** 2 * a0(t))
        - sp.diff(a0(t), t) * a1(t) / (lapse0() * a0(t) ** 2)
    )
    return sp.trigsimp(sp.simplify(value))


def momentum_constraint_zero_shift_mismatch(tau: int) -> sp.Expr:
    """Coefficient of partial_mu q at q=0 when shift compensation is omitted."""
    if tau not in (-1, 1):
        raise ValueError("tau must be +/-1")
    # D_nu(K^nu_mu-delta^nu_mu K)=-3 partial_mu H.
    # The scalar flux vanishes at sigma_0'=0.
    return sp.simplify(-3 * tau * static_hubble1(T))


def gauge_ledger() -> dict[str, Any]:
    return {
        "radial_parameter": "xi^rho(x,t)",
        "M4_scalar_parameter": "xi(x,t), delta x^mu=nabla^mu xi",
        "transformations": {
            "delta_sigma": "delta_sigma-xi^rho partial_rho sigma_0",
            "psi": "psi-H xi^rho",
            "lapse_A": "A-N0^-1 partial_t(N0 xi^rho)",
            "shift_B": "B-N0^2 xi^rho-a0^2 partial_t xi",
            "longitudinal_E": "E-xi",
            "endpoint": "delta rho_J-xi^rho|J",
            "delta_X": (
                "intrinsic pullback curvature is invariant when the endpoint "
                "transformation is included"
            ),
        },
        "fold_not_pure_gauge": "delta X=tau chi_1 is intrinsic",
        "endpoint_invariant": "delta rho_J+xi-compensated induced trace",
        "complete_gauge_fixed": False,
        "residual_mode": (
            "homogeneous scalar shift solution until a B1 endpoint condition is supplied"
        ),
        "gauge_kernel_inverted": False,
    }


def adm_constraint_ledger() -> dict[str, Any]:
    return {
        "ADM_metric": (
            "ds5^2=N^2 dt^2+h_mu_nu(dx^mu+N^mu dt)"
            "(dx^nu+N^nu dt)"
        ),
        "scalar_variables": [
            "lapse A_q(t)",
            "radial shift N_mu=partial_mu B_q(t)",
            "Weyl scalar psi_q(t)",
            "longitudinal scalar E_q(t)",
            "endpoint delta rho_J,q",
            "bulk scalar delta sigma_q(t)",
        ],
        "Hamiltonian": (
            "delta_N S=0; normal Einstein constraint including scalar and "
            "x-dependent metric terms"
        ),
        "momentum": (
            "D_nu(K^nu_mu-delta^nu_mu K)"
            "=kappa_1^-1 Z5(n sigma)D_mu sigma"
        ),
        "critical_scalar_flux": 0,
        "zero_shift_mismatch": (
            "-3 tau chi_1 t/[4 sin(pi t/4)^2] partial_mu q"
        ),
        "zero_shift_admissible": False,
        "lapse_solution": None,
        "shift_solution": None,
        "endpoint_compensator": None,
        "bulk_regular_condition": "regular at t=0",
        "missing_boundary_condition": (
            "the scalar radial-shift/longitudinal Green-function condition at "
            "the moving B1 endpoint t=1"
        ),
        "B1_stored_variation": (
            "homogeneous background junction and conservation identities only; "
            "no x-dependent scalar shift/endpoint second variation"
        ),
        "boundary_flux_cancellation": None,
        "homogeneous_mode_classification": (
            "cannot distinguish residual gauge from boundary radion until the "
            "endpoint shift condition is fixed"
        ),
        "unique_constraint_inverse": False,
        "result": PRIMARY_RESULT,
    }


def jordan_moduli_ledger() -> dict[str, Any]:
    return {
        "form": (
            "S_J=integral sqrt(-h)[F(q)R4/2-K_J(q)(partial q)^2/2-V_J(q)]"
        ),
        "K_scalar": (
            "2 Z5 integral_0^rhoJ N a^2(partial_q sigma)^2 d rho >=2"
        ),
        "K_EH": (
            "bulk ADM scalar quadratic form; depends on A_q,B_q,E_q and psi_q"
        ),
        "K_GHY": (
            "cancels radial second derivatives and contributes to the endpoint "
            "constraint form; separate value unavailable before compensation"
        ),
        "K_B1": (
            "intrinsic C_partial R4 contributes to F and boundary scalar "
            "metric constraints; direct q term vanishes at fixed a_J=1"
        ),
        "K_constraint": (
            "negative/indefinite Schur term after solving lapse and shift"
        ),
        "K_endpoint": (
            "moving-boundary response paired with the scalar shift trace"
        ),
        "cancellations": (
            "EH/GHY/constraint/endpoint pieces are gauge dependent separately"
        ),
        "known_partial_sum": "K_scalar>=2",
        "unresolved_sum": (
            "K_EH+K_GHY+K_B1+K_constraint+K_endpoint"
        ),
        "total_K_J": None,
        "reason": "no unique shift/endpoint constraint inverse",
        "hidden_normalization_to_one": False,
    }


def einstein_kinetic_ledger() -> dict[str, Any]:
    return {
        "Weyl_formula": (
            "k_E=(F0/F)K_J+(3F0/2)(F'/F)^2"
        ),
        "at_fold": "k_q^E(0)=K_J(0)+3F1^2/(2F0)",
        "Weyl_exact": "3 chi_1^2(4-pi)^2/(16 pi)>0",
        "scalar_bound": "K_scalar>=2>0",
        "unknown_existing_action_piece": (
            "K_shift_endpoint_red=K_EH+K_GHY+K_B1+K_constraint+K_endpoint"
        ),
        "total": (
            "k_q^E(0)=K_scalar+K_shift_endpoint_red"
            "+3 chi_1^2(4-pi)^2/(16 pi)"
        ),
        "sign": None,
        "positive_norm_certified": False,
        "ghost_certified": False,
        "zero_or_nondynamical_certified": False,
        "gauge_independent": False,
        "reason": (
            "K_shift_endpoint_red is undefined without the moving-endpoint "
            "radial-shift boundary condition"
        ),
        "result": PRIMARY_RESULT,
    }


def formal_einstein_potential() -> sp.Expr:
    """V_E=(F0/F)^2 V_J through a formal Taylor polynomial."""
    f = frame_F0() + sp.Symbol("F_1", real=True) * Q + F2 * Q**2 / 2
    v = V0 + V1 * Q + V2 * Q**2 / 2
    return sp.simplify((frame_F0() / f) ** 2 * v)


def einstein_potential_hessian_formula() -> sp.Expr:
    """Second derivative at q=0 before imposing a stationary relation."""
    return sp.simplify(sp.diff(formal_einstein_potential(), Q, 2).subs(Q, 0))


def potential_ledger() -> dict[str, Any]:
    return {
        "v6_11_Gamma": (
            "Gamma_red,tau=Gamma_c+(delta_mu/4)q^2"
            "-tau(nu_1/6)q^3+..."
        ),
        "frame_classification": (
            "on-shell regulated action after substituting the maximally "
            "symmetric X(q) branch and X-dependent four-volume"
        ),
        "is_offshell_V_J": False,
        "formal_transform": "V_E=(F0/F)^2 V_J",
        "formal_hessian": (
            "V_E''(0)=V2-4(F1/F0)V1"
            "+[6(F1/F0)^2-2F2/F0]V0"
        ),
        "missing_inputs": [
            "off-shell Jordan coefficients V0,V1,V2 before the X equation",
            "F2 from a2,N2 and moving-endpoint response",
        ],
        "stationary_point_preservation": (
            "cannot test until V_J and F are known consistently off shell"
        ),
        "B_ext_E": None,
        "B_core_E": None,
        "canonical_mass_ext": None,
        "canonical_mass_core": None,
        "reduced_signs_preserved_as_physical": False,
        "result": POTENTIAL_RESULT,
    }


def verdict_ledger() -> dict[str, Any]:
    return {
        "case": "E",
        "k_q_E": None,
        "B_ext_E": None,
        "B_core_E": None,
        "m_ext_squared": None,
        "m_core_squared": None,
        "tachyon": False,
        "ghost": False,
        "gauge": False,
        "nondynamical": False,
        "Morse_index_lower_bound": None,
        "exterior_result": "physical verdict unresolved",
        "core_result": "physical verdict unresolved",
        "sheet_map": "sign(X-2)=tau unchanged",
        "sheet_selection_consequence": (
            "no sheet is rejected or certified by the incomplete Einstein-frame reduction"
        ),
        "global_stability": False,
        "result": PHYSICAL_RESULT,
    }


def integrity_ledger() -> dict[str, Any]:
    return {
        "new_action_terms": [],
        "new_primitives": [],
        "measured_inputs": [],
        "tau_J": False,
        "neutral_work": False,
        "next_construction": (
            "derive the scalar radial-shift Green function from the bulk "
            "momentum constraint with the x-dependent B1 moving-endpoint "
            "matching condition, then reconstruct off-shell V_J and F2"
        ),
    }


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "v6_11_head_sha": V611_HEAD_SHA,
        "primary_result": PRIMARY_RESULT,
        "preserved_results": [
            "BHSM_Y_SIGMA_EXP_MINUS_BETA_REJECTED_BY_CANONICAL_NORMALIZATION",
            "BHSM_AVAILABLE_C_BHSM_HAS_ZERO_LIGHT_HEAVY_COUPLING",
            "BHSM_MINIMAL_WELL_POSED_ACTION_HAS_NO_JUNCTION_MIXING_TERM",
            "BHSM_TWO_FOLD_SHEETS_HAVE_OPPOSITE_REDUCED_HESSIAN_SIGN",
        ],
        **GUARDS,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "constraints": {
            **_common("BHSM_fold_radial_ADM_scalar_constraints_v6_12_0"),
            "status": PRIMARY_RESULT,
            "gauge": gauge_ledger(),
            "constraints": adm_constraint_ledger(),
            "exact_checks": {
                "H0": sp.sstr(static_hubble0()),
                "H1": sp.sstr(static_hubble1()),
                "zero_shift_mismatch_plus": sp.sstr(
                    momentum_constraint_zero_shift_mismatch(1)
                ),
                "zero_shift_mismatch_minus": sp.sstr(
                    momentum_constraint_zero_shift_mismatch(-1)
                ),
            },
        },
        "frame": {
            **_common("BHSM_fold_four_dimensional_frame_function_v6_12_0"),
            "status": FRAME_RESULT,
            "frame": frame_ledger(),
            "exact": {
                "one_cap_I0": sp.sstr(one_cap_frame_integral_0()),
                "one_cap_I1": sp.sstr(one_cap_frame_integral_1()),
                "F0": sp.sstr(frame_F0()),
                "F1_plus": sp.sstr(frame_F1(1)),
                "F1_minus": sp.sstr(frame_F1(-1)),
                "F2_functional": sp.sstr(frame_F2_formula()),
                "Omega2_plus": sp.sstr(omega_squared(1)),
                "Omega2_minus": sp.sstr(omega_squared(-1)),
            },
        },
        "jordan": {
            **_common("BHSM_fold_Jordan_moduli_metric_v6_12_0"),
            "status": "BHSM_FOLD_JORDAN_MODULI_METRIC_PARTIALLY_DERIVED",
            "jordan": jordan_moduli_ledger(),
        },
        "einstein": {
            **_common("BHSM_fold_Einstein_frame_kinetic_norm_v6_12_0"),
            "status": PRIMARY_RESULT,
            "einstein": einstein_kinetic_ledger(),
            "Weyl_plus": sp.sstr(weyl_kinetic_at_fold(1)),
            "Weyl_minus": sp.sstr(weyl_kinetic_at_fold(-1)),
        },
        "verdict": {
            **_common("BHSM_fold_physical_mass_and_sheet_verdict_v6_12_0"),
            "status": PHYSICAL_RESULT,
            "potential": potential_ledger(),
            "formal_VE_hessian": sp.sstr(einstein_potential_hessian_formula()),
            "verdict": verdict_ledger(),
        },
        "report": {
            **_common("BHSM_v6_12_0_hidden_input_and_final_report"),
            "status": PRIMARY_RESULT,
            "central_answer": (
                "F0, F1, the Weyl factor, and the positive Weyl kinetic term "
                "are exact. The v6.11 zero-shift tangent violates the momentum "
                "constraint. The missing moving-B1-endpoint scalar-shift "
                "boundary condition prevents a unique constraint inverse and "
                "kinetic sign. The on-shell cusp also does not supply the "
                "off-shell V_J and F2 needed for Einstein-frame masses."
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
