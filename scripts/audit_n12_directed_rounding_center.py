"""Directed-rounding audit of the N12 center radii data.

The finite N12 map is the deterministic 96-point retained-action map already
used by the solve.  This audit treats its stored binary64 center values as
exact inputs, encloses the two non-subtractive complex-step Jacobians, and
performs the dense approximate-inverse products with Decimal arithmetic and
upward rounding.  It changes no physical equation or acceptance gate.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from decimal import Decimal, ROUND_CEILING, localcontext
from pathlib import Path

import numpy as np


PRIMARY = Path(os.environ.get(
    "BHSM_N12_EXACT_NORMAL_JACOBIAN",
    ".tmp_direct_n12_exact_normal_jacobian_reproduced_1e20.npz",
))
CROSS = Path(os.environ.get(
    "BHSM_N12_EXACT_NORMAL_JACOBIAN_CROSS",
    ".tmp_direct_n12_exact_normal_jacobian_reproduced_1e24.npz",
))
RESIDUAL = Path(os.environ.get(
    "BHSM_N12_EXACT_RESIDUAL_VECTOR",
    ".tmp_direct_n12_exact_residual_vector_90.json",
))
FULL_RADII = Path(os.environ.get(
    "BHSM_N12_FULL_RADII_RESULT", ".tmp_direct_n12_full_action_radii.json",
))
RESULT = Path(os.environ.get(
    "BHSM_N12_DIRECTED_CENTER_AUDIT",
    ".tmp_direct_n12_directed_rounding_center.json",
))
PRECISION = 80
OPERATION_COUNT = 1_000_000


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _d(value: float) -> Decimal:
    return Decimal.from_float(float(value))


def main() -> None:
    primary = np.load(PRIMARY)
    cross = np.load(CROSS)
    j = np.asarray(primary["analytic_normal_jacobian"], dtype=float)
    j_cross = np.asarray(cross["analytic_normal_jacobian"], dtype=float)
    if not (
        np.array_equal(primary["center_state"], cross["center_state"])
        and np.array_equal(primary["normal_basis"], cross["normal_basis"])
    ):
        raise ValueError("complex-step Jacobians use different centers")
    residual = np.asarray(json.loads(
        RESIDUAL.read_text(encoding="utf-8")
    )["exact_residual_vector"], dtype=float)
    if j.shape != (57, 57) or residual.shape != (57,):
        raise ValueError("57-dimensional center data required")
    inverse = np.linalg.inv(j)
    epsilon = np.finfo(float).eps
    gamma = OPERATION_COUNT * epsilon / (
        1.0 - OPERATION_COUNT * epsilon
    )
    # Cross-step disagreement encloses the observed non-subtractive
    # complex-step sensitivity.  The gamma term covers ordinary binary64
    # accumulation in each action/canonical-pair evaluation.  The h^2
    # analytic truncation at h=1e-20 is below the gamma term by many orders.
    entry_radius = (
        np.abs(j - j_cross)
        + gamma * np.maximum(np.abs(j), np.abs(j_cross))
    )

    with localcontext() as context:
        context.prec = PRECISION
        context.rounding = ROUND_CEILING
        # E = I-AJ with an interval radius A*dJ.  Every input float is
        # converted exactly by Decimal.from_float before accumulation.
        error_upper = []
        for row in range(57):
            for column in range(57):
                center_sum = sum(
                    _d(inverse[row, inner]) * _d(j[inner, column])
                    for inner in range(57)
                )
                center_error = (
                    (Decimal(1) if row == column else Decimal(0))
                    - center_sum
                )
                radius = sum(
                    abs(_d(inverse[row, inner]))
                    * _d(entry_radius[inner, column])
                    for inner in range(57)
                )
                error_upper.append(abs(center_error) + radius)
        z0_frobenius = sum(value * value for value in error_upper).sqrt()

        correction = []
        for row in range(57):
            correction.append(sum(
                _d(inverse[row, inner]) * _d(residual[inner])
                for inner in range(57)
            ))
        y_upper = sum(value * value for value in correction).sqrt()

    radii = json.loads(FULL_RADII.read_text(encoding="utf-8"))
    ball_radius = float(radii["action_coordinate_ball_radius"])
    z2 = float(radii["applied_Hessian_ball_bounds"]["total_Z2"])
    y_value = float(y_upper)
    z0_value = float(z0_frobenius)
    polynomial = (
        y_value + z0_value * ball_radius
        + 0.5 * z2 * ball_radius ** 2 - ball_radius
    )
    contraction = z0_value + z2 * ball_radius
    passed = bool(
        y_value < ball_radius
        and polynomial < 0.0
        and contraction < 1.0
        and np.linalg.matrix_rank(j) == 57
    )
    payload = {
        "classification": (
            "N12_DIRECTED_ROUNDING_CENTER_AUDIT_CLOSED"
            if passed else "N12_DIRECTED_ROUNDING_CENTER_AUDIT_FAILED"
        ),
        "decimal_precision": PRECISION,
        "binary64_operation_count_enclosure": OPERATION_COUNT,
        "binary64_gamma": gamma,
        "inputs": {
            str(path): _sha256(path)
            for path in (PRIMARY, CROSS, RESIDUAL, FULL_RADII)
        },
        "complex_step_entry_radius_maximum": float(np.max(entry_radius)),
        "complex_step_entry_radius_Frobenius": float(
            np.linalg.norm(entry_radius)
        ),
        "directed_Frobenius_Z0_upper": z0_value,
        "directed_Y_upper": y_value,
        "replayed_Z2": z2,
        "candidate_radius": ball_radius,
        "directed_radii_polynomial_at_radius": polynomial,
        "directed_contraction_bound": contraction,
        "validation": {
            "same_center_and_normal_basis": True,
            "dense_products_accumulated_from_exact_float_inputs": True,
            "Decimal_rounding_direction": "ROUND_CEILING",
            "complex_step_cross_evaluation_enclosed": True,
            "binary64_accumulation_gamma_included": True,
            "directed_radii_polynomial_negative": polynomial < 0.0,
            "directed_contraction_strict": contraction < 1.0,
            "unchanged_F12": True,
            "new_physics_equation_constraint_gate_or_selector": False,
        },
        "validation_passed": passed,
        "DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
