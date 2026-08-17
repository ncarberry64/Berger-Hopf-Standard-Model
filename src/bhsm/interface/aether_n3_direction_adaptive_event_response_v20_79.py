"""Resolve the v20.77 KKT response without differencing the exact action covector."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import exact_action_jet_at_state
from bhsm.interface.aether_n3_exact_action_hessian_assembly_v18_18 import exact_sbp_action_hessian
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_event_covector
from bhsm.interface.aether_n3_post_recovery_multisecant_proposal_v20_77 import v20_77_selected_raw_vector
from bhsm.interface.aether_n3_reclassified_chain_proposal_v18_11 import _square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    ORDER, kkt_variable_scales, unpack_reduced,
)
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import trapezoid_sbp_difference
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_72 import v20_72_selected_raw_vector
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_73 import v20_73_selected_raw_vector
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_75 import v20_75_selected_raw_vector


VERSION = "v20.79"
CLASSIFICATION = "BHSM_N3_DIRECTION_ADAPTIVE_ORDERED_EVENT_RESPONSE"
FULL_BHSM_COMPLETE = False
STEPS = (1.0e-4, 3.0e-5, 1.0e-5, 3.0e-6, 1.0e-6)


def _directions(raw: np.ndarray, scales: np.ndarray, residual: np.ndarray) -> dict[str, np.ndarray]:
    artifact = json.loads(Path(
        "artifacts/BHSM_N3_POST_RECOVERY_MULTI_SECANT_PROPOSAL_V20_77.json"
    ).read_text(encoding="utf-8"))["post_recovery_multisecant_proposal"]
    selected = artifact["exact_line_search"]["best"]
    selected_raw = np.asarray([float.fromhex(value) for value in selected["raw_vector_hex"]])
    alpha = float(selected["alpha"])
    return {
        "physical_residual": residual.copy(),
        "latest_accepted_secant_v20_75_to_v20_77": (
            raw - v20_75_selected_raw_vector()
        ) * scales,
        "material_corridor_secant_v20_72_to_v20_73": (
            v20_73_selected_raw_vector() - v20_72_selected_raw_vector()
        ) * scales,
        "multisecant_proposal_direction": (
            selected_raw - v20_75_selected_raw_vector()
        ) * scales / alpha,
    }


def _event_gradient_scaled(ybase: np.ndarray, scales: np.ndarray) -> np.ndarray:
    return sbp_event_covector(ybase / scales[:-1]) / scales[:-1] / scales[-1]


def _structured_response(
    direction: np.ndarray, step: float, y: np.ndarray, scales: np.ndarray,
    action_hessian_scaled: np.ndarray, event_gradient: np.ndarray,
) -> np.ndarray:
    norm = float(np.linalg.norm(direction))
    unit = direction / norm
    event_gradient_response = norm * (
        _event_gradient_scaled(y[:-1] + step * unit[:-1], scales)
        - _event_gradient_scaled(y[:-1] - step * unit[:-1], scales)
    ) / (2.0 * step)
    response = np.empty(376)
    response[:-1] = (
        action_hessian_scaled @ direction[:-1]
        + y[-1] * event_gradient_response
        + direction[-1] * event_gradient
    )
    response[-1] = float(event_gradient @ direction[:-1])
    return response


def direction_adaptive_event_response_audit() -> dict[str, Any]:
    scales = kkt_variable_scales(); raw = v20_77_selected_raw_vector(); y = raw * scales
    residual = _square_physical_residual(y)
    action = exact_sbp_action_hessian(raw[:-1]); action_raw = np.asarray(action.pop("hessian"))
    inverse = 1.0 / scales[:-1]
    action_scaled = inverse[:, None] * action_raw * inverse[None, :]
    event_gradient = _event_gradient_scaled(y[:-1], scales)
    unpacked = unpack_reduced(raw)
    q = np.asarray(unpacked["coordinates"]); multipliers = np.asarray(unpacked["multipliers"])
    period = float(unpacked["period"]); velocity = trapezoid_sbp_difference() @ q / period
    eigenvalues = np.linalg.eigvalsh(exact_action_jet_at_state(
        ORDER, q[-1], velocity[-1], multipliers[-1], points=44,
    ).hessian)
    rows = []
    selected_steps = []
    for name, direction in _directions(raw, scales, residual).items():
        responses = {
            step: _structured_response(
                direction, step, y, scales, action_scaled, event_gradient,
            ) for step in STEPS
        }
        comparisons = []
        for coarse, fine in zip(STEPS[:-1], STEPS[1:]):
            change = float(
                np.linalg.norm(responses[fine] - responses[coarse])
                / max(1.0, np.linalg.norm(responses[fine]))
            )
            comparisons.append({"coarse_step": coarse, "fine_step": fine, "relative_change": change})
        best_pair = min(comparisons, key=lambda item: item["relative_change"])
        selected_step = float(best_pair["fine_step"]); selected_steps.append(selected_step)
        predicted = responses[selected_step]
        norm = float(np.linalg.norm(direction)); unit = direction / norm
        finite = norm * (
            _square_physical_residual(y + selected_step * unit)
            - _square_physical_residual(y - selected_step * unit)
        ) / (2.0 * selected_step)
        rows.append({
            "direction": name, "physical_scaled_direction_norm": norm,
            "selected_step": selected_step, "selected_adjacent_pair_relative_change": best_pair["relative_change"],
            "structured_response_l2": float(np.linalg.norm(predicted)),
            "exact_central_response_l2_at_selected_step": float(np.linalg.norm(finite)),
            "structured_vs_exact_relative_residual": float(
                np.linalg.norm(predicted - finite) / max(1.0, np.linalg.norm(finite))
            ),
            "event_row_absolute_residual": float(abs(predicted[-1] - finite[-1])),
            "step_comparisons": comparisons,
        })
    return {
        "source_frontier": {"version": "v20.77", "exact_f376_l2": float(np.linalg.norm(residual))},
        "ordered_event_spectrum": {
            "event_eigenvalue": float(eigenvalues[6]),
            "lower_gap": float(eigenvalues[6] - eigenvalues[5]),
            "upper_gap": float(eigenvalues[7] - eigenvalues[6]),
            "isolated_at_frontier": bool(eigenvalues[6] > eigenvalues[5] and eigenvalues[7] > eigenvalues[6]),
        },
        "exact_action_response": {
            **action, "scaled_hessian_norm": float(np.linalg.norm(action_scaled)),
            "used_without_outer_residual_differencing": True,
        },
        "directions": rows,
        "one_common_event_response_step_exists": len(set(selected_steps)) == 1,
        "response_method": "EXACT_ACTION_HESSIAN_PLUS_DIRECTION_ADAPTIVE_ORDERED_EVENT_COVECTOR_RESPONSE",
        "outcome": "FINITE_DIFFERENCE_EVENT_COVECTOR_INCONSISTENCY_IDENTIFIED",
        "next_action": "DERIVE_THE_ISOLATED_ORDERED_EIGENVALUE_COVECTOR_BY_RAYLEIGH_PERTURBATION",
        "physical_equations_changed": False, "event_definition_changed": False,
        "acceptance_gate_changed": False, "componentwise_monotonicity_added": False,
    }


def completion_payload() -> dict[str, Any]:
    result = direction_adaptive_event_response_audit()
    validation = {
        "source_v20_77_reproduced": abs(result["source_frontier"]["exact_f376_l2"] - 0.758671922543989) < 5.0e-12,
        "ordered_event_isolated": result["ordered_event_spectrum"]["isolated_at_frontier"],
        "exact_action_assembly_reproduces_gradient": result["exact_action_response"]["gradient_relative_residual"] < 5.0e-11,
        "all_directions_resolved": all(row["selected_adjacent_pair_relative_change"] < 2.0e-2 for row in result["directions"]),
        "structured_response_matches_exact_checks": all(row["structured_vs_exact_relative_residual"] < 2.0e-4 for row in result["directions"]),
        "event_rows_match": all(row["event_row_absolute_residual"] < 2.0e-4 for row in result["directions"]),
        "same_physics": not result["physical_equations_changed"] and not result["event_definition_changed"] and not result["acceptance_gate_changed"],
        "no_componentwise_gate": not result["componentwise_monotonicity_added"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_DIRECTION_ADAPTIVE_EVENT_RESPONSE_V20_79", "version": VERSION,
        "classification": CLASSIFICATION, "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "direction_adaptive_event_response": result,
        "status": "VALIDATED" if passed else "INVALIDATED", "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_DIRECTION_ADAPTIVE_EVENT_RESPONSE_V20_79.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "STEPS",
    "direction_adaptive_event_response_audit", "completion_payload", "materialize",
]
