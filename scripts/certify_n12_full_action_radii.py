"""Assemble the fail-closed full-action N12 radii calculation.

The map, branch selector, action coordinates, and physical gates are those of
the existing 57-row N12 solve.  This script only combines independently
derived center data and retained-action ball majorants.  It distinguishes a
negative numerical radii polynomial from a formally promoted proof.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np

from derive_n12_action_ball_majorants import action_bound
from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    embed_nested_state,
)
from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _attachment_jacobian_at_order,
    _authoritative_n6_event_child_anchor,
    _trace_jacobian_at_order,
)
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


ORDER = 12
POINTS = 96
INFLATION = 1.0 + 1.0e-10
CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_CHECKPOINT", ".tmp_direct_n12_corrected_branch_state.npz"
))
EXACT_NORMAL = Path(os.environ.get(
    "BHSM_N12_EXACT_NORMAL_JACOBIAN",
    ".tmp_direct_n12_exact_normal_jacobian_reproduced_1e20.npz",
))
EXACT_NORMAL_CROSS = Path(os.environ.get(
    "BHSM_N12_EXACT_NORMAL_JACOBIAN_CROSS",
    ".tmp_direct_n12_exact_normal_jacobian_reproduced_1e24.npz",
))
RESIDUAL = Path(os.environ.get(
    "BHSM_N12_EXACT_RESIDUAL_VECTOR",
    ".tmp_direct_n12_exact_residual_vector_90.json",
))
THIRD = Path(os.environ.get(
    "BHSM_N12_THIRD_VARIATION_RESULT",
    ".tmp_direct_n12_center_action_third_variations_current.npz",
))
ACTION_MAJORANT = Path(os.environ.get(
    "BHSM_N12_ACTION_MAJORANT_RESULT",
    ".tmp_direct_n12_stable_action_ball_majorants_89_2e11.json",
))
BORDERED = Path(os.environ.get(
    "BHSM_N12_BORDERED_BALL_RESULT",
    ".tmp_direct_n12_bordered_relative_ball_90_2e11_corrected.json",
))
ORDERED = Path(os.environ.get(
    "BHSM_N12_ORDERED_EIGENLINE_BALL_RESULT",
    ".tmp_direct_n12_ordered_event_eigenline_ball_90_2e11_corrected.json",
))
STABLE_CENTER = Path(os.environ.get(
    "BHSM_N12_STABLE_CENTER_RESULT",
    ".tmp_direct_n12_corrected_branch_stable_lm_90.json",
))
ONE_SIDED = Path(os.environ.get(
    "BHSM_N12_MOMENTUM_HESSIAN_ONE_SIDED_RESULT",
    ".tmp_direct_n12_center_momentum_hessian_one_sided_1e10.npz",
))
RICHARDSON = Path(os.environ.get(
    "BHSM_N12_MOMENTUM_HESSIAN_RICHARDSON",
    ".tmp_direct_n12_center_momentum_hessian_richardson.npz",
))
USE_RICHARDSON_CROSS_DIAGNOSTIC = os.environ.get(
    "BHSM_N12_USE_MOMENTUM_RICHARDSON_CROSS_DIAGNOSTIC", "1"
) == "1"
CROSS_RESOLUTION = Path(
    "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
)
RESULT = Path(os.environ.get(
    "BHSM_N12_FULL_RADII_RESULT",
    ".tmp_direct_n12_full_action_radii.json",
))


def _up(value: float) -> float:
    return math.nextafter(float(value) * INFLATION, math.inf)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _symmetric_power(matrix: np.ndarray, power: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(matrix)
    if np.min(values) <= 0.0:
        raise np.linalg.LinAlgError("positive Gram matrix required")
    return vectors @ np.diag(values ** power) @ vectors.T


def _decode(payload: dict[str, list[str]]) -> tuple[np.ndarray, ...]:
    return tuple(np.asarray([
        float.fromhex(value) for value in payload[name]
    ]) for name in ("coordinates", "velocities", "multipliers"))


def _bordered_state_left(matrix: np.ndarray, qdim: int) -> np.ndarray:
    return np.vstack((
        np.zeros((qdim, matrix.shape[1])),
        matrix[:qdim],
        matrix[qdim + 2:],
    ))


def _bordered_state_right(matrix: np.ndarray, qdim: int) -> np.ndarray:
    return np.vstack((
        np.zeros((qdim, matrix.shape[1])),
        matrix[:qdim],
        -matrix[qdim + 2:],
    ))


def _momentum_third_bound(
    sector: str,
    state: np.ndarray,
    normal: np.ndarray,
    weights: np.ndarray,
    q_weights: np.ndarray,
    third: np.ndarray,
    bordered_record: dict[str, object],
    radius: float,
) -> dict[str, float]:
    """Bound D^3 of the existing state-dependent canonical momentum."""

    qdim = dimensions(ORDER)["coordinates"]
    q = state[:qdim]
    jet = exact_full_action_jet_at_state(
        ORDER, q, state[qdim:2 * qdim], state[2 * qdim:], points=POINTS
    )
    gradient = np.asarray(jet.gradient) / weights
    hessian = (
        np.asarray(jet.hessian)
        / weights[:, None]
        / weights[None, :]
    )
    attachment = _attachment_jacobian_at_order(ORDER, q)
    boundary_scaling = _symmetric_power(
        attachment @ np.diag(1.0 / q_weights ** 2) @ attachment.T,
        -0.5,
    )
    combined = np.vstack((
        boundary_scaling @ attachment,
        hessian[2 * qdim:, qdim:2 * qdim],
    ))
    bordered = np.block([
        [hessian[qdim:2 * qdim, qdim:2 * qdim], -combined.T],
        [combined, np.zeros((combined.shape[0], combined.shape[0]))],
    ])
    inverse = np.linalg.inv(bordered)
    rhs = np.zeros((bordered.shape[0], 2))
    rhs[qdim:qdim + 2] = boundary_scaling
    solution = inverse @ rhs

    signs = (-1.0) ** np.arange(ORDER)
    boundary_value = q[1 + 2 * ORDER:1 + 3 * ORDER] @ signs
    first_bordered = []
    for column in range(normal.shape[1]):
        direction = normal[:, column]
        hessian_derivative = np.tensordot(
            third, direction, axes=(2, 0)
        )
        raw_q_direction = direction[:qdim] / q_weights
        boundary_direction = (
            raw_q_direction[1 + 2 * ORDER:1 + 3 * ORDER] @ signs
        )
        attachment_derivative = np.zeros_like(attachment)
        attachment_derivative[0, 1 + 2 * ORDER:1 + 3 * ORDER] = (
            -2.0 / np.cosh(2.0 * boundary_value) ** 2
            * boundary_direction * signs
        )
        attachment_derivative[1] = -attachment_derivative[0]
        combined_derivative = np.vstack((
            boundary_scaling @ attachment_derivative,
            hessian_derivative[2 * qdim:, qdim:2 * qdim],
        ))
        first_bordered.append(np.block([
            [hessian_derivative[
                qdim:2 * qdim, qdim:2 * qdim
            ], -combined_derivative.T],
            [combined_derivative,
             np.zeros((combined.shape[0], combined.shape[0]))],
        ]))
    first_bordered = np.asarray(first_bordered)
    first_solution = np.einsum(
        "ab,ibc,cd->iad", -inverse, first_bordered, solution
    )
    first_solution_matrix = first_solution.transpose(1, 0, 2).reshape(
        bordered.shape[0], -1
    )
    left = _bordered_state_left(inverse.T, qdim)
    right_solution = _bordered_state_right(solution, qdim)
    right_first = _bordered_state_right(first_solution_matrix, qdim)
    right_identity = _bordered_state_right(
        np.eye(bordered.shape[0]), qdim
    )
    mixed_specs = {
        "A_G2_U": [normal, normal, left, right_solution],
        "A_G2_U1": [normal, normal, left, right_first],
        "A_G3_U": [normal, normal, normal, left, right_solution],
        "A_G2_operator": [normal, normal, left, right_identity],
        "A_G3_operator": [
            normal, normal, normal, left, right_identity
        ],
    }
    mixed = {
        name: float(action_bound(
            state, projection=normal, mixed_directions=directions
        ).d[-1])
        for name, directions in mixed_specs.items()
    }

    # The saddle matrix also contains the retained nonlinear attachment
    # Jacobian.  Global derivatives of -tanh(2s) give |B''| <= 8 and
    # |B'''| <= 32; include these rather than sampling the boundary chart.
    boundary_covector = np.zeros(qdim)
    boundary_covector[1 + 2 * ORDER:1 + 3 * ORDER] = (
        signs / q_weights[1 + 2 * ORDER:1 + 3 * ORDER]
    )
    normal_boundary_norm = float(np.linalg.norm(
        normal[:qdim].T @ boundary_covector
    ))
    boundary_row_norm = float(np.linalg.norm(
        boundary_scaling @ np.asarray([1.0, -1.0])
    ))

    def attachment_term(matrix: np.ndarray, coefficient: float) -> float:
        return coefficient * boundary_row_norm * (
            float(np.linalg.norm(inverse.T[:qdim], 2))
            * float(np.linalg.norm(matrix[qdim:qdim + 2], 2))
            + float(np.linalg.norm(inverse.T[qdim:qdim + 2], 2))
            * float(np.linalg.norm(matrix[:qdim], 2))
        )

    second_coefficient = 8.0 * normal_boundary_norm ** 2
    third_coefficient = 32.0 * normal_boundary_norm ** 3
    mixed["A_G2_U"] += attachment_term(solution, second_coefficient)
    mixed["A_G2_U1"] += attachment_term(
        first_solution_matrix, second_coefficient
    )
    mixed["A_G3_U"] += attachment_term(solution, third_coefficient)
    mixed["A_G2_operator"] += attachment_term(
        np.eye(bordered.shape[0]), second_coefficient
    )
    mixed["A_G3_operator"] += attachment_term(
        np.eye(bordered.shape[0]), third_coefficient
    )

    relative_first_ball = (
        float(bordered_record["relative_first_variation_bound"])
        + radius * float(bordered_record["relative_second_variation_bound"])
    ) / (1.0 - float(
        bordered_record["relative_ball_perturbation_bound"]
    ))
    u0_center = float(np.linalg.norm(solution, 2))
    u1_center = float(np.linalg.norm(first_solution_matrix, 2))
    u0_ball = u0_center
    u1_ball = u1_center
    for _ in range(32):
        b2u = mixed["A_G2_U"] + mixed["A_G2_operator"] * max(
            0.0, u0_ball - u0_center
        )
        u2_ball = 2.0 * relative_first_ball * u1_ball + b2u
        next_u1 = u1_center + radius * u2_ball
        next_u0 = u0_center + radius * next_u1
        if abs(next_u1 - u1_ball) <= 1.0e-12 * max(next_u1, 1.0):
            u0_ball, u1_ball = next_u0, next_u1
            break
        u0_ball, u1_ball = next_u0, next_u1
    b2u = mixed["A_G2_U"] + mixed["A_G2_operator"] * (
        u0_ball - u0_center
    )
    u2_ball = 2.0 * relative_first_ball * u1_ball + b2u
    b2u1 = mixed["A_G2_U1"] + mixed["A_G2_operator"] * (
        u1_ball - u1_center
    )
    b3u = mixed["A_G3_U"] + mixed["A_G3_operator"] * (
        u0_ball - u0_center
    )
    u3_ball = (
        3.0 * relative_first_ball * u2_ball + 3.0 * b2u1 + b3u
    )

    velocity_output = np.zeros((state.size, qdim))
    velocity_output[qdim:2 * qdim] = np.eye(qdim)
    c3_ball = float(action_bound(
        state,
        projection=normal,
        mixed_directions=[
            velocity_output, normal, normal, normal
        ],
    ).d[-1])
    c0_center = float(np.linalg.norm(gradient[qdim:2 * qdim]))
    c1_center = float(np.linalg.norm(
        hessian[qdim:2 * qdim] @ normal, 2
    ))
    c2_center = float(np.linalg.norm(
        np.einsum(
            "vab,ai,bj->vij",
            third[qdim:2 * qdim], normal, normal,
        ).reshape(qdim, -1),
        2,
    ))
    c2_ball = c2_center + radius * c3_ball
    c1_ball = c1_center + radius * c2_ball
    c0_ball = c0_center + radius * c1_ball
    p3_ball = (
        u3_ball * c0_ball
        + 3.0 * u2_ball * c1_ball
        + 3.0 * u1_ball * c2_ball
        + u0_ball * c3_ball
    )
    return {
        "relative_A_G1_ball_bound": _up(relative_first_ball),
        "U0_center": _up(u0_center),
        "U1_center": _up(u1_center),
        "U0_ball": _up(u0_ball),
        "U1_ball": _up(u1_ball),
        "U2_ball": _up(u2_ball),
        "U3_ball": _up(u3_ball),
        "c0_ball": _up(c0_ball),
        "c1_ball": _up(c1_ball),
        "c2_ball": _up(c2_ball),
        "c3_ball": _up(c3_ball),
        "canonical_momentum_third_variation_bound": _up(p3_ball),
        **{name: _up(value) for name, value in mixed.items()},
    }


def main() -> None:
    size = dimensions(ORDER)
    qdim = size["coordinates"]
    mdim = size["multipliers"]
    state_dimension = 2 * qdim + mdim
    frequencies = spectral_frequencies(ORDER)
    q_weights = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
    m_weights = np.sqrt(1.0 + frequencies["multipliers"] ** 2)
    state_weights = np.concatenate((
        q_weights, np.ones(qdim), m_weights
    ))

    checkpoint = np.load(CHECKPOINT)
    state = np.asarray(checkpoint["state"], dtype=float)
    exact = np.load(EXACT_NORMAL)
    normal = np.asarray(exact["normal_basis"], dtype=float)
    analytic_jacobian = np.asarray(
        exact["analytic_normal_jacobian"], dtype=float
    )
    paired_jacobian = np.asarray(
        exact["paired_normal_jacobian"], dtype=float
    )
    exact_cross = np.load(EXACT_NORMAL_CROSS)
    cross_jacobian = np.asarray(
        exact_cross["analytic_normal_jacobian"], dtype=float
    )
    if not (
        np.array_equal(state, np.asarray(exact_cross["center_state"]))
        and np.array_equal(normal, np.asarray(exact_cross["normal_basis"]))
    ):
        raise ValueError("cross-step exact Jacobian belongs to another center")
    if not np.array_equal(state, np.asarray(exact["center_state"])):
        raise ValueError("exact normal Jacobian belongs to another center")
    inverse = np.linalg.inv(analytic_jacobian)
    residual_payload = json.loads(RESIDUAL.read_text(encoding="utf-8"))
    residual = np.asarray(residual_payload["exact_residual_vector"])
    if residual.shape != (57,):
        raise ValueError("57-row exact residual vector required")
    majorant = json.loads(ACTION_MAJORANT.read_text(encoding="utf-8"))
    bordered = json.loads(BORDERED.read_text(encoding="utf-8"))
    ordered = json.loads(ORDERED.read_text(encoding="utf-8"))
    stable = json.loads(STABLE_CENTER.read_text(encoding="utf-8"))
    if not all(payload.get("validation_passed") is True for payload in (
        majorant, bordered, ordered
    )):
        raise ValueError("validated component ball certificates required")
    radius = float(majorant["action_coordinate_ball_radius"])
    if not (
        radius == float(bordered["action_coordinate_ball_radius"])
        == float(ordered["action_coordinate_ball_radius"])
    ):
        raise ValueError("component certificates use different balls")
    third_payload = np.load(THIRD)
    if not np.array_equal(
        state, np.asarray(third_payload["center_state"])
    ):
        raise ValueError("third variation belongs to another center")

    # Fixed approximate inverse data.  The paired slopes remain diagnostic;
    # the actual numerical derivative enclosure comes from two independent
    # non-subtractive complex-step evaluations of the action formula.
    inverse_residual = float(np.linalg.norm(
        np.eye(57) - inverse @ analytic_jacobian, 2
    ))
    jacobian_cross_method = float(np.linalg.norm(
        analytic_jacobian - paired_jacobian, 2
    ))
    jacobian_complex_step_enclosure = float(np.linalg.norm(
        analytic_jacobian - cross_jacobian, 2
    ))
    z0 = _up(
        inverse_residual
        + float(np.linalg.norm(inverse, 2))
        * jacobian_complex_step_enclosure
    )
    y_bound = _up(float(np.linalg.norm(inverse @ residual)))

    # Constraint blocks: exact center Hessians plus action-derived third
    # variations already composed with the fixed approximate inverse.
    constraint_records = []
    constraint_z2 = 0.0
    for sector_index, (sector, row_start) in enumerate((
        ("event", 0), ("child", 30)
    )):
        sector_state = state[
            sector_index * state_dimension:
            (sector_index + 1) * state_dimension
        ]
        sector_normal = normal[
            sector_index * state_dimension:
            (sector_index + 1) * state_dimension
        ]
        jet = exact_full_action_jet_at_state(
            ORDER,
            sector_state[:qdim],
            sector_state[qdim:2 * qdim],
            sector_state[2 * qdim:],
            points=POINTS,
        )
        hessian = (
            np.asarray(jet.hessian)
            / state_weights[:, None]
            / state_weights[None, :]
        )
        third = np.asarray(third_payload[sector])
        # The retained constraint energy is the canonical v.L_v-L row.
        velocity_contraction = np.zeros(state_dimension)
        velocity_contraction[qdim:2 * qdim] = (
            sector_state[qdim:2 * qdim]
        )
        velocity_to_v = np.zeros((state_dimension, state_dimension))
        velocity_to_v[qdim:2 * qdim, qdim:2 * qdim] = np.eye(qdim)
        energy_hessian = (
            np.tensordot(velocity_contraction, third, axes=(0, 0))
            + velocity_to_v.T @ hessian
            + hessian @ velocity_to_v
            - hessian
        )
        multiplier_hessians = np.einsum(
            "mab,ai,bj->mij",
            third[2 * qdim:], sector_normal, sector_normal,
        )
        energy_normal_hessian = (
            sector_normal.T @ energy_hessian @ sector_normal
        )
        row_hessians = np.concatenate((
            multiplier_hessians, energy_normal_hessian[None]
        ))
        inverse_block = inverse[:, row_start:row_start + mdim + 1]
        center_applied = float(np.linalg.norm(np.einsum(
            "km,mij->kij", inverse_block, row_hessians
        )))

        multiplier_output = np.zeros((state_dimension, 57))
        multiplier_output[2 * qdim:] = inverse_block[:, :mdim].T
        multiplier_third = float(action_bound(
            sector_state,
            projection=sector_normal,
            mixed_directions=[
                multiplier_output,
                sector_normal, sector_normal, sector_normal,
            ],
        ).d[-1])
        mapped_velocity_normal = np.zeros((state_dimension, 57))
        mapped_velocity_normal[qdim:2 * qdim] = (
            sector_normal[qdim:2 * qdim]
        )
        energy_fourth = float(action_bound(
            sector_state,
            projection=sector_normal,
            mixed_directions=[
                velocity_contraction,
                sector_normal, sector_normal, sector_normal,
            ],
        ).d[-1])
        energy_mapped_third = float(action_bound(
            sector_state,
            projection=sector_normal,
            mixed_directions=[
                mapped_velocity_normal, sector_normal, sector_normal,
            ],
        ).d[-1])
        energy_action_third = float(action_bound(
            sector_state,
            projection=sector_normal,
            mixed_directions=[
                sector_normal, sector_normal, sector_normal,
            ],
        ).d[-1])
        energy_third_applied = float(np.linalg.norm(
            inverse_block[:, -1]
        )) * (
            energy_fourth
            + 3.0 * energy_mapped_third
            + energy_action_third
        )
        block_z2 = _up(
            center_applied
            + radius * (multiplier_third + energy_third_applied)
        )
        constraint_z2 += block_z2
        constraint_records.append({
            "sector": sector,
            "center_applied_Hessian_bound": _up(center_applied),
            "applied_multiplier_third_variation_bound": _up(
                multiplier_third
            ),
            "applied_energy_third_variation_bound": _up(
                energy_third_applied
            ),
            "ball_applied_Hessian_bound": block_z2,
        })

    # Ordered event and the sole nonlinear boundary chart row.
    ordered_scale = float(stable["ordered_scale"])
    ordered_scaled_hessian = (
        float(ordered["bounds"][
            "selected_eigenvalue_raw_Hessian_bound"
        ]) / ordered_scale
    )
    ordered_z2 = _up(
        float(np.linalg.norm(inverse[:, 25])) * ordered_scaled_hessian
    )
    trace = _trace_jacobian_at_order(ORDER)
    child_attachment = _attachment_jacobian_at_order(
        ORDER, state[state_dimension:state_dimension + qdim]
    )
    boundary = np.vstack((trace, child_attachment[1]))
    boundary_inverse_sqrt = _symmetric_power(
        boundary @ np.diag(1.0 / q_weights ** 2) @ boundary.T,
        -0.5,
    )
    nonlinear_boundary_output = (
        inverse[:, 26:30] @ boundary_inverse_sqrt[:, 3]
    )
    signs = (-1.0) ** np.arange(ORDER)
    boundary_covector = np.zeros(qdim)
    boundary_covector[1 + 2 * ORDER:1 + 3 * ORDER] = (
        signs / q_weights[1 + 2 * ORDER:1 + 3 * ORDER]
    )
    attachment_hessian_global = 2.0 * float(
        boundary_covector @ boundary_covector
    )
    boundary_z2 = _up(
        float(np.linalg.norm(nonlinear_boundary_output))
        * attachment_hessian_global
    )

    # Canonical momentum: independently evaluated one-sided center Hessian,
    # an action-derived D^3p truncation enclosure, and the same D^3p bound
    # for variation over the root ball.
    bordered_records = {
        (record["sector"], record["lift"]): record
        for record in bordered["records"]
    }
    momentum_records = []
    for sector_index, sector in enumerate(("event", "child")):
        sector_state = state[
            sector_index * state_dimension:
            (sector_index + 1) * state_dimension
        ]
        sector_normal = normal[
            sector_index * state_dimension:
            (sector_index + 1) * state_dimension
        ]
        momentum_records.append(_momentum_third_bound(
            sector,
            sector_state,
            sector_normal,
            state_weights,
            q_weights,
            np.asarray(third_payload[sector]),
            bordered_records[(sector, "v")],
            radius,
        ))
    momentum_third = _up(sum(
        record["canonical_momentum_third_variation_bound"]
        for record in momentum_records
    ))
    one_sided = np.load(ONE_SIDED)
    if not (
        np.array_equal(state, np.asarray(one_sided["center_state"]))
        and np.array_equal(normal, np.asarray(one_sided["normal_basis"]))
    ):
        raise ValueError("one-sided momentum data belongs to another center")
    one_sided_mismatch = np.asarray(one_sided["mismatch"])
    forward_step = float(json.loads(
        ONE_SIDED.with_suffix(".json").read_text(encoding="utf-8")
    )["forward_action_coordinate_step"])
    payload = json.loads(CROSS_RESOLUTION.read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    anchor = _authoritative_n6_event_child_anchor(payload)
    child6 = _decode(anchor["child_exact"])
    embedded_child = embed_nested_state(*child6, 6, ORDER)
    momentum_attachment = _attachment_jacobian_at_order(
        ORDER, embedded_child[0]
    )
    momentum_sqrt = _symmetric_power(
        momentum_attachment @ momentum_attachment.T, 0.5
    )
    momentum_output = inverse[:, 55:57] @ momentum_sqrt
    center_applied_approximation = float(np.linalg.norm(np.einsum(
        "ko,oij->kij", momentum_output, one_sided_mismatch
    )))
    truncation_unscaled = _up(
        math.sqrt(57.0) * 0.5 * forward_step * momentum_third
    )
    # A deliberately high operation count bounds ordinary binary64
    # accumulation around each complex-step canonical-pair evaluation.
    operation_count = 1_000_000
    epsilon = np.finfo(float).eps
    gamma = operation_count * epsilon / (
        1.0 - operation_count * epsilon
    )
    maximum_center_jacobian = max(
        float(np.max(np.abs(one_sided["event_momentum_jacobian"]))),
        float(np.max(np.abs(one_sided["child_momentum_jacobian"]))),
    )
    arithmetic_unscaled = _up(
        2.0 * gamma * maximum_center_jacobian / forward_step
        * math.sqrt(2.0 * 57.0 ** 2)
    )
    # The forward Taylor remainder and explicit floating-arithmetic bound
    # already enclose the one-sided center Hessian.  A Richardson replay is
    # therefore an optional independent diagnostic, not a mathematical term
    # required by the radii proof.
    if USE_RICHARDSON_CROSS_DIAGNOSTIC:
        richardson = np.load(RICHARDSON)
        if not (
            np.array_equal(state, np.asarray(richardson["center_state"]))
            and np.array_equal(normal, np.asarray(richardson["normal_basis"]))
        ):
            raise ValueError("Richardson momentum data belongs to another center")
        cross_method_unscaled = float(np.linalg.norm(
            one_sided_mismatch - np.asarray(richardson["mismatch"])
        ))
    else:
        cross_method_unscaled = 0.0
    momentum_output_norm = float(np.linalg.norm(momentum_output, 2))
    momentum_z2 = _up(
        center_applied_approximation
        + momentum_output_norm * (
            truncation_unscaled
            + arithmetic_unscaled
            + cross_method_unscaled
            + radius * momentum_third
        )
    )

    z2 = _up(
        constraint_z2 + ordered_z2 + boundary_z2 + momentum_z2
    )
    polynomial_at_radius = _up(
        y_bound + z0 * radius + 0.5 * z2 * radius ** 2 - radius
    )
    contraction_bound = _up(z0 + z2 * radius)
    discriminant = 1.0 - 2.0 * z2 * y_bound
    roots = None
    if discriminant > 0.0:
        root = math.sqrt(discriminant)
        roots = [
            (1.0 - z0 - root) / z2,
            (1.0 - z0 + root) / z2,
        ]
    numerical_radii_closed = bool(
        polynomial_at_radius < 0.0
        and contraction_bound < 1.0
        and radius > y_bound
    )

    # The scalar/mixed majorants use outward-inflated deterministic binary64
    # arithmetic, but the dense center inverse and complex-step evaluations
    # are not yet replayed by an independent directed-rounding interval
    # backend.  Keep theorem promotion fail-closed until that final audit.
    formal_interval_center_audit = False
    validation_passed = bool(
        numerical_radii_closed and formal_interval_center_audit
    )
    result = {
        "classification": (
            "DIRECT_N12_FULL_ACTION_RADII_CERTIFICATE"
            if validation_passed else
            "DIRECT_N12_NUMERICAL_RADII_CANDIDATE_CLOSED_"
            "FORMAL_INTERVAL_CENTER_AUDIT_OPEN"
            if numerical_radii_closed else
            "DIRECT_N12_NUMERICAL_CERTIFICATE_NOT_YET_OBTAINED"
        ),
        "order": ORDER,
        "points": POINTS,
        "action_coordinate_ball_radius": radius,
        "inputs": {
            str(path): _sha256(path) for path in (
                CHECKPOINT, EXACT_NORMAL, EXACT_NORMAL_CROSS, RESIDUAL, THIRD,
                ACTION_MAJORANT, BORDERED, ORDERED, ONE_SIDED,
            )
        } | ({str(RICHARDSON): _sha256(RICHARDSON)}
             if USE_RICHARDSON_CROSS_DIAGNOSTIC else {}),
        "center": {
            "exact_F12_norm": float(np.linalg.norm(residual)),
            "Y_approximate_inverse_residual_bound": y_bound,
            "analytic_normal_rank": int(np.linalg.matrix_rank(
                analytic_jacobian
            )),
            "analytic_normal_smallest_singular_value": float(
                np.linalg.svd(analytic_jacobian, compute_uv=False)[-1]
            ),
            "inverse_operator_norm": float(np.linalg.norm(inverse, 2)),
            "center_inverse_residual": inverse_residual,
            "analytic_vs_paired_J_operator_discrepancy": (
                jacobian_cross_method
            ),
            "analytic_complex_step_cross_enclosure": (
                jacobian_complex_step_enclosure
            ),
            "Z0_with_complex_step_enclosure": z0,
        },
        "applied_Hessian_ball_bounds": {
            "event_and_child_constraints": constraint_records,
            "ordered_event": ordered_z2,
            "boundary_chart": boundary_z2,
            "canonical_momentum": {
                "sectors": momentum_records,
                "joint_D3p_bound": momentum_third,
                "one_sided_center_applied_approximation": (
                    center_applied_approximation
                ),
                "forward_truncation_unscaled_bound": truncation_unscaled,
                "binary64_arithmetic_unscaled_bound": arithmetic_unscaled,
                "one_sided_vs_Richardson_unscaled_discrepancy": (
                    cross_method_unscaled if USE_RICHARDSON_CROSS_DIAGNOSTIC
                    else None
                ),
                "one_sided_Taylor_and_arithmetic_enclosure_is_sufficient": True,
                "Richardson_cross_diagnostic_used": (
                    USE_RICHARDSON_CROSS_DIAGNOSTIC
                ),
                "momentum_output_operator_norm": momentum_output_norm,
                "ball_applied_Hessian_bound": momentum_z2,
            },
            "total_Z2": z2,
        },
        "radii_polynomial": {
            "formula": "p(r)=Y+Z0*r+(Z2/2)*r^2-r",
            "value_at_candidate_radius": polynomial_at_radius,
            "contraction_bound_Z0_plus_Z2_r": contraction_bound,
            "discriminant": discriminant,
            "negative_interval_roots": roots,
            "numerical_radii_candidate_closed": numerical_radii_closed,
        },
        "validation": {
            "unchanged_exact_F12": True,
            "corrected_action_owned_ordered_branch": True,
            "all_component_ball_majorants_closed": True,
            "numerical_radii_polynomial_negative": numerical_radii_closed,
            "independent_directed_rounding_center_audit": (
                formal_interval_center_audit
            ),
            "new_physics_equation_constraint_gate_or_selector": False,
        },
        "validation_passed": validation_passed,
        "exact_next_dependency": (
            "REPLAY_THE_57_ROW_CENTER_F_J_AND_ONE_SIDED_CANONICAL_"
            "MOMENTUM_EVALUATIONS_WITH_INDEPENDENT_DIRECTED_ROUNDING_"
            "INTERVAL_LINEAR_ALGEBRA;_THEN_TRANSFER_THE_CERTIFIED_BALL_"
            "THROUGH_THE_EXISTING_ETA_EVENT_DIRAC_AND_PERSISTENCE_GATES"
        ),
        "DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED": False,
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
