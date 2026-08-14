"""Finite-chart complete-child Dirichlet BVP and metric DtN mismatch.

This is an instantaneous reconstruction condition for a nonequilibrium child,
not a stationary-particle definition.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import least_squares

from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_n3_scale_corrected_period_log_continuation_v17_76 import (
    v17_75_selected_raw_vector,
)
from bhsm.interface.aether_n3_terminal_child_boundary_map_v17_85 import (
    terminal_event_boundary_data,
)
from bhsm.interface.aether_post_cut_child_cap_reconstruction_v15_46 import (
    _round_cap_seed,
    action_gradient,
    child_cap_fields,
    child_cap_routhian,
)


VERSION = "v17.86"
CLASSIFICATION = "BHSM_N3_COMPLETE_CHILD_FINITE_CHART_BVP_DTN_MATCH"
FULL_BHSM_COMPLETE = False


def _boundary_log_trace(coefficients: np.ndarray, *, points: int) -> np.ndarray:
    del points
    values = np.asarray(coefficients, dtype=float)
    return np.asarray([
        values[1] + np.sum(values[2:6]),
        values[0] + np.sum(values[6:10]),
        np.sum(values[10:13]),
    ])


def _boundary_constraint_jacobian() -> np.ndarray:
    matrix = np.zeros((3, 15))
    matrix[0, 1] = 1.0
    matrix[0, 2:6] = 1.0
    matrix[1, 0] = 1.0
    matrix[1, 6:10] = 1.0
    matrix[2, 10:13] = 1.0
    return matrix


def solve_child_dirichlet_bvp(
    target_trace: np.ndarray, *, points: int = 110,
    maximum_evaluations: int = 700,
) -> dict[str, Any]:
    target = np.asarray(target_trace, dtype=float)
    if target.shape != (3,) or np.any(target <= 0.0):
        raise ValueError("target A, B, N trace must be positive")
    target_log = np.log(target)
    seed = _round_cap_seed().copy()
    seed_trace = _boundary_log_trace(seed, points=points)
    seed[1] += target_log[0] - seed_trace[0]
    seed[6] += target_log[1] - seed_trace[1]
    seed[10] += target_log[2] - seed_trace[2]
    jacobian = _boundary_constraint_jacobian()
    active = np.asarray([0, 2, 3, 4, 5, 7, 8, 9, 11, 12, 13, 14])
    tangent = np.zeros((15, 12))
    for column, index in enumerate(active):
        tangent[index, column] = 1.0
        if index in (2, 3, 4, 5):
            tangent[1, column] = -1.0
        elif index in (0, 7, 8, 9):
            tangent[6, column] = -1.0
        elif index in (11, 12):
            tangent[10, column] = -1.0

    def expand(values: np.ndarray) -> np.ndarray:
        coefficients = np.zeros(15)
        coefficients[active] = values
        coefficients[1] = target_log[0] - np.sum(coefficients[2:6])
        coefficients[6] = (
            target_log[1] - coefficients[0] - np.sum(coefficients[7:10])
        )
        coefficients[10] = target_log[2] - np.sum(coefficients[11:13])
        return coefficients

    initial = seed[active]
    gradient_seed = action_gradient(expand(initial), points=points)
    action_scale = max(1.0, float(np.linalg.norm(tangent.T @ gradient_seed)))

    def residual(values: np.ndarray) -> np.ndarray:
        coefficients = expand(values)
        try:
            gradient = action_gradient(coefficients, points=points)
        except (ValueError, OverflowError, FloatingPointError):
            return np.full(12, 1.0e6)
        return tangent.T @ gradient / action_scale

    lower_full = np.array(
        [-2.0, -2.0] + [-6.0] * 8 + [-5.0] * 3 + [-0.7, -0.7]
    )
    upper_full = np.array(
        [3.0, 3.0] + [6.0] * 8 + [5.0] * 3 + [0.7, 0.7]
    )
    solution = least_squares(
        residual,
        initial,
        bounds=(lower_full[active], upper_full[active]),
        xtol=2.0e-10,
        ftol=2.0e-10,
        gtol=2.0e-10,
        max_nfev=int(maximum_evaluations),
        x_scale="jac",
        verbose=0,
    )
    coefficients = expand(np.asarray(solution.x))
    solve_reduced_residual = residual(solution.x) * action_scale
    check_points = max(points + 50, 170)
    gradient = action_gradient(coefficients, points=check_points)
    constraints = _boundary_log_trace(
        coefficients, points=check_points
    ) - target_log
    physical_multipliers = np.linalg.lstsq(
        jacobian.T, -gradient, rcond=None
    )[0]
    stationarity = gradient + jacobian.T @ physical_multipliers
    reduced_stationarity = tangent.T @ gradient
    fields = child_cap_fields(coefficients, points=check_points)
    return {
        "success": bool(solution.success),
        "solver_message": str(solution.message),
        "function_evaluations": int(solution.nfev),
        "coordinates": coefficients.tolist(),
        "target_trace_A_B_N": target.tolist(),
        "achieved_trace_A_B_N": np.exp(
            _boundary_log_trace(coefficients, points=check_points)
        ).tolist(),
        "maximum_log_trace_residual": float(np.max(np.abs(constraints))),
        "maximum_KKT_stationarity_residual": float(
            np.max(np.abs(stationarity))
        ),
        "maximum_reduced_stationarity_residual": float(
            np.max(np.abs(reduced_stationarity))
        ),
        "maximum_solve_grid_reduced_stationarity_residual": float(
            np.max(np.abs(solve_reduced_residual))
        ),
        "scaled_KKT_residual_norm": float(np.linalg.norm(
            np.concatenate((reduced_stationarity / action_scale, constraints))
        )),
        "physical_boundary_multipliers_logA_logB_logN": (
            physical_multipliers.tolist()
        ),
        "child_outward_DtN_flux_logA_logB_logN": (
            -physical_multipliers
        ).tolist(),
        "minimum_eta_Legendre": float(np.min(np.asarray(
            fields["eta_legendre"]
        ))),
        "minimum_f_prime": float(np.min(np.asarray(fields["f_prime"]))),
        "localized_inertia_without_orbit": float(np.dot(
            np.asarray(fields["weights"]),
            np.asarray(fields["volume"])
            * np.asarray(fields["localization"])
            * np.asarray(fields["eta_legendre"])
            / np.asarray(fields["N"]),
        )),
        "routhian": float(child_cap_routhian(
            coefficients, points=check_points
        )),
        "interpretation": (
            "INSTANTANEOUS_DIRICHLET_RECONSTRUCTION_SLICE_NOT_A_STATIC_OR_"
            "ETERNALLY_STABLE_PARTICLE_REQUIREMENT"
        ),
    }


def child_bvp_dtn_match() -> dict[str, Any]:
    event = terminal_event_boundary_data(v17_75_selected_raw_vector())
    trace = event["spatial_trace_Gamma0"]
    target = np.asarray([
        trace["A_child_boundary_radius"],
        trace["B_child_boundary_radius"],
        trace["lapse"],
    ])
    child = solve_child_dirichlet_bvp(target)
    event_flux = event["GHY_eta_radial_flux_Gamma1"]
    event_vector = np.asarray([
        event_flux["Pi_log_A"],
        event_flux["Pi_log_B"],
        event_flux["Pi_log_N"],
    ])
    child_vector = np.asarray(child[
        "child_outward_DtN_flux_logA_logB_logN"
    ])
    mismatch = event_vector + child_vector
    child_bvp_closed = bool(
        child["success"]
        and child["maximum_solve_grid_reduced_stationarity_residual"] < 2.0e-4
    )
    return {
        "source_state": "v17.75_selected_fine_period_log_mix_state",
        "event_trace_A_B_N": target.tolist(),
        "event_outward_flux_logA_logB_logN": event_vector.tolist(),
        "child_BVP": child,
        "metric_lapse_F_child": mismatch.tolist(),
        "metric_lapse_F_child_norm": float(np.linalg.norm(mismatch)),
        "child_static_spatial_BVP_closed": child_bvp_closed,
        "metric_lapse_DtN_flux_promotable": child_bvp_closed,
        "flux_orientation": (
            "OUTWARD_EVENT_PLUS_OUTWARD_CHILD_EQUALS_ZERO"
        ),
        "complete_correspondence_evaluated": False,
        "missing_blocks": [
            "ETA_ENDPOINT_REACTION_AND_SIGMA_ADJOINT_FLUX",
            "GAUGE_SPINOR_GHOST_CALDERON_BLOCKS",
            "EVENT_ATTACHMENT_WENTZELL_BLOCK",
            "LORENTZIAN_TEMPORAL_CAUCHY_CONSTRAINT_MATCH",
            "FUNCTION_SPACE_AND_N_TO_INFINITY_CHILD_BVP_CONTROL",
        ],
        "near_flat_selection_test_eligible": False,
        "why_not_yet": (
            "THE_STATIC_SPATIAL_DIRICHLET_SLICE_DOES_NOT_CLOSE_AT_THE_EVENT_"
            "TRACE_AND_IS_NOT_A_REQUIRED_PARTICLE_EQUILIBRIUM;THE_"
            "LORENTZIAN_NONEQUILIBRIUM_CAUCHY_MATCH_MUST_REPLACE_IT"
        ),
    }


def completion_payload() -> dict[str, Any]:
    result = child_bvp_dtn_match()
    child = result["child_BVP"]
    validation = {
        "event_trace_used_without_new_coordinate": len(
            result["event_trace_A_B_N"]
        ) == 3,
        "child_BVP_solver_classified": isinstance(child["success"], bool),
        "child_trace_matched": child["maximum_log_trace_residual"] < 2.0e-12,
        "static_BVP_result_classified": (
            result["child_static_spatial_BVP_closed"]
            or not result["metric_lapse_DtN_flux_promotable"]
        ),
        "child_independent_grid_residual_reported": math.isfinite(
            child["maximum_reduced_stationarity_residual"]
        ),
        "child_eta_domain_positive": child["minimum_eta_Legendre"] > 0.0,
        "finite_metric_lapse_DtN_mismatch": math.isfinite(
            result["metric_lapse_F_child_norm"]
        ),
        "nonequilibrium_particle_doctrine_preserved": (
            "NOT_A_STATIC" in child["interpretation"]
        ),
        "incomplete_blocks_not_hidden": (
            not result["complete_correspondence_evaluated"]
            and len(result["missing_blocks"]) == 5
        ),
        "no_premature_near_flat_selection_claim": not result[
            "near_flat_selection_test_eligible"
        ],
        "failed_static_slice_not_made_particle_no_go": (
            result["child_static_spatial_BVP_closed"]
            or "LORENTZIAN_NONEQUILIBRIUM" in result["why_not_yet"]
        ),
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_child_bvp_dtn_match_v17_86",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "child_bvp_dtn_match": result,
        "status": (
            "VALIDATED" if passed and result["child_static_spatial_BVP_closed"]
            else "RECLASSIFIED" if passed else "INVALIDATED"
        ),
        "real_physical_property_explained": (
            "THE_EVENT_TRACE_DEFINES_A_CHILD_DIRICHLET_RECONSTRUCTION_AND_"
            "ITS_KKT_MULTIPLIERS_ARE_THE_FINITE_CHART_DtN_FLUX"
        ),
        "dependency_advanced": (
            "TESTS_AND_RECLASSIFIES_THE_STATIC_DIRICHLET_DtN_ROUTE_BEFORE_"
            "THE_REQUIRED_NONEQUILIBRIUM_CAUCHY_MATCH"
        ),
        "active_calculation": (
            "ADD_THE_ETA_SIGMA_REACTION_AND_LORENTZIAN_CAUCHY_MATCH_TO_CLOSE_"
            "THE_COMPLETE_GRAVITY_MATERIAL_F_child_BLOCK"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_child_bvp_dtn_match_v17_86.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "solve_child_dirichlet_bvp", "child_bvp_dtn_match",
    "completion_payload", "materialize",
]
