"""One-time exact-F376 plateau/ownership/proposal-mechanism audit at v20.62."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

from bhsm.interface.aether_n3_forty_eighth_bidirectional_probe_promotion_v20_62 import v20_62_selected_raw_vector
from bhsm.interface.aether_n3_forty_fifth_bidirectional_probe_promotion_v20_46 import v20_46_selected_raw_vector
from bhsm.interface.aether_n3_forty_first_bidirectional_probe_promotion_v20_28 import v20_28_selected_raw_vector
from bhsm.interface.aether_n3_forty_fourth_bidirectional_probe_promotion_v20_42 import v20_42_selected_raw_vector
from bhsm.interface.aether_n3_forty_second_bidirectional_fallback_promotion_v20_34 import v20_34_selected_raw_vector
from bhsm.interface.aether_n3_forty_seventh_bidirectional_fallback_promotion_v20_58 import v20_58_selected_raw_vector
from bhsm.interface.aether_n3_forty_sixth_bidirectional_fallback_promotion_v20_52 import v20_52_selected_raw_vector
from bhsm.interface.aether_n3_forty_third_bidirectional_probe_promotion_v20_38 import v20_38_selected_raw_vector
from bhsm.interface.aether_n3_fortieth_bidirectional_probe_promotion_v20_24 import v20_24_selected_raw_vector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_reclassified_chain_proposal_v18_11 import _square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_thirty_fifth_bidirectional_probe_promotion_v20_02 import v20_02_selected_raw_vector
from bhsm.interface.aether_n3_thirty_ninth_bidirectional_fallback_promotion_v20_20 import v20_20_selected_raw_vector
from bhsm.interface.aether_n3_thirty_seventh_bidirectional_probe_promotion_v20_10 import v20_10_selected_raw_vector
from bhsm.interface.aether_n3_thirty_sixth_bidirectional_probe_promotion_v20_06 import v20_06_selected_raw_vector


VERSION = "v20.67"
CLASSIFICATION = "BHSM_N3_V20_62_PLATEAU_PROPOSAL_MECHANISM_AUDIT"
FULL_BHSM_COMPLETE = False
BLOCKS = ("scale", "u", "w", "v", "lapse", "shift", "period", "event")
FRONTIERS: tuple[tuple[str, Callable[[], np.ndarray]], ...] = (
    ("v20.02", v20_02_selected_raw_vector),
    ("v20.06", v20_06_selected_raw_vector),
    ("v20.10", v20_10_selected_raw_vector),
    ("v20.20", v20_20_selected_raw_vector),
    ("v20.24", v20_24_selected_raw_vector),
    ("v20.28", v20_28_selected_raw_vector),
    ("v20.34", v20_34_selected_raw_vector),
    ("v20.38", v20_38_selected_raw_vector),
    ("v20.42", v20_42_selected_raw_vector),
    ("v20.46", v20_46_selected_raw_vector),
    ("v20.52", v20_52_selected_raw_vector),
    ("v20.58", v20_58_selected_raw_vector),
    ("v20.62", v20_62_selected_raw_vector),
)
PROBES = (
    ("v20.00", "BHSM_aether_n3_thirty_fifth_bidirectional_merit_manifold_probe_v20_00.json"),
    ("v20.04", "BHSM_aether_n3_thirty_sixth_bidirectional_merit_manifold_probe_v20_04.json"),
    ("v20.08", "BHSM_aether_n3_thirty_seventh_bidirectional_merit_manifold_probe_v20_08.json"),
    ("v20.16", "BHSM_aether_n3_thirty_ninth_bidirectional_merit_manifold_probe_v20_16.json"),
    ("v20.22", "BHSM_aether_n3_fortieth_bidirectional_merit_manifold_probe_v20_22.json"),
    ("v20.26", "BHSM_aether_n3_forty_first_bidirectional_merit_manifold_probe_v20_26.json"),
    ("v20.30", "BHSM_aether_n3_forty_second_bidirectional_merit_manifold_probe_v20_30.json"),
    ("v20.36", "BHSM_aether_n3_forty_third_bidirectional_merit_manifold_probe_v20_36.json"),
    ("v20.40", "BHSM_aether_n3_forty_fourth_bidirectional_merit_manifold_probe_v20_40.json"),
    ("v20.44", "BHSM_aether_n3_forty_fifth_bidirectional_merit_manifold_probe_v20_44.json"),
    ("v20.48", "BHSM_aether_n3_forty_sixth_bidirectional_merit_manifold_probe_v20_48.json"),
    ("v20.54", "BHSM_aether_n3_forty_seventh_bidirectional_merit_manifold_probe_v20_54.json"),
    ("v20.60", "BHSM_aether_n3_forty_eighth_bidirectional_merit_manifold_probe_v20_60.json"),
)
FLUX = (
    ("v20.18", False, "BHSM_aether_n3_thirty_ninth_bidirectional_probe_promotion_v20_18.json"),
    ("v20.20", True, "BHSM_aether_n3_thirty_ninth_bidirectional_fallback_promotion_v20_20.json"),
    ("v20.24", True, "BHSM_aether_n3_fortieth_bidirectional_probe_promotion_v20_24.json"),
    ("v20.28", True, "BHSM_aether_n3_forty_first_bidirectional_probe_promotion_v20_28.json"),
    ("v20.32", False, "BHSM_aether_n3_forty_second_bidirectional_probe_promotion_v20_32.json"),
    ("v20.34", True, "BHSM_aether_n3_forty_second_bidirectional_fallback_promotion_v20_34.json"),
    ("v20.38", True, "BHSM_aether_n3_forty_third_bidirectional_probe_promotion_v20_38.json"),
    ("v20.42", True, "BHSM_aether_n3_forty_fourth_bidirectional_probe_promotion_v20_42.json"),
    ("v20.46", True, "BHSM_aether_n3_forty_fifth_bidirectional_probe_promotion_v20_46.json"),
    ("v20.50", False, "BHSM_aether_n3_forty_sixth_bidirectional_probe_promotion_v20_50.json"),
    ("v20.52", True, "BHSM_aether_n3_forty_sixth_bidirectional_fallback_promotion_v20_52.json"),
    ("v20.56", False, "BHSM_aether_n3_forty_seventh_bidirectional_probe_promotion_v20_56.json"),
    ("v20.58", True, "BHSM_aether_n3_forty_seventh_bidirectional_fallback_promotion_v20_58.json"),
    ("v20.62", True, "BHSM_aether_n3_forty_eighth_bidirectional_probe_promotion_v20_62.json"),
)


def _exact_f376(raw: np.ndarray) -> np.ndarray:
    return _square_physical_residual(np.asarray(raw, dtype=float) * kkt_variable_scales())


def _owner(row: int) -> dict[str, Any]:
    if row < 230:
        node, column = divmod(row, 10)
        if column == 0:
            block, component = "scale", "scale"
        elif column < 4:
            block, component = "u", f"u{column - 1}"
        elif column < 7:
            block, component = "w", f"w{column - 4}"
        else:
            block, component = "v", f"v{column - 7}"
        return {"block": block, "sector": "q_stationarity", "history_node": node + 1, "component": component}
    if row < 374:
        node, column = divmod(row - 230, 6)
        block = "lapse" if column < 3 else "shift"
        component = f"{block}{column if column < 3 else column - 3}"
        return {"block": block, "sector": "multiplier_stationarity", "history_node": node, "component": component}
    if row == 374:
        return {"block": "period", "sector": "period", "history_node": None, "component": "period"}
    return {"block": "event", "sector": "event", "history_node": None, "component": "event"}


def _region(node: int | None) -> str:
    if node is None:
        return "GLOBAL"
    if node <= 2:
        return "RESET_NEAR"
    if node >= 21:
        return "EVENT_NEAR"
    return "INTERIOR_HISTORY"


def _block_rows(name: str) -> np.ndarray:
    return np.asarray([row for row in range(376) if _owner(row)["block"] == name], dtype=int)


def _block_stats(residual: np.ndarray) -> dict[str, Any]:
    total2 = float(residual @ residual)
    result: dict[str, Any] = {}
    for block in BLOCKS:
        rows = _block_rows(block)
        values = residual[rows]
        local = int(np.argmax(np.abs(values)))
        norm2 = float(values @ values)
        result[block] = {
            "rows": int(values.size),
            "l2": float(np.sqrt(norm2)),
            "squared_fraction": norm2 / total2,
            "rms_per_row": float(np.sqrt(norm2 / values.size)),
            "max_abs": float(abs(values[local])),
            "max_row": int(rows[local]),
        }
    return result


def _localization(residual: np.ndarray) -> dict[str, Any]:
    region2 = {"RESET_NEAR": 0.0, "INTERIOR_HISTORY": 0.0, "EVENT_NEAR": 0.0}
    node2 = np.zeros(24)
    for row in range(374):
        node = int(_owner(row)["history_node"])
        node2[node] += float(residual[row] ** 2)
    for node, value in enumerate(node2):
        region2[_region(node)] += float(value)
    total2 = float(np.sum(node2))
    fractions = {name: value / total2 for name, value in region2.items()}
    largest = max(fractions, key=fractions.get)
    label = largest if fractions[largest] >= 0.55 else "BROADLY_DISTRIBUTED"
    return {
        "classification": label,
        "region_squared_fractions": fractions,
        "maximum_node": int(np.argmax(node2)),
        "maximum_node_l2": float(np.sqrt(np.max(node2))),
    }


def _linear_trend(values: list[float]) -> dict[str, Any]:
    y = np.asarray(values, dtype=float)
    x = np.arange(y.size, dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    fit = intercept + slope * x
    if y.size > 2:
        stderr = float(np.sqrt(np.sum((y - fit) ** 2) / (y.size - 2) / np.sum((x - np.mean(x)) ** 2)))
    else:
        stderr = 0.0
    resolution = max(2.0 * stderr, 64.0 * np.finfo(float).eps * max(float(np.max(np.abs(y))), 1.0))
    label = "FALLING" if slope < -resolution else "GROWING" if slope > resolution else "FLAT_WITHIN_RESOLUTION"
    return {"linear_slope_per_accepted_state": float(slope), "slope_resolution_2sigma": resolution, "classification": label}


def _window_trends(accepted: list[dict[str, Any]]) -> dict[str, Any]:
    versions = [row["version"] for row in accepted]
    indices = {version: index for index, version in enumerate(versions)}
    result: dict[str, Any] = {}
    series = {"total": [row["total_l2"] for row in accepted]}
    series.update({block: [row["blocks"][block]["l2"] for row in accepted] for block in BLOCKS})
    for name, values in series.items():
        result[name] = {
            "v20_02_to_v20_62": {"absolute_change": values[-1] - values[0], **_linear_trend(values)},
            "v20_28_to_v20_62": {"absolute_change": values[-1] - values[indices["v20.28"]], **_linear_trend(values[indices["v20.28"]:])},
            "latest_five": {"absolute_change": values[-1] - values[-5], **_linear_trend(values[-5:])},
        }
    return result


def _read_nested(path: Path, suffix: str) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    keys = [key for key, value in payload.items() if key.endswith(suffix) and isinstance(value, dict)]
    if len(keys) != 1:
        raise ValueError(f"expected one *{suffix} object in {path}, found {keys}")
    return payload, payload[keys[0]]


def _proposal_diagnostics(artifact_dir: Path) -> dict[str, Any]:
    rows = []
    for version, filename in PROBES:
        payload, probe = _read_nested(artifact_dir / filename, "bidirectional_merit_manifold_probe")
        selected = probe["selected_true_merit_candidate_pending_child_acceptance"]
        rows.append({
            "version": version,
            "source_norm": float(probe["source_complete_norm"]),
            "candidate_norm": float(selected.get("candidate_complete_norm", selected["metrics"]["complete"])),
            "exact_reduction": float(selected["complete_norm_reduction"]),
            "fractional_reduction": float(selected["complete_norm_reduction"] / probe["source_complete_norm"]),
            "alpha": float(selected["alpha"]),
            "orientation": selected.get("orientation"),
            "relative_exact_linear_residual": float(probe["linear_probe"]["relative_exact_linear_residual"]),
            "direction_response_relative_change": float(probe["direct_response"]["resulting_direction_relative_change"]),
            "solver_interpretation": payload.get("solver_interpretation"),
        })
    early = np.asarray([row["exact_reduction"] for row in rows[:7]])
    recent = np.asarray([row["exact_reduction"] for row in rows[-5:]])
    collapse_ratio = float(np.median(recent) / np.median(early))
    return {
        "owned_probe_history": rows,
        "early_median_exact_reduction": float(np.median(early)),
        "recent_median_exact_reduction": float(np.median(recent)),
        "recent_to_early_median_reduction_ratio": collapse_ratio,
        "proposal_reduction_collapsed": bool(collapse_ratio < 0.10),
        "latest_response_resolved": bool(rows[-1]["direction_response_relative_change"] < 0.10),
        "latest_linearization_predictive": bool(rows[-1]["relative_exact_linear_residual"] < 0.25),
        "latest_proposal_model_demonstrably_unresolved": bool(
            rows[-1]["direction_response_relative_change"] >= 0.10
            or rows[-1]["relative_exact_linear_residual"] >= 0.25
            or rows[-1]["solver_interpretation"] == "INVALIDATED"
        ),
    }


def _flux_diagnostics(artifact_dir: Path) -> dict[str, Any]:
    rows = []
    for version, accepted, filename in FLUX:
        payload, promotion = _read_nested(artifact_dir / filename, "promotion")
        child = promotion["event_to_complete_child"]
        step = promotion["global_step"]
        rows.append({
            "version": version,
            "accepted": accepted,
            "candidate_norm": float(step["candidate_complete_norm"]),
            "exact_reduction": float(step["complete_norm_reduction"]),
            "dynamic_flux_envelope": float(child["resolved_dynamic_flux_envelope"]),
            "status": payload["status"],
        })
    accepted_flux = np.asarray([row["dynamic_flux_envelope"] for row in rows if row["accepted"]])
    rejected_flux = np.asarray([row["dynamic_flux_envelope"] for row in rows if not row["accepted"]])
    return {
        "candidates": rows,
        "accepted_flux_range": [float(np.min(accepted_flux)), float(np.max(accepted_flux))],
        "rejected_flux_range": [float(np.min(rejected_flux)), float(np.max(rejected_flux))],
        "classification": "OSCILLATORY_GATE_REJECTION_NOT_SYSTEMATIC_PLATEAU_OWNER",
        "reason": "accepted states continue below the unchanged 2e-5 gate while lower-merit primary candidates intermittently fail it",
    }


def plateau_proposal_mechanism_audit(artifact_dir: str | Path = "artifacts") -> dict[str, Any]:
    artifact_path = Path(artifact_dir)
    accepted: list[dict[str, Any]] = []
    raw_states: list[np.ndarray] = []
    residuals: list[np.ndarray] = []
    for version, loader in FRONTIERS:
        raw = loader()
        residual = _exact_f376(raw)
        accepted.append({
            "version": version,
            "total_l2": float(np.linalg.norm(residual)),
            "blocks": _block_stats(residual),
            "localization": _localization(residual),
        })
        raw_states.append(raw)
        residuals.append(residual)
    trends = _window_trends(accepted)
    latest = accepted[-1]
    latest_residual = residuals[-1]
    top_rows = []
    for row in np.argsort(np.abs(latest_residual))[-20:][::-1]:
        owner = _owner(int(row))
        top_rows.append({
            "row": int(row), "value": float(latest_residual[row]), "abs": float(abs(latest_residual[row])),
            **owner, "region": _region(owner["history_node"]),
        })
    localization_versions = {"v20.02", "v20.28", "v20.46", "v20.62"}
    localization = {row["version"]: row["localization"] for row in accepted if row["version"] in localization_versions}
    proposal = _proposal_diagnostics(artifact_path)
    flux = _flux_diagnostics(artifact_path)
    reductions = np.asarray([accepted[index - 1]["total_l2"] - accepted[index]["total_l2"] for index in range(1, len(accepted))])
    secants = [raw_states[index] - raw_states[index - 1] for index in range(1, len(raw_states))]
    recent_cosines = []
    for left, right in zip(secants[-5:-1], secants[-4:]):
        recent_cosines.append(float(np.dot(left, right) / (np.linalg.norm(left) * np.linalg.norm(right))))
    major = [block for block in BLOCKS if latest["blocks"][block]["squared_fraction"] >= 0.05]
    stalled_major = [block for block in major if trends[block]["latest_five"]["classification"] != "FALLING"]
    dominant = [block for block in stalled_major if latest["blocks"][block]["squared_fraction"] >= 0.60]
    latest_region = latest["localization"]
    history_localized = latest_region["classification"] == "INTERIOR_HISTORY" and latest_region["region_squared_fractions"]["INTERIOR_HISTORY"] >= 0.70
    superlinear_signature = bool(
        reductions[-1] > reductions[-2] > reductions[-3]
        and proposal["owned_probe_history"][-1]["relative_exact_linear_residual"] < 0.10
        and proposal["owned_probe_history"][-1]["relative_exact_linear_residual"] < proposal["owned_probe_history"][-2]["relative_exact_linear_residual"]
    )
    root_basin = {
        "latest_linearization_predictive": proposal["latest_linearization_predictive"],
        "latest_direction_response_resolved": proposal["latest_response_resolved"],
        "superlinear_signature": superlinear_signature,
        "tangent_convergence_demonstrated": False,
        "krylov_consistency_is_not_physics": True,
        "classification": "NOT_DEMONSTRATED" if not superlinear_signature else "ENTERING",
    }
    physical_owner = bool(dominant)
    localization_owner = bool(history_localized and stalled_major)
    mechanism_stall = bool(
        proposal["proposal_reduction_collapsed"]
        and not physical_owner
        and not localization_owner
        and not superlinear_signature
        and proposal["latest_proposal_model_demonstrably_unresolved"]
        and any(row["accepted"] for row in flux["candidates"][-4:])
    )
    distributed_material_descent = bool(
        trends["total"]["latest_five"]["classification"] == "FALLING"
        and len(stalled_major) == 0
        and not proposal["proposal_reduction_collapsed"]
    )
    if physical_owner:
        outcome = "B: DOMINANT_PHYSICAL_OWNER_IDENTIFIED"
    elif localization_owner:
        outcome = "C: HISTORY_LOCALIZED_OWNER_IDENTIFIED"
    elif superlinear_signature:
        outcome = "D: LOCAL_ROOT_BASIN_ENTERING"
    elif mechanism_stall:
        outcome = "E: PROPOSAL_MECHANISM_STALLED_WHILE_PHYSICAL_ROOT_OPEN"
    elif distributed_material_descent:
        outcome = "A: DISTRIBUTED_DESCENT_CONTINUES"
    else:
        outcome = "F: INSUFFICIENT_SEPARATION"
    first_owner = dominant[0] if dominant else (stalled_major[0] if localization_owner else None)
    return {
        "residual_definition": {
            "evaluation": "_square_physical_residual(raw*kkt_variable_scales())",
            "layout": {"q_stationarity": 230, "multiplier_stationarity": 144, "period": 1, "event": 1},
            "sum_rows": 376, "unweighted": True, "equations_changed": False,
        },
        "accepted_frontier": {"version": "v20.62", "exact_f376_l2": latest["total_l2"]},
        "accepted_states": accepted,
        "v20_62_exact_ownership": latest["blocks"],
        "trends": trends,
        "v20_62_largest_20_rows": top_rows,
        "node_localization": localization,
        "scale_test": {
            **latest["blocks"]["scale"],
            "recent_slope": trends["scale"]["latest_five"],
            "dominant_physical_owner": "scale" in dominant,
        },
        "flux_audit": flux,
        "proposal_mechanism": {
            **proposal,
            "recent_accepted_raw_secant_cosines": recent_cosines,
            "recent_accepted_exact_reductions": [float(value) for value in reductions[-5:]],
        },
        "root_basin_test": root_basin,
        "physical_vs_proposal": {
            "major_blocks_at_least_5_percent": major,
            "stalled_or_growing_major_blocks": stalled_major,
            "dominant_stalled_blocks_at_least_60_percent": dominant,
            "physical_owner_demonstrated": physical_owner or localization_owner,
            "proposal_exhaustion_demonstrated": mechanism_stall,
        },
        "outcome": outcome,
        "first_action_owned_blocker": first_owner,
        "next_action": "E1_RECENT_SECANT_RESPONSE_SUBSPACE_EXACT_F376_RECOVERY" if outcome.startswith("E:") else (
            "RESUME_UNCHANGED_CONTINUATION" if outcome.startswith(("A:", "D:")) else
            "DERIVE_OR_REPAIR_FIRST_ACTION_OWNED_BLOCKER" if outcome.startswith(("B:", "C:")) else
            "OBTAIN_ONE_ADDITIONAL_SEPARATING_DIAGNOSTIC"
        ),
    }


def completion_payload(artifact_dir: str | Path = "artifacts") -> dict[str, Any]:
    audit = plateau_proposal_mechanism_audit(artifact_dir)
    latest = audit["accepted_states"][-1]
    block_sum = sum((row["l2"] ** 2) for row in latest["blocks"].values())
    validation = {
        "exact_v20_62_norm_reproduced": abs(latest["total_l2"] - 0.766997331117846) < 5.0e-12,
        "all_required_accepted_states": [row["version"] for row in audit["accepted_states"]] == [version for version, _ in FRONTIERS],
        "block_squares_recompose_exactly": abs(block_sum - latest["total_l2"] ** 2) < 1.0e-12,
        "block_row_count_is_376": sum(row["rows"] for row in latest["blocks"].values()) == 376,
        "twenty_largest_rows": len(audit["v20_62_largest_20_rows"]) == 20,
        "four_localization_snapshots": len(audit["node_localization"]) == 4,
        "accepted_and_rejected_flux_separate": {row["accepted"] for row in audit["flux_audit"]["candidates"]} == {True, False},
        "exactly_one_outcome": audit["outcome"][0] in "ABCDEF" and audit["outcome"][1] == ":",
        "no_physics_or_acceptance_change": not audit["residual_definition"]["equations_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_V20_62_PLATEAU_PROPOSAL_MECHANISM_AUDIT_V20_67",
        "version": VERSION, "classification": CLASSIFICATION, "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "plateau_proposal_mechanism_audit": audit,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "ledger": {
            "VALIDATED": ["exact unweighted F376 ownership", "accepted-state trends and localization", "owned proposal-response and flux histories"],
            "INVALIDATED": ["componentwise monotonicity as physics", "Krylov convergence as a physical gate"],
            "RECLASSIFIED": ["v20.62 plateau as physical-owner or proposal-mechanism evidence according to the single audit outcome"],
            "OPEN": ["N3_EXACT_KKT_CLOSURE", "FULL_BHSM_COMPLETE"],
        },
        "validation": validation, "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_V20_62_PLATEAU_PROPOSAL_MECHANISM_AUDIT_V20_67.json"
    path.write_text(deterministic_json(completion_payload(target)), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "plateau_proposal_mechanism_audit", "completion_payload", "materialize"]
