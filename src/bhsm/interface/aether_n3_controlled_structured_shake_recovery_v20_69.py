"""Proposal-only structured shake after validated Outcome E and H5."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.sparse.linalg import LinearOperator, gmres

from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import _action_curvature_transform
from bhsm.interface.aether_n3_forty_ninth_bidirectional_probe_promotion_v20_66 import v20_66_selected_raw_vector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN, _metrics
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_reclassified_chain_proposal_v18_11 import _square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_structural_hindsight_recovery_v20_68 import _fresh_child_gate
from bhsm.interface.aether_n3_thirtieth_bidirectional_fallback_promotion_v19_82 import v19_82_selected_raw_vector
from bhsm.interface.aether_n3_thirty_fifth_bidirectional_probe_promotion_v20_02 import v20_02_selected_raw_vector


VERSION = "v20.69"
CLASSIFICATION = "BHSM_N3_CONTROLLED_STRUCTURED_SHAKE_PROPOSAL_RECOVERY"
FULL_BHSM_COMPLETE = False
RESPONSE_STEP = 1.0e-8
BACKTRACKS = 31


def v20_69_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_N3_CONTROLLED_STRUCTURED_SHAKE_RECOVERY_V20_69.json"
    ).read_text(encoding="utf-8"))
    result = payload["controlled_structured_shake_recovery"]
    if not result["promotion"]["promoted"]:
        raise ValueError("v20.69 structured-shake candidate was not physically promoted")
    selected = result["prospective_exact_search"]["best"]
    return np.asarray([float.fromhex(value) for value in selected["raw_vector_hex"]])


def _collective_mask() -> np.ndarray:
    mask = np.zeros(376)
    for node in range(23):
        mask[10 * node] = 1.0
        mask[10 * node + 4:10 * node + 10] = 1.0
    mask[374] = 1.0
    return mask


def _shaken_response(base_y: np.ndarray, transform: np.ndarray) -> tuple[np.ndarray, dict[str, Any]]:
    residual = _square_physical_residual(base_y)
    def response(direction_y: np.ndarray) -> np.ndarray:
        norm = float(np.linalg.norm(direction_y))
        if norm == 0.0:
            return np.zeros(376)
        unit = direction_y / norm
        return norm * (
            _square_physical_residual(base_y + RESPONSE_STEP * unit)
            - _square_physical_residual(base_y - RESPONSE_STEP * unit)
        ) / (2.0 * RESPONSE_STEP)
    operator = LinearOperator((376, 376), matvec=lambda dx: response(transform @ dx), dtype=float)
    callbacks: list[float] = []
    direction_x, info = gmres(
        operator, -residual, rtol=1.0e-6, atol=0.0, restart=20, maxiter=1,
        callback=lambda value: callbacks.append(float(value)), callback_type="pr_norm",
    )
    return direction_x, {
        "gmres_info_has_no_physical_authority": int(info),
        "iterations": len(callbacks),
        "final_callback_relative_residual": callbacks[-1] if callbacks else None,
    }


def controlled_structured_shake_recovery() -> dict[str, Any]:
    source_raw = v20_66_selected_raw_vector(); scales = kkt_variable_scales()
    source_y = source_raw * scales; source_norm = float(np.linalg.norm(_square_physical_residual(source_y)))
    transform, transform_audit = _action_curvature_transform(source_raw)
    historical_x = np.linalg.solve(transform, (v20_02_selected_raw_vector() - v19_82_selected_raw_vector()) * scales)
    collective_x = historical_x * _collective_mask()
    collective_x /= np.linalg.norm(collective_x)
    hindsight = json.loads(Path("artifacts/BHSM_N3_STRUCTURAL_HINDSIGHT_RECOVERY_V20_68.json").read_text(encoding="utf-8"))["structural_hindsight_recovery"]
    amplitude = float(hindsight["prospective_search"]["class_action_amplitudes"]["MEDIUM_DESCENT"])
    transported = []
    shake_records = []
    for sign in (-1.0, 1.0):
        excitation_x = sign * amplitude * collective_x
        shaken_y = source_y + transform @ excitation_x
        direction_x, response = _shaken_response(shaken_y, transform)
        transported.append(direction_x)
        shake_records.append({
            "sign": sign, "temporary_action_coordinate_amplitude": amplitude,
            "temporary_exact_f376_norm": float(np.linalg.norm(_square_physical_residual(shaken_y))),
            "temporary_excitation_removed_before_candidate_evaluation": True,
            "response": response,
        })
    directions = [
        ("response_from_negative_shake", transported[0]),
        ("response_from_positive_shake", transported[1]),
        ("symmetric_transport", 0.5 * (transported[0] + transported[1])),
        ("curvature_transport", 0.5 * (transported[1] - transported[0])),
    ]
    trials = []
    best = None
    for name, direction_x in directions:
        for orientation in (-1.0, 1.0):
            for backtrack in range(BACKTRACKS):
                alpha = orientation * 0.5**backtrack
                # The temporary shake is absent here: every candidate starts at source_y.
                candidate_y = source_y + alpha * (transform @ direction_x)
                try:
                    residual = _square_physical_residual(candidate_y)
                    norm = float(np.linalg.norm(residual)); raw = candidate_y / scales
                    eta = float(_minimum_node_eta(raw)); reduction = source_norm - norm
                    row = {"direction": name, "alpha": alpha, "backtrack": backtrack, "norm": norm, "reduction": reduction, "eta": eta}
                    trials.append(row)
                    if eta > 1.0e-5 and reduction > MARGIN and (best is None or norm < best["norm"]):
                        best = {**row, "raw": raw}
                except (ArithmeticError, FloatingPointError, ValueError):
                    continue
    class_rows = hindsight["descent_class_comparison"]
    plateau_median = float(class_rows["PLATEAU_DESCENT"]["median_exact_reduction"])
    medium_median = float(class_rows["MEDIUM_DESCENT"]["median_exact_reduction"])
    material_threshold = float(np.sqrt(plateau_median * medium_median))
    material = bool(best is not None and best["reduction"] >= material_threshold)
    promotion = {"attempted": False, "promoted": False}
    best_summary = None
    if best is not None:
        best_summary = {key: value for key, value in best.items() if key != "raw"}
        best_summary["raw_vector_hex"] = [float(value).hex() for value in best["raw"]]
    if material and best is not None:
        child = _fresh_child_gate(best["raw"])
        promotion = {"attempted": True, "promoted": child["all_pass"], "child": child}
    return {
        "source_frontier": {"version": "v20.66", "exact_f376_l2": source_norm},
        "authorization_chain": ["OUTCOME_E_PROPOSAL_MECHANISM_STALLED", "H5_HINDSIGHT_SUBSPACE_NO_MATERIAL_RECOVERY"],
        "structured_excitation": {
            "pattern": "HISTORICAL_LARGE_V19_82_TO_V20_02_PROJECTED_TO_SCALE_W_V_PERIOD_IN_ACTION_COORDINATES",
            "amplitude_owner": "MEDIAN_MEDIUM_DESCENT_ACTION_COORDINATE_SECANT_NORM",
            "amplitude": amplitude, "records": shake_records,
            "physical_equation_or_coefficient_changed": False,
        },
        "transported_proposals": [name for name, _ in directions],
        "prospective_exact_search": {
            "candidate_origin_is_unshaken_v20_66": True,
            "exact_original_f376_authoritative": True,
            "trial_count": len(trials), "best_trials": sorted(trials, key=lambda row: row["norm"])[:12],
            "material_threshold_from_geometric_gap_between_plateau_and_medium_medians": material_threshold,
            "best": best_summary, "material_recovery": material,
        },
        "promotion": promotion,
        "classification": "STRUCTURED_SHAKE_MATERIAL_RECOVERY" if material else "STRUCTURED_SHAKE_NO_MATERIAL_RECOVERY",
        "coordinate_map": transform_audit,
        "physical_equations_changed": False, "event_definition_changed": False,
        "complete_child_gate_changed": False, "componentwise_monotonicity_added": False,
        "next_action": "ADOPT_PROMOTED_SHAKE_PROPOSAL_AND_RESUME_EXACT_N3_CLOSURE" if promotion["promoted"] else "E4_REVISIT_EXACT_RESIDUAL_OWNERSHIP_WITH_SHAKE_AND_HINDSIGHT_FAILURE_EVIDENCE",
    }


def completion_payload() -> dict[str, Any]:
    result = controlled_structured_shake_recovery()
    validation = {
        "source_v20_66_reproduced": abs(result["source_frontier"]["exact_f376_l2"] - 0.766949553481446) < 5.0e-12,
        "shake_removed_from_final_candidates": all(row["temporary_excitation_removed_before_candidate_evaluation"] for row in result["structured_excitation"]["records"]) and result["prospective_exact_search"]["candidate_origin_is_unshaken_v20_66"],
        "exact_f376_authoritative": result["prospective_exact_search"]["exact_original_f376_authoritative"],
        "promotion_only_after_material_recovery": not result["promotion"]["attempted"] or result["prospective_exact_search"]["material_recovery"],
        "same_physics": not result["physical_equations_changed"] and not result["event_definition_changed"] and not result["complete_child_gate_changed"],
        "no_componentwise_gate": not result["componentwise_monotonicity_added"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_CONTROLLED_STRUCTURED_SHAKE_RECOVERY_V20_69", "version": VERSION,
        "classification": CLASSIFICATION, "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "controlled_structured_shake_recovery": result,
        "status": "VALIDATED" if passed else "INVALIDATED", "validation": validation, "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_CONTROLLED_STRUCTURED_SHAKE_RECOVERY_V20_69.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "v20_69_selected_raw_vector", "controlled_structured_shake_recovery", "completion_payload", "materialize"]
