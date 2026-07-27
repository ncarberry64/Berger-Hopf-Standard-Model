"""BHSM v6.13.0 moving-B1-endpoint scalar-shift domain theorem."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import sympy as sp


VERSION = "v6.13.0"
SPRINT = "bhsm-moving-endpoint-shift-domain-v6-13-0"
SOURCE_MAIN_SHA = "39a01dcc877105a41d0dfa145407585d55906756"
V612_HEAD_SHA = "b8d6c1550ade4cb2c86e331f8f74cb001d35b94b"

PRIMARY_RESULT = "BHSM_EXISTING_B1_VARIATION_DOES_NOT_SUPPLY_SHIFT_BOUNDARY_DATA"
KINETIC_RESULT = (
    "BHSM_FOLD_KINETIC_SIGN_REQUIRES_EMBEDDING_VARIATION_OR_SHIFT_DOMAIN"
)

ARTIFACT_FILES = {
    "variation": "BHSM_moving_endpoint_variation_v6_13_0.json",
    "report": "BHSM_v6_13_0_final_report.json",
}

GUARDS = {
    "arbitrary_boundary_condition_added": False,
    "embedding_variation_assumed": False,
    "new_action_term_introduced": False,
    "new_primitive_introduced": False,
    "tau_J_introduced": False,
    "boundary_tension_introduced": False,
    "radion_potential_introduced": False,
    "measured_input_used": False,
    "neutral_work_performed": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
}

# Linear scalar variables at the unperturbed endpoint.
B, ZETA, E_RHO = sp.symbols("B zeta E_rho", real=True)
N0, A0 = sp.symbols("N_0 a_0", real=True, positive=True)
XI_RHO, XI_RHO_D = sp.symbols("xi_rho xi_rho_d", real=True)
PSI, H_RHO = sp.symbols("psi H_rho", real=True)
DELTA_SIGMA, SIGMA_RHO = sp.symbols("delta_sigma sigma_0_rho", real=True)
DELTA_X, X_RHO = sp.symbols("delta_X X_0_rho", real=True)
T, CHI_1 = sp.symbols("t chi_1", real=True, positive=True)


def endpoint_shift_invariant(
    b: sp.Expr = B,
    zeta: sp.Expr = ZETA,
    e_rho: sp.Expr = E_RHO,
) -> sp.Expr:
    """Gauge-invariant scalar normal threading at the endpoint.

    The convention is delta g -> delta g-L_xi g and
    rho_endpoint=rho_J+zeta.  Consequently zeta -> zeta+xi^rho.
    """
    return sp.expand(b + N0**2 * zeta - A0**2 * e_rho)


def transformed_endpoint_variables() -> dict[str, sp.Expr]:
    """Linear transformations under radial and M4 scalar diffeomorphisms."""
    return {
        "B": B - N0**2 * XI_RHO - A0**2 * XI_RHO_D,
        "zeta": ZETA + XI_RHO,
        "E_rho": E_RHO - XI_RHO_D,
        "psi": PSI - H_RHO * XI_RHO,
        "delta_sigma": DELTA_SIGMA - SIGMA_RHO * XI_RHO,
        "delta_X": DELTA_X - X_RHO * XI_RHO,
    }


def transformed_endpoint_shift_invariant() -> sp.Expr:
    transformed = transformed_endpoint_variables()
    return endpoint_shift_invariant(
        transformed["B"], transformed["zeta"], transformed["E_rho"]
    )


def endpoint_conformal_pullback(
    psi: sp.Expr = PSI, zeta: sp.Expr = ZETA
) -> sp.Expr:
    return sp.expand(psi + H_RHO * zeta)


def endpoint_scalar_pullback(
    delta_sigma: sp.Expr = DELTA_SIGMA, zeta: sp.Expr = ZETA
) -> sp.Expr:
    return sp.expand(delta_sigma + SIGMA_RHO * zeta)


def endpoint_curvature_pullback(
    delta_x: sp.Expr = DELTA_X, zeta: sp.Expr = ZETA
) -> sp.Expr:
    return sp.expand(delta_x + X_RHO * zeta)


def zero_shift_mismatch(tau: int) -> sp.Expr:
    """The exact v6.12 momentum-constraint source."""
    if tau not in (-1, 1):
        raise ValueError("tau must be +/-1")
    return sp.simplify(
        -3 * tau * CHI_1 * T / (4 * sp.sin(sp.pi * T / 4) ** 2)
    )


def pullback_ledger() -> dict[str, Any]:
    return {
        "bulk_ADM_metric": (
            "ds5^2=N^2 d rho^2+h_mu_nu(dx^mu+N^mu d rho)"
            "(dx^nu+N^nu d rho)"
        ),
        "embedding": "X^A(x)=(rho_J+zeta(x),x^mu)",
        "induced_metric_exact": (
            "gamma_mu_nu=[h_mu_nu+N_mu D_nu zeta+N_nu D_mu zeta"
            "+(N^2+N_alpha N^alpha)D_mu zeta D_nu zeta]_Sigma"
        ),
        "induced_metric_linear": (
            "delta gamma_mu_nu=delta h_mu_nu+zeta partial_rho h0_mu_nu"
        ),
        "lapse_normal_exact": (
            "N_Sigma=[N^-2+2N^mu D_mu zeta/N^2"
            "+(h^mu_nu+N^mu N^nu/N^2)D_mu zeta D_nu zeta]^-1/2"
        ),
        "lapse_normal_linear": "delta N_Sigma=A+zeta partial_rho N0",
        "relative_shift_one_form": "V_mu=N_mu+N^2 D_mu zeta",
        "scalar_pullback": "sigma_Sigma=sigma0+delta sigma+zeta sigma0'",
        "level_set_normal": "s_A=(1,-D_mu zeta)",
        "unit_normal_linear": (
            "n_A=(N,-N D_mu zeta); "
            "n^mu=-(N^mu+N^2 D^mu zeta)/N"
        ),
        "shift_enters_induced_metric_at": "quadratic derivative order",
    }


def gauge_ledger() -> dict[str, Any]:
    return {
        "convention": (
            "delta g -> delta g-L_xi g, "
            "xi^A=(xi^rho,D^mu xi), rho_Sigma=rho_J+zeta"
        ),
        "transformations": {
            "A": "A-(N0 xi^rho)'",
            "B": "B-N0^2 xi^rho-a0^2 partial_rho xi",
            "psi": "psi-(a0'/a0)xi^rho",
            "E": "E-xi",
            "delta_sigma": "delta_sigma-sigma0' xi^rho",
            "zeta": "zeta+xi^rho|Sigma",
            "delta_X": "delta_X-X0' xi^rho",
        },
        "endpoint_shift_invariant": (
            "S_Sigma=[B+N0^2 zeta-a0^2 partial_rho E]_Sigma"
        ),
        "endpoint_conformal_invariant": (
            "Psi_Sigma=[psi+(a0'/a0)zeta]_Sigma"
        ),
        "endpoint_scalar_invariant": (
            "delta sigma_Sigma=[delta sigma+sigma0' zeta]_Sigma"
        ),
        "endpoint_curvature_invariant": (
            "delta X_Sigma=[delta X+X0' zeta]_Sigma"
        ),
        "delta_X_intrinsic_proof": (
            "radial xi^rho terms cancel in the pullback; an M4 scalar "
            "diffeomorphism acts only by the Lie derivative of background X, "
            "which vanishes for the homogeneous constant-X fold"
        ),
        "fixed_endpoint_gauge": "zeta=0 may be chosen with xi^rho|Sigma=-zeta",
        "longitudinal_gauge": "E=0 may be chosen with xi=E",
        "residual_classification": (
            "S_Sigma is unchanged by both choices and by their residual "
            "transformations; an undetermined S_Sigma trace is not residual gauge"
        ),
    }


def repository_domain_ledger() -> dict[str, Any]:
    return {
        "B1_geometry": (
            "a provisional codimension-one intrinsic M4 boundary/interface; "
            "the Z2 construction uses y=0 and glues two regular caps"
        ),
        "B1_support_in_frozen_action": "fixed boundary domain and fixed embedding iota",
        "metric_ontology": (
            "independent intrinsic h_mu_nu with exact multiplier constraint "
            "h_mu_nu=iota^*g_mu_nu"
        ),
        "rho_J_static_status": (
            "cap length/junction position solved by the homogeneous boundary-value "
            "problem; not promoted to an x-dependent embedding field"
        ),
        "static_transversality": (
            "v6.1.7 includes the one-dimensional moving-upper-limit/domain "
            "shape response along the homogeneous cap family"
        ),
        "v6_11_moving_endpoint": (
            "proper-normal coordinate representation of the same solved domain; "
            "fixed-domain and moving-coordinate descriptions agree after matching "
            "endpoint data"
        ),
        "embedding_varied": False,
        "zeta_action_variable": False,
        "shift_boundary_value_fixed": False,
        "boundary_domains_frozen": True,
    }


def first_variation_ledger() -> dict[str, Any]:
    return {
        "action": "S_P1+S_GHY+S_B1+S_scalar+S_match",
        "P1_GHY_metric_boundary_term": (
            "(1/2) integral_Sigma sqrt|gamma| kappa_1[Q_mu_nu] "
            "delta gamma^mu_nu"
        ),
        "B1_metric_boundary_term": (
            "integral_Sigma sqrt|gamma| "
            "(C_partial G_mu_nu-T_partial,mu_nu/2)delta gamma^mu_nu"
        ),
        "matching": (
            "vary independent g,h,Lambda; impose h=iota^*g; eliminate Lambda"
        ),
        "derived_metric_condition": (
            "kappa_1[Q_mu_nu]+2C_partial G_mu_nu"
            "=T_partial,mu_nu"
        ),
        "longitudinal_junction_identity": (
            "D^mu(kappa_1[Q_mu_nu]+2C_partial G_mu_nu"
            "-T_partial,mu_nu)=-[T_bulk,n nu]"
        ),
        "longitudinal_classification": (
            "Codazzi/Bianchi Ward identity after the bulk momentum constraint; "
            "not an independent endpoint-domain equation for S_Sigma"
        ),
        "bulk_shift_variation": (
            "D_nu(K^nu_mu-delta^nu_mu K)"
            "=kappa_1^-1 Z5(n sigma)D_mu sigma"
        ),
        "bulk_shift_radial_endpoint_term": 0,
        "reason_no_shift_endpoint_term": (
            "the ADM shift enters K_mu_nu through tangential derivatives and "
            "has no radial derivative; at fixed embedding gamma_mu_nu=h_mu_nu, "
            "so GHY, B1, scalar Dirichlet data, and S_match contain no "
            "independent delta S_Sigma"
        ),
        "scalar_endpoint_term": (
            "-Z5 integral_Sigma sqrt|gamma| (n sigma)delta sigma; "
            "the wall problem fixes delta sigma_Sigma=0"
        ),
        "embedding_variation": (
            "absent; if it were declared, tangential displacement gives the "
            "Codazzi/Ward momentum balance and normal displacement gives a "
            "shape equation, neither present in the frozen variational domain"
        ),
        "x_dependent_embedding_variation": False,
        "coefficient_of_free_delta_S_Sigma": None,
        "endpoint_condition": None,
        "condition_classification": "absent because embedding/threading data are not varied",
        "junction_is_shift_boundary_condition": False,
        "result": PRIMARY_RESULT,
    }


def boundary_data_ledger() -> dict[str, Any]:
    return {
        "fixed": [
            "B1 support/domain and embedding iota",
            "bulk and B1 action coefficients",
            "topology, Z2 gluing, and normal orientation",
            "bulk scalar Dirichlet trace sigma_Sigma=0",
        ],
        "freely_varied": [
            "bulk metric and independent intrinsic metric before matching",
            "metric matching multiplier Lambda",
            "bulk radial shift in the interior as a constraint multiplier",
        ],
        "constrained": [
            "h_mu_nu=iota^*g_mu_nu",
            "bulk Hamiltonian and momentum constraints",
            "metric junction condition",
            "a_Sigma=1 and the stored scalar-wall junction traces",
        ],
        "gauge": [
            "radial coordinate displacement zeta used to represent the fixed support",
            "longitudinal scalar E",
        ],
        "physically_dynamical": [
            "constraint-reduced bulk fields",
            "intrinsic B1 metric/connection/scalar sectors in their declared domain",
        ],
        "unspecified": [
            "gauge-invariant endpoint threading S_Sigma",
            "a variational rule for x-dependent embedding deformations",
        ],
        "radion_status": (
            "not established: zeta is not an independent action variable, while "
            "S_Sigma is gauge invariant but lacks boundary-domain data"
        ),
    }


def constraint_and_kinetic_ledger() -> dict[str, Any]:
    return {
        "source": (
            "J_shift(t)=-3 tau chi_1 t/[4 sin^2(pi t/4)]"
        ),
        "endpoint_condition_derived": False,
        "L_C_constructed": False,
        "differential_order": None,
        "pole_regularity": "known but insufficient without endpoint domain",
        "endpoint_condition": None,
        "kernel": None,
        "adjoint_kernel": None,
        "solvability_condition": None,
        "homogeneous_trace": (
            "S_Sigma is not residual gauge, but cannot be called a physical "
            "radion or zero mode without an embedding/domain variational rule"
        ),
        "Green_operator_constructed": False,
        "Green_operator_exists": None,
        "pseudoinverse_used": False,
        "K_shift_endpoint_red": None,
        "preserved": {
            "F0_equals_M4_squared": "pi/2",
            "K_scalar": ">=2>0",
            "K_Weyl": "3 chi_1^2(4-pi)^2/(16 pi)>0",
            "k_q_E": "K_scalar+K_shift_endpoint_red+K_Weyl",
        },
        "k_q_E": None,
        "kinetic_sign": None,
        "physical_masses_calculated": False,
        "exact_next_input": (
            "declare from the existing theory whether iota is fixed or freely "
            "varied for x-dependent deformations and, if varied, supply its "
            "action-derived shape/momentum domain; otherwise specify an "
            "action-derived boundary threading domain for S_Sigma"
        ),
        "result": KINETIC_RESULT,
    }


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "v6_12_head_sha": V612_HEAD_SHA,
        "primary_result": PRIMARY_RESULT,
        **GUARDS,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "variation": {
            **_common("BHSM_moving_endpoint_variation_v6_13_0"),
            "status": PRIMARY_RESULT,
            "pullback": pullback_ledger(),
            "gauge": gauge_ledger(),
            "repository_domain": repository_domain_ledger(),
            "first_variation": first_variation_ledger(),
            "boundary_data": boundary_data_ledger(),
            "exact": {
                "endpoint_shift_invariant": sp.sstr(endpoint_shift_invariant()),
                "transformed_endpoint_shift": sp.sstr(
                    transformed_endpoint_shift_invariant()
                ),
                "mismatch_plus": sp.sstr(zero_shift_mismatch(1)),
                "mismatch_minus": sp.sstr(zero_shift_mismatch(-1)),
            },
        },
        "report": {
            **_common("BHSM_v6_13_0_final_report"),
            "status": KINETIC_RESULT,
            "central_answer": (
                "The frozen P1+GHY+B1+scalar variational problem varies the "
                "matched induced metrics on a fixed B1 embedding. It derives the "
                "junction tensor and the bulk momentum constraint, but no term "
                "proportional to a free variation of the gauge-invariant endpoint "
                "threading S_Sigma. Therefore no endpoint condition, unique "
                "constraint operator, Green function, Schur correction, or total "
                "Einstein-frame kinetic sign follows."
            ),
            "constraint_and_kinetic": constraint_and_kinetic_ledger(),
            "boundary_data": boundary_data_ledger(),
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
