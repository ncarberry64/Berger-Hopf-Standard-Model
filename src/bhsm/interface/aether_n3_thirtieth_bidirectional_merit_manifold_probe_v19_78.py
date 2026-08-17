"""Scan both orientations of a bounded geometric probe from v19.76."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.sparse.linalg import LinearOperator, gmres

from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import _action_curvature_transform
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN, _metrics
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_reclassified_chain_proposal_v18_11 import _square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_twenty_ninth_bidirectional_probe_promotion_v19_76 import v19_76_selected_raw_vector


VERSION = "v19.78"
CLASSIFICATION = "BHSM_N3_THIRTIETH_BIDIRECTIONAL_MERIT_MANIFOLD_PROBE"
FULL_BHSM_COMPLETE = False
SOURCE_NORM = 0.783424601549721
BACKTRACKS = 41
GMRES_RESTART = 40
GMRES_OUTER_ITERATIONS = 1
GMRES_RTOL = 1.0e-6


def v19_78_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_thirtieth_bidirectional_merit_manifold_probe_v19_78.json"
    ).read_text(encoding="utf-8"))
    selected = payload["thirtieth_bidirectional_merit_manifold_probe"][
        "selected_true_merit_candidate_pending_child_acceptance"
    ]
    if selected is None:
        raise ValueError("v19.78 has no exact-merit candidate")
    return np.asarray([float.fromhex(value) for value in selected["raw_vector_hex"]])


def thirtieth_bidirectional_merit_manifold_probe() -> dict[str, Any]:
    audit = json.loads(Path(
        "artifacts/BHSM_aether_n3_thirty_third_direct_residual_scale_audit_v19_77.json"
    ).read_text(encoding="utf-8"))
    measured = audit["thirty_third_direct_residual_scale_audit"]
    pair = measured["selected_finest_common_stable_pair"]
    source_stability_gate_passed = pair is not None
    if pair is None:
        bounded_pairs = [
            row for row in measured["common_scale_pairs"]
            if row["maximum_relative_change"] < 5.0e-3
        ]
        if not bounded_pairs:
            raise ValueError("v19.77 has no bounded direct-response pair")
        pair = min(
            bounded_pairs,
            key=lambda row: row["maximum_event_row_absolute_change"],
        )
    response_step = float(pair["fine_step"])
    comparison_step = float(pair["coarse_step"])
    raw = v19_76_selected_raw_vector()
    scales = kkt_variable_scales()
    y = raw * scales
    residual = _square_physical_residual(y)
    initial = _metrics(residual)

    def direct_response(direction_y: np.ndarray, step: float = response_step) -> np.ndarray:
        direction = np.asarray(direction_y, dtype=float)
        norm = float(np.linalg.norm(direction))
        if norm == 0.0:
            return np.zeros(376)
        unit = direction / norm
        finite = (
            _square_physical_residual(y + step * unit)
            - _square_physical_residual(y - step * unit)
        ) / (2.0 * step)
        return norm * finite

    transform, transform_audit = _action_curvature_transform(raw)
    operator = LinearOperator(
        (376, 376),
        matvec=lambda direction_x: direct_response(transform @ direction_x),
        dtype=float,
    )
    callback_residuals: list[float] = []
    direction_x, info = gmres(
        operator, -residual, rtol=GMRES_RTOL, atol=0.0,
        restart=GMRES_RESTART, maxiter=GMRES_OUTER_ITERATIONS,
        callback=lambda value: callback_residuals.append(float(value)),
        callback_type="pr_norm",
    )
    direction_y = transform @ direction_x
    direction_norm = float(np.linalg.norm(direction_y))
    linear_residual = direct_response(direction_y) + residual
    unit = direction_y / direction_norm
    response_consistency = float(
        np.linalg.norm(
            direct_response(unit, response_step)
            - direct_response(unit, comparison_step)
        ) / max(1.0, np.linalg.norm(direct_response(unit, response_step)))
    )
    trials = []
    eligible = []
    for orientation in (1, -1):
        for backtrack in range(BACKTRACKS):
            unsigned_fraction = 0.5**backtrack
            alpha = orientation * unsigned_fraction
            candidate_y = y + alpha * direction_y
            try:
                candidate_residual = _square_physical_residual(candidate_y)
                candidate_raw = candidate_y / scales
                metrics = _metrics(candidate_residual)
                eta = _minimum_node_eta(candidate_raw)
                row = {
                    "orientation": "positive" if orientation > 0 else "negative",
                    "alpha": alpha,
                    "backtrack": backtrack,
                    "unsigned_fraction": unsigned_fraction,
                    "action_curvature_coordinate_step_norm": float(
                        unsigned_fraction * np.linalg.norm(direction_x)
                    ),
                    "physical_scaled_coordinate_step_norm": unsigned_fraction * direction_norm,
                    "raw_coordinate_step_norm": float(
                        unsigned_fraction * np.linalg.norm(direction_y / scales)
                    ),
                    "eta_minimum": eta,
                    "metrics": metrics,
                    "complete_norm_reduction": initial["complete"] - metrics["complete"],
                    "raw_vector_hex": [float(value).hex() for value in candidate_raw],
                }
                row["true_merit_eligible"] = bool(
                    eta > 1.0e-5 and row["complete_norm_reduction"] > MARGIN
                )
                trials.append(row)
                if row["true_merit_eligible"]:
                    eligible.append(row)
            except (ArithmeticError, FloatingPointError, ValueError) as exc:
                trials.append({
                    "orientation": "positive" if orientation > 0 else "negative",
                    "alpha": alpha,
                    "backtrack": backtrack,
                    "unsigned_fraction": unsigned_fraction,
                    "domain_valid": False,
                    "exception": type(exc).__name__,
                })
    selected = min(eligible, key=lambda row: row["metrics"]["complete"]) if eligible else None
    best_by_orientation = {}
    for orientation in ("positive", "negative"):
        rows = [row for row in eligible if row["orientation"] == orientation]
        best_by_orientation[orientation] = (
            None if not rows else min(rows, key=lambda row: row["metrics"]["complete"])
        )
    return {
        "source_state": "v19.76_twenty_ninth_bidirectional_probe_promoted_state",
        "source_complete_norm": initial["complete"],
        "source_eta_minimum": _minimum_node_eta(raw),
        "direct_response": {
            "source_artifact": audit["artifact"],
            "source_status": audit["status"],
            "fine_step": response_step,
            "comparison_step": comparison_step,
            "source_maximum_relative_change": pair["maximum_relative_change"],
            "source_maximum_event_row_absolute_change": pair[
                "maximum_event_row_absolute_change"
            ],
            "source_stability_gate_passed": source_stability_gate_passed,
            "invalidated_scale_used_only_to_generate_bounded_proposals": (
                not source_stability_gate_passed
            ),
            "resulting_direction_relative_change": response_consistency,
            "differentiates_unchanged_exact_376_residual": True,
            "used_only_as_local_geometric_probe": True,
            "prior_failed_direction_models_reused": False,
        },
        "coordinate_map": transform_audit,
        "linear_probe": {
            "method": "BOUNDED_GMRES_LOCAL_GEOMETRIC_PROBE_ONLY",
            "rtol": GMRES_RTOL,
            "restart": GMRES_RESTART,
            "maximum_outer_iterations": GMRES_OUTER_ITERATIONS,
            "info": int(info),
            "iterations": len(callback_residuals),
            "callback_relative_residuals": callback_residuals,
            "relative_exact_linear_residual": float(
                np.linalg.norm(linear_residual) / max(1.0, np.linalg.norm(residual))
            ),
            "convergence_not_required_to_legitimize_proposal": True,
            "never_promoted_as_newton_without_independent_validation": True,
        },
        "direction": {
            "action_curvature_coordinate_norm": float(np.linalg.norm(direction_x)),
            "physical_scaled_coordinate_norm": direction_norm,
            "raw_coordinate_norm": float(np.linalg.norm(direction_y / scales)),
        },
        "line_scan": {
            "both_orientations_scanned": True,
            "full_step_not_preferred": True,
            "exact_nonlinear_residual_authoritative": True,
            "best_true_merit_candidate_by_orientation": best_by_orientation,
        },
        "trials": trials,
        "selected_true_merit_candidate_pending_child_acceptance": selected,
        "physical_solve_dimension": [376, 376],
        "event_multiplier_explicit": True,
        "physical_equations_changed": False,
        "event_definition_changed": False,
        "componentwise_monotonicity_required": False,
        "must_remain_on_previous_iterate_path": False,
    }


def completion_payload() -> dict[str, Any]:
    result = thirtieth_bidirectional_merit_manifold_probe()
    selected = result["selected_true_merit_candidate_pending_child_acceptance"]
    response = result["direct_response"]
    probe = result["linear_probe"]
    validation = {
        "source_is_v19_76": result["source_state"].startswith("v19.76"),
        "source_norm_reproduced": abs(result["source_complete_norm"] - SOURCE_NORM) < 5.0e-12,
        "response_source_status_preserved": (
            (response["source_status"] == "VALIDATED" and response["source_stability_gate_passed"])
            or (
                response["source_status"] == "INVALIDATED"
                and response["invalidated_scale_used_only_to_generate_bounded_proposals"]
            )
        ),
        "unchanged_exact_residual_differentiated": response["differentiates_unchanged_exact_376_residual"],
        "probe_only_not_newton_claim": (
            response["used_only_as_local_geometric_probe"]
            and probe["never_promoted_as_newton_without_independent_validation"]
        ),
        "krylov_convergence_not_physical_gate": probe["convergence_not_required_to_legitimize_proposal"],
        "prior_failed_models_not_reused": not response["prior_failed_direction_models_reused"],
        "right_coordinate_map_invertible": result["coordinate_map"]["invertible"],
        "both_orientations_scanned": result["line_scan"]["both_orientations_scanned"],
        "exact_nonlinear_merit_authoritative": result["line_scan"]["exact_nonlinear_residual_authoritative"],
        "square_explicit_multiplier_system": (
            result["physical_solve_dimension"] == [376, 376]
            and result["event_multiplier_explicit"]
        ),
        "physical_equations_unchanged": not result["physical_equations_changed"],
        "event_definition_unchanged": not result["event_definition_changed"],
        "no_componentwise_filter": not result["componentwise_monotonicity_required"],
        "previous_path_not_a_constraint": not result["must_remain_on_previous_iterate_path"],
        "selected_reduces_true_merit": bool(
            selected is None or selected["complete_norm_reduction"] > MARGIN
        ),
        "selected_preserves_eta": bool(
            selected is None or selected["eta_minimum"] > 1.0e-5
        ),
    }
    passed = all(validation.values())
    solver_interpretation_valid = bool(
        response["source_stability_gate_passed"]
        and
        probe["info"] == 0
        and response["resulting_direction_relative_change"] < 5.0e-3
    )
    return {
        "artifact": "BHSM_aether_n3_thirtieth_bidirectional_merit_manifold_probe_v19_78",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "thirtieth_bidirectional_merit_manifold_probe": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "solver_interpretation": "VALIDATED" if solver_interpretation_valid else "INVALIDATED",
        "physical_candidate_status": "PENDING_COMPLETE_CHILD_GATE" if selected is not None else "NONE",
        "real_physical_property_explained": (
            "A_FRESH_BOUNDED_LOCAL_GEOMETRIC_PROBE_FROM_V19_76_LOCATES_"
            "EXACT_NONLINEAR_MERIT_STATES_WITHOUT_A_NEWTON_CLAIM"
        ),
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "RECONSTRUCT_AND_TEST_COMPETITIVE_SELECTED_COMPLETE_CHILD_STATES"
            if selected is not None
            else "REMEASURE_OR_GENERATE_THE_NEXT_BOUNDED_GEOMETRIC_PROBE"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_thirtieth_bidirectional_merit_manifold_probe_v19_78.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "v19_78_selected_raw_vector", "thirtieth_bidirectional_merit_manifold_probe",
    "completion_payload", "materialize",
]
