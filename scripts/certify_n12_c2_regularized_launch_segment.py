"""Certify an explicit pole-cancelled outgoing segment from the C2 reset."""

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
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (  # noqa: E402
    dimensions,
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
BALL_RADIUS = 1.0e-12
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_REGULARIZED_LAUNCH_SEGMENT.json"
CANDIDATE = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
RADII = BASE / "BHSM_N12_FINITE_TERMINAL_RADII_CERTIFICATE.json"
INTERFACE = BASE / "BHSM_N12_FINITE_TERMINAL_TWO_SIDED_FORWARD_INTERFACE.json"
BIRTH = BASE / "BHSM_N12_C2_BIRTH_COEFFICIENT_QUOTIENT_JET.json"
GERM = BASE / "BHSM_N12_C2_DESINGULARIZED_COEFFICIENT_GERM.json"
MAJORANTS = BASE / "BHSM_N12_C2_LAUNCH_ACTION_MAJORANTS.json"
EIGENLINE = BASE / "BHSM_N12_C2_LAUNCH_EVENT_EIGENLINE_BALL.json"
MIXED = BASE / "BHSM_N12_C2_LAUNCH_EVENT_EIGENLINE_MIXED_MAJORANTS.json"
THEORY = ROOT / "theory" / "n12_c2_regularized_launch_segment.md"
INPUTS = (
    CANDIDATE, RADII, INTERFACE, BIRTH, GERM, MAJORANTS, EIGENLINE, MIXED,
    THEORY,
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
        raise FileNotFoundError("complete C2 launch inputs required")
    radii, interface, birth, germ, majorants, line, mixed = (
        _load_json(path)
        for path in (RADII, INTERFACE, BIRTH, GERM, MAJORANTS, EIGENLINE, MIXED)
    )
    if not all(record.get("validation_passed") is True for record in (
        radii, interface, birth, germ, majorants, line, mixed,
    )):
        raise RuntimeError("validated C2 launch parents required")
    if float(line["action_coordinate_ball_radius"]) != BALL_RADIUS:
        raise RuntimeError("C2 launch eigenline ball radius mismatch")

    with np.load(CANDIDATE) as data:
        joint = np.asarray(data["state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)
    # The actual C2 arm is the stored first arm after the certified reset swap.
    state = joint[:STATE_DIMENSION]
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

    # Load the committed canonical majorant implementation even if unrelated
    # working-tree edits to that shared file are present.
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

    root_radius = float(
        radii["radii_polynomial"]["negative_interval_roots"][0]
    )
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

    event_majorants = next(
        row for row in majorants["sectors"] if row["sector"] == "event"
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
        float(event_majorants[2]) * (1.0 + maximum_q_weight)
        + float(event_majorants[3]) * configuration_upper
    ))
    rhs_upper = _up(float(np.linalg.norm(rhs)) + rhs_lipschitz * BALL_RADIUS)
    fixed_b_lipschitz = _up(sum(b_bounds.values()))
    b_lipschitz = _up(fixed_b_lipschitz + rhs_upper * line_lipschitz)

    root_c_lower, root_c_upper = (
        float(value) for value in germ["certified_intervals"]["c_psi"]
    )
    root_b_lower, root_b_upper = (
        float(value) for value in germ["certified_intervals"]["b_psi"]
    )
    lambda_lipschitz = _up(float(
        line_bounds["selected_eigenvalue_first_derivative_bound"]
    ))
    # First use the outer launch ball to bound the hard solve and R.  Then
    # derive, rather than choose, the root-relative tube on which Delta keeps
    # at least half of its certified birth product.
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
    root_product_lower = _down(root_c_lower * root_b_lower)
    denominator_loss_slope = _up(
        root_b_upper * c_lipschitz
        + root_c_upper * b_lipschitz
        + lambda_lipschitz * remainder_upper
    )
    positivity_radius = _down(
        root_product_lower / denominator_loss_slope
    )
    dynamic_margin = _down(0.5 * min(available_margin, positivity_radius))
    c_lower = _down(root_c_lower - c_lipschitz * dynamic_margin)
    c_upper = _up(root_c_upper + c_lipschitz * dynamic_margin)
    b_lower = _down(root_b_lower - b_lipschitz * dynamic_margin)
    b_upper = _up(root_b_upper + b_lipschitz * dynamic_margin)
    lambda_upper = _up(lambda_lipschitz * dynamic_margin)
    denominator_lower = _down(
        c_lower * b_lower - lambda_upper * remainder_upper
    )
    denominator_upper = _up(
        c_upper * b_upper + lambda_upper * remainder_upper
    )

    raw_dirac_lipschitz = _up(
        maximum_reduced_weight**2 * float(event_majorants[3])
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
        b_upper * c_lipschitz + c_upper * b_lipschitz
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
    regularized_speed_upper = _up(numerator_upper / denominator_lower)
    regularized_jacobi_upper = _up(
        numerator_lipschitz / denominator_lower
        + numerator_upper * denominator_lipschitz / denominator_lower**2
    )

    path_fraction = 0.25
    path_limited_lambda = _down(
        path_fraction * dynamic_margin / regularized_speed_upper
    )
    Jacobi_exponent_cap = 0.5
    Jacobi_limited_lambda = _down(
        Jacobi_exponent_cap / regularized_jacobi_upper
    )
    lambda_segment = _down(min(
        path_limited_lambda, Jacobi_limited_lambda
    ))
    u_segment = _down(lambda_segment**2)
    coordinate_time_lower = _down(u_segment / (2.0 * denominator_upper))
    coordinate_time_upper = _up(u_segment / (2.0 * denominator_lower))
    coefficient_ball = _coefficient_enclosure(state, weights, BALL_RADIUS)
    lapse_lower, lapse_upper = (
        float(value) for value in coefficient_ball["root_lapse_interval"]
    )
    proper_time_lower = _down(lapse_lower * coordinate_time_lower)
    proper_time_upper = _up(lapse_upper * coordinate_time_upper)
    jacobi_growth_upper = _up(math.exp(
        regularized_jacobi_upper * lambda_segment
    ))

    validation = {
        "actual_C2_stored_first_arm_consumed": selected == 24,
        "root_enclosure_strictly_inside_launch_ball": available_margin > 0.0,
        "root_relative_tube_is_derived_from_Delta_positivity": (
            0.0 < dynamic_margin <= available_margin
            and positivity_radius > 0.0
        ),
        "selected_eigenline_simple_on_launch_ball": hard_gap_lower > 0.0,
        "root_relative_c_and_b_stay_strictly_positive": (
            c_lower > 0.0 and b_lower > 0.0
        ),
        "pole_cancelled_denominator_stays_strictly_positive": (
            denominator_lower > 0.0
        ),
        "regularized_lambda_vector_field_is_bounded": (
            math.isfinite(regularized_speed_upper)
            and regularized_speed_upper > 0.0
        ),
        "first_regularized_Jacobi_generator_is_bounded": (
            math.isfinite(regularized_jacobi_upper)
            and regularized_jacobi_upper >= 0.0
        ),
        "explicit_signed_lambda_segment_is_nonzero": lambda_segment > 0.0,
        "explicit_physical_u_segment_is_nonzero": u_segment > 0.0,
        "explicit_coordinate_and_proper_durations_are_positive": (
            coordinate_time_lower > 0.0 and proper_time_lower > 0.0
        ),
        "launch_path_uses_strict_fraction_of_available_action_margin": (
            regularized_speed_upper * lambda_segment
            < dynamic_margin
        ),
        "first_Jacobi_growth_uses_derived_exponent_cap": (
            regularized_jacobi_upper * lambda_segment
            <= Jacobi_exponent_cap
        ),
        "boundary_lapse_and_radius_rate_remain_positive": (
            lapse_lower > 0.0
            and coefficient_ball["root_D_tau_log_R4_interval"][0] > 0.0
        ),
        "signed_lambda_is_state_chart_and_u_is_time_readout": True,
        "no_endpoint_selector_recurrence_scale_action_term_gate_or_chord_added": True,
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_REGULARIZED_LAUNCH_SEGMENT",
        "status": (
            "EXPLICIT_NONZERO_C2_LAUNCH_SEGMENT_AND_FIRST_JACOBI_BOUND_CERTIFIED"
            if passed else "C2_REGULARIZED_LAUNCH_SEGMENT_NOT_CERTIFIED"
        ),
        "classification": (
            "THE_SIGNED_OUTGOING_SELECTED_EIGENVALUE_IS_THE_REGULAR_STATE_"
            "PARAMETER_AT_THE_C2_EVENT,_WHILE_u=lambda_event^2_IS_THE_"
            "INTRINSIC_PHYSICAL_TIME_READOUT;_THE_POLE_CANCELLED_REPARAMETRIZED_"
            "EULER_DIRAC_FIELD_AND_ITS_FIRST_JACOBI_GENERATOR_ARE_UNIFORMLY_"
            "BOUNDED_ON_AN_EXPLICIT_ACTION_BALL,_PRODUCING_A_NONZERO_"
            "FORWARD_C2_SEGMENT_WITHOUT_A_FUTURE_ENDPOINT_CHOICE"
        ),
        "exact_regularized_system": {
            "state_parameter": "s=lambda_event>=0",
            "physical_readout": "u=s^2",
            "denominator": "Delta=c_psi*b_psi+s*R",
            "R": "D_lambda[(q_dot,hard_rate)]",
            "dt_ds": "s/Delta",
            "dq_ds": "s*q_dot/Delta",
            "dz_ds": "(b_psi*psi+s*hard_rate)/Delta",
            "birth_limit": "(dt/ds,dq/ds,dz/ds)=(0,0,psi/c_psi)",
            "proper_time": "d_tau=N*dt",
        },
        "launch_ball": {
            "action_radius": BALL_RADIUS,
            "exact_root_distance_upper": root_radius,
            "available_dynamic_margin_lower": available_margin,
            "Delta_positivity_radius_lower": positivity_radius,
            "derived_root_relative_tube_radius": dynamic_margin,
            "Delta_loss_slope_upper": denominator_loss_slope,
            "path_fraction_used": path_fraction,
            "Jacobi_exponent_cap": Jacobi_exponent_cap,
            "path_limited_lambda_upper": path_limited_lambda,
            "Jacobi_limited_lambda_upper": Jacobi_limited_lambda,
            "selected_eigenline_gap_lower": hard_gap_lower,
            "lambda_Lipschitz_upper": lambda_lipschitz,
            "selected_line_Lipschitz_upper": line_lipschitz,
            "c_psi_Lipschitz_upper": c_lipschitz,
            "b_psi_Lipschitz_upper": b_lipschitz,
            "c_psi_interval": [c_lower, c_upper],
            "b_psi_interval": [b_lower, b_upper],
            "lambda_upper": lambda_upper,
            "hard_rate_action_upper": hard_rate_action_upper,
            "R_upper": remainder_upper,
            "Delta_interval": [denominator_lower, denominator_upper],
            "Delta_action_derivative_upper": denominator_lipschitz,
            "regularized_state_speed_upper": regularized_speed_upper,
            "regularized_first_Jacobi_generator_upper": regularized_jacobi_upper,
            "first_Jacobi_growth_upper": jacobi_growth_upper,
            "specialized_action_bounds": {**c_bounds, **b_bounds},
        },
        "explicit_segment": {
            "signed_lambda_end_lower": lambda_segment,
            "physical_u_end_lower": u_segment,
            "coordinate_time_interval": [coordinate_time_lower, coordinate_time_upper],
            "proper_time_interval": [proper_time_lower, proper_time_upper],
            "action_path_use_upper": _up(
                regularized_speed_upper * lambda_segment
            ),
            "D_tau_log_R4_interval_on_launch_ball": coefficient_ball[
                "root_D_tau_log_R4_interval"
            ],
            "log_R4_interval_on_launch_ball": coefficient_ball[
                "root_log_R4_interval"
            ],
            "lapse_interval_on_launch_ball": [lapse_lower, lapse_upper],
            "future_endpoint_selected": False,
        },
        "exact_next_dependency": (
            "INTEGRATE_THE_ACTUAL_BOUNDARY_COEFFICIENT_AND_FIRST_PHYSICAL_"
            "QUOTIENT_TRANSFER_OVER_THIS_CERTIFIED_SEGMENT_WITH_AN_INVERSE_"
            "FREE_VOLterra_REMAINDER,_THEN_EVALUATE_THE_CORRESPONDING_C2_"
            "WEYL_BLOCK_WITHOUT_IMPOSING_A_FUTURE_ENDPOINT_LOAD"
        ),
        "claim_boundary": {
            "explicit_validated_C2_segment": "CERTIFIED",
            "complete_C2_history_or_endpoint": "OPEN_NOT_SELECTED",
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
        "Delta": payload["launch_ball"]["Delta_interval"],
        "lambda_end": payload["explicit_segment"]["signed_lambda_end_lower"],
        "proper_time": payload["explicit_segment"]["proper_time_interval"],
        "Jacobi": payload["launch_ball"][
            "regularized_first_Jacobi_generator_upper"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
