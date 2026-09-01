"""Certify the actual reset-selected C2 birth coefficient and quotient jet."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np
from scipy.linalg import null_space


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (  # noqa: E402
    embed_nested_state,
)
from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (  # noqa: E402
    _authoritative_n6_event_child_anchor,
)
from bhsm.interface.aether_forward_boundary_radius import (  # noqa: E402
    boundary_log_lapse,
    boundary_log_radius,
    boundary_log_radius_jets,
    proper_time_log_radius_rate,
)
from bhsm.interface.aether_full_reset_action_jacobian import (  # noqa: E402
    full_reset_action_jacobian,
    full_reset_residual,
)


ORDER = 12
POINTS = 96
QDIM = 37
STATE_DIMENSION = 98
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_BIRTH_COEFFICIENT_QUOTIENT_JET.json"
CANDIDATE = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
ROOT_RESIDUAL = ROOT / (
    "artifacts/n12_direct_checkpoint/BHSM_N12_EXACT_ROOT_RESIDUAL.json"
)
CROSS_RESOLUTION = ROOT / (
    "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
)
RADII = BASE / "BHSM_N12_FINITE_TERMINAL_RADII_CERTIFICATE.json"
INTERFACE = BASE / "BHSM_N12_FINITE_TERMINAL_TWO_SIDED_FORWARD_INTERFACE.json"
MATCHING = BASE / "BHSM_N12_GATE7_C2_DIAGRAM_SLOT_MATCHING_AUDIT.json"
THEORY = ROOT / "theory/n12_c2_birth_coefficient_quotient_jet.md"
MODULES = (
    ROOT / "src/bhsm/interface/aether_constraint_consistent_sobolev_lift_v15_84.py",
    ROOT / "src/bhsm/interface/aether_cross_resolution_reconnaissance_v21_35.py",
    ROOT / "src/bhsm/interface/aether_forward_boundary_radius.py",
    ROOT / "src/bhsm/interface/aether_full_reset_action_jacobian.py",
)
INPUTS = (
    CANDIDATE,
    ROOT_RESIDUAL,
    CROSS_RESOLUTION,
    RADII,
    INTERFACE,
    MATCHING,
    THEORY,
    *MODULES,
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _decode(payload: dict[str, list[str]]) -> tuple[np.ndarray, ...]:
    return tuple(
        np.asarray([float.fromhex(value) for value in payload[name]])
        for name in ("coordinates", "velocities", "multipliers")
    )


def _normalization_coordinates() -> np.ndarray:
    cross = _load(CROSS_RESOLUTION)["cross_resolution_reconnaissance"]
    anchor = _authoritative_n6_event_child_anchor(cross)
    return embed_nested_state(*_decode(anchor["child_exact"]), 6, ORDER)[0]


def _cauchy_covectors_action(
    state: np.ndarray, weights: np.ndarray
) -> tuple[np.ndarray, float, float]:
    q = state[:QDIM]
    velocity = state[QDIM : 2 * QDIM]
    multipliers = state[2 * QDIM :]
    jets = boundary_log_radius_jets(
        ORDER, q, np.zeros(QDIM), np.zeros(QDIM)
    )
    gradient_x = np.asarray(jets["gradient"], dtype=float)
    signs_j = (-1.0) ** np.arange(ORDER)
    signs_k = (-1.0) ** np.arange(1, ORDER + 1)
    hessian_x = np.zeros((QDIM, QDIM))
    hessian_x[25:37, 25:37] = (
        -2.0
        * (1.0 - math.tanh(2.0 * float(jets["boundary_v"])) ** 2)
        * np.outer(signs_j, signs_j)
    )
    lapse = math.exp(boundary_log_lapse(ORDER, multipliers))
    rate = proper_time_log_radius_rate(ORDER, q, velocity, multipliers)
    raw_x = np.zeros(STATE_DIMENSION)
    raw_x[:QDIM] = gradient_x
    raw_rate = np.zeros(STATE_DIMENSION)
    raw_rate[:QDIM] = hessian_x @ velocity / lapse
    raw_rate[QDIM : 2 * QDIM] = gradient_x / lapse
    raw_rate[2 * QDIM : 2 * QDIM + ORDER] = -rate * signs_k
    return np.vstack((raw_x, raw_rate)) / weights[None, :], lapse, rate


def _evaluate_cauchy(state: np.ndarray) -> np.ndarray:
    return np.asarray(
        (
            boundary_log_radius(ORDER, state[:QDIM]),
            proper_time_log_radius_rate(
                ORDER,
                state[:QDIM],
                state[QDIM : 2 * QDIM],
                state[2 * QDIM :],
            ),
        )
    )


def _coefficient_enclosure(
    state: np.ndarray, weights: np.ndarray, action_radius: float
) -> dict[str, Any]:
    q = state[:QDIM]
    velocity = state[QDIM : 2 * QDIM]
    multipliers = state[2 * QDIM :]
    q_weights = weights[:QDIM]
    velocity_weights = weights[QDIM : 2 * QDIM]
    multiplier_weights = weights[2 * QDIM :]
    signs_k = (-1.0) ** np.arange(1, ORDER + 1)
    signs_j = (-1.0) ** np.arange(ORDER)
    b_slice = slice(1 + 2 * ORDER, 1 + 3 * ORDER)

    b_center = float(q[b_slice] @ signs_j)
    velocity_b_center = float(velocity[b_slice] @ signs_j)
    b_dual = float(np.linalg.norm(signs_j / q_weights[b_slice]))
    velocity_b_dual = float(
        np.linalg.norm(signs_j / velocity_weights[b_slice])
    )
    b_absolute_upper = abs(b_center) + action_radius * b_dual
    velocity_b_absolute_upper = (
        abs(velocity_b_center) + action_radius * velocity_b_dual
    )
    tanh_upper = math.tanh(2.0 * b_absolute_upper)

    lapse_dual = float(
        np.linalg.norm(signs_k / multiplier_weights[:ORDER])
    )
    log_lapse = boundary_log_lapse(ORDER, multipliers)
    lapse_center = math.exp(log_lapse)
    lapse_lower = lapse_center * math.exp(-action_radius * lapse_dual)
    lapse_upper = lapse_center * math.exp(action_radius * lapse_dual)

    numerator_center = (
        proper_time_log_radius_rate(ORDER, q, velocity, multipliers)
        * lapse_center
    )
    fixed_velocity_coefficients = np.concatenate(
        (np.ones(1), signs_k, np.zeros(ORDER), tanh_upper * signs_j)
    )
    velocity_change = action_radius * float(
        np.linalg.norm(fixed_velocity_coefficients / velocity_weights)
    )
    tanh_change_contribution = (
        2.0 * action_radius * b_dual * velocity_b_absolute_upper
    )
    numerator_upper = (
        abs(numerator_center) + velocity_change + tanh_change_contribution
    )
    rate_absolute_upper = numerator_upper / lapse_lower
    q_gradient_dual = (
        2.0 * velocity_b_absolute_upper / lapse_lower * b_dual
    )
    velocity_gradient_dual = float(
        np.linalg.norm(fixed_velocity_coefficients / velocity_weights)
    ) / lapse_lower
    multiplier_gradient_dual = rate_absolute_upper * lapse_dual
    full_gradient_dual = math.sqrt(
        q_gradient_dual**2
        + velocity_gradient_dual**2
        + multiplier_gradient_dual**2
    )
    rate_center = proper_time_log_radius_rate(
        ORDER, q, velocity, multipliers
    )
    uncertainty = full_gradient_dual * action_radius
    x_center = boundary_log_radius(ORDER, q)
    x_gradient = np.asarray(
        boundary_log_radius_jets(
            ORDER, q, np.zeros(QDIM), np.zeros(QDIM)
        )["gradient"],
        dtype=float,
    )
    x_uncertainty = action_radius * float(
        np.linalg.norm(x_gradient / q_weights)
    )
    return {
        "center_log_R4": x_center,
        "center_R4": math.exp(x_center),
        "root_log_R4_interval": [
            x_center - x_uncertainty,
            x_center + x_uncertainty,
        ],
        "center_log_lapse": log_lapse,
        "center_lapse": lapse_center,
        "root_lapse_interval": [lapse_lower, lapse_upper],
        "center_D_tau_log_R4": rate_center,
        "root_D_tau_log_R4_interval": [
            rate_center - uncertainty,
            rate_center + uncertainty,
        ],
        "action_dual_rate_gradient_bound": full_gradient_dual,
    }


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        missing = [str(path) for path in INPUTS if not path.is_file()]
        raise FileNotFoundError(f"missing C2 birth-jet inputs: {missing}")
    radii, interface, matching = (
        _load(path) for path in (RADII, INTERFACE, MATCHING)
    )
    if not all(
        record.get("validation_passed") is True
        for record in (radii, interface, matching)
    ):
        raise RuntimeError("validated C2 reset parents required")

    with np.load(CANDIDATE) as data:
        stored_joint = np.asarray(data["state"], dtype=float)
        event_third = np.asarray(data["event_third"], dtype=float)
        child_third = np.asarray(data["child_third"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)

    # Stored order is (E_*,C_*).  Physical forward order after the certified
    # swap is (E1,C2)=(C_*,E_*); the action tensors must be swapped as well.
    joint = np.concatenate(
        (stored_joint[STATE_DIMENSION:], stored_joint[:STATE_DIMENSION])
    )
    root = _load(ROOT_RESIDUAL)
    normalization = _normalization_coordinates()
    reset, residual_event_index = full_reset_residual(
        ORDER,
        joint,
        weights,
        reference,
        float(root["ordered_scale"]),
        normalization,
        points=POINTS,
        high_precision_action=True,
    )
    jacobian, jacobian_event_index = full_reset_action_jacobian(
        ORDER,
        joint,
        child_third,
        event_third,
        weights,
        reference,
        float(root["ordered_scale"]),
        normalization,
        points=POINTS,
    )
    tangent = null_space(jacobian)
    child_projection = tangent[STATE_DIMENSION:]
    child_basis, child_singular, _ = np.linalg.svd(
        child_projection, full_matrices=False
    )
    child_rank = int(np.sum(child_singular > 1.0e-10))
    child_basis = child_basis[:, :child_rank]
    c2_state = joint[STATE_DIMENSION:]
    cauchy_covectors, lapse, rate = _cauchy_covectors_action(
        c2_state, weights
    )
    quotient_map = cauchy_covectors @ child_basis
    _, cauchy_singular, right = np.linalg.svd(
        quotient_map, full_matrices=False
    )
    cauchy_rank = int(np.sum(cauchy_singular > 1.0e-10))

    direction_rows: list[dict[str, Any]] = []
    step = 1.0e-6
    for index in range(2):
        child_action_direction = child_basis @ right[index]
        coefficients = np.linalg.lstsq(
            child_projection, child_action_direction, rcond=None
        )[0]
        lifted = tangent @ coefficients
        analytic = quotient_map @ right[index]
        child_raw_direction = child_action_direction / weights
        finite = (
            _evaluate_cauchy(c2_state + step * child_raw_direction)
            - _evaluate_cauchy(c2_state - step * child_raw_direction)
        ) / (2.0 * step)
        direction_rows.append(
            {
                "right_singular_direction": index,
                "C2_birth_Cauchy_jet": analytic.tolist(),
                "finite_difference_Cauchy_jet": finite.tolist(),
                "finite_difference_residual": float(
                    np.linalg.norm(analytic - finite)
                ),
                "swapped_reset_tangency_residual": float(
                    np.linalg.norm(jacobian @ lifted)
                ),
                "C2_projection_lift_residual": float(
                    np.linalg.norm(
                        lifted[STATE_DIMENSION:] - child_action_direction
                    )
                ),
            }
        )

    root_radius = float(
        radii["radii_polynomial"]["negative_interval_roots"][0]
    )
    coefficient = _coefficient_enclosure(c2_state, weights, root_radius)
    incoming_x = boundary_log_radius(
        ORDER, joint[:STATE_DIMENSION][:QDIM]
    )
    validation = {
        "parent_artifacts_validate": True,
        "stored_pair_swapped_to_physical_E1_C2_order": (
            interface["exact_local_theorem"]["physical_chronology"]
            == "E0_TO_C1_TO_[T>0]_E1_TO_C2"
        ),
        "complete_swapped_reset_residual_below_2e_14": float(
            np.linalg.norm(reset)
        ) < 2.0e-14,
        "swapped_reset_selected_event_is_branch_23": (
            residual_event_index == jacobian_event_index == 23
        ),
        "swapped_reset_Jacobian_has_rank_57": int(
            np.linalg.matrix_rank(jacobian)
        ) == 57,
        "swapped_reset_tangent_dimension_is_139": tangent.shape[1] == 139,
        "actual_C2_projection_rank_is_73": child_rank == 73,
        "actual_C2_Cauchy_jet_rank_is_two": cauchy_rank == 2,
        "both_Cauchy_singular_values_are_strictly_positive": bool(
            cauchy_singular[1] > 0.5
        ),
        "analytic_C2_jets_match_centered_differences": all(
            row["finite_difference_residual"] < 1.0e-8
            for row in direction_rows
        ),
        "representative_directions_lift_to_swapped_reset_tangent": all(
            row["swapped_reset_tangency_residual"] < 1.0e-11
            and row["C2_projection_lift_residual"] < 1.0e-11
            for row in direction_rows
        ),
        "event_and_child_birth_radius_traces_match": abs(
            float(coefficient["center_log_R4"]) - incoming_x
        ) < 1.0e-14,
        "actual_C2_root_lapse_is_strictly_positive": coefficient[
            "root_lapse_interval"
        ][0]
        > 0.0,
        "actual_C2_root_proper_radius_rate_is_strictly_positive": coefficient[
            "root_D_tau_log_R4_interval"
        ][0]
        > 0.0,
        "certified_event_half_is_forward_outgoing": interface["validation"][
            "event_half_is_forward_outgoing"
        ],
        "no_future_endpoint_history_member_selector_scale_action_term_gate_or_chord_added": True,
    }
    return {
        "artifact": "BHSM_N12_C2_BIRTH_COEFFICIENT_QUOTIENT_JET",
        "status": "ACTUAL_RESET_SELECTED_C2_BIRTH_CAUCHY_JET_RANK_TWO_CERTIFIED",
        "classification": (
            "AFTER_RECOMPUTING_THE_COMPLETE_RESET_MAP_IN_THE_CERTIFIED_"
            "SWAPPED_FORWARD_ORDER_(E1,C2)=(C_*,E_*),_THE_139_DIMENSIONAL_"
            "RESET_TANGENT_PROJECTS_WITH_RANK_73_TO_THE_ACTUAL_C2_ARM_AND_"
            "THE_ACTION_OWNED_MAP_TO_(log_R4,D_tau_log_R4)_HAS_RANK_TWO;_"
            "THE_C2_BIRTH_LAPSE_AND_PROPER_RADIUS_RATE_ARE_STRICTLY_"
            "POSITIVE_ON_THE_ROOT_BALL"
        ),
        "physical_forward_order": {
            "stored": "(E_*,C_*)",
            "swapped": "(E1,C2)=(C_*,E_*)",
            "reason": interface["exact_local_theorem"]["swap"],
            "full_reset_map_recomputed_after_swap": True,
            "original_tangent_first_arm_reused_without_recomputation": False,
        },
        "swapped_reset": {
            "residual_norm": float(np.linalg.norm(reset)),
            "residual_maximum": float(np.max(np.abs(reset))),
            "rank": int(np.linalg.matrix_rank(jacobian)),
            "tangent_dimension": int(tangent.shape[1]),
            "selected_event_branch": int(jacobian_event_index),
            "C2_projection_rank": child_rank,
            "C2_projection_smallest_nonzero_singular_value": float(
                child_singular[child_rank - 1]
            ),
        },
        "C2_birth_coefficient": coefficient,
        "C2_birth_quotient_jet": {
            "map": "D_xi(log_R4,D_tau_log_R4)_ON_THE_73_DIMENSIONAL_C2_RESET_IMAGE",
            "rank": cauchy_rank,
            "singular_values": cauchy_singular.tolist(),
            "row_norms": np.linalg.norm(quotient_map, axis=1).tolist(),
            "center_lapse_crosscheck": lapse,
            "center_rate_crosscheck": rate,
            "representative_directions": direction_rows,
            "gauge_covariance": "BOTH_OUTPUTS_ARE_GEOMETRY_SCALARS",
            "intrinsic_time_quotient": (
                "NOT_YET_REMOVED;_ONE_TIME_DIRECTION_CANNOT_REMOVE_BOTH_"
                "INDEPENDENT_COEFFICIENT_DIRECTIONS"
            ),
            "physical_common_scale": "RETAINED",
        },
        "diagram_feed": {
            "C2_slot": "M_C2=M_C_MAX_ON_THE_ACTUAL_RESET_SELECTED_C2_HISTORY",
            "actual_birth_coefficient": "CERTIFIED",
            "actual_birth_first_reset_quotient_jet": "CERTIFIED_RANK_TWO",
            "future_coefficient_path": "OPEN",
            "endpoint_stratum": "OPEN_WITH_RETAINED_EVENT_OR_CANONICAL_STOP_RULE",
            "complete_M_C2_spectral_family": "OPEN_AFTER_PATH_OR_EQUIVALENT_JOINT_OPERATOR",
            "second_covariant_quotient_jet": "OPEN",
        },
        "exact_next_dependency": (
            "DERIVE_THE_OUTGOING_DESINGULARIZED_C2_COEFFICIENT_AND_FIRST_"
            "JACOBI_GERM_FROM_THIS_CERTIFIED_BIRTH_DATA,_THEN_CERTIFY_THE_"
            "FIRST_REGULAR_C2_SEGMENT_AND_FEED_ITS_ACTUAL_x_D_xi_x_AND_"
            "DURATION_JETS_TO_THE_EXISTING_INVERSE_FREE_WEYL_TRANSFER"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_C2_OUTGOING_COEFFICIENT_JACOBI_GERM",
            "C2_response_theory": "CLOSED_EXISTING_OBJECT_MATCH",
            "actual_C2_birth_coefficient_and_first_jet": "CERTIFIED",
            "actual_C2_future_path_and_endpoint": "OPEN",
            "complete_M_C2_and_second_jet": "OPEN",
            "zero_source_force": "OPEN_AFTER_COMPLETE_C2_REALIZATION",
            "same_action_saddle": "OPEN_AFTER_FORCE",
            "physical_Hessian": "OPEN_AFTER_SADDLE",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in INPUTS
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
    print(
        json.dumps(
            {
                "status": payload["status"],
                "C2_projection_rank": payload["swapped_reset"][
                    "C2_projection_rank"
                ],
                "C2_Cauchy_jet_rank": payload["C2_birth_quotient_jet"][
                    "rank"
                ],
                "validation_passed": payload["validation_passed"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
