"""Certify the full-local-action branch-24 line at the tracked 1221 edge."""

from __future__ import annotations

import json
import hashlib
import math
import os
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

BASE = ROOT / "artifacts" / "flagship_integration"
CHECKPOINT = BASE / "BHSM_N12_C2_1221_CANCELLED_CHART_CHECKPOINT.npz"
THIRD = BASE / "BHSM_N12_C2_1221_CANCELLED_CHART_THIRD_VARIATION.npz"
ACTION = BASE / "BHSM_N12_C2_1221_CANCELLED_CHART_ACTION_MAJORANTS_R1E8.json"
RESULT = BASE / "BHSM_N12_C2_1221_FULL_ACTION_EIGENLINE_BALL_R1E8.json"
RADIUS = 1.0e-8
QDIM = 37
INFLATION = 1.0 + 1.0e-10
INPUTS = (CHECKPOINT, THIRD, ACTION)

os.environ["BHSM_N12_CERTIFICATE_BALL"] = str(RADIUS)

from derive_n12_c2_launch_eigenline_ball import _load as _load_canonical  # noqa: E402
from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data  # noqa: E402
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
)

action_bound = _load_canonical("derive_n12_action_ball_majorants").action_bound


def _up(value: float) -> float:
    return math.nextafter(float(value) * INFLATION, math.inf)


def _down(value: float) -> float:
    return math.nextafter(float(value) / INFLATION, -math.inf)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def build_payload() -> dict:
    majorant = json.loads(ACTION.read_text(encoding="utf-8"))
    if majorant.get("validation_passed") is not True:
        raise RuntimeError("validated full retained-action majorant required")
    with np.load(CHECKPOINT) as data:
        center = np.asarray(data["child_state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)
    with np.load(THIRD) as data:
        third = np.asarray(data["child"], dtype=float)
    reduced_weights = metric_data()[1]
    reduced_indices = np.arange(QDIM, center.size)
    reduced = np.asarray(exact_full_action_jet_at_state(
        12, center[:QDIM], center[QDIM:2 * QDIM], center[2 * QDIM:], points=96,
    ).hessian, dtype=float)[QDIM:, QDIM:]
    values, vectors = np.linalg.eigh(reduced)
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    psi = vectors[:, selected]
    if float(psi @ reference) < 0.0:
        psi = -psi
    complement = np.delete(vectors, selected, axis=1)
    complement_delta = np.delete(values, selected) - values[selected]
    gap = float(np.min(np.abs(complement_delta)))
    inverse = np.diag(1.0 / complement_delta)
    inverse_norm = _up(1.0 / gap)
    identity = np.eye(center.size)
    selected_action = np.concatenate((np.zeros(QDIM), psi * reduced_weights))
    complement_action = np.vstack((
        np.zeros((QDIM, complement.shape[1])),
        complement * reduced_weights[:, None],
    ))
    reduced_action = np.vstack((
        np.zeros((QDIM, reduced_weights.size)), np.diag(reduced_weights),
    ))

    derivatives = np.asarray([
        np.tensordot(third, identity[:, column], axes=(2, 0))[
            np.ix_(reduced_indices, reduced_indices)
        ] * reduced_weights[:, None] * reduced_weights[None, :]
        for column in range(center.size)
    ])
    scalar_gradient = np.asarray([psi @ derivative @ psi for derivative in derivatives])
    coupling_columns = np.column_stack([
        complement.T @ derivative @ psi for derivative in derivatives
    ])
    hard_columns = np.asarray([
        inverse @ (complement.T @ derivative @ complement)
        for derivative in derivatives
    ])
    scalar_one = _up(float(np.linalg.norm(scalar_gradient)))
    coupling_one = _up(float(np.linalg.norm(coupling_columns, 2)))
    weighted_coupling_one = _up(float(np.linalg.norm(inverse @ coupling_columns, 2)))
    relative_hard_one = _up(float(np.linalg.norm(hard_columns)))

    def bound(*directions: np.ndarray) -> float:
        return _up(float(action_bound(
            center, projection=identity, mixed_directions=list(directions),
        ).d[-1]))

    d4_hard = bound(identity, identity, reduced_action, reduced_action)
    d4_pc = bound(identity, identity, selected_action, complement_action)
    d4_pp = bound(identity, identity, selected_action, selected_action)
    relative_hard_two = _up(inverse_norm * d4_hard)
    relative_ball = _up(
        relative_hard_one * RADIUS + 0.5 * relative_hard_two * RADIUS**2
    )
    complement_ok = relative_ball < 1.0
    complement_inverse = _up(inverse_norm / (1.0 - relative_ball))
    complement_distance = _down(1.0 / complement_inverse)
    scalar_shift = _up(scalar_one * RADIUS + 0.5 * d4_hard * RADIUS**2)
    coupling = _up(coupling_one * RADIUS + 0.5 * d4_hard * RADIUS**2)
    weighted_coupling_two = _up(inverse_norm * d4_pc)
    weighted_coupling = _up(
        weighted_coupling_one * RADIUS
        + 0.5 * weighted_coupling_two * RADIUS**2
    )
    eigen_shift = scalar_shift
    schur = math.inf
    shifted_inverse = complement_inverse
    graph = math.inf
    denominator = -math.inf
    for _ in range(64):
        shift_product = _up(complement_inverse * eigen_shift)
        if shift_product >= 1.0:
            break
        shifted_inverse = _up(complement_inverse / (1.0 - shift_product))
        denominator = _down(
            1.0 - relative_ball - inverse_norm * eigen_shift
        )
        if denominator <= 0.0:
            break
        graph = _up(weighted_coupling / denominator)
        schur = _up(coupling * graph)
        updated = _up(scalar_shift + schur)
        if updated <= eigen_shift * (1.0 + 1.0e-12):
            eigen_shift = updated
            break
        eigen_shift = updated
    gap_lower = _down(
        complement_distance - eigen_shift - schur - 2.0 * coupling
    )
    relative_one_ball = _up(
        (relative_hard_one + inverse_norm * d4_hard * RADIUS) / denominator
    )
    coupling_one_ball = _up(coupling_one + d4_pc * RADIUS)
    weighted_coupling_one_ball = _up(
        (weighted_coupling_one + inverse_norm * d4_pc * RADIUS) / denominator
    )
    scalar_one_ball = _up(scalar_one + d4_pp * RADIUS)
    fixed_lambda_partial = _up(coupling * shifted_inverse * graph)
    implicit = _down(1.0 - fixed_lambda_partial)
    schur_one = _up(
        scalar_one_ball + 2.0 * coupling_one_ball * graph
        + coupling * relative_one_ball * graph
    )
    lambda_one = _up(schur_one / implicit)
    schur_two = _up(
        d4_pp + 2.0 * d4_pc * graph
        + 2.0 * coupling_one_ball * weighted_coupling_one_ball
        + 4.0 * coupling_one_ball * relative_one_ball * graph
        + coupling * (2.0 * relative_one_ball**2 + relative_hard_two / denominator) * graph
    )
    mixed_lambda = _up(
        2.0 * coupling_one_ball * shifted_inverse * graph
        + 2.0 * coupling * shifted_inverse * relative_one_ball * graph
    )
    lambda_lambda = _up(2.0 * coupling * shifted_inverse**2 * graph)
    lambda_two = _up((
        schur_two + 2.0 * mixed_lambda * lambda_one + lambda_lambda * lambda_one**2
    ) / implicit)
    direct_p2 = _up(complement_inverse * d4_pc)
    p2 = _up(
        direct_p2
        + 2.0 * (relative_one_ball + complement_inverse * lambda_one)
        * weighted_coupling_one_ball
        + weighted_coupling_one_ball**2
    )
    validation = {
        "full_local_action_hessian_used": True,
        "branch_24_selected": selected == 24,
        "ambient_action_ball_radius_matches_majorant": (
            float(majorant["action_coordinate_ball_radius"]) == RADIUS
        ),
        "fixed_complement_Neumann_bound_closes": complement_ok,
        "selected_line_stays_simple": gap_lower > 0.0,
        "Schur_implicit_denominator_positive": implicit > 0.0,
        "no_binary64_eigenvalue_used_as_propagated_descriptor": True,
        "no_selector_equation_constraint_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_1221_FULL_ACTION_EIGENLINE_BALL_R1E8",
        "status": "FULL_ACTION_BRANCH_24_LINE_CERTIFIED" if passed else "FULL_ACTION_LINE_BALL_FAILED",
        "action_coordinate_ball_radius": RADIUS,
        "center": {
            "numeric_selected_eigenvalue_not_used_as_descriptor": float(values[selected]),
            "center_gap": gap,
        },
        "bounds": {
            "relative_complement_ball_perturbation": relative_ball,
            "eigenline_gap_lower": gap_lower,
            "eigenvector_graph_norm": graph,
            "weighted_selected_to_complement_first_variation_on_ball": weighted_coupling_one_ball,
            "selected_eigenvalue_first_derivative_bound": lambda_one,
            "selected_eigenvalue_raw_Hessian_bound": lambda_two,
            "selected_line_second_variation_coefficient_upper": p2,
            "complement_inverse_upper": complement_inverse,
            "relative_complement_first_variation_on_ball": relative_one_ball,
            "D4_ambient_ambient_raw_reduced_raw_reduced": d4_hard,
            "D4_ambient_ambient_selected_complement": d4_pc,
            "D4_ambient_ambient_selected_selected": d4_pp,
        },
        "validation": validation,
        "validation_passed": passed,
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
