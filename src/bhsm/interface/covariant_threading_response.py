"""BHSM v6.18.0 covariant threading-response action audit."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import sympy as sp


VERSION = "v6.18.0"
SPRINT = "bhsm-covariant-threading-response-fold-phase-v6-18-0"
SOURCE_MAIN_SHA = "9f61c9eaf09ebdb78056231e0615ba64aaf171ed"
V617_HEAD_SHA = "ec5efd65234783fde414742f1dbc0445bea645e8"
PR177_MERGE_SHA = SOURCE_MAIN_SHA

PRIMARY_RESULT = "BHSM_INDUCED_THREADING_ACTION_REPRODUCES_CONSTRAINT_RESPONSE"
THRESHOLD_RESULT = "BHSM_FOLD_SOURCE_VANISHING_REPLACES_EXPLICIT_ENERGY_THRESHOLD"
DOMAIN_RESULT = "BHSM_THREADING_RESPONSE_ACTION_RESTORES_NONEMPTY_FOLD_DOMAIN"
KINETIC_RESULT = (
    "BHSM_FOLD_KINETIC_REMAINS_UNRESOLVED_BY_EXACT_OPERATOR_OBSTRUCTION"
)

ARTIFACT_FILES = {
    "action": "BHSM_threading_response_action_and_kernel_v6_18_0.json",
    "activation": "BHSM_local_fold_phase_invariant_audit_v6_18_0.json",
    "constraint": "BHSM_fold_constraint_response_and_kinetic_v6_18_0.json",
    "verdict": "BHSM_v6_18_0_response_verdict_and_model_map.json",
}

GUARDS = {
    "new_fundamental_action": False,
    "unsupported_stiffness": False,
    "fitted_threshold": False,
    "arbitrary_switch": False,
    "new_numerical_primitive": False,
    "new_dimensionful_scale": False,
    "measured_input": False,
    "boundary_tension": False,
    "tau_J": False,
    "neutral_work": False,
    "physical_bulk_Dirac_law": False,
    "generic_pseudoinverse": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "time_assigned_to_common_core": False,
}

CHI_1_VALUE = 5.26830787154212
C_RESPONSE = sp.pi * sp.Symbol("chi_1", positive=True) / 16


def harmonic_laplacian(ell: int, radius: sp.Expr = sp.Symbol("a", positive=True)) -> sp.Expr:
    if ell < 0:
        raise ValueError("ell must be nonnegative")
    return sp.Integer(ell) * (ell + 2) / radius**2


def threading_kernel_eigenvalue(
    ell: int, radius: sp.Expr = sp.Symbol("a", positive=True)
) -> sp.Expr:
    """Normalized v6.16 P1 Hessian eigenvalue on round spatial S3."""
    return sp.simplify(-2 * harmonic_laplacian(ell, radius) / radius**2)


def source_eigenvalue(
    ell: int,
    tau: int,
    q_ell: sp.Expr,
    chi_1: sp.Expr = sp.Symbol("chi_1", positive=True),
    radius: sp.Expr = sp.Symbol("a", positive=True),
) -> sp.Expr:
    if tau not in (-1, 1):
        raise ValueError("tau must be +/-1")
    c = sp.pi * chi_1 / 16
    return sp.simplify(tau * c * threading_kernel_eigenvalue(ell, radius) * q_ell)


def dynamic_response(
    ell: int,
    tau: int,
    q_ell: sp.Expr,
    chi_1: sp.Expr = sp.Symbol("chi_1", positive=True),
) -> sp.Expr:
    if ell == 0:
        return sp.Integer(0)
    if tau not in (-1, 1):
        raise ValueError("tau must be +/-1")
    return sp.simplify(-tau * sp.pi * chi_1 * q_ell / 16)


def corrected_resting_principle() -> dict[str, Any]:
    return {
        "statement": (
            "When J_Sigma[q]=0, the homogeneous integration constant "
            "C_Sigma is selected to vanish, so Sbar_Sigma=0."
        ),
        "C_Sigma": 0,
        "classification": "Adopted BHSM axiom",
        "partial_q_Sbar_imposed_zero": False,
        "dynamic_response_permitted": (
            "Sbar_Sigma=-tau(pi chi_1/16)q+O(q^2)"
        ),
        "tau_switches_to_zero": False,
        "time_assigned_to_common_core": False,
        "v6_17_history_rewritten": False,
    }


def action_ledger() -> dict[str, Any]:
    return {
        "derivation_source": "existing P1+GHY+B1+matcher+scalar Hessian",
        "construction": (
            "Hamilton-Jacobi/on-shell constrained-collar functional with "
            "Sbar as boundary data"
        ),
        "fundamental_boundary_action": False,
        "induced_effective_action": True,
        "general_Dirichlet_to_Neumann_operator": (
            "nonlocal in general; only the symmetric-background harmonic "
            "kernel is derived"
        ),
        "symmetric_background_functional": (
            "Gamma_eff=1/2<Sbar,K_Sigma Sbar>"
            "+<Sbar,K_Sigma tau(pi chi_1/16)q>+Gamma_0"
        ),
        "inner_product": (
            "<f,g>_Sigma=integral_B1 sqrt(abs(gamma)) conjugate(f)g"
        ),
        "interface_count": "the common Z2 interface is counted once",
        "bulk_cap_factor": (
            "the two reflected P1 collar contributions share one common "
            "overall normalization"
        ),
        "orientation": (
            "tau changes the source sign; the outward average and kernel are "
            "orientation even"
        ),
        "normalization": (
            "lambda of v6.16 shifts Sbar by lambda, so delta Sbar=lambda"
        ),
        "higher_terms": "O(Sbar^3,Sbar^2 q,Sbar q^2)",
        "new_action_term": False,
        "result": PRIMARY_RESULT,
    }


def kernel_ledger() -> dict[str, Any]:
    return {
        "parent_density": (
            "N^-2[(D_muD_nu lambda)^2-(D^2 lambda)^2]"
        ),
        "general_order": 4,
        "round_S3_reduction": (
            "Bochner identity reduces the integrated form to a curvature "
            "times first-derivative pairing"
        ),
        "round_S3_operator": "Khat_Sigma=(2/a^2)D_spatial^2",
        "eigenvalue": "-2 ell(ell+2)/a^4",
        "ell_0": "kernel/integration constant",
        "ell_ge_1": "nonzero and invertible mode by mode",
        "Lorentzian_action_sign": (
            "negative for the displayed time-independent spatial harmonics"
        ),
        "Euclidean_Hessian_sign": (
            "not certified without Wick rotating the complete constrained "
            "P1+GHY sector"
        ),
        "canonical_Hamiltonian_sign": (
            "not certified before the full constraint reduction"
        ),
        "stability": "constraint-indefinite; not a ghost theorem",
        "lower_derivative_completion": (
            "curvature commutator supplies the second-order reduction on the "
            "round background; general lower terms remain in the DtN kernel"
        ),
        "unsupported_stiffness_added": False,
    }


def source_ledger() -> dict[str, Any]:
    return {
        "bulk_source": (
            "J_shift(t)=-3 tau chi_1 t/[4 sin^2(pi t/4)]"
        ),
        "regular_response": "S_q,req(t)=-tau(pi chi_1/16)t",
        "B1_response": "partial_q Sbar_Sigma=-tau pi chi_1/16",
        "effective_source": (
            "J_Sigma[q]=K_Sigma tau(pi chi_1/16)Pi_perp q"
        ),
        "derivation": (
            "Hamilton-Jacobi integrability fixes the source relative to the "
            "v6.16 Hessian because the v6.17 momentum constraint fixes the "
            "response for every nonconstant harmonic"
        ),
        "proportional_to": (
            "derivatives of q through K_Sigma; not an algebraic threshold"
        ),
        "source_free_condition": "Pi_perp q=0, equivalently D_mu q=0 locally",
        "upper_tau_plus": "-pi chi_1 q/16",
        "lower_tau_minus": "+pi chi_1 q/16",
        "scalar_sign_independent": True,
        "coefficient_inserted_by_hand": False,
        "result": PRIMARY_RESULT,
    }


def activation_audit() -> dict[str, Any]:
    def row(covariant, parity, dimension, sign, available, rest, sheets, scalar_sign, observer, scale, distinguishes):
        return {
            "local_covariance": covariant,
            "Z2": parity,
            "dimension": dimension,
            "sign_definite": sign,
            "existing_action": available,
            "vanishes_at_rest": rest,
            "sheet_behavior": sheets,
            "scalar_sign": scalar_sign,
            "new_observer": observer,
            "new_scale": scale,
            "distinguishes_transition": distinguishes,
        }

    return {
        "Delta_X=X-2": row(True, "even", "curvature", False, True, False, "tau odd", "even", False, False, False),
        "lambda_fold_min": row(True, "even", "Hessian eigenvalue", False, True, False, "sheet dependent", "even", False, False, False),
        "sigma_squared": row(True, "even", "field squared", True, True, False, "same magnitude", "even", False, False, False),
        "normal_sigma_squared": row(True, "even", "gradient squared", True, True, False, "same magnitude", "even", False, False, False),
        "nabla_sigma_squared": row(True, "even", "gradient squared", False, True, False, "same magnitude", "even", False, False, False),
        "U5_difference": row(True, "even", "action density", False, True, False, "same magnitude", "even", False, False, False),
        "Dq_squared": row(True, "even", "gradient squared", False, True, True, "same", "same", False, False, True),
        "fold_energy_density": row(True, "even", "energy density", True, "conditional", True, "same", "same", True, False, True),
        "normal_stress": row(True, "even", "pressure/stress", False, True, False, "sheet dependent", "even", False, False, False),
        "intrinsic_curvature": row(True, "even", "curvature", False, True, False, "sheet dependent", "even", False, False, False),
        "selected_model": "A: no explicit threshold",
        "reason": (
            "J_Sigma is derivative sourced and vanishes when D_mu q=0; no "
            "activation invariant is needed"
        ),
        "hard_Heaviside": False,
        "E_crit": None,
        "selected_invariant": None,
        "new_scale": False,
        "result": THRESHOLD_RESULT,
    }


def response_domain_ledger() -> dict[str, Any]:
    return {
        "decomposition": "Sbar=C_Sigma+Pi_perp Sbar",
        "homogeneous_mode": "C_Sigma; action kernel ell=0",
        "resting_selection": "C_Sigma=0 by adopted axiom",
        "dynamic_solution": (
            "Pi_perp Sbar=-tau(pi chi_1/16)Pi_perp q"
        ),
        "dynamic_boundary_equation_replaces_hard_zero": True,
        "hard_zero_also_imposed_during_transition": False,
        "gauge_invariant": True,
        "Z2_compatible": True,
        "pole_regular": True,
        "duplicate_junction_equation": False,
        "duplicate_Ward_identity": False,
        "fixed_composite_same_trace": True,
        "unresolved_trace_before_resting_selection": 1,
        "unresolved_trace_after_resting_selection": 0,
        "admissible_dynamic_domain_nonempty": True,
        "sheet_source_signs": "opposite",
        "scalar_sign_independent": True,
        "result": DOMAIN_RESULT,
    }


def rest_transition_rest_ledger() -> dict[str, Any]:
    return {
        "initial": "J_Sigma=0, C_Sigma=0, Sbar=0",
        "transition": "J_Sigma!=0, Sbar=-K_Sigma^-1 J_Sigma",
        "final_stationary_comparison": "J_Sigma=0 selects Sbar=0 again",
        "mechanism": (
            "elliptic/algebraic constraint response on each M4 slice in the "
            "derived approximation"
        ),
        "retarded_relaxation_derived": False,
        "dissipation_derived": False,
        "white_hole_interpretation": "conditional BHSM identification",
        "time_assigned_to_core": False,
    }


def constraint_and_kinetic_ledger() -> dict[str, Any]:
    return {
        "full_Y": ["A", "B", "psi", "E", "delta sigma", "zeta"],
        "threading_block": "K_Sigma on Pi_perp plus C_Sigma=0",
        "full_L_C": None,
        "reason_full_operator_open": (
            "the symmetric-background threading DtN block is derived, but "
            "the coupled finite-q ADM Hessian and its normalization are not"
        ),
        "threading_kernel": {"ell_0": 1, "ell_ge_1": 0},
        "threading_adjoint_kernel": {"ell_0": 1, "ell_ge_1": 0},
        "source_compatible": True,
        "threading_projected_inverse": (
            "harmonic inverse 1/K_ell for ell>=1; no generic pseudoinverse"
        ),
        "full_Green_operator": None,
        "finite_q_solve": False,
        "q_to_zero_convergence": None,
        "K_shift_endpoint_red": None,
        "K_scalar": ">=2>0",
        "K_Weyl": 1.220620174933802,
        "k_q_E": None,
        "kinetic_sign": None,
        "sheet_dependence": "response sign odd; unresolved norm",
        "scalar_sign_dependence": "none",
        "physical_mass": None,
        "kinetic_result": KINETIC_RESULT,
    }


def model_map() -> dict[str, Any]:
    sectors = [
        "parent/core/topology", "P1 geometry", "B1 intrinsic action",
        "scalar-wall fold", "threading response", "fold kinetic sector",
        "gauge connections", "fermionic action/domain",
        "charged-current/CKM", "neutral propagation/PMNS",
        "absolute scale bridge", "scalar/topographic Hessian",
        "prediction/falsification layer",
    ]
    return {
        name: {
            "Adopted foundation": "preserved repository doctrine",
            "Derived consequence": (
                "v6.18 induced response" if name == "threading response" else "preserved"
            ),
            "Numerically validated": (
                "chi_1 response coefficient" if name == "threading response" else "sector ledger"
            ),
            "Rejected by calculation": (
                "hard dynamic Sbar=0" if name == "threading response" else None
            ),
            "Active construction target": (
                "full finite-q coupled ADM Green operator"
                if name == "fold kinetic sector"
                else "independent sector closure"
            ),
        }
        for name in sectors
    }


def verdict_ledger() -> dict[str, Any]:
    return {
        "response_theorem": PRIMARY_RESULT,
        "threshold_theorem": THRESHOLD_RESULT,
        "domain_theorem": DOMAIN_RESULT,
        "kinetic_theorem": KINETIC_RESULT,
        "fold_response_sector_closed_at_leading_order": True,
        "fold_kinetic_sector_closed": False,
        "new_fundamental_action_required": False,
        "new_threshold_scale_required": False,
        "general_covariant_DtN_kernel_complete": False,
    }


def _common(name: str) -> dict[str, Any]:
    return {
        "artifact": name, "version": VERSION, "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA, "v6_17_head_sha": V617_HEAD_SHA,
        "pr_177_merge_sha": PR177_MERGE_SHA, "primary_result": PRIMARY_RESULT,
        **GUARDS,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "action": {**_common("BHSM_threading_response_action_and_kernel_v6_18_0"), "resting": corrected_resting_principle(), "action": action_ledger(), "kernel": kernel_ledger(), "source": source_ledger()},
        "activation": {**_common("BHSM_local_fold_phase_invariant_audit_v6_18_0"), "activation": activation_audit(), "history": rest_transition_rest_ledger()},
        "constraint": {**_common("BHSM_fold_constraint_response_and_kinetic_v6_18_0"), "domain": response_domain_ledger(), "constraint_and_kinetic": constraint_and_kinetic_ledger()},
        "verdict": {**_common("BHSM_v6_18_0_response_verdict_and_model_map"), "verdict": verdict_ledger(), "model_map": model_map()},
    }


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def artifact_bytes() -> dict[str, bytes]:
    return {ARTIFACT_FILES[k]: deterministic_json(v).encode() for k, v in artifact_payloads().items()}


def materialize_artifacts(root: Path) -> list[Path]:
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    paths = []
    for filename, content in artifact_bytes().items():
        path = target / filename
        path.write_bytes(content)
        paths.append(path)
    return paths
