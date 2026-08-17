"""One bounded square-KKT proposal using the validated Rayleigh event covector."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from scipy.sparse.linalg import LinearOperator, gmres

from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import _action_curvature_transform
from bhsm.interface.aether_n3_exact_action_hessian_assembly_v18_18 import exact_sbp_action_hessian
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_post_recovery_multisecant_proposal_v20_77 import v20_77_selected_raw_vector
from bhsm.interface.aether_n3_rayleigh_event_covector_v20_80 import (
    rayleigh_project_event_multiplier, rayleigh_sbp_event_covector,
    rayleigh_square_physical_residual,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_structural_hindsight_recovery_v20_68 import _fresh_child_gate
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_72 import v20_72_selected_raw_vector
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_73 import v20_73_selected_raw_vector
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_75 import v20_75_selected_raw_vector


VERSION = "v20.81"
CLASSIFICATION = "BHSM_N3_RAYLEIGH_EVENT_SQUARE_KKT_PROPOSAL"
FULL_BHSM_COMPLETE = False
RESPONSE_STEP = 3.0e-8
COARSE_RESPONSE_STEP = 1.0e-7
BACKTRACKS = 18


def v20_81_selected_raw_vector() -> np.ndarray:
    import json
    payload = json.loads(Path(
        "artifacts/BHSM_N3_RAYLEIGH_SQUARE_KKT_PROPOSAL_V20_81.json"
    ).read_text(encoding="utf-8"))["rayleigh_square_kkt_proposal"]
    if not payload["promotion"]["promoted"]:
        raise ValueError("v20.81 has no physically promoted state")
    return np.asarray([float.fromhex(value) for value in payload["exact_line_search"]["best"]["raw_vector_hex"]])


def _event_gradient_scaled(ybase: np.ndarray, scales: np.ndarray) -> np.ndarray:
    return rayleigh_sbp_event_covector(ybase / scales[:-1]) / scales[:-1] / scales[-1]


def _response(
    direction: np.ndarray, step: float, y: np.ndarray, scales: np.ndarray,
    action_hessian: np.ndarray, event_gradient: np.ndarray,
) -> np.ndarray:
    norm = float(np.linalg.norm(direction))
    if norm == 0.0:
        return np.zeros(376)
    unit = direction / norm
    event_response = norm * (
        _event_gradient_scaled(y[:-1] + step * unit[:-1], scales)
        - _event_gradient_scaled(y[:-1] - step * unit[:-1], scales)
    ) / (2.0 * step)
    result = np.empty(376)
    result[:-1] = action_hessian @ direction[:-1] + y[-1] * event_response + direction[-1] * event_gradient
    result[-1] = float(event_gradient @ direction[:-1])
    return result


def rayleigh_square_kkt_proposal(
    source_raw_override: np.ndarray | None = None, *, source_label: str = "v20.77",
    krylov_restart: int = 12, child_fallback_limit: int = 1,
) -> dict[str, Any]:
    scales = kkt_variable_scales()
    source_raw = (
        rayleigh_project_event_multiplier(v20_77_selected_raw_vector())
        if source_raw_override is None else np.asarray(source_raw_override, dtype=float)
    )
    source_y = source_raw * scales; residual = rayleigh_square_physical_residual(source_y)
    source_norm = float(np.linalg.norm(residual))
    assembled = exact_sbp_action_hessian(source_raw[:-1]); action_raw = np.asarray(assembled.pop("hessian"))
    inverse = 1.0 / scales[:-1]
    action_hessian = inverse[:, None] * action_raw * inverse[None, :]
    event_gradient = _event_gradient_scaled(source_y[:-1], scales)
    transform, transform_audit = _action_curvature_transform(source_raw)
    directions = {
        "corrected_physical_residual": residual,
        "latest_accepted_secant": (source_raw - v20_75_selected_raw_vector()) * scales,
        "material_corridor_secant": (v20_73_selected_raw_vector() - v20_72_selected_raw_vector()) * scales,
    }
    response_checks = []
    for name, direction in directions.items():
        fine = _response(direction, RESPONSE_STEP, source_y, scales, action_hessian, event_gradient)
        coarse = _response(direction, COARSE_RESPONSE_STEP, source_y, scales, action_hessian, event_gradient)
        response_checks.append({
            "direction": name, "fine_step": RESPONSE_STEP, "coarse_step": COARSE_RESPONSE_STEP,
            "fine_response_l2": float(np.linalg.norm(fine)),
            "coarse_to_fine_relative_change": float(np.linalg.norm(fine - coarse) / max(1.0, np.linalg.norm(fine))),
        })
    response_resolved = all(row["coarse_to_fine_relative_change"] < 2.0e-2 for row in response_checks)
    callbacks: list[float] = []
    direction_y = np.zeros(376); info = -99
    if response_resolved:
        operator = LinearOperator(
            (376, 376),
            matvec=lambda dx: _response(transform @ dx, RESPONSE_STEP, source_y, scales, action_hessian, event_gradient),
            dtype=float,
        )
        direction_x, info = gmres(
            operator, -residual, rtol=1.0e-4, atol=0.0, restart=krylov_restart, maxiter=1,
            callback=lambda value: callbacks.append(float(value)), callback_type="pr_norm",
        )
        direction_y = transform @ direction_x
    trials = []; best = None; eligible = []
    if response_resolved and np.linalg.norm(direction_y) > 0.0:
        for orientation in (-1.0, 1.0):
            for backtrack in range(BACKTRACKS):
                alpha = orientation * 0.5**backtrack
                candidate_y = source_y + alpha * direction_y
                try:
                    raw = candidate_y / scales; candidate_residual = rayleigh_square_physical_residual(candidate_y)
                    norm = float(np.linalg.norm(candidate_residual)); eta = float(_minimum_node_eta(raw))
                    row = {"orientation": "negative" if orientation < 0.0 else "positive", "alpha": alpha,
                           "backtrack": backtrack, "exact_rayleigh_f376_l2": norm,
                           "exact_reduction": source_norm - norm, "eta_minimum": eta}
                    trials.append(row)
                    if eta > 1.0e-5 and row["exact_reduction"] > MARGIN:
                        eligible.append({**row, "raw": raw})
                        if best is None or norm < best["exact_rayleigh_f376_l2"]:
                            best = eligible[-1]
                except (ArithmeticError, FloatingPointError, ValueError):
                    continue
    best_summary = None; promotion = {"attempted": False, "promoted": False}
    if best is not None:
        if child_fallback_limit == 1:
            best_summary = {key: value for key, value in best.items() if key != "raw"}
            best_summary["raw_vector_hex"] = [float(value).hex() for value in best["raw"]]
            child = _fresh_child_gate(best["raw"])
            promotion = {"attempted": True, "promoted": child["all_pass"], "child": child}
        else:
            selected = None; attempts = []
            for candidate in sorted(eligible, key=lambda row: row["exact_rayleigh_f376_l2"])[:child_fallback_limit]:
                child = _fresh_child_gate(candidate["raw"])
                attempts.append({
                    "alpha": candidate["alpha"], "exact_rayleigh_f376_l2": candidate["exact_rayleigh_f376_l2"],
                    "all_pass": child["all_pass"], "flux_envelope": child["flux_envelope"],
                })
                if child["all_pass"]:
                    selected = candidate
                    break
            if selected is not None:
                best = selected
            best_summary = {key: value for key, value in best.items() if key != "raw"}
            best_summary["raw_vector_hex"] = [float(value).hex() for value in best["raw"]]
            promotion = {"attempted": True, "promoted": selected is not None,
                         "child": child, "child_attempts": attempts}
    return {
        "source": {"geometry": source_label, "event_multiplier_rayleigh_reprojected": source_raw_override is None, "exact_rayleigh_f376_l2": source_norm},
        "response": {"method": "EXACT_ACTION_HESSIAN_PLUS_RAYLEIGH_EVENT_COVECTOR_DIRECTIONAL_RESPONSE",
                     "checks": response_checks, "resolved": response_resolved,
                     "gmres_info_has_no_physical_authority": int(info), "iterations": len(callbacks),
                     **({"krylov_restart_numerical_control": krylov_restart} if krylov_restart != 12 else {}),
                     "final_callback_relative_residual": callbacks[-1] if callbacks else None,
                     "proposal_direction_scaled_l2": float(np.linalg.norm(direction_y)),
                     "coordinate_map": transform_audit},
        "exact_line_search": {"both_orientations": True, "trial_count": len(trials),
                              "best_trials": sorted(trials, key=lambda row: row["exact_rayleigh_f376_l2"])[:10],
                              "best": best_summary, "original_unweighted_376_rows_authoritative": True},
        "promotion": promotion,
        "outcome": "RAYLEIGH_SQUARE_KKT_DESCENT_PROMOTED" if promotion["promoted"] else (
            "RAYLEIGH_SQUARE_KKT_DESCENT_PENDING_CHILD" if best is not None else
            "RAYLEIGH_SQUARE_KKT_PROPOSAL_NO_DESCENT" if response_resolved else "RAYLEIGH_RESPONSE_UNRESOLVED"
        ),
        "next_action": "CONTINUE_RAYLEIGH_EXACT_N3_CLOSURE" if promotion["promoted"] else "AUDIT_THE_FIRST_FAILED_RAYLEIGH_RESPONSE_OR_PHYSICAL_GATE",
        "physical_equations_changed": False, "event_definition_changed": False,
        "numerical_event_derivative_corrected": True, "acceptance_gate_changed": False,
        "componentwise_monotonicity_added": False,
    }


def completion_payload() -> dict[str, Any]:
    result = rayleigh_square_kkt_proposal(); best = result["exact_line_search"]["best"]
    validation = {
        "source_reproduced": abs(result["source"]["exact_rayleigh_f376_l2"] - 0.798607212645983) < 5.0e-12,
        "response_resolved": result["response"]["resolved"],
        "exact_rows_decide": result["exact_line_search"]["original_unweighted_376_rows_authoritative"],
        "both_orientations": result["exact_line_search"]["both_orientations"],
        "candidate_reduces_merit": best is None or best["exact_reduction"] > 0.0,
        "promotion_requires_child": not result["promotion"]["promoted"] or result["promotion"]["child"]["all_pass"],
        "same_physics": not result["physical_equations_changed"] and not result["event_definition_changed"] and not result["acceptance_gate_changed"],
        "no_componentwise_gate": not result["componentwise_monotonicity_added"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_RAYLEIGH_SQUARE_KKT_PROPOSAL_V20_81", "version": VERSION,
        "classification": CLASSIFICATION, "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "rayleigh_square_kkt_proposal": result, "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation, "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_RAYLEIGH_SQUARE_KKT_PROPOSAL_V20_81.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "v20_81_selected_raw_vector", "rayleigh_square_kkt_proposal", "completion_payload", "materialize"]
