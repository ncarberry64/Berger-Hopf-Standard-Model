"""Audit event-return evidence already present in the certified N12 witness.

Only the certified witness endpoints are evaluated.  No new evolution,
continuation, or return search is performed, and the endpoint result is not
used to exclude an unrecorded interior or later return.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import (
    exact_action_jet_at_state,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import dimensions


ROOT = Path(__file__).resolve().parents[1]
ORDER = 12
STATE = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
)
DIRECT = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_CERTIFICATE.json"
)
PERSISTENCE = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_POSITIVE_DURATION_PERSISTENCE_WITNESS.json"
)
INTRINSIC = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_INTRINSIC_STATE_RETURN_SECTION_GATE.json"
)
RESULT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_EXISTING_PERSISTENCE_EVENT_RETURN_AUDIT.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _ordered_event(state, reference, points):
    qdim = dimensions(ORDER)["coordinates"]
    jet = exact_action_jet_at_state(
        ORDER,
        state[:qdim],
        state[qdim:2 * qdim],
        state[2 * qdim:],
        points=points,
    )
    values, vectors = np.linalg.eigh(np.asarray(jet.hessian, dtype=float))
    overlaps = np.abs(vectors.T @ reference)
    selected = int(np.argmax(overlaps))
    lower_gap = (
        float(values[selected] - values[selected - 1])
        if selected else float("inf")
    )
    upper_gap = (
        float(values[selected + 1] - values[selected])
        if selected + 1 < values.size else float("inf")
    )
    return {
        "selected_index": selected,
        "raw_eigenvalue": float(values[selected]),
        "reference_overlap": float(overlaps[selected]),
        "negative_inertia": int(np.count_nonzero(values < 0.0)),
        "minimum_neighbor_gap": min(lower_gap, upper_gap),
    }


def main() -> None:
    inputs = (STATE, DIRECT, PERSISTENCE, INTRINSIC)
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing event-return inputs: " + ", ".join(missing))
    direct = json.loads(DIRECT.read_text(encoding="utf-8"))
    persistence = json.loads(PERSISTENCE.read_text(encoding="utf-8"))
    intrinsic = json.loads(INTRINSIC.read_text(encoding="utf-8"))
    if not (
        direct["DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED"]
        and persistence["DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED"]
        and persistence["validation_passed"]
        and intrinsic["derived_first_return_section"]["map_executable"] is False
    ):
        raise RuntimeError("the required certified, still-open return inputs fail")

    checkpoint = np.load(STATE)
    joint = np.asarray(checkpoint["state"], dtype=float)
    reference = np.asarray(checkpoint["branch_reference"], dtype=float)
    reference /= np.linalg.norm(reference)
    dims = dimensions(ORDER)
    sdim = 2 * dims["coordinates"] + dims["multipliers"]
    event = joint[:sdim]
    child_initial = joint[sdim:]
    child_final = np.asarray(
        persistence["fine_evolution"]["final_state"], dtype=float
    )
    if child_final.shape != (sdim,):
        raise RuntimeError("certified persistence final state has wrong shape")

    evaluations = {}
    for points in (96, 192, 384):
        evaluations[str(points)] = {
            "event_section_anchor": _ordered_event(event, reference, points),
            "initial_child": _ordered_event(child_initial, reference, points),
            "final_child": _ordered_event(child_final, reference, points),
        }
    base = evaluations["96"]
    initial_value = float(base["initial_child"]["raw_eigenvalue"])
    final_value = float(base["final_child"]["raw_eigenvalue"])
    endpoints_positive = all(
        record[location]["raw_eigenvalue"] > 0.0
        for record in evaluations.values()
        for location in ("initial_child", "final_child")
    )
    endpoint_move_away = all(
        record["final_child"]["raw_eigenvalue"]
        > record["initial_child"]["raw_eigenvalue"]
        for record in evaluations.values()
    )
    rows = persistence["fine_evolution"]["rows"]
    validation = {
        "certified_witness_only_no_new_evolution_or_continuation": True,
        "existing_ordered_event_and_branch_reference_used": True,
        "event_anchor_is_numerically_on_ordered_section": all(
            abs(record["event_section_anchor"]["raw_eigenvalue"]) < 1.0e-10
            for record in evaluations.values()
        ),
        "certified_child_endpoints_are_positive": endpoints_positive,
        "endpoint_move_away_is_cross_quadrature_robust": endpoint_move_away,
        "endpoint_eigenline_overlap_is_continuous": min(
            record[location]["reference_overlap"]
            for record in evaluations.values()
            for location in ("initial_child", "final_child")
        ) > 0.98,
        "persistence_eta_admissible": (
            persistence["fine_evolution"]["minimum_eta_Legendre"] > 0.0
        ),
        "persistence_constraints_preserved": (
            persistence["fine_evolution"]["maximum_constraint_residual"] < 1.0e-8
        ),
        "interior_and_later_return_left_unadjudicated": True,
        "no_parent_subtraction_observable_or_prediction_promoted": True,
    }
    payload = {
        "artifact": "BHSM_N12_EXISTING_PERSISTENCE_EVENT_RETURN_AUDIT",
        "classification": (
            "CERTIFIED_WITNESS_ENDPOINTS_DO_NOT_SUPPLY_AN_EVENT_RETURN;_"
            "INTERIOR_AND_LATER_RETURN_UNADJUDICATED"
        ),
        "scope": {
            "role": "ENDPOINT_AUDIT_OF_AN_EXISTING_CERTIFIED_HISTORY",
            "new_evolution_continuation_or_numerical_campaign": False,
            "coordinate_duration": persistence["fine_evolution"][
                "coordinate_duration"
            ],
            "child_proper_duration": persistence["fine_evolution"][
                "child_proper_duration"
            ],
            "certified_history_rows": len(rows),
            "event_evaluated_at": ["event_anchor", "child_initial", "child_final"],
            "event_not_evaluated_on_unstored_interior_states": True,
        },
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in inputs
        },
        "endpoint_cross_quadrature": evaluations,
        "summary": {
            "initial_child_ordered_eigenvalue_at_96": initial_value,
            "final_child_ordered_eigenvalue_at_96": final_value,
            "endpoint_delta_at_96": final_value - initial_value,
            "endpoint_secant_rate_at_96": (
                (final_value - initial_value)
                / persistence["fine_evolution"]["coordinate_duration"]
            ),
            "both_endpoints_positive_at_all_quadratures": endpoints_positive,
            "final_endpoint_farther_from_zero_at_all_quadratures": (
                endpoint_move_away
            ),
            "maximum_constraint_residual_on_certified_witness": persistence[
                "fine_evolution"
            ]["maximum_constraint_residual"],
            "minimum_eta_on_certified_witness": persistence["fine_evolution"][
                "minimum_eta_Legendre"
            ],
        },
        "action_ownership_conclusion": {
            "existing_witness_records_a_first_positive_return": False,
            "unrecorded_interior_return_excluded": False,
            "later_first_positive_return_proved_to_exist": False,
            "return_domain_proved_empty": False,
            "parent_stationary_section_restored": False,
            "matched_parent_subtraction_authorized": False,
            "interpretation": (
                "the only certified history has no recorded event-section state "
                "after reconstruction, and its stored endpoint is farther from "
                "the section; endpoint evidence cannot replace the analytic "
                "global-flow return-or-no-return theorem"
            ),
        },
        "first_missing_action_owned_object": intrinsic[
            "first_missing_action_owned_object"
        ],
        "prediction_frozen": False,
        "held_out_comparison_performed": False,
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "classification": payload["classification"],
        "initial_child_ordered_eigenvalue_at_96": initial_value,
        "final_child_ordered_eigenvalue_at_96": final_value,
        "first_missing_action_owned_object": payload[
            "first_missing_action_owned_object"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
