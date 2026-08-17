"""Compact exact-F376 ownership reassessment after the recovered proposal contracts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

from bhsm.interface.aether_n3_controlled_structured_shake_recovery_v20_69 import v20_69_selected_raw_vector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_plateau_proposal_mechanism_audit_v20_67 import BLOCKS, _block_stats, _localization, _owner, _region
from bhsm.interface.aether_n3_reclassified_chain_proposal_v18_11 import _square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_70 import v20_70_selected_raw_vector
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_71 import v20_71_selected_raw_vector
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_72 import v20_72_selected_raw_vector
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_73 import v20_73_selected_raw_vector
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_74 import v20_74_selected_raw_vector
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_75 import v20_75_selected_raw_vector


VERSION = "v20.76"
CLASSIFICATION = "BHSM_N3_POST_RECOVERY_EXACT_RESIDUAL_OWNERSHIP_AUDIT"
FULL_BHSM_COMPLETE = False
STATES: tuple[tuple[str, Callable[[], np.ndarray]], ...] = (
    ("v20.69", v20_69_selected_raw_vector),
    ("v20.70", v20_70_selected_raw_vector),
    ("v20.71", v20_71_selected_raw_vector),
    ("v20.72", v20_72_selected_raw_vector),
    ("v20.73", v20_73_selected_raw_vector),
    ("v20.74", v20_74_selected_raw_vector),
    ("v20.75", v20_75_selected_raw_vector),
)


def _exact(raw: np.ndarray) -> np.ndarray:
    return _square_physical_residual(np.asarray(raw) * kkt_variable_scales())


def _trend(values: list[float]) -> dict[str, Any]:
    y = np.asarray(values, dtype=float)
    x = np.arange(y.size, dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    fitted = intercept + slope * x
    stderr = float(np.sqrt(np.sum((y - fitted) ** 2) / max(y.size - 2, 1) / np.sum((x - np.mean(x)) ** 2)))
    resolution = max(2.0 * stderr, 64.0 * np.finfo(float).eps * max(float(np.max(np.abs(y))), 1.0))
    label = "FALLING" if slope < -resolution else "GROWING" if slope > resolution else "FLAT_WITHIN_RESOLUTION"
    return {"slope_per_accepted_state": float(slope), "two_sigma_resolution": resolution, "classification": label, "absolute_change": float(y[-1] - y[0])}


def post_recovery_ownership_audit() -> dict[str, Any]:
    accepted = []
    residuals = []
    for version, loader in STATES:
        residual = _exact(loader())
        residuals.append(residual)
        accepted.append({
            "version": version,
            "exact_f376_l2": float(np.linalg.norm(residual)),
            "blocks": _block_stats(residual),
            "localization": _localization(residual),
        })
    latest = accepted[-1]
    recent = accepted[-3:]
    trends = {
        "total": {
            "full_recovery_sprint": _trend([row["exact_f376_l2"] for row in accepted]),
            "latest_three": _trend([row["exact_f376_l2"] for row in recent]),
        }
    }
    for block in BLOCKS:
        trends[block] = {
            "full_recovery_sprint": _trend([row["blocks"][block]["l2"] for row in accepted]),
            "latest_three": _trend([row["blocks"][block]["l2"] for row in recent]),
        }
    residual = residuals[-1]
    top_rows = []
    for row in np.argsort(np.abs(residual))[-20:][::-1]:
        owner = _owner(int(row))
        top_rows.append({
            "row": int(row), "value": float(residual[row]), "abs": float(abs(residual[row])),
            **owner, "region": _region(owner["history_node"]),
        })
    major = [block for block in BLOCKS if latest["blocks"][block]["squared_fraction"] >= 0.05]
    stalled_major = [block for block in major if trends[block]["latest_three"]["classification"] != "FALLING"]
    dominant = [block for block in stalled_major if latest["blocks"][block]["squared_fraction"] >= 0.60]
    localization = latest["localization"]
    history_owner = bool(
        localization["classification"] == "INTERIOR_HISTORY"
        and localization["region_squared_fractions"]["INTERIOR_HISTORY"] >= 0.70
    )
    reductions = [accepted[index - 1]["exact_f376_l2"] - accepted[index]["exact_f376_l2"] for index in range(1, len(accepted))]
    confirmed_contraction = bool(reductions[-1] < 1.0e-2 * np.median(reductions[:4]) and reductions[-2] < 0.1 * np.median(reductions[:4]))
    if dominant:
        outcome = "DOMINANT_PHYSICAL_OWNER_IDENTIFIED"
        next_action = "DERIVE_OR_REPAIR_DOMINANT_ACTION_OWNER"
    elif history_owner:
        outcome = "HISTORY_LOCALIZED_OWNER_IDENTIFIED"
        next_action = "DERIVE_OR_REPAIR_HISTORY_LOCALIZED_OWNER"
    elif confirmed_contraction:
        outcome = "RENEWED_PROPOSAL_EXHAUSTION_NO_PHYSICAL_OWNER"
        next_action = "BUILD_NEXT_ACTION_OWNED_PROPOSAL_FROM_V20_75_OWNERSHIP_AND_RECOVERED_SECANT_MEMORY"
    else:
        outcome = "INSUFFICIENT_SEPARATION"
        next_action = "OBTAIN_ONE_ADDITIONAL_SEPARATING_DIAGNOSTIC"
    return {
        "frontier": {"version": "v20.75", "exact_f376_l2": latest["exact_f376_l2"]},
        "accepted_recovery_sprint": accepted,
        "latest_exact_ownership": latest["blocks"],
        "trends": trends,
        "largest_20_rows": top_rows,
        "latest_localization": localization,
        "major_blocks_at_least_5_percent": major,
        "stalled_or_growing_major_blocks": stalled_major,
        "dominant_stalled_blocks_at_least_60_percent": dominant,
        "accepted_exact_reductions": reductions,
        "two_step_contraction_confirmed": confirmed_contraction,
        "outcome": outcome,
        "next_action": next_action,
        "equations_changed": False,
        "row_scaling_added": False,
        "acceptance_gate_changed": False,
    }


def completion_payload() -> dict[str, Any]:
    result = post_recovery_ownership_audit()
    latest = result["accepted_recovery_sprint"][-1]
    block2 = sum(row["l2"] ** 2 for row in latest["blocks"].values())
    validation = {
        "v20_75_norm_reproduced": abs(result["frontier"]["exact_f376_l2"] - 0.758674247739506) < 5.0e-12,
        "seven_accepted_states": len(result["accepted_recovery_sprint"]) == 7,
        "block_squares_recompose": abs(block2 - result["frontier"]["exact_f376_l2"] ** 2) < 1.0e-12,
        "block_rows_recompose_376": sum(row["rows"] for row in latest["blocks"].values()) == 376,
        "twenty_largest_rows": len(result["largest_20_rows"]) == 20,
        "one_outcome": result["outcome"] in {
            "DOMINANT_PHYSICAL_OWNER_IDENTIFIED", "HISTORY_LOCALIZED_OWNER_IDENTIFIED",
            "RENEWED_PROPOSAL_EXHAUSTION_NO_PHYSICAL_OWNER", "INSUFFICIENT_SEPARATION",
        },
        "same_physics": not result["equations_changed"] and not result["row_scaling_added"] and not result["acceptance_gate_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_POST_RECOVERY_OWNERSHIP_AUDIT_V20_76",
        "version": VERSION, "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "post_recovery_ownership_audit": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation, "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_POST_RECOVERY_OWNERSHIP_AUDIT_V20_76.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "post_recovery_ownership_audit", "completion_payload", "materialize"]
