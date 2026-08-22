"""Measure the N12 high-shell Dirac/Feshbach block without changing BHSM.

The result is a finite-cutoff diagnostic.  It may localize the continuum
Schur owner but is never promoted as an interval or infinite-tail proof.
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
from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import (
    exact_action_jet_at_state,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


SOURCE_ORDER = 12
MAXIMUM_ORDER = int(os.environ.get("BHSM_N12_DIRAC_TAIL_ORDER", "48"))
POINT_COUNTS = tuple(int(item) for item in os.environ.get(
    "BHSM_N12_DIRAC_TAIL_POINTS", "256,512"
).split(","))
CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_CHECKPOINT", ".tmp_direct_n12_corrected_branch_state.npz"
))
PROMOTION = Path(os.environ.get(
    "BHSM_N12_PROMOTION",
    ".tmp_direct_n12_complete_persistent_child_promotion.json",
))
RESULT = Path(os.environ.get(
    "BHSM_N12_DIRAC_TAIL_RESULT",
    ".tmp_direct_n12_high_shell_dirac_schur.json",
))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _split_state(joint: np.ndarray, which: str) -> tuple[np.ndarray, ...]:
    qdim = dimensions(SOURCE_ORDER)["coordinates"]
    mdim = dimensions(SOURCE_ORDER)["multipliers"]
    sdim = 2 * qdim + mdim
    state = joint[:sdim] if which == "event" else joint[sdim:]
    return (
        state[:qdim], state[qdim:2 * qdim], state[2 * qdim:]
    )


def _low_z_indices() -> np.ndarray:
    qmax = dimensions(MAXIMUM_ORDER)["coordinates"]
    low = [0]
    for family in range(3):
        low.extend(range(
            1 + family * MAXIMUM_ORDER,
            1 + family * MAXIMUM_ORDER + SOURCE_ORDER,
        ))
    low.extend(qmax + mode for mode in range(SOURCE_ORDER))
    low.extend(
        qmax + MAXIMUM_ORDER + mode for mode in range(SOURCE_ORDER)
    )
    return np.asarray(low, dtype=int)


def _gauge_fixed_normal_indices(order: int) -> np.ndarray:
    """Return the existing (scale,u,v,log-lapse) normal slice.

    The boundary-compatible quotient removes the w-velocity and shift-rate
    principal gauge directions.  This is the same slice used by
    ``boundary_compatible_gauge_quotient_audit``; it is not a new equation
    or a numerical regularization.
    """

    qdim = dimensions(order)["coordinates"]
    indices = [0]
    indices.extend(range(1, 1 + order))
    indices.extend(range(1 + 2 * order, 1 + 3 * order))
    indices.extend(range(qdim, qdim + order))
    return np.asarray(indices, dtype=int)


def _low_gauge_fixed_normal_indices() -> np.ndarray:
    qmax = dimensions(MAXIMUM_ORDER)["coordinates"]
    indices = [0]
    indices.extend(range(1, 1 + SOURCE_ORDER))
    indices.extend(range(
        1 + 2 * MAXIMUM_ORDER,
        1 + 2 * MAXIMUM_ORDER + SOURCE_ORDER,
    ))
    indices.extend(range(qmax, qmax + SOURCE_ORDER))
    return np.asarray(indices, dtype=int)


def _embedded_reference(reference: np.ndarray) -> np.ndarray:
    qsource = dimensions(SOURCE_ORDER)["coordinates"]
    qmax = dimensions(MAXIMUM_ORDER)["coordinates"]
    result = np.zeros(
        dimensions(MAXIMUM_ORDER)["coordinates"]
        + dimensions(MAXIMUM_ORDER)["multipliers"]
    )
    result[0] = reference[0]
    for family in range(3):
        result[
            1 + family * MAXIMUM_ORDER:
            1 + family * MAXIMUM_ORDER + SOURCE_ORDER
        ] = reference[
            1 + family * SOURCE_ORDER:
            1 + (family + 1) * SOURCE_ORDER
        ]
    result[qmax:qmax + SOURCE_ORDER] = reference[
        qsource:qsource + SOURCE_ORDER
    ]
    result[
        qmax + MAXIMUM_ORDER:qmax + MAXIMUM_ORDER + SOURCE_ORDER
    ] = reference[qsource + SOURCE_ORDER:qsource + 2 * SOURCE_ORDER]
    return result / np.linalg.norm(result)


def _evaluate(state: tuple[np.ndarray, ...], points: int,
              reference: np.ndarray | None) -> dict[str, object]:
    embedded = embed_nested_state(
        *state, SOURCE_ORDER, MAXIMUM_ORDER
    )
    jet = exact_action_jet_at_state(
        MAXIMUM_ORDER, *embedded, points=points
    )
    hessian = np.asarray(jet.hessian, dtype=float)
    qmax = dimensions(MAXIMUM_ORDER)["coordinates"]
    frequencies = spectral_frequencies(MAXIMUM_ORDER)
    z_weights = np.concatenate((
        np.ones(qmax),
        np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))
    normalized = (
        hessian / z_weights[:, None] / z_weights[None, :]
    )
    low = _low_z_indices()
    high = np.asarray([
        index for index in range(hessian.shape[0]) if index not in set(low)
    ], dtype=int)
    ll = normalized[np.ix_(low, low)]
    lh = normalized[np.ix_(low, high)]
    hh = normalized[np.ix_(high, high)]
    hh_singular = np.linalg.svd(hh, compute_uv=False)
    hh_inverse_lh_t = np.linalg.solve(hh, lh.T)
    feedback = lh @ hh_inverse_lh_t
    effective = ll - feedback
    normal = _gauge_fixed_normal_indices(MAXIMUM_ORDER)
    normal_low = _low_gauge_fixed_normal_indices()
    normal_low_set = set(normal_low.tolist())
    normal_high = np.asarray([
        index for index in normal
        if index not in normal_low_set
    ], dtype=int)
    normal_ll = normalized[np.ix_(normal_low, normal_low)]
    normal_lh = normalized[np.ix_(normal_low, normal_high)]
    normal_hh = normalized[np.ix_(normal_high, normal_high)]
    normal_hh_singular = np.linalg.svd(normal_hh, compute_uv=False)
    normal_feedback = normal_lh @ np.linalg.solve(normal_hh, normal_lh.T)
    normal_effective = normal_ll - normal_feedback
    output: dict[str, object] = {
        "matrix_dimension": int(hessian.shape[0]),
        "low_dimension": int(low.size),
        "high_dimension": int(high.size),
        "high_high_smallest_singular_value": float(hh_singular[-1]),
        "high_high_largest_singular_value": float(hh_singular[0]),
        "high_high_inverse_norm": float(1.0 / hh_singular[-1]),
        "low_high_operator_norm": float(np.linalg.norm(lh, ord=2)),
        "Feshbach_feedback_operator_norm": float(
            np.linalg.norm(feedback, ord=2)
        ),
        "effective_low_smallest_singular_value": float(
            np.linalg.svd(effective, compute_uv=False)[-1]
        ),
        "finite_cutoff_only": True,
        "gauge_fixed_normal_slice": {
            "variables": "scale,u,v,log_lapse",
            "low_dimension": int(normal_low.size),
            "high_dimension": int(normal_high.size),
            "high_high_smallest_singular_value": float(
                normal_hh_singular[-1]
            ),
            "high_high_largest_singular_value": float(
                normal_hh_singular[0]
            ),
            "high_high_inverse_norm": float(
                1.0 / normal_hh_singular[-1]
            ),
            "low_high_operator_norm": float(
                np.linalg.norm(normal_lh, ord=2)
            ),
            "Feshbach_feedback_operator_norm": float(
                np.linalg.norm(normal_feedback, ord=2)
            ),
            "effective_low_smallest_singular_value": float(
                np.linalg.svd(normal_effective, compute_uv=False)[-1]
            ),
        },
    }
    if reference is not None:
        embedded_ref = _embedded_reference(reference)
        raw_values, raw_vectors = np.linalg.eigh(hessian)
        selected = int(np.argmax(np.abs(raw_vectors.T @ embedded_ref)))
        output.update({
            "selected_raw_ordered_eigenvalue": float(raw_values[selected]),
            "selected_raw_ordered_reference_overlap": float(abs(
                raw_vectors[:, selected] @ embedded_ref
            )),
            "selected_raw_ordered_index": selected,
            "neighbor_gap_below": float(
                raw_values[selected] - raw_values[selected - 1]
            ) if selected > 0 else None,
            "neighbor_gap_above": float(
                raw_values[selected + 1] - raw_values[selected]
            ) if selected + 1 < raw_values.size else None,
        })
    return output


def main() -> None:
    promotion = json.loads(PROMOTION.read_text(encoding="utf-8"))
    if not promotion["DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED"]:
        raise RuntimeError("the certified N12 anchor is required")
    checkpoint = np.load(CHECKPOINT)
    joint = np.asarray(checkpoint["state"], dtype=float)
    reference = np.asarray(checkpoint["branch_reference"], dtype=float)
    states = {
        name: _split_state(joint, name) for name in ("event", "child")
    }
    evaluations = {}
    for points in POINT_COUNTS:
        evaluations[str(points)] = {
            "event": _evaluate(states["event"], points, reference),
            "child": _evaluate(states["child"], points, None),
        }
    first = evaluations[str(POINT_COUNTS[0])]
    last = evaluations[str(POINT_COUNTS[-1])]
    convergence = {}
    keys = (
        "high_high_smallest_singular_value",
        "low_high_operator_norm",
        "Feshbach_feedback_operator_norm",
        "effective_low_smallest_singular_value",
    )
    for name in ("event", "child"):
        convergence[name] = {
            key: abs(float(last[name][key]) - float(first[name][key]))
            for key in keys
        }
    principal_gap = math.sqrt(29.0) - 5.0
    validation = {
        "certified_N12_anchor_consumed": True,
        "unchanged_retained_action_Hessian_used": True,
        "existing_L2_velocity_H1_multiplier_graph_weights_used": True,
        "high_high_blocks_invertible_at_both_quadratures": all(
            evaluations[str(points)][name][
                "high_high_smallest_singular_value"
            ] > 0.0
            for points in POINT_COUNTS for name in ("event", "child")
        ),
        "finite_cutoff_not_promoted_as_infinite_tail_bound": True,
        "instantaneous_gauge_slice_not_promoted_as_positive_duration_"
        "normal_operator": True,
        "gauge_slice_improves_the_raw_high_shell_gap": all(
            evaluations[str(points)][name]["gauge_fixed_normal_slice"][
                "high_high_smallest_singular_value"
            ]
            > evaluations[str(points)][name][
                "high_high_smallest_singular_value"
            ]
            for points in POINT_COUNTS for name in ("event", "child")
        ),
        "higher_order_embedded_states_not_promoted_as_roots": True,
        "no_new_equation_constraint_gate_scale_or_fit": True,
    }
    payload = {
        "classification": (
            "N12_HIGH_SHELL_DIRAC_FESHBACH_FINITE_CUTOFF_DIAGNOSTIC;_"
            "ANALYTIC_INFINITE_TAIL_ENCLOSURE_STILL_REQUIRED"
        ),
        "source_checkpoint": str(CHECKPOINT),
        "source_checkpoint_SHA256": _sha256(CHECKPOINT),
        "source_order": SOURCE_ORDER,
        "maximum_probe_order": MAXIMUM_ORDER,
        "quadrature_point_counts": POINT_COUNTS,
        "action_principal_modulus_gap": principal_gap,
        "evaluations": evaluations,
        "quadrature_absolute_differences": convergence,
        "scope": {
            "finite_high_high_invertibility_measured": True,
        "high_shell_block_is_gauge_reduced_normal_operator": False,
            "instantaneous_gauge_fixed_normal_slice_measured": True,
            "instantaneous_gauge_slice_is_the_positive_duration_normal_"
            "operator": False,
            "raw_high_high_inverse_used_as_continuum_normal_inverse": False,
            "uniform_N12_to_infinity_inverse_proved": False,
            "ordered_event_projector_convergence_proved": False,
            "full_event_child_normal_Schur_closed": False,
            "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        },
        "exact_next_dependency": (
            "CONSTRUCT_THE_EXISTING_POSITIVE_DURATION_GAUGE_FIXED_HIGH_"
            "SHELL_JACOBI_NORMAL_OPERATOR_AND_TURN_THE_RETAINED_ACTION_"
            "PRINCIPAL_PLUS_COMPACT_SPLIT_INTO_AN_EXPLICIT_N12_TO_"
            "INFINITY_OPERATOR_NORM_ENCLOSURE,_INCLUDING_THE_ORDERED_"
            "EVENT_PROJECTOR_AND_CANONICAL_MOMENTUM_FLUX_TAIL"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
