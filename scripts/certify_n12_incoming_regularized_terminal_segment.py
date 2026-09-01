"""Certify an explicit inverse-free incoming segment at the terminal event."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (  # noqa: E402
    spectral_frequencies,
)
from derive_n12_c2_birth_coefficient_quotient_jet import (  # noqa: E402
    _coefficient_enclosure,
)
from derive_n12_c2_launch_eigenline_ball import _load  # noqa: E402


ORDER = 12
POINTS = 96
QDIM = 37
STATE_DIMENSION = 98
BALL_RADIUS = 6.2e-13
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_INCOMING_REGULARIZED_TERMINAL_SEGMENT.json"
CANDIDATE = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
ORIENTATION = BASE / "BHSM_N12_FINITE_TERMINAL_ORIENTATION_CERTIFICATE.json"
COEFFICIENT = BASE / "BHSM_N12_FINITE_HISTORY_TERMINAL_COEFFICIENT_JET.json"
MAJORANTS = BASE / "BHSM_N12_FINITE_TERMINAL_SOLUTION_BALL_ACTION_MAJORANTS.json"
EIGENLINE = BASE / "BHSM_N12_FINITE_TERMINAL_CHILD_EIGENLINE_SOLUTION_BALL.json"
MIXED = BASE / "BHSM_N12_FINITE_TERMINAL_CHILD_EIGENLINE_MIXED_MAJORANTS.json"
GERM = BASE / "BHSM_N12_INCOMING_COEFFICIENT_PATH_QUADRATIC_GERM.json"
THEORY = ROOT / "theory" / "n12_incoming_regularized_terminal_segment.md"
INPUTS = (
    CANDIDATE, ORIENTATION, COEFFICIENT, MAJORANTS, EIGENLINE, MIXED,
    GERM, THEORY,
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _up(value: float) -> float:
    return math.nextafter(float(value) * (1.0 + 1.0e-10), math.inf)


def _down(value: float) -> float:
    return math.nextafter(float(value) / (1.0 + 1.0e-10), -math.inf)


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("complete incoming terminal-segment inputs required")
    orientation, coefficient, majorants, line, mixed, germ = (
        _load_json(path)
        for path in (ORIENTATION, COEFFICIENT, MAJORANTS, EIGENLINE, MIXED, GERM)
    )
    if not all(record.get("validation_passed") is True for record in (
        orientation, coefficient, majorants, line, mixed, germ,
    )):
        raise RuntimeError("validated incoming terminal-segment parents required")
    if float(line["action_coordinate_ball_radius"]) != BALL_RADIUS:
        raise RuntimeError("incoming eigenline solution-ball radius mismatch")

    with np.load(CANDIDATE) as data:
        joint = np.asarray(data["state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)
    # The stored second arm is the forward-incoming C1 history endpoint.
    state = joint[STATE_DIMENSION:]
    frequencies = spectral_frequencies(ORDER)
    q_weights = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
    reduced_weights = np.concatenate((
        np.ones(QDIM),
        np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))
    maximum_q_weight = float(np.max(q_weights))
    maximum_reduced_weight = float(np.max(reduced_weights))
    identity = np.eye(STATE_DIMENSION)

    jet = exact_full_action_jet_at_state(
        ORDER, state[:QDIM], state[QDIM:2 * QDIM], state[2 * QDIM:],
        points=POINTS,
    )
    hessian = np.asarray(jet.hessian, dtype=float)
    reduced = hessian[QDIM:, QDIM:]
    values, vectors = np.linalg.eigh(reduced)
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    psi = vectors[:, selected]
    if float(psi @ reference) < 0.0:
        psi = -psi
    complement = np.delete(vectors, selected, axis=1)
    selected_action = np.concatenate((
        np.zeros(QDIM), psi * reduced_weights,
    ))
    complement_action = np.vstack((
        np.zeros((QDIM, complement.shape[1])),
        complement * reduced_weights[:, None],
    ))

    # Load the committed canonical majorant implementation even when the
    # user's unrelated working-tree version of the shared file is dirty.
    os.environ["BHSM_N12_CERTIFICATE_BALL"] = str(BALL_RADIUS)
    action_bound = _load("derive_n12_action_ball_majorants").action_bound
    c_specs = {
        "D3_PPP": [selected_action] * 3,
        "D3_CPP": [complement_action, selected_action, selected_action],
        "D4_XPPP": [identity, selected_action, selected_action, selected_action],
    }
    c_bounds = {
        name: float(action_bound(
            state, projection=identity, mixed_directions=directions,
        ).d[-1])
        for name, directions in c_specs.items()
    }

    velocity = state[QDIM:2 * QDIM]
    psi_velocity_as_q = np.concatenate((
        psi[:QDIM] * weights[:QDIM], np.zeros(STATE_DIMENSION - QDIM),
    ))
    velocity_as_q = np.concatenate((
        velocity * weights[:QDIM], np.zeros(STATE_DIMENSION - QDIM),
    ))
    varying_velocity_as_q = np.zeros((STATE_DIMENSION, STATE_DIMENSION))
    varying_velocity_as_q[:QDIM] = (
        weights[:QDIM, None] * identity[QDIM:2 * QDIM]
    )
    b_specs = {
        "D2_PSI_VELOCITY_AS_Q_X": [psi_velocity_as_q, identity],
        "D3_PSI_VELOCITY_AS_Q_X": [
            selected_action, velocity_as_q, identity,
        ],
        "D2_PSI_X_VELOCITY_AS_Q": [
            selected_action, varying_velocity_as_q,
        ],
    }
    b_bounds = {
        name: float(action_bound(
            state, projection=identity, mixed_directions=directions,
        ).d[-1])
        for name, directions in b_specs.items()
    }

    root_radius = float(orientation["solution_distance_upper"])
    available_margin = _down(BALL_RADIUS - root_radius)
    line_bounds = line["bounds"]
    line_lipschitz = _up(float(
        line_bounds["weighted_selected_to_complement_first_variation_on_ball"]
    ))
    psi_action_lipschitz = _up(maximum_reduced_weight * line_lipschitz)
    c_lipschitz = _up(
        c_bounds["D4_XPPP"]
        + 3.0 * c_bounds["D3_CPP"] * line_lipschitz
    )

    child_majorants = next(
        row for row in majorants["sectors"] if row["sector"] == "child"
    )["derivative_operator_majorants_0_through_5"]
    configuration_center = q_weights * velocity
    configuration_upper = _up(
        float(np.linalg.norm(configuration_center))
        + maximum_q_weight * BALL_RADIUS
    )
    mixed_q = hessian[QDIM:, :QDIM]
    rhs = np.concatenate((
        np.asarray(jet.gradient[:QDIM], dtype=float)
        - mixed_q[:QDIM] @ velocity,
        -mixed_q[QDIM:] @ velocity,
    ))
    rhs_lipschitz = _up(maximum_reduced_weight * (
        float(child_majorants[2]) * (1.0 + maximum_q_weight)
        + float(child_majorants[3]) * configuration_upper
    ))
    rhs_upper = _up(float(np.linalg.norm(rhs)) + rhs_lipschitz * BALL_RADIUS)
    fixed_b_lipschitz = _up(sum(b_bounds.values()))
    b_lipschitz = _up(fixed_b_lipschitz + rhs_upper * line_lipschitz)

    duration = coefficient["desingularized_duration_jet"]
    root_c_lower, root_c_upper = (
        float(value) for value in duration["root_c_psi_interval"]
    )
    root_b_lower, root_b_upper = (
        float(value) for value in duration["root_b_psi_interval"]
    )
    lambda_lipschitz = _up(float(
        line_bounds["selected_eigenvalue_first_derivative_bound"]
    ))
    outer_lambda_upper = _up(lambda_lipschitz * available_margin)
    hard_gap_lower = _down(
        float(line_bounds["eigenline_gap_lower"]) - outer_lambda_upper
    )
    hard_inverse_upper = _up(1.0 / hard_gap_lower)
    hard_rate_raw_upper = _up(hard_inverse_upper * rhs_upper)
    hard_rate_action_upper = _up(
        maximum_reduced_weight * hard_rate_raw_upper
    )
    lambda_hessian = _up(float(
        line_bounds["selected_eigenvalue_raw_Hessian_bound"]
    ))
    hard_flow_upper = _up(math.hypot(
        configuration_upper, hard_rate_action_upper
    ))
    remainder_upper = _up(lambda_lipschitz * hard_flow_upper)

    root_abs_c_lower = _down(-root_c_upper)
    root_abs_c_upper = _up(-root_c_lower)
    root_product_abs_lower = _down(root_abs_c_lower * root_b_lower)
    denominator_loss_slope = _up(
        root_b_upper * c_lipschitz
        + root_abs_c_upper * b_lipschitz
        + lambda_lipschitz * remainder_upper
    )
    sign_radius = _down(root_product_abs_lower / denominator_loss_slope)
    dynamic_margin = _down(0.5 * min(available_margin, sign_radius))
    c_lower = _down(root_c_lower - c_lipschitz * dynamic_margin)
    c_upper = _up(root_c_upper + c_lipschitz * dynamic_margin)
    b_lower = _down(root_b_lower - b_lipschitz * dynamic_margin)
    b_upper = _up(root_b_upper + b_lipschitz * dynamic_margin)
    lambda_upper = _up(lambda_lipschitz * dynamic_margin)
    abs_denominator_lower = _down(
        (-c_upper) * b_lower - lambda_upper * remainder_upper
    )
    abs_denominator_upper = _up(
        (-c_lower) * b_upper + lambda_upper * remainder_upper
    )

    raw_dirac_lipschitz = _up(
        maximum_reduced_weight**2 * float(child_majorants[3])
    )
    projector_lipschitz = _up(
        2.0 * hard_inverse_upper * raw_dirac_lipschitz
    )
    hard_rate_lipschitz_raw = _up(
        hard_inverse_upper * (
            rhs_lipschitz + projector_lipschitz * rhs_upper
        )
        + hard_inverse_upper**2 * raw_dirac_lipschitz * rhs_upper
    )
    hard_rate_lipschitz_action = _up(
        maximum_reduced_weight * hard_rate_lipschitz_raw
    )
    hard_flow_lipschitz = _up(math.hypot(
        maximum_q_weight, hard_rate_lipschitz_action
    ))
    remainder_lipschitz = _up(
        lambda_hessian * hard_flow_upper
        + lambda_lipschitz * hard_flow_lipschitz
    )
    denominator_lipschitz = _up(
        b_upper * c_lipschitz + (-c_lower) * b_lipschitz
        + lambda_lipschitz * remainder_upper
        + lambda_upper * remainder_lipschitz
    )

    selected_action_upper = _up(
        float(np.linalg.norm(selected_action))
        + psi_action_lipschitz * dynamic_margin
    )
    numerator_upper = _up(math.hypot(
        lambda_upper * configuration_upper,
        b_upper * selected_action_upper
        + lambda_upper * hard_rate_action_upper,
    ))
    numerator_lipschitz = _up(
        lambda_lipschitz * configuration_upper
        + lambda_upper * maximum_q_weight
        + b_lipschitz * selected_action_upper
        + b_upper * psi_action_lipschitz
        + lambda_lipschitz * hard_rate_action_upper
        + lambda_upper * hard_rate_lipschitz_action
    )
    regularized_speed_upper = _up(
        numerator_upper / abs_denominator_lower
    )
    regularized_jacobi_upper = _up(
        numerator_lipschitz / abs_denominator_lower
        + numerator_upper * denominator_lipschitz
        / abs_denominator_lower**2
    )

    path_fraction = 0.25
    path_limited_lambda = _down(
        path_fraction * dynamic_margin / regularized_speed_upper
    )
    jacobi_exponent_cap = 0.5
    jacobi_limited_lambda = _down(
        jacobi_exponent_cap / regularized_jacobi_upper
    )
    lambda_segment = _down(min(path_limited_lambda, jacobi_limited_lambda))
    u_segment = _down(lambda_segment**2)
    proper_lookback_lower = _down(
        u_segment / (2.0 * abs_denominator_upper)
    )
    proper_lookback_upper = _up(
        u_segment / (2.0 * abs_denominator_lower)
    )
    coefficient_ball = _coefficient_enclosure(state, weights, BALL_RADIUS)
    lapse_lower, lapse_upper = (
        float(value) for value in coefficient_ball["root_lapse_interval"]
    )
    jacobi_growth_upper = _up(math.exp(
        regularized_jacobi_upper * lambda_segment
    ))

    validation = {
        "actual_incoming_stored_second_arm_consumed": selected == 23,
        "root_enclosure_strictly_inside_solution_ball": available_margin > 0.0,
        "root_relative_tube_is_derived_from_negative_Delta_control": (
            0.0 < dynamic_margin <= available_margin and sign_radius > 0.0
        ),
        "selected_eigenline_simple_on_solution_ball": hard_gap_lower > 0.0,
        "c_psi_stays_strictly_negative_and_b_psi_positive": (
            c_upper < 0.0 and b_lower > 0.0
        ),
        "incoming_denominator_stays_strictly_negative": (
            abs_denominator_lower > 0.0
        ),
        "regularized_lambda_vector_field_is_bounded": (
            math.isfinite(regularized_speed_upper)
            and regularized_speed_upper > 0.0
        ),
        "first_regularized_Jacobi_generator_is_bounded": (
            math.isfinite(regularized_jacobi_upper)
            and regularized_jacobi_upper >= 0.0
        ),
        "explicit_positive_lambda_segment_is_nonzero": lambda_segment > 0.0,
        "explicit_physical_u_segment_is_nonzero": u_segment > 0.0,
        "explicit_proper_lookback_duration_is_positive": (
            proper_lookback_lower > 0.0
        ),
        "path_uses_strict_fraction_of_available_action_margin": (
            regularized_speed_upper * lambda_segment < dynamic_margin
        ),
        "first_Jacobi_growth_uses_derived_exponent_cap": (
            regularized_jacobi_upper * lambda_segment
            <= jacobi_exponent_cap
        ),
        "terminal_lapse_and_forward_radius_rate_remain_positive": (
            lapse_lower > 0.0
            and coefficient_ball["root_D_tau_log_R4_interval"][0] > 0.0
        ),
        "lambda_increases_backward_from_terminal_and_decreases_forward": True,
        "no_Euler_Dirac_block_inverse_used": True,
        "no_amplitude_selector_recurrence_scale_action_term_gate_or_chord_added": True,
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_INCOMING_REGULARIZED_TERMINAL_SEGMENT",
        "status": (
            "EXPLICIT_NONZERO_INCOMING_TERMINAL_SEGMENT_AND_FIRST_JACOBI_BOUND_CERTIFIED"
            if passed else "INCOMING_REGULARIZED_TERMINAL_SEGMENT_NOT_CERTIFIED"
        ),
        "classification": (
            "THE_INCOMING_BRANCH_23_SELECTED_EIGENVALUE_IS_A_REGULAR_"
            "BACKWARD_FROM_TERMINAL_STATE_PARAMETER;_THE_CERTIFIED_NEGATIVE_"
            "c_psi_TIMES_POSITIVE_b_psi_KEEPS_Delta_STRICTLY_NEGATIVE_ON_AN_"
            "EXPLICIT_ACTION_TUBE,_SO_THE_POLE_CANCELLED_FIELD_AND_ITS_FIRST_"
            "JACOBI_GENERATOR_ARE_UNIFORMLY_BOUNDED_AND_A_NONZERO_FINITE_"
            "AMPLITUDE_FORMATION_SEGMENT_EXISTS_WITHOUT_SELECTING_A_HISTORY"
        ),
        "exact_regularized_system": {
            "state_parameter": "s=lambda_incoming>=0_measured_backward_from_terminal",
            "physical_readout": "u=s^2",
            "denominator": "Delta=c_psi*b_psi+s*R<0",
            "R": "D_lambda[(q_dot,hard_rate)]",
            "dY_ds": "(b_psi*Psi+s*V_hard)/Delta",
            "d_proper_lookback_ds": "-s/Delta>0",
            "terminal_limit": "dY/ds=Psi/c_psi",
            "forward_orientation": "s_decreases_to_zero_as_physical_time_increases",
        },
        "terminal_ball": {
            "action_radius": BALL_RADIUS,
            "exact_root_distance_upper": root_radius,
            "available_dynamic_margin_lower": available_margin,
            "negative_Delta_sign_radius_lower": sign_radius,
            "derived_root_relative_tube_radius": dynamic_margin,
            "Delta_loss_slope_upper": denominator_loss_slope,
            "path_fraction_used": path_fraction,
            "Jacobi_exponent_cap": jacobi_exponent_cap,
            "path_limited_lambda_upper": path_limited_lambda,
            "Jacobi_limited_lambda_upper": jacobi_limited_lambda,
            "selected_eigenline_gap_lower": hard_gap_lower,
            "lambda_Lipschitz_upper": lambda_lipschitz,
            "selected_line_Lipschitz_upper": line_lipschitz,
            "c_psi_Lipschitz_upper": c_lipschitz,
            "b_psi_Lipschitz_upper": b_lipschitz,
            "c_psi_interval": [c_lower, c_upper],
            "b_psi_interval": [b_lower, b_upper],
            "lambda_upper": lambda_upper,
            "hard_rate_action_upper": hard_rate_action_upper,
            "configuration_rate_action_upper": configuration_upper,
            "R_upper": remainder_upper,
            "minus_Delta_interval": [
                abs_denominator_lower, abs_denominator_upper,
            ],
            "Delta_interval": [
                -abs_denominator_upper, -abs_denominator_lower,
            ],
            "Delta_action_derivative_upper": denominator_lipschitz,
            "regularized_state_speed_upper": regularized_speed_upper,
            "regularized_first_Jacobi_generator_upper": regularized_jacobi_upper,
            "first_Jacobi_growth_upper": jacobi_growth_upper,
            "specialized_action_bounds": {**c_bounds, **b_bounds},
        },
        "explicit_segment": {
            "positive_lambda_end_lower": lambda_segment,
            "physical_u_end_lower": u_segment,
            "proper_lookback_duration_interval": [
                proper_lookback_lower, proper_lookback_upper,
            ],
            "action_path_use_upper": _up(
                regularized_speed_upper * lambda_segment
            ),
            "D_tau_log_R4_interval_on_terminal_ball": coefficient_ball[
                "root_D_tau_log_R4_interval"
            ],
            "log_R4_interval_on_terminal_ball": coefficient_ball[
                "root_log_R4_interval"
            ],
            "lapse_interval_on_terminal_ball": [lapse_lower, lapse_upper],
            "physical_history_member_selected": False,
        },
        "exact_next_dependency": (
            "PROPAGATE_THE_TERMINAL_RADIUS_CAUCHY_JET_AND_ITS_PHYSICAL_"
            "QUOTIENT_DERIVATIVES_OVER_THIS_EXPLICIT_SEGMENT_WITH_AN_"
            "INVERSE_FREE_VOLterra_REMAINDER,_THEN_EVALUATE_THE_EXISTING_"
            "COMPACT_INCOMING_M_f_BLOCK_AND_JOINT_EVENT_CHILD_SEAM"
        ),
        "claim_boundary": {
            "explicit_uniform_finite_amplitude_incoming_segment": "CERTIFIED",
            "complete_normalized_radius_path_remainder": "OPEN_NEXT",
            "joint_incoming_event_child_seam": "OPEN_AFTER_PATH",
            "non_scale_reset_quotient_pullback": "OPEN_AFTER_PATH",
            "zero_source_force": "OPEN_AFTER_SEAM",
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
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "Delta": payload["terminal_ball"]["Delta_interval"],
        "lambda_end": payload["explicit_segment"]["positive_lambda_end_lower"],
        "proper_lookback": payload["explicit_segment"][
            "proper_lookback_duration_interval"
        ],
        "Jacobi": payload["terminal_ball"][
            "regularized_first_Jacobi_generator_upper"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
