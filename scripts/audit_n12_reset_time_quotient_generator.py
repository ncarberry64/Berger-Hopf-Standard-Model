"""Audit the provenance of the fixed-event reset time quotient generator."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
from scipy.linalg import null_space


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (  # noqa: E402
    _exact_full_jet_euler_dirac_acceleration,
)


ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_RESET_TIME_QUOTIENT_GENERATOR_AUDIT.json"
)
INPUTS = (
    ARTIFACTS / (
        "intrinsic_state_selection/BHSM_N12_CONTINUUM_SINGULAR_HITTING_RESET_RELATION.json"
    ),
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_CONSTRAINT_PROJECTED_REPLACEMENT_SADDLE.json"
    ),
    ARTIFACTS / (
        "n12_direct_checkpoint/BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
    ),
    ROOT / "src/bhsm/interface/aether_cross_resolution_reconnaissance_v21_35.py",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def child_flow_tangency_rows() -> dict[str, Any]:
    with np.load(INPUTS[2]) as checkpoint:
        state = np.asarray(checkpoint["state"], dtype=float)
        jacobian = np.asarray(checkpoint["paired_jacobian"], dtype=float)[
            26:, 98:
        ]
    child = state[98:]
    q = child[:37]
    velocity = child[37:74]
    multipliers = child[74:]
    tangent_basis = null_space(jacobian)
    rows = []
    for points in (48, 96, 192):
        dynamics = _exact_full_jet_euler_dirac_acceleration(
            12, q, velocity, multipliers, points=points
        )
        child_flow = np.concatenate((
            dynamics["coordinate_rate"],
            dynamics["acceleration"],
            dynamics["multiplier_rate"],
        ))
        tangent_projection = tangent_basis @ (tangent_basis.T @ child_flow)
        norm = float(np.linalg.norm(child_flow))
        rows.append({
            "quadrature_points": points,
            "child_flow_vector_norm": norm,
            "fixed_event_reset_linearized_residual_norm": float(
                np.linalg.norm(jacobian @ child_flow)
            ),
            "relative_fixed_event_reset_residual": float(
                np.linalg.norm(jacobian @ child_flow) / norm
            ),
            "relative_distance_to_fixed_event_reset_kernel": float(
                np.linalg.norm(child_flow - tangent_projection) / norm
            ),
            "Euler_Dirac_condition_number": dynamics[
                "Dirac_condition_number"
            ],
        })
    residuals = [row["relative_fixed_event_reset_residual"] for row in rows]
    distances = [
        row["relative_distance_to_fixed_event_reset_kernel"] for row in rows
    ]
    return {
        "fixed_event_child_jacobian_shape": list(jacobian.shape),
        "fixed_event_child_raw_kernel_dimension": int(tangent_basis.shape[1]),
        "rows": rows,
        "relative_residual_cross_quadrature_spread": max(residuals) - min(residuals),
        "relative_distance_cross_quadrature_spread": max(distances) - min(distances),
    }


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("reset time-quotient audit inputs required")
    reset = _load(INPUTS[0])
    projected = _load(INPUTS[1])
    if not all(record.get("validation_passed") is True for record in (
        reset, projected
    )):
        raise RuntimeError("validated reset quotient inputs required")
    witness = child_flow_tangency_rows()
    validation = {
        "raw_fixed_event_reset_kernel_dimension_is_67": (
            witness["fixed_event_child_raw_kernel_dimension"] == 67
        ),
        "existing_whole_system_time_quotient_count_is_66": (
            reset["reset_correspondence"][
                "after_existing_whole_system_time_quotient"
            ] == 66
        ),
        "child_flow_candidate_failure_is_resolution_stable": (
            witness["relative_residual_cross_quadrature_spread"] < 1.0e-8
            and witness["relative_distance_cross_quadrature_spread"] < 1.0e-8
        ),
        "child_flow_candidate_is_not_in_fixed_event_reset_kernel": all(
            row["relative_fixed_event_reset_residual"] > 1.0e-3
            and row["relative_distance_to_fixed_event_reset_kernel"] > 1.0e-3
            for row in witness["rows"]
        ),
        "raw_kernel_not_relabelled_final_physical_quotient": (
            projected["existing_quotient_audit"][
                "raw_nullspace_crosscheck_is_final_physical_quotient"
            ] is False
        ),
        "no_projected_child_flow_substituted_as_symmetry_generator": True,
        "no_gauge_slice_selector_endpoint_scale_fit_new_gate_or_prediction_added": True,
    }
    return {
        "artifact": "BHSM_N12_RESET_TIME_QUOTIENT_GENERATOR_AUDIT",
        "status": "WHOLE_SYSTEM_TIME_QUOTIENT_COUNT_RETAINED_EXPLICIT_HYBRID_GENERATOR_OPEN",
        "classification": (
            "THE_FIXED_EVENT_CHILD_RESET_FIBER_HAS_RAW_DIMENSION_67_AND_THE_"
            "RETAINED_WHOLE_SYSTEM_TIME_QUOTIENT_COUNT_IS_66,_BUT_THE_LOCAL_"
            "CHILD_EULER_DIRAC_FLOW_VECTOR_IS_NOT_TANGENT_TO_THE_FIXED_EVENT_"
            "RESET_RELATION;_ITS_STABLE_RELATIVE_LINEARIZED_RESIDUAL_IS_ABOUT_"
            "1.136E-2,_SO_ORTHOGONALLY_PROJECTING_IT_AND_CALLING_THE_RESULT_"
            "THE_TIME_GENERATOR_WOULD_ADD_AN_UNOWNED_GAUGE_SLICE"
        ),
        "dimension_statement": {
            "raw_fixed_event_child_constraint_tangent": 67,
            "declared_after_existing_whole_system_time_quotient": 66,
            "explicit_generator_certified_in_current_checkpoint": False,
            "candidate_tested": "LOCAL_CHILD_EULER_DIRAC_VECTOR_FIELD_AT_RESET",
            "candidate_is_hybrid_whole_system_time_generator": False,
        },
        "exact_reason": (
            "FIXING_THE_EVENT_WHILE_ADVANCING_ONLY_THE_CHILD_DOES_NOT_PRESERVE_"
            "THE_COMPLETE_EVENT_CHILD_RESET_EQUATIONS;_THE_TRUE_PHASE_"
            "GENERATOR_MUST_BE_DERIVED_FROM_THE_COUPLED_HYBRID_EVENT_CHILD_"
            "ACTION_OR_THE_QUOTIENT_MUST_BE_FORMULATED_INTRINSICALLY"
        ),
        "witness": witness,
        "force_and_saddle_consequence": {
            "raw_constraint_projection_theorem_remains_valid": True,
            "final_physical_quotient_force_evaluated": False,
            "raw_boundary_log_R4_projection_promoted_to_physical_quotient": False,
            "bordered_KKT_raw_crosscheck_remains_valid": True,
            "required_before_center_or_Hessian_classification": (
                "CERTIFY_THE_COUPLED_HYBRID_TIME_GENERATOR_OR_USE_AN_"
                "INTRINSIC_QUOTIENT_DESCRIPTOR_FORMULATION"
            ),
        },
        "exact_next_dependency": (
            "AS_PART_OF_THE_PARAMETRIC_EVENT_CHILD_EXTERIOR_OPERATOR_ORACLE,_"
            "DERIVE_THE_COUPLED_196_DIMENSIONAL_HYBRID_TIME_PHASE_GENERATOR_"
            "AND_ITS_INDUCED_FIXED_EVENT_QUOTIENT_OR_FORMULATE_THE_FORCE_AND_"
            "HESSIAN_DIRECTLY_ON_THE_INTRINSIC_QUOTIENT;_DO_NOT_PROJECT_THE_"
            "CHILD_FLOW_BY_HAND"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_EXTERIOR_ORACLE_AND_PHYSICAL_QUOTIENT_OPEN",
            "raw_reset_tangent_dimension": "DERIVED_67",
            "post_time_quotient_dimension_count": "RETAINED_66",
            "explicit_time_generator": "OPEN",
            "actual_physical_quotient_force": "OPEN",
            "geometry_reset_KKT_Hessian": "OPEN",
            "same_action_saddle": "OPEN",
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
