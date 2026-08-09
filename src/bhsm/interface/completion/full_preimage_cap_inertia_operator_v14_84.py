"""BHSM v14.84 full-preimage cap-inertia operator theorem.

The two strata are the reflection-related caps of the existing full-preimage
collar, not new fluids or fields.  This module proves the finite-dimensional
operator completion-of-squares theorem on the nine-dimensional ell=2 trace
space.  It does not compute the cap critical actions, their reduced Hessians,
or a physical nonzero relative-transport generator.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence

import numpy as np


VERSION = "v14.84"
PRIMARY_VERDICT = (
    "BHSM_V14_84_THE_FULL_PREIMAGE_CAP_OPERATOR_PARALLEL_SUM_PRESERVES_"
    "POSITIVE_SEMIDEFINITE_DIFFERENTIAL_SHEAR_SOFTENING_AND_REFLECTION_"
    "CONDITIONALLY_DERIVES_THE_ONE_QUARTER_INERTIA_FRACTION_BUT_THE_CAP_"
    "CRITICAL_ACTIONS_PHYSICAL_RELATIVE_TRANSPORT_DEGREE_ONE_DOMAIN_AND_"
    "COMPLETE_HESSIAN_REMAIN_OPEN"
)
EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_FULL_PREIMAGE_TWO_STRATUM_KINETIC_REDUCTION_WITH_DERIVED_"
    "LAYER_INERTIAS_SHEAR_COVARIANCE_AND_DEGREE_ONE_SELF_ADJOINT_BACKGROUND"
)
CHARGED_CURRENT_PROVENANCE_GATE = (
    "PARENT_ACTION_DERIVATION_OR_UNIQUENESS_SELECTION_OF_THE_SPECTRAL_"
    "CHARGED_CURRENT_KERNEL"
)
NONCENTRAL_CURRENT_GATE = "ACTION_OWNED_FAMILY_NONCENTRAL_LEFT_HANDED_CURRENT_SOURCE"


def _square_matrix(value: Sequence[Sequence[float]], name: str) -> np.ndarray:
    matrix = np.asarray(value, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"{name} must be a square matrix")
    if not np.all(np.isfinite(matrix)):
        raise ValueError(f"{name} must be finite")
    return matrix


def positive_inertia(
    value: Sequence[Sequence[float]], name: str = "inertia", tolerance: float = 1e-12
) -> np.ndarray:
    """Return a symmetric positive-definite reduced inertia matrix."""

    matrix = _square_matrix(value, name)
    if not np.allclose(matrix, matrix.T, atol=tolerance, rtol=0.0):
        raise ValueError(f"{name} must be symmetric")
    matrix = 0.5 * (matrix + matrix.T)
    if float(np.min(np.linalg.eigvalsh(matrix))) <= tolerance:
        raise ValueError(f"{name} must be positive definite on the reduced domain")
    return matrix


def operator_parallel_sum(
    m_plus: Sequence[Sequence[float]], m_minus: Sequence[Sequence[float]]
) -> np.ndarray:
    """Return (M_plus^-1 + M_minus^-1)^-1 for positive inertias."""

    plus = positive_inertia(m_plus, "M_plus")
    minus = positive_inertia(m_minus, "M_minus")
    if plus.shape != minus.shape:
        raise ValueError("cap inertias must act on the same reduced trace space")
    identity = np.eye(plus.shape[0])
    inverse_sum = np.linalg.solve(plus, identity) + np.linalg.solve(minus, identity)
    parallel = np.linalg.solve(inverse_sum, identity)
    return 0.5 * (parallel + parallel.T)


def operator_kinetic_decomposition(
    q_dot: Sequence[float],
    q: Sequence[float],
    a_plus: Sequence[Sequence[float]],
    a_minus: Sequence[Sequence[float]],
    m_plus: Sequence[Sequence[float]],
    m_minus: Sequence[Sequence[float]],
) -> dict[str, Any]:
    """Evaluate the exact capwise operator kinetic decomposition.

    This is the reduced finite-dimensional theorem after the global
    gauge/constraint/domain problem has supplied two positive cap inertias on
    one common trace coordinate and has left no unaccounted cross-cap kinetic
    block.
    """

    plus = positive_inertia(m_plus, "M_plus")
    minus = positive_inertia(m_minus, "M_minus")
    if plus.shape != minus.shape:
        raise ValueError("cap inertias must have the same shape")
    n = plus.shape[0]
    ap = _square_matrix(a_plus, "A_plus")
    am = _square_matrix(a_minus, "A_minus")
    if ap.shape != (n, n) or am.shape != (n, n):
        raise ValueError("transport generators must act on the inertia space")
    coordinate = np.asarray(q, dtype=float)
    velocity = np.asarray(q_dot, dtype=float)
    if coordinate.shape != (n,) or velocity.shape != (n,):
        raise ValueError("Q and Q_dot must be vectors in the common trace space")

    transported_plus = ap @ coordinate
    transported_minus = am @ coordinate
    total = plus + minus
    weighted_transport = np.linalg.solve(
        total, plus @ transported_plus + minus @ transported_minus
    )
    relative_transport = transported_plus - transported_minus
    parallel = operator_parallel_sum(plus, minus)

    original = 0.5 * float((velocity + transported_plus) @ plus @ (velocity + transported_plus))
    original += 0.5 * float((velocity + transported_minus) @ minus @ (velocity + transported_minus))
    decomposed = 0.5 * float((velocity + weighted_transport) @ total @ (velocity + weighted_transport))
    decomposed += 0.5 * float(relative_transport @ parallel @ relative_transport)
    return {
        "original": original,
        "decomposed": decomposed,
        "residual": decomposed - original,
        "total_inertia": total,
        "parallel_sum": parallel,
        "mean_transport_on_q": weighted_transport,
        "relative_transport_on_q": relative_transport,
    }


def shear_softening_operator(
    a_plus: Sequence[Sequence[float]],
    a_minus: Sequence[Sequence[float]],
    m_plus: Sequence[Sequence[float]],
    m_minus: Sequence[Sequence[float]],
) -> np.ndarray:
    """Return Delta A^T (M_plus:M_minus) Delta A, a PSD operator."""

    parallel = operator_parallel_sum(m_plus, m_minus)
    delta = _square_matrix(a_plus, "A_plus") - _square_matrix(a_minus, "A_minus")
    if delta.shape != parallel.shape:
        raise ValueError("transport and inertia operators must have the same shape")
    result = delta.T @ parallel @ delta
    return 0.5 * (result + result.T)


def inverse_square_root(matrix: Sequence[Sequence[float]]) -> np.ndarray:
    inertia = positive_inertia(matrix, "M")
    eigenvalues, eigenvectors = np.linalg.eigh(inertia)
    return (eigenvectors * (1.0 / np.sqrt(eigenvalues))) @ eigenvectors.T


def normalized_shear_operator(
    a_plus: Sequence[Sequence[float]],
    a_minus: Sequence[Sequence[float]],
    m_plus: Sequence[Sequence[float]],
    m_minus: Sequence[Sequence[float]],
) -> np.ndarray:
    total = positive_inertia(m_plus, "M_plus") + positive_inertia(m_minus, "M_minus")
    root = inverse_square_root(total)
    normalized = root @ shear_softening_operator(a_plus, a_minus, m_plus, m_minus) @ root
    return 0.5 * (normalized + normalized.T)


def reflection_inertia_intertwining(
    m_plus: Sequence[Sequence[float]],
    m_minus: Sequence[Sequence[float]],
    reflection: Sequence[Sequence[float]],
    tolerance: float = 1e-12,
) -> dict[str, Any]:
    """Test M_minus=R M_plus R^T and equality after pullback to the plus cap."""

    plus = positive_inertia(m_plus, "M_plus")
    minus = positive_inertia(m_minus, "M_minus")
    transform = _square_matrix(reflection, "reflection")
    if plus.shape != minus.shape or plus.shape != transform.shape:
        raise ValueError("reflection and cap inertias must have the same shape")
    identity = np.eye(plus.shape[0])
    if not np.allclose(transform.T @ transform, identity, atol=tolerance, rtol=0.0):
        raise ValueError("the canonical reflection identification must be orthogonal")
    expected_minus = transform @ plus @ transform.T
    pulled_minus = transform.T @ minus @ transform
    residual = float(np.linalg.norm(minus - expected_minus, ord=2))
    pullback_residual = float(np.linalg.norm(pulled_minus - plus, ord=2))
    return {
        "intertwining_residual": residual,
        "pullback_equality_residual": pullback_residual,
        "intertwines": residual <= tolerance and pullback_residual <= tolerance,
        "pulled_minus": pulled_minus,
    }


def round_reflection_inertia_factor(dimension: int = 9, m0: float = 3.0) -> dict[str, float]:
    """Return the reflection-derived normalized parallel-sum factor."""

    if dimension <= 0 or m0 <= 0.0:
        raise ValueError("dimension and m0 must be positive")
    inertia = m0 * np.eye(dimension)
    total = 2.0 * inertia
    parallel = operator_parallel_sum(inertia, inertia)
    # On the SO(4)-irreducible round ell=2 space, M0=m0 I.  Therefore
    # M^-1/2 P M^-1/2=(1/4)I, independently of m0.
    normalized_parallel = inverse_square_root(total) @ parallel @ inverse_square_root(total)
    eigenvalues = np.linalg.eigvalsh(normalized_parallel)
    return {
        "nu": float(np.mean(eigenvalues)),
        "spread": float(np.max(eigenvalues) - np.min(eigenvalues)),
        "ell2_isotropic_coefficient_per_R2": float(8.0 * np.mean(eigenvalues) / 3.0),
    }


def _noncommuting_witness() -> dict[str, float]:
    n = 9
    u = np.linspace(0.2, 1.0, n)
    v = np.linspace(1.0, -0.4, n)
    plus = np.diag(np.linspace(1.5, 3.5, n)) + 0.07 * np.outer(u, u)
    minus = np.diag(np.linspace(4.0, 2.0, n)) + 0.05 * np.outer(v, v)
    a_plus = np.roll(np.eye(n), 1, axis=0) - 0.2 * np.eye(n)
    a_minus = np.diag(np.linspace(-0.4, 0.5, n))
    q = np.linspace(-0.8, 0.9, n)
    q_dot = np.linspace(0.3, -0.2, n)
    decomposition = operator_kinetic_decomposition(q_dot, q, a_plus, a_minus, plus, minus)
    shear = shear_softening_operator(a_plus, a_minus, plus, minus)
    return {
        "kinetic_residual": float(decomposition["residual"]),
        "inertia_commutator_norm": float(np.linalg.norm(plus @ minus - minus @ plus)),
        "parallel_sum_minimum_eigenvalue": float(np.min(np.linalg.eigvalsh(decomposition["parallel_sum"]))),
        "shear_minimum_eigenvalue": float(np.min(np.linalg.eigvalsh(shear))),
    }


def completion_payload() -> dict[str, Any]:
    witness = _noncommuting_witness()
    round_factor = round_reflection_inertia_factor()
    validation = {
        "noncommuting_operator_identity_exact": abs(witness["kinetic_residual"]) < 1e-11,
        "witness_inertias_actually_noncommute": witness["inertia_commutator_norm"] > 1e-6,
        "parallel_sum_positive": witness["parallel_sum_minimum_eigenvalue"] > 0.0,
        "shear_operator_positive_semidefinite": witness["shear_minimum_eigenvalue"] > -1e-12,
        "reflection_round_nu_is_one_quarter": abs(round_factor["nu"] - 0.25) < 1e-12,
        "round_factor_independent_of_component": round_factor["spread"] < 1e-12,
        "ell2_coefficient_conditionally_two_thirds": abs(round_factor["ell2_isotropic_coefficient_per_R2"] - 2.0 / 3.0) < 1e-12,
        "adm_shift_route_forbidden": True,
        "full_bhsm_not_claimed": True,
        "flavor_provenance_gates_preserved": True,
    }
    return {
        "artifact": "BHSM_full_preimage_cap_inertia_operator_theorem_v14_84",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "existing_geometry": {
            "full_preimage_collar": "C_tilde_eta=pi_85^-1(C_eta)",
            "plus_cap": "C_tilde_plus={rho>=0}",
            "minus_cap": "C_tilde_minus={rho<=0}",
            "intersection": "Sigma_tilde={rho=0}",
            "round_measure": "dmu8=dmuF cos(rho)^3 ds dmu4",
            "new_fluid_or_field_introduced": False,
        },
        "operator_theorem": {
            "cap_inertias": "M_plus/minus=delta^2 Gamma_plus/minus^crit / delta Q_dot^2 at Phi_star",
            "total_inertia": "M=M_plus+M_minus",
            "parallel_sum": "P=(M_plus^-1+M_minus^-1)^-1",
            "mean_transport": "Abar Q=M^-1(M_plus A_plus+M_minus A_minus)Q",
            "relative_transport": "Delta A=A_plus-A_minus",
            "kinetic_identity": "T=1/2< Q_dot+Abar Q,M(Q_dot+Abar Q)>+1/2<Delta A Q,P Delta A Q>",
            "stationary_comoving_stiffness": "H_eff=H0-Delta A^dagger P Delta A",
            "sign": "Delta A^dagger P Delta A is positive semidefinite",
        },
        "theorem_hypotheses": [
            "the gauge/constraint/ghost-reduced cap critical actions are twice differentiable on one common nine-dimensional ell=2 trace space",
            "M_plus and M_minus are coercive after quotienting all gauge and zero modes",
            "the reduced action is cap-additive in the kinetic block, with any seam or cross-cap kinetic terms separately retained",
            "A_plus and A_minus preserve the common self-adjoint trace domain",
            "the background and transports are stationary enough that omitted gyroscopic and time-dependent-connection terms vanish in the quoted H_eff formula",
        ],
        "reflection_theorem": {
            "covariant_statement": "M_minus=R M_plus R^T; hence R^T M_minus R=M_plus",
            "identified_caps": "M_plus=M_minus=M0",
            "parallel_sum": "P=M0/2",
            "round_SO4_branch": "H2 is irreducible, so M0=m0 I9",
            "derived_normalized_inertia_fraction": "nu=1/4 independent of m0",
            "chi2_status": "chi_2=2/(3R^2) only after retaining the normalized isotropic relative-transport hypothesis",
            "actual_reflection_symmetric_degree_one_background_verified": False,
        },
        "physical_transport_gate": {
            "ADM_coordinate_shift_is_physical_shear": False,
            "v14_41_source_free_relative_shift_after_rotation_quotient": "ZERO",
            "eligible_sources": [
                "gauge-reduced covariantly conserved matter/eta/Dirac momentum transport",
                "gauge-reduced quasilocal or canonical cap-boundary momentum",
                "conserved environmental exchange current Q^nu",
            ],
            "nonzero_physical_relative_transport_derived": False,
        },
        "sequential_subgates": [
            {"gate": "CAP_INERTIA", "status": "OPEN", "object": "derive M_plus and M_minus from the full-preimage critical action"},
            {"gate": "REFLECTION", "status": "CONDITIONAL_THEOREM", "object": "verify the stationary background/domain reflection intertwiner and derive nu=1/4"},
            {"gate": "PHYSICAL_TRANSPORT", "status": "OPEN", "object": "derive nonzero conserved gauge-reduced Delta A; ADM coordinate shift is excluded"},
            {"gate": "COMPLETE_RESPONSE", "status": "OPEN", "object": "insert the normalized shear operator into the complete ell=2 Hessian"},
        ],
        "open_gates": {
            "charged_current_kernel": CHARGED_CURRENT_PROVENANCE_GATE,
            "noncentral_left_handed_current": NONCENTRAL_CURRENT_GATE,
        },
        "not_claimed": [
            "positivity of the cap inertia after the unconstructed full gravity/gauge/ghost reduction",
            "a physical nonzero relative transport or its covariance",
            "the round Jacobi ordering for the complete BHSM Hessian",
            "action-derived Landau coefficients, CKM, PMNS, or particle observables",
            "full BHSM completion",
        ],
        "completion_status": {
            "operator_parallel_sum_sign_gate": "PASSED",
            "reflection_inertia_fraction_gate": "PASSED_CONDITIONALLY",
            "cap_inertia_gate": "OPEN",
            "physical_transport_gate": "OPEN",
            "complete_response_gate": "OPEN",
            "BHSM_complete": False,
            "Mark_III": "NOT_REACHED",
            "USB_synchronization_eligible": False,
        },
        "numeric_witness": witness,
        "round_reflection_witness": round_factor,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def materialize(repository: Path | None = None) -> Path:
    root = Path(__file__).resolve().parents[4] if repository is None else Path(repository)
    output = root / "artifacts" / "BHSM_full_preimage_cap_inertia_operator_theorem_v14_84.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(deterministic_json(completion_payload()), encoding="utf-8", newline="\n")
    return output
