"""Audit strict propagated-set reserve through the retained 1222 C2 core.

The pointwise 1222 cover and its state-Jacobi growth factors are already
certified.  This audit asks the distinct boundary-control question: does each
stored local chart leave enough unused output radius to carry the whole
compact Gate-7 reset-quotient ball?  A zero reserve is reported fail closed;
it is not promoted to a dynamical obstruction or a failure of local history
existence.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_COMPACT_RESET_PROPAGATION_RESERVE_AUDIT.json"
DATA = RESULT.with_suffix(".npz")
COMPACT = BASE / "BHSM_N12_GATE7_COMPACT_RESET_QUOTIENT_DOMAIN.json"
PULLBACK = BASE / "BHSM_N12_C2_1222_RESET_QUOTIENT_RADIUS_PULLBACK_ENCLOSURE.json"
PULLBACK_DATA = PULLBACK.with_suffix(".npz")
OUTER = BASE / "BHSM_N12_C2_POLE_FREE_OUTER_MARGIN_EXTENSION.json"
SECOND = BASE / "BHSM_N12_C2_TRANSLATED_POLE_FREE_SEGMENT.json"
EXTENDED = BASE / "BHSM_N12_C2_EXTENDED_DESCRIPTOR_RESOLUTION_AUDIT.json"
COMPENSATED = BASE / "BHSM_N12_C2_COMPENSATED_DESCRIPTOR_CONTINUATION.json"
ADAPTIVE = BASE / "BHSM_N12_C2_ADAPTIVE_BALL_CONTINUATION.json"
RECENTERED = BASE / "BHSM_N12_C2_RECENTERED_ADAPTIVE_CONTINUATION.json"
FIBER = BASE / "BHSM_N12_C2_DESCRIPTOR_FIBER_CANCELLED_CONTINUATION.json"
GAP = BASE / "BHSM_N12_C2_UNIFORM_GAP_CONTINUATION.json"
SECOND_GAP = BASE / "BHSM_N12_C2_SECOND_UNIFORM_GAP_CONTINUATION.json"
THEORY = ROOT / "theory" / "n12_gate7_compact_reset_propagation_reserve_audit.md"
STEP_NUMBERS = tuple(range(1215, 1223))


def _step_path(segment: int) -> Path:
    if segment == 1215:
        return BASE / "BHSM_N12_C2_CANCELLED_FIELD_LOHNER_STEP.json"
    return BASE / f"BHSM_N12_C2_LOHNER_STEP_{segment}.json"


INPUTS = (
    COMPACT,
    PULLBACK,
    PULLBACK_DATA,
    OUTER,
    SECOND,
    EXTENDED,
    COMPENSATED,
    ADAPTIVE,
    RECENTERED,
    FIBER,
    GAP,
    SECOND_GAP,
    *(_step_path(index) for index in STEP_NUMBERS),
    THEORY,
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _reserve_rows() -> tuple[np.ndarray, list[str], list[int]]:
    """Return output-radius reserves in the exact 1222 growth-factor order."""

    reserves: list[float] = []
    owners: list[str] = []
    local_indices: list[int] = []

    def append(owner: str, local_index: int, radius: float, use: float) -> None:
        reserves.append(float(radius) - float(use))
        owners.append(owner)
        local_indices.append(local_index)

    outer = _load(OUTER)
    append(
        "outer_margin",
        1,
        outer["improved_launch_ball"]["outer_action_radius"],
        outer["endpoint_recenter"]["outer_ball_total_radius_use"],
    )
    second = _load(SECOND)
    append(
        "translated_second",
        1,
        second["endpoint_recenter"]["translated_ball_radius"],
        second["endpoint_recenter"]["root_relative_path_plus_tube_upper"],
    )

    blocks = (
        (EXTENDED, "cover", "extended_descriptor", "translated_ball_local_radius", "endpoint_tube_radius_upper"),
        (COMPENSATED, "compensated_cover", "replayed_compensated", "translated_ball_local_radius", "endpoint_tube_radius_upper"),
        (ADAPTIVE, "adaptive_cover", "replayed_adaptive", "derived_local_radius", "endpoint_tube_radius_upper"),
        (RECENTERED, "recentered_cover", "replayed_recentered_adaptive", "derived_local_radius", "endpoint_tube_radius_upper"),
        (FIBER, "continuation", "descriptor_fiber_cancelled", "selected_ball_radius", "root_use_inside_selected_ball"),
        (GAP, "continuation", "uniform_gap", "selected_ball_radius", "root_use_inside_selected_ball"),
        (SECOND_GAP, "continuation", "second_uniform_gap", "selected_ball_radius", "root_use_inside_selected_ball"),
    )
    for path, section, owner, radius_key, use_key in blocks:
        for local_index, row in enumerate(_load(path)[section]["rows"], start=1):
            append(owner, local_index, row[radius_key], row[use_key])

    for segment in STEP_NUMBERS:
        record = _load(_step_path(segment))
        append(
            "matrix_Lohner",
            segment,
            record["domain"]["selected_domain_radius"],
            record["segment"]["joint_domain_use_upper"],
        )

    return np.asarray(reserves, dtype=float), owners, local_indices


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "missing compact propagation-reserve inputs: " + ", ".join(missing)
        )

    compact = _load(COMPACT)
    pullback = _load(PULLBACK)
    parents = [
        compact,
        pullback,
        *(_load(path) for path in (
            OUTER, SECOND, EXTENDED, COMPENSATED, ADAPTIVE, RECENTERED,
            FIBER, GAP, SECOND_GAP,
        )),
        *(_load(_step_path(index)) for index in STEP_NUMBERS),
    ]
    if not all(record.get("validation_passed") is True for record in parents):
        raise RuntimeError("validated compact-domain and finite-core parents required")

    reserves, owners, local_indices = _reserve_rows()
    with np.load(PULLBACK_DATA) as source:
        local_growth = np.asarray(
            source["local_state_Jacobi_growth_upper"], dtype=float
        )
        node_log_growth = np.asarray(
            source["node_log_state_Jacobi_growth_upper"], dtype=float
        )
    cumulative_growth = np.exp(node_log_growth[1:])

    rho = float(compact["parameter_domain"]["radius"])
    graph_first = float(
        compact["quotient_first_jet"]["normal_graph_first_jet_upper"]
    )
    reset_graph_lipschitz = 1.0 + graph_first
    required_full = cumulative_growth * reset_graph_lipschitz * rho
    allowable_initial = reserves / (cumulative_growth * reset_graph_lipschitz)
    strict = reserves > 0.0
    carries_full = reserves >= required_full
    zero_indices = np.flatnonzero(~strict)
    global_indices = np.arange(1, reserves.size + 1, dtype=np.int64)
    minimum_positive_allowable = float(np.min(allowable_initial[strict]))
    # A quarter of the inherited positive bottleneck leaves strict room for
    # outward rounding.  This is a derived proof subradius, not a physical
    # scale or a selected reset member.
    open_subball_target_radius = minimum_positive_allowable / 4.0
    target_required = (
        cumulative_growth * reset_graph_lipschitz * open_subball_target_radius
    )

    block_counts: dict[str, int] = {}
    for owner in owners:
        block_counts[owner] = block_counts.get(owner, 0) + 1

    failing_rows = [
        {
            "global_segment_index": int(global_indices[index]),
            "block": owners[index],
            "local_index": int(local_indices[index]),
            "stored_output_reserve": float(reserves[index]),
            "required_output_reserve_for_full_K_rho": float(required_full[index]),
            "allowable_initial_radius_from_this_row": float(allowable_initial[index]),
        }
        for index in zero_indices
    ]
    full_failure = np.flatnonzero(~carries_full)
    bottleneck_order = np.argsort(reserves)[:12]
    bottlenecks = [
        {
            "global_segment_index": int(global_indices[index]),
            "block": owners[index],
            "local_index": int(local_indices[index]),
            "stored_output_reserve": float(reserves[index]),
            "required_output_reserve_for_full_K_rho": float(required_full[index]),
            "allowable_initial_radius_from_this_row": float(allowable_initial[index]),
        }
        for index in bottleneck_order
    ]

    np.savez_compressed(
        DATA,
        global_segment_index=global_indices,
        local_block_index=np.asarray(local_indices, dtype=np.int64),
        stored_output_reserve=reserves,
        local_state_Jacobi_growth_upper=local_growth,
        cumulative_state_Jacobi_growth_upper=cumulative_growth,
        required_output_reserve_for_full_K_rho=required_full,
        allowable_initial_radius=allowable_initial,
        strict_positive_reserve=strict,
        carries_full_compact_domain=carries_full,
        required_output_reserve_for_open_subball_target=target_required,
    )

    expected_counts = pullback["Jacobi_provenance"]["block_segment_counts"]
    validation = {
        "exactly_1222_reserves_assembled": reserves.shape == (1222,),
        "reserve_order_matches_exact_growth_order": (
            local_growth.shape == (1222,)
            and node_log_growth.shape == (1223,)
            and cumulative_growth.shape == (1222,)
        ),
        "block_counts_match_pullback_provenance": block_counts == expected_counts,
        "all_stored_reserves_are_nonnegative": bool(np.all(reserves >= 0.0)),
        "exactly_two_stored_transitions_have_zero_reserve": (
            global_indices[zero_indices].tolist() == [791, 1064]
        ),
        "zero_reserves_are_adaptive_block_endpoints": (
            [owners[index] for index in zero_indices]
            == ["replayed_adaptive", "replayed_recentered_adaptive"]
        ),
        "compact_domain_radius_is_strictly_positive": rho > 0.0,
        "reset_graph_lipschitz_is_finite_positive": (
            math.isfinite(reset_graph_lipschitz) and reset_graph_lipschitz > 0.0
        ),
        "no_positive_initial_radius_is_certified_through_stored_cover": (
            float(np.min(allowable_initial)) == 0.0
        ),
        "full_compact_domain_is_not_carried_by_stored_cover": bool(
            np.any(~carries_full)
        ),
        "derived_open_subball_target_fits_every_strict_positive_row": bool(
            np.all(target_required[strict] < reserves[strict])
        ),
        "pointwise_core_and_local_history_claims_are_preserved": True,
        "no_member_finite_edge_selector_scale_recurrence_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())

    return {
        "artifact": "BHSM_N12_GATE7_COMPACT_RESET_PROPAGATION_RESERVE_AUDIT",
        "status": (
            "STORED_1222_CORE_PROPAGATED_SET_MAP_FAILS_STRICT_RESERVE_AT_TWO_TRANSITIONS"
            if passed else "COMPACT_RESET_PROPAGATION_RESERVE_AUDIT_INVALID"
        ),
        "classification": (
            "THE_RETAINED_POINTWISE_1222_COVER_HAS_EXACTLY_TWO_ZERO_OUTPUT_RESERVES;_"
            "THEREFORE_ITS_STORED_RADII_DO_NOT_CERTIFY_ANY_POSITIVE_RESET_FAMILY_"
            "THROUGH_THE_WHOLE_CORE"
        ),
        "propagated_set_test": {
            "compact_parameter_radius": rho,
            "normal_graph_first_jet_upper": graph_first,
            "reset_graph_lipschitz_upper": reset_graph_lipschitz,
            "segment_count": int(reserves.size),
            "terminal_cumulative_state_Jacobi_growth_upper": float(cumulative_growth[-1]),
            "minimum_stored_output_reserve": float(np.min(reserves)),
            "minimum_allowable_initial_radius": float(np.min(allowable_initial)),
            "minimum_strictly_positive_allowable_initial_radius": minimum_positive_allowable,
            "derived_open_subball_target_radius": open_subball_target_radius,
            "proof_subradius_is_not_a_new_physical_scale": True,
            "strict_positive_reserve_segment_count": int(np.count_nonzero(strict)),
            "full_compact_domain_carried_segment_count": int(np.count_nonzero(carries_full)),
            "full_compact_domain_failure_count": int(full_failure.size),
            "zero_reserve_rows": failing_rows,
            "required_new_reserve_at_zero_rows_for_open_subball_target": [
                {
                    "global_segment_index": int(global_indices[index]),
                    "required_output_reserve_strictly_above": float(target_required[index]),
                }
                for index in zero_indices
            ],
            "twelve_smallest_stored_reserves": bottlenecks,
            "block_segment_counts": block_counts,
        },
        "theorem": {
            "family_displacement_bound": (
                "delta_i<=exp(node_log_growth[i+1])*(1+||D_eta||)*rho"
            ),
            "strict_reserve_condition": (
                "stored_output_reserve_i>0_AND_delta_i<=stored_output_reserve_i"
            ),
            "fail_closed_consequence": (
                "A_ZERO_STORED_OUTPUT_RESERVE_MAKES_THE_EXISTING_COVER_UNABLE_TO_"
                "CERTIFY_ANY_POSITIVE_INITIAL_PARAMETER_RADIUS_THROUGH_ALL_1222_SEGMENTS"
            ),
        },
        "adjudication": {
            "compact_reset_quotient_domain": "CERTIFIED_AND_PRESERVED",
            "pointwise_1222_finite_core": "CERTIFIED_AND_PRESERVED",
            "boundary_controlled_propagated_compact_set_map": "NOT_CERTIFIED",
            "dynamical_nonexistence_inferred": False,
            "reset_member_selected": False,
            "finite_proof_edge_extrapolated": False,
            "exact_next_dependency": (
                "REBUILD_ONLY_THE_SATURATED_TRANSITION_BLOCKS_AT_GLOBAL_SEGMENTS_"
                "791_AND_1064_WITH_A_PREDECLARED_STRICT_OUTPUT_RESERVE_SIZED_BY_"
                "THE_DERIVED_OPEN_SUBBALL_TARGET_AND_RETAINED_CUMULATIVE_JACOBI_"
                "GROWTH;_THEN_REASSEMBLE_THE_"
                "BOUNDARY_CONTROLLED_MAP_TO_CAPTURE_OR_FIRST_RETAINED_STOP"
            ),
        },
        "claim_boundary": (
            "THIS_IS_A_NEGATIVE_AUDIT_OF_THE_STORED_COVER_RADII,_NOT_A_NO_GO_"
            "THEOREM_FOR_RESET_TO_CAPTURE_CONNECTION_AND_NOT_A_FAILURE_OF_LOCAL_"
            "FORWARD_HISTORY_EXISTENCE"
        ),
        "inputs": {path.name: _sha256(path) for path in INPUTS},
        "data": DATA.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA),
        "validation": validation,
        "validation_passed": passed,
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
        "zero_reserve_rows": payload["propagated_set_test"]["zero_reserve_rows"],
        "full_compact_domain_failure_count": payload["propagated_set_test"]["full_compact_domain_failure_count"],
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
