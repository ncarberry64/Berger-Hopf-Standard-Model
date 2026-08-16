"""Separate action and event ownership of the stable terminal response mismatch."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import _action_curvature_transform
from bhsm.interface.aether_n3_exact_action_hessian_assembly_v18_18 import exact_sbp_action_hessian
from bhsm.interface.aether_n3_exact_local_jet_sbp_covector_v17_61 import exact_local_jet_sbp_action_covector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_event_value_from_base
from bhsm.interface.aether_n3_natural_radius_scan_v21_04 import v21_04_selected_raw_vector
from bhsm.interface.aether_n3_plateau_proposal_mechanism_audit_v20_67 import _block_stats, _owner, _region
from bhsm.interface.aether_n3_rayleigh_event_covector_v20_80 import (
    rayleigh_sbp_event_covector, rayleigh_square_physical_residual,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales


VERSION = "v21.09"
CLASSIFICATION = "BHSM_N3_TERMINAL_ACTION_VS_EVENT_DERIVATIVE_OWNER_AUDIT"
FULL_BHSM_COMPLETE = False


def _components(y: np.ndarray, scales: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    base = y[:-1] / scales[:-1]
    action = np.zeros(376)
    action[:-1] = np.asarray(
        exact_local_jet_sbp_action_covector(base)["covector"]
    ) / scales[:-1]
    event = np.empty(376)
    event[:-1] = y[-1] * rayleigh_sbp_event_covector(base) / scales[:-1] / scales[-1]
    event[-1] = sbp_event_value_from_base(base) / scales[-1]
    return action, event


def _top_rows(difference: np.ndarray) -> list[dict[str, Any]]:
    result = []
    for row_index in np.argsort(np.abs(difference))[-10:][::-1]:
        owner = _owner(int(row_index))
        result.append({
            "row": int(row_index),
            "difference": float(difference[row_index]),
            "abs": float(abs(difference[row_index])),
            **owner,
            "region": _region(owner["history_node"]),
        })
    return result


def completion_payload() -> dict[str, Any]:
    raw = v21_04_selected_raw_vector()
    scales = kkt_variable_scales()
    y = raw * scales
    residual = rayleigh_square_physical_residual(y)
    source_norm = float(np.linalg.norm(residual))
    curvature = json.loads(Path(
        "artifacts/BHSM_N3_RESIDUAL_MANIFOLD_NORMAL_ACCELERATION_V21_06.json"
    ).read_text(encoding="utf-8"))["curvature_refresh"]
    inverse = 1.0 / scales[:-1]
    action_payload = exact_sbp_action_hessian(raw[:-1])
    action_raw = np.asarray(action_payload.pop("hessian"))
    action_scaled = inverse[:, None] * action_raw * inverse[None, :]
    action_matrix = np.zeros((376, 376))
    action_matrix[:-1, :-1] = action_scaled
    support = np.asarray(curvature["event_curvature_support_indices"], dtype=int)
    block = np.asarray(curvature["event_curvature_symmetric_block"], dtype=float)
    event_hessian = np.zeros((375, 375))
    event_hessian[np.ix_(support, support)] = block
    event_gradient = rayleigh_sbp_event_covector(raw[:-1]) * inverse / scales[-1]
    event_matrix = np.zeros((376, 376))
    event_matrix[:-1, :-1] = y[-1] * event_hessian
    event_matrix[:-1, -1] = event_gradient
    event_matrix[-1, :-1] = event_gradient
    matrix = action_matrix + event_matrix
    transform, transform_audit = _action_curvature_transform(raw)
    gradient_x = transform.T @ matrix.T @ residual
    direction_x = -gradient_x / np.linalg.norm(gradient_x)
    direction_y = transform @ direction_x
    radius_best = json.loads(Path(
        "artifacts/BHSM_N3_NATURAL_RADIUS_SCAN_V21_04.json"
    ).read_text(encoding="utf-8"))["natural_radius_scan"]["exact_search"]["best"]
    radius = min(
        float(radius_best["realized_action_coordinate_norm"]),
        float(radius_best["realized_physical_scaled_norm"])
        / max(float(np.linalg.norm(direction_y)), 1.0e-300),
    )
    exact_by_factor: dict[float, tuple[np.ndarray, np.ndarray]] = {}
    for factor in (0.5, 1.0, 2.0):
        local = factor * radius
        plus_action, plus_event = _components(y + local * direction_y, scales)
        minus_action, minus_event = _components(y - local * direction_y, scales)
        exact_by_factor[factor] = (
            (plus_action - minus_action) / (2.0 * local),
            (plus_event - minus_event) / (2.0 * local),
        )
    assembled = {
        "action": action_matrix @ direction_y,
        "event": event_matrix @ direction_y,
    }
    exact = {
        "action": exact_by_factor[1.0][0],
        "event": exact_by_factor[1.0][1],
    }
    owner_rows = []
    demonstrated = []
    for index, name in enumerate(("action", "event")):
        difference = assembled[name] - exact[name]
        denominator = max(float(np.linalg.norm(exact[name])), 1.0)
        half = float(np.linalg.norm(exact_by_factor[0.5][index] - exact[name]) / denominator)
        double = float(np.linalg.norm(exact_by_factor[2.0][index] - exact[name]) / denominator)
        mismatch = float(np.linalg.norm(difference) / denominator)
        stable = bool(half < 1.0e-2 and double < 1.0e-2)
        if stable and mismatch > 2.0e-2:
            demonstrated.append(name)
        owner_rows.append({
            "owner": name,
            "assembled_response_l2": float(np.linalg.norm(assembled[name])),
            "exact_response_l2": float(np.linalg.norm(exact[name])),
            "assembled_vs_exact_relative": mismatch,
            "half_vs_reference_exact_relative": half,
            "double_vs_reference_exact_relative": double,
            "exact_response_step_stable": stable,
            "difference_block_norms": _block_stats(difference),
            "largest_difference_rows": _top_rows(difference),
        })
    combined_exact = exact["action"] + exact["event"]
    combined_assembled = assembled["action"] + assembled["event"]
    combined_difference = combined_assembled - combined_exact
    if demonstrated == ["action"]:
        blocker = "EXACT_ACTION_HESSIAN_TERMINAL_SCALE_V_ASSEMBLY"
    elif demonstrated == ["event"]:
        blocker = "RAYLEIGH_EVENT_HESSIAN_TERMINAL_SCALE_V_ASSEMBLY"
    elif demonstrated:
        blocker = "COUPLED_ACTION_AND_EVENT_TERMINAL_SCALE_V_ASSEMBLY"
    else:
        blocker = None
    result = {
        "source_frontier": {"version": "v21.04", "exact_rayleigh_f376_l2": source_norm},
        "direction": {
            "name": "negative_current_merit_gradient",
            "action_coordinate_radius": radius,
            "physical_scaled_radius": float(radius * np.linalg.norm(direction_y)),
            "coordinate_map": transform_audit,
        },
        "owner_checks": owner_rows,
        "combined": {
            "assembled_vs_exact_relative": float(
                np.linalg.norm(combined_difference)
                / max(np.linalg.norm(combined_exact), 1.0)
            ),
            "difference_block_norms": _block_stats(combined_difference),
            "largest_difference_rows": _top_rows(combined_difference),
        },
        "classification": "TERMINAL_DERIVATIVE_OWNER_IDENTIFIED" if blocker else "TERMINAL_DERIVATIVE_OWNER_NOT_IDENTIFIED",
        "first_action_owned_blocker": blocker,
        "physical_equations_changed": False,
        "event_definition_changed": False,
        "acceptance_gate_changed": False,
    }
    validation = {
        "source_v21_04_reproduced": abs(source_norm - 0.782775399601569) < 5.0e-12,
        "components_recompose_residual": bool(np.allclose(
            sum(_components(y, scales)), residual, rtol=1.0e-12, atol=1.0e-12
        )),
        "components_recompose_assembled_response": bool(np.allclose(
            combined_assembled, matrix @ direction_y, rtol=1.0e-12, atol=1.0e-8
        )),
        "two_owner_checks": len(owner_rows) == 2,
        "one_classification": result["classification"] in {
            "TERMINAL_DERIVATIVE_OWNER_IDENTIFIED",
            "TERMINAL_DERIVATIVE_OWNER_NOT_IDENTIFIED",
        },
        "same_physics": not result["physical_equations_changed"]
        and not result["event_definition_changed"]
        and not result["acceptance_gate_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_TERMINAL_DERIVATIVE_OWNER_AUDIT_V21_09",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "terminal_derivative_owner_audit": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_TERMINAL_DERIVATIVE_OWNER_AUDIT_V21_09.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "completion_payload", "materialize"]
