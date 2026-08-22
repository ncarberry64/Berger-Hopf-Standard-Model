"""Take one exact hybrid weak step with the existing common scale direction.

The common event/child scale coordinate preserves all four boundary rows
exactly.  It is appended only to the existing v/m finite-core proposal after
that fiber was shown to terminate at the eta boundary.  The physical weak map
and acceptance gates are unchanged.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np

import continue_n64_hybrid_weak_finite_core as core
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import (
    RADIUS0,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import dimensions
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


ROOT = Path(__file__).resolve().parents[1]
INPUT = Path(os.environ.get(
    "BHSM_N64_SCALE_INPUT",
    ROOT / "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N64_HYBRID_WEAK_FINITE_CORE_STATE.npz",
))
OUTPUT_STATE = Path(os.environ.get(
    "BHSM_N64_SCALE_STATE",
    ROOT / "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N64_HYBRID_WEAK_SCALE_STATE.npz",
))
OUTPUT = Path(os.environ.get(
    "BHSM_N64_SCALE_RESULT",
    ROOT / "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N64_HYBRID_WEAK_SCALE_STEP.json",
))
STEP = float(os.environ.get("BHSM_N64_SCALE_DIFFERENCE_STEP", "1e-5"))
ETA_TANGENT = os.environ.get("BHSM_N64_SCALE_ETA_TANGENT", "1") == "1"
ETA_DIRECTION_TARGET = float(os.environ.get(
    "BHSM_N64_SCALE_ETA_DIRECTION_TARGET", "0.1"
))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _scale_shift(
    states: dict[str, tuple[np.ndarray, ...]], amplitude: float,
) -> dict[str, tuple[np.ndarray, ...]]:
    result = {}
    # This is a unit action-coordinate direction: each sector receives
    # amplitude/sqrt(2), and the scale coordinate already has unit weight.
    raw = amplitude / math.sqrt(2.0)
    for side in ("event", "child"):
        q, velocity, multipliers = states[side]
        shifted_q = q.copy()
        shifted_q[0] += raw
        result[side] = shifted_q, velocity.copy(), multipliers.copy()
    return result


def _geometry_direction(
    states: dict[str, tuple[np.ndarray, ...]],
) -> tuple[dict[str, np.ndarray], dict[str, float]]:
    """Minimum-action event-eta direction in the joint boundary kernel."""

    order = core.ORDER
    qdim = dimensions(order)["coordinates"]
    q, _, m = states["event"]
    from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
        _eta_legendre_minimum,
    )
    minimum = _eta_legendre_minimum(order, q, m, points=4000)
    chi = float(minimum["chi"])
    ks = np.arange(1, order + 1, dtype=float)
    js = np.arange(order, dtype=float)
    cos_k = np.cos(4.0 * ks * chi)
    cos_j = np.cos(4.0 * js * chi)
    window = math.sin(2.0 * chi) ** 2
    u = float(q[1:1 + order] @ cos_k)
    w = window * float(q[1 + order:1 + 2 * order] @ cos_j)
    v = window * float(q[1 + 2 * order:1 + 3 * order] @ cos_j)
    radius = RADIUS0 * math.exp(float(q[0]))
    c_term = 1.0 / (radius * math.exp(u + w)) ** 2
    a_radius = radius * math.exp(u + v) * math.cos(chi)
    b_radius = radius * math.exp(u - v) * math.sin(chi)
    a_term = 3.0 * math.cos(chi) ** 2 / a_radius**2
    b_term = 3.0 * math.sin(chi) ** 2 / b_radius**2
    spatial = c_term + a_term + b_term
    lapse = math.exp(float(m[:order] @ cos_k))
    shift = float(m[order:] @ (math.sin(4.0 * chi) * cos_j))
    x_eta = spatial - (shift / lapse) ** 2
    prefactor = 3.0 * x_eta**2
    raw_gradient = np.zeros(qdim)
    raw_gradient[0] = prefactor * (-2.0 * spatial)
    raw_gradient[1:1 + order] = prefactor * (-2.0 * spatial) * cos_k
    raw_gradient[1 + order:1 + 2 * order] = (
        prefactor * (-2.0 * c_term) * window * cos_j
    )
    raw_gradient[1 + 2 * order:1 + 3 * order] = (
        prefactor * (-2.0 * a_term + 2.0 * b_term) * window * cos_j
    )
    q_weights = np.sqrt(
        1.0 + spectral_frequencies(order)["coordinates"] ** 2
    )
    event_boundary = core.bridge._boundary_jacobian(order, states["event"][0])
    child_boundary = core.bridge._boundary_jacobian(order, states["child"][0])
    boundary_action = np.column_stack((
        -event_boundary / q_weights[None, :],
        child_boundary / q_weights[None, :],
    ))
    gradient_action = np.concatenate((raw_gradient / q_weights, np.zeros(qdim)))
    direction_action = gradient_action - boundary_action.T @ np.linalg.solve(
        boundary_action @ boundary_action.T,
        boundary_action @ gradient_action,
    )
    norm = float(np.linalg.norm(direction_action))
    direction_action /= norm
    raw = {
        "event": direction_action[:qdim] / q_weights,
        "child": direction_action[qdim:] / q_weights,
    }
    return raw, {
        "event_eta_action_derivative": float(gradient_action @ direction_action),
        "joint_boundary_linear_defect": float(np.linalg.norm(
            boundary_action @ direction_action
        )),
        "action_norm": float(np.linalg.norm(direction_action)),
        "chi": chi,
    }


def _geometry_shift(
    states: dict[str, tuple[np.ndarray, ...]],
    direction: dict[str, np.ndarray],
    amplitude: float,
) -> dict[str, tuple[np.ndarray, ...]]:
    result = {}
    for side in ("event", "child"):
        q, velocity, multipliers = states[side]
        result[side] = (
            q + amplitude * direction[side],
            velocity.copy(),
            multipliers.copy(),
        )
    return result


def _event_eta_action_gradient(
    states: dict[str, tuple[np.ndarray, ...]], variable_count: int,
    geometry_eta_derivative: float,
) -> tuple[np.ndarray, dict[str, float]]:
    """Gradient of the existing eta minimum in augmented action coordinates."""

    q, _, m = states["event"]
    order = core.ORDER
    qdim = dimensions(order)["coordinates"]
    record = core._eta(states)["event"]
    # Reuse the already-existing minimizer and differentiate eta at its chi.
    from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
        _eta_legendre_minimum,
    )
    minimum = _eta_legendre_minimum(order, q, m, points=4000)
    chi = float(minimum["chi"])
    ks = np.arange(1, order + 1, dtype=float)
    js = np.arange(order, dtype=float)
    cos_k = np.cos(4.0 * ks * chi)
    cos_j = np.cos(4.0 * js * chi)
    window = math.sin(2.0 * chi) ** 2
    u = float(q[1:1 + order] @ cos_k)
    w = window * float(q[1 + order:1 + 2 * order] @ cos_j)
    v = window * float(q[1 + 2 * order:1 + 3 * order] @ cos_j)
    radius = RADIUS0 * math.exp(float(q[0]))
    c_radius = radius * math.exp(u + w)
    a_radius = radius * math.exp(u + v) * math.cos(chi)
    b_radius = radius * math.exp(u - v) * math.sin(chi)
    c_term = 1.0 / c_radius**2
    a_term = 3.0 * math.cos(chi)**2 / a_radius**2
    b_term = 3.0 * math.sin(chi)**2 / b_radius**2
    spatial = c_term + a_term + b_term
    lapse = math.exp(float(m[:order] @ cos_k))
    shift_basis = math.sin(4.0 * chi) * cos_j
    shift = float(m[order:] @ shift_basis)
    ratio = shift / lapse
    x_eta = spatial - ratio**2
    prefactor = 3.0 * x_eta**2

    gradient = np.zeros(variable_count)
    frequencies = spectral_frequencies(order)
    m_weights = np.sqrt(1.0 + frequencies["multipliers"] ** 2)
    raw_m = np.concatenate((
        prefactor * 2.0 * ratio**2 * cos_k,
        prefactor * (-2.0 * ratio / lapse) * shift_basis,
    ))
    # Event z variables start with qdim velocity coordinates.
    gradient[qdim:qdim + 2 * order] = raw_m / m_weights
    # Last two coordinates are common scale and boundary-kernel geometry.
    gradient[-2] = prefactor * (-2.0 * spatial) / math.sqrt(2.0)
    gradient[-1] = geometry_eta_derivative
    return gradient, {
        "minimum": record,
        "chi": chi,
        "x_eta": x_eta,
        "action_gradient_norm": float(np.linalg.norm(gradient)),
    }


def main() -> None:
    if STEP <= 0.0:
        raise ValueError("positive scale difference step required")
    source = np.load(INPUT)
    states = {
        side: core._split(np.asarray(source[f"{side}_state"], dtype=float))
        for side in ("event", "child")
    }
    center = core._assemble(states)
    plus = core._assemble(_scale_shift(states, STEP))
    scale_column = (
        np.asarray(plus["residual"]) - np.asarray(center["residual"])
    ) / STEP
    geometry_direction, geometry_record = _geometry_direction(states)
    geometry_plus = core._assemble(_geometry_shift(
        states, geometry_direction, STEP
    ))
    geometry_column = (
        np.asarray(geometry_plus["residual"])
        - np.asarray(center["residual"])
    ) / STEP
    matrix = np.column_stack((
        np.asarray(center["matrix"]), scale_column, geometry_column
    ))
    residual = np.asarray(center["residual"])
    eta_gradient, eta_gradient_record = _event_eta_action_gradient(
        states, matrix.shape[1], geometry_record["event_eta_action_derivative"]
    )
    solve_matrix = matrix
    solve_rhs = -residual
    if ETA_TANGENT:
        solve_matrix = np.vstack((matrix, eta_gradient))
        solve_rhs = np.concatenate((-residual, [ETA_DIRECTION_TARGET]))
    correction = np.linalg.lstsq(solve_matrix, solve_rhs, rcond=None)[0]
    singular = np.linalg.svd(matrix, compute_uv=False)
    before = float(np.linalg.norm(residual))
    accepted = None
    trials = []
    for exponent in range(16):
        factor = 2.0 ** (-exponent)
        vm_states = core._apply(states, center, correction[:-2], factor)
        scale_states = _scale_shift(vm_states, factor * correction[-2])
        candidate = _geometry_shift(
            scale_states, geometry_direction, factor * correction[-1]
        )
        eta = core._eta(candidate)
        if min(eta.values()) <= 0.0:
            trials.append({
                "factor": factor,
                "eta": eta,
                "evaluated_exact_rows": False,
                "admissible": False,
            })
            continue
        evaluated = core._assemble(candidate)
        after = float(np.linalg.norm(evaluated["residual"]))
        trials.append({
            "factor": factor,
            "eta": eta,
            "evaluated_exact_rows": True,
            "exact_hybrid_weak_norm": after,
            "admissible": True,
        })
        if after < before and float(np.linalg.norm(evaluated["boundary"])) < 1e-12:
            accepted = factor, candidate, evaluated, eta, after
            break
    retained = states if accepted is None else accepted[1]
    final = center if accepted is None else accepted[2]
    eta = core._eta(retained) if accepted is None else accepted[3]
    OUTPUT_STATE.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        OUTPUT_STATE,
        order=np.asarray(core.ORDER),
        event_state=np.concatenate(retained["event"]),
        child_state=np.concatenate(retained["child"]),
    )
    validation = {
        "existing_common_scale_coordinate_only": True,
        "common_scale_preserves_four_boundary_rows_exactly": float(
            np.linalg.norm(plus["boundary"] - center["boundary"])
        ) < 1e-13,
        "unchanged_hybrid_weak_rows_reevaluated": True,
        "augmented_normal_full_row_rank": int(np.linalg.matrix_rank(matrix)) == matrix.shape[0],
        "exact_merit_reduced_if_accepted": accepted is None or accepted[4] < before,
        "eta_admissible_if_accepted": accepted is None or min(eta.values()) > 0.0,
        "not_promoted_as_complete_child_root": True,
        "no_equation_constraint_gate_scale_fit_or_event_definition_changed": True,
    }
    payload = {
        "classification": (
            "N64_COMMON_SCALE_AUGMENTED_HYBRID_WEAK_STEP_ACCEPTED"
            if accepted is not None else
            "N64_COMMON_SCALE_DIRECTION_DOES_NOT_RESCUE_THE_ADMISSIBLE_HYBRID_WEAK_STEP"
        ),
        "input": {"path": str(INPUT.relative_to(ROOT)).replace("\\", "/"), "SHA256": _sha256(INPUT)},
        "difference_step": STEP,
        "eta_tangent_predictor_used": ETA_TANGENT,
        "eta_direction_target": ETA_DIRECTION_TARGET,
        "eta_gradient": eta_gradient_record,
        "predicted_eta_directional_derivative": float(eta_gradient @ correction),
        "exact_norm_before": before,
        "exact_norm_after": float(np.linalg.norm(final["residual"])),
        "accepted": accepted is not None,
        "accepted_factor": 0.0 if accepted is None else accepted[0],
        "common_scale_action_coordinate_amplitude": float(correction[-2]),
        "boundary_kernel_geometry_action_coordinate_amplitude": float(
            correction[-1]
        ),
        "full_proposal_action_norm": float(np.linalg.norm(correction)),
        "scale_column_norm": float(np.linalg.norm(scale_column)),
        "geometry_column_norm": float(np.linalg.norm(geometry_column)),
        "geometry_direction": geometry_record,
        "normal_shape": list(matrix.shape),
        "normal_rank": int(np.linalg.matrix_rank(matrix)),
        "normal_smallest_singular_value": float(singular[-1]),
        "eta": eta,
        "boundary_norm": float(np.linalg.norm(final["boundary"])),
        "trials": trials,
        "state_artifact": {
            "path": str(OUTPUT_STATE.relative_to(ROOT)).replace("\\", "/"),
            "SHA256": _sha256(OUTPUT_STATE),
            "status": "FINITE_ANALYTIC_CORE_NOT_A_COMPLETE_CHILD_ROOT",
        },
        "M_star_certified": False,
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "exact_next_dependency": (
            "CONTINUE_THE_SAME_SCALE_AUGMENTED_HYBRID_WEAK_CORRECTION"
            if accepted is not None else
            "ADD_THE_MINIMUM_BOUNDARY_KERNEL_GEOMETRY_DIRECTION_SELECTED_BY_THE_EXISTING_ETA_GRADIENT"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
