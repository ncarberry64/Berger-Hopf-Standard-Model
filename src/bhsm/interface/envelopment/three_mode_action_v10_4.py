"""Common three-mode action gate after the author-selected v10.4 extension."""

from __future__ import annotations

from typing import Any


ACTION_VERDICT = "BHSM_THREE_MODE_COMMON_ACTION_BLOCKED_BY_NONUNIQUE_SUPPORT_COUPLINGS"


def _block(status: str, value: Any, reason: str) -> dict[str, Any]:
    return {"status": status, "value": value, "reason": reason}


def three_mode_action_payload() -> dict[str, Any]:
    cross = "q_C and q_W retain distinct M8/M5 action domains"
    depth = "upsilon is selected, but Z, U, F_C, and F_W are not action-selected"
    k = [
        [_block("DERIVED_CONDITIONAL", "6*kappa5", "M8 Einstein-frame q_C"), _block("UNDEFINED_CROSS_DOMAIN", None, cross), _block("OPEN", None, depth)],
        [_block("UNDEFINED_CROSS_DOMAIN", None, cross), _block("DERIVED_CONDITIONAL", 6.935084858283065, "M5 fold q_W"), _block("OPEN", None, depth)],
        [_block("OPEN", None, depth), _block("OPEN", None, depth), _block("DERIVED_CONDITIONAL", "1 after canonical normalization", "requires selected Z_reduced>0")],
    ]
    h = [
        [_block("DERIVED_CONDITIONAL", "H_C on nonstationary M8 domain", "no selected localized equilibrium"), _block("UNDEFINED_CROSS_DOMAIN", None, cross), _block("OPEN", None, depth)],
        [_block("UNDEFINED_CROSS_DOMAIN", None, cross), _block("DERIVED_CONDITIONAL", "H_W on D_fold", "v6.28-v6.30 fold domain"), _block("OPEN", None, depth)],
        [_block("OPEN", None, depth), _block("OPEN", None, depth), _block("DERIVED_CONDITIONAL", "U_eff''(1)", "nonnegative but not selected")],
    ]
    return {
        "artifact": "BHSM_three_mode_action_v10_4",
        "state": ["q_C", "q_W", "q_D"],
        "mode_status": {"q_C": "DERIVED_CONDITIONAL", "q_W": "DERIVED_CONDITIONAL", "q_D": "DERIVED_CONDITIONAL_ON_POSITIVE_Z_UPSILON"},
        "K_0": k,
        "H_0": h,
        "J_0": ["incomplete M8 localized source", "conditional fold source", None],
        "complete_common_source": None,
        "nonlinear_potential": None,
        "common_boundary_conditions": None,
        "seam_projection": "psi_seam=Pi_seam(q_C,q_W,q_D); only the historical q_W coefficient is known",
        "physical_rank": "2+1 conditional",
        "target_rank_three_reached": False,
        "verdict": ACTION_VERDICT,
        "validation_passed": all(cell["status"] != "DERIVED" for matrix in (k, h) for row in matrix for cell in row if cell["value"] is None),
    }
