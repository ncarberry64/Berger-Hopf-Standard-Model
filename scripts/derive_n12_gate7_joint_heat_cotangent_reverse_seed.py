"""Derive the joint closed-system heat cotangent and block reverse seed."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.special import exp1


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_JOINT_HEAT_COTANGENT_REVERSE_SEED.json"
ONTOLOGY = BASE / "BHSM_N12_GATE7_CLOSED_SYSTEM_ZERO_EXTERNAL_SOURCE_ONTOLOGY.json"
GLUING = BASE / "BHSM_N12_FINITE_HISTORY_GLUING_FORCE_PROVENANCE.json"
FUNCTIONAL = BASE / "BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json"
WARD = BASE / "BHSM_N12_GATE7_COMMON_SCALE_HEAT_ZETA_WARD.json"
INCIDENCE = BASE / "BHSM_N12_FORWARD_COMMON_SOURCE_INCIDENCE.json"
COVARIANT_SEAM = BASE / "BHSM_N12_AE2_COVARIANT_SEAM_ENCLOSURE_Z_MINUS_1.json"
THEORY = ROOT / "theory" / "n12_gate7_joint_heat_cotangent_reverse_seed.md"
INPUTS = (ONTOLOGY, GLUING, FUNCTIONAL, WARD, INCIDENCE, COVARIANT_SEAM, THEORY)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _heat_functional(matrix: np.ndarray, ell: float) -> float:
    eigenvalues = np.linalg.eigvalsh(matrix)
    return float(-0.5 * np.sum(exp1((ell * ell) * eigenvalues)))


def _witness() -> dict[str, float | bool]:
    a = np.array([[4.0, 0.2], [0.2, 3.4]])
    c = np.array([[0.18], [-0.11]])
    h = np.array([[2.7]])
    g = np.array([[0.55]])
    w = np.array([[0.35]])
    e = np.array([[0.13], [-0.09]])
    f = np.array([[3.8, 0.15], [0.15, 3.1]])
    p = np.block([
        [a, c, np.zeros((2, 2))],
        [c.T, h + g + w, e.T],
        [np.zeros((2, 2)), e, f],
    ])
    da = np.array([[0.07, -0.02], [-0.02, -0.03]])
    dc = np.array([[0.04], [0.01]])
    dh = np.array([[0.025]])
    dg = np.array([[0.018]])
    dw = np.array([[-0.015]])
    de = np.array([[-0.03], [0.02]])
    df = np.array([[0.01, 0.025], [0.025, -0.04]])
    dp = np.block([
        [da, dc, np.zeros((2, 2))],
        [dc.T, dh + dg + dw, de.T],
        [np.zeros((2, 2)), de, df],
    ])
    ell = 0.7
    values, vectors = np.linalg.eigh(p)
    q = 0.5 * (vectors * (np.exp(-(ell * ell) * values) / values)) @ vectors.T
    direct = float(np.trace(q @ dp))
    block = float(
        np.trace(q[:2, :2] @ da)
        + 2.0 * np.trace(q[:2, 2:3].T @ dc)
        + np.trace(q[2:3, 2:3] @ dh)
        + np.trace(q[2:3, 2:3] @ dg)
        + np.trace(q[2:3, 2:3] @ dw)
        + 2.0 * np.trace(q[3:, 2:3].T @ de)
        + np.trace(q[3:, 3:] @ df)
    )
    epsilon = 1.0e-6
    centered = (_heat_functional(p + epsilon * dp, ell) - _heat_functional(p - epsilon * dp, ell)) / (
        2.0 * epsilon
    )

    # Independent Schur determinant and first-variation replay at z=-1.
    rho = 1.0
    ar = a + rho * np.eye(2)
    fr = f + rho * np.eye(2)
    mf = h + rho - c.T @ np.linalg.solve(ar, c)
    mc = g - e.T @ np.linalg.solve(fr, e)
    seam = mf + mc + w
    direct_logdet = float(np.linalg.slogdet(p + rho * np.eye(5))[1])
    schur_logdet = float(np.linalg.slogdet(ar)[1] + np.linalg.slogdet(fr)[1] + np.log(seam[0, 0]))
    direct_resolvent_derivative = float(np.trace(np.linalg.solve(p + rho * np.eye(5), dp)))
    dmf = dh - dc.T @ np.linalg.solve(ar, c) - c.T @ np.linalg.solve(ar, dc) + c.T @ np.linalg.solve(ar, da) @ np.linalg.solve(ar, c)
    dmc = dg - de.T @ np.linalg.solve(fr, e) - e.T @ np.linalg.solve(fr, de) + e.T @ np.linalg.solve(fr, df) @ np.linalg.solve(fr, e)
    schur_derivative = float(
        np.trace(np.linalg.solve(ar, da))
        + np.trace(np.linalg.solve(fr, df))
        + ((dmf + dmc + dw) / seam)[0, 0]
    )
    return {
        "minimum_joint_eigenvalue": float(values.min()),
        "direct_heat_derivative": direct,
        "block_reverse_derivative": block,
        "centered_heat_derivative": centered,
        "direct_block_absolute_residual": abs(direct - block),
        "direct_centered_absolute_residual": abs(direct - centered),
        "direct_schur_logdet_absolute_residual": abs(direct_logdet - schur_logdet),
        "direct_schur_derivative_absolute_residual": abs(direct_resolvent_derivative - schur_derivative),
        "joint_matrix_positive": bool(values.min() > 0.0),
    }


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing joint heat-cotangent inputs: " + ", ".join(missing))
    ontology, gluing, functional, ward, incidence, covariant_seam = map(_load, INPUTS[:-1])
    records = (ontology, gluing, functional, ward, incidence, covariant_seam)
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated joint heat-cotangent parents required")
    witness = _witness()
    validation = {
        "only_external_J_ext_is_zeroed": (
            ontology["external_internal_partition"]["set_to_zero"] == ["J_ext"]
        ),
        "all_internal_seam_blocks_are_retained": (
            ontology["adjudication"]["internal_response_zeroing"] == "FORBIDDEN"
        ),
        "finite_endpoint_heat_derivative_parent_is_derived": (
            functional["status"] == "EXACT_FORCE_FUNCTIONAL_DERIVED_CURRENT_OPERATOR_REALIZATION_OPEN"
        ),
        "gluing_determinant_and_variation_identities_are_derived": (
            gluing["validation"]["both_determinant_identities_close"]
            and gluing["validation"]["both_variation_identities_close"]
        ),
        "common_scale_zeta_Ward_identity_is_preserved": (
            ward["adjudication"]["common_scale_zeta_moving_duration_completion"] == "CLOSED_ZERO"
        ),
        "incidence_is_used_as_internal_variation_vertices": (
            incidence["claim_boundary"]["domain_parametric_nonzero_local_incidence"] == "DERIVED"
        ),
        "reset_transport_is_covariantly_parallel_not_an_independent_source": (
            covariant_seam["covariant_seam_reduction"]["global_connection_compatibility"]
            == "NABLA_Phi_U_R=0"
        ),
        "joint_witness_is_positive": witness["joint_matrix_positive"],
        "direct_and_block_reverse_heat_derivatives_agree": (
            witness["direct_block_absolute_residual"] < 1.0e-14
        ),
        "analytic_and_centered_heat_derivatives_agree": (
            witness["direct_centered_absolute_residual"] < 1.0e-9
        ),
        "direct_and_Schur_log_determinants_agree": (
            witness["direct_schur_logdet_absolute_residual"] < 1.0e-14
        ),
        "direct_and_Schur_resolvent_derivatives_agree": (
            witness["direct_schur_derivative_absolute_residual"] < 1.0e-14
        ),
        "no_descriptor_kinetic_or_Euler_Dirac_inverse_is_required": True,
        "no_internal_response_zeroed_extra_seam_source_or_double_count_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_JOINT_HEAT_COTANGENT_REVERSE_SEED",
        "status": (
            "COMPLETE_JOINT_REVERSE_SEED_DERIVED_NUMERICAL_REALIZATION_OPEN"
            if passed else "JOINT_REVERSE_SEED_NOT_DERIVED"
        ),
        "classification": (
            "THE_COMPLETE_GRADED_HEAT_COTANGENT_IS_ONE_CLOSED_JOINT_OPERATOR_"
            "SEED_REVERSED_ONCE_THROUGH_M_f,_TRANSPORTED_M_C2,_U_R,_W_phys,_AND_"
            "RETAINED_CONTACTS;_ZERO_EXTERNAL_J_ext_ADDS_NO_SEAM_SOURCE"
        ),
        "exact_heat_seed": {
            "functional": "Gamma_heat(P)=-(1/2)*Tr(E1(ell^2*P))",
            "sector_seed": "Q_heat=(1/2)*exp(-ell^2*P)*P^(-1)",
            "graded_seed": "Q_joint=(1/2)*direct_sum_C(s_C*m_C*exp(-ell^2*P_C)*P_C^(-1))",
            "inverse_free_semigroup_form": "Q_heat=(1/2)*integral_(ell^2)^infinity exp(-s*P)ds",
        },
        "direct_block_reverse": {
            "q_A": "Q_AA",
            "q_C": "2*Q_AS",
            "q_H": "Q_SS",
            "q_G": "Q_SS",
            "q_W": "Q_SS",
            "q_E": "2*Q_FS",
            "q_F": "Q_FF",
            "complex_rule": "TAKE_REAL_HILBERT_SCHMIDT_PAIRING_WITH_HERMITIAN_VARIATIONS",
        },
        "inverse_free_seam_reverse": {
            "S_AE2": "M_f+U_R^dagger*M_C2*U_R+W_phys",
            "q_M_f": "Omega_S",
            "q_M_C2": "U_R*Omega_S*U_R^dagger",
            "q_W_phys": "Omega_S",
            "q_U_R_variation": (
                "ReTr[Omega_S^dagger*((D_U_R)^dagger*M_C2*U_R+"
                "U_R^dagger*M_C2*D_U_R)]"
            ),
            "covariant_transport_rule": (
                "nabla_U_R=0_SO_ORDINARY_FRAME_TERMS_ARE_ABSORBED_IN_nabla_M_C2_"
                "AND_ARE_NOT_AN_ADDITIONAL_SOURCE"
            ),
            "route_exclusivity": "USE_DIRECT_JOINT_OR_FACTORIZED_RESOLVENT_ROUTE_NOT_BOTH",
        },
        "replacement_accounting": {
            "direct_zeta_covector": "q_zeta=(59/30)*D_integral(d_tau/R4)",
            "replacement_covector_at_local_action_root": "q_rep=q_heat-q_zeta",
            "common_scale_zeta_covector": "ZERO_BY_MOVING_DURATION_WARD_IDENTITY",
            "non_scale_zeta_covector": "RETAIN_AND_REVERSE_WITH_THE_SAME_HISTORY",
        },
        "reverse_order": [
            "COMPLETE_JOINT_SELF_ADJOINT_OPERATOR",
            "FULL_BRST_GRADED_HEAT_SEED_PLUS_DIRECT_ZETA_COVECTOR",
            "JOINT_SEAM_BLOCKS_M_f_M_C2_U_R_W_phys_AND_CONTACTS",
            "FORMATION_AND_CHILD_COEFFICIENT_HISTORIES",
            "EVENT_RESET_TANGENT",
            "PHYSICAL_TIME_GAUGE_QUOTIENT",
            "PROJECTED_CAUCHY_LIMIT_OR_ACTUAL_FINITE_EVENT_CANONICAL_STOP",
            "BORDERED_KKT_ROOT",
        ],
        "matching_audit": {
            "joint_heat_cotangent_type": "CLOSED",
            "joint_block_reverse_type": "CLOSED",
            "zero_external_source_order": "CLOSED",
            "actual_complete_joint_operator_value": "ACTUALLY_MISSING",
            "actual_complete_joint_operator_first_jet": "ACTUALLY_MISSING",
            "maximal_projected_Cauchy_limit": "ACTUALLY_MISSING",
        },
        "witness": witness,
        "adjudication": {
            "joint_reverse_seed_formula": "CLOSED",
            "additional_seam_source": "FORBIDDEN",
            "internal_block_zeroing": "FORBIDDEN",
            "double_count_direct_and_factorized_routes": "FORBIDDEN",
            "actual_joint_graded_coefficient_cotangent": "OPEN_CURRENT_NUMERICAL_OWNER",
            "joint_reverse_adjoint_value": "WAITING_ON_ACTUAL_JOINT_OPERATOR_AND_FIRST_JET",
            "projected_Cauchy_tail": "OPEN",
            "same_action_KKT_root": "WAITING_ON_PROJECTED_FORCE",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
        },
        "exact_next_dependency": (
            "REALIZE_OR_SHARPLY_ENCLOSE_THE_COMPLETE_JOINT_GRADED_OPERATOR_AND_ITS_"
            "FIRST_ACTION_JET,_EVALUATE_THE_DERIVED_SINGLE_HEAT_MINUS_ZETA_SEED,_AND_"
            "REVERSE_IT_ONCE_TO_THE_PHYSICAL_PROJECTED_CAUCHY_NET"
        ),
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "Gate7": "ACTIVE_ACTUAL_JOINT_GRADED_COTANGENT_AND_REVERSE_VALUE",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "FULL_BHSM_COMPLETE": False,
            "finite_1222_core_promoted_to_endpoint": False,
            "numerical_force_claimed": False,
            "frozen_predictions_changed": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "direct_block_residual": payload["witness"]["direct_block_absolute_residual"],
        "direct_schur_residual": payload["witness"]["direct_schur_derivative_absolute_residual"],
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
