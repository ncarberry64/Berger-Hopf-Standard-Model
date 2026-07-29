"""BHSM v6.30.3 fixed-action fold-tangent and surface-existence test.

The merged fixed-h operator makes an exact first-order comparison possible.
Its normalized kernel vector is purely scalar.  The older nonzero Jordan
frame derivative instead uses a curvature-varying metric tangent.  The two
derivatives therefore do not belong to the same variational family.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import sympy as sp

from bhsm.interface import fold_einstein_frame_kinetic_reduction as v612


VERSION = "v6.30.3"
SPRINT = "bhsm-fixed-action-nonlinear-fold-potential-v6-30-3"
SOURCE_MAIN_SHA = "c049d4d6833c7c9b2c98682cdd81a9368693a0d3"
V6302_SCIENTIFIC_SHA = "0d72d9ab14d203cb7a5dd7c12733824d56d563c7"

PRIMARY_RESULT = (
    "BHSM_FIXED_ACTION_NONLINEAR_FOLD_FAMILY_BLOCKED_BY_"
    "INCOMPATIBLE_FIXED_H_AND_CURVATURE_VARYING_FIRST_TANGENTS"
)
SURFACE_RESULT = "BHSM_CRITICAL_FOLD_IS_REGULAR_SPACETIME_CONFIGURATION"
STABILITY_RESULT = (
    "BHSM_FOLD_LOCAL_STABILITY_BLOCKED_BY_"
    "INCOMPATIBLE_FIXED_H_AND_CURVATURE_VARYING_FIRST_TANGENTS"
)
SCALE_RESULT = (
    "BHSM_SCALE_BRIDGE_PHASE_NOT_PERMITTED_AFTER_"
    "FIXED_ACTION_FIRST_TANGENT_CONTRADICTION"
)

ARTIFACT_FILES = {
    "family": "BHSM_fixed_action_nonlinear_radial_family_v6_30_3.json",
    "surface": "BHSM_critical_fold_surface_existence_v6_30_3.json",
    "jordan": "BHSM_Jordan_frame_fold_coefficients_v6_30_3.json",
    "einstein": "BHSM_Einstein_frame_fold_self_interaction_v6_30_3.json",
    "permission": (
        "BHSM_fold_family_existence_and_scale_permission_v6_30_3.json"
    ),
}

GUARDS = {
    "measured_input_used": False,
    "empirical_inverse_used": False,
    "empirical_generation_basis_used": False,
    "fitted_parameter_used": False,
    "new_action_introduced": False,
    "new_primitive_introduced": False,
    "new_scale_introduced": False,
    "vacuum_constant_subtracted": False,
    "mu_varied_with_q": False,
    "curvature_probe_varied_with_q": False,
    "q_dependent_regulator_used": False,
    "M4_metric_equation_imposed_before_extraction": False,
    "on_shell_Puiseux_curve_used_as_fixed_action_family": False,
    "v6_28_Robin_inverse_reused": False,
    "generic_pseudoinverse_used": False,
    "historical_artifact_rewritten": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "physical_mass_claimed": False,
    "global_stability_claimed": False,
    "terminal_surface_assumed_from_quadratic_flatness": False,
}

T = sp.symbols("t", real=True)
TAU = sp.symbols("tau", nonzero=True, real=True)
CHI_1 = sp.symbols("chi_1", positive=True, real=True)
KAPPA_0, KAPPA_1, Z5, A5, G5, X = sp.symbols(
    "kappa_0 kappa_1 Z5 A5 G5 X", real=True
)


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def fixed_action_phi1() -> tuple[str, str, str, str]:
    """The v6.30.2 quotient-kernel generator in KKT field order."""

    return ("0", "0", "u1", "0")


def frame_linear_functional(
    lapse1: sp.Expr, warp1: sp.Expr, *, kappa1: sp.Expr = sp.Integer(1)
) -> sp.Expr:
    """Differentiate F=2*kappa1*int(N*a^2)dt+2*C_partial."""

    n0 = sp.pi / 4
    a0 = sp.sqrt(2) * sp.sin(sp.pi * T / 4)
    return sp.simplify(
        2
        * kappa1
        * sp.integrate(lapse1 * a0**2 + 2 * n0 * a0 * warp1, (T, 0, 1))
    )


def fixed_action_frame_F1() -> sp.Expr:
    """The fixed-h scalar Jacobi tangent has no lapse or warp component."""

    return frame_linear_functional(sp.Integer(0), sp.Integer(0))


def inherited_curvature_varying_frame_F1(tau: int) -> sp.Expr:
    """The v6.12 value, retained only for the domain comparison."""

    if tau not in (-1, 1):
        raise ValueError("tau must be +/-1")
    return sp.simplify(v612.frame_F1(tau))


def inherited_curvature_tangent(tau: int) -> sp.Expr:
    """dX/dq of the historical affine fold profiles."""

    if tau not in (-1, 1):
        raise ValueError("tau must be +/-1")
    return tau * CHI_1


def first_tangent_contradiction(tau: int) -> sp.Expr:
    """Nonzero mismatch between the two purported derivatives."""

    return sp.simplify(
        inherited_curvature_varying_frame_F1(tau)
        - fixed_action_frame_F1()
    )


def reduced_lagrangian() -> sp.Expr:
    """Frozen one-cap lapse-retained homogeneous action density."""

    a = sp.Function("a")(T)
    sigma = sp.Function("sigma")(T)
    lapse = sp.Function("N")(T)
    potential = A5 * sigma**2 / 2 + G5 * sigma**4 / 4
    return (
        6
        * KAPPA_1
        * (a**2 * sp.diff(a, T) ** 2 / lapse + lapse * X * a**2)
        - lapse * a**4 * (KAPPA_0 / 2 + potential)
        - a**4 * Z5 * sp.diff(sigma, T) ** 2 / (2 * lapse)
    )


def _euler_expression(lagrangian: sp.Expr, field: sp.Expr) -> sp.Expr:
    return sp.diff(lagrangian, field) - sp.diff(
        sp.diff(lagrangian, sp.diff(field, T)), T
    )


def radial_noether_identity_residual() -> sp.Expr:
    """Verify a'E_a+sigma'E_sigma-N(E_N)'=0 for the frozen action."""

    lagrangian = reduced_lagrangian()
    a = sp.Function("a")(T)
    sigma = sp.Function("sigma")(T)
    lapse = sp.Function("N")(T)
    e_a = _euler_expression(lagrangian, a)
    e_sigma = _euler_expression(lagrangian, sigma)
    e_n = sp.diff(lagrangian, lapse)
    return sp.simplify(
        sp.expand(
            sp.diff(a, T) * e_a
            + sp.diff(sigma, T) * e_sigma
            - lapse * sp.diff(e_n, T)
        )
    )


def family_ledger() -> dict[str, Any]:
    return {
        "fixed_controls": [
            "kappa_0",
            "kappa_1",
            "Z5",
            "A5",
            "G5",
            "C_partial",
        ],
        "dmu_dq": 0,
        "fixed_domain": "M5=[0,1]_t x M4; B1={t=1}",
        "fixed_regulator": "one q-independent Vol_reg(M4,h)",
        "curvature_probe": "R4=R_c+r with dr/dq=0",
        "Phi1_KKT_order": ["A", "psi", "delta_sigma", "eta_tr"],
        "Phi1": list(fixed_action_phi1()),
        "Phi1_equation": "mathbb L_D Phi1=0",
        "Phi1_source": "v6.30.2 fixed-h quotient kernel span{u1}",
        "historical_affine_tangent": {
            "N1": "-tau chi_1/4",
            "a1": (
                "tau chi_1[a0/4-sqrt(2)t cos(pi t/4)/4]"
            ),
            "dX_dq": "tau chi_1",
            "domain": "curvature-varying affine fold tangent",
        },
        "failed_equation": (
            "mathbb L_D Phi1=0 at dr/dq=0 cannot simultaneously have "
            "Phi1=(0,0,u1,0) and the nonzero (N1,a1) tangent used by F1_tau"
        ),
        "smallest_missing_object": (
            "a single first tangent belonging simultaneously to fixed h, "
            "dr/dq=0, and the historical dX/dq=tau chi_1 family"
        ),
        "missing_object_location": (
            "none: the requirements are mutually exclusive; supplying the "
            "historical tangent varies the independent M4 curvature probe"
        ),
        "Phi2": None,
        "highest_consistent_order": 1,
        "noether_identity": (
            "a' E_a+sigma' E_sigma-N(E_N)'=0"
        ),
        "noether_identity_symbolic_residual": str(
            radial_noether_identity_residual()
        ),
        "offshell_force_warning": (
            "if the local metric and lapse equations are both imposed, a "
            "scalar-only residual g(q)u1 must be accompanied by the "
            "metric/lapse variation of a covariant amplitude constraint; "
            "otherwise sigma' g(q)u1=0 forces g(q)=0 on a nontrivial profile"
        ),
        "result": PRIMARY_RESULT,
    }


def surface_ledger() -> dict[str, Any]:
    return {
        "configuration": "q=0 critical cap on the fixed-h field manifold",
        "induced_metric": "gamma_J=hbar at a0(1)=1",
        "induced_metric_determinant_ratio": 1,
        "induced_volume_measure_ratio": 1,
        "induced_metric_rank": 4,
        "matcher_trace_rank_pre_gauge": 2,
        "matcher_trace_rank_homogeneous": 1,
        "reduced_KKT_boundary_block_independent_rows": 3,
        "rank_change_at_q0": False,
        "one_cap_radial_proper_length": "pi/4",
        "two_cap_total_proper_length": "pi/2",
        "F0": "pi/2",
        "F0_positive": True,
        "k_E_0": 6.935084858283065,
        "k_E_0_positive": True,
        "canonical_distance": (
            "sqrt(k_E(0))*|q|+O(q^2), finite as q->0"
        ),
        "normal_H_at_B1": 1,
        "extrinsic_curvature_finite": True,
        "surface_measure_vanishes": False,
        "metric_degenerates": False,
        "boundary_field_manifold_terminates": False,
        "physical_degree_count_changes": False,
        "signed_scalar_domain": "q in R locally for each retained orientation label",
        "scalar_Z2": "(q,tau)->(-q,tau)",
        "tau_relation": (
            "tau is the historical curvature/orientation tangent label, not "
            "the sign of the scalar Jacobi amplitude"
        ),
        "tangent_cone": (
            "R in the scalar direction on each orientation component; q=0 "
            "is an interior field configuration"
        ),
        "sheet_meeting": (
            "the unoriented q=0 metric data coincide, while oriented tau "
            "labels remain distinct until a cap-exchange quotient is imposed"
        ),
        "quadratic_flatness_used_as_surface_test": False,
        "result": SURFACE_RESULT,
    }


def jordan_ledger() -> dict[str, Any]:
    return {
        "density": "sqrt(-h)[F(q)R4/2-V_J(q)+...]",
        "F_formula": (
            "2 kappa_1 integral_0^1 N(q,t)a(q,t)^2 dt+2 C_partial"
        ),
        "F0": str(v612.frame_F0()),
        "fixed_action_F1": str(fixed_action_frame_F1()),
        "fixed_action_derivation": (
            "DF[Phi1]=0 because the fixed-h kernel Phi1 has A1=psi1=0"
        ),
        "historical_F1_plus": str(
            inherited_curvature_varying_frame_F1(1)
        ),
        "historical_F1_minus": str(
            inherited_curvature_varying_frame_F1(-1)
        ),
        "historical_source": (
            "v6.12 affine profiles with dX/dq=tau chi_1"
        ),
        "required_probe_condition": "dr/dq=0",
        "comparison": "fixed_action_F1 != historical_F1_tau for chi_1>0",
        "F2": None,
        "V0": "symbolic and unsubtracted",
        "V1_fixed_action_Z2": 0,
        "V2": None,
        "null_Hessian_identity_reproduced_on_one_common_family": False,
        "result": (
            "BHSM_FIXED_ACTION_JORDAN_LINEAR_COEFFICIENT_DERIVED_ZERO_"
            "AND_HISTORICAL_NONZERO_COEFFICIENT_REJECTED_ON_THIS_DOMAIN"
        ),
    }


def einstein_ledger() -> dict[str, Any]:
    return {
        "definition": "V_E=(F0/F)^2 V_J",
        "fixed_action_Z2_consequence": "F1=V1=0",
        "inherited_V_E_prime_0": 0,
        "inherited_V_E_second_0": 0,
        "same_family_quadratic_test_available": False,
        "reason": (
            "the inherited cancellation uses nonzero F1_tau from a different "
            "curvature-varying tangent, while fixed-action F2 and V2 are not derived"
        ),
        "first_nonzero_interaction": None,
        "canonical_self_coupling": None,
        "local_stability": STABILITY_RESULT,
        "global_stability_claimed": False,
    }


def permission_ledger() -> dict[str, Any]:
    return {
        "local_family_exists_in_declared_complement": False,
        "Phi2_derived": False,
        "F2_and_V2_separately_extracted": False,
        "null_Hessian_identity_reproduced_on_same_family": False,
        "first_nonzero_interaction_derived": False,
        "q_domain_and_tau_relation_classified": True,
        "action_or_regulator_drift": False,
        "surface_result": SURFACE_RESULT,
        "obstruction_class": (
            "A: repairable variational-domain identification error"
        ),
        "frozen_action_inconsistent": False,
        "scope": (
            "the contradiction is in identifying the historical "
            "curvature-varying tangent with the new fixed-h scalar amplitude, "
            "not in the frozen action itself"
        ),
        "scale_phase_permitted": False,
        "scale_permission": SCALE_RESULT,
        "primary_result": PRIMARY_RESULT,
    }


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "v6_30_2_scientific_sha": V6302_SCIENTIFIC_SHA,
        "primary_result": PRIMARY_RESULT,
        **GUARDS,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "family": {
            **_common("BHSM_fixed_action_nonlinear_radial_family_v6_30_3"),
            "family": family_ledger(),
        },
        "surface": {
            **_common("BHSM_critical_fold_surface_existence_v6_30_3"),
            "surface": surface_ledger(),
        },
        "jordan": {
            **_common("BHSM_Jordan_frame_fold_coefficients_v6_30_3"),
            "Jordan": jordan_ledger(),
        },
        "einstein": {
            **_common("BHSM_Einstein_frame_fold_self_interaction_v6_30_3"),
            "Einstein": einstein_ledger(),
        },
        "permission": {
            **_common(
                "BHSM_fold_family_existence_and_scale_permission_v6_30_3"
            ),
            "permission": permission_ledger(),
        },
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
