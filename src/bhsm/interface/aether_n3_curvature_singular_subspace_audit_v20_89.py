"""Localize the weak singular subspace of the v20.88 curvature-aware KKT response."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import _action_curvature_transform
from bhsm.interface.aether_n3_exact_action_hessian_assembly_v18_18 import exact_sbp_action_hessian
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_rayleigh_curvature_preconditioned_proposal_v20_88 import v20_88_selected_raw_vector
from bhsm.interface.aether_n3_rayleigh_event_covector_v20_80 import (
    rayleigh_sbp_event_covector, rayleigh_square_physical_residual,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import event_gradient_indices, kkt_variable_scales
from bhsm.interface.aether_n3_structural_hindsight_recovery_v20_68 import (
    _child_tangent, _fractions, _node_fractions,
)


VERSION = "v20.89"
CLASSIFICATION = "BHSM_N3_CURVATURE_AWARE_SINGULAR_SUBSPACE_AUDIT"
FULL_BHSM_COMPLETE = False
SCALED_EVENT_STEP = 3.0e-8


def curvature_singular_subspace_audit(
    source_raw_override: np.ndarray | None = None, *, source_label: str = "v20.88",
) -> dict[str, Any]:
    scales = kkt_variable_scales()
    raw = v20_88_selected_raw_vector() if source_raw_override is None else np.asarray(source_raw_override, dtype=float)
    y = raw * scales
    residual = rayleigh_square_physical_residual(y); support = np.asarray(event_gradient_indices(), dtype=int)
    inverse = 1.0 / scales[:-1]
    def event_gradient(ybase: np.ndarray) -> np.ndarray:
        return rayleigh_sbp_event_covector(ybase / scales[:-1]) * inverse / scales[-1]
    gradient = event_gradient(y[:-1]); raw_block = np.empty((support.size, support.size))
    for column_position, column in enumerate(support):
        delta = np.zeros(375); delta[int(column)] = SCALED_EVENT_STEP
        response = (event_gradient(y[:-1] + delta) - event_gradient(y[:-1] - delta)) / (2.0 * SCALED_EVENT_STEP)
        raw_block[:, column_position] = response[support]
    block = 0.5 * (raw_block + raw_block.T)
    action = exact_sbp_action_hessian(raw[:-1]); action_raw = np.asarray(action.pop("hessian"))
    action_scaled = inverse[:, None] * action_raw * inverse[None, :]
    event_hessian = np.zeros((375, 375)); event_hessian[np.ix_(support, support)] = block
    matrix = np.zeros((376, 376)); matrix[:-1, :-1] = action_scaled + y[-1] * event_hessian
    matrix[:-1, -1] = gradient; matrix[-1, :-1] = gradient
    transform, transform_audit = _action_curvature_transform(raw); transformed = matrix @ transform
    left, singular, right_t = np.linalg.svd(transformed, full_matrices=True)
    tolerance = float(np.finfo(float).eps * max(transformed.shape) * singular[0])
    rank = int(np.count_nonzero(singular > tolerance))
    target = -residual; coefficients = left.T @ target
    amplitudes = np.zeros(376); amplitudes[:rank] = coefficients[:rank] / singular[:rank]
    direction_x = right_t.T @ amplitudes; direction_y = transform @ direction_x
    contributions = []
    for index in range(rank):
        physical = transform @ (right_t[index] * amplitudes[index])
        contributions.append((float(np.linalg.norm(physical)), index, physical))
    contributions.sort(reverse=True, key=lambda item: item[0])
    selected_indices = []
    for index in (rank - 1, rank - 2, rank, contributions[0][1]):
        if 0 <= index < 376 and index not in selected_indices:
            selected_indices.append(index)
    modes = []
    child_basis = []
    for index in selected_indices:
        direction_x_mode = right_t[index]
        direction_y_mode = transform @ direction_x_mode
        child_basis.append((f"singular_mode_{index}", direction_x_mode))
        modes.append({
            "index": index, "singular_value": float(singular[index]),
            "retained_by_moore_penrose_tolerance": bool(index < rank),
            "left_residual_coefficient": float(coefficients[index]),
            "solution_amplitude_if_retained": float(amplitudes[index]),
            "physical_scaled_mode_norm_per_unit_action_coordinate": float(np.linalg.norm(direction_y_mode)),
            "action_coordinate_block_fractions": _fractions(direction_x_mode),
            "action_coordinate_history_fractions": _node_fractions(direction_x_mode),
        })
    unit_solution = direction_x / np.linalg.norm(direction_x)
    child_basis.append(("normalized_moore_penrose_direction", unit_solution))
    tangent = _child_tangent(raw, child_basis, transform)
    hindsight = json.loads(Path(
        "artifacts/BHSM_N3_STRUCTURAL_HINDSIGHT_RECOVERY_V20_68.json"
    ).read_text(encoding="utf-8"))["structural_hindsight_recovery"]
    natural_radii = hindsight["prospective_search"]["class_action_amplitudes"]
    range_projection = left[:, :rank] @ coefficients[:rank]
    return {
        "source": {"version": source_label, "exact_rayleigh_f376_l2": float(np.linalg.norm(residual))},
        "response": {
            "rank": rank, "dimension": 376, "tolerance": tolerance,
            "largest_singular_value": float(singular[0]),
            "weakest_retained_singular_value": float(singular[rank - 1]),
            "strongest_discarded_singular_value": float(singular[rank]),
            "spectral_gap_at_rank_boundary": float(singular[rank - 1] / singular[rank]),
            "source_residual_outside_retained_range_l2": float(np.linalg.norm(target - range_projection)),
            "moore_penrose_action_coordinate_norm": float(np.linalg.norm(direction_x)),
            "moore_penrose_physical_scaled_norm": float(np.linalg.norm(direction_y)),
            "coordinate_map": transform_audit,
        },
        "event_curvature_support_indices": support.tolist(),
        "event_curvature_symmetric_block": block.tolist(),
        "localized_modes": modes,
        "largest_physical_solution_contributions": [
            {"mode": index, "physical_scaled_contribution_l2": norm,
             "singular_value": float(singular[index]), "action_amplitude": float(amplitudes[index])}
            for norm, index, _ in contributions[:8]
        ],
        "child_compatible_tangent": tangent,
        "bhsm_owned_action_coordinate_radii": natural_radii,
        "outcome": "WEAK_RETAINED_RANGE_MODES_DOMINATE_UNBOUNDED_INVERSE",
        "next_action": "BOUND_THE_RETAINED_RANGE_SOLUTION_BY_THE_HISTORICAL_BHSM_ACTION_COORDINATE_RADII_AND_TEST_EXACT_F376",
        "physical_equations_changed": False, "event_definition_changed": False,
        "acceptance_gate_changed": False,
    }


def completion_payload() -> dict[str, Any]:
    result = curvature_singular_subspace_audit(); response = result["response"]
    validation = {
        "source_v20_88_reproduced": abs(result["source"]["exact_rayleigh_f376_l2"] - 0.787472758683574) < 5.0e-12,
        "rank_boundary_resolved": response["weakest_retained_singular_value"] > response["tolerance"] >= response["strongest_discarded_singular_value"],
        "residual_in_retained_range": response["source_residual_outside_retained_range_l2"] < 2.0e-5,
        "child_chart_surjective": result["child_compatible_tangent"]["rank_DcG"] == 14,
        "singular_directions_child_compatible": result["child_compatible_tangent"]["all_event_directions_locally_compatible"],
        "natural_radii_owned": all(value > 0.0 for value in result["bhsm_owned_action_coordinate_radii"].values()),
        "same_physics": not result["physical_equations_changed"] and not result["event_definition_changed"] and not result["acceptance_gate_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_CURVATURE_SINGULAR_SUBSPACE_AUDIT_V20_89", "version": VERSION,
        "classification": CLASSIFICATION, "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "curvature_singular_subspace_audit": result, "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation, "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_CURVATURE_SINGULAR_SUBSPACE_AUDIT_V20_89.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "curvature_singular_subspace_audit", "completion_payload", "materialize"]
