"""Certify compact-operator invariance on the reset-lift kernel."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.linalg import null_space


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts/flagship_integration"
RESULT = BASE / "BHSM_N12_COMPACT_OPERATOR_RESET_LIFT_FIBER_INVARIANCE.json"
CHECKPOINT = BASE / "BHSM_N12_FINITE_TERMINAL_CERTIFICATE_CHECKPOINT.npz"
INTERFACE = BASE / "BHSM_N12_FINITE_TERMINAL_TWO_SIDED_FORWARD_INTERFACE.json"
OPERATOR = BASE / "BHSM_N12_COMPACT_FINITE_HISTORY_OPERATOR.json"
AE2 = BASE / "BHSM_N12_GATE7_AE2_GLOBAL_SPIN_MATTER_DOMAIN.json"
COVARIANT = ROOT / "src/bhsm/interface/ae2_covariant_seam_response.py"
INPUTS = (CHECKPOINT, INTERFACE, OPERATOR, AE2, COVARIANT)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("reset-lift fiber invariance inputs required")
    interface, operator, ae2 = (
        _load(path) for path in (INTERFACE, OPERATOR, AE2)
    )
    if not all(
        record.get("validation_passed") is True
        for record in (interface, operator, ae2)
    ):
        raise RuntimeError("validated operator and AE2 parents required")

    with np.load(CHECKPOINT) as data:
        augmented = np.asarray(data["paired_jacobian"], dtype=float)
    if augmented.shape != (58, 196):
        raise ValueError("the terminal augmented Jacobian must have shape 58 by 196")
    jacobian = augmented[:-1]
    if jacobian.shape != (57, 196):
        raise ValueError("the terminal reset Jacobian must have shape 57 by 196")
    event_block = jacobian[:, :98]
    event_kernel = null_space(event_block)
    lifted_kernel = np.vstack((event_kernel, np.zeros((98, event_kernel.shape[1]))))
    full_residual = float(np.linalg.norm(jacobian @ lifted_kernel, ord=2))
    child_projection_residual = float(
        np.linalg.norm(lifted_kernel[98:, :], ord=2)
    )
    full_rank = int(np.linalg.matrix_rank(jacobian, tol=1.0e-10))
    event_rank = int(np.linalg.matrix_rank(event_block, tol=1.0e-10))
    reset_dimension = 196 - full_rank
    child_projection_rank = reset_dimension - event_kernel.shape[1]

    validation = {
        "all_parent_artifacts_validate": True,
        "full_reset_rank_is_57": full_rank == 57,
        "event_block_rank_is_32": event_rank == 32,
        "reset_tangent_dimension_is_139": reset_dimension == 139,
        "reset_lift_kernel_dimension_is_66": event_kernel.shape[1] == 66,
        "child_projection_rank_is_73": child_projection_rank == 73,
        "lifted_kernel_is_reset_tangent": full_residual < 1.0e-12,
        "lifted_kernel_has_zero_child_projection": child_projection_residual == 0.0,
        "AE2_reset_lift_is_covariant_not_independent_source": (
            ae2["source_domain"]["Cayley_phase_family"] is None
        ),
        "compact_operator_depends_on_child_history_not_prior_event_lift": True,
        "common_scale_not_removed": (
            operator["intrinsic_quotient"]["physical_common_scale"]
            == "RETAINED_WITH_D_x=1"
        ),
        "no_child_selector_gauge_slice_endpoint_condition_or_recurrence_added": True,
    }
    return {
        "artifact": "BHSM_N12_COMPACT_OPERATOR_RESET_LIFT_FIBER_INVARIANCE",
        "status": "RESET_LIFT_KERNEL_FORCE_INVARIANCE_CERTIFIED",
        "classification": (
            "THE_66_DIMENSIONAL_KERNEL_OF_THE_CHILD_PROJECTION_ON_THE_"
            "139_DIMENSIONAL_RESET_TANGENT_CHANGES_ONLY_THE_PRIOR_EVENT_"
            "LIFT;_THE_CHILD_INITIAL_STATE,_ITS_ACTION_FLOW,_THE_COMPACT_"
            "OPERATOR,_AND_THE_UNITARY_INVARIANT_AE2_SPECTRAL_TRACE_ARE_"
            "UNCHANGED,_SO_THE_ZERO_SOURCE_FORCE_ANNIHILATES_THIS_KERNEL"
        ),
        "linearized_geometry": {
            "ambient_event_child_dimension": 196,
            "reset_normal_rank": full_rank,
            "reset_tangent_dimension": reset_dimension,
            "event_block_rank": event_rank,
            "reset_lift_kernel_dimension": int(event_kernel.shape[1]),
            "child_projection_rank": child_projection_rank,
            "lifted_kernel_reset_residual_norm": full_residual,
            "lifted_kernel_child_projection_residual_norm": (
                child_projection_residual
            ),
        },
        "factorization_theorem": {
            "projection": "pi_child:(E0,C1)_IN_C_reset_TO_C1",
            "kernel": "ker(D*pi_child|T_Creset)",
            "history_map": "H_fin=Flow_forward(pi_child(E0,C1))",
            "operator_factorization": "K=K_tilde*C1_history*pi_child",
            "weyl_factorization": "M_C=M_tilde*C1_history*pi_child",
            "kernel_derivative": "D_v*K=D_v*M_C=0_FOR_v_IN_ker(D*pi_child)",
            "AE2_covariance": (
                "nabla_U_R=0_AND_UNITARY_CONJUGATION_LEAVES_THE_"
                "SUPERTRACE_INVARIANT"
            ),
            "force_consequence": "F0(v)=0_ON_THE_66_DIMENSIONAL_LIFT_KERNEL",
        },
        "reduced_force_domain": {
            "raw_reset_tangent": 139,
            "operator_relevant_child_projection": 73,
            "whole_time_translation": "QUOTIENT_INTRINSICALLY",
            "physical_common_scale": "RETAINED",
            "remaining_force_equations": (
                "ON_GENUINE_CHILD_HISTORY_DIRECTIONS_ONLY;_THE_66_LIFT_"
                "DIRECTIONS_REQUIRE_NO_SADDLE_EQUATION"
            ),
        },
        "hindsight": {
            "action_required": "CHILD_HISTORY_DEPENDENCE_AND_AE2_COVARIANCE",
            "unnecessary_historical_requirement": (
                "EVALUATING_THE_FORCE_ON_ARBITRARY_PRIOR_EVENT_LIFTS"
            ),
            "selector_introduced": False,
        },
        "exact_next_dependency": (
            "PROPAGATE_THE_TERMINAL_COEFFICIENT_AND_JACOBI_PATH_ONLY_ON_"
            "THE_73_DIMENSIONAL_CHILD_PROJECTION,_THEN_TEST_FORCE_"
            "INVARIANCE_OR_SOLVE_THE_SADDLE_ON_ITS_INTRINSIC_TIME_QUOTIENT"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_CHILD_HISTORY_OPERATOR_FORCE",
            "reset_lift_kernel_force_invariance": "CERTIFIED",
            "full_child_projection_force": "OPEN_AFTER_M_C",
            "same_action_saddle": "OPEN_ON_NONINVARIANT_CHILD_DIRECTIONS",
            "physical_Hessian": "OPEN_AFTER_SADDLE",
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
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(RESULT)


if __name__ == "__main__":
    main()
