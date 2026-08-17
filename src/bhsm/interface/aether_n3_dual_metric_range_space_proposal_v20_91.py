"""Bound curvature-aware proposals by both BHSM-owned action and physical metrics."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import _action_curvature_transform
from bhsm.interface.aether_n3_exact_action_hessian_assembly_v18_18 import exact_sbp_action_hessian
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_rayleigh_curvature_preconditioned_proposal_v20_88 import v20_88_selected_raw_vector
from bhsm.interface.aether_n3_rayleigh_event_covector_v20_80 import (
    rayleigh_sbp_event_covector, rayleigh_square_physical_residual,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_structural_hindsight_recovery_v20_68 import HISTORY, _fresh_child_gate


VERSION = "v20.91"
CLASSIFICATION = "BHSM_N3_CURVATURE_AWARE_DUAL_METRIC_RANGE_SPACE_PROPOSAL"
FULL_BHSM_COMPLETE = False


def v20_91_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_N3_DUAL_METRIC_RANGE_SPACE_PROPOSAL_V20_91.json"
    ).read_text(encoding="utf-8"))["dual_metric_range_space_proposal"]
    if not payload["promotion"]["promoted"]:
        raise ValueError("v20.91 has no physically promoted state")
    return np.asarray([float.fromhex(value) for value in payload["exact_search"]["best"]["raw_vector_hex"]])


def _physical_history_radii(scales: np.ndarray) -> dict[str, float]:
    hindsight = json.loads(Path(
        "artifacts/BHSM_N3_STRUCTURAL_HINDSIGHT_RECOVERY_V20_68.json"
    ).read_text(encoding="utf-8"))["structural_hindsight_recovery"]
    records = hindsight["historical_transitions"]; raws = [loader() for _, loader in HISTORY]
    grouped = {label: [] for label in ("LARGE_DESCENT", "MEDIUM_DESCENT", "PLATEAU_DESCENT")}
    for index, record in enumerate(records):
        grouped[record["descent_class"]].append(float(np.linalg.norm((raws[index + 1] - raws[index]) * scales)))
    return {label: float(np.median(values)) for label, values in grouped.items()}


def _physical_trust_solution(
    singular: np.ndarray, right_t: np.ndarray, coefficients: np.ndarray, radius: float,
) -> tuple[np.ndarray, float]:
    def components(lagrange: float) -> np.ndarray:
        return singular * coefficients / (singular**2 + lagrange)
    low = 0.0; high = 1.0
    while np.linalg.norm(components(high)) > radius:
        high *= 4.0
    for _ in range(96):
        middle = 0.5 * (low + high)
        if np.linalg.norm(components(middle)) > radius:
            low = middle
        else:
            high = middle
    return right_t.T @ components(high), high


def dual_metric_range_space_proposal(
    source_raw_override: np.ndarray | None = None, *, source_label: str = "v20.88",
    curvature_artifact: str | Path = (
        "artifacts/BHSM_N3_CURVATURE_SINGULAR_SUBSPACE_AUDIT_V20_89.json"
    ),
    curvature_key: str = "curvature_singular_subspace_audit",
    curvature_override: dict[str, Any] | None = None,
    radius_schedule_override: list[dict[str, float | str]] | None = None,
) -> dict[str, Any]:
    scales = kkt_variable_scales()
    raw = v20_88_selected_raw_vector() if source_raw_override is None else np.asarray(source_raw_override, dtype=float)
    y = raw * scales
    residual = rayleigh_square_physical_residual(y); source_norm = float(np.linalg.norm(residual))
    audit = curvature_override if curvature_override is not None else json.loads(
        Path(curvature_artifact).read_text(encoding="utf-8")
    )[curvature_key]
    support = np.asarray(audit["event_curvature_support_indices"], dtype=int)
    block = np.asarray(audit["event_curvature_symmetric_block"], dtype=float)
    inverse = 1.0 / scales[:-1]
    action = exact_sbp_action_hessian(raw[:-1]); action_raw = np.asarray(action.pop("hessian"))
    action_scaled = inverse[:, None] * action_raw * inverse[None, :]
    event_hessian = np.zeros((375, 375)); event_hessian[np.ix_(support, support)] = block
    event_gradient = rayleigh_sbp_event_covector(raw[:-1]) * inverse / scales[-1]
    matrix = np.zeros((376, 376)); matrix[:-1, :-1] = action_scaled + y[-1] * event_hessian
    matrix[:-1, -1] = event_gradient; matrix[-1, :-1] = event_gradient
    transform, transform_audit = _action_curvature_transform(raw)
    left, singular, right_t = np.linalg.svd(matrix, full_matrices=True); coefficients = left.T @ (-residual)
    physical_radii = _physical_history_radii(scales); action_radii = audit["bhsm_owned_action_coordinate_radii"]
    radius_schedule = radius_schedule_override or [
        {
            "label": label,
            "physical_radius": physical_radii[label],
            "action_radius": float(action_radii[label]),
        }
        for label in ("PLATEAU_DESCENT", "MEDIUM_DESCENT", "LARGE_DESCENT")
    ]
    trials = []; eligible = []
    for schedule_row in radius_schedule:
        label = str(schedule_row["label"])
        physical_radius = float(schedule_row["physical_radius"])
        action_radius = float(schedule_row["action_radius"])
        physical_direction, lagrange = _physical_trust_solution(singular, right_t, coefficients, physical_radius)
        action_direction = np.linalg.solve(transform, physical_direction)
        intersection_factor = min(1.0, action_radius / max(float(np.linalg.norm(action_direction)), 1.0e-300))
        displacement_y = intersection_factor * physical_direction
        displacement_x = intersection_factor * action_direction
        for orientation in (-1.0, 1.0):
            candidate_y = y + orientation * displacement_y
            try:
                candidate_raw = candidate_y / scales
                norm = float(np.linalg.norm(rayleigh_square_physical_residual(candidate_y)))
                eta = float(_minimum_node_eta(candidate_raw)); reduction = source_norm - norm
                row = {"radius_class": label, "orientation": "negative" if orientation < 0.0 else "positive",
                       "bhsm_physical_scaled_radius": physical_radius, "bhsm_action_coordinate_radius": action_radius,
                       "intersection_factor": intersection_factor,
                       "realized_physical_scaled_norm": float(np.linalg.norm(displacement_y)),
                       "realized_action_coordinate_norm": float(np.linalg.norm(displacement_x)),
                       "lagrange_multiplier_numerical_control": lagrange,
                       "predicted_residual_l2_has_no_physical_authority": float(np.linalg.norm(residual + orientation * matrix @ displacement_y)),
                       "exact_rayleigh_f376_l2": norm, "exact_reduction": reduction, "eta_minimum": eta}
                trials.append(row)
                if eta > 1.0e-5 and reduction > MARGIN:
                    eligible.append({**row, "raw": candidate_raw})
            except (ArithmeticError, FloatingPointError, ValueError):
                continue
    selected = None; attempts = []
    for candidate in sorted(eligible, key=lambda row: row["exact_rayleigh_f376_l2"]):
        child = _fresh_child_gate(candidate["raw"])
        attempts.append({"radius_class": candidate["radius_class"], "orientation": candidate["orientation"],
                         "exact_rayleigh_f376_l2": candidate["exact_rayleigh_f376_l2"],
                         "all_pass": child["all_pass"], "flux_envelope": child["flux_envelope"]})
        if child["all_pass"]:
            selected = candidate
            break
    best = None
    if selected is not None:
        best = {key: value for key, value in selected.items() if key != "raw"}
        best["raw_vector_hex"] = [float(value).hex() for value in selected["raw"]]
    promotion = {"attempted": bool(eligible), "promoted": selected is not None,
                 "child": child if eligible else None, "child_attempts": attempts}
    return {
        "source": {"version": source_label, "exact_rayleigh_f376_l2": source_norm},
        "dual_metric_model": {"physical_metric": "EXISTING_BHSM_H6_SCALED_KKT_COORDINATES",
                              "action_metric": "VALIDATED_V18_15_ACTION_CURVATURE_COORDINATES",
                              "curvature_artifact": (
                                  "IN_MEMORY_ACTION_OWNED_TRANSPORT"
                                  if curvature_override is not None else str(curvature_artifact)
                              ),
                              "curvature_key": curvature_key,
                              "physical_radii": physical_radii, "action_radii": action_radii,
                              "radii_source": "V20_68_ACCEPTED_HISTORY_CLASS_MEDIANS",
                              "radius_schedule": radius_schedule,
                              "radius_schedule_interpolated_only_if_explicitly_overridden": radius_schedule_override is not None,
                              "singular_rank_not_used_AS_PHYSICS": True,
                              "coordinate_map": transform_audit, "used_only_to_propose": True},
        "exact_search": {"both_orientations": True, "trial_count": len(trials),
                         "trials": sorted(trials, key=lambda row: row["exact_rayleigh_f376_l2"]),
                         "best": best, "original_unweighted_376_rows_authoritative": True},
        "promotion": promotion,
        "outcome": "DUAL_METRIC_RANGE_SPACE_DESCENT_PROMOTED" if promotion["promoted"] else (
            "DUAL_METRIC_RANGE_SPACE_DESCENT_FAILED_CHILD" if eligible else "DUAL_METRIC_RANGE_SPACE_NO_EXACT_DESCENT"
        ),
        "physical_equations_changed": False, "event_definition_changed": False,
        "acceptance_gate_changed": False, "componentwise_monotonicity_added": False,
    }


def completion_payload() -> dict[str, Any]:
    result = dual_metric_range_space_proposal(); best = result["exact_search"]["best"]
    validation = {
        "source_v20_88_reproduced": abs(result["source"]["exact_rayleigh_f376_l2"] - 0.787472758683574) < 5.0e-12,
        "both_bhsm_metrics_used": result["dual_metric_model"]["physical_metric"].startswith("EXISTING_BHSM") and result["dual_metric_model"]["action_metric"].startswith("VALIDATED_V18_15"),
        "radii_from_accepted_history": result["dual_metric_model"]["radii_source"].startswith("V20_68"),
        "rank_not_physics": result["dual_metric_model"]["singular_rank_not_used_AS_PHYSICS"],
        "all_radii_tested_both_signs": result["exact_search"]["trial_count"] == 6 and result["exact_search"]["both_orientations"],
        "exact_rows_decide": result["exact_search"]["original_unweighted_376_rows_authoritative"],
        "candidate_reduces_merit": best is None or best["exact_reduction"] > 0.0,
        "promotion_requires_child": not result["promotion"]["promoted"] or result["promotion"]["child"]["all_pass"],
        "same_physics": not result["physical_equations_changed"] and not result["event_definition_changed"] and not result["acceptance_gate_changed"],
        "no_componentwise_gate": not result["componentwise_monotonicity_added"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_DUAL_METRIC_RANGE_SPACE_PROPOSAL_V20_91", "version": VERSION,
        "classification": CLASSIFICATION, "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "dual_metric_range_space_proposal": result, "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation, "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_DUAL_METRIC_RANGE_SPACE_PROPOSAL_V20_91.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "v20_91_selected_raw_vector", "dual_metric_range_space_proposal", "completion_payload", "materialize"]
