"""One-time exact Rayleigh-F376 ownership audit at the v20.95 frontier."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import numpy as np

from bhsm.interface.aether_n3_dual_metric_range_space_continuation_v20_92 import v20_92_selected_raw_vector
from bhsm.interface.aether_n3_dual_metric_range_space_proposal_v20_91 import v20_91_selected_raw_vector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_plateau_proposal_mechanism_audit_v20_67 import (
    BLOCKS, _block_stats, _localization, _owner, _region,
)
from bhsm.interface.aether_n3_rayleigh_curvature_preconditioned_proposal_v20_88 import v20_88_selected_raw_vector
from bhsm.interface.aether_n3_rayleigh_event_covector_v20_80 import rayleigh_square_physical_residual
from bhsm.interface.aether_n3_rayleigh_krylov_restriction_audit_v20_86 import v20_86_selected_raw_vector
from bhsm.interface.aether_n3_rayleigh_multiplier_continuation_v20_82 import v20_82_selected_raw_vector
from bhsm.interface.aether_n3_rayleigh_multiplier_continuation_v20_84 import v20_84_selected_raw_vector
from bhsm.interface.aether_n3_rayleigh_square_kkt_continuation_v20_83 import v20_83_selected_raw_vector
from bhsm.interface.aether_n3_rayleigh_square_kkt_continuation_v20_85 import v20_85_selected_raw_vector
from bhsm.interface.aether_n3_rayleigh_square_kkt_proposal_v20_81 import v20_81_selected_raw_vector
from bhsm.interface.aether_n3_refreshed_dual_metric_continuation_v20_95 import v20_95_selected_raw_vector
from bhsm.interface.aether_n3_refreshed_dual_metric_proposal_v20_94 import v20_94_selected_raw_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales


VERSION = "v20.96"
CLASSIFICATION = "BHSM_N3_EXACT_RAYLEIGH_F376_OWNERSHIP_CLOSURE_DISTANCE_AUDIT"
FULL_BHSM_COMPLETE = False
STATES: tuple[tuple[str, Callable[[], np.ndarray]], ...] = (
    ("v20.81", v20_81_selected_raw_vector),
    ("v20.82", v20_82_selected_raw_vector),
    ("v20.83", v20_83_selected_raw_vector),
    ("v20.84", v20_84_selected_raw_vector),
    ("v20.85", v20_85_selected_raw_vector),
    ("v20.86", v20_86_selected_raw_vector),
    ("v20.88", v20_88_selected_raw_vector),
    ("v20.91", v20_91_selected_raw_vector),
    ("v20.92", v20_92_selected_raw_vector),
    ("v20.94", v20_94_selected_raw_vector),
    ("v20.95", v20_95_selected_raw_vector),
)


def _trend(values: list[float]) -> dict[str, Any]:
    y = np.asarray(values, dtype=float)
    x = np.arange(y.size, dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    fitted = intercept + slope * x
    stderr = float(np.sqrt(
        np.sum((y - fitted) ** 2)
        / max(y.size - 2, 1)
        / np.sum((x - np.mean(x)) ** 2)
    ))
    resolution = max(
        2.0 * stderr,
        64.0 * np.finfo(float).eps * max(float(np.max(np.abs(y))), 1.0),
    )
    label = "FALLING" if slope < -resolution else (
        "GROWING" if slope > resolution else "FLAT_WITHIN_RESOLUTION"
    )
    return {
        "slope_per_accepted_state": float(slope),
        "two_sigma_resolution": resolution,
        "classification": label,
        "absolute_change": float(y[-1] - y[0]),
    }


def rayleigh_ownership_audit() -> dict[str, Any]:
    scales = kkt_variable_scales()
    accepted = []
    residuals = []
    for version, loader in STATES:
        residual = rayleigh_square_physical_residual(loader() * scales)
        residuals.append(residual)
        accepted.append({
            "version": version,
            "exact_rayleigh_f376_l2": float(np.linalg.norm(residual)),
            "blocks": _block_stats(residual),
            "localization": _localization(residual),
        })
    latest = accepted[-1]
    recent = accepted[-5:]
    trends = {
        "total": _trend([row["exact_rayleigh_f376_l2"] for row in recent]),
        **{
            block: _trend([row["blocks"][block]["l2"] for row in recent])
            for block in BLOCKS
        },
    }
    residual = residuals[-1]
    top_rows = []
    for row in np.argsort(np.abs(residual))[-20:][::-1]:
        owner = _owner(int(row))
        top_rows.append({
            "row": int(row),
            "value": float(residual[row]),
            "abs": float(abs(residual[row])),
            **owner,
            "region": _region(owner["history_node"]),
        })
    major = [
        block for block in BLOCKS
        if latest["blocks"][block]["squared_fraction"] >= 0.05
    ]
    stalled_major = [
        block for block in major if trends[block]["classification"] != "FALLING"
    ]
    dominant = [
        block for block in stalled_major
        if latest["blocks"][block]["squared_fraction"] >= 0.60
    ]
    localization = latest["localization"]
    history_localized = bool(
        localization["classification"] == "INTERIOR_HISTORY"
        and localization["region_squared_fractions"]["INTERIOR_HISTORY"] >= 0.70
        and stalled_major
    )
    reductions = [
        accepted[index - 1]["exact_rayleigh_f376_l2"]
        - accepted[index]["exact_rayleigh_f376_l2"]
        for index in range(1, len(accepted))
    ]
    local_root = bool(
        reductions[-1] > reductions[-2] > reductions[-3]
        and all(value > 0.0 for value in reductions[-3:])
    )
    distributed = bool(
        trends["total"]["classification"] == "FALLING"
        and not stalled_major
    )
    if dominant:
        outcome = "B: DOMINANT_PHYSICAL_OWNER_IDENTIFIED"
        next_action = "DERIVE_OR_REPAIR_FIRST_ACTION_OWNED_BLOCKER"
    elif history_localized:
        outcome = "C: HISTORY_LOCALIZED_OWNER_IDENTIFIED"
        next_action = "DERIVE_OR_REPAIR_FIRST_ACTION_OWNED_BLOCKER"
    elif local_root:
        outcome = "D: LOCAL_ROOT_BASIN_ENTERING"
        next_action = "RESUME_ESTABLISHED_CONTINUATION"
    elif distributed:
        outcome = "A: DISTRIBUTED_DESCENT_CONTINUES"
        next_action = "RESUME_ESTABLISHED_CONTINUATION"
    else:
        outcome = "E: PROPOSAL_MECHANISM_STALLED_WHILE_PHYSICAL_ROOT_OPEN"
        next_action = "REFRESH_ACTION_OWNED_PROPOSAL_MODEL_AT_V20_95"
    first_owner = dominant[0] if dominant else (stalled_major[0] if history_localized else None)
    return {
        "frontier": {"version": "v20.95", "exact_rayleigh_f376_l2": latest["exact_rayleigh_f376_l2"]},
        "exact_physical_block_norms": latest["blocks"],
        "dominant_rows": top_rows,
        "history_node_localization": localization,
        "recent_five_block_slopes": trends,
        "recent_exact_reductions": reductions[-5:],
        "major_blocks_at_least_5_percent": major,
        "stalled_or_growing_major_blocks": stalled_major,
        "dominant_stalled_blocks_at_least_60_percent": dominant,
        "classification": outcome,
        "first_action_owned_blocker": first_owner,
        "next_action": next_action,
        "equations_changed": False,
        "row_scaling_added": False,
        "acceptance_gate_changed": False,
    }


def completion_payload() -> dict[str, Any]:
    audit = rayleigh_ownership_audit()
    block2 = sum(row["l2"] ** 2 for row in audit["exact_physical_block_norms"].values())
    validation = {
        "v20_95_norm_reproduced": abs(
            audit["frontier"]["exact_rayleigh_f376_l2"] - 0.783495243812703
        ) < 5.0e-12,
        "block_squares_recompose": abs(
            block2 - audit["frontier"]["exact_rayleigh_f376_l2"] ** 2
        ) < 1.0e-12,
        "block_rows_recompose_376": sum(
            row["rows"] for row in audit["exact_physical_block_norms"].values()
        ) == 376,
        "twenty_largest_rows": len(audit["dominant_rows"]) == 20,
        "one_A_to_E_classification": audit["classification"][:2] in {
            "A:", "B:", "C:", "D:", "E:",
        },
        "same_physics": not audit["equations_changed"]
        and not audit["row_scaling_added"]
        and not audit["acceptance_gate_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_RAYLEIGH_OWNERSHIP_AUDIT_V20_96",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "rayleigh_ownership_audit": audit,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_RAYLEIGH_OWNERSHIP_AUDIT_V20_96.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "rayleigh_ownership_audit", "completion_payload", "materialize",
]
