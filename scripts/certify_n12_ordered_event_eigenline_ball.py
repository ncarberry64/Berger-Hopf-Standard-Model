"""Certify a tracked N12 retained-action eigenline on an action ball.

The selected line is fixed by the validated repaired N6 branch record.  This
script proves a local block-Schur separation estimate for that same line; it
does not introduce an eigenvalue selector or alter the event equation.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np

from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import (
    exact_action_jet_at_state,
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
MIXED_MAJORANT = Path(os.environ.get(
    "BHSM_N12_ORDERED_MIXED_MAJORANT_RESULT",
    ".tmp_direct_n12_ordered_event_mixed_majorants_90_2e11.json",
))
RESULT = Path(os.environ.get(
    "BHSM_N12_ORDERED_EIGENLINE_BALL_RESULT",
    ".tmp_direct_n12_ordered_event_eigenline_ball_88.json",
))
SIDE = os.environ.get("BHSM_N12_EIGENLINE_SIDE", "event").strip().lower()


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


def main() -> None:
    if SIDE not in {"event", "child"}:
        raise ValueError("BHSM_N12_EIGENLINE_SIDE must be event or child")
    size = dimensions(ORDER)
    qdim = size["coordinates"]
    state_dimension = 2 * qdim + size["multipliers"]
    frequencies = spectral_frequencies(ORDER)
    state_weights = np.concatenate((
        np.sqrt(1.0 + frequencies["coordinates"] ** 2),
        np.ones(qdim),
        np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))
    reduced_weights = state_weights[qdim:]
    checkpoint = np.load(CHECKPOINT)
    state = np.asarray(checkpoint["state"], dtype=float)
    branch_reference = np.asarray(
        checkpoint["branch_reference"], dtype=float
    )
    jacobian = np.asarray(checkpoint["paired_jacobian"], dtype=float)
    _, singular, vh = np.linalg.svd(jacobian, full_matrices=False)
    offset = 0 if SIDE == "event" else state_dimension
    sector_normal = vh.T[offset:offset + state_dimension]

    third_payload = np.load(THIRD_VARIATION)
    third_center_key = (
        "center_state" if "center_state" in third_payload.files else "state"
    )
    if not np.array_equal(
        state, np.asarray(third_payload[third_center_key], dtype=float)
    ):
        raise ValueError("third variation does not belong to this checkpoint")
    third_key = SIDE if SIDE in third_payload.files else f"{SIDE}_third"
    third = np.asarray(third_payload[third_key], dtype=float)

    majorant = json.loads(ACTION_MAJORANT.read_text(encoding="utf-8"))
    if majorant.get("validation_passed") is not True:
        raise ValueError("validated retained-action majorant required")
    radius = float(majorant["action_coordinate_ball_radius"])
    mixed_majorant = json.loads(MIXED_MAJORANT.read_text(encoding="utf-8"))
    if mixed_majorant.get("validation_passed") is not True:
        raise ValueError("validated ordered-event mixed majorant required")
    fourth_bound = float(mixed_majorant["bounds"][
        "D4_normal_normal_raw_reduced_raw_reduced"
    ])
    selected_complement_fourth_bound = float(mixed_majorant["bounds"][
        "D4_normal_normal_selected_complement"
    ])
    selected_selected_fourth_bound = float(mixed_majorant["bounds"][
        "D4_normal_normal_selected_selected"
    ])

    sector_state = state[offset:offset + state_dimension]
    hessian = np.asarray(exact_action_jet_at_state(
        ORDER,
        sector_state[:qdim],
        sector_state[qdim:2 * qdim],
        sector_state[2 * qdim:],
        points=POINTS,
    ).hessian, dtype=float)
    eigenvalues, eigenvectors = np.linalg.eigh(hessian)
    selected = int(np.argmax(np.abs(eigenvectors.T @ branch_reference)))
    center_vector = eigenvectors[:, selected]
    complement_indices = [
        index for index in range(eigenvalues.size) if index != selected
    ]
    complement_vectors = eigenvectors[:, complement_indices]
    complement_diagonal = (
        eigenvalues[complement_indices] - eigenvalues[selected]
    )
    center_gap = float(np.min(np.abs(complement_diagonal)))
    center_complement_inverse = np.diag(1.0 / complement_diagonal)
    center_complement_inverse_norm = _up(1.0 / center_gap)

    reduced_indices = np.arange(qdim, state_dimension)
    hessian_derivatives = []
    for column in range(sector_normal.shape[1]):
        full_derivative = np.tensordot(
            third, sector_normal[:, column], axes=(2, 0)
        )
        # The stored third variation is action-normalized in all slots,
        # whereas the ordered event is the eigenvalue of the raw reduced
        # (velocity,multiplier) Hessian.  Restore its two Hessian-slot
        # weights while retaining action coordinates for the state direction.
        hessian_derivatives.append(
            full_derivative[np.ix_(reduced_indices, reduced_indices)]
            * reduced_weights[:, None]
            * reduced_weights[None, :]
        )
    hessian_derivatives = np.asarray(hessian_derivatives)

    scalar_gradient = np.asarray([
        center_vector @ derivative @ center_vector
        for derivative in hessian_derivatives
    ])
    scalar_gradient_bound = _up(float(np.linalg.norm(scalar_gradient)))
    coupling_derivative = np.column_stack([
        complement_vectors.T @ derivative @ center_vector
        for derivative in hessian_derivatives
    ])
    coupling_first_bound = _up(float(np.linalg.norm(
        coupling_derivative, 2
    )))
    weighted_coupling_first_bound = _up(float(np.linalg.norm(
        center_complement_inverse @ coupling_derivative, 2
    )))
    relative_complement_first = np.asarray([
        center_complement_inverse
        @ (complement_vectors.T @ derivative @ complement_vectors)
        for derivative in hessian_derivatives
    ])
    relative_complement_first_bound = _up(float(np.linalg.norm(
        relative_complement_first
    )))
    relative_complement_second_bound = _up(
        center_complement_inverse_norm * fourth_bound
    )
    relative_complement_ball_bound = _up(
        relative_complement_first_bound * radius
        + 0.5 * relative_complement_second_bound * radius ** 2
    )
    complement_at_center_lambda_invertible = (
        relative_complement_ball_bound < 1.0
    )
    if not complement_at_center_lambda_invertible:
        complement_inverse_ball_bound = math.inf
        complement_distance_lower = 0.0
    else:
        complement_inverse_ball_bound = _up(
            center_complement_inverse_norm
            / (1.0 - relative_complement_ball_bound)
        )
        complement_distance_lower = _down(
            1.0 / complement_inverse_ball_bound
        )

    second_remainder = _up(0.5 * fourth_bound * radius ** 2)
    scalar_shift_bound = _up(
        scalar_gradient_bound * radius + second_remainder
    )
    coupling_bound = _up(
        coupling_first_bound * radius + second_remainder
    )
    weighted_coupling_second_bound = _up(
        center_complement_inverse_norm
        * selected_complement_fourth_bound
    )
    weighted_fixed_block_coupling_bound = _up(
        weighted_coupling_first_bound * radius
        + 0.5 * weighted_coupling_second_bound * radius ** 2
    )

    # Close the scalar Schur root bound by fixed-point iteration.  Shifting
    # the complement from the center eigenvalue by delta consumes
    # complement_inverse_ball_bound * delta of its Neumann denominator.
    eigenvalue_shift_bound = scalar_shift_bound
    shifted_complement_inverse_bound = complement_inverse_ball_bound
    schur_correction_bound = math.inf
    for _ in range(32):
        shift_product = _up(
            complement_inverse_ball_bound * eigenvalue_shift_bound
        )
        if shift_product >= 1.0:
            break
        shifted_complement_inverse_bound = _up(
            complement_inverse_ball_bound / (1.0 - shift_product)
        )
        relative_shift_denominator = _down(
            1.0
            - relative_complement_ball_bound
            - center_complement_inverse_norm * eigenvalue_shift_bound
        )
        if relative_shift_denominator <= 0.0:
            break
        graph_norm_bound = _up(
            weighted_fixed_block_coupling_bound
            / relative_shift_denominator
        )
        schur_correction_bound = _up(
            coupling_bound * graph_norm_bound
        )
        updated = _up(scalar_shift_bound + schur_correction_bound)
        if updated <= eigenvalue_shift_bound * (1.0 + 1.0e-12):
            eigenvalue_shift_bound = updated
            break
        eigenvalue_shift_bound = updated

    # Weyl's bound for the fixed block off-diagonal perturbation costs at
    # most ||b|| for each of the two adjacent spectral sets.
    eigenline_gap_lower = _down(
        complement_distance_lower
        - eigenvalue_shift_bound
        - schur_correction_bound
        - 2.0 * coupling_bound
    )
    relative_shift_denominator = _down(
        1.0
        - relative_complement_ball_bound
        - center_complement_inverse_norm * eigenvalue_shift_bound
    )
    graph_norm_bound = _up(
        weighted_fixed_block_coupling_bound
        / relative_shift_denominator
    )
    center_overlap_lower = _down(
        1.0 / math.sqrt(1.0 + graph_norm_bound ** 2)
    )

    # Bound the Hessian of the scalar Schur root in the fixed center
    # eigenbasis.  This retains the small weighted coupling R*Db instead of
    # replacing it by ||R|| ||Db||, which would erase the action-selected
    # spectral structure.
    relative_first_ball_bound = _up(
        (
            relative_complement_first_bound
            + center_complement_inverse_norm * fourth_bound * radius
        ) / relative_shift_denominator
    )
    relative_second_ball_bound = _up(
        relative_complement_second_bound / relative_shift_denominator
    )
    coupling_first_ball_bound = _up(
        coupling_first_bound
        + selected_complement_fourth_bound * radius
    )
    weighted_coupling_first_ball_bound = _up(
        (
            weighted_coupling_first_bound
            + center_complement_inverse_norm
            * selected_complement_fourth_bound
            * radius
        ) / relative_shift_denominator
    )
    scalar_first_ball_bound = _up(
        scalar_gradient_bound
        + selected_selected_fourth_bound * radius
    )
    scalar_second_ball_bound = selected_selected_fourth_bound
    fixed_schur_lambda_derivative = _up(
        coupling_bound * shifted_complement_inverse_bound * graph_norm_bound
    )
    implicit_denominator_lower = _down(
        1.0 - fixed_schur_lambda_derivative
    )
    schur_first_partial_bound = _up(
        scalar_first_ball_bound
        + 2.0 * coupling_first_ball_bound * graph_norm_bound
        + coupling_bound
        * relative_first_ball_bound
        * graph_norm_bound
    )
    selected_eigenvalue_first_derivative_bound = _up(
        schur_first_partial_bound / implicit_denominator_lower
    )
    schur_second_partial_bound = _up(
        scalar_second_ball_bound
        + 2.0 * selected_complement_fourth_bound * graph_norm_bound
        + 2.0
        * coupling_first_ball_bound
        * weighted_coupling_first_ball_bound
        + 4.0
        * coupling_first_ball_bound
        * relative_first_ball_bound
        * graph_norm_bound
        + coupling_bound
        * (
            2.0 * relative_first_ball_bound ** 2
            + relative_second_ball_bound
        )
        * graph_norm_bound
    )
    schur_mixed_state_lambda_bound = _up(
        2.0
        * coupling_first_ball_bound
        * shifted_complement_inverse_bound
        * graph_norm_bound
        + 2.0
        * coupling_bound
        * shifted_complement_inverse_bound
        * relative_first_ball_bound
        * graph_norm_bound
    )
    schur_lambda_second_bound = _up(
        2.0
        * coupling_bound
        * shifted_complement_inverse_bound ** 2
        * graph_norm_bound
    )
    selected_eigenvalue_Hessian_bound = _up(
        (
            schur_second_partial_bound
            + 2.0
            * schur_mixed_state_lambda_bound
            * selected_eigenvalue_first_derivative_bound
            + schur_lambda_second_bound
            * selected_eigenvalue_first_derivative_bound ** 2
        ) / implicit_denominator_lower
    )
    certified = bool(
        complement_at_center_lambda_invertible
        and math.isfinite(schur_correction_bound)
        and eigenline_gap_lower > 0.0
        and center_overlap_lower > 1.0 / math.sqrt(2.0)
    )

    payload = {
        "classification": (
            "N12_CORRECTED_ORDERED_EVENT_EIGENLINE_CERTIFIED_ON_ACTION_BALL"
            if certified else
            "N12_ORDERED_EVENT_EIGENLINE_BALL_CERTIFICATE_FAILED"
        ),
        "sector": SIDE,
        "order": ORDER,
        "points": POINTS,
        "action_coordinate_ball_radius": radius,
        "checkpoint": str(CHECKPOINT),
        "checkpoint_SHA256": _sha256(CHECKPOINT),
        "third_variation": str(THIRD_VARIATION),
        "third_variation_SHA256": _sha256(THIRD_VARIATION),
        "action_majorant": str(ACTION_MAJORANT),
        "action_majorant_SHA256": _sha256(ACTION_MAJORANT),
        "ordered_mixed_majorant": str(MIXED_MAJORANT),
        "ordered_mixed_majorant_SHA256": _sha256(MIXED_MAJORANT),
        "validated_N6_branch_index": int(
            checkpoint["n6_ordered_branch_index"]
        ),
        "transported_N12_eigenline_index": selected,
        "center_selected_eigenvalue_binary64": float(eigenvalues[selected]),
        "center_neighbor_gap": center_gap,
        "normal_rank": int(np.linalg.matrix_rank(jacobian)),
        "normal_smallest_singular_value": float(singular[-1]),
        "bounds": {
            "retained_action_fourth_variation": fourth_bound,
            "selected_scalar_gradient": scalar_gradient_bound,
            "selected_to_complement_coupling_first_variation": (
                coupling_first_bound
            ),
            "weighted_selected_to_complement_first_variation": (
                weighted_coupling_first_bound
            ),
            "selected_complement_fourth_variation": (
                selected_complement_fourth_bound
            ),
            "relative_complement_first_variation": (
                relative_complement_first_bound
            ),
            "relative_complement_second_variation": (
                relative_complement_second_bound
            ),
            "relative_complement_ball_perturbation": (
                relative_complement_ball_bound
            ),
            "complement_inverse_at_center_lambda": (
                complement_inverse_ball_bound
            ),
            "complement_distance_at_center_lambda_lower": (
                complement_distance_lower
            ),
            "selected_scalar_shift": scalar_shift_bound,
            "selected_to_complement_coupling": coupling_bound,
            "weighted_fixed_block_coupling": (
                weighted_fixed_block_coupling_bound
            ),
            "selected_eigenvalue_shift": eigenvalue_shift_bound,
            "Schur_correction": schur_correction_bound,
            "shifted_complement_inverse": (
                shifted_complement_inverse_bound
            ),
            "eigenline_gap_lower": eigenline_gap_lower,
            "eigenvector_graph_norm": graph_norm_bound,
            "transported_center_overlap_lower": center_overlap_lower,
            "ordered_eigenprojector_reduced_resolvent_bound": _up(
                1.0 / eigenline_gap_lower
            ) if certified else None,
            "relative_complement_first_variation_on_ball": (
                relative_first_ball_bound
            ),
            "relative_complement_second_variation_on_ball": (
                relative_second_ball_bound
            ),
            "selected_to_complement_first_variation_on_ball": (
                coupling_first_ball_bound
            ),
            "weighted_selected_to_complement_first_variation_on_ball": (
                weighted_coupling_first_ball_bound
            ),
            "fixed_Schur_implicit_denominator_lower": (
                implicit_denominator_lower
            ),
            "selected_eigenvalue_first_derivative_bound": (
                selected_eigenvalue_first_derivative_bound
            ),
            "selected_eigenvalue_raw_Hessian_bound": (
                selected_eigenvalue_Hessian_bound
            ),
        },
        "validation": {
            "same_checkpoint_as_third_variation": True,
            "retained_action_majorant_validated": True,
            "mixed_raw_Hessian_slot_majorant_validated": True,
            "fixed_complement_Neumann_bound_closed": (
                complement_at_center_lambda_invertible
            ),
            "selected_line_remains_simple": certified,
            "transported_branch_selector_remains_unique": certified,
            "unchanged_ordered_event_equation": True,
            "new_selector_equation_constraint_or_gate": False,
        },
        "validation_passed": certified,
        "scope": (
            "CORRECTED_ORDERED_EVENT_EIGENLINE_AND_REDUCED_RESOLVENT_"
            "ONLY;_THE_COMPLETE_COMPOSED_F12_HESSIAN_BOUND_REMAINS"
        ),
        "DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
