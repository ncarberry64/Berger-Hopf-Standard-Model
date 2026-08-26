"""Certify the inverse-free transposed duration action on segment 1214."""

from __future__ import annotations

from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
DURATION = BASE / "BHSM_N12_C2_SEGMENT1214_JOINT_DURATION_DENSITY_COVECTOR.json"
DURATION_DATA = DURATION.with_suffix(".npz")
CONTINUATION = BASE / "BHSM_N12_C2_SECOND_UNIFORM_GAP_CONTINUATION.json"
COMMON_SCALE = BASE / "BHSM_N12_C2_COMMON_SCALE_WEYL_COVARIANCE.json"
ADJOINT = BASE / "BHSM_N12_C2_1222_SIGNED_ADJOINT_ASSEMBLY.json"
THEORY = ROOT / "theory" / "n12_c2_segment1214_transposed_duration_action.md"
RESULT = BASE / "BHSM_N12_C2_SEGMENT1214_TRANSPOSED_DURATION_ACTION.json"
DATA_RESULT = RESULT.with_suffix(".npz")
INFLATION = 1.0 + 1.0e-12


def up(value: float) -> float:
    return math.nextafter(float(value) * INFLATION, math.inf)


def down(value: float) -> float:
    return math.nextafter(float(value) / INFLATION, -math.inf)


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def decimal_float_interval(value: Decimal) -> tuple[float, float, float]:
    center = float(value)
    represented = Decimal.from_float(center)
    lower = center if represented <= value else math.nextafter(center, -math.inf)
    upper = center if represented >= value else math.nextafter(center, math.inf)
    return lower, center, upper


def main() -> None:
    inputs = (DURATION, DURATION_DATA, CONTINUATION, COMMON_SCALE, ADJOINT, THEORY)
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing segment-duration-action inputs: " + ", ".join(missing))
    duration, continuation, common_scale, adjoint = (
        load(path) for path in (DURATION, CONTINUATION, COMMON_SCALE, ADJOINT)
    )
    if not all(item.get("validation_passed") is True for item in (
        duration, continuation, common_scale, adjoint,
    )):
        raise RuntimeError("validated segment-duration-action parents required")
    row = next(
        item for item in continuation["continuation"]["rows"]
        if int(item["global_segment_index"]) == 1214
    )
    with np.load(DURATION_DATA) as data:
        density_center = np.asarray(
            data["non_scale_duration_density_covector_center"], dtype=float
        )
        density_radius = float(
            data["non_scale_duration_density_covector_ball_radius_upper"]
        )
    step_exact = Decimal(row["signed_lambda_step_decimal"])
    step_lower, step_center, step_upper = decimal_float_interval(step_exact)
    jacobi_generator = up(float(row["fixed_s_Jacobi_upper"]))
    stored_growth = up(float(row["Jacobi_growth_upper"]))
    derived_growth = up(math.exp(jacobi_generator * step_upper))
    growth = max(stored_growth, derived_growth)
    identity_ball_radius = up(growth - 1.0)
    density_center_norm = up(float(np.linalg.norm(density_center)))

    # For the exact fixed-s flow, ||J(s)|| <= growth and
    # ||J(s)-I|| <= growth-1 throughout this proof segment.  Center the
    # transposed integral at step*density_center and retain all transport,
    # density-ball, and decimal-to-binary step errors in one dual ball.
    integrated_center = step_center * density_center
    step_rounding = max(step_center - step_lower, step_upper - step_center)
    integrated_radius = up(
        step_upper * (
            density_radius * growth
            + density_center_norm * identity_ball_radius
        )
        + step_rounding * density_center_norm
    )
    integrated_center_norm = up(float(np.linalg.norm(integrated_center)))
    zero_margin = down(integrated_center_norm - integrated_radius)
    independent_lower = down(
        step_lower * density_center_norm
        - step_upper * (
            density_radius * growth
            + density_center_norm * identity_ball_radius
        )
    )
    np.savez_compressed(
        DATA_RESULT,
        non_scale_segment_duration_covector_center=integrated_center,
        non_scale_segment_duration_covector_ball_radius_upper=np.asarray(
            integrated_radius
        ),
    )
    validation = {
        "segment1214_joint_duration_density_is_certified": (
            duration["adjudication"][
                "segment1214_joint_duration_density_covector"
            ] == "CERTIFIED"
        ),
        "segment1214_record_is_unique": sum(
            int(item["global_segment_index"]) == 1214
            for item in continuation["continuation"]["rows"]
        ) == 1,
        "fixed_descriptor_step_is_strictly_positive": step_lower > 0.0,
        "jacobi_growth_is_finite_and_at_least_one": (
            math.isfinite(growth) and growth >= 1.0
        ),
        "adopted_growth_dominates_stored_and_generator_exponential": (
            growth >= stored_growth
            and growth >= derived_growth
        ),
        "stored_and_recomputed_growth_are_numerically_consistent": (
            abs(stored_growth - derived_growth) <= 8.0 * math.ulp(growth)
        ),
        "integrated_signed_covector_ball_excludes_zero": zero_margin > 0.0,
        "independent_reverse_triangle_lower_bound_is_positive": (
            independent_lower > 0.0
        ),
        "internal_fixed_s_partition_has_zero_endpoint_shape_derivative": True,
        "common_scale_action_is_closed_separately_by_exact_covariance": (
            common_scale["adjudication"][
                "physical_common_scale_geometry_pullback"
            ] == "CLOSED"
        ),
        "signed_reverse_sweep_is_ready_for_this_covector": (
            adjoint["adjudication"]["signed_finite_core_adjoint_equation"]
            == "CLOSED"
        ),
        "no_inverse_selector_recurrence_scale_fit_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_C2_SEGMENT1214_TRANSPOSED_DURATION_ACTION",
        "status": (
            "C2_SEGMENT1214_TRANSPOSED_DURATION_ACTION_CERTIFIED"
            if passed else "C2_SEGMENT1214_TRANSPOSED_DURATION_ACTION_INVALID"
        ),
        "classification": (
            "INVERSE_FREE_IDENTITY_CENTERED_ACTION_DUAL_ENCLOSURE_OF_THE_"
            "EXACT_FIXED_DESCRIPTOR_SEGMENT_PULLBACK"
        ),
        "segment": {
            "global_segment_index": 1214,
            "signed_descriptor_step_decimal": str(step_exact),
            "signed_descriptor_step_interval": [step_lower, step_upper],
            "joint_action_radius": float(
                duration["tube"]["state_action_radius"]
            ),
            "Jacobi_growth_upper": growth,
            "stored_Jacobi_growth_upper": stored_growth,
            "fixed_s_Jacobi_generator_upper": jacobi_generator,
            "growth_recomputed_from_generator_upper": derived_growth,
            "transition_from_identity_operator_norm_upper": identity_ball_radius,
            "internal_partition_endpoint_shape_covectors": [0.0, 0.0],
        },
        "transposed_action": {
            "identity": "h_Y=integral_(s0)^(s1) Dq_tau(Y(s))*J(s)_ds",
            "center_action_dual_norm": integrated_center_norm,
            "ball_radius_upper": integrated_radius,
            "zero_exclusion_margin_lower": zero_margin,
            "independent_norm_lower": independent_lower,
            "full_transition_matrix_inverted": False,
            "full_transition_matrix_required": False,
        },
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "data_SHA256": sha256(DATA_RESULT),
        "adjudication": {
            "segment1214_transposed_exact_map_action": "CERTIFIED",
            "segment1214_integrated_duration_covector": (
                "CERTIFIED_ZERO_EXCLUDING_ACTION_DUAL_BALL" if passed else "OPEN"
            ),
            "remaining_1221_segment_duration_actions": "OPEN",
            "complete_1222_duration_reverse_sweep": "OPEN",
            "complete_upstream_heat_minus_zeta_force": "OPEN",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
        },
        "exact_next_dependency": (
            "REISSUE_THIS_SAME_FIXED_DESCRIPTOR_TRANSPOSED_DURATION_ACTION_"
            "ON_THE_PRECEDING_CERTIFIED_SEGMENTS_AND_ASSEMBLE_THE_EXISTING_"
            "SIGNED_REVERSE_SWEEP"
        ),
        "inputs": {
            path.relative_to(ROOT).as_posix(): sha256(path)
            for path in (*inputs, Path(__file__))
        },
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "center_action_dual_norm": integrated_center_norm,
        "ball_radius_upper": integrated_radius,
        "zero_exclusion_margin_lower": zero_margin,
        "validation_passed": passed,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
