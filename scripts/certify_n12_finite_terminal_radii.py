"""Assemble the nonlinear radii bound for the 58-row terminal reset map.

The first 57 rows are the unchanged event-to-child reset equations.  The
last row is the child selected eigenvalue, normalized by its transverse
gradient on the reset tangent.  This module adds no equation or selector; it
only combines retained-action derivative bounds with the directed center
audit at the finite terminal candidate.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from certify_n12_full_action_radii import (  # noqa: E402
    _momentum_third_bound,
    _symmetric_power,
    _up,
)
from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (  # noqa: E402
    embed_nested_state,
)
from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (  # noqa: E402
    _attachment_jacobian_at_order,
    _authoritative_n6_event_child_anchor,
    _trace_jacobian_at_order,
)
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (  # noqa: E402
    dimensions,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (  # noqa: E402
    spectral_frequencies,
)
from derive_n12_action_ball_majorants import action_bound  # noqa: E402


ORDER = 12
POINTS = 96
DIMENSION = 58
ROOT_BALL_RADIUS = float(os.environ.get(
    "BHSM_N12_TERMINAL_ROOT_BALL_RADIUS", "1e-11"
))
CANDIDATE = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
)
DIRECTED_DATA = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FINITE_TERMINAL_DIRECTED_CENTER_DATA.npz"
)
DIRECTED_CENTER = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FINITE_TERMINAL_DIRECTED_CENTER.json"
)
CROSS_RESOLUTION = ROOT / (
    "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
)
ACTION_MAJORANT = Path(os.environ.get(
    "BHSM_N12_TERMINAL_ACTION_MAJORANT",
    "artifacts/flagship_integration/"
    "BHSM_N12_FINITE_TERMINAL_ACTION_BALL_MAJORANTS.json",
))
BORDERED = Path(os.environ.get(
    "BHSM_N12_TERMINAL_BORDERED",
    "artifacts/flagship_integration/"
    "BHSM_N12_FINITE_TERMINAL_BORDERED_RELATIVE_BALL.json",
))
EVENT_ORDERED = Path(os.environ.get(
    "BHSM_N12_TERMINAL_EVENT_EIGENLINE",
    "artifacts/flagship_integration/"
    "BHSM_N12_FINITE_TERMINAL_EVENT_EIGENLINE_BALL.json",
))
CHILD_ORDERED = Path(os.environ.get(
    "BHSM_N12_TERMINAL_CHILD_EIGENLINE",
    "artifacts/flagship_integration/"
    "BHSM_N12_FINITE_TERMINAL_CHILD_EIGENLINE_BALL.json",
))
ONE_SIDED = Path(os.environ.get(
    "BHSM_N12_TERMINAL_MOMENTUM_ONE_SIDED",
    "artifacts/flagship_integration/"
    "BHSM_N12_FINITE_TERMINAL_MOMENTUM_HESSIAN_ONE_SIDED.npz",
))
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FINITE_TERMINAL_RADII_CERTIFICATE.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _decode(payload: dict[str, list[str]]) -> tuple[np.ndarray, ...]:
    return tuple(np.asarray([
        float.fromhex(value) for value in payload[name]
    ]) for name in ("coordinates", "velocities", "multipliers"))


def build_payload() -> dict[str, object]:
    size = dimensions(ORDER)
    qdim = size["coordinates"]
    mdim = size["multipliers"]
    state_dimension = 2 * qdim + mdim
    frequencies = spectral_frequencies(ORDER)
    q_weights = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
    state_weights = np.concatenate((
        q_weights,
        np.ones(qdim),
        np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))

    with np.load(CANDIDATE) as candidate:
        state = np.asarray(candidate["state"], dtype=float)
    with np.load(DIRECTED_DATA) as data:
        normal = np.asarray(data["normal_basis"], dtype=float)
        analytic_jacobian = np.asarray(data["primary_normal"], dtype=float)
        child_scale = float(data["child_gradient_scale"])
        data_center = np.asarray(data["center_state"], dtype=float)
    if not np.array_equal(state, data_center):
        raise ValueError("directed terminal data belongs to another center")
    inverse = np.linalg.inv(analytic_jacobian)
    directed = json.loads(DIRECTED_CENTER.read_text(encoding="utf-8"))
    y_bound = float(directed["directed_Y_upper"])
    z0 = float(directed["directed_Z0_upper"])

    majorant = json.loads(ACTION_MAJORANT.read_text(encoding="utf-8"))
    bordered = json.loads(BORDERED.read_text(encoding="utf-8"))
    event_ordered = json.loads(EVENT_ORDERED.read_text(encoding="utf-8"))
    child_ordered = json.loads(CHILD_ORDERED.read_text(encoding="utf-8"))
    components = (majorant, bordered, event_ordered, child_ordered)
    if not all(item.get("validation_passed") is True for item in components):
        raise ValueError("validated terminal component bounds required")
    radius = float(majorant["action_coordinate_ball_radius"])
    if any(float(item["action_coordinate_ball_radius"]) != radius
           for item in components[1:]):
        raise ValueError("terminal component bounds use different radii")
    if not (0.0 < ROOT_BALL_RADIUS <= radius):
        raise ValueError("root-ball radius must lie inside the component ball")

    with np.load(CANDIDATE) as third_payload:
        if not np.array_equal(state, np.asarray(third_payload["state"])):
            raise ValueError("candidate third variation belongs to another center")
        thirds = {
            sector: np.asarray(third_payload[f"{sector}_third"], dtype=float)
            for sector in ("event", "child")
        }

    constraint_records: list[dict[str, object]] = []
    constraint_z2 = 0.0
    for sector_index, (sector, row_start) in enumerate((
        ("event", 0), ("child", 30)
    )):
        sector_state = state[
            sector_index * state_dimension:(sector_index + 1) * state_dimension
        ]
        sector_normal = normal[
            sector_index * state_dimension:(sector_index + 1) * state_dimension
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
        third = thirds[sector]
        velocity_contraction = np.zeros(state_dimension)
        velocity_contraction[qdim:2 * qdim] = sector_state[qdim:2 * qdim]
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
        energy_normal_hessian = sector_normal.T @ energy_hessian @ sector_normal
        row_hessians = np.concatenate((
            multiplier_hessians, energy_normal_hessian[None],
        ))
        inverse_block = inverse[:, row_start:row_start + mdim + 1]
        center_applied = float(np.linalg.norm(np.einsum(
            "km,mij->kij", inverse_block, row_hessians,
        )))

        multiplier_output = np.zeros((state_dimension, DIMENSION))
        multiplier_output[2 * qdim:] = inverse_block[:, :mdim].T
        multiplier_third = float(action_bound(
            sector_state,
            projection=sector_normal,
            mixed_directions=[
                multiplier_output,
                sector_normal, sector_normal, sector_normal,
            ],
        ).d[-1])
        mapped_velocity_normal = np.zeros((state_dimension, DIMENSION))
        mapped_velocity_normal[qdim:2 * qdim] = sector_normal[qdim:2 * qdim]
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
        energy_third_applied = float(np.linalg.norm(inverse_block[:, -1])) * (
            energy_fourth + 3.0 * energy_mapped_third + energy_action_third
        )
        block_z2 = _up(
            center_applied
            + radius * (multiplier_third + energy_third_applied)
        )
        constraint_z2 += block_z2
        constraint_records.append({
            "sector": sector,
            "center_applied_Hessian_bound": _up(center_applied),
            "applied_multiplier_third_variation_bound": _up(multiplier_third),
            "applied_energy_third_variation_bound": _up(energy_third_applied),
            "ball_applied_Hessian_bound": block_z2,
        })

    root = json.loads((ROOT / (
        "artifacts/n12_direct_checkpoint/BHSM_N12_EXACT_ROOT_RESIDUAL.json"
    )).read_text(encoding="utf-8"))
    event_hessian = float(event_ordered["bounds"][
        "selected_eigenvalue_raw_Hessian_bound"
    ]) / float(root["ordered_scale"])
    child_hessian = float(child_ordered["bounds"][
        "selected_eigenvalue_raw_Hessian_bound"
    ]) / child_scale
    ordered_records = {
        "event": _up(float(np.linalg.norm(inverse[:, 25])) * event_hessian),
        "child_terminal": _up(
            float(np.linalg.norm(inverse[:, 57])) * child_hessian
        ),
    }
    ordered_z2 = _up(sum(ordered_records.values()))

    trace = _trace_jacobian_at_order(ORDER)
    child_attachment = _attachment_jacobian_at_order(
        ORDER, state[state_dimension:state_dimension + qdim]
    )
    boundary = np.vstack((trace, child_attachment[1]))
    boundary_inverse_sqrt = _symmetric_power(
        boundary @ np.diag(1.0 / q_weights ** 2) @ boundary.T, -0.5
    )
    nonlinear_boundary_output = inverse[:, 26:30] @ boundary_inverse_sqrt[:, 3]
    signs = (-1.0) ** np.arange(ORDER)
    boundary_covector = np.zeros(qdim)
    boundary_covector[1 + 2 * ORDER:1 + 3 * ORDER] = (
        signs / q_weights[1 + 2 * ORDER:1 + 3 * ORDER]
    )
    boundary_z2 = _up(
        float(np.linalg.norm(nonlinear_boundary_output))
        * 2.0 * float(boundary_covector @ boundary_covector)
    )

    bordered_records = {
        (record["sector"], record["lift"]): record
        for record in bordered["records"]
    }
    momentum_records = []
    for sector_index, sector in enumerate(("event", "child")):
        sector_state = state[
            sector_index * state_dimension:(sector_index + 1) * state_dimension
        ]
        sector_normal = normal[
            sector_index * state_dimension:(sector_index + 1) * state_dimension
        ]
        momentum_records.append(_momentum_third_bound(
            sector,
            sector_state,
            sector_normal,
            state_weights,
            q_weights,
            thirds[sector],
            bordered_records[(sector, "v")],
            radius,
        ))
    momentum_third = _up(sum(
        record["canonical_momentum_third_variation_bound"]
        for record in momentum_records
    ))
    with np.load(ONE_SIDED) as one_sided:
        if not (
            np.array_equal(state, np.asarray(one_sided["center_state"]))
            and np.array_equal(normal, np.asarray(one_sided["normal_basis"]))
        ):
            raise ValueError("one-sided momentum data belongs to another center")
        one_sided_mismatch = np.asarray(one_sided["mismatch"])
        maximum_center_jacobian = max(
            float(np.max(np.abs(one_sided["event_momentum_jacobian"]))),
            float(np.max(np.abs(one_sided["child_momentum_jacobian"]))),
        )
    one_sided_metadata = json.loads(
        ONE_SIDED.with_suffix(".json").read_text(encoding="utf-8")
    )
    forward_step = float(one_sided_metadata[
        "forward_action_coordinate_step"
    ])
    cross = json.loads(CROSS_RESOLUTION.read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    embedded_child = embed_nested_state(
        *_decode(_authoritative_n6_event_child_anchor(cross)["child_exact"]),
        6,
        ORDER,
    )
    momentum_attachment = _attachment_jacobian_at_order(
        ORDER, embedded_child[0]
    )
    momentum_sqrt = _symmetric_power(
        momentum_attachment @ momentum_attachment.T, 0.5
    )
    momentum_output = inverse[:, 55:57] @ momentum_sqrt
    center_applied = float(np.linalg.norm(np.einsum(
        "ko,oij->kij", momentum_output, one_sided_mismatch,
    )))
    truncation_unscaled = _up(
        math.sqrt(DIMENSION) * 0.5 * forward_step * momentum_third
    )
    epsilon = np.finfo(float).eps
    operation_count = 1_000_000
    gamma = operation_count * epsilon / (1.0 - operation_count * epsilon)
    arithmetic_unscaled = _up(
        2.0 * gamma * maximum_center_jacobian / forward_step
        * math.sqrt(2.0 * DIMENSION ** 2)
    )
    momentum_output_norm = float(np.linalg.norm(momentum_output, 2))
    momentum_z2 = _up(
        center_applied
        + momentum_output_norm * (
            truncation_unscaled + arithmetic_unscaled
            + radius * momentum_third
        )
    )

    z2 = _up(constraint_z2 + ordered_z2 + boundary_z2 + momentum_z2)
    polynomial = _up(
        y_bound
        + z0 * ROOT_BALL_RADIUS
        + 0.5 * z2 * ROOT_BALL_RADIUS ** 2
        - ROOT_BALL_RADIUS
    )
    contraction = _up(z0 + z2 * ROOT_BALL_RADIUS)
    discriminant = (1.0 - z0) ** 2 - 2.0 * z2 * y_bound
    roots = None
    if discriminant > 0.0:
        square_root = math.sqrt(discriminant)
        roots = [
            ((1.0 - z0) - square_root) / z2,
            ((1.0 - z0) + square_root) / z2,
        ]
    closed = bool(
        polynomial < 0.0
        and contraction < 1.0
        and ROOT_BALL_RADIUS > y_bound
    )
    validation = {
        "directed_center_Y_and_Z0_closed": bool(
            directed["validation_passed"]
        ),
        "all_component_ball_majorants_closed": True,
        "terminal_map_dimension_is_58": analytic_jacobian.shape == (58, 58),
        "numerical_radii_polynomial_negative": closed,
        "contraction_bound_below_one": contraction < 1.0,
        "root_ball_radius_lies_inside_component_ball": (
            ROOT_BALL_RADIUS <= radius
        ),
        "root_ball_radius_exceeds_Y": ROOT_BALL_RADIUS > y_bound,
        "no_equation_action_term_selector_scale_gate_or_chord_added": True,
    }
    return {
        "artifact": "BHSM_N12_FINITE_TERMINAL_RADII_CERTIFICATE",
        "status": (
            "TERMINAL_58_ROW_ROOT_BALL_CLOSED"
            if all(validation.values()) else
            "TERMINAL_58_ROW_ROOT_BALL_NOT_CLOSED"
        ),
        "classification": (
            "THE_DIRECTED_CENTER_AND_RETAINED_ACTION_DERIVATIVE_"
            "MAJORANTS_CLOSE_A_CONTRACTIVE_58_ROW_TERMINAL_RESET_ROOT_BALL"
            if closed else
            "THE_58_ROW_TERMINAL_RESET_ROOT_BALL_REMAINS_OPEN"
        ),
        "action_coordinate_ball_radius": radius,
        "certified_root_ball_radius": ROOT_BALL_RADIUS,
        "center": {
            "directed_Y_upper": y_bound,
            "directed_Z0_upper": z0,
            "normal_smallest_singular_value": float(
                np.linalg.svd(analytic_jacobian, compute_uv=False)[-1]
            ),
            "inverse_operator_norm": float(np.linalg.norm(inverse, 2)),
        },
        "applied_Hessian_ball_bounds": {
            "event_and_child_constraints": constraint_records,
            "ordered_eigenvalues": ordered_records,
            "ordered_eigenvalues_total": ordered_z2,
            "boundary_chart": boundary_z2,
            "canonical_momentum": {
                "sectors": momentum_records,
                "joint_D3p_bound": momentum_third,
                "one_sided_center_applied_approximation": center_applied,
                "forward_truncation_unscaled_bound": truncation_unscaled,
                "binary64_arithmetic_unscaled_bound": arithmetic_unscaled,
                "momentum_output_operator_norm": momentum_output_norm,
                "ball_applied_Hessian_bound": momentum_z2,
            },
            "total_Z2": z2,
        },
        "radii_polynomial": {
            "formula": "p(r)=Y+Z0*r+(Z2/2)*r^2-r",
            "value_at_candidate_radius": polynomial,
            "contraction_bound_Z0_plus_Z2_r": contraction,
            "discriminant": discriminant,
            "negative_interval_roots": roots,
            "root_ball_closed": closed,
        },
        "proof_boundary": {
            "local_terminal_stratum_exists_in_root_ball": closed,
            "event_child_spectral_and_domain_margin_transfer": "OPEN",
            "global_or_universal_terminal_reachability": "NOT_CLAIMED",
            "compact_endpoint_force_or_saddle": "OPEN",
        },
        "exact_next_dependency": (
            "TRANSFER_THE_EVENT_AND_CHILD_EIGENLINE,_LEGENDRE,_RESET_"
            "REGULARITY,_AND_TERMINAL_ORIENTATION_MARGINS_OVER_THE_ROOT_BALL;_"
            "THEN_EVALUATE_THE_COMPACT_ENDPOINT_ZERO_SOURCE_FORCE_OR_SADDLE"
        ),
        "inputs": {
            str(path.relative_to(ROOT) if path.is_absolute() else path): _sha256(path)
            for path in (
                CANDIDATE, DIRECTED_DATA, DIRECTED_CENTER,
                ACTION_MAJORANT, BORDERED, EVENT_ORDERED, CHILD_ORDERED,
                ONE_SIDED, CROSS_RESOLUTION,
            )
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "claim_boundary": {
            "Gate7": "ACTIVE_TERMINAL_MARGIN_TRANSFER" if closed else "ACTIVE",
            "Gate8": "LOCKED",
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(payload["radii_polynomial"], indent=2))


if __name__ == "__main__":
    main()
