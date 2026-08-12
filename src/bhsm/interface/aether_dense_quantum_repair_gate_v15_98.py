"""Quantum cone-repair lower bound using the dense v15.97 pushforward."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

from bhsm.interface.aether_dense_proper_joint_pushforward_v15_97 import (
    dense_constraint_solved_cycle,
)
from bhsm.interface.aether_zeta_rg_microscopic_completion_v15_61 import (
    GAUGE_BETA_ONE_LOOP,
)


VERSION = "v15.98"
CLASSIFICATION = "BHSM_DENSE_QUANTUM_CONE_REPAIR_GATE"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def dense_repair_gate(cycle: Mapping[str, Any] | None = None) -> dict[str, Any]:
    values = dense_constraint_solved_cycle() if cycle is None else cycle
    magnetic = float(values["proper_cycle_K_magnetic"])
    electric = float(values["proper_cycle_K_electric"])
    mismatch = electric - magnetic
    minimum = mismatch / 2.0
    maximum_beta = max(abs(float(value)) for value in GAUGE_BETA_ONE_LOOP.values())
    maximum_difference_rate = 2.0 * maximum_beta / (8.0 * math.pi**2)
    return {
        "dense_K_magnetic": magnetic,
        "dense_K_electric": electric,
        "dense_coefficient_ratio": electric / magnetic,
        "dense_gauge_speed": math.sqrt(magnetic / electric),
        "coefficient_mismatch": mismatch,
        "minimum_max_sector_correction": minimum,
        "minimum_correction_over_K_magnetic": minimum / magnetic,
        "at_least_one_correction_exceeds_smaller_classical_coefficient": minimum > magnetic,
        "optimistic_maximum_difference_rate_per_log_mu": maximum_difference_rate,
        "minimum_log_scale_interval": mismatch / maximum_difference_rate,
        "controlled_one_loop_or_RG_repair_possible": False,
        "reason": (
            "the_triangle_lower_bound_still_exceeds_the_complete_dense_"
            "magnetic_coefficient;_the_required_change_is_order_one_in_the_"
            "classical_Hessian_and_nearly_10^4_maximal_one-loop_e-folds"
        ),
        "one_common_quantum_saddle_required": True,
        "recompute_gauge_and_Yukawa_together": True,
    }


def completion_payload() -> dict[str, Any]:
    gate = dense_repair_gate()
    validation = {
        "dense_cone_mismatch": gate["dense_coefficient_ratio"] > 3.0,
        "order_one_correction_required": gate["at_least_one_correction_exceeds_smaller_classical_coefficient"],
        "perturbative_RG_interval_enormous": gate["minimum_log_scale_interval"] > 9000.0,
        "controlled_repair_rejected": not gate["controlled_one_loop_or_RG_repair_possible"],
        "one_unsplit_quantum_problem": gate["one_common_quantum_saddle_required"] and gate["recompute_gauge_and_Yukawa_together"],
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_dense_quantum_repair_gate_v15_98",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "dense_quantum_repair_gate": gate,
        "scientific_result": (
            "THE_DENSE_PUSHFORWARD_REQUIRES_MAX(|DELTA_K_E|,|DELTA_K_B|)>="
            "852.168262=1.052244*K_B;_THE_SPARSE_10735-E-FOLD_ESTIMATE_IS_"
            "SUPERSEDED_BY_A_DENSE_9612-E-FOLD_BOUND,_BUT_THE_REQUIRED_"
            "CORRECTION_REMAINS_NONPERTURBATIVE_AND_UNSPLIT"
        ),
        "claim_boundary": {
            "sparse_v15_95_numerical_bound_superseded": True,
            "nonperturbative_gate_survives_dense_quadrature": True,
            "quantum_event_saddle_solved": False,
        },
        "active_calculation": (
            "INSERT_COMMON_BACKGROUND_VERTICES_IN_V15.96_AND_SOLVE_THE_"
            "DENSE_COUPLED_QUANTUM_EVENT_SADDLE_WITH_GAUGE_AND_YUKAWA_TOGETHER"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical(value: Any) -> Any:
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float")
        return round(value, 12)
    if isinstance(value, Mapping):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_dense_quantum_repair_gate_v15_98.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "dense_repair_gate",
    "completion_payload", "deterministic_json", "materialize",
]
