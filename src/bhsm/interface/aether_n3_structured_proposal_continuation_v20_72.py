"""Resume exact N=3 continuation from promoted v20.71 using the recovered proposal mechanism."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import _action_curvature_transform
from bhsm.interface.aether_n3_controlled_structured_shake_recovery_v20_69 import (
    _collective_mask,
    _shaken_response,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_reclassified_chain_proposal_v18_11 import _square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_structural_hindsight_recovery_v20_68 import _fresh_child_gate
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_71 import v20_71_selected_raw_vector
from bhsm.interface.aether_n3_thirtieth_bidirectional_fallback_promotion_v19_82 import v19_82_selected_raw_vector
from bhsm.interface.aether_n3_thirty_fifth_bidirectional_probe_promotion_v20_02 import v20_02_selected_raw_vector


VERSION = "v20.72"
CLASSIFICATION = "BHSM_N3_STRUCTURED_PROPOSAL_EXACT_CONTINUATION"
FULL_BHSM_COMPLETE = False
BACKTRACKS = 31


def v20_72_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_N3_STRUCTURED_PROPOSAL_CONTINUATION_V20_72.json"
    ).read_text(encoding="utf-8"))
    result = payload["structured_proposal_continuation"]
    if not result["promotion"]["promoted"]:
        raise ValueError("v20.72 candidate was not physically promoted")
    return np.asarray([
        float.fromhex(value)
        for value in result["exact_line_search"]["best"]["raw_vector_hex"]
    ])


def structured_proposal_continuation() -> dict[str, Any]:
    source_raw = v20_71_selected_raw_vector()
    scales = kkt_variable_scales()
    source_y = source_raw * scales
    source_norm = float(np.linalg.norm(_square_physical_residual(source_y)))
    transform, transform_audit = _action_curvature_transform(source_raw)
    historical_x = np.linalg.solve(
        transform,
        (v20_02_selected_raw_vector() - v19_82_selected_raw_vector()) * scales,
    )
    collective_x = historical_x * _collective_mask()
    collective_x /= np.linalg.norm(collective_x)
    hindsight = json.loads(Path(
        "artifacts/BHSM_N3_STRUCTURAL_HINDSIGHT_RECOVERY_V20_68.json"
    ).read_text(encoding="utf-8"))["structural_hindsight_recovery"]
    amplitude = float(
        hindsight["prospective_search"]["class_action_amplitudes"]["MEDIUM_DESCENT"]
    )
    temporary_y = source_y + transform @ (amplitude * collective_x)
    direction_x, response = _shaken_response(temporary_y, transform)
    trials = []
    best = None
    for orientation in (-1.0, 1.0):
        for backtrack in range(BACKTRACKS):
            alpha = orientation * 0.5**backtrack
            # The temporary excitation is absent: this starts at the exact v20.71 state.
            candidate_y = source_y + alpha * (transform @ direction_x)
            try:
                candidate_raw = candidate_y / scales
                residual = _square_physical_residual(candidate_y)
                norm = float(np.linalg.norm(residual))
                eta = float(_minimum_node_eta(candidate_raw))
                reduction = source_norm - norm
                row = {
                    "orientation": "negative" if orientation < 0.0 else "positive",
                    "alpha": alpha,
                    "backtrack": backtrack,
                    "exact_f376_l2": norm,
                    "exact_reduction": reduction,
                    "eta_minimum": eta,
                }
                trials.append(row)
                if eta > 1.0e-5 and reduction > MARGIN and (
                    best is None or norm < best["exact_f376_l2"]
                ):
                    best = {**row, "raw": candidate_raw}
            except (ArithmeticError, FloatingPointError, ValueError):
                continue
    best_summary = None
    promotion = {"attempted": False, "promoted": False}
    if best is not None:
        best_summary = {key: value for key, value in best.items() if key != "raw"}
        best_summary["raw_vector_hex"] = [float(value).hex() for value in best["raw"]]
        child = _fresh_child_gate(best["raw"])
        promotion = {"attempted": True, "promoted": child["all_pass"], "child": child}
    return {
        "source_frontier": {"version": "v20.71", "exact_f376_l2": source_norm},
        "proposal": {
            "mechanism": "POSITIVE_HISTORICAL_SCALE_W_V_PERIOD_SHAKE_RESPONSE_TRANSPORT",
            "temporary_action_coordinate_amplitude": amplitude,
            "temporary_exact_f376_l2": float(np.linalg.norm(_square_physical_residual(temporary_y))),
            "temporary_excitation_removed_before_all_candidate_evaluations": True,
            "response": response,
            "coordinate_map": transform_audit,
            "solver_interpretation_has_no_physical_authority": True,
        },
        "exact_line_search": {
            "both_orientations_scanned": True,
            "original_unweighted_f376_authoritative": True,
            "valid_trial_count": len(trials),
            "best_trials": sorted(trials, key=lambda row: row["exact_f376_l2"])[:12],
            "best": best_summary,
        },
        "promotion": promotion,
        "physical_equations_changed": False,
        "event_definition_changed": False,
        "complete_child_gate_changed": False,
        "componentwise_monotonicity_added": False,
        "status": "PROMOTED" if promotion["promoted"] else "NOT_PROMOTED",
        "next_action": (
            "CONTINUE_EXACT_N3_CLOSURE_FROM_V20_72"
            if promotion["promoted"]
            else "REVISIT_EXACT_RESIDUAL_OWNERSHIP_AT_V20_71"
        ),
    }


def completion_payload() -> dict[str, Any]:
    result = structured_proposal_continuation()
    best = result["exact_line_search"]["best"]
    validation = {
        "source_v20_71_reproduced": abs(
            result["source_frontier"]["exact_f376_l2"] - 0.761073299983252
        ) < 5.0e-12,
        "shake_removed": result["proposal"]["temporary_excitation_removed_before_all_candidate_evaluations"],
        "exact_unweighted_f376_decides": result["exact_line_search"]["original_unweighted_f376_authoritative"],
        "both_orientations_scanned": result["exact_line_search"]["both_orientations_scanned"],
        "candidate_classified": best is not None or result["exact_line_search"]["valid_trial_count"] > 0,
        "promotion_only_after_exact_descent": not result["promotion"]["attempted"] or best["exact_reduction"] > 0.0,
        "promotion_only_after_child_gate": not result["promotion"]["promoted"] or result["promotion"]["child"]["all_pass"],
        "same_physics": not result["physical_equations_changed"] and not result["event_definition_changed"] and not result["complete_child_gate_changed"],
        "no_componentwise_gate": not result["componentwise_monotonicity_added"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_STRUCTURED_PROPOSAL_CONTINUATION_V20_72",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "structured_proposal_continuation": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_STRUCTURED_PROPOSAL_CONTINUATION_V20_72.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "v20_72_selected_raw_vector", "structured_proposal_continuation",
    "completion_payload", "materialize",
]
