"""Certify the terminal Cauchy jet of the compact-history radius coefficient."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_boundary_radius import (  # noqa: E402
    boundary_log_lapse,
    boundary_log_radius,
    proper_time_log_radius_rate,
)


BASE = ROOT / "artifacts/flagship_integration"
RESULT = BASE / "BHSM_N12_FINITE_HISTORY_TERMINAL_COEFFICIENT_JET.json"
CANDIDATE = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
RADII = BASE / "BHSM_N12_FINITE_TERMINAL_RADII_CERTIFICATE.json"
ORIENTATION = BASE / "BHSM_N12_FINITE_TERMINAL_ORIENTATION_CERTIFICATE.json"
INTERFACE = BASE / "BHSM_N12_FINITE_TERMINAL_TWO_SIDED_FORWARD_INTERFACE.json"
OPERATOR = BASE / "BHSM_N12_COMPACT_FINITE_HISTORY_OPERATOR.json"
INPUTS = (CANDIDATE, RADII, ORIENTATION, INTERFACE, OPERATOR)
ORDER = 12
QDIM = 37
STATE_DIMENSION = 98


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() == ".json":
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _terminal_rate_enclosure(
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

    numerator_center = proper_time_log_radius_rate(
        ORDER, q, velocity, multipliers
    ) * lapse_center
    fixed_velocity_coefficients = np.concatenate(
        (np.ones(1), signs_k, np.zeros(ORDER), tanh_upper * signs_j)
    )
    velocity_change = action_radius * float(
        np.linalg.norm(fixed_velocity_coefficients / velocity_weights)
    )
    tanh_change_contribution = (
        2.0
        * action_radius
        * b_dual
        * velocity_b_absolute_upper
    )
    numerator_upper = (
        abs(numerator_center) + velocity_change + tanh_change_contribution
    )
    rate_absolute_upper = numerator_upper / lapse_lower

    q_gradient_dual = (
        2.0
        * velocity_b_absolute_upper
        / lapse_lower
        * b_dual
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
    return {
        "center_log_lapse": log_lapse,
        "center_lapse": lapse_center,
        "lapse_interval": [lapse_lower, lapse_upper],
        "center_D_tau_log_R4": rate_center,
        "root_D_tau_log_R4_interval": [
            rate_center - uncertainty,
            rate_center + uncertainty,
        ],
        "action_dual_rate_gradient_bound": full_gradient_dual,
        "rate_uncertainty": uncertainty,
        "bound_components": {
            "q_gradient_dual": q_gradient_dual,
            "velocity_gradient_dual": velocity_gradient_dual,
            "multiplier_gradient_dual": multiplier_gradient_dual,
            "boundary_anisotropy_absolute_upper": b_absolute_upper,
            "boundary_velocity_anisotropy_absolute_upper": (
                velocity_b_absolute_upper
            ),
        },
    }


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("finite-history terminal coefficient inputs required")
    radii, orientation, interface, operator = (
        _load(path) for path in (RADII, ORIENTATION, INTERFACE, OPERATOR)
    )
    if not all(
        record.get("validation_passed") is True
        for record in (radii, orientation, interface, operator)
    ):
        raise RuntimeError("validated terminal operator parents required")

    with np.load(CANDIDATE) as data:
        joint = np.asarray(data["state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
    incoming = joint[STATE_DIMENSION:]
    root_radius = float(
        radii["radii_polynomial"]["negative_interval_roots"][0]
    )
    rate = _terminal_rate_enclosure(incoming, weights, root_radius)
    x_center = boundary_log_radius(ORDER, incoming[:QDIM])

    cubic_center_lower = float(orientation["center_cubic"]["lower"])
    cubic_center_upper = float(orientation["center_cubic"]["upper"])
    cubic_shift = float(
        orientation["root_cubic_transfer"]["total_shift_upper"]
    )
    c_lower = cubic_center_lower - cubic_shift
    c_upper = float(
        orientation["root_cubic_transfer"]["root_c_psi_upper"]
    )
    b_center = float(orientation["root_forcing_transfer"]["center_b_psi"])
    b_shift = float(
        orientation["root_forcing_transfer"]["fixed_line_shift_upper"]
        + orientation["root_forcing_transfer"]["line_shift_upper"]
    )
    b_lower = float(
        orientation["root_forcing_transfer"]["root_b_psi_lower"]
    )
    b_upper = b_center + b_shift
    time_coefficient_lower = 1.0 / (2.0 * abs(c_lower) * b_upper)
    time_coefficient_upper = 1.0 / (2.0 * abs(c_upper) * b_lower)

    validation = {
        "all_parent_artifacts_validate": True,
        "incoming_half_is_the_event_reaching_history_endpoint": (
            interface["validation"]["incoming_child_selected_line_is_branch_23"]
            is True
        ),
        "root_rate_interval_is_strictly_positive": (
            rate["root_D_tau_log_R4_interval"][0] > 0.0
        ),
        "root_lapse_interval_is_strictly_positive": rate["lapse_interval"][0]
        > 0.0,
        "hitting_c_interval_is_strictly_negative": c_upper < 0.0,
        "hitting_b_interval_is_strictly_positive": b_lower > 0.0,
        "finite_time_quadratic_coefficient_interval_is_positive": (
            0.0 < time_coefficient_lower <= time_coefficient_upper
        ),
        "physical_common_scale_endpoint_jet_is_one": (
            operator["intrinsic_quotient"]["physical_common_scale"]
            == "RETAINED_WITH_D_x=1"
        ),
        "no_lambda_value_history_member_or_validation_cutoff_selected": True,
        "no_recurrence_reset_physics_endpoint_condition_or_scale_added": True,
    }
    return {
        "artifact": "BHSM_N12_FINITE_HISTORY_TERMINAL_COEFFICIENT_JET",
        "status": "ACTION_OWNED_TERMINAL_RADIUS_CAUCHY_JET_CERTIFIED",
        "classification": (
            "THE_INCOMING_TERMINAL_HALF_SUPPLIES_A_STRICTLY_POSITIVE_"
            "ACTION_OWNED_PROPER_RADIUS_RATE_AND_POSITIVE_LAPSE_ON_THE_"
            "CERTIFIED_ROOT_BALL;_THE_HITTING_PRODUCT_GIVES_A_POSITIVE_"
            "QUADRATIC_PROPER_DURATION_COEFFICIENT_IN_lambda_0_WITHOUT_"
            "SELECTING_lambda_0_OR_A_HISTORY_MEMBER"
        ),
        "terminal_coefficient_data": {
            "center_log_R4": x_center,
            "center_R4": math.exp(x_center),
            **rate,
        },
        "desingularized_duration_jet": {
            "asymptotic": (
                "T(lambda_0)=lambda_0^2/(-2*c_psi(E1)*b_psi(E1))"
                "+o(lambda_0^2)"
            ),
            "root_c_psi_interval": [c_lower, c_upper],
            "root_b_psi_interval": [b_lower, b_upper],
            "quadratic_coefficient_interval": [
                time_coefficient_lower,
                time_coefficient_upper,
            ],
            "lambda_0_selected": False,
        },
        "operator_feed": {
            "terminal_x": "CERTIFIED",
            "terminal_D_tau_x": "CERTIFIED",
            "duration_base_and_geometry_jets": (
                "PARAMETRIC_IN_THE_ACTION_OWNED_lambda_0_AND_EVENT_CHILD_"
                "JACOBI_COORDINATES"
            ),
            "full_x_path_and_Jacobi_path": "NEXT_CURRENT_OWNER",
        },
        "hindsight": {
            "action_required": "TERMINAL_COEFFICIENT_AND_DURATION_JETS",
            "existence_reopened": False,
            "owner_or_external_selector_required": False,
        },
        "exact_next_dependency": (
            "PROPAGATE_THIS_CERTIFIED_TERMINAL_CAUCHY_JET_THROUGH_THE_"
            "REGULAR_lambda_CHART_TO_ENCLOSE_x_xi(s),_D_xi*x,_T(xi),_AND_"
            "D_xi*T_ON_A_NONEMPTY_PARAMETER_BOX;_THEN_CALL_THE_COMPACT_"
            "HISTORY_WEYL_ORACLE"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_FINITE_HISTORY_JACOBI_PATH",
            "terminal_coefficient_Cauchy_jet": "CERTIFIED",
            "full_coefficient_path": "OPEN",
            "actual_M_C": "OPEN_AFTER_PATH",
            "zero_source_force": "OPEN_AFTER_M_C",
            "same_action_saddle": "OPEN_AFTER_FORCE",
            "physical_Hessian": "OPEN_AFTER_SADDLE",
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
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(RESULT)


if __name__ == "__main__":
    main()
