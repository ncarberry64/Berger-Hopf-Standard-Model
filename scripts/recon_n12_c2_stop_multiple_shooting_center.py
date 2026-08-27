"""Assemble the finite core-to-stop Hermite multiple-shooting center.

The stored global path supplies 47 positive nodes through action length 92;
the refined stop supplies the terminal node.  Exact retained-field rates are
evaluated at every node and at every cubic-Hermite midpoint.  The resulting
defect profile identifies the finite correlated proof mesh required by the
flow-cylinder theorem.  It is center reconnaissance, not interval authority.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_c2_exact_fixed_s_field import (  # noqa: E402
    exact_cancelled_euler_dirac_field_action,
)
from bhsm.interface.aether_forward_c2_geometry_incidence import (  # noqa: E402
    boundary_geometry_action_covectors,
)


BASE = ROOT / "artifacts" / "flagship_integration"
PATH_RECORD = BASE / "BHSM_N12_C2_GLOBAL_CANONICAL_STOP_RECONNAISSANCE.json"
PATH_DATA = PATH_RECORD.with_suffix(".npz")
STOP_RECORD = BASE / "BHSM_N12_C2_REFINED_CANONICAL_STOP_RECONNAISSANCE.json"
STOP_DATA = STOP_RECORD.with_suffix(".npz")
RESULT = BASE / "BHSM_N12_C2_STOP_MULTIPLE_SHOOTING_CENTER.json"
DATA = RESULT.with_suffix(".npz")


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _evaluate(args: tuple[np.ndarray, float, np.ndarray, np.ndarray]) -> dict[str, Any]:
    state, descriptor, weights, reference = args
    field = exact_cancelled_euler_dirac_field_action(
        state=state,
        weights=weights,
        reference=reference,
        signed_descriptor=max(float(descriptor), 0.0),
    )
    cancelled = np.asarray(field["cancelled_field_action"], dtype=float)
    norm = float(np.linalg.norm(cancelled))
    geometry = boundary_geometry_action_covectors(state=state, weights=weights)
    return {
        "state_rate": cancelled / weights / norm,
        "action_rate": cancelled / norm,
        "descriptor_rate": float(field["Delta"]) / norm,
        "Delta": float(field["Delta"]),
        "field_norm": norm,
        "selected_branch": int(field["selected_branch"]),
        "selected_eigenline_gap": float(field["selected_eigenline_gap"]),
        "boundary_lapse": float(np.exp(float(geometry["log_lapse"]))),
        "boundary_radius": float(np.exp(float(geometry["log_R4"]))),
    }


def _parallel_evaluate(
    states: np.ndarray,
    descriptors: np.ndarray,
    weights: np.ndarray,
    reference: np.ndarray,
) -> list[dict[str, Any]]:
    arguments = [
        (state, float(descriptor), weights, reference)
        for state, descriptor in zip(states, descriptors, strict=True)
    ]
    workers = min(4, os.cpu_count() or 1)
    with ProcessPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(_evaluate, arguments))


def build_payload() -> dict[str, Any]:
    path_record = json.loads(PATH_RECORD.read_text(encoding="utf-8"))
    stop_record = json.loads(STOP_RECORD.read_text(encoding="utf-8"))
    if path_record.get("status") != "FINITE_GLOBAL_s_ZERO_BRACKET_RECONNAISSANCE_ONLY":
        raise RuntimeError("global stop path required")
    if not stop_record["claim_boundary"]["stop_face_regular_at_center"]:
        raise RuntimeError("transverse refined stop center required")
    with np.load(PATH_DATA) as source:
        states = np.asarray(source["centers"], dtype=float)
        descriptors = np.asarray(source["signed_descriptors"], dtype=float)
        action_lengths = np.asarray(source["action_lengths"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    with np.load(STOP_DATA) as source:
        stop = np.asarray(source["stop_center"], dtype=float)
        stop_length = float(source["total_action_length"])
    states = np.vstack((states, stop))
    descriptors = np.concatenate((descriptors, [0.0]))
    action_lengths = np.concatenate((action_lengths, [stop_length]))

    print(f"evaluating {states.shape[0]} exact node rates", flush=True)
    node_rows = _parallel_evaluate(states, descriptors, weights, reference)
    state_rates = np.asarray([row["state_rate"] for row in node_rows])
    action_rates = np.asarray([row["action_rate"] for row in node_rows])
    descriptor_rates = np.asarray([row["descriptor_rate"] for row in node_rows])

    midpoints = []
    midpoint_descriptors = []
    midpoint_state_rates = []
    midpoint_descriptor_rates = []
    for index in range(states.shape[0] - 1):
        h = float(action_lengths[index + 1] - action_lengths[index])
        midpoint = (
            0.5 * (states[index] + states[index + 1])
            + h * (state_rates[index] - state_rates[index + 1]) / 8.0
        )
        midpoint_descriptor = (
            0.5 * (descriptors[index] + descriptors[index + 1])
            + h * (descriptor_rates[index] - descriptor_rates[index + 1]) / 8.0
        )
        midpoint_rate = (
            1.5 * (states[index + 1] - states[index]) / h
            - 0.25 * (state_rates[index] + state_rates[index + 1])
        )
        midpoint_descriptor_rate = (
            1.5 * (descriptors[index + 1] - descriptors[index]) / h
            - 0.25 * (descriptor_rates[index] + descriptor_rates[index + 1])
        )
        midpoints.append(midpoint)
        midpoint_descriptors.append(midpoint_descriptor)
        midpoint_state_rates.append(midpoint_rate)
        midpoint_descriptor_rates.append(midpoint_descriptor_rate)
    midpoints = np.asarray(midpoints)
    midpoint_descriptors = np.asarray(midpoint_descriptors)
    midpoint_state_rates = np.asarray(midpoint_state_rates)
    midpoint_descriptor_rates = np.asarray(midpoint_descriptor_rates)

    print(f"evaluating {midpoints.shape[0]} exact midpoint rates", flush=True)
    midpoint_rows = _parallel_evaluate(
        midpoints, midpoint_descriptors, weights, reference
    )
    exact_midpoint_state_rates = np.asarray([
        row["state_rate"] for row in midpoint_rows
    ])
    exact_midpoint_descriptor_rates = np.asarray([
        row["descriptor_rate"] for row in midpoint_rows
    ])
    state_defects = (midpoint_state_rates - exact_midpoint_state_rates) * weights
    descriptor_defects = (
        midpoint_descriptor_rates - exact_midpoint_descriptor_rates
    )
    state_defect_norms = np.linalg.norm(state_defects, axis=1)

    tangent_cosines = np.sum(action_rates[:-1] * action_rates[1:], axis=1)
    tangent_cosines /= (
        np.linalg.norm(action_rates[:-1], axis=1)
        * np.linalg.norm(action_rates[1:], axis=1)
    )
    tangent_cosines = np.clip(tangent_cosines, -1.0, 1.0)
    tangent_turns = np.arccos(tangent_cosines)
    worst = int(np.argmax(state_defect_norms))
    worst_descriptor = int(np.argmax(np.abs(descriptor_defects)))

    np.savez_compressed(
        DATA,
        centers=states,
        signed_descriptors=descriptors,
        action_lengths=action_lengths,
        state_weights=weights,
        branch_reference=reference,
        state_rates=state_rates,
        action_rates=action_rates,
        descriptor_rates=descriptor_rates,
        Hermite_midpoints=midpoints,
        Hermite_midpoint_descriptors=midpoint_descriptors,
        Hermite_midpoint_state_rate_defects=state_defects,
        Hermite_midpoint_descriptor_rate_defects=descriptor_defects,
        tangent_turns=tangent_turns,
    )
    return {
        "artifact": "BHSM_N12_C2_STOP_MULTIPLE_SHOOTING_CENTER",
        "status": "FINITE_47_SEAM_HERMITE_STOP_CENTER_ASSEMBLED;_INTERVAL_SHADOWING_OPEN",
        "mesh": {
            "nodes": int(states.shape[0]),
            "seams": int(states.shape[0] - 1),
            "action_length_start": float(action_lengths[0]),
            "action_length_stop": float(action_lengths[-1]),
            "minimum_step": float(np.min(np.diff(action_lengths))),
            "maximum_step": float(np.max(np.diff(action_lengths))),
        },
        "center_defect_profile": {
            "maximum_Hermite_midpoint_state_rate_defect_action_norm": float(
                state_defect_norms[worst]
            ),
            "worst_state_defect_seam": worst,
            "maximum_absolute_Hermite_midpoint_descriptor_rate_defect": float(
                abs(descriptor_defects[worst_descriptor])
            ),
            "worst_descriptor_defect_seam": worst_descriptor,
            "maximum_state_rate_defect_after_first_four_seams": float(
                np.max(state_defect_norms[4:])
            ),
            "integrated_midpoint_state_defect_proxy": float(
                np.sum(np.diff(action_lengths) * state_defect_norms)
            ),
            "first_four_seam_fraction_of_integrated_defect_proxy": float(
                np.sum(np.diff(action_lengths)[:4] * state_defect_norms[:4])
                / np.sum(np.diff(action_lengths) * state_defect_norms)
            ),
            "maximum_adjacent_tangent_turn_radians": float(np.max(tangent_turns)),
            "total_adjacent_tangent_turn_radians": float(np.sum(tangent_turns)),
        },
        "sampled_domain_margins": {
            "minimum_selected_eigenline_gap": min(
                float(row["selected_eigenline_gap"])
                for row in node_rows + midpoint_rows
            ),
            "minimum_boundary_lapse": min(
                float(row["boundary_lapse"]) for row in node_rows + midpoint_rows
            ),
            "minimum_boundary_radius": min(
                float(row["boundary_radius"]) for row in node_rows + midpoint_rows
            ),
            "minimum_field_action_norm": min(
                float(row["field_norm"]) for row in node_rows + midpoint_rows
            ),
            "all_selected_branches_are_24": all(
                int(row["selected_branch"]) == 24 for row in node_rows + midpoint_rows
            ),
        },
        "proof_assembly": {
            "initial_inclusion": "CERTIFIED_1222_CORE_TUBE",
            "center_curve": "PIECEWISE_CUBIC_HERMITE_WITH_EXACT_ACTION_FIELD_NODE_RATES",
            "terminal_equation": "s=0_WITH_Ds[V]<0",
            "required_enclosure": (
                "ONE_BLOCK_LOWER_TRIANGULAR_GREEN_HERMITE_OR_SHEARED_LOHNER_"
                "KRAWCZYK_OPERATOR_ON_THE_47_CORRELATED_SEAMS"
            ),
            "full_Euler_Dirac_inverse_required": False,
        },
        "claim_boundary": {
            "exact_node_and_midpoint_fields_evaluated": True,
            "Hermite_center_is_exact_flow": False,
            "between_node_interval_remainder_certified": False,
            "finite_reset_to_stop_witness_certified": False,
            "Gate7": "ACTIVE",
            "Gate8": "LOCKED",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "BOUND_THE_BETWEEN_NODE_GREEN_HERMITE_REMAINDER_AND_THE_"
            "CONJUGATED_TRANSVERSE_PROPAGATOR_ON_THE_STORED_47_SEAM_"
            "CORRELATED_CENTER,_THEN_APPLY_THE_SCALAR_TERMINAL_INTERVAL_NEWTON"
        ),
        "data": DATA.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            PATH_RECORD.relative_to(ROOT).as_posix(): _sha256(PATH_RECORD),
            PATH_DATA.relative_to(ROOT).as_posix(): _sha256(PATH_DATA),
            STOP_RECORD.relative_to(ROOT).as_posix(): _sha256(STOP_RECORD),
            STOP_DATA.relative_to(ROOT).as_posix(): _sha256(STOP_DATA),
        },
        "validation_passed": False,
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
        "mesh": payload["mesh"],
        "center_defect_profile": payload["center_defect_profile"],
        "sampled_domain_margins": payload["sampled_domain_margins"],
        "exact_next_dependency": payload["exact_next_dependency"],
    }, indent=2))


if __name__ == "__main__":
    main()
