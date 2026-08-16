"""Focused direct-response resolution audit at the accepted v20.77 frontier."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_post_recovery_multisecant_proposal_v20_77 import v20_77_selected_raw_vector
from bhsm.interface.aether_n3_reclassified_chain_proposal_v18_11 import _square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_72 import v20_72_selected_raw_vector
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_73 import v20_73_selected_raw_vector
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_75 import v20_75_selected_raw_vector


VERSION = "v20.78"
CLASSIFICATION = "BHSM_N3_V20_77_DIRECT_RESPONSE_RESOLUTION_AUDIT"
FULL_BHSM_COMPLETE = False
STEPS = (1.0e-6, 3.0e-7, 1.0e-7, 3.0e-8, 1.0e-8, 3.0e-9)


def direct_response_resolution_audit() -> dict[str, Any]:
    scales = kkt_variable_scales(); raw = v20_77_selected_raw_vector(); y = raw * scales
    residual = _square_physical_residual(y)
    multisecant_artifact = __import__("json").loads(Path(
        "artifacts/BHSM_N3_POST_RECOVERY_MULTI_SECANT_PROPOSAL_V20_77.json"
    ).read_text(encoding="utf-8"))["post_recovery_multisecant_proposal"]
    selected = multisecant_artifact["exact_line_search"]["best"]
    selected_raw = np.asarray([float.fromhex(value) for value in selected["raw_vector_hex"]])
    alpha = float(selected["alpha"])
    directions = {
        "physical_residual": residual.copy(),
        "latest_accepted_secant_v20_75_to_v20_77": (raw - v20_75_selected_raw_vector()) * scales,
        "material_corridor_secant_v20_72_to_v20_73": (v20_73_selected_raw_vector() - v20_72_selected_raw_vector()) * scales,
        "multisecant_proposal_direction": (selected_raw - v20_75_selected_raw_vector()) * scales / alpha,
    }
    records = []
    responses: dict[str, dict[float, np.ndarray]] = {}
    for name, direction in directions.items():
        norm = float(np.linalg.norm(direction)); unit = direction / norm
        local = {}
        for step in STEPS:
            response = norm * (
                _square_physical_residual(y + step * unit)
                - _square_physical_residual(y - step * unit)
            ) / (2.0 * step)
            local[step] = response
        responses[name] = local
        records.append({
            "direction": name, "physical_scaled_direction_norm": norm,
            "responses": [{"step": step, "response_l2": float(np.linalg.norm(local[step])), "event_row_response": float(local[step][375])} for step in STEPS],
        })
    comparisons = []
    for coarse, fine in zip(STEPS[:-1], STEPS[1:]):
        rows = []
        for name in directions:
            fine_response = responses[name][fine]; coarse_response = responses[name][coarse]
            rows.append({
                "direction": name,
                "relative_change": float(np.linalg.norm(fine_response - coarse_response) / max(1.0, np.linalg.norm(fine_response))),
                "event_row_absolute_change": float(abs(fine_response[375] - coarse_response[375])),
            })
        maximum_relative = max(row["relative_change"] for row in rows)
        maximum_event = max(row["event_row_absolute_change"] for row in rows)
        comparisons.append({
            "coarse_step": coarse, "fine_step": fine,
            "directions": rows,
            "maximum_relative_change": maximum_relative,
            "maximum_event_row_absolute_change": maximum_event,
            "all_directions_stable": bool(maximum_relative < 5.0e-3 and maximum_event < 1.0e-3),
        })
    stable = [row for row in comparisons if row["all_directions_stable"]]
    selected_pair = stable[-1] if stable else None
    return {
        "source_frontier": {"version": "v20.77", "exact_f376_l2": float(np.linalg.norm(residual))},
        "directions": records, "successive_scale_comparisons": comparisons,
        "selected_finest_common_stable_pair": selected_pair,
        "diagnostic_stability_definition": {"maximum_relative_change": 5.0e-3, "maximum_event_row_absolute_change": 1.0e-3},
        "outcome": "COMMON_RESOLVED_RESPONSE_SCALE_IDENTIFIED" if selected_pair is not None else "DIRECT_RESPONSE_RESOLUTION_BLOCKER",
        "next_action": "FORM_ONE_BOUNDED_RESPONSE_PROPOSAL_AT_THE_RESOLVED_SCALE" if selected_pair is not None else "DERIVE_ANALYTIC_OR_COMPLEX_STEP_EVENT_RESPONSE_BEFORE_MORE_NEWTON_PROPOSALS",
        "physical_equations_changed": False, "event_definition_changed": False,
        "acceptance_gate_changed": False, "componentwise_monotonicity_added": False,
    }


def completion_payload() -> dict[str, Any]:
    result = direct_response_resolution_audit()
    validation = {
        "source_v20_77_reproduced": abs(result["source_frontier"]["exact_f376_l2"] - 0.758671922543989) < 5.0e-12,
        "four_physical_directions": len(result["directions"]) == 4,
        "all_steps_measured": all(len(row["responses"]) == len(STEPS) for row in result["directions"]),
        "all_adjacent_pairs_compared": len(result["successive_scale_comparisons"]) == len(STEPS) - 1,
        "same_physics": not result["physical_equations_changed"] and not result["event_definition_changed"] and not result["acceptance_gate_changed"],
        "no_componentwise_gate": not result["componentwise_monotonicity_added"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_DIRECT_RESPONSE_RESOLUTION_AUDIT_V20_78", "version": VERSION,
        "classification": CLASSIFICATION, "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "direct_response_resolution_audit": result,
        "status": "VALIDATED" if passed else "INVALIDATED", "validation": validation, "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_DIRECT_RESPONSE_RESOLUTION_AUDIT_V20_78.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "direct_response_resolution_audit", "completion_payload", "materialize"]
