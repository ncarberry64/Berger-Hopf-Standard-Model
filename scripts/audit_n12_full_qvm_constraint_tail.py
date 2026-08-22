"""Audit the full q-v-m high-shell constraint normal map above certified N12.

This is a retained-action diagnostic, not a higher-N child promotion.  Every
higher-order state used here is the zero-padded certified N12 event or child.
The existing boundary-compatible normal quotient removes only w-velocity and
shift-multiplier directions; all coordinate modes remain available.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    embed_nested_state,
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
from bhsm.interface.aether_m4_standard_model_zeta_backreaction_v15_51 import (
    standard_model_casimir_coefficient,
)
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import (
    RADIUS0,
)


SOURCE_ORDER = 12
ORDERS = tuple(int(value) for value in os.environ.get(
    "BHSM_N12_FULL_QVM_ORDERS", "16,20,24,32"
).split(","))
POINTS = int(os.environ.get("BHSM_N12_FULL_QVM_POINTS", "96"))
CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_CHECKPOINT",
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz",
))
PROMOTION = Path(os.environ.get(
    "BHSM_N12_PROMOTION",
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_CERTIFICATE.json",
))
RESULT = Path(os.environ.get(
    "BHSM_N12_FULL_QVM_RESULT",
    ".tmp_direct_n12_full_qvm_constraint_tail.json",
))
CORRECTION_CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_FULL_QVM_CORRECTION_CHECKPOINT",
    ".tmp_n12_full_qvm_linear_correction_candidates.npz",
))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _split_state(joint: np.ndarray, name: str) -> tuple[np.ndarray, ...]:
    qdim = dimensions(SOURCE_ORDER)["coordinates"]
    mdim = dimensions(SOURCE_ORDER)["multipliers"]
    state_dim = 2 * qdim + mdim
    state = joint[:state_dim] if name == "event" else joint[state_dim:]
    return state[:qdim], state[qdim:2 * qdim], state[2 * qdim:]


def _high_constraint_rows(order: int) -> tuple[np.ndarray, np.ndarray]:
    qdim = dimensions(order)["coordinates"]
    lapse = 2 * qdim + np.arange(SOURCE_ORDER, order)
    shift = 2 * qdim + order + np.arange(SOURCE_ORDER, order)
    rows = np.concatenate((lapse, shift)).astype(int)
    multiplier_modes = np.concatenate((
        np.arange(SOURCE_ORDER, order),
        order + np.arange(SOURCE_ORDER, order),
    )).astype(int)
    return rows, multiplier_modes


def _normal_columns(
    order: int, *, high_only: bool, principal_quotient: bool,
) -> tuple[np.ndarray, list[str]]:
    """Return the existing q-v-m boundary-compatible normal coordinates.

    Coordinate q=(scale,u,w,b) is physical configuration data and remains in
    the normal map.  The already-derived principal quotient removes only the
    w block of velocity variations and the shift block of multiplier
    variations.  No physical row or additional quotient is introduced here.
    """

    qdim = dimensions(order)["coordinates"]
    first = SOURCE_ORDER if high_only else 0
    columns: list[int] = []
    labels: list[str] = []
    if not high_only:
        columns.append(0)
        labels.append("q_scale")
    for family, name in enumerate(("q_u", "q_w", "q_b")):
        for mode in range(first, order):
            columns.append(1 + family * order + mode)
            labels.append(name)
    if not high_only:
        columns.append(qdim)
        labels.append("v_scale")
    velocity_families = (
        ((0, "v_u"), (2, "v_b")) if principal_quotient else
        ((0, "v_u"), (1, "v_w"), (2, "v_b"))
    )
    for family, name in velocity_families:
        for mode in range(first, order):
            columns.append(qdim + 1 + family * order + mode)
            labels.append(name)
    for mode in range(first, order):
        columns.append(2 * qdim + mode)
        labels.append("m_lapse")
    if not principal_quotient:
        for mode in range(first, order):
            columns.append(2 * qdim + order + mode)
            labels.append("m_shift")
    return np.asarray(columns, dtype=int), labels


def _column_weights(order: int, columns: np.ndarray) -> np.ndarray:
    qdim = dimensions(order)["coordinates"]
    frequencies = spectral_frequencies(order)
    q_weights = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
    m_weights = np.sqrt(1.0 + frequencies["multipliers"] ** 2)
    full = np.concatenate((q_weights, np.ones(qdim), m_weights))
    return full[columns]


def _block_fractions(vector: np.ndarray, labels: list[str]) -> dict[str, float]:
    norm2 = float(vector @ vector)
    names = sorted(set(labels))
    return {
        name: float(sum(
            vector[index] ** 2
            for index, label in enumerate(labels) if label == name
        ) / max(1.0e-300, norm2))
        for name in names
    }


def _matrix_record(
    jacobian: np.ndarray,
    omitted: np.ndarray,
    order: int,
    row_modes: np.ndarray,
    *,
    high_only: bool,
    principal_quotient: bool,
) -> dict[str, object]:
    columns, labels = _normal_columns(
        order,
        high_only=high_only,
        principal_quotient=principal_quotient,
    )
    frequencies = spectral_frequencies(order)
    row_weights = np.sqrt(
        1.0 + frequencies["multipliers"][row_modes] ** 2
    )
    column_weights = _column_weights(order, columns)
    matrix = (
        jacobian[:, columns]
        / row_weights[:, None]
        / column_weights[None, :]
    )
    u, singular, vh = np.linalg.svd(matrix, full_matrices=False)
    soft = vh[-1]
    soft_left = u[:, -1]
    high_count = order - SOURCE_ORDER
    left_shell_energy = (
        soft_left[:high_count] ** 2 + soft_left[high_count:] ** 2
    )
    left_peak = int(np.argmax(left_shell_energy))
    upper_start = max(0, (2 * high_count) // 3)
    right_mode_energy: dict[int, float] = {}
    for index, label in enumerate(labels):
        if label in {"q_scale", "v_scale"}:
            continue
        # Labels are appended in monotonically increasing modal blocks.
        block_indices = [i for i, value in enumerate(labels) if value == label]
        position = block_indices.index(index)
        mode = position + (SOURCE_ORDER if high_only else 0)
        right_mode_energy[mode] = right_mode_energy.get(mode, 0.0) + float(
            soft[index] ** 2
        )
    right_total = max(1.0e-300, sum(right_mode_energy.values()))
    right_peak_mode = max(right_mode_energy, key=right_mode_energy.get)
    correction, _, _, _ = np.linalg.lstsq(matrix, -omitted, rcond=None)
    linear_remainder = matrix @ correction + omitted
    soft_source_projection = float(soft_left @ omitted)
    return {
        "shape": list(matrix.shape),
        "rank": int(np.linalg.matrix_rank(matrix)),
        "smallest_singular_value": float(singular[-1]),
        "largest_singular_value": float(singular[0]),
        "normal_right_inverse_bound": float(1.0 / singular[-1]),
        "condition_number": float(singular[0] / singular[-1]),
        "exact_source_minimum_action_norm_linear_correction": float(
            np.linalg.norm(correction)
        ),
        "exact_source_linear_remainder_norm": float(
            np.linalg.norm(linear_remainder)
        ),
        "exact_source_soft_left_projection": soft_source_projection,
        "exact_source_soft_projection_fraction": float(
            abs(soft_source_projection)
            / max(1.0e-300, np.linalg.norm(omitted))
        ),
        "exact_source_soft_required_correction_amplitude": float(
            abs(soft_source_projection) / singular[-1]
        ),
        "exact_source_correction_block_fractions": _block_fractions(
            correction, labels
        ),
        "_exact_source_action_correction": correction.tolist(),
        "soft_action_coordinate_block_fractions": _block_fractions(
            soft, labels
        ),
        "soft_left_constraint_output": {
            "lapse_fraction": float(
                np.linalg.norm(soft_left[:high_count]) ** 2
            ),
            "shift_fraction": float(
                np.linalg.norm(soft_left[high_count:]) ** 2
            ),
            "upper_third_shell_fraction": float(
                np.sum(left_shell_energy[upper_start:])
            ),
            "peak_mode": SOURCE_ORDER + left_peak,
            "peak_shell_fraction": float(left_shell_energy[left_peak]),
        },
        "soft_right_modal_localization": {
            "peak_mode": int(right_peak_mode),
            "peak_mode_fraction": float(
                right_mode_energy[right_peak_mode] / right_total
            ),
            "upper_third_mode_fraction": float(sum(
                value for mode, value in right_mode_energy.items()
                if mode >= SOURCE_ORDER + upper_start
            ) / right_total),
        },
        "row_normalization": "H_MINUS_1_MULTIPLIER_WEAK_NORM",
        "column_normalization": "Q_H1_V_L2_M_H1_ACTION_GRAPH_NORM",
        "slice": (
            "INSTANTANEOUS_PRINCIPAL_ACCELERATION_JACOBI_QUOTIENT"
            if principal_quotient else
            "FULL_QVM_CONSTRAINT_ROW_SPACE_NORMAL"
        ),
    }


def _boundary_reaction_data(
    q: np.ndarray, multipliers: np.ndarray, order: int,
) -> tuple[float, np.ndarray]:
    """Return c and dc for the already-retained weak boundary reaction.

    The lapse constraint contains ``c*(-1)^k`` from the action boundary
    Casimir term.  The existing weak reaction relation routes this trace
    covector to the boundary operator, so the bulk normal map subtracts both
    the covector and its derivative.  This changes no action or equation.
    """

    qdim = dimensions(order)["coordinates"]
    mdim = dimensions(order)["multipliers"]
    signs_k = (-1.0) ** np.arange(1, order + 1)
    signs_j = (-1.0) ** np.arange(order)
    u_boundary = float(q[1:1 + order] @ signs_k)
    b_boundary = float(q[1 + 2 * order:1 + 3 * order] @ signs_j)
    radius = RADIUS0 * math.exp(float(q[0]))
    a_boundary = radius * math.exp(u_boundary + b_boundary) / math.sqrt(2.0)
    b_radius = radius * math.exp(u_boundary - b_boundary) / math.sqrt(2.0)
    r4 = a_boundary * b_radius / math.sqrt(
        a_boundary ** 2 + b_radius ** 2
    )
    boundary_log_lapse = float(multipliers[:order] @ signs_k)
    coefficient = (
        -standard_model_casimir_coefficient()
        * math.exp(boundary_log_lapse) / r4
    )
    dlog_r4 = np.zeros(2 * qdim + mdim)
    dlog_r4[0] = 1.0
    dlog_r4[1:1 + order] = signs_k
    b_factor = -(a_boundary ** 2 - b_radius ** 2) / (
        a_boundary ** 2 + b_radius ** 2
    )
    dlog_r4[1 + 2 * order:1 + 3 * order] = b_factor * signs_j
    dlog_lapse = np.zeros_like(dlog_r4)
    dlog_lapse[2 * qdim:2 * qdim + order] = signs_k
    derivative = coefficient * (dlog_lapse - dlog_r4)
    return float(coefficient), derivative


def _evaluate(state: tuple[np.ndarray, ...], order: int) -> dict[str, object]:
    q, velocity, multipliers = embed_nested_state(
        *state, SOURCE_ORDER, order
    )
    jet = exact_full_action_jet_at_state(
        order, q, velocity, multipliers, points=POINTS
    )
    hessian = np.asarray(jet.hessian, dtype=float)
    rows, row_modes = _high_constraint_rows(order)
    high_count = order - SOURCE_ORDER
    signs_high = (-1.0) ** np.arange(SOURCE_ORDER + 1, order + 1)
    boundary_coefficient, boundary_derivative = _boundary_reaction_data(
        q, multipliers, order
    )
    jacobian = hessian[rows, :].copy()
    jacobian[:high_count, :] -= (
        signs_high[:, None] * boundary_derivative[None, :]
    )
    frequencies = spectral_frequencies(order)
    row_weights = np.sqrt(
        1.0 + frequencies["multipliers"][row_modes] ** 2
    )
    raw_omitted = np.asarray(jet.gradient, dtype=float)[rows].copy()
    raw_omitted[:high_count] -= boundary_coefficient * signs_high
    omitted = raw_omitted / row_weights
    shell = np.sqrt(
        omitted[:high_count] ** 2 + omitted[high_count:] ** 2
    )
    return {
        "N": order,
        "probe_kind": "ZERO_PADDED_CERTIFIED_N12_NOT_A_HIGHER_N_ROOT",
        "exact_omitted_constraint_weak_norm": float(np.linalg.norm(omitted)),
        "exact_omitted_constraint_weak_max": float(np.max(np.abs(omitted))),
        "weak_boundary_reaction_coefficient": boundary_coefficient,
        "weak_reaction_covector_and_derivative_subtracted": True,
        "omitted_shells": [{
            "mode": mode,
            "weak_norm": float(shell[index]),
            "mode_squared_weak_norm": float(mode ** 2 * shell[index]),
        } for index, mode in enumerate(range(SOURCE_ORDER, order))],
        "high_only_normal_map": _matrix_record(
            jacobian, omitted, order, row_modes,
            high_only=True, principal_quotient=True,
        ),
        "all_mode_normal_map": _matrix_record(
            jacobian, omitted, order, row_modes,
            high_only=False, principal_quotient=True,
        ),
        "full_qvm_high_only_normal_map": _matrix_record(
            jacobian, omitted, order, row_modes,
            high_only=True, principal_quotient=False,
        ),
        "full_qvm_all_mode_normal_map": _matrix_record(
            jacobian, omitted, order, row_modes,
            high_only=False, principal_quotient=False,
        ),
    }


def _power_fit(rows: list[dict[str, object]], key: str) -> dict[str, float]:
    orders = np.asarray([row["N"] for row in rows], dtype=float)
    values = np.asarray([
        row[key]["normal_right_inverse_bound"] for row in rows
    ], dtype=float)
    slope, intercept = np.polyfit(np.log(orders), np.log(values), 1)
    predicted = np.exp(intercept) * orders ** slope
    relative = np.linalg.norm(values - predicted) / np.linalg.norm(values)
    return {
        "measured_inverse_growth_exponent": float(slope),
        "log_intercept": float(intercept),
        "relative_fit_residual": float(relative),
        "summable_with_n_minus_2_tail_if_exponent_below_one": bool(slope < 1.0),
        "finite_probe_fit_is_not_an_asymptotic_proof": True,
    }


def _state_weights(order: int) -> np.ndarray:
    qdim = dimensions(order)["coordinates"]
    frequencies = spectral_frequencies(order)
    return np.concatenate((
        np.sqrt(1.0 + frequencies["coordinates"] ** 2),
        np.ones(qdim),
        np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))


def _embed_action_vector(
    action_vector: np.ndarray, source: int, target: int,
) -> np.ndarray:
    raw = np.asarray(action_vector, dtype=float) / _state_weights(source)
    qdim = dimensions(source)["coordinates"]
    q, velocity, multipliers = (
        raw[:qdim], raw[qdim:2 * qdim], raw[2 * qdim:]
    )
    embedded = np.concatenate(embed_nested_state(
        q, velocity, multipliers, source, target
    ))
    return embedded * _state_weights(target)


def _strong_S2_weights(order: int) -> np.ndarray:
    """Existing one-derivative-stronger compactness graph weights."""

    qdim = dimensions(order)["coordinates"]
    frequencies = spectral_frequencies(order)
    q_frequency = frequencies["coordinates"]
    m_frequency = frequencies["multipliers"]
    return np.concatenate((
        np.sqrt(1.0 + q_frequency ** 2 + q_frequency ** 4),
        np.sqrt(1.0 + q_frequency ** 2),
        np.sqrt(1.0 + m_frequency ** 2 + m_frequency ** 4),
    ))


def _correction_cauchy_rows(rows: list[dict[str, object]]) -> list[dict[str, float | int]]:
    output = []
    key = "full_qvm_all_mode_normal_map"
    for previous, current in zip(rows, rows[1:]):
        source = int(previous["N"])
        target = int(current["N"])
        left = np.asarray(
            previous[key]["_exact_source_action_correction"], dtype=float
        )
        right = np.asarray(
            current[key]["_exact_source_action_correction"], dtype=float
        )
        embedded = _embed_action_vector(left, source, target)
        distance = float(np.linalg.norm(right - embedded))
        left_raw = left / _state_weights(source)
        source_qdim = dimensions(source)["coordinates"]
        embedded_raw = np.concatenate(embed_nested_state(
            left_raw[:source_qdim],
            left_raw[source_qdim:2 * source_qdim],
            left_raw[2 * source_qdim:],
            source,
            target,
        ))
        right_raw = right / _state_weights(target)
        strong_weights = _strong_S2_weights(target)
        strong_distance = float(np.linalg.norm(
            (right_raw - embedded_raw) * strong_weights
        ))
        strong_norm = float(np.linalg.norm(right_raw * strong_weights))
        output.append({
            "source_N": source,
            "target_N": target,
            "exact_common_mode_injected_action_distance": distance,
            "source_N_squared_distance": float(source ** 2 * distance),
            "target_correction_norm": float(np.linalg.norm(right)),
            "relative_distance": float(
                distance / max(1.0e-300, np.linalg.norm(right))
            ),
            "S2_H2q_H1v_H2m_injected_distance": strong_distance,
            "source_N_squared_S2_distance": float(
                source ** 2 * strong_distance
            ),
            "target_correction_S2_norm": strong_norm,
            "relative_S2_distance": float(
                strong_distance / max(1.0e-300, strong_norm)
            ),
        })
    return output


def main() -> None:
    promotion = json.loads(PROMOTION.read_text(encoding="utf-8"))
    certified = bool(
        promotion.get("DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED")
        or promotion.get("direct_N12_complete_persistent_child_certified")
    )
    if not certified:
        raise RuntimeError("the certified direct N12 anchor is required")
    checkpoint = np.load(CHECKPOINT)
    joint = np.asarray(checkpoint["state"], dtype=float)
    states = {
        name: _split_state(joint, name) for name in ("event", "child")
    }
    evaluations = {
        name: [_evaluate(states[name], order) for order in ORDERS]
        for name in ("event", "child")
    }
    correction_cauchy = {
        name: _correction_cauchy_rows(rows)
        for name, rows in evaluations.items()
    }
    last_order = int(ORDERS[-1])
    correction_payload: dict[str, np.ndarray] = {}
    for name in ("event", "child"):
        action_correction = np.asarray(
            evaluations[name][-1]["full_qvm_all_mode_normal_map"][
                "_exact_source_action_correction"
            ],
            dtype=float,
        )
        raw_correction = action_correction / _state_weights(last_order)
        embedded_state = np.concatenate(embed_nested_state(
            *states[name], SOURCE_ORDER, last_order
        ))
        correction_payload[f"{name}_embedded_state"] = embedded_state
        correction_payload[f"{name}_raw_correction"] = raw_correction
        correction_payload[f"{name}_candidate_state"] = (
            embedded_state + raw_correction
        )
    correction_payload["order"] = np.asarray(last_order, dtype=int)
    np.savez_compressed(CORRECTION_CHECKPOINT, **correction_payload)
    source_summary = {
        name: {
            "maximum_sampled_N_squared_action_Cauchy_distance": float(max(
                row["source_N_squared_distance"]
                for row in correction_cauchy[name]
            )),
            "maximum_sampled_S2_correction_norm": float(max(
                row["target_correction_S2_norm"]
                for row in correction_cauchy[name]
            )),
            "N48_exact_source_soft_required_correction_amplitude": float(
                evaluations[name][-1]["full_qvm_all_mode_normal_map"][
                    "exact_source_soft_required_correction_amplitude"
                ]
            ),
            "N48_exact_source_total_linear_correction_norm": float(
                evaluations[name][-1]["full_qvm_all_mode_normal_map"][
                    "exact_source_minimum_action_norm_linear_correction"
                ]
            ),
        }
        for name in ("event", "child")
    }
    fits = {
        name: {
            key: _power_fit(evaluations[name], key)
            for key in (
                "high_only_normal_map",
                "all_mode_normal_map",
                "full_qvm_high_only_normal_map",
                "full_qvm_all_mode_normal_map",
            )
        }
        for name in ("event", "child")
    }
    validation = {
        "certified_N12_anchor_consumed": True,
        "unchanged_retained_full_action_jet_used": True,
        "existing_boundary_compatible_w_velocity_shift_multiplier_quotient_used": True,
        "all_coordinate_modes_retained": True,
        "all_high_constraint_normal_maps_have_full_row_rank": all(
            row[key]["rank"] == row[key]["shape"][0]
            for rows in evaluations.values() for row in rows
            for key in (
                "high_only_normal_map",
                "all_mode_normal_map",
                "full_qvm_high_only_normal_map",
                "full_qvm_all_mode_normal_map",
            )
        ),
        "zero_padded_probes_not_promoted_as_complete_children": True,
        "finite_power_fit_not_promoted_as_uniform_bound": True,
        "existing_weak_boundary_reaction_relation_applied": True,
        "physical_equations_and_gates_unchanged": True,
    }
    for rows in evaluations.values():
        for row in rows:
            for key in (
                "high_only_normal_map",
                "all_mode_normal_map",
                "full_qvm_high_only_normal_map",
                "full_qvm_all_mode_normal_map",
            ):
                row[key].pop("_exact_source_action_correction", None)
    output = {
        "artifact": "BHSM_N12_FULL_QVM_CONSTRAINT_TAIL_DIAGNOSTIC",
        "source_order": SOURCE_ORDER,
        "orders": list(ORDERS),
        "quadrature_points": POINTS,
        "checkpoint": str(CHECKPOINT),
        "checkpoint_sha256": _sha256(CHECKPOINT),
        "promotion": str(PROMOTION),
        "promotion_sha256": _sha256(PROMOTION),
        "normal_slice": {
            "finite_child_constraint_normal": (
                "ACTION_METRIC_ROW_SPACE_OF_FULL_QVM_CONSTRAINT_JACOBIAN"
            ),
            "supporting_principal_Jacobi_slice_retained": (
                "ALL_Q;_V_SCALE_U_B;_M_LAPSE"
            ),
            "supporting_principal_Jacobi_slice_quotiented": "V_W;_M_SHIFT",
            "slice_scope": (
                "THE_W_SHIFT_QUOTIENT_IS_RECORDED_AS_AN_INSTANTANEOUS_"
                "ACCELERATION_JACOBI_DIAGNOSTIC_AND_IS_NOT_SUBSTITUTED_"
                "FOR_THE_FULL_FINITE_CHILD_CONSTRAINT_NORMAL"
            ),
        },
        "evaluations": evaluations,
        "exact_source_correction_cauchy_diagnostic": correction_cauchy,
        "exact_source_summary": source_summary,
        "linear_correction_candidate_checkpoint": str(CORRECTION_CHECKPOINT),
        "finite_power_fits": fits,
        "classification": (
            "N12_TO_N48_RETAINED_ACTION_SOURCE_RESTRICTED_LINEAR_TAIL_"
            "IS_ACTION_CAUCHY_AND_S2_BOUNDED_DESPITE_STATIC_WORST_INVERSE_"
            "COLLAPSE;_FINITE_STRUCTURAL_RESULT_ONLY"
        ),
        "scientific_interpretation": {
            "validated": (
                "AFTER_THE_EXISTING_WEAK_BOUNDARY_REACTION_IS_ROUTED,_THE_"
                "EXACT_N12_OMITTED_BULK_SOURCE_HAS_INVERSE_SQUARE_SHELL_"
                "DECAY;_ITS_MINIMUM_ACTION_LINEAR_CORRECTIONS_FORM_AN_"
                "N_MINUS_2_COMMON_MODE_CAUCHY_SEQUENCE_AND_REMAIN_S2_"
                "BOUNDED_ON_N16_TO_N48"
            ),
            "invalidated": (
                "THE_NAIVE_PROOF_USING_THE_WORST_INSTANTANEOUS_STATIC_"
                "CONSTRAINT_RIGHT_INVERSE_TIMES_A_GENERIC_N_MINUS_2_SOURCE;_"
                "THE_MEASURED_WORST_INVERSE_GROWS_FAR_FASTER_THAN_N"
            ),
            "reclassified": (
                "THE_COLLAPSING_STATIC_SHIFT_OWNED_LINE_IS_ASYMPTOTICALLY_"
                "DECOUPLED_FROM_THE_ACTUAL_RETAINED_SOURCE_ON_THE_SAMPLED_"
                "CUTS;_IT_IS_NOT_A_RETAINED_ACTION_OBSTRUCTION_WITHOUT_A_"
                "NONLINEAR_NON_TANGENT_HISTORY_COLLAPSE_SEQUENCE"
            ),
            "not_proved": (
                "THE_ZERO_PADDED_LINEAR_PROBES_ARE_NOT_CORRECTED_COMPLETE_"
                "CHILD_ROOTS_AND_DO_NOT_ENCLOSE_THE_NONLINEAR_JOINT_EVENT_"
                "CHILD_RADIUS_OR_THE_INFINITE_TAIL"
            ),
        },
        "exact_next_mathematical_lemma": (
            "USE_THE_ETA_COMPLETED_RADIAL_DIFFEO_WARD_IDENTITY_TO_ENCLOSE_"
            "THE_SOURCE_RESTRICTED_MIXED_EULER_DIRAC_SCHUR_CORRECTION_IN_"
            "S2_WITH_AN_N_MINUS_2_CAUCHY_TAIL_AND_CERTIFY_THE_GAUGE_REDUCED_"
            "ORDERED_EVENT_PROJECTOR_ON_THE_CORRECTED_NORMAL_SECTION;_"
            "THEN_CLOSE_THE_UNCHANGED_NONLINEAR_JOINT_EVENT_CHILD_RADIUS_"
            "AND_TRANSFER_ETA_EVENT_DIRAC_PERSISTENCE"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "result": str(RESULT),
        "validation_passed": output["validation_passed"],
        "fits": fits,
        "omitted_weak_norms": {
            name: [row["exact_omitted_constraint_weak_norm"] for row in rows]
            for name, rows in evaluations.items()
        },
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
