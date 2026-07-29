"""BHSM v6.30.5 fixed-h Lyapunov--Schmidt effective potential.

The strict D0 family fixes the independent four-metric and its curvature.
The Hamiltonian constraint is solved algebraically in areal gauge, the
scalar complement is inverted on the exact Dirichlet spectral complement,
and the remaining nonlinear residual is retained as the reduced force.

The module deliberately separates a radial exact branch (reduced force
zero) from a reduced effective family (complement residual zero).
"""

from __future__ import annotations

from functools import lru_cache
import json
import math
from pathlib import Path
from typing import Any, Callable

import numpy as np
from scipy.integrate import quad, solve_bvp, solve_ivp

from bhsm.interface import fixed_h_variational_family_solvability as v6304


VERSION = "v6.30.5"
SPRINT = "bhsm-fixed-h-lyapunov-schmidt-potential-v6-30-5"
SOURCE_MAIN_SHA = "7c8b8b7496732e7f7cf227279563cb9962299b50"
PARENT_SCIENTIFIC_SHAS = {
    "v6.30.2": "0d72d9ab14d203cb7a5dd7c12733824d56d563c7",
    "v6.30.3": "394c59bf4cb4fbb3a47c0aacf3a97ab8f9f16ff4",
    "v6.30.4": "5841d7e9298793126e03c71e828d2ba01945bc0d",
    "v6.30.4_serialization_fix": (
        "c59e724de309cfb83116ed246011e37e28496776"
    ),
}
ACTION_DOMAIN = "frozen P1+GHY+scalar+B1+matcher action; strict D0"
TAYLOR = "Phi(q)=sum_n q^n Phi_n/n!"

EXACT_RESULT = (
    "BHSM_STRICT_FIXED_H_EXACT_ON_SHELL_BRANCH_BLOCKED_AT_THIRD_ORDER_"
    "IN_THE_STABLE_WALL_SIGN_DOMAIN"
)
REDUCED_RESULT = (
    "BHSM_FIXED_H_REDUCED_POTENTIAL_FIRST_NONZERO_INTERACTION_DERIVED"
)
STABILITY_RESULT = (
    "BHSM_FIXED_H_QUARTIC_LOCAL_MINIMUM_IN_THE_STABLE_WALL_SIGN_DOMAIN"
)
SCALE_RESULT = (
    "BHSM_SCALE_BRIDGE_PHASE_NOT_PERMITTED_WITH_UNSELECTED_G5"
)
PRIMARY_RESULT = REDUCED_RESULT

ARTIFACT_FILES = {
    "projectors": "BHSM_fixed_h_KKT_projectors_v6_30_5.json",
    "amplitude": "BHSM_fixed_h_amplitude_coordinate_v6_30_5.json",
    "source3": "BHSM_fixed_h_third_order_source_v6_30_5.json",
    "noether3": (
        "BHSM_fixed_h_third_order_Noether_compatibility_v6_30_5.json"
    ),
    "projection3": (
        "BHSM_fixed_h_third_order_kernel_projection_v6_30_5.json"
    ),
    "phi3": "BHSM_fixed_h_Phi3_complement_v6_30_5.json",
    "source4": "BHSM_fixed_h_fourth_order_source_v6_30_5.json",
    "phi4": "BHSM_fixed_h_Phi4_complement_v6_30_5.json",
    "action": "BHSM_fixed_h_reduced_action_identity_v6_30_5.json",
    "jordan": "BHSM_fixed_h_Jordan_coefficients_v6_30_5.json",
    "einstein": "BHSM_fixed_h_Einstein_coefficients_v6_30_5.json",
    "canonical": "BHSM_fixed_h_canonical_interaction_v6_30_5.json",
    "stability": "BHSM_fixed_h_local_stability_v6_30_5.json",
    "exact": "BHSM_fixed_h_exact_branch_permission_v6_30_5.json",
    "scale": "BHSM_scale_phase_permission_v6_30_5.json",
}

GUARDS = {
    "measured_input_used": False,
    "empirical_inverse_used": False,
    "empirical_generation_basis_used": False,
    "fitted_parameter_used": False,
    "new_action_introduced": False,
    "new_primitive_introduced": False,
    "free_control_coefficient_introduced": False,
    "new_scale_introduced": False,
    "vacuum_constant_subtracted": False,
    "mu_varied_with_q": False,
    "curvature_varied_in_D0": False,
    "q_dependent_regulator_used": False,
    "M4_metric_equation_imposed_before_extraction": False,
    "historical_D2_coefficient_imported": False,
    "Robin_inverse_used": False,
    "generic_pseudoinverse_used": False,
    "kernel_row_deleted": False,
    "historical_artifact_rewritten": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "physical_mass_claimed": False,
    "global_stability_claimed": False,
}

MU = 29.430918352947562
M4 = 21.690130229412136
C_GRAV = 394.70598844295543
G3_GAMMA = 130.14078137647281
G3_ZETA = 2368.2359306577326
EXACT_BRANCH_RATIO = -18.19749278903491
F0 = math.pi / 2
RC = 24.0
F2_Z = -6.938766957338083
F4_ZZ = 237.5402652381
F4_G = 5.0978230687
K0 = 6.673443432880105
VE4_GAMMA_Z = 260.28156275294563
VE4_Z2_OVER_KAPPA = 3633.0356624841
STABILITY_THRESHOLD = -13.95809839182684
CANONICAL_G_OVER_Z2 = 5.84444718718846
CANONICAL_INV_KAPPA = 81.5773688846122


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def stable(value: float, digits: int = 14) -> float:
    if abs(value) < 5.0e-14:
        return 0.0
    return float(f"{value:.{digits}g}")


def projector_scalar(coefficient: float) -> tuple[float, float]:
    """Return scalar amplitudes of P and Q for X=c*u1+X_perp."""

    return coefficient, 0.0


def projector_identities() -> dict[str, bool]:
    """Exact coefficient algebra; the perpendicular component is implicit."""

    return {
        "P2_equals_P": True,
        "Q2_equals_Q": True,
        "PQ_zero": True,
        "QP_zero": True,
    }


def projector_ledger() -> dict[str, Any]:
    return {
        "KKT_field_order": ["A", "psi", "delta_sigma", "eta_tr"],
        "kernel": "Phi1=(0,0,u1,0)",
        "adjoint_kernel": "Phi1_dagger=(0,0,u1,0)",
        "pairing": (
            "integral_0^(pi/4) 4 sin(rho)^4 u1 X_sigma d rho "
            "plus the extended endpoint saddle pairing"
        ),
        "normalization_N": 1,
        "normalization_proof": (
            "the inherited per-cap mode normalization is "
            "integral 4 sin(rho)^4 u1^2 d rho=1; endpoint contribution "
            "vanishes because Phi1 has eta=0 and u1(pi/4)=0"
        ),
        "P": "P X=Phi1 <Phi1_dagger,X>_KKT",
        "Q": "I-P",
        "identities": projector_identities(),
        "domain_preservation": {
            "regular_pole": True,
            "scalar_Dirichlet": True,
            "fixed_h_trace": True,
            "gauge": True,
            "matcher_reaction": True,
            "reason": (
                "u1 is regular, Dirichlet, pure scalar, and has zero reaction"
            ),
        },
        "implementation_warning": (
            "no row is deleted and no Euclidean dot product or "
            "pseudoinverse is used"
        ),
    }


def amplitude_ledger() -> dict[str, Any]:
    return {
        "definition": (
            "<Phi1_dagger,Phi(q)-Phi0>_KKT=q and "
            "P(Phi(q)-Phi0)=q Phi1"
        ),
        "higher_orders": "P Phi_n=0 for every n>=2",
        "scalar_equivalent": (
            "integral 4 sin(rho)^4 u1 delta_sigma(q,rho)d rho=q"
        ),
        "equivalence_proof": (
            "Phi1 and Phi1_dagger have only a scalar component and their "
            "KKT endpoint pairing vanishes"
        ),
        "coordinate_only": True,
        "action_multiplier_added": False,
        "reflection": "q->-q at fixed tau",
        "allowed_reparameterization": (
            "none after the exact phase condition and fixed Phi1 "
            "normalization; odd trial changes would violate the condition"
        ),
    }


def third_order_source_ledger() -> dict[str, Any]:
    return {
        "factorial_equation": "mathbb L_D Phi3=S3",
        "definitions": {
            "gamma": "G5/Z5",
            "zeta": "Z5/kappa1",
            "A2": (
                "-zeta tan(rho)^2[u1'^2+mu_c u1^2]/12"
            ),
            "r3": (
                "gamma u1^3-mu_c A2 u1+(A2'/2)u1'"
            ),
        },
        "components": {
            "Hamiltonian": "0 by scalar reflection after inserting Phi2",
            "tangential_Einstein": (
                "0 at odd order; its first reduced-force Noether completion "
                "appears at order four"
            ),
            "scalar": "S3_sigma=-6 r3",
            "matcher_trace": "0",
            "matcher_reaction": "0 at odd order",
        },
        "term_ledger": [
            {
                "term": "-6 (G5/Z5) u1^3",
                "origin": "-N a^4 G5 sigma^4/4",
                "parity": "odd residual",
                "bulk_or_boundary": "bulk",
                "cap_sign": "same on both caps",
                "survives_projection": True,
            },
            {
                "term": "+6 mu_c A2 u1",
                "origin": "quadratic potential times lapse response",
                "parity": "odd residual",
                "bulk_or_boundary": "bulk",
                "cap_sign": "same on both caps",
                "survives_projection": True,
            },
            {
                "term": "-3 A2' u1'",
                "origin": "scalar kinetic radial-measure/lapse response",
                "parity": "odd residual",
                "bulk_or_boundary": "bulk",
                "cap_sign": "same on both caps",
                "survives_projection": True,
            },
            {
                "term": "0",
                "origin": (
                    "GHY+B1+matcher: fixed trace, u1(B1)=0, "
                    "Phi1_dagger has zero reaction component"
                ),
                "parity": "odd",
                "bulk_or_boundary": "boundary",
                "cap_sign": "orientation terms cancel or vanish capwise",
                "survives_projection": False,
            },
        ],
        "eta2_included": (
            "eta2 is retained in the full KKT vector; it contributes no "
            "order-three scalar boundary term because u1(B1)=0 and the "
            "adjoint kernel has zero matcher component"
        ),
    }


def noether_ledger() -> dict[str, Any]:
    return {
        "off_shell_identity": "a' E_a+sigma' E_sigma-N(E_N)'=0",
        "derivation_order": "lapse retained before areal gauge",
        "order_three": {
            "Hamiltonian": "S3_N=0",
            "tangential": "S3_a=0",
            "scalar": "S3_sigma=-6 r3",
            "compatibility": (
                "at source order three sigma0'=0, so the scalar source "
                "does not enter the order-three Noether coefficient"
            ),
        },
        "nonlinear_cokernel_representative": (
            "Xi(Phi): E_N=0, E_sigma=xi_sigma, "
            "E_a=-(sigma'/a')xi_sigma, with matcher completion zero"
        ),
        "base_limit": "Xi(Phi0)=Phi1 residual representative",
        "order_four_completion": (
            "the q^3 scalar reduced force produces the q^4 tangential "
            "residual required by E_a=-(sigma'/a')E_sigma"
        ),
        "why_fixed_Q_is_not_row_deletion": (
            "the constant KKT projector fixes the amplitude and scalar "
            "complement; the exact field-dependent primal residual map Xi "
            "restores the dependent Noether component"
        ),
        "pole_regular": True,
        "cap_regular": True,
        "matcher_trace_compatible": True,
        "endpoint_reaction_compatible": True,
        "gauge_compatible": True,
        "result": "BHSM_FIXED_H_THIRD_ORDER_NOETHER_COMPATIBILITY_DERIVED",
    }


def projection_formula() -> dict[str, Any]:
    return {
        "C": (
            "(G5/Z5) M4+(Z5/kappa1) C_grav"
        ),
        "M4": M4,
        "C_grav": C_GRAV,
        "Omega3": (
            "-6 C = -130.140781376472814...(G5/Z5)"
            "-2368.235930657732552...(Z5/kappa1)"
        ),
        "g_convention": "g(q)=g3 q^3/3!+O(q^5)",
        "g3": (
            "130.140781376472814...(G5/Z5)"
            "+2368.235930657732552...(Z5/kappa1)=-Omega3"
        ),
        "exact_zero_condition": (
            "G5/Z5=-18.1974927890349085...(Z5/kappa1)"
        ),
        "stable_wall_sign": (
            "G5>0,Z5>0,kappa1>0 implies Omega3<0 and g3>0"
        ),
        "exact_branch": EXACT_RESULT,
        "reduced_family": REDUCED_RESULT,
    }


def _mode_functions() -> tuple[
    float, float, Callable[[Any], Any], Callable[[Any], Any]
]:
    mu, norm, raw = v6304._shooting_mode(max_step=0.001, rtol=1.0e-12)

    def u(x: Any) -> Any:
        values = np.asarray(x)
        if values.ndim == 0:
            return norm * raw(float(values))
        return np.array([norm * raw(float(v)) for v in values])

    def du(x: Any) -> Any:
        values = np.asarray(x)
        if values.ndim == 0:
            return norm * raw(float(values), 1)
        return np.array([norm * raw(float(v), 1) for v in values])

    return mu, norm, u, du


@lru_cache(maxsize=1)
def numerical_diagnostics() -> dict[str, Any]:
    """Two-route projection and complement diagnostics.

    Shooting constructs the regular particular solution and removes its
    exact kernel component.  Augmented collocation independently solves for
    the Fredholm projection and the orthogonality condition.
    """

    endpoint = math.pi / 4
    pole = 1.0e-6
    mu, norm, u, du = _mode_functions()

    def weight(x: Any) -> Any:
        return 4 * np.sin(x) ** 4

    def abar(x: Any) -> Any:
        values = np.asarray(x)
        result = -np.tan(values) ** 2 * (
            du(values) ** 2 + mu * u(values) ** 2
        ) / 12
        return np.where(values == 0, 0.0, result)

    def d_abar(x: Any) -> Any:
        values = np.asarray(x)
        energy = du(values) ** 2 + mu * u(values) ** 2
        result = -(
            2 * np.tan(values) / np.cos(values) ** 2 * energy
            - 8 * np.tan(values) * du(values) ** 2
        ) / 12
        return np.where(values == 0, 0.0, result)

    def r_g(x: Any) -> Any:
        return u(x) ** 3

    def r_z(x: Any) -> Any:
        return -mu * abar(x) * u(x) + d_abar(x) * du(x) / 2

    projections = [
        quad(
            lambda x: float(weight(x) * u(x) * source(x)),
            0,
            endpoint,
            epsabs=2.0e-9,
            limit=300,
        )[0]
        for source in (r_g, r_z)
    ]

    def shooting_response(
        source: Callable[[Any], Any], projection: float
    ) -> tuple[Callable[[Any], Any], Callable[[Any], Any], float, float]:
        f0 = 6 * (float(source(0)) - projection * float(u(0)))

        def rhs(x: float, state: list[float]) -> list[float]:
            return [
                state[1],
                -4 / math.tan(x) * state[1]
                - mu * state[0]
                + 6 * (float(source(x)) - projection * float(u(x))),
            ]

        solution = solve_ivp(
            rhs,
            (pole, endpoint),
            [f0 * pole**2 / 10, f0 * pole / 5],
            rtol=3.0e-10,
            atol=3.0e-12,
            max_step=0.001,
            dense_output=True,
        )
        inner = quad(
            lambda x: float(
                weight(x)
                * u(x)
                * solution.sol(max(x, pole))[0]
            ),
            0,
            endpoint,
            epsabs=2.0e-7,
            limit=300,
        )[0]

        def value(x: Any) -> Any:
            values = np.asarray(x)
            return solution.sol(np.maximum(values, pole))[0] - inner * u(
                values
            )

        def derivative(x: Any) -> Any:
            values = np.asarray(x)
            return solution.sol(np.maximum(values, pole))[1] - inner * du(
                values
            )

        return value, derivative, float(solution.y[0, -1]), inner

    shot_g = shooting_response(r_g, projections[0])
    shot_z = shooting_response(r_z, projections[1])
    mesh = np.linspace(pole, endpoint, 250)

    def collocation(
        source: Callable[[Any], Any], guess: float
    ) -> Any:
        def rhs(x: Any, state: Any, parameter: Any) -> Any:
            return np.vstack(
                (
                    state[1],
                    -4 / np.tan(x) * state[1]
                    - mu * state[0]
                    + 6 * (source(x) - parameter[0] * u(x)),
                    weight(x) * u(x) * state[0],
                )
            )

        def boundary(left: Any, right: Any, parameter: Any) -> Any:
            f0 = 6 * (
                float(source(0)) - parameter[0] * float(u(0))
            )
            return np.array(
                [
                    left[1] - f0 * pole / 5,
                    right[0],
                    left[2],
                    right[2],
                ]
            )

        return solve_bvp(
            rhs,
            boundary,
            mesh,
            np.zeros((3, len(mesh))),
            p=np.array([guess]),
            tol=2.0e-5,
            max_nodes=5000,
        )

    bvp_g = collocation(r_g, projections[0])
    bvp_z = collocation(r_z, projections[1])
    nodes = np.linspace(pole, endpoint, 101)
    differences = [
        float(np.max(np.abs(shot[0](nodes) - bvp.sol(nodes)[0])))
        for shot, bvp in ((shot_g, bvp_g), (shot_z, bvp_z))
    ]
    bounds = {
        "M4_projection_difference": 2.0e-7,
        "C_grav_projection_difference": 2.0e-5,
        "Phi3_G_profile_difference": 2.0e-7,
        "Phi3_grav_profile_difference": 2.0e-5,
        "shooting_endpoint_residual": 2.0e-9,
        "orthogonality_residual": 2.0e-8,
    }
    observed = {
        "M4_projection_difference": abs(projections[0] - bvp_g.p[0]),
        "C_grav_projection_difference": abs(projections[1] - bvp_z.p[0]),
        "Phi3_G_profile_difference": differences[0],
        "Phi3_grav_profile_difference": differences[1],
        "shooting_endpoint_residual": max(
            abs(shot_g[2]), abs(shot_z[2])
        ),
        "orthogonality_residual": max(
            abs(
                quad(
                    lambda x: float(weight(x) * u(x) * shot[0](x)),
                    0,
                    endpoint,
                )[0]
            )
            for shot in (shot_g, shot_z)
        ),
    }
    for key, value in observed.items():
        if not value < bounds[key]:
            raise RuntimeError(f"{key}={value} exceeds {bounds[key]}")

    def a4(x: float, gamma: float, zeta: float) -> float:
        if x == 0:
            return 0.0
        sigma3 = gamma * float(shot_g[0](x)) + zeta * float(
            shot_z[0](x)
        )
        dsigma3 = gamma * float(shot_g[1](x)) + zeta * float(
            shot_z[1](x)
        )
        h0 = 1 / math.tan(x)
        ux = float(u(x))
        dux = float(du(x))
        a2 = zeta * float(abar(x))
        p2 = zeta * dux**2 / (12 * h0**2)
        p4 = zeta * dux * dsigma3 / (36 * h0**2)
        d2 = zeta * mu * ux**2 / (12 * h0**2)
        d4 = (
            zeta * mu * ux * sigma3 / (36 * h0**2)
            - gamma * zeta * ux**4 / (24 * h0**2)
        )
        return 12 * (d2**2 - d4 + p2 * d2 - p4 - a2**2 / 4)

    def f4(gamma: float, zeta: float) -> float:
        return quad(
            lambda x: 4 * math.sin(x) ** 2 * a4(x, gamma, zeta),
            0,
            endpoint,
            epsabs=2.0e-6,
            limit=300,
        )[0]

    f4_zz = f4(0, 1)
    f4_g = f4(1, 1) - f4_zz
    a4_zz = a4(endpoint, 0, 1)
    a4_g = a4(endpoint, 1, 1) - a4_zz
    a2_endpoint = float(abar(endpoint))
    return {
        "methods": [
            "adaptive regular-pole shooting plus Gauss-Kronrod projection",
            "augmented Dirichlet collocation solving the Fredholm coefficient",
        ],
        "precision": {
            "shooting_rtol": 3.0e-10,
            "collocation_tol": 2.0e-5,
            "profile_nodes": 101,
        },
        "mu": stable(mu),
        "normalization": stable(norm),
        "projection": {
            "M4": stable(projections[0]),
            "C_grav": stable(projections[1]),
        },
        "Phi3": {
            "formula": (
                "sigma3=(G5/Z5)sigma3_G+(Z5/kappa1)sigma3_grav"
            ),
            "regular_pole": True,
            "Dirichlet_endpoint": True,
            "KKT_orthogonal": True,
        },
        "fourth_order": {
            "F4_Z5_squared_over_kappa1": stable(f4_zz, 12),
            "F4_G5": stable(f4_g, 12),
            "A4_endpoint_zeta_squared": stable(a4_zz, 12),
            "A4_endpoint_gamma_zeta": stable(a4_g, 12),
            "eta4_Z5_squared_over_kappa1": stable(
                -24 * a4_zz + 144 * a2_endpoint**2, 12
            ),
            "eta4_G5": stable(-24 * a4_g, 12),
        },
        "agreement": {
            "serialization_policy": (
                "certified cross-platform bounds are serialized instead "
                "of raw observed last-bit differences"
            ),
            **{
                key: {"relation": "<", "certified_upper_bound": value}
                for key, value in bounds.items()
            },
        },
    }


def phi3_ledger() -> dict[str, Any]:
    return {
        "equation": (
            "(d^2+4 cot(rho)d+mu_c)sigma3=6 Q r3"
        ),
        "solution": (
            "sigma3=(G5/Z5)sigma3_G+(Z5/kappa1)sigma3_grav"
        ),
        "Phi3_perp": ["0", "0", "sigma3", "0"],
        "boundary_conditions": [
            "sigma3'(0)=0 regular pole",
            "sigma3(pi/4)=0",
            "integral 4 sin^4(rho)u1 sigma3=0",
        ],
        "inverse": (
            "exact v6.30.2 Dirichlet scalar complement inverse with gap "
            "64.0147366689857; no pseudoinverse"
        ),
        "diagnostics": numerical_diagnostics(),
        "result": (
            "BHSM_FIXED_H_LYAPUNOV_SCHMIDT_FAMILY_CONSTRUCTED_THROUGH_"
            "THIRD_ORDER"
        ),
    }


def fourth_order_ledger() -> dict[str, Any]:
    return {
        "exact_constraint": (
            "N^2=[6 kappa1 H0^2-Z5 sigma'^2/2]/"
            "[6 kappa1 H0^2-U5(sigma)]"
        ),
        "expansion": {
            "p2": "Z5 u1'^2/(12 kappa1 H0^2)",
            "p4": "Z5 u1' sigma3'/(36 kappa1 H0^2)",
            "d2": "Z5 mu_c u1^2/(12 kappa1 H0^2)",
            "d4": (
                "Z5 mu_c u1 sigma3/(36 kappa1 H0^2)"
                "-G5 u1^4/(24 kappa1 H0^2)"
            ),
            "B4": "d2^2-d4+p2 d2-p4",
            "A4": "12[B4-A2^2/4]",
        },
        "S4_components": {
            "Hamiltonian": (
                "the exact q^4 coefficient solved algebraically by A4"
            ),
            "tangential_Einstein": (
                "Noether completion E_a=-(sigma'/a')E_sigma of the "
                "q^3 reduced scalar force"
            ),
            "scalar": "0 by reflection",
            "matcher_trace": "0 recursively at fixed h",
            "matcher_reaction": "eta4=-24 kappa1 A4_J+144 kappa1 A2_J^2",
        },
        "Omega4": 0,
        "Omega4_reason": "even action implies odd force; no q^4 force term",
        "cap_orientation": (
            "constraint and reaction are cap-even; scalar is cap-odd and "
            "vanishes at this order"
        ),
        "Noether_compatible": True,
    }


def phi4_ledger() -> dict[str, Any]:
    diagnostics = numerical_diagnostics()["fourth_order"]
    return {
        "Phi4_perp": ["A4", "0", "0", "eta4"],
        "P_Phi4": 0,
        "A4": (
            "12[d2^2-d4+p2 d2-p4-A2^2/4]"
        ),
        "psi4": 0,
        "sigma4": 0,
        "eta4": "-24 kappa1 A4(pi/4)+144 kappa1 A2(pi/4)^2",
        "coefficients": diagnostics,
        "regular_pole": "A4=O(rho^2)",
        "fixed_h_endpoint": "psi4(pi/4)=sigma4(pi/4)=0",
        "matcher_recurrence": True,
        "complement_residual": (
            "zero after the field-dependent Noether cokernel completion"
        ),
        "result": (
            "BHSM_FIXED_H_LYAPUNOV_SCHMIDT_FAMILY_CONSTRUCTED_THROUGH_"
            "FOURTH_ORDER"
        ),
    }


def action_identity_ledger() -> dict[str, Any]:
    return {
        "definition": "Gamma_red(q)=Gamma[Phi(q)] at fixed h and R_c",
        "exact_derivative": (
            "Gamma_red'=J(q)g(q), "
            "J(q)=-2 Z5 integral a0^4 u1 sigma_q/N d rho"
        ),
        "factor_two": "two identical caps",
        "J_parity": "even",
        "J0": "-2 Z5",
        "J2": (
            "2 Z5 integral a0^4 A2 u1^2 d rho="
            "-28.8076655430488 Z5^2/kappa1"
        ),
        "why_Phi3_drops_from_J2": "<u1,sigma3>_KKT=0",
        "force": "g(q)=g3 q^3/3!+O(q^5)",
        "action": "Gamma_red=Gamma0+Gamma4 q^4/4!+O(q^6)",
        "identity": "Gamma4=J0 g3=-2 Z5 g3=2 Z5 Omega3",
        "direct_action_crosscheck": {
            "direct_scalar_quartic": "-12 G5 M4",
            "lapse_relaxation": "-12 Z5 (Z5/kappa1) C_grav",
            "sum": "-2 Z5 g3",
            "agreement": "exact coefficient identity",
        },
        "included_boundaries": (
            "GHY already performs the radial integration-by-parts "
            "cancellation; fixed B1 and matcher trace variations vanish; "
            "reaction/canonical endpoint terms cancel in the KKT pairing"
        ),
        "reduced_family_not_exact_branch": True,
    }


def jordan_ledger() -> dict[str, Any]:
    diagnostics = numerical_diagnostics()["fourth_order"]
    return {
        "density": "sqrt(-h)[F(q)R_c/2-V_J(q)]",
        "R_c": 24,
        "F0": "pi/2",
        "F1": 0,
        "F2": "-6.9387669573380825... Z5",
        "F4": (
            f"{diagnostics['F4_Z5_squared_over_kappa1']} Z5^2/kappa1"
            f"+{diagnostics['F4_G5']} G5"
        ),
        "Gamma2": 0,
        "Gamma4": "-2 Z5 g3",
        "VJ0": "symbolic and unsubtracted",
        "VJ1": 0,
        "VJ2": "12 F2",
        "VJ3": 0,
        "VJ4": "12 F4+2 Z5 g3",
        "extraction_order": (
            "F and V_J extracted before imposing the M4 metric equation"
        ),
        "dependency_graph": {
            "F2": ["Phi2"],
            "F4": ["Phi2", "Phi3", "Phi4 lapse"],
            "Gamma4": ["Phi1", "Phi2", "stationarity; Phi4 cancels"],
            "VJ4": ["F4", "Gamma4"],
        },
        "historical_D2_F1_used": False,
    }


def einstein_ledger() -> dict[str, Any]:
    return {
        "definition": "V_E=(F0/F)^2 V_J",
        "raw_fixed_h_coefficients": {
            "VE1": 0,
            "VE2": "F2[12-2 VJ0/F0]",
            "VE3": 0,
            "VE4": (
                "VJ4-12(F2/F0)VJ2"
                "-2(F4/F0)VJ0+18(F2/F0)^2 VJ0"
            ),
        },
        "background_M4_stationarity_applied_after_extraction": (
            "VJ0=R_c F0/4=6 F0; no subtraction"
        ),
        "same_family_null_hessian": {
            "VE1": 0,
            "VE2": 0,
            "source": "D0 coefficients plus q=0 M4 stationarity",
            "historical_D2_F1_used": False,
        },
        "first_nonzero": {
            "order": 4,
            "VE4": (
                "-Gamma4-36 F2^2/F0="
                "260.281562752946 G5"
                "+3633.0356624841 Z5^2/kappa1"
            ),
            "simplified": (
                "260.281562752946 G5+"
                "3633.0356624841 Z5^2/kappa1"
            ),
            "positive_condition": (
                "G5/Z5>-13.95809839182684 Z5/kappa1"
            ),
        },
        "reflection": "VE is even and independent of tau",
    }


def canonical_ledger() -> dict[str, Any]:
    return {
        "same_domain_kinetic": {
            "k0": K0,
            "formula": "2 Z5 integral_0^1 N0 a0^2 u1^2 dt",
            "representative_normalization": "Z5=1",
            "positive": True,
            "why_historical_value_rejected": (
                "6.935084858283065 contains D2 first-order "
                "threading/Weyl contributions; D0 Phi1 is pure scalar"
            ),
            "frame_contribution_at_q0": 0,
        },
        "canonical_map": {
            "kE": "k0+k2 q^2/2+O(q^4)",
            "phi_of_q": (
                "sqrt(k0)q+k2 q^3/(12 sqrt(k0))+O(q^5)"
            ),
            "q_of_phi": (
                "phi/sqrt(k0)-k2 phi^3/(12 k0^(5/2))+O(phi^5)"
            ),
            "k2_status": (
                "not needed for the first quartic interaction because "
                "VE2=VE3=0"
            ),
        },
        "first_interaction": {
            "order": 4,
            "g4": "VE4/k0^2",
            "general_formula": (
                "5.84444718718846 G5/Z5^2+"
                "81.5773688846122/kappa1"
            ),
            "Z5_equals_kappa1_equals_1_representative": (
                "5.84444718718846 G5+81.5773688846122"
            ),
            "dimensionless": True,
            "physical_mass_claimed": False,
            "tau_dependence": "none",
            "reflection": "even",
        },
        "coordinate_invariance": (
            "the exact phase condition removes odd amplitude "
            "reparameterizations; independently, the order and sign of the "
            "first nonzero canonical derivative are invariant"
        ),
        "reduced_force_crosscheck": "g4=VE4/k0^2 using Gamma4=-2 Z5 g3",
    }


def stability_ledger() -> dict[str, Any]:
    return {
        "quadratic": 0,
        "cubic": 0,
        "quartic": (
            "g4=5.84444718718846 G5/Z5^2+"
            "81.5773688846122/kappa1"
        ),
        "classification": {
            "stable_wall_G5_positive": "strict local quartic minimum",
            "threshold": (
                "minimum above, maximum below, higher-order flat at "
                "G5/Z5=-13.95809839182684 Z5/kappa1"
            ),
            "frozen_repository_unconditional": (
                "undetermined because the frozen action leaves G5 "
                "sign and magnitude unselected"
            ),
        },
        "conditional_result": STABILITY_RESULT,
        "global_stability": False,
        "forbidden": [
            "physical particle mass",
            "global or nonperturbative stability",
            "vacuum uniqueness",
            "tunneling lifetime",
            "phenomenological viability",
        ],
    }


def exact_permission_ledger() -> dict[str, Any]:
    return {
        "Omega3": projection_formula()["Omega3"],
        "zero_condition": projection_formula()["exact_zero_condition"],
        "stable_wall_sign_domain": {
            "Omega3_nonzero": True,
            "exact_branch_continues": False,
            "result": EXACT_RESULT,
        },
        "unselected_G5": (
            "the parameterized frozen action admits one algebraic "
            "third-order cancellation value; no repository theorem selects it"
        ),
        "generic_exact_branch": "blocked at third order",
        "reduced_effective_family": "constructed through fourth order",
        "continuous_family_of_exact_vacua_claimed": False,
    }


def scale_permission_ledger() -> dict[str, Any]:
    return {
        "v6_30_5_scientific_closure": True,
        "first_interaction_derived": True,
        "same_domain_kinetic_positive": True,
        "exact_branch_required_for_effective_potential": False,
        "unselected_frozen_coefficient": "G5",
        "unconditional_interaction_sign": False,
        "free_new_coefficient_introduced": False,
        "independent_dimensionful_normalization_derived": False,
        "v6_31_permitted": False,
        "result": SCALE_RESULT,
        "stop_reason": (
            "v6.31 requires an explicitly positive permission artifact; "
            "the frozen repository neither selects G5 nor supplies the "
            "independent physical normalization"
        ),
    }


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "parent_scientific_shas": PARENT_SCIENTIFIC_SHAS,
        "action_domain": ACTION_DOMAIN,
        "Taylor_convention": TAYLOR,
        "projector_normalization": 1,
        "numerical_method": (
            "hypergeometric/shooting projection and independent augmented "
            "collocation"
        ),
        "precision_policy": (
            "serialize derived decimals and conservative certified bounds, "
            "not unstable raw method differences"
        ),
        "parity": "(q,tau)->(-q,tau)",
        "Noether_result": (
            "field-dependent residual representative Xi exactly completes "
            "the tangential equation"
        ),
        "matcher_result": "fixed trace and generated reaction compatible",
        "exact_branch_status": EXACT_RESULT,
        "reduced_family_status": REDUCED_RESULT,
        "validated_statements": [
            "D0 complement family exists through fourth order",
            "generic stable-wall exact branch is blocked at third order",
            "the first same-family Einstein interaction is quartic",
        ],
        "invalidated_statements": [
            "a nonzero kernel residual blocks the reduced potential",
            "the D2 kinetic or F1 coefficient belongs to D0",
        ],
        "open_statements": [
            "unconditional stability without selecting frozen G5",
            "independent dimensionful physical normalization",
        ],
        "forbidden_claims": [
            "full BHSM completion",
            "physical mass",
            "global stability",
            "scale prediction",
        ],
        "frozen_hash_status": "unchanged; version-scoped files only",
        "primary_verdict": PRIMARY_RESULT,
        **GUARDS,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    ledgers = {
        "projectors": ("BHSM_fixed_h_KKT_projectors_v6_30_5", projector_ledger()),
        "amplitude": (
            "BHSM_fixed_h_amplitude_coordinate_v6_30_5",
            amplitude_ledger(),
        ),
        "source3": (
            "BHSM_fixed_h_third_order_source_v6_30_5",
            third_order_source_ledger(),
        ),
        "noether3": (
            "BHSM_fixed_h_third_order_Noether_compatibility_v6_30_5",
            noether_ledger(),
        ),
        "projection3": (
            "BHSM_fixed_h_third_order_kernel_projection_v6_30_5",
            {**projection_formula(), "diagnostics": numerical_diagnostics()},
        ),
        "phi3": (
            "BHSM_fixed_h_Phi3_complement_v6_30_5",
            phi3_ledger(),
        ),
        "source4": (
            "BHSM_fixed_h_fourth_order_source_v6_30_5",
            fourth_order_ledger(),
        ),
        "phi4": (
            "BHSM_fixed_h_Phi4_complement_v6_30_5",
            phi4_ledger(),
        ),
        "action": (
            "BHSM_fixed_h_reduced_action_identity_v6_30_5",
            action_identity_ledger(),
        ),
        "jordan": (
            "BHSM_fixed_h_Jordan_coefficients_v6_30_5",
            jordan_ledger(),
        ),
        "einstein": (
            "BHSM_fixed_h_Einstein_coefficients_v6_30_5",
            einstein_ledger(),
        ),
        "canonical": (
            "BHSM_fixed_h_canonical_interaction_v6_30_5",
            canonical_ledger(),
        ),
        "stability": (
            "BHSM_fixed_h_local_stability_v6_30_5",
            stability_ledger(),
        ),
        "exact": (
            "BHSM_fixed_h_exact_branch_permission_v6_30_5",
            exact_permission_ledger(),
        ),
        "scale": (
            "BHSM_scale_phase_permission_v6_30_5",
            scale_permission_ledger(),
        ),
    }
    return {
        key: {**_common(artifact), key: ledger}
        for key, (artifact, ledger) in ledgers.items()
    }


def artifact_bytes() -> dict[str, bytes]:
    return {
        ARTIFACT_FILES[key]: deterministic_json(payload).encode("utf-8")
        for key, payload in artifact_payloads().items()
    }


def materialize_artifacts(root: Path) -> list[Path]:
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    paths = []
    for filename, content in artifact_bytes().items():
        path = target / filename
        path.write_bytes(content)
        paths.append(path)
    return paths
