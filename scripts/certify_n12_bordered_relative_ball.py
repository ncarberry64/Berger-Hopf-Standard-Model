"""Certify the four N12 canonical bordered solves on an action ball.

The proof uses the exact center third variation and the retained-action
fourth-variation majorant.  It controls the relative perturbation
``G(center)^-1 (G(state)-G(center))`` directly, avoiding a condition-number
proxy that discards the bordered structure.  This is certificate machinery
for the unchanged residual only.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np

from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _attachment_jacobian_at_order,
)
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import dimensions
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


ORDER = 12
POINTS = 96
INFLATION = 1.0 + 1.0e-10
CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_CHECKPOINT", ".tmp_direct_n12_corrected_branch_state.npz"
))
THIRD_VARIATION = Path(os.environ.get(
    "BHSM_N12_THIRD_VARIATION_RESULT",
    ".tmp_direct_n12_center_action_third_variations_current.npz",
))
ACTION_MAJORANT = Path(os.environ.get(
    "BHSM_N12_ACTION_MAJORANT_RESULT",
    ".tmp_direct_n12_stable_action_ball_majorants_88_1e8.json",
))
RESULT = Path(os.environ.get(
    "BHSM_N12_BORDERED_BALL_RESULT",
    ".tmp_direct_n12_bordered_relative_ball_88.json",
))


def _up(value: float) -> float:
    return math.nextafter(float(value) * INFLATION, math.inf)


def _down(value: float) -> float:
    return math.nextafter(float(value) / INFLATION, -math.inf)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _symmetric_power(matrix: np.ndarray, power: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(matrix)
    if np.min(values) <= 0.0:
        raise np.linalg.LinAlgError("positive boundary Gram required")
    return vectors @ np.diag(values ** power) @ vectors.T


def _attachment_second_jacobian_bound(
    coordinates: np.ndarray,
    q_weights: np.ndarray,
    column_weights: np.ndarray,
    boundary_row_scaling: np.ndarray,
    radius: float,
) -> float:
    """Bound D^2 of the scaled attachment Jacobian on the ball."""

    signs = (-1.0) ** np.arange(ORDER)
    v_slice = slice(1 + 2 * ORDER, 1 + 3 * ORDER)
    state_covector = signs / q_weights[v_slice]
    column_covector = signs / column_weights[v_slice]
    # |8 sech^2(2s) tanh(2s)| <= 8 globally, so no sampled maximization
    # participates in the proof.
    scalar = 8.0
    row_vector = boundary_row_scaling @ np.asarray([1.0, -1.0])
    return _up(
        scalar
        * float(np.linalg.norm(row_vector))
        * float(np.linalg.norm(column_covector))
        * float(np.linalg.norm(state_covector)) ** 2
    )


def main() -> None:
    size = dimensions(ORDER)
    qdim = size["coordinates"]
    mdim = size["multipliers"]
    state_dimension = 2 * qdim + mdim
    frequencies = spectral_frequencies(ORDER)
    q_weights = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
    m_weights = np.sqrt(1.0 + frequencies["multipliers"] ** 2)
    state_weights = np.concatenate((q_weights, np.ones(qdim), m_weights))

    checkpoint = np.load(CHECKPOINT)
    state = np.asarray(checkpoint["state"], dtype=float)
    jacobian = np.asarray(checkpoint["paired_jacobian"], dtype=float)
    _, singular, vh = np.linalg.svd(jacobian, full_matrices=False)
    normal_basis = vh.T
    if singular[-1] <= 0.0 or normal_basis.shape != (2 * state_dimension, 57):
        raise ValueError("full-rank paired N12 normal Jacobian required")

    third_payload = np.load(THIRD_VARIATION)
    third_center = np.asarray(third_payload["center_state"], dtype=float)
    if not np.array_equal(state, third_center):
        raise ValueError("third variation does not belong to this checkpoint")
    if not np.array_equal(
        state_weights, np.asarray(third_payload["state_weights"], dtype=float)
    ):
        raise ValueError("third-variation action coordinates differ")

    majorant = json.loads(ACTION_MAJORANT.read_text(encoding="utf-8"))
    if majorant.get("validation_passed") is not True:
        raise ValueError("validated retained-action majorant required")
    radius = float(majorant["action_coordinate_ball_radius"])
    sector_majorants = {
        record["sector"]: record for record in majorant["sectors"]
    }

    records = []
    for sector_index, sector in enumerate(("event", "child")):
        offset = sector_index * state_dimension
        sector_state = state[offset:offset + state_dimension]
        coordinates = sector_state[:qdim]
        velocity = sector_state[qdim:2 * qdim]
        multipliers = sector_state[2 * qdim:]
        hessian_raw = np.asarray(exact_full_action_jet_at_state(
            ORDER, coordinates, velocity, multipliers, points=POINTS
        ).hessian, dtype=float)
        hessian = (
            hessian_raw
            / state_weights[:, None]
            / state_weights[None, :]
        )
        third = np.asarray(third_payload[sector], dtype=float)
        sector_normal = normal_basis[offset:offset + state_dimension]
        attachment = _attachment_jacobian_at_order(ORDER, coordinates)
        boundary_scaling = _symmetric_power(
            attachment @ np.diag(1.0 / q_weights ** 2) @ attachment.T,
            -0.5,
        )
        fourth_bound = float(
            sector_majorants[sector][
                "restricted_derivative_operator_majorants_0_through_5"
            ][4]
        )

        for kind, indices, column_weights in (
            ("q", np.arange(qdim), q_weights),
            ("v", np.arange(qdim, 2 * qdim), np.ones(qdim)),
        ):
            constraint_indices = np.arange(2 * qdim, state_dimension)
            form = hessian[np.ix_(indices, indices)]
            constraint = hessian[np.ix_(constraint_indices, indices)]
            combined = np.vstack((
                boundary_scaling @ attachment / column_weights[None, :],
                constraint,
            ))
            bordered = np.block([
                [form, -combined.T],
                [combined, np.zeros((2 + mdim, 2 + mdim))],
            ])
            inverse = np.linalg.inv(bordered)
            inverse_residual = _up(float(np.linalg.norm(
                np.eye(bordered.shape[0]) - inverse @ bordered, 2
            )))
            if inverse_residual >= 1.0:
                raise np.linalg.LinAlgError(
                    "center bordered inverse residual is not contractive"
                )
            inverse_norm = _up(
                float(np.linalg.norm(inverse, 2)) / (1.0 - inverse_residual)
            )

            relative_first = []
            for direction_index in range(normal_basis.shape[1]):
                direction = sector_normal[:, direction_index]
                hessian_derivative = np.tensordot(
                    third, direction, axes=(2, 0)
                )
                form_derivative = hessian_derivative[
                    np.ix_(indices, indices)
                ]
                constraint_derivative = hessian_derivative[
                    np.ix_(constraint_indices, indices)
                ]
                # Both bordered lifts contain the same B(q) attachment
                # rows.  Their column metrics differ, but a state variation
                # changes B in the q- and v-lift systems alike.
                raw_direction = direction[:qdim] / q_weights
                complex_coordinates = coordinates.astype(complex)
                complex_coordinates += 1j * 1.0e-20 * raw_direction
                attachment_derivative = np.imag(
                    _attachment_jacobian_at_order(
                        ORDER, complex_coordinates
                    )
                ) / 1.0e-20
                combined_derivative = np.vstack((
                    boundary_scaling @ attachment_derivative
                    / column_weights[None, :],
                    constraint_derivative,
                ))
                bordered_derivative = np.block([
                    [form_derivative, -combined_derivative.T],
                    [combined_derivative,
                     np.zeros((2 + mdim, 2 + mdim))],
                ])
                relative_first.append(inverse @ bordered_derivative)
            relative_first_bound = _up(float(np.linalg.norm(
                np.asarray(relative_first)
            )))

            attachment_second = _attachment_second_jacobian_bound(
                coordinates,
                q_weights,
                column_weights,
                boundary_scaling,
                radius,
            )
            # One action fourth derivative controls D^2(form), one controls
            # D^2(constraint), and the off-diagonal constraint block occurs
            # twice in the symmetric bordered matrix.  The factor three is
            # a conservative triangle/Frobenius majorant for those blocks.
            bordered_second_bound = _up(
                3.0 * fourth_bound + 2.0 * attachment_second
            )
            relative_second_bound = _up(
                inverse_norm * bordered_second_bound
            )
            relative_ball_perturbation = _up(
                relative_first_bound * radius
                + 0.5 * relative_second_bound * radius ** 2
            )
            certified = relative_ball_perturbation < 1.0
            records.append({
                "sector": sector,
                "lift": kind,
                "center_bordered_smallest_singular_value": float(
                    np.linalg.svd(bordered, compute_uv=False)[-1]
                ),
                "center_bordered_inverse_norm": inverse_norm,
                "center_inverse_residual_bound": inverse_residual,
                "relative_first_variation_bound": relative_first_bound,
                "retained_action_fourth_variation_bound": fourth_bound,
                "attachment_second_jacobian_bound": attachment_second,
                "bordered_second_variation_bound": bordered_second_bound,
                "relative_second_variation_bound": relative_second_bound,
                "relative_ball_perturbation_bound": (
                    relative_ball_perturbation
                ),
                "Neumann_denominator_lower_bound": _down(
                    1.0 - relative_ball_perturbation
                ),
                "bordered_inverse_ball_bound": (
                    _up(inverse_norm / (1.0 - relative_ball_perturbation))
                    if certified else None
                ),
                "certified_invertible_on_ball": certified,
            })

    passed = all(record["certified_invertible_on_ball"] for record in records)
    payload = {
        "classification": (
            "N12_BORDERED_CANONICAL_LIFT_INVERSES_CERTIFIED_ON_ACTION_BALL"
            if passed else
            "N12_BORDERED_CANONICAL_LIFT_BALL_CERTIFICATE_FAILED"
        ),
        "order": ORDER,
        "points": POINTS,
        "action_coordinate_ball_radius": radius,
        "checkpoint": str(CHECKPOINT),
        "checkpoint_SHA256": _sha256(CHECKPOINT),
        "third_variation": str(THIRD_VARIATION),
        "third_variation_SHA256": _sha256(THIRD_VARIATION),
        "action_majorant": str(ACTION_MAJORANT),
        "action_majorant_SHA256": _sha256(ACTION_MAJORANT),
        "normal_rank": int(np.linalg.matrix_rank(jacobian)),
        "normal_smallest_singular_value": float(singular[-1]),
        "records": records,
        "validation": {
            "same_checkpoint_as_third_variation": True,
            "same_action_coordinates": True,
            "retained_action_majorant_validated": True,
            "all_four_bordered_inverses_certified": passed,
            "unchanged_F12": True,
            "new_physics_equation_constraint_or_gate": False,
        },
        "validation_passed": passed,
        "scope": (
            "BORDERED_CANONICAL_LIFT_INVERSES_ONLY;_THE_COMPOSED_"
            "MOMENTUM_AND_ORDERED_EIGENVALUE_F12_HESSIAN_BOUNDS_REMAIN"
        ),
        "DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
