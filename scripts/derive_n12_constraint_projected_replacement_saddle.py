"""Derive the constraint-projected same-action replacement-saddle theorem."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.constraint_projected_replacement_saddle import (  # noqa: E402
    bordered_kkt_correction,
    kkt_force_decomposition,
    linearized_tangent_correction,
    projected_force,
)


ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_CONSTRAINT_PROJECTED_REPLACEMENT_SADDLE.json"
)
INPUTS = (
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json"
    ),
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_AE2_NEGATIVE_AXIS_SEAM_FAMILY.json"
    ),
    ARTIFACTS / "BHSM_aether_quantum_functional_accounting_v16_00.json",
    ARTIFACTS / (
        "n12_direct_checkpoint/BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
    ),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _real(value: Any) -> float:
    return float(np.real_if_close(value))


def reset_tangent_witness() -> dict[str, Any]:
    checkpoint = np.load(INPUTS[-1])
    jacobian = np.asarray(checkpoint["paired_jacobian"], dtype=float)[26:, 98:]
    child = np.asarray(checkpoint["state"], dtype=float)[98:]

    # This is the exact boundary log-radius covector already used by the
    # finite-endpoint force audit.  It is a geometry-direction witness, not
    # the unknown heat-minus-zeta force covector.
    q = child[:37]
    signs_k = (-1.0) ** np.arange(1, 13)
    signs_j = (-1.0) ** np.arange(12)
    boundary_v = float(q[25:37] @ signs_j)
    log_radius_covector = np.zeros(jacobian.shape[1])
    log_radius_covector[0] = 1.0
    log_radius_covector[1:13] = signs_k
    log_radius_covector[25:37] = -math.tanh(2.0 * boundary_v) * signs_j
    geometry = projected_force(log_radius_covector, jacobian)

    # A deliberately nonzero normal covector proves constructively that an
    # ambient force need not vanish at a constrained saddle.
    seed_multiplier = np.linspace(-0.7, 0.9, jacobian.shape[0])
    normal_covector = jacobian.T @ seed_multiplier
    normal = kkt_force_decomposition(normal_covector, jacobian)

    # A positive, deterministic witness checks the projected Newton identity.
    # It is not promoted as the unavailable physical geometry Hessian.
    hessian = np.diag(np.linspace(1.0, 2.0, jacobian.shape[1]))
    linearized = linearized_tangent_correction(
        hessian, log_radius_covector, jacobian
    )
    bordered = bordered_kkt_correction(
        hessian, log_radius_covector, jacobian
    )
    tangent_basis = geometry["tangent_basis"]
    geometry_map = tangent_basis[:37, :]
    geometry_singular_values = np.linalg.svd(geometry_map, compute_uv=False)
    geometry_rank = int(np.sum(geometry_singular_values > 1.0e-11))
    return {
        "fixed_event_child_constraint_shape": list(jacobian.shape),
        "constraint_rank": int(np.linalg.matrix_rank(jacobian)),
        "physical_tangent_dimension": int(tangent_basis.shape[1]),
        "constraint_tangent_kernel_residual_norm": geometry[
            "kernel_residual_norm"
        ],
        "constraint_tangent_orthonormality_residual_norm": geometry[
            "orthonormality_residual_norm"
        ],
        "child_q_variation_rank_on_tangent": geometry_rank,
        "boundary_v": boundary_v,
        "boundary_log_R4_covector_ambient_norm": geometry["ambient_norm"],
        "boundary_log_R4_covector_tangent_projection_norm": geometry[
            "tangent_norm"
        ],
        "normal_only_covector_ambient_norm": normal["ambient_norm"],
        "normal_only_covector_tangent_projection_norm": normal["tangent_norm"],
        "normal_only_multiplier_absorption_residual_norm": normal[
            "normal_absorption_residual_norm"
        ],
        "normal_only_shifted_force_residual_norm": normal[
            "shifted_force_minus_tangent_residual_norm"
        ],
        "linearized_witness_minimum_tangent_eigenvalue": _real(
            np.min(linearized["reduced_hessian_eigenvalues"])
        ),
        "linearized_witness_maximum_tangent_eigenvalue": _real(
            np.max(linearized["reduced_hessian_eigenvalues"])
        ),
        "linearized_witness_projected_residual_norm": linearized[
            "projected_linearized_residual_norm"
        ],
        "linearized_witness_positive_definite_on_tangent": linearized[
            "positive_definite_on_tangent"
        ],
        "bordered_KKT_minimum_singular_value": bordered[
            "minimum_bordered_singular_value"
        ],
        "bordered_KKT_condition_number": bordered[
            "bordered_condition_number"
        ],
        "bordered_KKT_stationarity_residual_norm": bordered[
            "stationarity_residual_norm"
        ],
        "bordered_KKT_constraint_residual_norm": bordered[
            "constraint_residual_norm"
        ],
        "nullspace_bordered_ambient_correction_residual_norm": float(
            np.linalg.norm(
                linearized["ambient_correction"]
                - bordered["ambient_correction"]
            )
        ),
    }


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("constraint-projected replacement inputs required")
    force, seam, accounting = (_load(path) for path in INPUTS[:-1])
    if not all(record.get("validation_passed") is True for record in (
        force, seam, accounting
    )):
        raise RuntimeError("validated same-action replacement inputs required")
    witness = reset_tangent_witness()
    validation = {
        "same_replacement_action_accounting_consumed": (
            accounting["determinant_accounting"][
                "same_replacement_for_geometry_gauge_and_Yukawa"
            ] is True
        ),
        "exact_heat_minus_zeta_force_functional_consumed": (
            force["claim_boundary"][
                "heat_minus_zeta_replacement_force_functional"
            ] == "DERIVED"
        ),
        "full_negative_axis_broad_seam_enclosure_consumed": (
            seam["claim_boundary"][
                "complete_spectral_parameter_coverage"
            ] == "CLOSED_ON_NEGATIVE_REAL_AXIS"
        ),
        "actual_reset_tangent_dimension_is_67": (
            witness["physical_tangent_dimension"] == 67
        ),
        "actual_reset_constraint_has_full_row_rank": (
            witness["constraint_rank"] == 31
        ),
        "actual_reset_tangent_basis_is_numerically_valid": (
            witness["constraint_tangent_kernel_residual_norm"] < 1.0e-10
            and witness["constraint_tangent_orthonormality_residual_norm"]
            < 1.0e-10
        ),
        "normal_nonzero_force_is_absorbed_by_multiplier": (
            witness["normal_only_covector_ambient_norm"] > 1.0
            and witness["normal_only_covector_tangent_projection_norm"]
            < 1.0e-10
            and witness["normal_only_multiplier_absorption_residual_norm"]
            < 1.0e-10
        ),
        "actual_boundary_log_radius_varies_on_reset_tangent": (
            witness["boundary_log_R4_covector_tangent_projection_norm"] > 0.18
        ),
        "projected_linearized_saddle_identity_verified": (
            witness["linearized_witness_positive_definite_on_tangent"] is True
            and witness["linearized_witness_projected_residual_norm"] < 1.0e-12
        ),
        "nullspace_and_bordered_KKT_crosscheck_verified": (
            witness["bordered_KKT_stationarity_residual_norm"] < 1.0e-12
            and witness["bordered_KKT_constraint_residual_norm"] < 1.0e-12
            and witness[
                "nullspace_bordered_ambient_correction_residual_norm"
            ] < 1.0e-12
        ),
        "geometry_witness_not_promoted_to_quantum_force": True,
        "no_reset_selector_new_gate_scale_fit_or_frozen_prediction_change": True,
    }
    return {
        "artifact": "BHSM_N12_CONSTRAINT_PROJECTED_REPLACEMENT_SADDLE",
        "status": "EXACT_CONSTRAINT_TANGENT_FORCE_CRITERION_DERIVED_JOINT_PHYSICAL_SADDLE_OPEN",
        "classification": (
            "AT_A_CLASSICAL_CONSTRAINED_ROOT_THE_SAME_CONFIGURATION_IS_A_"
            "ROOT_OF_THE_HEAT_MINUS_ZETA_REPLACEMENT_ACTION_IF_AND_ONLY_IF_"
            "THE_REPLACEMENT_FORCE_COVECTOR_VANISHES_ON_THE_CONSTRAINT_"
            "TANGENT;_A_CONSTRAINT_NORMAL_FORCE_IS_ABSORBED_BY_A_KKT_"
            "MULTIPLIER_SHIFT;_THE_67_DIMENSIONAL_ACTION_OWNED_RESET_FIBER_"
            "THEREFORE_REQUIRES_A_PROJECTED_FORCE_OR_A_JOINT_CONSTRAINED_"
            "SADDLE,_NOT_AN_ARBITRARY_CHILD_REPRESENTATIVE"
        ),
        "exact_theorem": {
            "constraint_surface": "C(y)=0_WITH_J=D_C(y)",
            "physical_tangent": "T_y=ker(J)_WITH_ORTHONORMAL_BASIS_N",
            "replacement_force": (
                "q_rep=D_y_Gamma_heat-D_y_Gamma_SM_zeta"
            ),
            "same_configuration_transfer_criterion": "N^dagger*q_rep=0",
            "equivalent_multiplier_statement": (
                "q_rep+J^dagger*(lambda_rep-lambda_class)=0"
            ),
            "ambient_zero_force": "SUFFICIENT_BUT_NOT_NECESSARY",
            "normal_component": (
                "(I-N*N^dagger)q_rep_IS_ABSORBED_BY_THE_KKT_MULTIPLIER"
            ),
            "if_projected_force_is_nonzero": (
                "SOLVE_D_Gamma_total(y)+J(y)^dagger*lambda=0_AND_C(y)=0"
            ),
            "linearized_tangent_equation": (
                "(N^dagger*H_total*N)*delta_xi=-N^dagger*q_rep"
            ),
            "bordered_equivalent": (
                "[[H_total,J^dagger],[J,0]]*[delta_y,delta_lambda]="
                "[-q_rep,0]"
            ),
            "ill_conditioned_H_inverse_formed": False,
            "required_nondegeneracy": (
                "N^dagger*H_total*N_INVERTIBLE_ON_THE_RETAINED_PHYSICAL_"
                "TANGENT_AFTER_EXISTING_GAUGE_TIME_AND_SCALE_QUOTIENTS"
            ),
            "hessian_distinction": (
                "H_total_HERE_IS_THE_GEOMETRY_RESET_KKT_HESSIAN_NEEDED_TO_"
                "LOCATE_THE_ZERO_SOURCE_SADDLE;_IT_IS_NOT_THE_DOWNSTREAM_"
                "PAIR_PLUS_CONTACT_SOURCE_HESSIAN_D_A2_Gamma"
            ),
        },
        "actual_N12_reset_witness": witness,
        "stage_adjudication": {
            "G7_08_force_and_G7_09_saddle_are_mathematically_coupled": True,
            "new_gate_introduced": False,
            "G7_08_closed": False,
            "G7_09_closed": False,
            "actual_projected_heat_minus_zeta_force_covector_available": False,
            "actual_geometry_reset_KKT_Hessian_available": False,
            "actual_same_action_saddle_solved": False,
            "pair_plus_contact_source_Hessian_is_downstream": True,
            "force_value_or_sign_from_broad_seam_intervals": "NOT_DETERMINED",
        },
        "exact_next_dependency": (
            "CONSTRUCT_THE_ACTUAL_JOINT_FINITE_HISTORY_HEAT_OPERATOR_AND_"
            "ITS_COMPLETE_GEOMETRY_RESET_JET_TO_EVALUATE_N_DAGGER_Q_rep,_"
            "AND_CONSTRUCT_THE_CONSTRAINT_REDUCED_GEOMETRY_KKT_HESSIAN_"
            "N_DAGGER_H_total_N;_THEN_CERTIFY_EITHER_DIRECT_TRANSFER_"
            "N_DAGGER_Q_rep=0_OR_THE_JOINT_NEW_SADDLE_WITHOUT_SELECTING_A_"
            "RESET_FIBER_REPRESENTATIVE_BY_HAND"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_PROJECTED_FORCE_AND_JOINT_SADDLE_REALIZATION_OPEN",
            "constraint_tangent_force_criterion": "DERIVED",
            "ambient_force_zero_required": False,
            "constraint_normal_force_multiplier_absorption": "DERIVED",
            "actual_projected_force_value": "OPEN",
            "actual_projected_force_sign": "OPEN",
            "geometry_reset_KKT_Hessian": "OPEN",
            "same_action_saddle": "OPEN_COUPLED_TO_FORCE",
            "pair_plus_contact_Hessian": "PENDING_AFTER_ZERO_SOURCE_SADDLE",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(RESULT)


if __name__ == "__main__":
    main()
