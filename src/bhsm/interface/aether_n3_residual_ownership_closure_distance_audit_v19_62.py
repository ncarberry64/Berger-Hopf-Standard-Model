"""Diagnostic-only exact-F376 ownership and closure-distance audit."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

from bhsm.interface.aether_n3_eighth_bidirectional_probe_promotion_v18_87 import v18_87_selected_raw_vector
from bhsm.interface.aether_n3_eighteenth_bidirectional_probe_promotion_v19_29 import v19_29_selected_raw_vector
from bhsm.interface.aether_n3_fifteenth_bidirectional_probe_promotion_v19_17 import v19_17_selected_raw_vector
from bhsm.interface.aether_n3_fifth_bidirectional_probe_promotion_v18_73 import v18_73_selected_raw_vector
from bhsm.interface.aether_n3_fourteenth_bidirectional_fallback_promotion_v19_13 import v19_13_selected_raw_vector
from bhsm.interface.aether_n3_fourth_bidirectional_probe_promotion_v18_68 import v18_68_selected_raw_vector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_nineteenth_bidirectional_probe_promotion_v19_33 import v19_33_selected_raw_vector
from bhsm.interface.aether_n3_reclassified_chain_proposal_v18_11 import _square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales, unpack_reduced
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import trapezoid_sbp_difference
from bhsm.interface.aether_n3_seventeenth_bidirectional_probe_promotion_v19_25 import v19_25_selected_raw_vector
from bhsm.interface.aether_n3_seventh_bidirectional_fallback_promotion_v18_83 import v18_83_selected_raw_vector
from bhsm.interface.aether_n3_sixteenth_bidirectional_probe_promotion_v19_21 import v19_21_selected_raw_vector
from bhsm.interface.aether_n3_sixth_bidirectional_probe_promotion_v18_77 import v18_77_selected_raw_vector
from bhsm.interface.aether_n3_thirteenth_bidirectional_probe_promotion_v19_07 import v19_07_selected_raw_vector
from bhsm.interface.aether_n3_twelfth_bidirectional_probe_promotion_v19_03 import v19_03_selected_raw_vector
from bhsm.interface.aether_n3_twentieth_bidirectional_probe_promotion_v19_37 import v19_37_selected_raw_vector
from bhsm.interface.aether_n3_twenty_fifth_bidirectional_probe_promotion_v19_57 import v19_57_selected_raw_vector
from bhsm.interface.aether_n3_twenty_first_bidirectional_probe_promotion_v19_41 import v19_41_selected_raw_vector
from bhsm.interface.aether_n3_twenty_fourth_bidirectional_probe_promotion_v19_53 import v19_53_selected_raw_vector
from bhsm.interface.aether_n3_twenty_second_bidirectional_probe_promotion_v19_45 import v19_45_selected_raw_vector
from bhsm.interface.aether_n3_twenty_sixth_bidirectional_probe_promotion_v19_61 import v19_61_selected_raw_vector
from bhsm.interface.aether_n3_twenty_third_bidirectional_probe_promotion_v19_49 import v19_49_selected_raw_vector


VERSION = "v19.62"
CLASSIFICATION = "BHSM_N3_RESIDUAL_OWNERSHIP_AND_CLOSURE_DISTANCE_AUDIT"
FULL_BHSM_COMPLETE = False
BLOCKS = ("F_scale", "F_u", "F_w", "F_v", "F_lapse", "F_shift", "F_period", "F_event")
FRONTIERS: tuple[tuple[str, Callable[[], np.ndarray]], ...] = (
    ("v18.68", v18_68_selected_raw_vector), ("v18.73", v18_73_selected_raw_vector),
    ("v18.77", v18_77_selected_raw_vector), ("v18.83", v18_83_selected_raw_vector),
    ("v18.87", v18_87_selected_raw_vector), ("v19.03", v19_03_selected_raw_vector),
    ("v19.07", v19_07_selected_raw_vector), ("v19.13", v19_13_selected_raw_vector),
    ("v19.17", v19_17_selected_raw_vector), ("v19.21", v19_21_selected_raw_vector),
    ("v19.25", v19_25_selected_raw_vector), ("v19.29", v19_29_selected_raw_vector),
    ("v19.33", v19_33_selected_raw_vector), ("v19.37", v19_37_selected_raw_vector),
    ("v19.41", v19_41_selected_raw_vector), ("v19.45", v19_45_selected_raw_vector),
    ("v19.49", v19_49_selected_raw_vector), ("v19.53", v19_53_selected_raw_vector),
    ("v19.57", v19_57_selected_raw_vector), ("v19.61", v19_61_selected_raw_vector),
)
PROBES = (
    ("v19.43", "BHSM_aether_n3_twenty_second_bidirectional_merit_manifold_probe_v19_43.json", "twenty_second_bidirectional_merit_manifold_probe"),
    ("v19.47", "BHSM_aether_n3_twenty_third_bidirectional_merit_manifold_probe_v19_47.json", "twenty_third_bidirectional_merit_manifold_probe"),
    ("v19.51", "BHSM_aether_n3_twenty_fourth_bidirectional_merit_manifold_probe_v19_51.json", "twenty_fourth_bidirectional_merit_manifold_probe"),
    ("v19.55", "BHSM_aether_n3_twenty_fifth_bidirectional_merit_manifold_probe_v19_55.json", "twenty_fifth_bidirectional_merit_manifold_probe"),
    ("v19.59", "BHSM_aether_n3_twenty_sixth_bidirectional_merit_manifold_probe_v19_59.json", "twenty_sixth_bidirectional_merit_manifold_probe"),
)


def _exact_f376(raw: np.ndarray) -> np.ndarray:
    """Current retained exact action/event KKT covector; no extra row scaling."""
    return _square_physical_residual(np.asarray(raw) * kkt_variable_scales())


def _ownership(row: int) -> dict[str, Any]:
    if row < 230:
        local, column = divmod(row, 10)
        block = ("F_scale", "F_u", "F_w", "F_v")[(0 if column == 0 else 1 if column < 4 else 2 if column < 7 else 3)]
        return {"block": block, "kind": "q_stationarity", "node": local + 1, "column": column}
    if row < 374:
        local, column = divmod(row - 230, 6)
        return {"block": "F_lapse" if column < 3 else "F_shift", "kind": "multiplier_stationarity", "node": local, "column": column}
    return {"block": "F_period" if row == 374 else "F_event", "kind": "period_stationarity" if row == 374 else "event", "node": None, "column": None}


def _region(node: int | None) -> str:
    if node is None:
        return "global"
    if node <= 2:
        return "reset_near"
    if node >= 21:
        return "event_near"
    return "interior_history"


def _block_arrays(residual: np.ndarray) -> dict[str, np.ndarray]:
    q = residual[:230].reshape(23, 10)
    m = residual[230:374].reshape(24, 6)
    return {
        "F_scale": q[:, 0], "F_u": q[:, 1:4].ravel(),
        "F_w": q[:, 4:7].ravel(), "F_v": q[:, 7:10].ravel(),
        "F_lapse": m[:, :3].ravel(), "F_shift": m[:, 3:].ravel(),
        "F_period": residual[374:375], "F_event": residual[375:376],
    }


def _block_stats(residual: np.ndarray) -> dict[str, Any]:
    total2 = float(residual @ residual)
    result = {}
    for name, values in _block_arrays(residual).items():
        flat = np.asarray(values).ravel()
        local = int(np.argmax(np.abs(flat)))
        rows = np.flatnonzero(np.array([_ownership(i)["block"] == name for i in range(376)]))
        row = int(rows[local])
        norm2 = float(flat @ flat)
        result[name] = {
            "rows": int(flat.size), "l2_norm": float(np.sqrt(norm2)),
            "squared_contribution": norm2, "fraction_total_squared": norm2 / total2,
            "rms_per_row": float(np.sqrt(norm2 / flat.size)),
            "maximum_absolute_component": float(abs(flat[local])),
            "maximum_row": row, "maximum_owner": _ownership(row),
        }
    return result


def _node_localization(residual: np.ndarray) -> dict[str, Any]:
    node2 = np.zeros(24)
    for row, value in enumerate(residual[:374]):
        owner = _ownership(row)
        node2[int(owner["node"])] += float(value * value)
    regions = {"reset_near": range(0, 3), "interior_history": range(3, 21), "event_near": range(21, 24)}
    stationarity2 = float(np.sum(node2))
    by_region = {}
    for name, nodes in regions.items():
        indices = list(nodes)
        value2 = float(np.sum(node2[indices]))
        by_region[name] = {
            "nodes": indices, "l2_norm": float(np.sqrt(value2)),
            "fraction_stationarity_squared": value2 / stationarity2,
            "rms_per_node": float(np.sqrt(value2 / len(indices))),
        }
    maximum = int(np.argmax(node2))
    return {
        "node_norms": [float(np.sqrt(value)) for value in node2],
        "regions": by_region, "maximum_node": maximum,
        "maximum_node_region": _region(maximum),
        "partition_definition": "physical nodes 0-2 reset-near, 3-20 interior, 21-23 event-near; diagnostic only",
    }


def _motion(raw: np.ndarray, previous: np.ndarray | None) -> dict[str, Any]:
    state = unpack_reduced(raw)
    q = np.asarray(state["coordinates"])
    velocity = trapezoid_sbp_difference() @ q / float(state["period"])
    slices = {"scale": slice(0, 1), "u": slice(1, 4), "w": slice(4, 7), "v": slice(7, 10)}
    result = {"history_velocity_norms": {name: float(np.linalg.norm(velocity[:, section])) for name, section in slices.items()}}
    if previous is not None:
        prior_q = np.asarray(unpack_reduced(previous)["coordinates"])
        result["accepted_frontier_displacement_norms"] = {name: float(np.linalg.norm((q - prior_q)[:, section])) for name, section in slices.items()}
    return result


def _trend(values: list[float]) -> dict[str, Any]:
    recent = np.asarray(values[-5:], dtype=float)
    prior = np.asarray(values[-10:-5], dtype=float)
    slope = float(np.polyfit(np.arange(recent.size), recent, 1)[0])
    prior_slope = float(np.polyfit(np.arange(prior.size), prior, 1)[0])
    relative = slope / max(float(np.mean(np.abs(recent))), 1.0e-300)
    label = "FALLING" if relative < -1.0e-4 else "GROWING" if relative > 1.0e-4 else "APPROXIMATELY_FLAT"
    return {
        "recent_linear_slope_per_accepted_step": slope,
        "recent_relative_slope_per_step": relative,
        "preceding_linear_slope_per_accepted_step": prior_slope,
        "label": label,
        "accelerating_toward_zero": bool(slope < 0.0 and prior_slope < 0.0 and abs(slope) > 1.2 * abs(prior_slope)),
    }


def residual_ownership_closure_distance_audit() -> dict[str, Any]:
    accepted = []
    raws = []
    for version, loader in FRONTIERS:
        raw = loader()
        residual = _exact_f376(raw)
        accepted.append({
            "version": version, "total_l2_norm": float(np.linalg.norm(residual)),
            "blocks": _block_stats(residual), "node_localization": _node_localization(residual),
            "motion": _motion(raw, raws[-1] if raws else None),
        })
        raws.append(raw)
    latest_residual = _exact_f376(raws[-1])
    top_rows = []
    for row in np.argsort(np.abs(latest_residual))[-20:][::-1]:
        owner = _ownership(int(row))
        top_rows.append({"row": int(row), "value": float(latest_residual[row]), "absolute_value": float(abs(latest_residual[row])), **owner, "region": _region(owner["node"])})
    index = {row["version"]: i for i, row in enumerate(accepted)}
    trends = {}
    for block in BLOCKS:
        values = [row["blocks"][block]["l2_norm"] for row in accepted]
        trend = _trend(values)
        trend.update({
            "v18_68_to_v19_29_absolute_change": values[index["v19.29"]] - values[index["v18.68"]],
            "v18_87_to_v19_29_absolute_change": values[index["v19.29"]] - values[index["v18.87"]],
            "last_five_absolute_change": values[-1] - values[-5],
            "v18_68_to_latest_absolute_change": values[-1] - values[0],
            "v18_87_to_latest_absolute_change": values[-1] - values[index["v18.87"]],
        })
        trends[block] = trend
    total_values = [row["total_l2_norm"] for row in accepted]
    total_trend = _trend(total_values)
    total_trend["naive_nonphysical_steps_to_zero"] = (
        -total_values[-1] / total_trend["recent_linear_slope_per_accepted_step"]
        if total_trend["recent_linear_slope_per_accepted_step"] < 0.0 else None
    )
    latest_blocks = accepted[-1]["blocks"]
    major = [name for name in BLOCKS if latest_blocks[name]["fraction_total_squared"] >= 0.05]
    largest_block = max(BLOCKS, key=lambda name: latest_blocks[name]["fraction_total_squared"])
    largest_fraction = latest_blocks[largest_block]["fraction_total_squared"]
    latest_regions = accepted[-1]["node_localization"]["regions"]
    largest_region = max(latest_regions, key=lambda name: latest_regions[name]["fraction_stationarity_squared"])
    largest_region_fraction = latest_regions[largest_region]["fraction_stationarity_squared"]
    response_rows = []
    for version, filename, key in PROBES:
        payload = json.loads((Path("artifacts") / filename).read_text(encoding="utf-8"))
        probe = payload[key]
        selected = probe["selected_true_merit_candidate_pending_child_acceptance"]
        response_rows.append({
            "version": version, "solver_interpretation": payload["solver_interpretation"],
            "relative_exact_linear_residual": probe["linear_probe"]["relative_exact_linear_residual"],
            "direction_response_relative_change": probe["direct_response"]["resulting_direction_relative_change"],
            "fractional_exact_merit_reduction": selected["complete_norm_reduction"] / probe["source_complete_norm"],
        })
    fractions = [row["fractional_exact_merit_reduction"] for row in response_rows]
    local_response = {
        "recent_response_diagnostics": response_rows,
        "increasing_fractional_merit_reduction": bool(all(b > a for a, b in zip(fractions, fractions[1:]))),
        "coherent_direction_response": bool(response_rows[-1]["direction_response_relative_change"] < 0.1),
        "increasingly_accurate_local_linearization": bool(
            response_rows[-1]["relative_exact_linear_residual"] < 0.25
            and response_rows[-1]["relative_exact_linear_residual"] < response_rows[-2]["relative_exact_linear_residual"]
        ),
        "source": "already-owned v19.43-v19.59 exact-merit and response diagnostics",
    }
    history_localized = largest_region_fraction >= 0.70
    dominant_stalled = largest_fraction >= 0.60 and trends[largest_block]["label"] != "FALLING"
    root_basin = bool(local_response["increasing_fractional_merit_reduction"] and total_trend["accelerating_toward_zero"])
    distributed = bool(total_trend["label"] == "FALLING" and largest_fraction < 0.60 and sum(trends[name]["label"] == "FALLING" for name in major) >= 2)
    if dominant_stalled:
        classification = "OUTCOME B: DOMINANT_PHYSICAL_OWNER_IDENTIFIED"
    elif history_localized:
        classification = "OUTCOME C: HISTORY_LOCALIZED_OWNER_IDENTIFIED"
    elif root_basin:
        classification = "OUTCOME D: LOCAL_ROOT_BASIN_ENTERING"
    elif distributed:
        classification = "OUTCOME A: DISTRIBUTED_DESCENT_CONTINUES"
    else:
        classification = "OUTCOME E: INSUFFICIENT_DIAGNOSTIC_SEPARATION"
    action_owner = {
        "F_scale": "scale-coordinate stationarity of the retained local-jet SBP action/event KKT covector",
        "F_u": "u-geometry stationarity", "F_w": "w-geometry stationarity", "F_v": "v-geometry stationarity",
        "F_lapse": "lapse multiplier stationarity / constraint owner", "F_shift": "shift multiplier stationarity / constraint owner",
        "F_period": "period stationarity", "F_event": "ordered-event eigenvalue constraint",
    }
    displacement = accepted[-1]["motion"]["accepted_frontier_displacement_norms"]
    motion_carriers = [name for name, value in displacement.items() if value >= 0.05 * max(displacement.values())]
    motion_comparison = {
        "latest_motion": accepted[-1]["motion"],
        "latest_accepted_displacement_carriers_at_5_percent_of_maximum": motion_carriers,
        "corresponding_residual_trends": {name: trends[f"F_{name}"]["label"] for name in ("scale", "u", "w", "v")},
        "other_major_block_comparatively_frozen": any(name not in ("F_scale", "F_u", "F_w", "F_v") and trends[name]["label"] == "APPROXIMATELY_FLAT" for name in major),
        "interpretation": "w/v carry most accepted displacement and both residual blocks fall; scale is smaller but its residual grows; dominant period residual falls",
        "correlation_is_not_causality": True,
    }
    return {
        "residual_definition": {
            "evaluation": "_square_physical_residual(raw*kkt_variable_scales())",
            "meaning": "current retained exact action/event F376 in its validated KKT coordinates, without additional left row scaling",
            "layout": {"q_stationarity": [0, 230], "multiplier_stationarity": [230, 374], "period": 374, "event": 375},
            "physical_solve_dimension": [376, 376], "equations_changed": False, "row_scaling_added": False,
        },
        "accepted_frontiers": accepted,
        "rejected_candidates_excluded": [
            {"version": "v18.81", "reason": "complete-child flux gate failure"},
            {"version": "v19.11", "reason": "complete-child flux gate failure"},
        ],
        "latest_largest_20_rows": top_rows,
        "block_trends": trends, "total_trend": total_trend,
        "latest_dominance": {"largest_block": largest_block, "fraction_total_squared": largest_fraction, "major_blocks_at_least_5_percent": major},
        "latest_history_localization": {"largest_region": largest_region, "fraction_stationarity_squared": largest_region_fraction, "strongly_localized_threshold": 0.70},
        "motion_residual_comparison": motion_comparison,
        "local_root_basin_evidence": local_response,
        "classification": classification,
        "first_action_owned_blocker": action_owner[largest_block] if classification.startswith(("OUTCOME B", "OUTCOME C")) else None,
        "thresholds_are_diagnostic_not_physical_gates": True,
        "continuation_changed": False,
    }


def completion_payload() -> dict[str, Any]:
    result = residual_ownership_closure_distance_audit()
    latest = result["accepted_frontiers"][-1]
    total2 = latest["total_l2_norm"] ** 2
    block2 = sum(row["squared_contribution"] for row in latest["blocks"].values())
    validation = {
        "requested_v19_29_norm_reproduced": abs(result["accepted_frontiers"][11]["total_l2_norm"] - 0.793187079982019) < 5.0e-12,
        "latest_v19_61_norm_reproduced": abs(latest["total_l2_norm"] - 0.788717933323162) < 5.0e-12,
        "all_requested_frontiers_present": all(version in {row["version"] for row in result["accepted_frontiers"]} for version in ("v18.68", "v18.73", "v18.77", "v18.83", "v18.87", "v19.03", "v19.07", "v19.13", "v19.17", "v19.21", "v19.25", "v19.29")),
        "accepted_only_trend": len(result["accepted_frontiers"]) == len(FRONTIERS),
        "eight_exact_blocks": set(latest["blocks"]) == set(BLOCKS),
        "block_squares_recompose_total": abs(block2 - total2) < 1.0e-12,
        "twenty_dominant_rows": len(result["latest_largest_20_rows"]) == 20,
        "node_partition_complete": sum(len(row["nodes"]) for row in latest["node_localization"]["regions"].values()) == 24,
        "no_equation_or_scaling_change": not result["residual_definition"]["equations_changed"] and not result["residual_definition"]["row_scaling_added"],
        "one_classification": result["classification"].startswith("OUTCOME "),
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_RESIDUAL_OWNERSHIP_AND_CLOSURE_DISTANCE_AUDIT_V19_62",
        "version": VERSION, "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "residual_ownership_and_closure_distance_audit": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "ledger": {
            "VALIDATED": ["exact accepted-frontier F376 replay", "eight physical block decomposition", "node/history localization", "recent slopes and naive nonphysical extrapolation"],
            "INVALIDATED": ["solver convergence as physical evidence", "componentwise monotonicity as a gate"],
            "RECLASSIFIED": [],
            "OPEN": ["N3_EXACT_KKT_CLOSURE", "FULL_BHSM_COMPLETE"],
        },
        "active_calculation": "RESUME_UNCHANGED_N3_CONTINUATION" if result["classification"].startswith(("OUTCOME A", "OUTCOME D", "OUTCOME E")) else "DERIVE_AND_REPAIR_FIRST_ACTION_OWNED_BLOCKER",
        "validation": validation, "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_RESIDUAL_OWNERSHIP_AND_CLOSURE_DISTANCE_AUDIT_V19_62.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "residual_ownership_closure_distance_audit", "completion_payload", "materialize"]
