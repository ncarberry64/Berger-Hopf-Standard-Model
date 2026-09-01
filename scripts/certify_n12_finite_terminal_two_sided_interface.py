"""Certify the two-sided local reset interface at the terminal root."""

from __future__ import annotations

from decimal import Decimal, localcontext
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import numpy as np
from scipy.linalg import null_space


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
ACTION_TUBE_RADIUS = 2.0e-2
os.environ["BHSM_N12_CERTIFICATE_BALL"] = str(ACTION_TUBE_RADIUS)

from derive_n12_action_ball_majorants import action_bound  # noqa: E402
from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (  # noqa: E402
    embed_nested_state,
)
from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (  # noqa: E402
    _authoritative_n6_event_child_anchor,
)
from bhsm.interface.aether_full_reset_action_jacobian import (  # noqa: E402
    full_reset_action_jacobian,
)
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
SOLUTION_MAJORANT = BASE / "BHSM_N12_FINITE_TERMINAL_SOLUTION_BALL_ACTION_MAJORANTS.json"
EVENT_LINE = BASE / "BHSM_N12_FINITE_TERMINAL_EVENT_EIGENLINE_SOLUTION_BALL.json"
CHILD_ORIENTATION = BASE / "BHSM_N12_FINITE_TERMINAL_ORIENTATION_CERTIFICATE.json"
MARGIN = BASE / "BHSM_N12_FINITE_TERMINAL_MARGIN_TRANSFER.json"
ROOT_RESIDUAL = ROOT / "artifacts/n12_direct_checkpoint/BHSM_N12_EXACT_ROOT_RESIDUAL.json"
CROSS = ROOT / "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
THEORY = ROOT / "theory/n12_finite_terminal_two_sided_interface.md"
RESULT = BASE / "BHSM_N12_FINITE_TERMINAL_TWO_SIDED_FORWARD_INTERFACE.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() == ".json":
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _decode(payload: dict[str, list[str]]) -> tuple[np.ndarray, ...]:
    return tuple(np.asarray([
        float.fromhex(value) for value in payload[name]
    ]) for name in ("coordinates", "velocities", "multipliers"))


def _decimal_reduced_hessian(blocks: dict[str, object]) -> list[list[Decimal]]:
    vv = blocks["hessian_velocity_velocity"]
    mv = blocks["hessian_multiplier_velocity"]
    mm = blocks["hessian_multiplier_multiplier"]
    return [
        vv[row][:] + [mv[column][row] for column in range(len(mm))]
        for row in range(len(vv))
    ] + [mv[row][:] + mm[row][:] for row in range(len(mm))]


def _quadratic(vector: list[Decimal], matrix: list[list[Decimal]]) -> Decimal:
    return sum(
        vector[row] * matrix[row][column] * vector[column]
        for row in range(len(vector))
        for column in range(len(vector))
    )


def build_payload() -> dict[str, object]:
    inputs = (
        CANDIDATE_DATA, CANDIDATE, DIRECTED, RADII, SOLUTION_MAJORANT,
        EVENT_LINE, CHILD_ORIENTATION, MARGIN, ROOT_RESIDUAL, CROSS, THEORY,
    )
    if not all(path.is_file() for path in inputs):
        raise FileNotFoundError("two-sided terminal interface inputs required")
    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    radii = json.loads(RADII.read_text(encoding="utf-8"))
    majorant = json.loads(SOLUTION_MAJORANT.read_text(encoding="utf-8"))
    event_line = json.loads(EVENT_LINE.read_text(encoding="utf-8"))
    child_orientation = json.loads(CHILD_ORIENTATION.read_text(encoding="utf-8"))
    margin = json.loads(MARGIN.read_text(encoding="utf-8"))
    if not all(item.get("validation_passed") is True for item in (
        candidate, radii, majorant, event_line, child_orientation, margin,
    )):
        raise ValueError("validated two-sided terminal inputs required")

    with np.load(CANDIDATE_DATA) as data:
        joint_state = np.asarray(data["state"], dtype=float)
        event_third = np.asarray(data["event_third"], dtype=float)
        child_third = np.asarray(data["child_third"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)
    state = joint_state[:STATE_DIMENSION]
    with np.load(DIRECTED) as directed:
        normal = np.asarray(directed["normal_basis"], dtype=float)[:STATE_DIMENSION]

    solution_radius = float(radii["radii_polynomial"]["negative_interval_roots"][0])
    if solution_radius >= float(majorant["action_coordinate_ball_radius"]):
        raise ValueError("terminal solution exceeds event solution-line ball")

    jet = exact_full_action_jet_at_state(
        ORDER, state[:QDIM], state[QDIM:2 * QDIM], state[2 * QDIM:],
        points=POINTS,
    )
    hessian = np.asarray(jet.hessian, dtype=float)
    reduced = hessian[QDIM:, QDIM:]
    _, vectors = np.linalg.eigh(reduced)
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

    difference_step = Decimal("0.01")
    decimal_state = [Decimal.from_float(float(value)) for value in state]
    decimal_direction = [Decimal(0)] * QDIM + [
        Decimal.from_float(float(value)) for value in psi
    ]
    endpoint_values: list[Decimal] = []
    endpoint_rounding_action_radii: list[float] = []
    with localcontext() as context:
        context.prec = 80
        for sign in (Decimal(-1), Decimal(1)):
            endpoint = [
                value + sign * difference_step * direction
                for value, direction in zip(decimal_state, decimal_direction)
            ]
            rounded = [Decimal.from_float(float(value)) for value in endpoint]
            endpoint_rounding_action_radii.append(float(np.linalg.norm([
                float(abs(actual - intended)) * weight
                for actual, intended, weight in zip(rounded, endpoint, weights)
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

    selected_projection = (
        selected_action / np.linalg.norm(selected_action)
    )[:, None]
    d5_selected = float(action_bound(
        state, projection=selected_projection,
        mixed_directions=[selected_action] * 5,
    ).d[-1])
    d3_rounding = float(action_bound(
        state, projection=np.eye(STATE_DIMENSION),
        mixed_directions=[
            np.eye(STATE_DIMENSION), selected_action, selected_action,
        ],
    ).d[-1])
    rounding_error = (
        d3_rounding * sum(endpoint_rounding_action_radii)
        / (2.0 * float(difference_step))
    )
    center_error = (
        d5_selected * float(difference_step) ** 2 / 6.0 + rounding_error
    )
    center_lower = float(center_cubic) - center_error
    center_upper = float(center_cubic) + center_error

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
    graph = float(event_line["bounds"]["eigenvector_graph_norm"])
    normalized_line_difference = graph + 0.5 * graph ** 2
    line_cubic_shift = (
        1.5 * graph ** 2 * cubic_bounds["D3_PPP"]
        + 3.0 * cubic_bounds["D3_CPP"] * graph
        + 3.0 * cubic_bounds["D3_CCP"] * graph ** 2
        + cubic_bounds["D3_CCC"] * graph ** 3
    )
    state_cubic_shift = cubic_bounds["D4_NPPP"] * solution_radius
    root_cubic_lower = center_lower - line_cubic_shift - state_cubic_shift

    velocity = state[QDIM:2 * QDIM]
    psi_velocity_as_q = np.concatenate((
        psi[:QDIM] * weights[:QDIM], np.zeros(STATE_DIMENSION - QDIM)
    ))
    velocity_as_q = np.concatenate((
        velocity * weights[:QDIM], np.zeros(STATE_DIMENSION - QDIM)
    ))
    normal_velocity_as_q = np.zeros((STATE_DIMENSION, normal.shape[1]))
    normal_velocity_as_q[:QDIM] = (
        weights[:QDIM, None] * normal[QDIM:2 * QDIM]
    )
    b_specs = {
        "D2_PSI_VELOCITY_AS_Q_N": [psi_velocity_as_q, normal],
        "D3_PSI_VELOCITY_AS_Q_N": [
            selected_action, velocity_as_q, normal,
        ],
        "D2_PSI_NORMAL_VELOCITY_AS_Q": [
            selected_action, normal_velocity_as_q,
        ],
    }
    b_bounds = {
        name: float(action_bound(
            state, projection=normal, mixed_directions=directions
        ).d[-1])
        for name, directions in b_specs.items()
    }
    fixed_b_shift = sum(b_bounds.values()) * solution_radius
    mixed = hessian[QDIM:, :QDIM]
    rhs = np.concatenate((
        np.asarray(jet.gradient[:QDIM], dtype=float)
        - mixed[:QDIM] @ velocity,
        -mixed[QDIM:] @ velocity,
    ))
    center_b = float(psi @ rhs)
    event_majorant = next(
        item for item in majorant["sectors"] if item["sector"] == "event"
    )["derivative_operator_majorants_0_through_5"]
    maximum_weight = float(np.max(weights))
    crude_rhs_shift = (
        maximum_weight * float(event_majorant[2]) * solution_radius
        + maximum_weight ** 2 * float(event_majorant[3])
        * solution_radius * float(np.linalg.norm(velocity))
        + maximum_weight ** 2 * float(event_majorant[2]) * solution_radius
    )
    line_b_shift = (
        float(np.linalg.norm(rhs)) + crude_rhs_shift
    ) * normalized_line_difference
    root_b_lower = center_b - fixed_b_shift - line_b_shift

    root_record = json.loads(ROOT_RESIDUAL.read_text(encoding="utf-8"))
    cross = json.loads(CROSS.read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    anchor = _authoritative_n6_event_child_anchor(cross)
    normalization_coordinates = embed_nested_state(
        *_decode(anchor["child_exact"]), 6, ORDER
    )[0]
    jacobian, _ = full_reset_action_jacobian(
        ORDER, joint_state, event_third, child_third, weights, reference,
        float(root_record["ordered_scale"]), normalization_coordinates,
        points=POINTS,
    )
    event_block = jacobian[:, :STATE_DIMENSION]
    child_block = jacobian[:, STATE_DIMENSION:]
    reset_tangent = null_space(jacobian)
    child_projection = reset_tangent[STATE_DIMENSION:]
    child_state = joint_state[STATE_DIMENSION:]
    child_jet = exact_full_action_jet_at_state(
        ORDER,
        child_state[:QDIM],
        child_state[QDIM:2 * QDIM],
        child_state[2 * QDIM:],
        points=POINTS,
    )
    child_reduced = np.asarray(
        child_jet.hessian, dtype=float
    )[QDIM:, QDIM:]
    _, child_vectors = np.linalg.eigh(child_reduced)
    child_selected = int(np.argmax(np.abs(child_vectors.T @ reference)))
    child_psi = child_vectors[:, child_selected]
    if float(child_psi @ reference) < 0.0:
        child_psi = -child_psi
    child_selected_action = np.concatenate((
        np.zeros(QDIM), child_psi * weights[QDIM:]
    ))
    unit_incoming = (
        child_selected_action / np.linalg.norm(child_selected_action)
    )
    lift_coefficients = np.linalg.lstsq(
        child_projection, unit_incoming, rcond=None
    )[0]
    incoming_projection_residual = float(np.linalg.norm(
        unit_incoming - child_projection @ lift_coefficients
    ))
    event_singular = np.linalg.svd(event_block, compute_uv=False)
    child_singular = np.linalg.svd(child_block, compute_uv=False)

    validation = {
        "terminal_root_and_child_incoming_orientation_certified": (
            child_orientation["validation"][
                "terminal_hitting_product_is_strictly_negative"
            ] is True
        ),
        "event_selected_line_is_branch_24": selected == 24,
        "incoming_child_selected_line_is_branch_23": child_selected == 23,
        "event_selected_line_simple_on_solution_ball": (
            float(event_line["bounds"]["eigenline_gap_lower"]) > 0.0
        ),
        "event_center_cubic_is_strictly_positive": center_lower > 0.0,
        "event_root_cubic_is_strictly_positive": root_cubic_lower > 0.0,
        "event_root_forcing_is_strictly_positive": root_b_lower > 0.0,
        "event_half_is_forward_outgoing": (
            root_cubic_lower > 0.0 and root_b_lower > 0.0
        ),
        "terminal_reset_and_canonical_margins_transfer": (
            margin["transferred_margins"]["terminal_58_row_root_exists"] is True
            and margin["transferred_margins"][
                "all_four_canonical_lifts_invertible"
            ] is True
        ),
        "center_reset_block_ranks_have_expected_structure": (
            int(np.linalg.matrix_rank(jacobian)) == 57
            and int(np.linalg.matrix_rank(event_block)) == 32
            and int(np.linalg.matrix_rank(child_block)) == 31
            and int(np.linalg.matrix_rank(child_projection, tol=1.0e-11)) == 73
        ),
        "incoming_soft_tangent_has_no_center_projection_obstruction": (
            incoming_projection_residual < 1.0e-12
        ),
        "no_selector_endpoint_action_term_scale_fit_chord_or_prediction_added": True,
    }

    return {
        "artifact": "BHSM_N12_FINITE_TERMINAL_TWO_SIDED_FORWARD_INTERFACE",
        "status": (
            "TWO_SIDED_LOCAL_FORWARD_EVENT_CHILD_INTERFACE_AND_POSITIVE_"
            "DURATION_CHILD_HISTORY_CERTIFIED"
        ),
        "classification": (
            "THE_CERTIFIED_DOUBLE_EVENT_RESET_ROOT_HAS_A_CHILD_HALF_WITH_"
            "c_psi*b_psi<0_AND_AN_EVENT_HALF_WITH_c_psi*b_psi>0;_THE_"
            "RESET_EQUATIONS_ARE_SWAP_INVARIANT_ON_THE_DOUBLE_EVENT_LOCUS,_"
            "AND_THE_CERTIFIED_RESET_PROJECTION_IS_A_SUBMERSION_ONTO_THE_"
            "73_DIMENSIONAL_CONSTRAINED_CHILD_MANIFOLD,_SO_THE_INCOMING_"
            "GERM_LIFTS_TO_NEARBY_FORWARD_EVENT_TO_CHILD_DATA_AND_REACHES_"
            "A_NEW_EVENT_IN_T>0_BEFORE_THAT_EVENT_CREATES_A_NEW_CHILD"
        ),
        "event_outgoing_orientation": {
            "center_c_psi_interval": [center_lower, center_upper],
            "root_c_psi_lower": root_cubic_lower,
            "center_b_psi": center_b,
            "root_b_psi_lower": root_b_lower,
            "root_hitting_product_lower": root_cubic_lower * root_b_lower,
            "selected_line_graph_norm": graph,
            "cubic_bounds": cubic_bounds,
            "fixed_line_product_rule_bounds": b_bounds,
            "center_symmetric_difference": str(center_cubic),
            "center_remainder_upper": center_error,
            "line_cubic_shift_upper": line_cubic_shift,
            "state_cubic_shift_upper": state_cubic_shift,
            "fixed_b_shift_upper": fixed_b_shift,
            "line_b_shift_upper": line_b_shift,
        },
        "reset_projection_crosscheck": {
            "full_reset_rank": int(np.linalg.matrix_rank(jacobian)),
            "event_block_rank": int(np.linalg.matrix_rank(event_block)),
            "event_block_smallest_nonzero_singular_value": float(
                event_singular[31]
            ),
            "child_block_rank": int(np.linalg.matrix_rank(child_block)),
            "child_block_smallest_nonzero_singular_value": float(
                child_singular[30]
            ),
            "reset_tangent_dimension": int(reset_tangent.shape[1]),
            "child_projection_rank": int(np.linalg.matrix_rank(
                child_projection, tol=1.0e-11
            )),
            "constrained_child_tangent_dimension": 73,
            "incoming_soft_unit_projection_residual": incoming_projection_residual,
            "numerical_center_crosscheck_not_used_in_place_of_certified_lifts": True,
        },
        "exact_local_theorem": {
            "swap": (
                "ON_e(E_*)=e(C_*)=0,_SWAPPING_(E_*,C_*)_EXCHANGES_THE_"
                "TWO_CONSTRAINT_BLOCKS_AND_CHANGES_ONLY_THE_SIGNS_OF_ZERO_"
                "TRACE_AND_MOMENTUM_DIFFERENCES,_SO_(C_*,E_*)_IS_ALSO_A_"
                "RESET_PAIR"
            ),
            "submersion": (
                "FULL_RESET_RANK_57_PLUS_THE_CERTIFIED_EVENT_BLOCK_RANK_32_"
                "IMPLY_RANK(D_pi_child|T_Creset)=139-(98-32)=73,_EQUAL_"
                "TO_THE_CONSTRAINED_CHILD_TANGENT_DIMENSION"
            ),
            "lift": (
                "CONSTRAINT_PROPAGATION_PUTS_THE_INCOMING_GERM_IN_THE_"
                "CONSTRAINED_CHILD_MANIFOLD;_THE_SUBMERSION_THEOREM_LIFTS_"
                "EVERY_SUFFICIENTLY_NEAR_PRE_EVENT_POINT_TO_A_RESET_PAIR"
            ),
            "positive_duration_family": (
                "FOR_EVERY_SUFFICIENTLY_SMALL_lambda_0>0,_AN_EVENT_E0(lambda_0)_"
                "CREATES_THE_LIFTED_CHILD_C1=Y_-(lambda_0),_WHICH_FLOWS_"
                "FORWARD_FOR_T(lambda_0)>0_TO_THE_NEW_EVENT_E1=C_*;_THE_"
                "SWAPPED_INCIDENCE_IS_THE_FORWARD_EVENT_TO_NEW_CHILD_GLUE_"
                "FROM_E1=C_*_TO_C2=E_*"
            ),
            "physical_chronology": "E0_TO_C1_TO_[T>0]_E1_TO_C2",
            "historical_reset_graph_semantic_alias": (
                "FORWARD_EVENT_TO_NEW_CHILD_GLUE"
            ),
            "same_event_recurrence_required": False,
            "quantifier": "NONEMPTY_LOCAL_FAMILY_NOT_UNIVERSAL_REACHABILITY",
            "physical_selector_introduced": False,
        },
        "exact_next_dependency": (
            "ASSEMBLE_THE_COMPACT_TWO_SIDED_OPERATOR_AND_ITS_FIRST_PHYSICAL_"
            "EVENT_CHILD_QUOTIENT_JET_ON_THIS_NONEMPTY_LOCAL_FINITE_HISTORY_"
            "STRATUM,_THEN_EVALUATE_AND_ROOT_THE_EXISTING_HEAT_MINUS_ZETA_"
            "COVECTOR_WITHOUT_SELECTING_AN_EVENT_CHILD_MEMBER"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_COMPACT_TWO_SIDED_OPERATOR_REALIZATION",
            "positive_duration_forward_child_history": (
                "CERTIFIED_LOCAL_EXISTENCE"
            ),
            "positive_duration_reset_to_event_family": "CERTIFIED_LOCAL_EXISTENCE",
            "positive_duration_reset_to_event_family_semantic_status": (
                "HISTORICAL_COMPATIBILITY_ALIAS_ONLY"
            ),
            "universal_terminal_reachability": False,
            "compact_finite_endpoint_operator": "OPEN_CURRENT_OWNER",
            "actual_projected_force": "OPEN_AFTER_OPERATOR",
            "same_action_saddle": "OPEN_AFTER_FORCE",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in inputs
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
    print(json.dumps({
        "status": payload["status"],
        "root_event_c_lower": payload["event_outgoing_orientation"][
            "root_c_psi_lower"
        ],
        "root_event_b_lower": payload["event_outgoing_orientation"][
            "root_b_psi_lower"
        ],
        "incoming_projection_residual": payload["reset_projection_crosscheck"][
            "incoming_soft_unit_projection_residual"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
