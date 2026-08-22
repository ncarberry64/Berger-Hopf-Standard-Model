"""Certify the existing N12 Calderon graph gap on its action ball.

This is a finite-core lemma for the unchanged source-restricted continuum
program.  It encloses the existing boundary-compatible (w, shift) gauge
quotient on the already-certified N12 action-coordinate ball.  It does not
turn a sampled history into an interval proof and does not promote a
continuum child.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np

from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _attachment_jacobian_at_order,
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
ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
)
PROMOTION = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_CERTIFICATE.json"
)
THIRD = ROOT / (
    "artifacts/n12_direct_checkpoint/BHSM_N12_THIRD_VARIATIONS.npz"
)
MAJORANTS = ROOT / (
    "artifacts/n12_direct_checkpoint/BHSM_N12_ACTION_MAJORANTS.json"
)
STATIC_SYMBOL = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_EVENT_CHILD_CALDERON_N12_TO_N32_P96.json"
)
DIRECTED_CENTER = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_CALDERON_DIRECTED_CENTER.json"
)
ROOT_ROUNDING = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_DIRECTED_ROUNDING_CERTIFICATE.json"
)
RESULT = Path(os.environ.get(
    "BHSM_N12_CALDERON_ACTION_BALL_RESULT",
    str(ROOT / (
        "artifacts/n12_direct_checkpoint/"
        "BHSM_N12_CALDERON_ACTION_BALL.json"
    )),
))


def _up(value: float) -> float:
    return math.nextafter(float(value) * INFLATION, math.inf)


def _down(value: float) -> float:
    return math.nextafter(float(value) / INFLATION, -math.inf)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _symmetric_power(matrix: np.ndarray, power: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(matrix)
    if float(np.min(values)) <= 0.0:
        raise np.linalg.LinAlgError("positive trace Gram required")
    return vectors @ np.diag(values ** power) @ vectors.T


def _split(joint: np.ndarray, side: int) -> np.ndarray:
    size = dimensions(ORDER)
    state_dimension = 2 * size["coordinates"] + size["multipliers"]
    return joint[side * state_dimension:(side + 1) * state_dimension]


def _center_data(
    state: np.ndarray,
    state_weights: np.ndarray,
    q_weights: np.ndarray,
    m_weights: np.ndarray,
    common_sqrt: np.ndarray,
) -> dict[str, np.ndarray | float]:
    qdim = dimensions(ORDER)["coordinates"]
    q = state[:qdim]
    velocity = state[qdim:2 * qdim]
    multipliers = state[2 * qdim:]
    hessian = np.asarray(exact_full_action_jet_at_state(
        ORDER, q, velocity, multipliers, points=POINTS
    ).hessian, dtype=float)
    normalized_hessian = (
        hessian / state_weights[:, None] / state_weights[None, :]
    )
    velocity_keep = np.concatenate((
        np.arange(0, 1 + ORDER),
        np.arange(1 + 2 * ORDER, 1 + 3 * ORDER),
    ))
    state_keep = np.concatenate((
        qdim + velocity_keep,
        2 * qdim + np.arange(ORDER),
    ))
    attachment = _attachment_jacobian_at_order(ORDER, q)
    inverse_sqrt = np.linalg.inv(common_sqrt)
    coupling = np.hstack((
        inverse_sqrt @ attachment[:, velocity_keep],
        np.zeros((2, ORDER)),
    ))
    core = normalized_hessian[np.ix_(state_keep, state_keep)]
    matrix = np.block([
        [core, -coupling.T],
        [coupling, np.zeros((2, 2))],
    ])
    inverse = np.linalg.inv(matrix)
    inverse_residual = _up(float(np.linalg.norm(
        np.eye(matrix.shape[0]) - inverse @ matrix, ord=2
    )))
    if inverse_residual >= 1.0:
        raise np.linalg.LinAlgError("center quotient inverse is unresolved")
    inverse_bound = _up(
        float(np.linalg.norm(inverse, ord=2)) / (1.0 - inverse_residual)
    )
    response = inverse[-2:, -2:]
    return {
        "matrix": matrix,
        "inverse": inverse,
        "inverse_residual": inverse_residual,
        "inverse_bound": inverse_bound,
        "response": response,
        "response_norm": float(np.linalg.norm(response, ord=2)),
        "attachment": attachment,
        "attachment_scaled": attachment / q_weights[None, :],
        "state_keep": state_keep,
        "velocity_keep": velocity_keep,
        "common_inverse_sqrt": inverse_sqrt,
        "center_smallest_singular": float(
            np.linalg.svd(matrix, compute_uv=False)[-1]
        ),
    }


def main() -> None:
    promotion = json.loads(PROMOTION.read_text(encoding="utf-8"))
    if promotion.get("DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED") is not True:
        raise RuntimeError("certified N12 anchor required")
    majorants = json.loads(MAJORANTS.read_text(encoding="utf-8"))
    if majorants.get("validation_passed") is not True:
        raise RuntimeError("validated action majorants required")
    certified_root_radius = float(majorants["action_coordinate_ball_radius"])
    sectors = {record["sector"]: record for record in majorants["sectors"]}
    third_payload = np.load(THIRD)
    checkpoint = np.load(CHECKPOINT)
    joint = np.asarray(checkpoint["state"], dtype=float)
    size = dimensions(ORDER)
    qdim = size["coordinates"]
    frequencies = spectral_frequencies(ORDER)
    q_weights = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
    m_weights = np.sqrt(1.0 + frequencies["multipliers"] ** 2)
    state_weights = np.concatenate((q_weights, np.ones(qdim), m_weights))
    if not np.array_equal(state_weights, third_payload["state_weights"]):
        raise ValueError("third variation uses different action coordinates")
    states = {name: _split(joint, index) for index, name in enumerate((
        "event", "child"
    ))}
    attachments = {
        name: _attachment_jacobian_at_order(ORDER, state[:qdim])
        for name, state in states.items()
    }
    inverse_q_metric = np.diag(1.0 / q_weights ** 2)
    grams = {
        name: attachment @ inverse_q_metric @ attachment.T
        for name, attachment in attachments.items()
    }
    common_gram = 0.5 * (grams["event"] + grams["child"])
    common_sqrt = _symmetric_power(common_gram, 0.5)
    common_inverse_sqrt = _symmetric_power(common_gram, -0.5)
    center = {
        name: _center_data(
            state, state_weights, q_weights, m_weights, common_sqrt
        )
        for name, state in states.items()
    }

    static = json.loads(STATIC_SYMBOL.read_text(encoding="utf-8"))
    static_row = static["rows"][0]
    expected = {
        "event": np.asarray(
            static_row["event_action_normalized_response"], dtype=float
        ),
        "child": np.asarray(
            static_row["child_action_normalized_response"], dtype=float
        ),
    }
    response_cross_errors = {
        name: float(np.linalg.norm(center[name]["response"] - expected[name]))
        for name in center
    }

    directed = json.loads(DIRECTED_CENTER.read_text(encoding="utf-8"))
    directed_exact_root_symbol_closed = bool(
        directed.get("validation_passed") is True
    )
    directed_sectors = directed["sector_records"]
    directed_gram = directed["common_trace_Gram"]
    directed_gap = float(
        directed["symbol"]["minimum_singular_value_lower"]
    )
    root_rounding = json.loads(ROOT_ROUNDING.read_text(encoding="utf-8"))
    if root_rounding.get("validation_passed") is not True:
        raise RuntimeError("directed N12 root-rounding certificate required")
    root_Y = float(root_rounding["directed_Y_upper"])
    root_contraction = float(root_rounding["directed_contraction_bound"])
    if not 0.0 <= root_contraction < 1.0:
        raise RuntimeError("contractive N12 root enclosure required")
    exact_root_distance_upper = _up(root_Y / (1.0 - root_contraction))

    center_gram_minimum_binary = float(np.linalg.eigvalsh(common_gram)[0])
    center_gram_minimum = float(
        directed_gram["minimum_eigenvalue_lower"]
    )
    common_inverse_sqrt_bound = float(
        directed_gram["inverse_sqrt_Frobenius_bound"]
    )
    center_gap_binary = float(
        static_row["minimum_graph_symbol_singular_value"]
    )
    center_gap = directed_gap
    center_cosine = _up(1.0 - center_gap ** 2)
    shape_slice = slice(1 + 2 * ORDER, 1 + 3 * ORDER)
    shape_covector_norm = float(np.linalg.norm(
        ((-1.0) ** np.arange(ORDER)) / q_weights[shape_slice]
    ))
    raw_shape_sign_norm = math.sqrt(float(ORDER))
    sector_constants = {}
    for name in ("event", "child"):
        state_keep = np.asarray(center[name]["state_keep"], dtype=int)
        third = np.asarray(third_payload[name], dtype=float)
        restricted_third = third[np.ix_(
            state_keep, state_keep, np.arange(state_weights.size)
        )]
        sector_constants[name] = {
            "hessian_first": _up(float(np.linalg.norm(restricted_third))),
            "fourth": float(
                sectors[name]["derivative_operator_majorants_0_through_5"][4]
            ),
        }

    def enclose(candidate_radius: float) -> dict[str, object]:
        delta_scalar = _up(
            2.0 * shape_covector_norm * candidate_radius
            + 4.0 * shape_covector_norm ** 2 * candidate_radius ** 2
        )
        delta_attachment_keep = _up(
            math.sqrt(2.0) * raw_shape_sign_norm * delta_scalar
        )
        delta_attachment_scaled = _up(
            math.sqrt(2.0) * shape_covector_norm * delta_scalar
        )
        records: dict[str, dict[str, float | bool]] = {}
        for name in ("event", "child"):
            data = center[name]
            hessian_first = float(sector_constants[name]["hessian_first"])
            fourth = float(sector_constants[name]["fourth"])
            delta_hessian = _up(
                hessian_first * candidate_radius
                + 0.5 * fourth * candidate_radius ** 2
            )
            delta_coupling = _up(
                common_inverse_sqrt_bound * delta_attachment_keep
            )
            delta_matrix = _up(delta_hessian + delta_coupling)
            inverse_bound = float(
                directed_sectors[name]["interval_inverse_Frobenius_bound"]
            )
            relative = _up(inverse_bound * delta_matrix)
            inverse_closed = relative < 1.0
            delta_response_fixed_gram = (
                _up(inverse_bound * relative / (1.0 - relative))
                if inverse_closed else math.inf
            )
            records[name] = {
                "center_quotient_smallest_singular_value": float(
                    data["center_smallest_singular"]
                ),
                "center_quotient_inverse_bound": inverse_bound,
                "center_inverse_residual_bound": float(
                    directed_sectors[name][
                        "interval_inverse_defect_upper"
                    ]
                ),
                "restricted_action_third_variation_bound": hessian_first,
                "full_action_fourth_variation_bound": fourth,
                "Hessian_ball_perturbation_bound": delta_hessian,
                "attachment_ball_perturbation_bound": delta_attachment_keep,
                "fixed_Gram_quotient_matrix_perturbation_bound": delta_matrix,
                "fixed_Gram_relative_perturbation_bound": relative,
                "fixed_Gram_inverse_closed": inverse_closed,
                "fixed_Gram_response_perturbation_bound": (
                    delta_response_fixed_gram
                ),
            }
        gram_perturbations = {}
        for name in ("event", "child"):
            xnorm = float(np.linalg.norm(
                center[name]["attachment_scaled"], ord=2
            ))
            gram_perturbations[name] = _up(
                2.0 * xnorm * delta_attachment_scaled
                + delta_attachment_scaled ** 2
            )
        delta_common_gram = _up(0.5 * (
            gram_perturbations["event"] + gram_perturbations["child"]
        ))
        gram_minimum_lower = _down(
            center_gram_minimum - delta_common_gram
        )
        gram_closed = gram_minimum_lower > 0.0
        delta_sqrt = (
            _up(
                delta_common_gram / (
                    math.sqrt(center_gram_minimum)
                    + math.sqrt(gram_minimum_lower)
                )
            ) if gram_closed else math.inf
        )
        delta_relative_sqrt = _up(
            delta_sqrt * common_inverse_sqrt_bound
        )
        response_perturbations = {}
        for name in ("event", "child"):
            fixed = float(
                records[name]["fixed_Gram_response_perturbation_bound"]
            )
            center_norm = float(
                directed_sectors[name]["response_Frobenius_bound"]
            )
            response_perturbations[name] = _up(
                (1.0 + delta_relative_sqrt) ** 2 * fixed
                + (2.0 * delta_relative_sqrt + delta_relative_sqrt ** 2)
                * center_norm
            )
            records[name]["action_normalized_response_perturbation_bound"] = (
                response_perturbations[name]
            )
            records[name]["graph_projector_perturbation_bound"] = (
                response_perturbations[name]
            )
        projector_sum = _up(
            response_perturbations["event"]
            + response_perturbations["child"]
        )
        cosine_upper = _up(center_cosine + projector_sum)
        ball_gap = (
            _down(math.sqrt(max(0.0, 1.0 - cosine_upper)))
            if cosine_upper < 1.0 else 0.0
        )
        return {
            "radius": candidate_radius,
            "delta_scalar": delta_scalar,
            "delta_attachment_scaled": delta_attachment_scaled,
            "delta_common_gram": delta_common_gram,
            "gram_minimum_lower": gram_minimum_lower,
            "gram_closed": gram_closed,
            "delta_relative_sqrt": delta_relative_sqrt,
            "records": records,
            "projector_sum": projector_sum,
            "cosine_upper": cosine_upper,
            "ball_gap": ball_gap,
        }

    subdivision = 0
    enclosure = enclose(certified_root_radius)
    while float(enclosure["ball_gap"]) <= 0.0 and subdivision < 100:
        subdivision += 1
        enclosure = enclose(certified_root_radius / 2.0 ** subdivision)
    radius = float(enclosure["radius"])
    records = enclosure["records"]
    delta_scalar = float(enclosure["delta_scalar"])
    delta_attachment_scaled = float(enclosure["delta_attachment_scaled"])
    delta_common_gram = float(enclosure["delta_common_gram"])
    gram_minimum_lower = float(enclosure["gram_minimum_lower"])
    gram_closed = bool(enclosure["gram_closed"])
    delta_relative_sqrt = float(enclosure["delta_relative_sqrt"])
    projector_sum = float(enclosure["projector_sum"])
    cosine_upper = float(enclosure["cosine_upper"])
    ball_gap = float(enclosure["ball_gap"])
    exact_root_contained = radius >= exact_root_distance_upper
    validation = {
        "certified_direct_N12_pair_consumed": True,
        "same_action_coordinates_as_third_variation": True,
        "unchanged_retained_action_Hessian_used": True,
        "directed_exact_root_box_symbol_closed": (
            directed_exact_root_symbol_closed
        ),
        "existing_boundary_compatible_w_shift_quotient_used": True,
        # The old binary bordered solves are deliberately retained only as a
        # diagnostic.  Their 1e6-scale inverse amplifies double rounding, so
        # the directed interval replay above, not numerical agreement with
        # those legacy responses, is the center authority.
        "binary_static_response_cross_check_is_diagnostic_only": True,
        "both_fixed_Gram_quotient_inverses_closed_on_ball": all(
            bool(records[name]["fixed_Gram_inverse_closed"])
            for name in records
        ),
        "common_trace_Gram_positive_on_ball": gram_closed,
        "Calderon_graph_symbol_gap_positive_on_whole_ball": ball_gap > 0.0,
        "whole_ball_provably_contains_the_exact_N12_root": (
            exact_root_contained
        ),
        "sampled_history_not_promoted_as_interval_proof": True,
        "no_new_equation_constraint_gate_scale_fit_or_event_definition": True,
    }
    output = {
        "classification": (
            "N12_EXACT_ROOT_CALDERON_GRAPH_GAP_CERTIFIED_ON_A_WHOLE_"
            "ACTION_COORDINATE_BALL"
            if all(validation.values()) else
            "N12_ISOTROPIC_ACTION_BALL_EXACT_ROOT_CALDERON_"
            "CERTIFICATE_NOT_YET_CLOSED"
        ),
        "order": ORDER,
        "points": POINTS,
        "certified_N12_root_ball_radius": certified_root_radius,
        "action_coordinate_ball_radius_per_sector": radius,
        "dyadic_subdivisions_from_certified_root_ball": subdivision,
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in (
                CHECKPOINT, PROMOTION, THIRD, MAJORANTS, STATIC_SYMBOL,
                DIRECTED_CENTER, ROOT_ROUNDING,
            )
        },
        "exact_root_enclosure": {
            "directed_Y_upper": root_Y,
            "directed_contraction_bound": root_contraction,
            "distance_from_numerical_center_upper": (
                exact_root_distance_upper
            ),
            "contained_in_reported_transverse_ball": exact_root_contained,
        },
        "center": {
            "common_trace_Gram_minimum_eigenvalue_binary": (
                center_gram_minimum_binary
            ),
            "common_trace_Gram_minimum_eigenvalue_directed_lower": (
                center_gram_minimum
            ),
            "four_by_four_symbol_gap_binary": center_gap_binary,
            "four_by_four_symbol_gap_directed_lower": center_gap,
            "largest_principal_cosine_directed_upper": center_cosine,
            "response_cross_check_errors": response_cross_errors,
        },
        "ball_bounds": {
            "attachment_scalar_variation_bound": delta_scalar,
            "attachment_scaled_operator_variation_bound": (
                delta_attachment_scaled
            ),
            "common_trace_Gram_perturbation_bound": delta_common_gram,
            "common_trace_Gram_minimum_eigenvalue_lower": gram_minimum_lower,
            "common_sqrt_relative_perturbation_bound": delta_relative_sqrt,
            "sector_records": records,
            "sum_of_graph_projector_perturbation_bounds": projector_sum,
            "largest_principal_cosine_upper": cosine_upper,
            "seven_by_seven_symbol_gap_lower": ball_gap,
        },
        "scope": (
            "CENTERED_FINITE_N12_GRAPH_TRANSVERSALITY_ENCLOSURE;_IT_"
            "COUNTS_AS_AN_EXACT_ROOT_LEMMA_ONLY_IF_THE_DIRECTED_ROOT_"
            "ENCLOSURE_IS_CONTAINED"
        ),
        "exact_next_dependency": (
            directed.get("exact_next_dependency")
            if not directed_exact_root_symbol_closed else
            "DERIVE_THE_POSITIVE_DURATION_c_M0_ON_THE_CERTIFIED_"
            "EXACT_ROOT_GRAPH_NEIGHBORHOOD"
        ),
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    with RESULT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
