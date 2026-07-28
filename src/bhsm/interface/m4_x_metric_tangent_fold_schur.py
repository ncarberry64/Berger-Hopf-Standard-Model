"""BHSM v6.22.0 M4 X-metric tangent and fold-Schur obstruction audit.

The repository defines the scalar-wall M4 reference by Ric(h)=3 X h, so
R4=12 X.  The v6.20 missing-tangent target instead states delta R4=delta X.
The mismatch occurs before a covariant metric family, gauge quotient, domain,
or inverse can be selected.  This module records that earliest obstruction
and deliberately emits no downstream Schur or kinetic coefficient.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import sympy as sp


VERSION = "v6.22.0"
SPRINT = "bhsm-m4-x-metric-tangent-fold-schur-v6-22-0"
SOURCE_MAIN_SHA = "4bdedf9e492f35696b2af076afae84e3ca5f67e7"
PRIMARY_RESULT = (
    "BHSM_M4_X_METRIC_TANGENT_BLOCKED_BY_X_TO_R4_NORMALIZATION_CONFLICT"
)
SCHUR_RESULT = (
    "BHSM_FOLD_SCHUR_REDUCTION_BLOCKED_BY_X_TO_R4_NORMALIZATION_CONFLICT"
)
KINETIC_RESULT = (
    "BHSM_FOLD_KINETIC_SIGN_REMAINS_UNRESOLVED_BY_"
    "X_TO_R4_NORMALIZATION_CONFLICT"
)

ARTIFACT_FILES = {
    "definition": "BHSM_M4_X_definition_and_branch_audit_v6_22_0.json",
    "tangent": "BHSM_gauge_quotiented_M4_X_metric_tangent_v6_22_0.json",
    "source_domain": "BHSM_fold_complete_mixed_source_domain_v6_22_0.json",
    "kinetic": "BHSM_fold_schur_kinetic_verdict_v6_22_0.json",
}

GUARDS = {
    "measured_input": False,
    "fitted_coefficient": False,
    "chat_only_candidate_imported": False,
    "new_primitive": False,
    "new_scale": False,
    "new_action": False,
    "new_boundary_parameter": False,
    "generic_pseudoinverse": False,
    "numerical_solve_launched": False,
    "physical_mass_claim": False,
    "stability_claim": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
}

X = sp.symbols("X", positive=True, real=True)
A = sp.symbols("A", real=True)
PHI = sp.symbols("phi", real=True)
BOX_PHI = sp.symbols("Box_phi", real=True)
R4 = sp.symbols("R_4", real=True)


def frw_scalar_curvature(
    x_value: sp.Expr = X, acceleration: sp.Expr = A
) -> sp.Expr:
    """Repository Lorentzian closed-FRW identity R4=6(A+X)."""
    return sp.expand(6 * (acceleration + x_value))


def branch_scalar_curvatures(x_value: sp.Expr = X) -> dict[str, sp.Expr]:
    """Scalar curvature on the two exact M4 branches stored at criticality."""
    return {
        "maximally_symmetric_dS4": frw_scalar_curvature(
            x_value, x_value
        ),
        "critical_static_RxS3": frw_scalar_curvature(
            x_value, sp.Integer(0)
        ),
    }


def branch_dR4_dX() -> dict[str, sp.Expr]:
    """Ordinary homogeneous-family derivatives on the stored branches."""
    return {
        name: sp.diff(value, X)
        for name, value in branch_scalar_curvatures().items()
    }


def frechet_scalar_curvature(
    div_div_k: sp.Expr,
    box_trace_k: sp.Expr,
    ricci_contract_k: sp.Expr,
) -> sp.Expr:
    """DR_h[k] for k_mu_nu=delta h_mu_nu in the repository convention."""
    return sp.expand(div_div_k - box_trace_k - ricci_contract_k)


def conformal_frechet_scalar_curvature(
    scalar_curvature: sp.Expr = R4,
    phi: sp.Expr = PHI,
    box_phi: sp.Expr = BOX_PHI,
) -> sp.Expr:
    """Four-dimensional check for k_mu_nu=2 phi h_mu_nu."""
    return sp.expand(-6 * box_phi - 2 * scalar_curvature * phi)


def conformal_exact_linear_coefficient(
    scalar_curvature: sp.Expr = R4,
    phi: sp.Expr = PHI,
    box_phi: sp.Expr = BOX_PHI,
) -> sp.Expr:
    """Differentiate the exact 4D conformal curvature law at epsilon=0."""
    epsilon = sp.symbols("epsilon", real=True)
    exact_to_linear_order = sp.exp(-2 * epsilon * phi) * (
        scalar_curvature - 6 * epsilon * box_phi
    )
    return sp.expand(sp.diff(exact_to_linear_order, epsilon).subs(epsilon, 0))


def pure_diffeomorphism_curvature_variation(
    lie_derivative_of_R4: sp.Expr,
) -> sp.Expr:
    """Naturality check DR_h[L_xi h]=L_xi R4."""
    return sp.expand(lie_derivative_of_R4)


def formal_adjoint_ledger() -> dict[str, str]:
    """Formal L2 adjoint and boundary current before a domain is chosen."""
    return {
        "operator": (
            "DR_h^*[f]_mu_nu=nabla_mu nabla_nu f"
            "-h_mu_nu Box f-f Ric_mu_nu"
        ),
        "green_current": (
            "n_mu[f nabla_nu k^(mu nu)-f nabla^mu tr(k)"
            "-(nabla_nu f)k^(mu nu)+(nabla^mu f)tr(k)]"
        ),
        "flux_status": (
            "not evaluable: no covariant M4 regulator boundary and no "
            "action-selected tangent/adjoint domain are stored"
        ),
    }


def definition_ledger() -> dict[str, Any]:
    """Repository-native definition and branch inventory for curvature X."""
    curvatures = branch_scalar_curvatures()
    derivatives = branch_dR4_dX()
    return {
        "symbol_scope": (
            "curvature X only; unrelated embedding maps named X and ordinary "
            "coordinates x are excluded"
        ),
        "definitions": [
            {
                "source": (
                    "src/bhsm/interface/"
                    "intrinsic_m4_junction_background.py:264"
                ),
                "statement": "X=H^2+a^-2; A=N^-1 dot(H)+H^2",
                "classification": "homogeneous closed-FRW invariant",
            },
            {
                "source": (
                    "src/bhsm/interface/"
                    "scalar_wall_junction_audit.py:268-275"
                ),
                "statement": (
                    "signature=(-,+,+,+,+), "
                    "Ric_mu_nu(h)=3 X h_mu_nu"
                ),
                "classification": (
                    "maximally symmetric M4 curvature parameter in the "
                    "frozen scalar-wall action"
                ),
            },
            {
                "source": (
                    "src/bhsm/interface/"
                    "scalar_wall_puiseux_fold.py:299-318"
                ),
                "statement": (
                    "X is solved with the warp factor and cap endpoint; "
                    "X=2+tau chi_1 r+O(r^2)"
                ),
                "classification": (
                    "homogeneous on-shell Puiseux branch coordinate"
                ),
            },
            {
                "source": (
                    "src/bhsm/interface/"
                    "scalar_wall_fold_morse_sheet_selection.py:195-235"
                ),
                "statement": (
                    "delta X=tau chi_1 is a component of the stored "
                    "fixed-control fold vector"
                ),
                "classification": (
                    "homogeneous tangent promoted adiabatically through q(x)"
                ),
            },
            {
                "source": (
                    "src/bhsm/interface/"
                    "critical_lapse_weyl_hessian.py:267-303"
                ),
                "statement": (
                    "delta R4[T_X]=tau chi_1 q and a local hbar[X] "
                    "representative/domain are absent"
                ),
                "classification": "v6.20 proposed local tangent target",
            },
        ],
        "questions": {
            "X_is_local_scalar_field": False,
            "X_is_FRW_H2_plus_a_minus2": True,
            "X_is_universally_proportional_to_R4": False,
            "X_is_homogeneous_family_parameter": True,
            "X_is_on_shell_branch_coordinate": True,
            "one_X_has_multiple_stored_M4_branches": True,
            "v6_20_action_branch": (
                "maximally symmetric Einstein M4 action density/regulator; "
                "no coordinate-level hbar[X] family or regulated domain"
            ),
            "hbar_mu_nu_X_declared": False,
            "only_curvature_condition_declared": True,
        },
        "branch_inventory": {
            "maximally_symmetric_dS4": {
                "stored_relation": "A=X; Ric(h)=3X h",
                "R4": sp.sstr(curvatures["maximally_symmetric_dS4"]),
                "dR4_dX": sp.sstr(
                    derivatives["maximally_symmetric_dS4"]
                ),
                "homogeneous_metric_family": (
                    "ds4^2=-du^2+X^-1 cosh^2(sqrt(X)(u-u0)) dOmega3^2"
                ),
                "action_role": (
                    "used by the scalar-wall reduced action and analytic "
                    "maximally symmetric M4 volume regulator"
                ),
            },
            "critical_static_RxS3": {
                "stored_relation": "A=0; H=0; a=X^-1/2",
                "R4": sp.sstr(curvatures["critical_static_RxS3"]),
                "dR4_dX": sp.sstr(
                    derivatives["critical_static_RxS3"]
                ),
                "homogeneous_metric_family": (
                    "ds4^2=-du^2+X^-1 dOmega3^2 at the critical embedding"
                ),
                "action_role": (
                    "separate exact critical junction branch, not the "
                    "maximally symmetric scalar-wall regulator"
                ),
            },
        },
        "critical_degeneracy": (
            "the dS4 bounce and static R x S3 branch are distinct metrics "
            "with X=2 q5"
        ),
        "local_vs_homogeneous": (
            "A: ordinary derivative exists for stored homogeneous ansatz "
            "branches; B: no field-valued right inverse is stored; "
            "C: their combination is therefore not defined"
        ),
    }


def normalization_conflict_ledger() -> dict[str, Any]:
    """Earliest exact inconsistency that triggers the sprint stop rule."""
    return {
        "action_convention_source": (
            "src/bhsm/interface/scalar_wall_junction_audit.py:270"
        ),
        "action_convention": "Ric_mu_nu(h)=3X h_mu_nu",
        "action_consequence": "R4=12X and delta R4=12 delta X",
        "v6_20_target_source": (
            "src/bhsm/interface/critical_lapse_weyl_hessian.py:269-271"
        ),
        "v6_20_target": "delta R4[T_X]=delta X=tau chi_1 q",
        "coefficient_expected": 12,
        "coefficient_stored_in_target": 1,
        "static_branch_coefficient": 6,
        "conflict_residual_maximally_symmetric": 11,
        "normalization_resolved": False,
        "can_be_removed_by_diffeomorphism": False,
        "can_be_fixed_by_gauge_choice": False,
        "requires_new_measured_input": False,
        "minimum_missing_object": (
            "one repository-level declaration fixing whether the local "
            "response variable is X, R4, or R4/12, together with the "
            "corresponding covariant hbar[X] family and domain"
        ),
        "earliest_stop": PRIMARY_RESULT,
    }


def metric_tangent_ledger() -> dict[str, Any]:
    """Bounded tangent audit; no quotient inverse is manufactured."""
    return {
        "background": (
            "normalized q5=1 critical maximally symmetric scalar-wall "
            "action density at X=2"
        ),
        "signature": "Lorentzian M4 (-,+,+,+)",
        "regulator": (
            "analytic maximally symmetric M4 volume with X^-2 scaling; "
            "no coordinate-level regulated manifold or boundary stored"
        ),
        "DR_h": (
            "nabla_mu nabla_nu k^(mu nu)-Box tr_h(k)"
            "-Ric_mu_nu k^(mu nu)"
        ),
        "variation_variable": "k_mu_nu=delta h_mu_nu",
        "conformal_check": (
            "for k_mu_nu=2 phi h_mu_nu, "
            "DR_h[k]=-6 Box phi-2 R4 phi"
        ),
        "diffeomorphism_check": (
            "DR_h[L_xi h]=L_xi R4; it vanishes on constant-R4 "
            "backgrounds for boundary-admissible xi"
        ),
        "homogeneous_check": {
            "maximally_symmetric_dR4_dX": 12,
            "critical_static_dR4_dX": 6,
            "v6_20_target_dR4_dX": 1,
            "passed": False,
        },
        "decomposition": (
            "York/Hodge decomposition is required but not uniquely "
            "instantiated before the X-to-R4 normalization is fixed"
        ),
        "gauge_quotient": None,
        "domain": None,
        "operator_to_invert": None,
        "kernel_dimension": None,
        "adjoint_kernel_dimension": None,
        "compatibility": None,
        "tangent_representation": None,
        "TT_source_audit": {
            "DR_kernel_fact": (
                "on the Einstein dS4 branch every TT tensor obeys "
                "DR_h[k_TT]=0"
            ),
            "action_source_projection_zero_proved": False,
            "unsourced_TT_freedom_removed": False,
        },
        "formal_adjoint": formal_adjoint_ledger(),
        "inverse_constructed": False,
        "theorem_verdict": PRIMARY_RESULT,
    }


def source_domain_ledger() -> dict[str, Any]:
    """Downstream stages prohibited by the earliest tangent obstruction."""
    return {
        "complete_field_vector": [
            "A",
            "B",
            "psi",
            "E",
            "delta sigma",
            "zeta",
        ],
        "preserved_reductions": {
            "zeta": "fixed-iota representative zeta=0",
            "threading": (
                "Pi_perp S_Sigma=-tau(pi chi_1/16)Pi_perp q; "
                "C_Sigma=0"
            ),
            "threading_domain_nonempty": True,
            "threading_unresolved_trace_count": 0,
        },
        "P1_tangent_source": None,
        "GHY_tangent_cancellation": (
            "historical capwise cancellation preserved; not recomputed with "
            "an undefined local X tangent"
        ),
        "B1_tangent_source": None,
        "matcher_tangent_source": None,
        "J_A_complete": None,
        "J_psi_complete": None,
        "J_E_complete": None,
        "endpoint_conditions": None,
        "scalar_boundary_conditions": None,
        "metric_junction_conditions": None,
        "complete_operator": None,
        "formal_adjoint_domain": None,
        "green_form_vanishing": None,
        "source_orthogonality": None,
        "source_compatibility": None,
        "double_counting_audit": {
            "K_Weyl_existing": (
                "3 chi_1^2(4-pi)^2/(16 pi)"
            ),
            "X_tangent_role": None,
            "separation_proved": False,
            "double_counting_performed": False,
        },
        "Schur_inverse": None,
        "Schur_complement": None,
        "blocker": PRIMARY_RESULT,
        "verdict": SCHUR_RESULT,
    }


def kinetic_ledger() -> dict[str, Any]:
    """Exact bounded kinetic verdict with no downstream numerical value."""
    return {
        "action_convention": (
            "S_deriv^(2)=1/2 integral sqrt(-h)"
            "[K_direct(Dq)^2+2(Dq)<J,Y>+<Y,LY>]"
        ),
        "two_cap_multiplicity": 2,
        "common_B1_multiplicity": 1,
        "radial_measure": "pi sin^4(pi t/4) dt",
        "K_scalar": "2 integral a0^2 u1^2 d rho >=2>0",
        "K_grav_constraint_J": None,
        "K_Weyl": "3 chi_1^2(4-pi)^2/(16 pi)",
        "k_q_E": None,
        "numerical_method": None,
        "numerical_uncertainty": None,
        "sign": None,
        "domain_conditions": None,
        "sheet_dependence": None,
        "scalar_sign_dependence": (
            "known inherited terms are scalar-sign independent; total open"
        ),
        "physical_claims_not_made": [
            "physical mass",
            "tachyon status",
            "nonlinear stability",
            "global sheet selection",
            "white-hole dynamics",
            "cosmological production",
        ],
        "exact_blocker": PRIMARY_RESULT,
        "verdict": KINETIC_RESULT,
    }


def _common(name: str) -> dict[str, Any]:
    return {
        "artifact": name,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "primary_result": PRIMARY_RESULT,
        "schur_result": SCHUR_RESULT,
        "kinetic_result": KINETIC_RESULT,
        **GUARDS,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "definition": {
            **_common("BHSM_M4_X_definition_and_branch_audit_v6_22_0"),
            "definition_ledger": definition_ledger(),
            "normalization_conflict": normalization_conflict_ledger(),
        },
        "tangent": {
            **_common(
                "BHSM_gauge_quotiented_M4_X_metric_tangent_v6_22_0"
            ),
            "metric_tangent": metric_tangent_ledger(),
            "normalization_conflict": normalization_conflict_ledger(),
        },
        "source_domain": {
            **_common("BHSM_fold_complete_mixed_source_domain_v6_22_0"),
            "source_domain": source_domain_ledger(),
        },
        "kinetic": {
            **_common("BHSM_fold_schur_kinetic_verdict_v6_22_0"),
            "kinetic": kinetic_ledger(),
            "integrity": {"guards": dict(GUARDS)},
        },
    }


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def artifact_bytes() -> dict[str, bytes]:
    return {
        ARTIFACT_FILES[key]: deterministic_json(payload).encode("utf-8")
        for key, payload in artifact_payloads().items()
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
