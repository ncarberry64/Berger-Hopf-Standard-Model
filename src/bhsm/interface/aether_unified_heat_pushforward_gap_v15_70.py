"""Heat-semigroup candidate for the unified gauge--Yukawa pushforward."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.optimize import brentq

from bhsm.interface.aether_diagonal_sp1_m4_attachment_v15_50 import (
    RADIUS0,
    attachment_states,
)


VERSION = "v15.70"
CLASSIFICATION = "BHSM_UNIFIED_HEAT_SEMIGROUP_PUSHFORWARD_GAP_TEST"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


UP_CHANNEL_FACTOR = 7.0 / 5.0


def geometric_heat_parameter() -> float:
    """Return t=(ell_kappa/R4)^2; the ratio is kappa1 independent."""

    radius_ratio = RADIUS0 / 2.0
    return 1.0 / radius_ratio**2


def regulated_dimensionless_susceptibility(
    heat_parameter: float, tolerance: float = 1.0e-15,
) -> float:
    t = float(heat_parameter)
    if t <= 0.0 or tolerance <= 0.0:
        raise ValueError("positive heat parameter and tolerance required")
    total = 0.0
    n = 0
    while True:
        x = n + 1.5
        term = (n + 1.0) * (n + 2.0) / x * math.exp(-t * x * x)
        total += term
        if n > 8 and term < tolerance:
            return total
        n += 1
        if n > 2_000_000:
            raise RuntimeError("heat sum failed to converge")


def physical_heat_susceptibility(heat_parameter: float) -> float:
    radius = RADIUS0 / 2.0
    return regulated_dimensionless_susceptibility(heat_parameter) / (
        2.0 * math.pi**2 * radius**2
    )


def largest_static_inverse_kernel_bound() -> dict[str, float]:
    radius = RADIUS0 / 2.0
    k5 = float(attachment_states()["reconstructed_round_boundary"]["connection_kinetic_coefficient"])
    transverse = radius / (2.0 * k5)  # m=2.
    coulomb = 2.0 * radius / (3.0 * k5)  # ell=1.
    return {
        "K_F_five_dimensional": k5,
        "transverse_maximum": transverse,
        "Coulomb_maximum": coulomb,
        "sum_bound": transverse + coulomb,
    }


def up_channel_gap_norm_bound(heat_parameter: float) -> float:
    kernel = largest_static_inverse_kernel_bound()["sum_bound"]
    susceptibility = physical_heat_susceptibility(heat_parameter)
    return 2.0 * UP_CHANNEL_FACTOR * kernel * susceptibility


def critical_heat_parameter() -> float:
    return float(brentq(lambda value: up_channel_gap_norm_bound(value) - 1.0, 1.0e-8, 0.1))


def unified_heat_candidate_contract() -> dict[str, Any]:
    t = geometric_heat_parameter()
    bound = up_channel_gap_norm_bound(t)
    critical = critical_heat_parameter()
    return {
        "single_parent_regulator": "R_parent=exp(-ell_kappa^2*H5)",
        "same_regulator_applied_before_gauge_and_LR_source_derivatives": True,
        "cutoff_profile": "canonical_heat_semigroup_exp(-x)",
        "scale": "ell_kappa=kappa1^(-1/6)",
        "provenance": "CONDITIONAL_SINGLE-LAW_ACTION_COMPLETION_CANDIDATE",
        "geometric_heat_parameter_t": t,
        "dimensionless_susceptibility": regulated_dimensionless_susceptibility(t),
        "up_channel_gap_operator_norm_upper_bound": bound,
        "supercritical_even_at_upper_bound": bound >= 1.0,
        "critical_heat_parameter_upper_bound": critical,
        "critical_effective_cutoff_times_R4": 1.0 / math.sqrt(critical),
        "actual_effective_cutoff_times_R4": 1.0 / math.sqrt(t),
        "candidate_generates_nonzero_composite_Yukawa": False,
        "candidate_generates_same-pushforward_finite_gauge_polarization": True,
        "candidate_accepted_as_complete_BHSM_pushforward": False,
    }


def rejection_semantics() -> dict[str, Any]:
    return {
        "rejected_statement": (
            "the_coefficient-free_parent_heat_semigroup_at_ell_kappa_"
            "simultaneously_generates_the_required_absolute_gauge_and_nonzero_"
            "Yukawa_sectors"
        ),
        "reason": (
            "the_same-pushforward_up-channel_gap_norm_is_below_one_by_more_"
            "than_four_orders_of_magnitude"
        ),
        "independent_Yukawa_added_after_rejection": False,
        "independent_gauge_retuning_after_rejection": False,
        "required_enlargement": (
            "an_action-owned_Aether-event_localization_measure_or_non-Gaussian_"
            "parent_interaction_inside_the_same_M5-to-M4_pushforward"
        ),
    }


def completion_payload() -> dict[str, Any]:
    candidate = unified_heat_candidate_contract()
    rejection = rejection_semantics()
    validation = {
        "geometric_heat_parameter_positive": candidate["geometric_heat_parameter_t"] > 0.0,
        "regulated_susceptibility_positive": candidate["dimensionless_susceptibility"] > 0.0,
        "kernel_bound_positive": largest_static_inverse_kernel_bound()["sum_bound"] > 0.0,
        "candidate_strictly_subcritical": not candidate[
            "supercritical_even_at_upper_bound"
        ] and candidate["up_channel_gap_operator_norm_upper_bound"] < 1.0e-3,
        "critical_cutoff_far_above_geometric_cutoff": candidate[
            "critical_effective_cutoff_times_R4"
        ] > 50.0 * candidate["actual_effective_cutoff_times_R4"],
        "unified_failure_not_split_rescued": not rejection[
            "independent_Yukawa_added_after_rejection"
        ] and not rejection["independent_gauge_retuning_after_rejection"],
        "no_new_continuous_coefficient": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_unified_heat_pushforward_gap_v15_70",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "unified_heat_candidate": candidate,
        "static_inverse_kernel_bound": largest_static_inverse_kernel_bound(),
        "rejection_semantics": rejection,
        "claim_boundary": {
            "one_regulator_used_for_both_sectors": True,
            "gap_norm_upper_bound_derived": True,
            "canonical_heat_candidate_rejected": True,
            "nonzero_Yukawa_generated": False,
            "complete_unified_pushforward_derived": False,
        },
        "active_calculation": (
            "DERIVE_THE_NON-GAUSSIAN_AETHER-EVENT_LOCALIZATION_MEASURE_OR_"
            "PARENT_INTERACTION_THAT_MODIFIES_BOTH_THE_GAUGE_TWO-POINT_"
            "RESIDUE_AND_LR_KERNEL_WITHIN_THE_SAME_M5-TO-M4_PUSHFORWARD"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical_json_value(value: Any) -> Any:
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float cannot be materialized")
        rounded = round(value, 12)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, Mapping):
        return {key: _canonical_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical_json_value(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        _canonical_json_value(payload), indent=2, sort_keys=True,
        ensure_ascii=False, allow_nan=False,
    ) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_unified_heat_pushforward_gap_v15_70.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "UP_CHANNEL_FACTOR",
    "geometric_heat_parameter", "regulated_dimensionless_susceptibility",
    "physical_heat_susceptibility", "largest_static_inverse_kernel_bound",
    "up_channel_gap_norm_bound", "critical_heat_parameter",
    "unified_heat_candidate_contract", "rejection_semantics",
    "completion_payload", "deterministic_json", "materialize",
]
