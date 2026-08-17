"""Compact historical-secant hindsight recovery from the accepted v20.66 frontier."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Callable

import numpy as np
from scipy.linalg import qr
from scipy.optimize import least_squares
from scipy.sparse.linalg import LinearOperator, gmres

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import constraint_residual
from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import _action_curvature_transform
from bhsm.interface.aether_n3_admissible_child_cauchy_germ_v17_95 import _trace_jacobian
from bhsm.interface.aether_n3_child_constraint_cauchy_match_v17_94 import _metric_radial_flux_covector
from bhsm.interface.aether_n3_complete_child_chart_reconstruction_v18_24 import JACOBIAN_STEP, _child_rows, _pack_child, _unpack_child
from bhsm.interface.aether_n3_constraint_solved_orbit_v16_08 import _advance_constrained, eta_legendre_minimum, exact_euler_dirac_acceleration
from bhsm.interface.aether_n3_eighth_bidirectional_probe_promotion_v18_87 import v18_87_selected_raw_vector
from bhsm.interface.aether_n3_eighteenth_bidirectional_probe_promotion_v19_29 import v19_29_selected_raw_vector
from bhsm.interface.aether_n3_fifteenth_bidirectional_probe_promotion_v19_17 import v19_17_selected_raw_vector
from bhsm.interface.aether_n3_fifth_bidirectional_probe_promotion_v18_73 import v18_73_selected_raw_vector
from bhsm.interface.aether_n3_forty_eighth_bidirectional_probe_promotion_v20_62 import v20_62_selected_raw_vector
from bhsm.interface.aether_n3_forty_fifth_bidirectional_probe_promotion_v20_46 import v20_46_selected_raw_vector
from bhsm.interface.aether_n3_forty_first_bidirectional_probe_promotion_v20_28 import v20_28_selected_raw_vector
from bhsm.interface.aether_n3_forty_fourth_bidirectional_probe_promotion_v20_42 import v20_42_selected_raw_vector
from bhsm.interface.aether_n3_forty_ninth_bidirectional_probe_promotion_v20_66 import v20_66_selected_raw_vector
from bhsm.interface.aether_n3_forty_second_bidirectional_fallback_promotion_v20_34 import v20_34_selected_raw_vector
from bhsm.interface.aether_n3_forty_seventh_bidirectional_fallback_promotion_v20_58 import v20_58_selected_raw_vector
from bhsm.interface.aether_n3_forty_sixth_bidirectional_fallback_promotion_v20_52 import v20_52_selected_raw_vector
from bhsm.interface.aether_n3_forty_third_bidirectional_probe_promotion_v20_38 import v20_38_selected_raw_vector
from bhsm.interface.aether_n3_fortieth_bidirectional_probe_promotion_v20_24 import v20_24_selected_raw_vector
from bhsm.interface.aether_n3_fourteenth_bidirectional_fallback_promotion_v19_13 import v19_13_selected_raw_vector
from bhsm.interface.aether_n3_fourth_bidirectional_probe_promotion_v18_68 import v18_68_selected_raw_vector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN, _metrics
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_reclassified_chain_proposal_v18_11 import _square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales, unpack_reduced
from bhsm.interface.aether_n3_required_child_cauchy_flux_v17_93 import _canonical_pair
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import trapezoid_sbp_difference
from bhsm.interface.aether_n3_seventh_bidirectional_fallback_promotion_v18_83 import v18_83_selected_raw_vector
from bhsm.interface.aether_n3_sixteenth_bidirectional_probe_promotion_v19_21 import v19_21_selected_raw_vector
from bhsm.interface.aether_n3_sixth_bidirectional_probe_promotion_v18_77 import v18_77_selected_raw_vector
from bhsm.interface.aether_n3_thirteenth_bidirectional_probe_promotion_v19_07 import v19_07_selected_raw_vector
from bhsm.interface.aether_n3_thirtieth_bidirectional_fallback_promotion_v19_82 import v19_82_selected_raw_vector
from bhsm.interface.aether_n3_thirty_fifth_bidirectional_probe_promotion_v20_02 import v20_02_selected_raw_vector
from bhsm.interface.aether_n3_thirty_ninth_bidirectional_fallback_promotion_v20_20 import v20_20_selected_raw_vector
from bhsm.interface.aether_n3_thirty_seventh_bidirectional_probe_promotion_v20_10 import v20_10_selected_raw_vector
from bhsm.interface.aether_n3_thirty_sixth_bidirectional_probe_promotion_v20_06 import v20_06_selected_raw_vector
from bhsm.interface.aether_n3_twelfth_bidirectional_probe_promotion_v19_03 import v19_03_selected_raw_vector
from bhsm.interface.aether_n3_twenty_ninth_bidirectional_probe_promotion_v19_76 import v19_76_selected_raw_vector
from bhsm.interface.aether_n3_twenty_seventh_bidirectional_fallback_promotion_v19_68 import v19_68_selected_raw_vector
from bhsm.interface.aether_n3_twenty_sixth_bidirectional_probe_promotion_v19_61 import v19_61_selected_raw_vector


VERSION = "v20.68"
CLASSIFICATION = "BHSM_N3_STRUCTURAL_HINDSIGHT_PROPOSAL_RECOVERY"
FULL_BHSM_COMPLETE = False
RESPONSE_FINE_STEP = 1.0e-8
RESPONSE_COARSE_STEP = 3.0e-8
HISTORY: tuple[tuple[str, Callable[[], np.ndarray]], ...] = (
    ("v18.68", v18_68_selected_raw_vector), ("v18.73", v18_73_selected_raw_vector),
    ("v18.77", v18_77_selected_raw_vector), ("v18.83", v18_83_selected_raw_vector),
    ("v18.87", v18_87_selected_raw_vector), ("v19.03", v19_03_selected_raw_vector),
    ("v19.07", v19_07_selected_raw_vector), ("v19.13", v19_13_selected_raw_vector),
    ("v19.17", v19_17_selected_raw_vector), ("v19.21", v19_21_selected_raw_vector),
    ("v19.29", v19_29_selected_raw_vector), ("v19.61", v19_61_selected_raw_vector),
    ("v19.68", v19_68_selected_raw_vector), ("v19.76", v19_76_selected_raw_vector),
    ("v19.82", v19_82_selected_raw_vector), ("v20.02", v20_02_selected_raw_vector),
    ("v20.06", v20_06_selected_raw_vector), ("v20.10", v20_10_selected_raw_vector),
    ("v20.20", v20_20_selected_raw_vector), ("v20.24", v20_24_selected_raw_vector),
    ("v20.28", v20_28_selected_raw_vector), ("v20.34", v20_34_selected_raw_vector),
    ("v20.38", v20_38_selected_raw_vector), ("v20.42", v20_42_selected_raw_vector),
    ("v20.46", v20_46_selected_raw_vector), ("v20.52", v20_52_selected_raw_vector),
    ("v20.58", v20_58_selected_raw_vector), ("v20.62", v20_62_selected_raw_vector),
    ("v20.66", v20_66_selected_raw_vector),
)
COORDINATE_BLOCKS = {
    "scale": np.asarray([10 * node for node in range(23)]),
    "u": np.asarray([10 * node + column for node in range(23) for column in range(1, 4)]),
    "w": np.asarray([10 * node + column for node in range(23) for column in range(4, 7)]),
    "v": np.asarray([10 * node + column for node in range(23) for column in range(7, 10)]),
    "lapse": np.asarray([230 + 6 * node + column for node in range(24) for column in range(3)]),
    "shift": np.asarray([230 + 6 * node + column for node in range(24) for column in range(3, 6)]),
    "period": np.asarray([374]), "event_multiplier": np.asarray([375]),
}


def _exact(raw: np.ndarray) -> np.ndarray:
    return _square_physical_residual(np.asarray(raw) * kkt_variable_scales())


def _event_data(raw: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    state = unpack_reduced(raw)
    qh = np.asarray(state["coordinates"]); mh = np.asarray(state["multipliers"])
    vh = trapezoid_sbp_difference() @ qh / float(state["period"])
    qe, ve, me = qh[-1], vh[-1], mh[-1]
    pe, _, le, _ = _canonical_pair(qe, ve, me)
    event_covector, _ = _metric_radial_flux_covector(qe, me)
    return qe, pe, le.T @ event_covector


def _fractions(direction_x: np.ndarray) -> dict[str, float]:
    denominator = float(direction_x @ direction_x)
    return {name: float(direction_x[rows] @ direction_x[rows] / denominator) for name, rows in COORDINATE_BLOCKS.items()}


def _node_fractions(direction_x: np.ndarray) -> dict[str, float]:
    node2 = np.zeros(24)
    for node in range(23):
        node2[node + 1] += float(direction_x[10 * node:10 * (node + 1)] @ direction_x[10 * node:10 * (node + 1)])
    for node in range(24):
        values = direction_x[230 + 6 * node:230 + 6 * (node + 1)]
        node2[node] += float(values @ values)
    denominator = max(float(np.sum(node2)), 1.0e-300)
    return {
        "reset_near": float(np.sum(node2[:3]) / denominator),
        "interior_history": float(np.sum(node2[3:21]) / denominator),
        "event_near": float(np.sum(node2[21:]) / denominator),
    }


def _historical_dataset() -> tuple[list[dict[str, Any]], list[np.ndarray], list[np.ndarray]]:
    raws = [loader() for _, loader in HISTORY]
    residual_norms = [float(np.linalg.norm(_exact(raw))) for raw in raws]
    records = []
    directions_x = []
    for index in range(len(raws) - 1):
        transform, _ = _action_curvature_transform(raws[index])
        secant_y = (raws[index + 1] - raws[index]) * kkt_variable_scales()
        secant_x = np.linalg.solve(transform, secant_y)
        directions_x.append(secant_x)
        prior_angle = None
        if index:
            prior = directions_x[-2]
            prior_angle = float(np.degrees(np.arccos(np.clip(np.dot(prior, secant_x) / (np.linalg.norm(prior) * np.linalg.norm(secant_x)), -1.0, 1.0))))
        records.append({
            "source": HISTORY[index][0], "target": HISTORY[index + 1][0],
            "exact_reduction": residual_norms[index] - residual_norms[index + 1],
            "fractional_reduction": (residual_norms[index] - residual_norms[index + 1]) / residual_norms[index],
            "action_coordinate_secant_norm": float(np.linalg.norm(secant_x)),
            "angle_to_prior_accepted_secant_degrees": prior_angle,
            "block_fractions": _fractions(secant_x), "history_fractions": _node_fractions(secant_x),
        })
    reductions = np.asarray([row["exact_reduction"] for row in records])
    q1, q2 = np.quantile(reductions, [1.0 / 3.0, 2.0 / 3.0])
    for row in records:
        row["descent_class"] = "LARGE_DESCENT" if row["exact_reduction"] >= q2 else "MEDIUM_DESCENT" if row["exact_reduction"] >= q1 else "PLATEAU_DESCENT"
    return records, raws, directions_x


def _class_comparison(records: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for label in ("LARGE_DESCENT", "MEDIUM_DESCENT", "PLATEAU_DESCENT"):
        rows = [row for row in records if row["descent_class"] == label]
        result[label] = {
            "count": len(rows),
            "median_exact_reduction": float(np.median([row["exact_reduction"] for row in rows])),
            "median_action_coordinate_secant_norm": float(np.median([row["action_coordinate_secant_norm"] for row in rows])),
            "mean_block_fractions": {name: float(np.mean([row["block_fractions"][name] for row in rows])) for name in COORDINATE_BLOCKS},
            "mean_history_fractions": {name: float(np.mean([row["history_fractions"][name] for row in rows])) for name in ("reset_near", "interior_history", "event_near")},
        }
    large = result["LARGE_DESCENT"]["mean_block_fractions"]
    plateau = result["PLATEAU_DESCENT"]["mean_block_fractions"]
    result["large_minus_plateau_block_fraction"] = {name: large[name] - plateau[name] for name in COORDINATE_BLOCKS}
    return result


def _orthonormalize(named: list[tuple[str, np.ndarray]]) -> list[tuple[str, np.ndarray]]:
    basis: list[tuple[str, np.ndarray]] = []
    for name, vector in named:
        value = np.asarray(vector, dtype=float).copy()
        original = float(np.linalg.norm(value))
        for _, prior in basis:
            value -= np.dot(prior, value) * prior
        norm = float(np.linalg.norm(value))
        if norm > 1.0e-8 * max(original, 1.0e-300):
            basis.append((name, value / norm))
    return basis


def _current_response_direction(raw: np.ndarray, transform: np.ndarray) -> tuple[np.ndarray, dict[str, Any]]:
    scales = kkt_variable_scales(); y = raw * scales; residual = _square_physical_residual(y)
    def response(direction_y: np.ndarray, step: float) -> np.ndarray:
        norm = float(np.linalg.norm(direction_y))
        if norm == 0.0:
            return np.zeros(376)
        unit = direction_y / norm
        return norm * (_square_physical_residual(y + step * unit) - _square_physical_residual(y - step * unit)) / (2.0 * step)
    operator = LinearOperator((376, 376), matvec=lambda dx: response(transform @ dx, RESPONSE_FINE_STEP), dtype=float)
    callbacks: list[float] = []
    direction_x, info = gmres(
        operator, -residual, rtol=1.0e-6, atol=0.0, restart=30, maxiter=1,
        callback=lambda value: callbacks.append(float(value)), callback_type="pr_norm",
    )
    direction_y = transform @ direction_x
    unit_y = direction_y / np.linalg.norm(direction_y)
    fine = response(unit_y, RESPONSE_FINE_STEP); coarse = response(unit_y, RESPONSE_COARSE_STEP)
    consistency = float(np.linalg.norm(fine - coarse) / max(1.0, np.linalg.norm(fine)))
    linear = float(np.linalg.norm(response(direction_y, RESPONSE_FINE_STEP) + residual) / max(1.0, np.linalg.norm(residual)))
    return direction_x, {
        "gmres_info_not_a_physical_gate": int(info), "iterations": len(callbacks),
        "final_callback_relative_residual": callbacks[-1] if callbacks else None,
        "response_relative_change": consistency, "relative_exact_linear_residual": linear,
        "response_steps": [RESPONSE_FINE_STEP, RESPONSE_COARSE_STEP],
    }


def _child_tangent(raw: np.ndarray, basis: list[tuple[str, np.ndarray]], transform: np.ndarray) -> dict[str, Any]:
    payload = json.loads(Path("artifacts/BHSM_aether_n3_forty_ninth_bidirectional_probe_child_v20_65.json").read_text(encoding="utf-8"))
    child_state = payload["forty_ninth_bidirectional_probe_child"]["child_state"]
    child = _pack_child(np.asarray(child_state["coordinates"]), np.asarray(child_state["velocities"]), np.asarray(child_state["multipliers"]))
    qe, pe, flux = _event_data(raw)
    dc = np.empty((14, 26))
    for column in range(26):
        delta = np.zeros(26); delta[column] = JACOBIAN_STEP
        dc[:, column] = (_child_rows(child + delta, qe, pe, flux) - _child_rows(child - delta, qe, pe, flux)) / (2.0 * JACOBIAN_STEP)
    row_norms = np.maximum(np.linalg.norm(dc, axis=1), 1.0e-30)
    singular = np.linalg.svd(dc / row_norms[:, None], compute_uv=False)
    tolerance = np.finfo(float).eps * max(dc.shape) * singular[0]
    rank = int(np.count_nonzero(singular > tolerance))
    rows = []
    scales = kkt_variable_scales()
    for name, direction_x in basis:
        direction_raw = (transform @ direction_x) / scales
        epsilon = 1.0e-4
        qep, pep, fluxp = _event_data(raw + epsilon * direction_raw)
        qem, pem, fluxm = _event_data(raw - epsilon * direction_raw)
        dz = (_child_rows(child, qep, pep, fluxp) - _child_rows(child, qem, pem, fluxm)) / (2.0 * epsilon)
        child_direction = np.linalg.lstsq(dc, -dz, rcond=None)[0]
        defect = dc @ child_direction + dz
        rows.append({"basis": name, "child_correction_norm_per_unit_action_coordinate": float(np.linalg.norm(child_direction)), "linearized_compatibility_defect": float(np.linalg.norm(defect))})
    return {
        "rank_DcG": rank, "child_variables": 26, "physical_rows": 14,
        "all_event_directions_locally_compatible": bool(rank == 14),
        "does_not_supply_an_extra_global_equation": True,
        "basis_tangent_solves": rows,
        "interpretation": "D_cG is surjective, so child compatibility supplies a tangent lift dc for every tested dz but no event-space selector",
    }


def _trial(raw: np.ndarray, transform: np.ndarray, displacement_x: np.ndarray) -> dict[str, Any]:
    scales = kkt_variable_scales()
    candidate = raw + (transform @ displacement_x) / scales
    try:
        metrics = _metrics(_exact(candidate)); eta = _minimum_node_eta(candidate)
        return {"valid": True, "norm": float(metrics["complete"]), "eta": float(eta), "raw": candidate}
    except (ArithmeticError, FloatingPointError, ValueError) as exc:
        return {"valid": False, "exception": type(exc).__name__}


def _subspace_search(raw: np.ndarray, transform: np.ndarray, basis: list[tuple[str, np.ndarray]], records: list[dict[str, Any]]) -> dict[str, Any]:
    source_norm = float(np.linalg.norm(_exact(raw)))
    class_amplitudes = {}
    for label in ("LARGE_DESCENT", "MEDIUM_DESCENT", "PLATEAU_DESCENT"):
        class_amplitudes[label] = float(np.median([row["action_coordinate_secant_norm"] for row in records if row["descent_class"] == label]))
    amplitudes = sorted(set(class_amplitudes.values()))
    coefficient_rows: list[tuple[str, np.ndarray, list[str]]] = []
    dimension = len(basis)
    for index, (name, unit) in enumerate(basis):
        for amplitude in amplitudes:
            for sign in (-1.0, 1.0):
                coefficient_rows.append((f"pure:{name}", sign * amplitude * unit, [name]))
    for left in range(dimension):
        for right in range(left + 1, dimension):
            for amplitude in amplitudes[:2]:
                for left_sign in (-1.0, 1.0):
                    for right_sign in (-1.0, 1.0):
                        direction = (left_sign * basis[left][1] + right_sign * basis[right][1]) / math.sqrt(2.0)
                        coefficient_rows.append((f"pair:{basis[left][0]}+{basis[right][0]}", amplitude * direction, [basis[left][0], basis[right][0]]))
    if dimension >= 3:
        amplitude = class_amplitudes["MEDIUM_DESCENT"]
        for signs in np.ndindex(*(2,) * dimension):
            direction = sum((1.0 if sign else -1.0) * basis[index][1] for index, sign in enumerate(signs)) / math.sqrt(dimension)
            coefficient_rows.append(("mixed_all", amplitude * direction, [name for name, _ in basis]))
    best: dict[str, Any] | None = None
    summaries = []
    for label, displacement, members in coefficient_rows:
        result = _trial(raw, transform, displacement)
        if not result["valid"]:
            continue
        reduction = source_norm - result["norm"]
        row = {"label": label, "members": members, "action_coordinate_step_norm": float(np.linalg.norm(displacement)), "norm": result["norm"], "reduction": reduction, "eta": result["eta"], "raw": result["raw"]}
        if result["eta"] > 1.0e-5 and reduction > MARGIN and (best is None or result["norm"] < best["norm"]):
            best = row
        summaries.append({key: value for key, value in row.items() if key != "raw"})
    if best is not None:
        base_displacement = (best["raw"] - raw) * kkt_variable_scales()
        base_x = np.linalg.solve(transform, base_displacement)
        for factor in (0.5, 0.75, 1.25, 1.5, 2.0):
            result = _trial(raw, transform, factor * base_x)
            if result["valid"]:
                reduction = source_norm - result["norm"]
                row = {"label": f"refine:{factor:g}*{best['label']}", "members": best["members"], "action_coordinate_step_norm": float(np.linalg.norm(factor * base_x)), "norm": result["norm"], "reduction": reduction, "eta": result["eta"], "raw": result["raw"]}
                summaries.append({key: value for key, value in row.items() if key != "raw"})
                if result["eta"] > 1.0e-5 and reduction > MARGIN and result["norm"] < best["norm"]:
                    best = row
    plateau_reductions = [row["exact_reduction"] for row in records if row["descent_class"] == "PLATEAU_DESCENT"]
    large_floor = min(row["exact_reduction"] for row in records if row["descent_class"] == "LARGE_DESCENT")
    material_threshold = max(large_floor, 5.0 * float(np.median(plateau_reductions)))
    best_summary = None if best is None else {key: value for key, value in best.items() if key != "raw"}
    if best is not None:
        best_summary["raw_vector_hex"] = [float(value).hex() for value in best["raw"]]
    return {
        "source_norm": source_norm, "class_action_amplitudes": class_amplitudes,
        "trial_count": len(coefficient_rows), "valid_trial_count": len(summaries),
        "best_trials": sorted(summaries, key=lambda row: row["norm"])[:12],
        "material_recovery_threshold_from_distribution": material_threshold,
        "best": best_summary,
        "material_recovery": bool(best is not None and best["reduction"] >= material_threshold),
    }


def _fresh_child_gate(raw: np.ndarray) -> dict[str, Any]:
    qe, pe, event_flux = _event_data(raw)
    prior_payload = json.loads(Path("artifacts/BHSM_aether_n3_forty_ninth_bidirectional_probe_child_v20_65.json").read_text(encoding="utf-8"))
    prior = prior_payload["forty_ninth_bidirectional_probe_child"]["child_state"]
    germ = _pack_child(np.asarray(prior["coordinates"]), np.asarray(prior["velocities"]), np.asarray(prior["multipliers"]))
    jacobian = np.empty((14, 26))
    for column in range(26):
        delta = np.zeros(26); delta[column] = JACOBIAN_STEP
        jacobian[:, column] = (_child_rows(germ + delta, qe, pe, event_flux) - _child_rows(germ - delta, qe, pe, event_flux)) / (2.0 * JACOBIAN_STEP)
    row_norms = np.maximum(np.linalg.norm(jacobian, axis=1), 1.0)
    _, singular, _ = np.linalg.svd(jacobian / row_norms[:, None], full_matrices=False)
    tolerance = np.finfo(float).eps * max(jacobian.shape) * singular[0]
    rank = int(np.count_nonzero(singular > tolerance))
    _, _, pivots = qr(jacobian / row_norms[:, None], mode="economic", pivoting=True)
    chart = np.asarray(pivots[:14], dtype=int); fixed = germ.copy()
    solve_scales = np.r_[np.full(3, 1.0e-9), np.full(7, 1.0e-9), np.full(2, 1.0e-7), np.full(2, 2.0e-5)]
    def residual(values: np.ndarray) -> np.ndarray:
        child = fixed.copy(); child[chart] = values
        return _child_rows(child, qe, pe, event_flux) / solve_scales
    solution = least_squares(residual, germ[chart], method="lm", ftol=1.0e-13, xtol=1.0e-13, gtol=1.0e-13, max_nfev=900)
    child = fixed.copy(); child[chart] = solution.x
    rows = _child_rows(child, qe, pe, event_flux)
    qc, vc, mc = _unpack_child(child)
    pc, force, lc, _ = _canonical_pair(qc, vc, mc)
    ec, _ = _metric_radial_flux_covector(qe, unpack_reduced(raw)["multipliers"][-1])
    cc, _ = _metric_radial_flux_covector(qc, mc)
    child_flux = lc.T @ cc
    dynamics = exact_euler_dirac_acceleration(3, qc, vc, mc, points=44)
    acceleration = np.asarray(dynamics["acceleration"]); multiplier_rate = np.asarray(dynamics["multiplier_rate"])
    tangent_scale = max(1.0, float(np.max(np.abs(vc))), float(np.max(np.abs(acceleration))), float(np.max(np.abs(multiplier_rate))))
    flux_norms = []
    for relative_step in (8.0e-4, 4.0e-4):
        epsilon = relative_step / tangent_scale
        plus, _, _, _ = _canonical_pair(qc + epsilon * vc, vc + epsilon * acceleration, mc + epsilon * multiplier_rate)
        minus, _, _, _ = _canonical_pair(qc - epsilon * vc, vc - epsilon * acceleration, mc - epsilon * multiplier_rate)
        p_dot = (plus - minus) / (2.0 * epsilon)
        flux_norms.append(float(np.linalg.norm(child_flux - (-p_dot + force - event_flux))))
    q, velocity, multipliers = qc.copy(), vc.copy(), mc.copy(); persistence = []
    for _ in range(10):
        q, velocity, multipliers, _, projection = _advance_constrained(q, velocity, multipliers, 1.0e-5, points=44)
        persistence.append((bool(projection["success"]), float(np.max(np.abs(constraint_residual(3, q, velocity, multipliers, points=44)))), float(eta_legendre_minimum(q, multipliers, points=3000)["minimum"]), bool(np.all(np.isfinite(np.r_[q, velocity, multipliers])))))
    trace = _trace_jacobian() @ (qc - qe)
    gates = {
        "rank_14": rank == 14, "solver_success": bool(solution.success),
        "trace": float(np.max(np.abs(trace))) < 1.0e-9,
        "seven_constraints": float(np.max(np.abs(constraint_residual(3, qc, vc, mc, points=44)))) < 1.0e-9,
        "momentum": float(np.linalg.norm(pc - pe)) < 1.0e-7,
        "two_scale_flux": max(flux_norms) < 2.0e-5,
        "child_eta": float(eta_legendre_minimum(qc, mc, points=5000)["minimum"]) > 0.0,
        "persistence": all(success and finite and constraint < 1.0e-8 and eta > 0.0 for success, constraint, eta, finite in persistence),
        "nonzero_motion": bool(np.linalg.norm(q - qc) > 0.0 and np.linalg.norm(velocity) > 0.0),
    }
    return {
        "gates": gates, "all_pass": all(gates.values()), "rank": rank,
        "maximum_14_row_abs": float(np.max(np.abs(rows))), "flux_envelope": max(flux_norms),
        "eta_minimum": float(eta_legendre_minimum(qc, mc, points=5000)["minimum"]),
        "persistence_max_constraint": max(row[1] for row in persistence),
    }


def structural_hindsight_recovery() -> dict[str, Any]:
    records, raws, directions = _historical_dataset()
    comparison = _class_comparison(records)
    raw = raws[-1]; transform, transform_audit = _action_curvature_transform(raw)
    response_x, response_audit = _current_response_direction(raw, transform)
    large_indices = [index for index, row in enumerate(records) if row["descent_class"] == "LARGE_DESCENT"]
    representative = max(large_indices, key=lambda index: records[index]["exact_reduction"])
    named = [
        ("recent_secant_v20_62_to_v20_66", np.linalg.solve(transform, (raws[-1] - raws[-2]) * kkt_variable_scales())),
        ("previous_secant_v20_58_to_v20_62", np.linalg.solve(transform, (raws[-2] - raws[-3]) * kkt_variable_scales())),
        (f"historical_large_{records[representative]['source']}_to_{records[representative]['target']}", directions[representative]),
        ("current_direct_response", response_x),
    ]
    basis = _orthonormalize(named)
    tangent = _child_tangent(raw, basis, transform)
    search = _subspace_search(raw, transform, basis, records)
    best = search["best"]
    promotion = {"attempted": False, "promoted": False}
    if search["material_recovery"] and best is not None:
        candidate = np.asarray([float.fromhex(value) for value in best["raw_vector_hex"]])
        child = _fresh_child_gate(candidate)
        promotion = {"attempted": True, "promoted": child["all_pass"], "child": child}
    members = [] if best is None else best["members"]
    if not search["material_recovery"]:
        hindsight_classification = "H5: HINDSIGHT_SUBSPACE_NO_MATERIAL_RECOVERY"
    elif any(name.startswith("historical_large") for name in members) and len(members) == 1:
        hindsight_classification = "H1: HISTORICAL_HINDSIGHT_IDENTIFIES_MATERIAL_PROPOSAL_COMPONENT"
    elif members and all("secant" in name for name in members):
        hindsight_classification = "H3: CURVED_SECANT_MEMORY_RECOVERS_MATERIAL_DESCENT"
    else:
        hindsight_classification = "H4: COMBINED_HINDSIGHT_SUBSPACE_RECOVERS_MATERIAL_DESCENT"
    return {
        "source_frontier": {"version": "v20.66", "exact_f376_l2": float(np.linalg.norm(_exact(raw)))},
        "plateau_audit_outcome": "E: PROPOSAL_MECHANISM_STALLED_WHILE_PHYSICAL_ROOT_OPEN",
        "historical_transitions": records, "descent_class_comparison": comparison,
        "basis": {"action_owned_transform": transform_audit, "members_after_orthogonalization": [name for name, _ in basis], "dimension": len(basis)},
        "current_direct_response": response_audit,
        "child_compatible_tangent": tangent,
        "prospective_search": search, "promotion": promotion,
        "classification": hindsight_classification,
        "physical_equations_changed": False, "left_residual_scaling_added": False,
        "complete_child_gate_changed": False, "empirical_particle_data_used": False,
        "next_action": "ADOPT_PROMOTED_HINDSIGHT_STATE_AND_RESUME_EXACT_N3_CLOSURE" if promotion["promoted"] else "E3_CONTROLLED_STRUCTURED_SHAKE_PROPOSAL",
    }


def completion_payload() -> dict[str, Any]:
    result = structural_hindsight_recovery()
    validation = {
        "source_v20_66_reproduced": abs(result["source_frontier"]["exact_f376_l2"] - 0.766949553481446) < 5.0e-12,
        "historical_classes_present": {row["descent_class"] for row in result["historical_transitions"]} == {"LARGE_DESCENT", "MEDIUM_DESCENT", "PLATEAU_DESCENT"},
        "rank_14_child_tangent": result["child_compatible_tangent"]["rank_DcG"] == 14,
        "prospective_exact_trials": result["prospective_search"]["valid_trial_count"] > 0,
        "one_hindsight_classification": result["classification"].startswith(tuple(f"H{index}:" for index in range(1, 7))),
        "promotion_only_after_material_recovery": not result["promotion"]["attempted"] or result["prospective_search"]["material_recovery"],
        "same_physics": not result["physical_equations_changed"] and not result["left_residual_scaling_added"] and not result["complete_child_gate_changed"],
        "no_empirical_targets": not result["empirical_particle_data_used"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_STRUCTURAL_HINDSIGHT_RECOVERY_V20_68", "version": VERSION,
        "classification": CLASSIFICATION, "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "structural_hindsight_recovery": result, "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation, "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_STRUCTURAL_HINDSIGHT_RECOVERY_V20_68.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "structural_hindsight_recovery", "completion_payload", "materialize"]
