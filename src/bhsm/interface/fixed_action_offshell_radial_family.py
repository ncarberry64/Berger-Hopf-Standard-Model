"""BHSM v6.30.1 fixed-action off-shell radial-family domain audit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import sympy as sp

from bhsm.interface import fold_einstein_frame_kinetic_reduction as v612
from bhsm.interface import reduced_fold_operator_domain as v628


VERSION = "v6.30.1"
SPRINT = "bhsm-fixed-action-offshell-radial-family-v6-30-1"
SOURCE_MAIN_SHA = "ceaff39ad4c9d2996182407f411a38e6d85ee284"
V630_SCIENTIFIC_SHA = "0956941ce156ca30a7dc48369b5efeda00245471"

PRIMARY_RESULT = (
    "BHSM_FIXED_ACTION_OFFSHELL_RADIAL_FAMILY_BLOCKED_BY_"
    "UNDERIVED_FIXED_H_MATCHER_DIRICHLET_RANGE_OPERATOR"
)
STABILITY_RESULT = (
    "BHSM_FOLD_LOCAL_STABILITY_BLOCKED_BY_"
    "UNDERIVED_FIXED_H_MATCHER_DIRICHLET_RANGE_OPERATOR"
)
SCALE_RESULT = (
    "BHSM_SCALE_BRIDGE_PHASE_NOT_PERMITTED_BEFORE_"
    "FIXED_H_MATCHER_DIRICHLET_RANGE_CLOSURE"
)

ARTIFACT_FILES = {
    "controls": "BHSM_fixed_action_control_and_regulator_ledger_v6_30_1.json",
    "domain": "BHSM_fixed_h_matcher_domain_comparison_v6_30_1.json",
    "family": "BHSM_fixed_action_radial_family_coefficients_v6_30_1.json",
    "potential": "BHSM_fold_Einstein_frame_self_interaction_v6_30_1.json",
    "existence": (
        "BHSM_fixed_action_family_existence_and_scale_permission_v6_30_1.json"
    ),
}

GUARDS = {
    "measured_input_used": False,
    "empirical_inverse_used": False,
    "empirical_generation_basis_used": False,
    "fitted_parameter_used": False,
    "chat_only_value_imported": False,
    "new_action_introduced": False,
    "new_primitive_introduced": False,
    "new_scale_introduced": False,
    "vacuum_constant_subtracted": False,
    "mu_varied_with_q": False,
    "q_dependent_regulator_used": False,
    "local_X_FRW_field_created": False,
    "M4_metric_equation_imposed_before_extraction": False,
    "on_shell_Puiseux_curve_used": False,
    "unprojected_inverse_used": False,
    "generic_pseudoinverse_used": False,
    "historical_artifact_rewritten": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "physical_mass_claimed": False,
    "global_stability_claimed": False,
}

T = sp.symbols("t", real=True)
Q = sp.symbols("q", real=True)
R_PROBE = sp.symbols("r", real=True)
PSI_J = sp.symbols("psi_J", real=True)
P_PSI = sp.symbols("P_psi", real=True)
LAMBDA = sp.symbols("lambda", real=True)
C_PARTIAL = sp.symbols("C_partial", positive=True, real=True)


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def control_rows() -> list[dict[str, Any]]:
    rows = [
        ("kappa_0", "scalar_wall_junction_audit action ledger", "L^-5", "12 kappa_1"),
        ("kappa_1", "P1 Einstein-Hilbert action", "L^-3", "symbolic positive"),
        ("Z5", "bulk scalar kinetic action", "L^-3", "symbolic positive"),
        ("A5", "U5 quadratic coefficient", "L^-5", "-mu_c Z5"),
        ("G5", "U5 quartic coefficient", "L^-5", "symbolic fixed"),
        ("C_partial", "one common intrinsic B1 action", "L^-2", "kappa_1/2"),
    ]
    return [
        {
            "symbol": symbol,
            "repository_source": source,
            "dimension": dimension,
            "critical_value_or_status": value,
            "derivative_with_respect_to_q": 0,
            "derivative_with_respect_to_tau": 0,
            "regulator_dependence": "none",
            "status": "fixed action control",
        }
        for symbol, source, dimension, value in rows
    ]


def dmu_dq() -> sp.Integer:
    return sp.Integer(0)


def regulator_ledger() -> dict[str, Any]:
    return {
        "coordinate_manifold": "M5=[0,1]_t x M4 on each cap",
        "B1": "{t=1}",
        "coordinate_range_q_dependent": False,
        "B1_location_q_dependent": False,
        "M4_regulator": "one formal Vol_reg(M4,h) functional",
        "M4_regulator_q_dependent": False,
        "reported_quantity": "reduced density per fixed Vol_reg(M4,h)",
        "reference_chart_q_dependent": False,
        "subtraction_convention": "none",
        "vacuum_constant_subtracted": False,
    }


def m4_metric_ledger() -> dict[str, Any]:
    return {
        "metric": "independent h_mu_nu",
        "curvature_probe": "R4=R_c+r with r independent of q",
        "d_r_d_q": 0,
        "X_FRW_local_field": None,
        "q_identified_with_curvature": False,
        "M4_equation_timing": "only after F(q) and V_J(q) extraction",
    }


def onshell_robin_residual() -> sp.Expr:
    """The v6.28 matcher-eliminated metric B1 domain."""

    return P_PSI + 12 * C_PARTIAL * LAMBDA * PSI_J


def fixed_h_dirichlet_residual() -> sp.Expr:
    """At fixed independent h, matcher variation fixes induced metric."""

    return PSI_J


def metric_modulus() -> dict[str, sp.Expr]:
    return v628.metric_modulus()


def metric_modulus_robin_residual_at_zero_derivative() -> sp.Expr:
    """The inherited z mode obeys the on-shell lambda=0 boundary equation."""

    z = metric_modulus()
    return sp.simplify(v628.metric_b1_operator(z["A"], z["psi"], 0))


def metric_modulus_dirichlet_residual() -> sp.Expr:
    return sp.simplify(metric_modulus()["psi"].subs(T, 1))


def domains_are_equal() -> bool:
    return False


def matcher_variation_ledger() -> dict[str, Any]:
    return {
        "uneliminated_variations": {
            "bulk_boundary_metric": "Pi_bulk+Lambda=0",
            "independent_h": "-Lambda+2 C_partial G4-T_B1=0",
            "multiplier": "h-iota^*gamma=0",
        },
        "on_shell_elimination": (
            "combining all three equations gives the tensor junction and the "
            "v6.28 Robin domain"
        ),
        "off_shell_fixed_h": (
            "do not impose delta_h Gamma=0; matcher fixes iota^*gamma=h "
            "(Dirichlet), while Lambda is the boundary response"
        ),
        "consequence": (
            "the matcher-eliminated Robin operator is an on-shell-h operator "
            "and is not the range operator of Gamma[h,q] at fixed h"
        ),
    }


def family_coefficient_ledger() -> dict[str, Any]:
    return {
        "field_vector_required": [
            "bulk lapse A or exact N",
            "bulk Weyl/warp field psi or exact a",
            "delta_sigma_perp",
            "full-shift-constrained threading",
            "independent h_mu_nu",
            "matcher multiplier Lambda_mu_nu",
        ],
        "coordinates": {
            "q": "normalized critical scalar Jacobi amplitude",
            "r": "independent M4 curvature probe",
            "tau": "one-sided fold sheet label",
        },
        "kernel": "span{u1} after fixed-h Dirichlet data remove metric z",
        "complement": (
            "u1-orthogonal radial fields on the not-yet-derived fixed-h "
            "Dirichlet matcher domain"
        ),
        "order_reached": 1,
        "Phi0": "critical cap with independent h",
        "Phi1": {
            "sigma1": "u1, normalized by integral N0 a0^4 u1^2 dt=1",
            "a1": "not promoted from the control-varying Puiseux curve",
            "N1": "not promoted from the control-varying Puiseux curve",
            "equation": "L0 u1=0 on the scalar Dirichlet domain",
        },
        "Phi2": None,
        "Phi3": None,
        "Phi4": None,
        "reason": (
            "Q L0 Q and its Green operator have not been derived on the "
            "fixed-h Dirichlet matcher domain"
        ),
        "absence_of_neighboring_solution_is_failure": False,
    }


def jordan_coefficient_ledger() -> dict[str, Any]:
    return {
        "common_density_convention": (
            "Gamma4/Vol_reg=sqrt(-h) coefficient density with "
            "+F(q)R4/2-V_J(q)"
        ),
        "F0": sp.sstr(v612.frame_F0()),
        "F1_plus": sp.sstr(v612.frame_F1(1)),
        "F1_minus": sp.sstr(v612.frame_F1(-1)),
        "F2": None,
        "V0": "symbolic, no subtraction",
        "V1": "2(F1/F0)V0 from inherited stationarity",
        "V2": None,
        "v6_30_identity_checked": False,
        "reason": "Phi2 is unavailable on the required fixed-h domain",
        "higher_curvature_absorbed_into_F_or_V": False,
    }


def potential_ledger() -> dict[str, Any]:
    return {
        "V_E_prime_0": 0,
        "V_E_second_0": 0,
        "source": "inherited v6.30 invariant quadratic theorem",
        "first_nonzero_higher_derivative": None,
        "canonical_self_coupling": None,
        "kinetic_at_fold": "6.935084858283065 +/- 2e-12 >0",
        "local_stability": STABILITY_RESULT,
        "global_stability": False,
    }


def existence_ledger() -> dict[str, Any]:
    return {
        "hypotheses": {
            "fixed_controls": True,
            "fixed_regulator": True,
            "simple_scalar_kernel": True,
            "v6_28_Robin_Fredholm_operator": True,
            "fixed_h_Dirichlet_Fredholm_operator": None,
            "fixed_h_complement_invertibility": None,
            "nonlinear_fixed_h_boundary_map_regular": None,
        },
        "local_existence_theorem_emitted": False,
        "failed_hypothesis": (
            "the fixed-h uneliminated-matcher Dirichlet operator, adjoint "
            "domain, Green current, and complement inverse are underived"
        ),
        "obstruction_class": "C: missing derivation within the frozen action",
        "fatal_inconsistency": False,
        "scale_permission": SCALE_RESULT,
        "scale_phase_permitted": False,
        "primary_result": PRIMARY_RESULT,
    }


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "v6_30_scientific_sha": V630_SCIENTIFIC_SHA,
        "primary_result": PRIMARY_RESULT,
        **GUARDS,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "controls": {
            **_common("BHSM_fixed_action_control_and_regulator_ledger_v6_30_1"),
            "controls": control_rows(),
            "dmu_dq": int(dmu_dq()),
            "regulator": regulator_ledger(),
            "M4": m4_metric_ledger(),
        },
        "domain": {
            **_common("BHSM_fixed_h_matcher_domain_comparison_v6_30_1"),
            "matcher": matcher_variation_ledger(),
            "on_shell_Robin": sp.sstr(onshell_robin_residual()),
            "off_shell_fixed_h_Dirichlet": sp.sstr(
                fixed_h_dirichlet_residual()
            ),
            "domains_equal": domains_are_equal(),
            "metric_z_Robin_residual_lambda0": sp.sstr(
                metric_modulus_robin_residual_at_zero_derivative()
            ),
            "metric_z_Dirichlet_residual": sp.sstr(
                metric_modulus_dirichlet_residual()
            ),
        },
        "family": {
            **_common("BHSM_fixed_action_radial_family_coefficients_v6_30_1"),
            "family": family_coefficient_ledger(),
        },
        "potential": {
            **_common("BHSM_fold_Einstein_frame_self_interaction_v6_30_1"),
            "Jordan": jordan_coefficient_ledger(),
            "Einstein": potential_ledger(),
        },
        "existence": {
            **_common(
                "BHSM_fixed_action_family_existence_and_scale_permission_v6_30_1"
            ),
            "existence": existence_ledger(),
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
