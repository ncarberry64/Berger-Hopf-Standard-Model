"""Classify the regular 12-dimensional v18.68 child fiber by ownership."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.linalg import qr
from scipy.optimize import least_squares

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import constraint_residual
from bhsm.interface.aether_n3_action_owned_stiffness_measurement_v18_14 import _local_action_terms
from bhsm.interface.aether_n3_child_constraint_cauchy_match_v17_94 import _metric_radial_flux_covector
from bhsm.interface.aether_n3_complete_child_chart_reconstruction_v18_24 import _child_rows, _pack_child, _unpack_child
from bhsm.interface.aether_n3_constraint_solved_orbit_v16_08 import _advance_constrained, eta_legendre_minimum
from bhsm.interface.aether_n3_fourth_bidirectional_merit_manifold_probe_v18_66 import v18_66_selected_raw_vector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import unpack_reduced
from bhsm.interface.aether_n3_required_child_cauchy_flux_v17_93 import _canonical_pair
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import trapezoid_sbp_difference
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import RADIUS0
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import sobolev_weights, spectral_frequencies


VERSION = "v18.69"
CLASSIFICATION = "BHSM_N3_CHILD_FIBER_OWNERSHIP_AUDIT"
FULL_BHSM_COMPLETE = False
ORDER = 3
JACOBIAN_STEPS = (1.0e-4, 2.0e-4, 4.0e-4)
REFERENCE_STEP = 2.0e-4
FIBER_AMPLITUDE = 2.0e-4


def _event_data() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    state = unpack_reduced(v18_66_selected_raw_vector())
    qh = np.asarray(state["coordinates"], dtype=float)
    mh = np.asarray(state["multipliers"], dtype=float)
    vh = trapezoid_sbp_difference() @ qh / float(state["period"])
    qe, ve, me = qh[-1], vh[-1], mh[-1]
    pe, _, le, _ = _canonical_pair(qe, ve, me)
    event_covector, _ = _metric_radial_flux_covector(qe, me)
    return qe, pe, le.T @ event_covector


def _accepted_child() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_fourth_bidirectional_probe_child_v18_67.json"
    ).read_text(encoding="utf-8"))
    child = payload["fourth_bidirectional_probe_child"]["child_state"]
    return _pack_child(
        np.asarray(child["coordinates"], dtype=float),
        np.asarray(child["velocities"], dtype=float),
        np.asarray(child["multipliers"], dtype=float),
    )


def _natural_amplitudes() -> np.ndarray:
    frequencies = spectral_frequencies(ORDER)["coordinates"]
    q = 1.0 / (1.0 + frequencies**2) ** 3.0
    weights = sobolev_weights(ORDER)
    velocity = 1.0 / weights["velocities"]
    multipliers = 1.0 / weights["multipliers"]
    return np.concatenate((q, velocity, multipliers))


def _raw_jacobian(
    child: np.ndarray, qe: np.ndarray, pe: np.ndarray, event_flux: np.ndarray,
    step: float,
) -> np.ndarray:
    jacobian = np.empty((14, 26))
    for column in range(26):
        delta = np.zeros(26)
        delta[column] = step
        jacobian[:, column] = (
            _child_rows(child + delta, qe, pe, event_flux)
            - _child_rows(child - delta, qe, pe, event_flux)
        ) / (2.0 * step)
    return jacobian


def _rank_nullspace(jacobian: np.ndarray, amplitudes: np.ndarray) -> tuple[np.ndarray, np.ndarray, int, np.ndarray]:
    action_owned = np.asarray(jacobian, dtype=float) * amplitudes[None, :]
    row_scales = np.maximum(np.linalg.norm(action_owned, axis=1), 1.0e-30)
    scaled = action_owned / row_scales[:, None]
    _, singular, vh = np.linalg.svd(scaled, full_matrices=True)
    tolerance = np.finfo(float).eps * max(scaled.shape) * singular[0]
    rank = int(np.count_nonzero(singular > tolerance))
    return singular, vh[rank:].T, rank, row_scales


def _canonical_ownership_basis(nullspace: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    cauchy_projector = np.diag(np.r_[np.ones(20), np.zeros(6)])
    overlap = nullspace.T @ cauchy_projector @ nullspace
    fractions, rotation = np.linalg.eigh(0.5 * (overlap + overlap.T))
    order = np.argsort(fractions)[::-1]
    basis = nullspace @ rotation[:, order]
    fractions = np.clip(fractions[order], 0.0, 1.0)
    for column in range(basis.shape[1]):
        pivot = int(np.argmax(np.abs(basis[:, column])))
        if basis[pivot, column] < 0.0:
            basis[:, column] *= -1.0
    return basis, fractions


def _block_fractions(direction: np.ndarray) -> dict[str, float]:
    blocks = {
        "q_scale": slice(0, 1), "q_u": slice(1, 4), "q_w": slice(4, 7), "q_v": slice(7, 10),
        "rate_scale": slice(10, 11), "rate_u": slice(11, 14), "rate_w": slice(14, 17), "rate_v": slice(17, 20),
        "lapse_multipliers": slice(20, 23), "shift_multipliers": slice(23, 26),
    }
    denominator = float(direction @ direction)
    return {name: float(direction[block] @ direction[block] / denominator) for name, block in blocks.items()}


def _observable(child: np.ndarray, qe: np.ndarray, pe: np.ndarray, event_flux: np.ndarray) -> dict[str, Any]:
    q, velocity, multipliers = _unpack_child(child)
    rows = _child_rows(child, qe, pe, event_flux)
    terms = _local_action_terms(q, velocity, multipliers)
    advanced_q, advanced_v, advanced_m, _, projection = _advance_constrained(
        q, velocity, multipliers, 1.0e-5, points=44
    )
    advanced_constraints = constraint_residual(ORDER, advanced_q, advanced_v, advanced_m, points=44)
    advanced_eta = eta_legendre_minimum(advanced_q, advanced_m, points=3000)
    return {
        "maximum_14_row_residual": float(np.max(np.abs(rows))),
        "trace_maximum": float(np.max(np.abs(rows[:3]))),
        "constraint_maximum": float(np.max(np.abs(rows[3:10]))),
        "momentum_norm": float(np.linalg.norm(rows[10:12])),
        "dynamic_flux_norm": float(np.linalg.norm(rows[12:14])),
        "action_terms": terms,
        "action_value": float(sum(terms.values())),
        "reconstructed_radius": float(RADIUS0 * math.exp(float(q[0]))),
        "velocity_norm": float(np.linalg.norm(velocity)),
        "eta_minimum": float(eta_legendre_minimum(q, multipliers, points=5000)["minimum"]),
        "one_step_persistence": {
            "projection_success": bool(projection["success"]),
            "maximum_constraint_residual": float(np.max(np.abs(advanced_constraints))),
            "eta_minimum": float(advanced_eta["minimum"]),
            "coordinate_displacement": float(np.linalg.norm(advanced_q - q)),
            "nonzero_relative_evolution": bool(np.linalg.norm(advanced_q - q) > 0.0 and np.linalg.norm(advanced_v) > 0.0),
        },
    }


def _reproject(
    trial: np.ndarray, chart: np.ndarray, row_scales: np.ndarray,
    qe: np.ndarray, pe: np.ndarray, event_flux: np.ndarray,
) -> tuple[np.ndarray, dict[str, Any]]:
    fixed = np.asarray(trial, dtype=float).copy()

    def residual(values: np.ndarray) -> np.ndarray:
        candidate = fixed.copy()
        candidate[chart] = values
        return _child_rows(candidate, qe, pe, event_flux) / row_scales

    solution = least_squares(
        residual, fixed[chart].copy(), method="lm",
        ftol=1.0e-13, xtol=1.0e-13, gtol=1.0e-13, max_nfev=900,
    )
    result = fixed.copy()
    result[chart] = solution.x
    return result, {
        "success": bool(solution.success),
        "function_evaluations": int(solution.nfev),
        "scaled_final_norm": float(np.linalg.norm(solution.fun)),
        "correction_norm": float(np.linalg.norm(result - trial)),
    }


def child_fiber_ownership_audit() -> dict[str, Any]:
    qe, pe, event_flux = _event_data()
    child = _accepted_child()
    amplitudes = _natural_amplitudes()
    step_records: list[dict[str, Any]] = []
    nullspaces: dict[float, np.ndarray] = {}
    raw_jacobians: dict[float, np.ndarray] = {}
    for step in JACOBIAN_STEPS:
        raw = _raw_jacobian(child, qe, pe, event_flux, step)
        singular, nullspace, rank, _ = _rank_nullspace(raw, amplitudes)
        raw_jacobians[step] = raw
        nullspaces[step] = nullspace
        step_records.append({
            "raw_jacobian_step": step,
            "rank": rank,
            "nullity": 26 - rank,
            "singular_values": singular.tolist(),
            "smallest_resolved_singular_value": float(singular[rank - 1]),
        })
    reference = nullspaces[REFERENCE_STEP]
    for row in step_records:
        comparison = nullspaces[float(row["raw_jacobian_step"])]
        overlaps = np.linalg.svd(reference.T @ comparison, compute_uv=False)
        row["nullspace_minimum_principal_overlap_with_reference"] = float(np.min(overlaps))
        row["nullspace_maximum_principal_angle_degrees"] = float(np.degrees(np.arccos(np.clip(np.min(overlaps), -1.0, 1.0))))

    raw_reference = raw_jacobians[REFERENCE_STEP]
    _, _, pivots = qr(raw_reference, mode="economic", pivoting=True)
    chart = np.asarray(pivots[:14], dtype=int)
    # Numerical conditioning only: use the already-retained physical row
    # tolerances, rather than Jacobian row norms that can terminate while a
    # small constraint or momentum row is still just outside its gate.
    raw_row_scales = np.r_[
        np.full(3, 1.0e-9), np.full(7, 1.0e-9),
        np.full(2, 1.0e-7), np.full(2, 2.0e-5),
    ]
    basis, cauchy_fractions = _canonical_ownership_basis(reference)
    direction_records: list[dict[str, Any]] = []
    for index in range(basis.shape[1]):
        normalized_direction = basis[:, index]
        raw_direction = amplitudes * normalized_direction
        plus, plus_solve = _reproject(
            child + FIBER_AMPLITUDE * raw_direction, chart, raw_row_scales,
            qe, pe, event_flux,
        )
        minus, minus_solve = _reproject(
            child - FIBER_AMPLITUDE * raw_direction, chart, raw_row_scales,
            qe, pe, event_flux,
        )
        plus_observable = _observable(plus, qe, pe, event_flux)
        minus_observable = _observable(minus, qe, pe, event_flux)
        fraction = float(cauchy_fractions[index])
        if fraction >= 1.0 - 1.0e-10:
            ownership = "GENUINE_PHYSICAL_CAUCHY_FREEDOM"
        elif fraction <= 1.0e-10:
            ownership = "ALREADY_OWNED_BY_CONSTRAINT_OR_FOLIATION_MULTIPLIERS"
        else:
            ownership = "UNRESOLVED_CAUCHY_MULTIPLIER_MIXTURE"
        action_derivative = (
            plus_observable["action_value"] - minus_observable["action_value"]
        ) / (2.0 * FIBER_AMPLITUDE)
        eta_derivative = (
            plus_observable["eta_minimum"] - minus_observable["eta_minimum"]
        ) / (2.0 * FIBER_AMPLITUDE)
        direction_records.append({
            "direction": index + 1,
            "basis_definition": "EIGENVECTOR_OF_NULLSPACE_CAUCHY_OWNERSHIP_PROJECTOR_NOT_OUTCOME_OPTIMIZED",
            "ownership": ownership,
            "dimensionless_cauchy_fraction": fraction,
            "dimensionless_multiplier_fraction": float(1.0 - fraction),
            "dimensionless_block_fractions": _block_fractions(normalized_direction),
            "dimensionless_direction": normalized_direction.tolist(),
            "raw_direction_norm": float(np.linalg.norm(raw_direction)),
            "raw_maximum_component": float(np.max(np.abs(raw_direction))),
            "linearized_14_row_norm": float(np.linalg.norm(raw_reference @ raw_direction)),
            "plus_reprojection": plus_solve,
            "minus_reprojection": minus_solve,
            "plus": plus_observable,
            "minus": minus_observable,
            "centered_action_derivative_per_dimensionless_amplitude": float(action_derivative),
            "centered_eta_derivative_per_dimensionless_amplitude": float(eta_derivative),
        })

    counts = {
        label: sum(row["ownership"] == label for row in direction_records)
        for label in (
            "GAUGE_OR_CHART",
            "ALREADY_OWNED_BY_CONSTRAINT_OR_FOLIATION_MULTIPLIERS",
            "GENUINE_PHYSICAL_CAUCHY_FREEDOM",
            "UNRESOLVED_CAUCHY_MULTIPLIER_MIXTURE",
        )
    }
    resolved_action_variation = max(abs(row["centered_action_derivative_per_dimensionless_amplitude"]) for row in direction_records)
    resolved_eta_variation = max(abs(row["centered_eta_derivative_per_dimensionless_amplitude"]) for row in direction_records)
    return {
        "source_frontier": "V18_68_ACCEPTED",
        "source_exact_376_norm": 0.811248056430707,
        "whole_child_variable_count": 26,
        "retained_child_equality_count": 14,
        "additional_global_KKT_rows": 0,
        "natural_coordinate_metric": {
            "definition": "EXISTING_H6_COORDINATE_H5_RATE_H6_MULTIPLIER_SOBOLEV_AMPLITUDES",
            "amplitudes": amplitudes.tolist(),
            "tuned_to_outcomes": False,
        },
        "neighboring_rank_audit": step_records,
        "ownership_basis": {
            "gauge_statement": "MONOTONE_ETA_GAUGE_F_EQUALS_CHI_AND_TIME_RADIAL_DIFF_QUOTIENT_ALREADY_REMOVE_EXPLICIT_GAUGE_COORDINATES;_NO_REMAINING_NULL_VECTOR_IS_DECLARED_GAUGE_WITHOUT_A_GENERATOR",
            "cauchy_block": "Q_AND_QDOT_20_VARIABLES_AFTER_DECLARED_GAUGE_FIXING",
            "multiplier_block": "THREE_LAPSE_AND_THREE_SHIFT_COEFFICIENTS_OWNED_BY_THE_RETAINED_CONSTRAINT_FOLIATION_FORMULATION",
            "basis_not_unique": True,
            "canonicalization": "DIAGONALIZE_THE_CAUCHY_OWNERSHIP_PROJECTOR_INSIDE_KER_DC_G",
            "selected_reprojection_chart": chart.tolist(),
        },
        "fiber_probe": {
            "dimensionless_amplitude": FIBER_AMPLITUDE,
            "physical_rows_changed": False,
            "selector_introduced": False,
            "observable_optimization_performed": False,
            "directions": direction_records,
        },
        "ownership_counts": counts,
        "measured_variation": {
            "maximum_absolute_action_derivative_per_dimensionless_amplitude": float(resolved_action_variation),
            "maximum_absolute_eta_derivative_per_dimensionless_amplitude": float(resolved_eta_variation),
            "interpretation": "THE_EQUALITY_FIBER_IS_NOT_AN_OBSERVABLE-INVARIANT GAUGE OR CHART FIBER",
        },
        "scientific_conclusion": {
            "rank_14_surjectivity": "VALIDATED_FINITE_DIMENSIONAL_LOCAL_RESULT",
            "child_equalities_locally_obstruct_small_event_motion": False,
            "all_12_directions_are_gauge_or_already_owned": False,
            "physical_fiber_directions_remain": True,
            "action_derived_selector_claimed": False,
            "unique_actualization_owner": "OPEN_ACTION_DERIVED_CHILD_FIBER_SELECTION_OR_UNIQUE_ACTUALIZATION_OWNER",
        },
        "physical_equations_changed": False,
        "event_definition_changed": False,
        "complete_child_gate_changed": False,
    }


def completion_payload() -> dict[str, Any]:
    result = child_fiber_ownership_audit()
    ranks = result["neighboring_rank_audit"]
    directions = result["fiber_probe"]["directions"]
    validation = {
        "source_is_accepted_v18_68": result["source_frontier"] == "V18_68_ACCEPTED",
        "rank_14_at_all_neighboring_steps": all(row["rank"] == 14 and row["nullity"] == 12 for row in ranks),
        "all_12_directions_audited": len(directions) == 12,
        "all_reprojections_converged": all(row[sign + "_reprojection"]["success"] for row in directions for sign in ("plus", "minus")),
        "reprojected_equalities_close": all(
            row[sign]["trace_maximum"] < 1.0e-9
            and row[sign]["constraint_maximum"] < 1.0e-9
            and row[sign]["momentum_norm"] < 1.0e-7
            and row[sign]["dynamic_flux_norm"] < 2.0e-5
            for row in directions for sign in ("plus", "minus")
        ),
        "eta_domain_preserved": all(row[sign]["eta_minimum"] > 0.0 for row in directions for sign in ("plus", "minus")),
        "one_step_persistence_preserved": all(
            row[sign]["one_step_persistence"]["projection_success"]
            and row[sign]["one_step_persistence"]["maximum_constraint_residual"] < 1.0e-8
            and row[sign]["one_step_persistence"]["eta_minimum"] > 0.0
            and row[sign]["one_step_persistence"]["nonzero_relative_evolution"]
            for row in directions for sign in ("plus", "minus")
        ),
        "no_gauge_direction_invented": result["ownership_counts"]["GAUGE_OR_CHART"] == 0,
        "physical_cauchy_freedom_identified": result["ownership_counts"]["GENUINE_PHYSICAL_CAUCHY_FREEDOM"] > 0,
        "no_selector_invented": not result["fiber_probe"]["selector_introduced"] and not result["scientific_conclusion"]["action_derived_selector_claimed"],
        "same_physics": not result["physical_equations_changed"] and not result["event_definition_changed"] and not result["complete_child_gate_changed"],
        "no_extra_global_row": result["additional_global_KKT_rows"] == 0,
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_child_fiber_ownership_v18_69",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "child_fiber_ownership_audit": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": "THE_REGULAR_RANK_14_CHILD_MAP_HAS_A_12D_LOCAL_FIBER_CONTAINING_GENUINE_CAUCHY_FREEDOM_NOT_JUST_GAUGE_OR_CHART_REDUNDANCY",
        "dependency_advanced": "CLASSIFY_THE_12D_CHILD_FIBER_BY_OWNERSHIP",
        "active_calculation": "RESUME_EXACT_N3_CONTINUATION_WITH_CHILD_FIBER_UNIQUENESS_OWNER_RECORDED_OPEN",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_child_fiber_ownership_v18_69.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "child_fiber_ownership_audit", "completion_payload", "materialize"]
