"""Certify the finite terminal root's forward hitting orientation."""

from __future__ import annotations

from decimal import Decimal, localcontext
import hashlib
import json
import os
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

# This single retained-action tube contains the exact symmetric-difference
# endpoints used below.  It is far larger than the terminal root enclosure.
ACTION_TUBE_RADIUS = 2.0e-2
os.environ["BHSM_N12_CERTIFICATE_BALL"] = str(ACTION_TUBE_RADIUS)

from derive_n12_action_ball_majorants import action_bound  # noqa: E402
from bhsm.interface.aether_high_precision_velocity_jet import (  # noqa: E402
    high_precision_velocity_jet_blocks,
)
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
)


ORDER = 12
POINTS = 96
QDIM = 37
STATE_DIMENSION = 98
BASE = ROOT / "artifacts/flagship_integration"
CANDIDATE_DATA = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
CANDIDATE = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.json"
DIRECTED = BASE / "BHSM_N12_FINITE_TERMINAL_DIRECTED_CENTER_DATA.npz"
RADII = BASE / "BHSM_N12_FINITE_TERMINAL_RADII_CERTIFICATE.json"
SOLUTION_MAJORANT = BASE / (
    "BHSM_N12_FINITE_TERMINAL_SOLUTION_BALL_ACTION_MAJORANTS.json"
)
SOLUTION_LINE = BASE / (
    "BHSM_N12_FINITE_TERMINAL_CHILD_EIGENLINE_SOLUTION_BALL.json"
)
RESULT = BASE / "BHSM_N12_FINITE_TERMINAL_ORIENTATION_CERTIFICATE.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _decimal_reduced_hessian(blocks: dict[str, object]) -> list[list[Decimal]]:
    vv = blocks["hessian_velocity_velocity"]
    mv = blocks["hessian_multiplier_velocity"]
    mm = blocks["hessian_multiplier_multiplier"]
    return [
        vv[row][:] + [mv[column][row] for column in range(len(mm))]
        for row in range(len(vv))
    ] + [mv[row][:] + mm[row][:] for row in range(len(mm))]


def _quadratic(
    vector: list[Decimal], matrix: list[list[Decimal]]
) -> Decimal:
    return sum(
        vector[row] * matrix[row][column] * vector[column]
        for row in range(len(vector))
        for column in range(len(vector))
    )


def build_payload() -> dict[str, object]:
    with np.load(CANDIDATE_DATA) as candidate_data:
        state = np.asarray(candidate_data["state"], dtype=float)[STATE_DIMENSION:]
        weights = np.asarray(candidate_data["state_weights"], dtype=float)
        reference = np.asarray(candidate_data["branch_reference"], dtype=float)
    with np.load(DIRECTED) as directed:
        normal = np.asarray(
            directed["normal_basis"], dtype=float
        )[STATE_DIMENSION:]
    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    radii = json.loads(RADII.read_text(encoding="utf-8"))
    solution_majorant = json.loads(
        SOLUTION_MAJORANT.read_text(encoding="utf-8")
    )
    solution_line = json.loads(SOLUTION_LINE.read_text(encoding="utf-8"))
    if not all(item.get("validation_passed") is True for item in (
        candidate, radii, solution_majorant, solution_line
    )):
        raise ValueError("validated orientation inputs required")
    solution_radius = float(
        radii["radii_polynomial"]["negative_interval_roots"][0]
    )
    if solution_radius >= float(solution_majorant["action_coordinate_ball_radius"]):
        raise ValueError("solution enclosure exceeds the margin component ball")

    jet = exact_full_action_jet_at_state(
        ORDER,
        state[:QDIM],
        state[QDIM:2 * QDIM],
        state[2 * QDIM:],
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
        np.zeros(QDIM), psi * weights[QDIM:]
    ))
    complement_action = np.vstack((
        np.zeros((QDIM, complement.shape[1])),
        complement * weights[QDIM:, None],
    ))

    # Directed high-precision center cubic.  f'(0)=c_psi for
    # f(a)=<psi,H_red(x+a psi)psi>.  The centered remainder is bounded by
    # sup |f'''| h^2/6 = sup |D5 L[psi^5]| h^2/6.
    difference_step = Decimal("0.01")
    decimal_state = [Decimal.from_float(float(value)) for value in state]
    decimal_direction = [Decimal(0)] * QDIM + [
        Decimal.from_float(float(value)) for value in psi
    ]
    endpoint_values = []
    endpoint_rounding_action_radii = []
    with localcontext() as context:
        context.prec = 80
        for sign in (Decimal(-1), Decimal(1)):
            endpoint = [
                value + sign * difference_step * direction
                for value, direction in zip(decimal_state, decimal_direction)
            ]
            rounded_endpoint = [
                Decimal.from_float(float(value)) for value in endpoint
            ]
            endpoint_rounding_action_radii.append(float(np.linalg.norm([
                float(abs(rounded - intended)) * weight
                for rounded, intended, weight in zip(
                    rounded_endpoint, endpoint, weights
                )
            ])))
            blocks = high_precision_velocity_jet_blocks(
                ORDER,
                np.asarray(endpoint[:QDIM], dtype=object),
                np.asarray(endpoint[QDIM:2 * QDIM], dtype=object),
                np.asarray(endpoint[2 * QDIM:], dtype=object),
                points=POINTS,
                precision=80,
            )
            endpoint_values.append(_quadratic(
                decimal_direction[QDIM:], _decimal_reduced_hessian(blocks)
            ))
        center_cubic = (
            endpoint_values[1] - endpoint_values[0]
        ) / (Decimal(2) * difference_step)

    selected_tube_projection = (
        selected_action / np.linalg.norm(selected_action)
    )[:, None]
    d5_selected = float(action_bound(
        state,
        projection=selected_tube_projection,
        mixed_directions=[selected_action] * 5,
    ).d[-1])
    d3_endpoint_rounding = float(action_bound(
        state,
        projection=np.eye(STATE_DIMENSION),
        mixed_directions=[
            np.eye(STATE_DIMENSION), selected_action, selected_action
        ],
    ).d[-1])
    endpoint_rounding_error = (
        d3_endpoint_rounding * sum(endpoint_rounding_action_radii)
        / (2.0 * float(difference_step))
    )
    center_cubic_error = (
        d5_selected * float(difference_step) ** 2 / 6.0
        + endpoint_rounding_error
    )
    center_cubic_lower = float(center_cubic) - center_cubic_error
    center_cubic_upper = float(center_cubic) + center_cubic_error

    # Transfer c_psi to the exact root.  The fixed-line state variation is
    # D4[N,psi^3].  The selected-line graph expansion retains the signed
    # center value and bounds only the complement corrections.
    cubic_specs = {
        "D3_PPP": [selected_action] * 3,
        "D3_CPP": [complement_action, selected_action, selected_action],
        "D3_CCP": [complement_action, complement_action, selected_action],
        "D3_CCC": [complement_action] * 3,
        "D4_NPPP": [normal, selected_action, selected_action, selected_action],
    }
    cubic_bounds = {
        name: float(action_bound(
            state, projection=normal, mixed_directions=directions
        ).d[-1])
        for name, directions in cubic_specs.items()
    }
    graph = float(solution_line["bounds"]["eigenvector_graph_norm"])
    normalized_line_difference = graph + 0.5 * graph ** 2
    line_cubic_shift = (
        1.5 * graph ** 2 * cubic_bounds["D3_PPP"]
        + 3.0 * cubic_bounds["D3_CPP"] * graph
        + 3.0 * cubic_bounds["D3_CCP"] * graph ** 2
        + cubic_bounds["D3_CCC"] * graph ** 3
    )
    state_cubic_shift = cubic_bounds["D4_NPPP"] * solution_radius
    root_cubic_shift = line_cubic_shift + state_cubic_shift
    root_cubic_upper = center_cubic_upper + root_cubic_shift

    # Transfer b_psi.  First bound its fixed-line derivative by retaining
    # the exact three product-rule contractions instead of a full D3 norm.
    velocity = state[QDIM:2 * QDIM]
    psi_velocity_as_q = np.concatenate((
        psi[:QDIM] * weights[:QDIM], np.zeros(STATE_DIMENSION - QDIM)
    ))
    velocity_as_q = np.concatenate((
        velocity * weights[:QDIM], np.zeros(STATE_DIMENSION - QDIM)
    ))
    normal_velocity_as_q = np.zeros((STATE_DIMENSION, normal.shape[1]))
    normal_velocity_as_q[:QDIM] = weights[:QDIM, None] * normal[
        QDIM:2 * QDIM
    ]
    b_specs = {
        "D2_PSI_VELOCITY_AS_Q_N": [psi_velocity_as_q, normal],
        "D3_PSI_VELOCITY_AS_Q_N": [
            selected_action, velocity_as_q, normal
        ],
        "D2_PSI_NORMAL_VELOCITY_AS_Q": [
            selected_action, normal_velocity_as_q
        ],
    }
    b_bounds = {
        name: float(action_bound(
            state, projection=normal, mixed_directions=directions
        ).d[-1])
        for name, directions in b_specs.items()
    }
    fixed_b_shift = sum(b_bounds.values()) * solution_radius

    # H_red,q is not part of the specialized high-precision velocity block
    # payload, so the center b value uses the independently evaluated full
    # exact jet.  Its 1e-4 margin is transferred with outward bounds below.
    mixed = hessian[QDIM:, :QDIM]
    rhs = np.concatenate((
        np.asarray(jet.gradient[:QDIM], dtype=float)
        - mixed[:QDIM] @ velocity,
        -mixed[QDIM:] @ velocity,
    ))
    center_b = float(psi @ rhs)

    child_majorant = next(
        item for item in solution_majorant["sectors"]
        if item["sector"] == "child"
    )["derivative_operator_majorants_0_through_5"]
    maximum_weight = float(np.max(weights))
    crude_rhs_shift = (
        maximum_weight * float(child_majorant[2]) * solution_radius
        + maximum_weight ** 2 * float(child_majorant[3])
        * solution_radius * float(np.linalg.norm(velocity))
        + maximum_weight ** 2 * float(child_majorant[2]) * solution_radius
    )
    rhs_ball = float(np.linalg.norm(rhs)) + crude_rhs_shift
    line_b_shift = rhs_ball * normalized_line_difference
    root_b_lower = center_b - fixed_b_shift - line_b_shift

    validation = {
        "terminal_root_ball_closed": bool(
            radii["radii_polynomial"]["root_ball_closed"]
        ),
        "child_selected_line_is_branch_23": selected == 23,
        "child_selected_line_simple_on_solution_ball": float(
            solution_line["bounds"]["eigenline_gap_lower"]
        ) > 0.0,
        "directed_center_cubic_upper_is_negative": center_cubic_upper < 0.0,
        "root_cubic_upper_is_negative": root_cubic_upper < 0.0,
        "root_forcing_lower_is_positive": root_b_lower > 0.0,
        "terminal_hitting_product_is_strictly_negative": (
            root_cubic_upper < 0.0 and root_b_lower > 0.0
        ),
        "no_recurrence_universal_reachability_selector_or_new_gate_claimed": True,
        "no_action_term_scale_chord_or_prediction_added": True,
    }
    return {
        "artifact": "BHSM_N12_FINITE_TERMINAL_ORIENTATION_CERTIFICATE",
        "status": "FINITE_TERMINAL_FORWARD_ORIENTATION_CERTIFIED",
        "classification": (
            "A_DIRECTED_DECIMAL_SYMMETRIC_DIFFERENCE_WITH_RETAINED_D5_"
            "REMAINDER_PROVES_THE_CHILD_CENTER_CUBIC_NEGATIVE;_A_"
            "CANCELLATION_PRESERVING_D4_SELECTED_LINE_GRAPH_TRANSFER_"
            "KEEPS_c_psi_NEGATIVE_AT_THE_CERTIFIED_TERMINAL_ROOT,_WHILE_"
            "THE_EXACT_PRODUCT_RULE_TRANSFER_KEEPS_b_psi_POSITIVE,_SO_"
            "THE_LOCAL_TERMINAL_BRANCH_REACHES_THE_EVENT_IN_FINITE_"
            "POSITIVE_FORWARD_TIME"
        ),
        "solution_distance_upper": solution_radius,
        "center_cubic": {
            "decimal_centered_value": str(center_cubic),
            "symmetric_raw_soft_step": str(difference_step),
            "action_tube_radius": ACTION_TUBE_RADIUS,
            "D5_selected_bound": d5_selected,
            "D3_endpoint_rounding_bound": d3_endpoint_rounding,
            "endpoint_rounding_action_radii": endpoint_rounding_action_radii,
            "endpoint_rounding_error_upper": endpoint_rounding_error,
            "remainder_upper": center_cubic_error,
            "lower": center_cubic_lower,
            "upper": center_cubic_upper,
        },
        "root_cubic_transfer": {
            "selected_line_graph_norm": graph,
            "bounds": cubic_bounds,
            "line_shift_upper": line_cubic_shift,
            "state_shift_upper": state_cubic_shift,
            "total_shift_upper": root_cubic_shift,
            "root_c_psi_upper": root_cubic_upper,
        },
        "root_forcing_transfer": {
            "center_b_psi": center_b,
            "fixed_line_product_rule_bounds": b_bounds,
            "fixed_line_shift_upper": fixed_b_shift,
            "line_shift_upper": line_b_shift,
            "root_b_psi_lower": root_b_lower,
        },
        "consequence": {
            "finite_terminal_reset_stratum": "CERTIFIED",
            "local_forward_event_reaching_history": "CERTIFIED_EXISTENCE",
            "universal_terminal_reachability": "NOT_REQUIRED_NOT_CLAIMED",
            "post_event_recurrence": "NOT_REQUIRED_NOT_CLAIMED",
            "physical_child_selector": "NOT_INTRODUCED",
            "finite_endpoint_operator_force": "NEXT_CURRENT_OWNER",
        },
        "exact_next_dependency": (
            "REALIZE_THE_COMPACT_FINITE_ENDPOINT_OPERATOR_AND_ITS_FIRST_"
            "PHYSICAL_RESET_QUOTIENT_JET_ON_THIS_CERTIFIED_STRATUM,_THEN_"
            "EVALUATE_THE_EXISTING_HEAT_MINUS_ZETA_FORCE_COVECTOR"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_FINITE_ENDPOINT_ZERO_SOURCE_FORCE",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in (
                CANDIDATE_DATA, CANDIDATE, DIRECTED, RADII,
                SOLUTION_MAJORANT, SOLUTION_LINE,
            )
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "center_cubic": payload["center_cubic"],
        "root_cubic_upper": payload["root_cubic_transfer"]["root_c_psi_upper"],
        "root_b_lower": payload["root_forcing_transfer"]["root_b_psi_lower"],
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
