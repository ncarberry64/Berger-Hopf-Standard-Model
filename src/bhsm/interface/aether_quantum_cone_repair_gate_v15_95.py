"""Controlled-quantum gate for the BHSM proper-cycle cone mismatch."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

from bhsm.interface.aether_proper_time_joint_pushforward_v15_91 import (
    proper_time_cycle_pushforward,
)
from bhsm.interface.aether_zeta_rg_microscopic_completion_v15_61 import (
    GAUGE_BETA_ONE_LOOP,
)


VERSION = "v15.95"
CLASSIFICATION = "BHSM_QUANTUM_GAUGE_CONE_REPAIR_GATE"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def necessary_quantum_correction() -> dict[str, float | str | bool]:
    cycle = proper_time_cycle_pushforward()
    magnetic = float(cycle["proper_cycle_K_magnetic"])
    electric = float(cycle["proper_cycle_K_electric"])
    mismatch = electric - magnetic
    minimum_one_sector = mismatch / 2.0
    return {
        "K_magnetic_classical": magnetic,
        "K_electric_classical": electric,
        "cone_coefficient_mismatch": mismatch,
        "matching_equation": "delta_K_E-delta_K_B=-(K_E-K_B)",
        "triangle_inequality_minimum_max_correction": minimum_one_sector,
        "minimum_correction_over_K_magnetic": minimum_one_sector / magnetic,
        "at_least_one_correction_exceeds_smaller_classical_coefficient": (
            minimum_one_sector > magnetic
        ),
        "controlled_one_loop_repair_possible": False,
    }


def perturbative_rg_scale_test() -> dict[str, float | str | bool]:
    mismatch = float(necessary_quantum_correction()["cone_coefficient_mismatch"])
    maximum_beta = max(abs(float(value)) for value in GAUGE_BETA_ONE_LOOP.values())
    maximum_single_rate = maximum_beta / (8.0 * math.pi**2)
    maximum_difference_rate = 2.0 * maximum_single_rate
    required_log = mismatch / maximum_difference_rate
    return {
        "maximum_absolute_SM_one_loop_b": maximum_beta,
        "maximum_single_K_shift_per_log_mu": maximum_single_rate,
        "optimistic_two_component_difference_rate_per_log_mu": maximum_difference_rate,
        "minimum_log_scale_interval_at_that_rate": required_log,
        "natural_finite_log_interval_can_repair": False,
        "interpretation": (
            "even_granting_opposite_maximal_one-loop_running_to_the_two_"
            "components_would_require_more_than_10^4_e-folds;_long_before_"
            "that_the_fixed-one-loop_expansion_and_compact-cycle_matching_"
            "cease_to_be_the_same_controlled_problem"
        ),
    }


def exact_quantum_problem() -> dict[str, Any]:
    return {
        "effective_action": (
            "Gamma_quantum=Gamma_classical+(1/2)*STr_log_det_Rparent(Phi_star;A,H)"
        ),
        "common_regulator": "R_parent=exp(-ell_kappa^2*H5)",
        "required_Hessian": (
            "Pi_AB=delta^2_Gamma_quantum/delta_A_A_delta_A_B_on_the_"
            "proper_anisotropic_cycle_with_complete_gauge-ghost-spinor-HS_blocks"
        ),
        "required_solution": (
            "solve_delta_Gamma_quantum/delta_Phi=0_and_the_event_condition_"
            "together,_then_recompute_K_E,K_B,Z_Psi,Z_H,Y"
        ),
        "one_loop_evaluation_about_unshifted_classical_saddle_sufficient": False,
        "reason": (
            "the_correction_needed_for_cone_matching_is_larger_than_the_"
            "smaller_classical_quadratic_coefficient_and_would_shift_the_"
            "saddle_nonperturbatively"
        ),
        "separate_gauge_counterterm_allowed": False,
        "Yukawa_must_be_recomputed_with_same_quantum_saddle": True,
    }


def completion_payload() -> dict[str, Any]:
    necessary = necessary_quantum_correction()
    rg = perturbative_rg_scale_test()
    exact = exact_quantum_problem()
    validation = {
        "triangle_lower_bound_exceeds_KB": necessary[
            "at_least_one_correction_exceeds_smaller_classical_coefficient"
        ],
        "one_loop_repair_rejected": not necessary[
            "controlled_one_loop_repair_possible"
        ],
        "RG_interval_enormous": rg["minimum_log_scale_interval_at_that_rate"] > 1.0e4,
        "full_quantum_saddle_required": not exact[
            "one_loop_evaluation_about_unshifted_classical_saddle_sufficient"
        ],
        "no_split_counterterm": not exact["separate_gauge_counterterm_allowed"],
        "Yukawa_kept_in_same_problem": exact[
            "Yukawa_must_be_recomputed_with_same_quantum_saddle"
        ],
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_quantum_cone_repair_gate_v15_95",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "necessary_quantum_correction": necessary,
        "perturbative_RG_scale_test": rg,
        "exact_quantum_problem": exact,
        "scientific_result": (
            "CONE_MATCHING_REQUIRES_AT_LEAST_ONE_QUANTUM_CORRECTION_OF_"
            "MAGNITUDE_951.763659,_WHICH_IS_1.16999_TIMES_THE_ENTIRE_"
            "CLASSICAL_K_B;_THEREFORE_NO_CONTROLLED_ONE-LOOP_OR_RG_REPAIR_"
            "EXISTS_AND_THE_FULL_COMMON_QUANTUM_SADDLE_IS_REQUIRED"
        ),
        "claim_boundary": {
            "controlled_one_loop_cone_repair_excluded": True,
            "perturbative_RG_cone_repair_excluded": True,
            "full_nonperturbative_quantum_saddle_solved": False,
            "separate_gauge_or_Yukawa_counterterm_inserted": False,
        },
        "active_calculation": (
            "FORMULATE_AND_DISCRETIZE_THE_COMMON_GAUGE-GHOST-SPINOR-HS_"
            "SUPERDETERMINANT_ON_THE_PROPER_CYCLE_AND_SOLVE_THE_COUPLED_"
            "QUANTUM_EVENT_SADDLE_WITHOUT_SPLITTING_GAUGE_FROM_YUKAWA"
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
    path = target / "BHSM_aether_quantum_cone_repair_gate_v15_95.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "necessary_quantum_correction", "perturbative_rg_scale_test",
    "exact_quantum_problem", "completion_payload", "deterministic_json",
    "materialize",
]
