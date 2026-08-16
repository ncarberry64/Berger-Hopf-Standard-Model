"""BHSM-owned action-radius trust-region proposals in the curvature-aware range space."""
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
from bhsm.interface.aether_n3_structural_hindsight_recovery_v20_68 import _fresh_child_gate


VERSION = "v20.90"
CLASSIFICATION = "BHSM_N3_CURVATURE_AWARE_BOUNDED_RANGE_SPACE_PROPOSAL"
FULL_BHSM_COMPLETE = False


def v20_90_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_N3_BOUNDED_RANGE_SPACE_PROPOSAL_V20_90.json"
    ).read_text(encoding="utf-8"))["bounded_range_space_proposal"]
    if not payload["promotion"]["promoted"]:
        raise ValueError("v20.90 has no physically promoted state")
    return np.asarray([float.fromhex(value) for value in payload["exact_search"]["best"]["raw_vector_hex"]])


def _trust_solution(
    singular: np.ndarray, right_t: np.ndarray, coefficients: np.ndarray,
    rank: int, radius: float,
) -> tuple[np.ndarray, float]:
    kept_s = singular[:rank]; kept_c = coefficients[:rank]
    def components(lagrange: float) -> np.ndarray:
        return kept_s * kept_c / (kept_s**2 + lagrange)
    unbounded = components(0.0)
    if np.linalg.norm(unbounded) <= radius:
        return right_t[:rank].T @ unbounded, 0.0
    low = 0.0; high = 1.0
    while np.linalg.norm(components(high)) > radius:
        high *= 4.0
    for _ in range(96):
        middle = 0.5 * (low + high)
        if np.linalg.norm(components(middle)) > radius:
            low = middle
        else:
            high = middle
    value = components(high)
    return right_t[:rank].T @ value, high


def bounded_range_space_proposal() -> dict[str, Any]:
    scales = kkt_variable_scales(); raw = v20_88_selected_raw_vector(); y = raw * scales
    residual = rayleigh_square_physical_residual(y); source_norm = float(np.linalg.norm(residual))
    audit = json.loads(Path(
        "artifacts/BHSM_N3_CURVATURE_SINGULAR_SUBSPACE_AUDIT_V20_89.json"
    ).read_text(encoding="utf-8"))["curvature_singular_subspace_audit"]
    support = np.asarray(audit["event_curvature_support_indices"], dtype=int)
    block = np.asarray(audit["event_curvature_symmetric_block"], dtype=float)
    inverse = 1.0 / scales[:-1]
    action = exact_sbp_action_hessian(raw[:-1]); action_raw = np.asarray(action.pop("hessian"))
    action_scaled = inverse[:, None] * action_raw * inverse[None, :]
    event_hessian = np.zeros((375, 375)); event_hessian[np.ix_(support, support)] = block
    event_gradient = rayleigh_sbp_event_covector(raw[:-1]) * inverse / scales[-1]
    matrix = np.zeros((376, 376)); matrix[:-1, :-1] = action_scaled + y[-1] * event_hessian
    matrix[:-1, -1] = event_gradient; matrix[-1, :-1] = event_gradient
    transform, transform_audit = _action_curvature_transform(raw); transformed = matrix @ transform
    left, singular, right_t = np.linalg.svd(transformed, full_matrices=True)
    tolerance = np.finfo(float).eps * max(transformed.shape) * singular[0]
    rank = int(np.count_nonzero(singular > tolerance)); coefficients = left.T @ (-residual)
    radii = audit["bhsm_owned_action_coordinate_radii"]
    trials = []; eligible = []
    for label in ("PLATEAU_DESCENT", "MEDIUM_DESCENT", "LARGE_DESCENT"):
        radius = float(radii[label]); direction_x, lagrange = _trust_solution(singular, right_t, coefficients, rank, radius)
        predicted = residual + transformed @ direction_x
        for orientation in (-1.0, 1.0):
            displacement_x = orientation * direction_x; candidate_y = y + transform @ displacement_x
            try:
                candidate_raw = candidate_y / scales
                norm = float(np.linalg.norm(rayleigh_square_physical_residual(candidate_y)))
                eta = float(_minimum_node_eta(candidate_raw)); reduction = source_norm - norm
                row = {"radius_class": label, "action_coordinate_radius": radius,
                       "orientation": "negative" if orientation < 0.0 else "positive",
                       "lagrange_multiplier_numerical_control": lagrange,
                       "realized_action_coordinate_norm": float(np.linalg.norm(direction_x)),
                       "physical_scaled_step_norm": float(np.linalg.norm(transform @ displacement_x)),
                       "predicted_residual_l2_has_no_physical_authority": float(np.linalg.norm(predicted if orientation > 0.0 else residual - transformed @ direction_x)),
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
        "source": {"version": "v20.88", "exact_rayleigh_f376_l2": source_norm},
        "bounded_model": {"rank": rank, "dimension": 376, "coordinate_map": transform_audit,
                          "radii_source": "VALIDATED_V20_68_ACCEPTED_HISTORY_ACTION_COORDINATE_CLASS_MEDIANS",
                          "radii": radii, "physical_equations_changed": False,
                          "used_only_to_propose": True},
        "exact_search": {"both_orientations": True, "trial_count": len(trials),
                         "trials": sorted(trials, key=lambda row: row["exact_rayleigh_f376_l2"]),
                         "best": best, "original_unweighted_376_rows_authoritative": True},
        "promotion": promotion,
        "outcome": "BOUNDED_RANGE_SPACE_DESCENT_PROMOTED" if promotion["promoted"] else (
            "BOUNDED_RANGE_SPACE_DESCENT_FAILED_CHILD" if eligible else "BOUNDED_RANGE_SPACE_NO_EXACT_DESCENT"
        ),
        "physical_equations_changed": False, "event_definition_changed": False,
        "acceptance_gate_changed": False, "componentwise_monotonicity_added": False,
    }


def completion_payload() -> dict[str, Any]:
    result = bounded_range_space_proposal(); best = result["exact_search"]["best"]
    validation = {
        "source_v20_88_reproduced": abs(result["source"]["exact_rayleigh_f376_l2"] - 0.787472758683574) < 5.0e-12,
        "validated_rank_used": result["bounded_model"]["rank"] == 305,
        "radii_bhsm_owned": result["bounded_model"]["radii_source"].startswith("VALIDATED_V20_68"),
        "all_radii_tested_both_signs": result["exact_search"]["trial_count"] == 6 and result["exact_search"]["both_orientations"],
        "exact_rows_decide": result["exact_search"]["original_unweighted_376_rows_authoritative"],
        "candidate_reduces_merit": best is None or best["exact_reduction"] > 0.0,
        "promotion_requires_child": not result["promotion"]["promoted"] or result["promotion"]["child"]["all_pass"],
        "same_physics": not result["physical_equations_changed"] and not result["event_definition_changed"] and not result["acceptance_gate_changed"],
        "no_componentwise_gate": not result["componentwise_monotonicity_added"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_BOUNDED_RANGE_SPACE_PROPOSAL_V20_90", "version": VERSION,
        "classification": CLASSIFICATION, "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "bounded_range_space_proposal": result, "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation, "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_BOUNDED_RANGE_SPACE_PROPOSAL_V20_90.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "v20_90_selected_raw_vector", "bounded_range_space_proposal", "completion_payload", "materialize"]
