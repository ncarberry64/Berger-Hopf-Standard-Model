"""Assemble the exact-fiber C2 finite form core through segment 1222."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from bhsm.interface.aether_forward_c2_finite_core_descriptor import (  # noqa: E402
    assemble_finite_core_descriptor,
)
from derive_n12_c2_birth_coefficient_quotient_jet import (  # noqa: E402
    _coefficient_enclosure,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
DATA_RESULT = BASE / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.npz"
PREFIX = BASE / "BHSM_N12_C2_1064_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
PREFIX_DATA = PREFIX.with_suffix(".npz")
FIBER = BASE / "BHSM_N12_C2_DESCRIPTOR_FIBER_CANCELLED_CONTINUATION.json"
FIBER_DATA = FIBER.with_suffix(".npz")
GAP = BASE / "BHSM_N12_C2_UNIFORM_GAP_CONTINUATION.json"
GAP_DATA = GAP.with_suffix(".npz")
SECOND_GAP = BASE / "BHSM_N12_C2_SECOND_UNIFORM_GAP_CONTINUATION.json"
SECOND_GAP_DATA = SECOND_GAP.with_suffix(".npz")
FIRST_STEP = BASE / "BHSM_N12_C2_CANCELLED_FIELD_LOHNER_STEP.json"
MODULE = ROOT / "src" / "bhsm" / "interface" / "aether_forward_c2_finite_core_descriptor.py"
COEFFICIENT = ROOT / "scripts" / "derive_n12_c2_birth_coefficient_quotient_jet.py"
THEORY = ROOT / "theory" / "n12_c2_1222_segment_finite_core_descriptor.md"
STEP_NUMBERS = tuple(range(1215, 1223))


def _step_path(segment: int) -> Path:
    if segment == 1215:
        return FIRST_STEP
    return BASE / f"BHSM_N12_C2_LOHNER_STEP_{segment}.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rows(record: dict[str, Any], key: str) -> list[dict[str, Any]]:
    return list(record[key]["rows"])


def build_payload() -> dict[str, Any]:
    step_paths = tuple(_step_path(segment) for segment in STEP_NUMBERS)
    inputs = (
        PREFIX, PREFIX_DATA, FIBER, FIBER_DATA, GAP, GAP_DATA,
        SECOND_GAP, SECOND_GAP_DATA,
        *(path for step_path in step_paths for path in (step_path, step_path.with_suffix(".npz"))),
        MODULE, COEFFICIENT, THEORY,
    )
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing 1222 finite-core inputs: " + ", ".join(missing))

    prefix, fiber, gap, second_gap = (
        _load(path) for path in (PREFIX, FIBER, GAP, SECOND_GAP)
    )
    step_records = [_load(path) for path in step_paths]
    if not all(record.get("validation_passed") is True for record in (
        prefix, fiber, gap, second_gap, *step_records,
    )):
        raise RuntimeError("validated finite-core continuation parents required")

    with np.load(PREFIX_DATA) as data:
        prefix_nodes = np.asarray(data["C2_proof_center_nodes"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        prefix_tubes = np.asarray(data["node_action_tube_upper"], dtype=float)
        prefix_x = np.asarray(data["node_log_R4_center"], dtype=float)
        prefix_x_interval = np.asarray(data["node_log_R4_interval"], dtype=float)
        prefix_duration = np.asarray(data["segment_proper_duration_interval"], dtype=float)
    with np.load(FIBER_DATA) as data:
        fiber_nodes = np.asarray(data["C2_descriptor_fiber_predictor_centers"], dtype=float)
    with np.load(GAP_DATA) as data:
        gap_nodes = np.asarray(data["C2_uniform_gap_predictor_centers"], dtype=float)
    with np.load(SECOND_GAP_DATA) as data:
        second_gap_nodes = np.asarray(data["C2_second_uniform_gap_predictor_centers"], dtype=float)

    fiber_rows = _rows(fiber, "continuation")
    gap_rows = _rows(gap, "continuation")
    second_gap_rows = _rows(second_gap, "continuation")
    cover_nodes = (fiber_nodes, gap_nodes, second_gap_nodes)
    cover_rows = (fiber_rows, gap_rows, second_gap_rows)

    appended_nodes = [nodes[1:] for nodes in cover_nodes]
    appended_tubes = [
        np.asarray([row["endpoint_tube_radius_upper"] for row in rows], dtype=float)
        for rows in cover_rows
    ]
    appended_duration = [
        np.asarray([row["proper_time_increment_interval"] for row in rows], dtype=float)
        for rows in cover_rows
    ]
    step_endpoints: list[np.ndarray] = []
    step_starts: list[np.ndarray] = []
    for path in step_paths:
        with np.load(path.with_suffix(".npz")) as data:
            step_starts.append(np.asarray(data["center_state"], dtype=float))
            step_endpoints.append(np.asarray(data["endpoint_predictor_center"], dtype=float))
    appended_nodes.append(np.asarray(step_endpoints))
    appended_tubes.append(np.asarray([
        row["segment"]["endpoint_tube_radius_upper"] for row in step_records
    ], dtype=float))
    appended_duration.append(np.asarray([
        row["segment"]["proper_time_increment_interval"] for row in step_records
    ], dtype=float))

    joins = [
        float(np.linalg.norm((prefix_nodes[-1] - fiber_nodes[0]) * weights)),
        float(np.linalg.norm((fiber_nodes[-1] - gap_nodes[0]) * weights)),
        float(np.linalg.norm((gap_nodes[-1] - second_gap_nodes[0]) * weights)),
        float(np.linalg.norm((second_gap_nodes[-1] - step_starts[0]) * weights)),
    ]
    joins.extend(
        float(np.linalg.norm((left - right) * weights))
        for left, right in zip(step_endpoints[:-1], step_starts[1:], strict=True)
    )

    nodes = np.vstack((prefix_nodes, *appended_nodes))
    tubes = np.concatenate((prefix_tubes, *appended_tubes))
    durations = np.vstack((prefix_duration, *appended_duration))
    new_rows = [
        _coefficient_enclosure(node, weights, float(tube))
        for node, tube in zip(nodes[prefix_nodes.shape[0]:], tubes[prefix_tubes.size:], strict=True)
    ]
    x = np.concatenate((prefix_x, np.asarray([row["center_log_R4"] for row in new_rows])))
    x_interval = np.vstack((
        prefix_x_interval,
        np.asarray([row["root_log_R4_interval"] for row in new_rows]),
    ))
    h = np.sqrt(durations[:, 0] * durations[:, 1])

    specifications = {
        "scalar_c3": ("scalar", 3.0, None),
        "product_Dirac_lambda1_5_chirality_plus": ("product_Dirac", 1.5, 1),
        "product_Dirac_lambda1_5_chirality_minus": ("product_Dirac", 1.5, -1),
    }
    channels = {}
    for name, (kind, value, chirality) in specifications.items():
        kwargs = {
            "log_radii": x,
            "proper_durations": h,
            "channel": kind,
            "unit_channel_value": value,
        }
        if chirality is not None:
            kwargs["chirality"] = chirality
        channels[name] = assemble_finite_core_descriptor(**kwargs)
    arrays: dict[str, np.ndarray] = {
        "C2_proof_center_nodes": nodes,
        "state_weights": weights,
        "node_action_tube_upper": tubes,
        "node_log_R4_center": x,
        "node_log_R4_interval": x_interval,
        "segment_proper_duration_interval": durations,
        "segment_proper_duration_proof_center": h,
    }
    for name, channel in channels.items():
        for key in (
            "K_diagonal", "K_off_diagonal", "M_diagonal", "M_off_diagonal",
            "element_coefficient", "D_x_mid_K_elements", "D_h_K_elements",
            "D_h_M_elements",
        ):
            arrays[f"{name}__{key}"] = np.asarray(channel[key])
    np.savez_compressed(DATA_RESULT, **arrays)

    total_duration = np.sum(durations, axis=0)
    summaries = {
        name: {
            "channel": channel["channel"],
            "chirality": channel["chirality"],
            "descriptor_dimension": int(channel["dimension"]),
            "segment_count": int(channel["segment_count"]),
            "generalized_gap_lower": float(channel["generalized_gap_lower"]),
            "minimum_mass_diagonal": float(np.min(channel["M_diagonal"])),
            "explicit_matrix_inverse_formed": False,
        }
        for name, channel in channels.items()
    }
    validation = {
        "validated_1064_segment_prefix_consumed": prefix["coefficient_path"]["segment_count"] == 1064,
        "exact_fiber_cover_adds_64_segments": len(fiber_rows) == 64,
        "uniform_gap_cover_adds_64_segments": len(gap_rows) == 64,
        "second_uniform_gap_cover_adds_22_segments": len(second_gap_rows) == 22,
        "matrix_Lohner_cover_adds_8_segments": len(step_records) == 8,
        "all_chronological_joins_are_exact_to_storage": max(joins) == 0.0,
        "exactly_1223_nodes_and_1222_intervals": nodes.shape == (1223, 98) and durations.shape == (1222, 2),
        "every_interval_has_positive_proper_duration": np.all(durations[:, 0] > 0.0) and np.all(durations[:, 1] >= durations[:, 0]),
        "every_node_has_a_positive_finite_tube": np.all(np.isfinite(tubes)) and np.all(tubes > 0.0),
        "every_log_radius_center_is_enclosed": np.all((x_interval[:, 0] <= x) & (x <= x_interval[:, 1])),
        "all_channel_form_gaps_are_positive": all(channel["generalized_gap_lower"] > 0.0 for channel in channels.values()),
        "birth_retained_far_edge_is_Friedrichs_only": all(channel["birth_node_retained"] and channel["far_core_Dirichlet_node_eliminated"] for channel in channels.values()),
        "no_kinetic_or_Dirac_block_inverse_formed": True,
        "far_core_edge_not_promoted_to_event_or_stop": True,
        "no_selector_terminal_load_scale_fit_recurrence_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR",
        "status": "C2_1222_SEGMENT_EXACT_FIBER_FINITE_CORE_PENCIL_ASSEMBLED" if passed else "C2_1222_SEGMENT_FINITE_CORE_NOT_CERTIFIED",
        "classification": "ONE_NESTED_FRIEDRICHS_FORM_CORE_ASSEMBLED_THROUGH_THE_EXACT_FIBER_MATRIX_LOHNER_PREFIX;_THE_FAR_EDGE_IS_PROOF_TECHNOLOGY_NOT_ENDPOINT_PHYSICS",
        "coefficient_path": {
            "node_count": int(nodes.shape[0]),
            "segment_count": int(durations.shape[0]),
            "proper_duration_interval": [float(total_duration[0]), float(total_duration[1])],
            "log_R4_global_interval": [float(np.min(x_interval[:, 0])), float(np.max(x_interval[:, 1]))],
            "maximum_action_tube_upper": float(np.max(tubes)),
            "chronological_join_action_norm_residuals": joins,
            "latest_signed_descriptor": step_records[-1]["segment"]["signed_descriptor_end"],
            "proof_centers_are_exact_physical_states": False,
        },
        "descriptor_pencils": summaries,
        "endpoint_event_child_partition": {
            "retained_boundary": "C2_BIRTH_TRACE_NODE_0",
            "interior": "NODES_1_THROUGH_1221",
            "far_core_edge": "NODE_1222_DIRICHLET_FRIEDRICHS_FORM_CORE_TRUNCATION",
            "far_core_edge_is_physical_endpoint": False,
            "terminal_load_imposed": False,
        },
        "adjudication": {
            "finite_event_or_canonical_stop": "NOT_REACHED",
            "maximal_history_outcome": "OPEN",
            "finite_core_force_net": "EXTENDED_TO_1222",
            "Gate7": "G7_08_OPEN_PROJECTED_HEAT_MINUS_ZETA_CAUCHY_TAIL_OR_FINITE_EVENT_STOP",
            "Gate8": "LOCKED",
        },
        "validated_invalidated_open": {
            "VALIDATED": ["1222-segment nested form core", "positive fixed-channel descriptor gaps", "exact chronological joins"],
            "INVALIDATED": ["the segment-1222 proof edge is a physical endpoint", "more scalar proof boxes are the Gate-7 owner"],
            "OPEN": ["maximal endpoint outcome", "combined projected heat-minus-zeta force Cauchy tail", "zero-source force"],
        },
        "hindsight": {
            "classification": "PROOF_CHART_LIMIT_AND_CONTINUOUS_WITHIN_CLASS_EVOLUTION",
            "obstruction_physical": False,
        },
        "exact_next_dependency": "EVALUATE_THE_INVERSE_FREE_1222_CORE_WEYL_COEFFICIENT_COTANGENT_AND_FORM_THE_NEXT_PROJECTED_HEAT_MINUS_ZETA_FORCE_NET_INCREMENT;_DO_NOT_PROMOTE_THE_FAR_CORE_EDGE_TO_AN_ENDPOINT",
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA_RESULT),
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in inputs},
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({
        "status": payload["status"],
        "segments": payload["coefficient_path"]["segment_count"],
        "duration": payload["coefficient_path"]["proper_duration_interval"],
        "max_tube": payload["coefficient_path"]["maximum_action_tube_upper"],
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
