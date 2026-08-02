"""Physical three-mode gate preserving the frozen q_C/q_W/q_D ontology."""

from __future__ import annotations

from typing import Any


def three_mode_payload() -> dict[str, Any]:
    validation = {
        "three_modes_remain_distinct": True,
        "seam_not_counted_as_fourth_mode": True,
        "hessian_withheld": True,
        "no_stability_claim": True,
    }
    return {
        "artifact": "BHSM_three_mode_physical_action_v11_2",
        "modes": {"q_C": "core/Hopf", "q_W": "enclosure-wall/fold", "q_D": "support depth"},
        "kinetic_matrix": None,
        "hessian": None,
        "mixed_blocks": None,
        "eigenmodes": None,
        "physical_stability": None,
        "reason": "the complete local support-current couplings and reduced Dirac domain are absent",
        "status": "BHSM_PHYSICAL_THREE_MODE_ACTION_NOT_REACHED_BECAUSE_MARK_II_IS_OPEN",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }

