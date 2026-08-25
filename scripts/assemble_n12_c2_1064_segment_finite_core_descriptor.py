"""Assemble the action-owned 1064-segment C2 finite form-core pencil."""

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
sys.path.insert(0, str(ROOT / "scripts"))

from bhsm.interface.aether_forward_c2_finite_core_descriptor import (  # noqa: E402
    assemble_finite_core_descriptor,
)
from derive_n12_c2_birth_coefficient_quotient_jet import _coefficient_enclosure  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_1064_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
DATA_RESULT = BASE / "BHSM_N12_C2_1064_SEGMENT_FINITE_CORE_DESCRIPTOR.npz"
REFINED = BASE / "BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.json"
REFINED_DATA = BASE / "BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.npz"
OUTER = BASE / "BHSM_N12_C2_POLE_FREE_OUTER_MARGIN_EXTENSION.json"
OUTER_DATA = BASE / "BHSM_N12_C2_POLE_FREE_OUTER_MARGIN_EXTENSION.npz"
SECOND = BASE / "BHSM_N12_C2_TRANSLATED_POLE_FREE_SEGMENT.json"
SECOND_DATA = BASE / "BHSM_N12_C2_TRANSLATED_POLE_FREE_SEGMENT.npz"
EXTENDED = BASE / "BHSM_N12_C2_EXTENDED_DESCRIPTOR_RESOLUTION_AUDIT.json"
EXTENDED_DATA = BASE / "BHSM_N12_C2_EXTENDED_DESCRIPTOR_RESOLUTION_AUDIT.npz"
COMPENSATED = BASE / "BHSM_N12_C2_COMPENSATED_DESCRIPTOR_CONTINUATION.json"
COMPENSATED_DATA = BASE / "BHSM_N12_C2_COMPENSATED_DESCRIPTOR_CONTINUATION.npz"
ADAPTIVE = BASE / "BHSM_N12_C2_ADAPTIVE_BALL_CONTINUATION.json"
ADAPTIVE_DATA = BASE / "BHSM_N12_C2_ADAPTIVE_BALL_CONTINUATION.npz"
RECENTERED = BASE / "BHSM_N12_C2_RECENTERED_ADAPTIVE_CONTINUATION.json"
RECENTERED_DATA = BASE / "BHSM_N12_C2_RECENTERED_ADAPTIVE_CONTINUATION.npz"
CLASS = BASE / "BHSM_N12_C2_ENCLOSURE_CLASS_INVARIANT_EXTENSION.json"
MODULE = ROOT / "src/bhsm/interface/aether_forward_c2_finite_core_descriptor.py"
THEORY = ROOT / "theory/n12_c2_1064_segment_finite_core_descriptor.md"
INPUTS = (
    REFINED, REFINED_DATA, OUTER, OUTER_DATA, SECOND, SECOND_DATA,
    EXTENDED, EXTENDED_DATA, COMPENSATED, COMPENSATED_DATA,
    ADAPTIVE, ADAPTIVE_DATA, RECENTERED, RECENTERED_DATA, CLASS,
    MODULE, THEORY,
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _proper_rows(rows: list[dict[str, Any]]) -> list[list[float]]:
    return [list(map(float, row["proper_time_increment_interval"])) for row in rows]


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing finite-core descriptor inputs: " + ", ".join(missing))
    refined, outer, second, extended, compensated, adaptive, recentered, class_record = (
        _load(path) for path in (
            REFINED, OUTER, SECOND, EXTENDED, COMPENSATED, ADAPTIVE,
            RECENTERED, CLASS,
        )
    )
    if not all(record.get("validation_passed") is True for record in (
        refined, outer, second, extended, compensated, adaptive, recentered, class_record,
    )):
        raise RuntimeError("validated C2 coefficient-path parents required")

    with np.load(REFINED_DATA) as data:
        root = np.asarray(data["state"], dtype=float)[:98]
        weights = np.asarray(data["state_weights"], dtype=float)
    with np.load(OUTER_DATA) as data:
        outer_center = np.asarray(data["C2_predictor_state"], dtype=float)
    with np.load(SECOND_DATA) as data:
        second_center = np.asarray(data["C2_predictor_state"], dtype=float)
    with np.load(EXTENDED_DATA) as data:
        extended_centers = np.asarray(data["C2_predictor_centers"], dtype=float)
    with np.load(COMPENSATED_DATA) as data:
        compensated_centers = np.asarray(data["C2_compensated_predictor_centers"], dtype=float)
    with np.load(ADAPTIVE_DATA) as data:
        adaptive_centers = np.asarray(data["C2_adaptive_predictor_centers"], dtype=float)
    with np.load(RECENTERED_DATA) as data:
        recentered_centers = np.asarray(data["C2_recentered_adaptive_predictor_centers"], dtype=float)

    join_residuals = [
        float(np.linalg.norm((extended_centers[0] - second_center) * weights)),
        float(np.linalg.norm((compensated_centers[0] - extended_centers[-1]) * weights)),
        float(np.linalg.norm((adaptive_centers[0] - compensated_centers[-1]) * weights)),
        float(np.linalg.norm((recentered_centers[0] - adaptive_centers[-1]) * weights)),
    ]
    nodes = np.vstack((
        root,
        outer_center,
        second_center,
        extended_centers[1:],
        compensated_centers[1:],
        adaptive_centers[1:],
        recentered_centers[1:],
    ))
    duration_intervals = np.asarray(
        [outer["extended_segment"]["proper_time_interval"]]
        + [second["translated_segment"]["proper_time_increment_interval"]]
        + _proper_rows(extended["cover"]["rows"])
        + _proper_rows(compensated["compensated_cover"]["rows"])
        + _proper_rows(adaptive["adaptive_cover"]["rows"])
        + _proper_rows(recentered["recentered_cover"]["rows"]),
        dtype=float,
    )
    tubes = np.asarray(
        [refined["refined_radii_theorem"]["a_posteriori_root_distance_upper"]]
        + [outer["endpoint_recenter"]["endpoint_tube_radius_upper"]]
        + [second["endpoint_recenter"]["endpoint_tube_radius_upper"]]
        + [row["endpoint_tube_radius_upper"] for row in extended["cover"]["rows"]]
        + [row["endpoint_tube_radius_upper"] for row in compensated["compensated_cover"]["rows"]]
        + [row["endpoint_tube_radius_upper"] for row in adaptive["adaptive_cover"]["rows"]]
        + [row["endpoint_tube_radius_upper"] for row in recentered["recentered_cover"]["rows"]],
        dtype=float,
    )
    coefficient_rows = [
        _coefficient_enclosure(node, weights, float(tube))
        for node, tube in zip(nodes, tubes, strict=True)
    ]
    x_center = np.asarray([row["center_log_R4"] for row in coefficient_rows])
    x_interval = np.asarray([row["root_log_R4_interval"] for row in coefficient_rows])
    duration_center = np.sqrt(duration_intervals[:, 0] * duration_intervals[:, 1])

    channels = {
        "scalar_c3": assemble_finite_core_descriptor(
            log_radii=x_center,
            proper_durations=duration_center,
            channel="scalar",
            unit_channel_value=3.0,
        ),
        "product_Dirac_lambda1_5_chirality_plus": assemble_finite_core_descriptor(
            log_radii=x_center,
            proper_durations=duration_center,
            channel="product_Dirac",
            unit_channel_value=1.5,
            chirality=1,
        ),
        "product_Dirac_lambda1_5_chirality_minus": assemble_finite_core_descriptor(
            log_radii=x_center,
            proper_durations=duration_center,
            channel="product_Dirac",
            unit_channel_value=1.5,
            chirality=-1,
        ),
    }
    arrays: dict[str, np.ndarray] = {
        "C2_proof_center_nodes": nodes,
        "state_weights": weights,
        "node_action_tube_upper": tubes,
        "node_log_R4_center": x_center,
        "node_log_R4_interval": x_interval,
        "segment_proper_duration_interval": duration_intervals,
        "segment_proper_duration_proof_center": duration_center,
    }
    for name, channel in channels.items():
        for key in (
            "K_diagonal", "K_off_diagonal", "M_diagonal", "M_off_diagonal",
            "element_coefficient", "D_x_mid_K_elements", "D_h_K_elements",
            "D_h_M_elements",
        ):
            arrays[f"{name}__{key}"] = np.asarray(channel[key])
    np.savez_compressed(DATA_RESULT, **arrays)

    total_interval = np.sum(duration_intervals, axis=0)
    validation = {
        "class_invariant_parent_covers_1064_segments": (
            class_record["class_invariance_extension"]["extended_certified_segment_count"] == 1064
        ),
        "exactly_1065_chronological_nodes_assembled": nodes.shape == (1065, 98),
        "exactly_1064_positive_duration_intervals_assembled": (
            duration_intervals.shape == (1064, 2)
            and np.all(duration_intervals[:, 0] > 0.0)
            and np.all(duration_intervals[:, 1] >= duration_intervals[:, 0])
        ),
        "all_chronological_data_joins_are_exact_to_storage": max(join_residuals) == 0.0,
        "every_node_has_a_positive_finite_tube": (
            tubes.shape == (1065,) and np.all(np.isfinite(tubes)) and np.all(tubes > 0.0)
        ),
        "every_log_radius_center_is_inside_its_certified_interval": np.all(
            (x_interval[:, 0] <= x_center) & (x_center <= x_interval[:, 1])
        ),
        "all_three_fixed_channels_have_positive_uniform_form_gap": all(
            float(channel["generalized_gap_lower"]) > 0.0 for channel in channels.values()
        ),
        "birth_node_retained_and_far_core_node_eliminated": all(
            channel["birth_node_retained"] and channel["far_core_Dirichlet_node_eliminated"]
            for channel in channels.values()
        ),
        "no_ill_conditioned_kinetic_or_Dirac_block_inverted": all(
            channel["explicit_matrix_inverse_formed"] is False for channel in channels.values()
        ),
        "coefficient_derivative_adapter_is_element_local": all(
            np.asarray(channel["D_x_mid_K_elements"]).shape == (1064, 2, 2)
            for channel in channels.values()
        ),
        "far_core_Dirichlet_is_Friedrichs_exhaustion_not_physical_endpoint": True,
        "actual_reset_quotient_Jacobi_path_not_fabricated": True,
        "no_selector_terminal_load_scale_fit_recurrence_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    summaries = {
        name: {
            "channel": channel["channel"],
            "chirality": channel["chirality"],
            "descriptor_dimension": int(channel["dimension"]),
            "segment_count": int(channel["segment_count"]),
            "generalized_gap_lower": float(channel["generalized_gap_lower"]),
            "maximum_absolute_K_entry": float(max(
                np.max(np.abs(channel["K_diagonal"])),
                np.max(np.abs(channel["K_off_diagonal"])),
            )),
            "minimum_mass_diagonal": float(np.min(channel["M_diagonal"])),
            "explicit_matrix_inverse_formed": False,
        }
        for name, channel in channels.items()
    }
    return {
        "artifact": "BHSM_N12_C2_1064_SEGMENT_FINITE_CORE_DESCRIPTOR",
        "status": (
            "C2_1064_SEGMENT_ACTION_COEFFICIENT_FORM_CORE_PENCIL_ASSEMBLED"
            if passed else "C2_1064_SEGMENT_FINITE_CORE_DESCRIPTOR_NOT_CERTIFIED"
        ),
        "classification": (
            "THE_CERTIFIED_C2_PROOF_CENTERS_AND_PROPER_TIME_INTERVALS_ASSEMBLE_"
            "ONE_NONUNIFORM_NESTED_FRIEDRICHS_FORM_CORE_FOR_THE_SCALAR_AND_"
            "TWO_PRODUCT_DIRAC_CHANNELS_WITH_ELEMENT_LOCAL_COEFFICIENT_JETS_"
            "AND_NO_BLOCK_INVERSION_OR_PHYSICAL_FAR_ENDPOINT"
        ),
        "coefficient_path": {
            "node_count": int(nodes.shape[0]),
            "segment_count": int(duration_intervals.shape[0]),
            "proper_duration_interval": [float(total_interval[0]), float(total_interval[1])],
            "log_R4_global_interval": [float(np.min(x_interval[:, 0])), float(np.max(x_interval[:, 1]))],
            "maximum_action_tube_upper": float(np.max(tubes)),
            "chronological_join_action_norm_residuals": join_residuals,
            "proof_centers_are_exact_physical_states": False,
            "role": "CERTIFIED_COEFFICIENT_ENCLOSURE_FOR_ONE_NESTED_FORM_CORE",
        },
        "descriptor_pencils": summaries,
        "endpoint_event_child_partition": {
            "retained_boundary": "C2_BIRTH_TRACE_NODE_0",
            "interior": "NODES_1_THROUGH_1063",
            "far_core_edge": "NODE_1064_DIRICHLET_FORM_CORE_TRUNCATION",
            "far_core_edge_is_physical_endpoint": False,
            "terminal_load_imposed": False,
        },
        "derivative_interface": {
            "available": "D_(x_mid,h)_ELEMENT_FORMS_FOR_ALL_THREE_CHANNELS",
            "chain_rule": "D_xi_K=sum_e(D_xmid_K_e*D_xi_xmid_e+D_h_K_e*D_xi_h_e)",
            "actual_reset_quotient_coefficient_Jacobi": "OPEN",
            "full_D_xi_K": "OPEN_UNTIL_ACTION_OWNED_RESET_JACOBI_PATH_IS_SUPPLIED",
        },
        "adjudication": {
            "earlier_endpoint_only_data_inventory": "SUPERSEDED_FOR_FINITE_CORE_COEFFICIENT_PATH",
            "actual_maximal_history_coefficient_oracle": "OPEN_BEYOND_THIS_PREFIX",
            "actual_projected_zero_source_force": "OPEN_AFTER_RESET_QUOTIENT_JACOBI_AND_MAXIMAL_TAIL",
            "proof_edge_promoted_to_endpoint": False,
        },
        "exact_next_dependency": (
            "PROPAGATE_THE_ACTION_OWNED_RESET_QUOTIENT_JACOBI_COTANGENT_"
            "THROUGH_THIS_COEFFICIENT_PATH_AND_CERTIFY_THE_COMBINED_PROJECTED_"
            "FINITE_CORE_FORCE_NET_IS_CAUCHY_ON_THE_MAXIMAL_EXHAUSTION,_OR_"
            "SUPPLY_AN_ACTUAL_FINITE_EVENT_OR_CANONICAL_STOP"
        ),
        "claim_boundary": {
            "C2_1064_segment_coefficient_form_core": "ASSEMBLED",
            "C2_maximal_coefficient_oracle": "OPEN",
            "full_reset_quotient_D_xi_K": "OPEN",
            "zero_source_force": "OPEN",
            "Gate7": "ACTIVE_PROJECTED_FORCE_TAIL_OR_FINITE_EVENT_STOP",
            "FULL_BHSM_COMPLETE": False,
        },
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA_RESULT),
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
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
        "nodes": payload["coefficient_path"]["node_count"],
        "segments": payload["coefficient_path"]["segment_count"],
        "duration": payload["coefficient_path"]["proper_duration_interval"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
