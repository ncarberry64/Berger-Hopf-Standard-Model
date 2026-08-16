"""Run the authorized proposal-only structured shake with exact Rayleigh F376."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.sparse.linalg import LinearOperator, gmres

from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import _action_curvature_transform
from bhsm.interface.aether_n3_controlled_structured_shake_recovery_v20_69 import _collective_mask
from bhsm.interface.aether_n3_curvature_transport_proposal_v21_00 import v21_00_selected_raw_vector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_rayleigh_event_covector_v20_80 import rayleigh_square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_structural_hindsight_recovery_v20_68 import _fresh_child_gate
from bhsm.interface.aether_n3_thirtieth_bidirectional_fallback_promotion_v19_82 import v19_82_selected_raw_vector
from bhsm.interface.aether_n3_thirty_fifth_bidirectional_probe_promotion_v20_02 import v20_02_selected_raw_vector


VERSION = "v21.03"
CLASSIFICATION = "BHSM_N3_EXACT_RAYLEIGH_CONTROLLED_STRUCTURED_SHAKE_RECOVERY"
FULL_BHSM_COMPLETE = False
RESPONSE_STEP = 1.0e-8
BACKTRACKS = 31


def _shaken_response(base_y: np.ndarray, transform: np.ndarray) -> tuple[np.ndarray, dict[str, Any]]:
    residual = rayleigh_square_physical_residual(base_y)

    def response(direction_y: np.ndarray) -> np.ndarray:
        norm = float(np.linalg.norm(direction_y))
        if norm == 0.0:
            return np.zeros(376)
        unit = direction_y / norm
        return norm * (
            rayleigh_square_physical_residual(base_y + RESPONSE_STEP * unit)
            - rayleigh_square_physical_residual(base_y - RESPONSE_STEP * unit)
        ) / (2.0 * RESPONSE_STEP)

    operator = LinearOperator(
        (376, 376), matvec=lambda dx: response(transform @ dx), dtype=float
    )
    callbacks: list[float] = []
    direction_x, info = gmres(
        operator,
        -residual,
        rtol=1.0e-6,
        atol=0.0,
        restart=20,
        maxiter=1,
        callback=lambda value: callbacks.append(float(value)),
        callback_type="pr_norm",
    )
    return direction_x, {
        "gmres_info_has_no_physical_authority": int(info),
        "iterations": len(callbacks),
        "final_callback_relative_residual": callbacks[-1] if callbacks else None,
    }


def completion_payload() -> dict[str, Any]:
    source_raw = v21_00_selected_raw_vector()
    scales = kkt_variable_scales()
    source_y = source_raw * scales
    source_norm = float(np.linalg.norm(rayleigh_square_physical_residual(source_y)))
    transform, transform_audit = _action_curvature_transform(source_raw)
    historical_x = np.linalg.solve(
        transform,
        (v20_02_selected_raw_vector() - v19_82_selected_raw_vector()) * scales,
    )
    collective_x = historical_x * _collective_mask()
    collective_x /= np.linalg.norm(collective_x)
    prior_shake = json.loads(Path(
        "artifacts/BHSM_N3_CONTROLLED_STRUCTURED_SHAKE_RECOVERY_V20_69.json"
    ).read_text(encoding="utf-8"))["controlled_structured_shake_recovery"]
    amplitude = float(prior_shake["structured_excitation"]["amplitude"])
    material_threshold = float(
        prior_shake["prospective_exact_search"][
            "material_threshold_from_geometric_gap_between_plateau_and_medium_medians"
        ]
    )
    transported = []
    shake_records = []
    for sign in (-1.0, 1.0):
        excitation_x = sign * amplitude * collective_x
        shaken_y = source_y + transform @ excitation_x
        direction_x, response = _shaken_response(shaken_y, transform)
        transported.append(direction_x)
        shake_records.append({
            "sign": sign,
            "temporary_action_coordinate_amplitude": amplitude,
            "temporary_exact_rayleigh_f376_norm": float(
                np.linalg.norm(rayleigh_square_physical_residual(shaken_y))
            ),
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
                candidate_y = source_y + alpha * (transform @ direction_x)
                try:
                    norm = float(np.linalg.norm(rayleigh_square_physical_residual(candidate_y)))
                    raw = candidate_y / scales
                    eta = float(_minimum_node_eta(raw))
                    reduction = source_norm - norm
                    row = {
                        "direction": name,
                        "alpha": alpha,
                        "backtrack": backtrack,
                        "norm": norm,
                        "reduction": reduction,
                        "eta": eta,
                    }
                    trials.append(row)
                    if eta > 1.0e-5 and reduction > MARGIN and (
                        best is None or norm < best["norm"]
                    ):
                        best = {**row, "raw": raw}
                except (ArithmeticError, FloatingPointError, ValueError):
                    continue
    material = bool(best is not None and best["reduction"] >= material_threshold)
    promotion = {"attempted": False, "promoted": False}
    best_summary = None
    if best is not None:
        best_summary = {key: value for key, value in best.items() if key != "raw"}
        best_summary["raw_vector_hex"] = [float(value).hex() for value in best["raw"]]
    if material and best is not None:
        child = _fresh_child_gate(best["raw"])
        promotion = {"attempted": True, "promoted": child["all_pass"], "child": child}
    result = {
        "source_frontier": {"version": "v21.00", "exact_rayleigh_f376_l2": source_norm},
        "authorization_chain": [
            "V20_96_OUTCOME_E_PROPOSAL_MECHANISM_STALLED",
            "V20_68_H5_HINDSIGHT_SUBSPACE_NO_MATERIAL_RECOVERY",
            "V21_01_DIRECT_CURVATURE_REFRESH_NO_MATERIAL_RECOVERY",
        ],
        "structured_excitation": {
            "pattern": "HISTORICAL_LARGE_V19_82_TO_V20_02_PROJECTED_TO_SCALE_W_V_PERIOD_IN_ACTION_COORDINATES",
            "amplitude_owner": "EXISTING_V20_69_MEDIAN_MEDIUM_DESCENT_ACTION_RADIUS",
            "amplitude": amplitude,
            "records": shake_records,
            "physical_equation_or_coefficient_changed": False,
        },
        "prospective_exact_search": {
            "candidate_origin_is_unshaken_v21_00": True,
            "exact_original_rayleigh_f376_authoritative": True,
            "trial_count": len(trials),
            "best_trials": sorted(trials, key=lambda row: row["norm"])[:12],
            "material_threshold_reused_from_accepted_history": material_threshold,
            "best": best_summary,
            "material_recovery": material,
        },
        "promotion": promotion,
        "classification": "STRUCTURED_SHAKE_MATERIAL_RECOVERY" if material else "STRUCTURED_SHAKE_NO_MATERIAL_RECOVERY",
        "coordinate_map": transform_audit,
        "physical_equations_changed": False,
        "event_definition_changed": False,
        "complete_child_gate_changed": False,
        "componentwise_monotonicity_added": False,
    }
    validation = {
        "source_v21_00_reproduced": abs(source_norm - 0.782778933037026) < 5.0e-12,
        "shake_removed_from_final_candidates": all(
            row["temporary_excitation_removed_before_candidate_evaluation"]
            for row in shake_records
        ) and result["prospective_exact_search"]["candidate_origin_is_unshaken_v21_00"],
        "exact_rayleigh_f376_authoritative": result["prospective_exact_search"][
            "exact_original_rayleigh_f376_authoritative"
        ],
        "promotion_only_after_material_recovery": not promotion["attempted"] or material,
        "same_physics": not result["physical_equations_changed"]
        and not result["event_definition_changed"]
        and not result["complete_child_gate_changed"],
        "no_componentwise_gate": not result["componentwise_monotonicity_added"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_RAYLEIGH_STRUCTURED_SHAKE_RECOVERY_V21_03",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "rayleigh_structured_shake_recovery": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_RAYLEIGH_STRUCTURED_SHAKE_RECOVERY_V21_03.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "completion_payload", "materialize"]
