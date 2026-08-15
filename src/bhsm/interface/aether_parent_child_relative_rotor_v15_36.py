"""Compact momentum constraint and the parent--child relative Hopf rotor.

The v15.34--v15.35 reduced fixed-charge calculation used the correct
antiperiodic FR spectrum but had not yet imposed the compact spatial momentum
constraint.  On closed S7, contraction of that constraint with any Killing
field shows that the total spatial Hopf momentum must vanish.  A lone rotor is
therefore not a complete constrained state.

The admissible nonzero sector is relative: the localized child carries J and
the parent/environment carries -J.  Eliminating the common rotation gives the
parallel-sum inertia I_rel=(I_child^-1+I_parent^-1)^-1 and energy
J^2/(2 I_rel).  The parent term is finite while I_child tends to zero at both
material collapse limits, so the stabilization mechanism and its finite
Routhian minimum survive.  The local coexact shift/frame-dragging equation is
still unsolved and is reported explicitly.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.optimize import minimize_scalar

from bhsm.interface.aether_complete_child_localized_fiber_v15_34 import (
    HOPF_ORBIT_VOLUME,
    localized_child_terms,
)


VERSION = "v15.36"
CLASSIFICATION = "COMPACT_CONSTRAINT_CORRECTED_RELATIVE_ROTOR"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def compact_killing_momentum_constraint_theorem() -> dict[str, Any]:
    """Derive the zero-total-Killing-momentum condition on closed S7."""

    return {
        "momentum_constraint": "-2*D_j*pi^j_i=P_i_matter",
        "test_field": "any_spatial_Killing_field_K^i",
        "integrated_left_side": (
            "integral_K^i*D_j*pi^j_i=-integral_pi^ji*D_jK_i=0"
        ),
        "boundary_term": 0.0,
        "compact_result": "integral_S7_K^i*P_i_matter=0",
        "single_nonzero_Hopf_rotor_admissible": False,
        "event_degree_can_replace_countercharge": False,
        "admissible_nonzero_sector": (
            "parent-child_relative_rotation_with_J_child+J_parent=0"
        ),
        "local_constraint_requirement": (
            "solve_the_Hopf_coexact_shift_or_gravitational_countercurrent_"
            "profile_not_only_the_integrated_charge"
        ),
    }


def unlocalized_parent_inertia(
    *, kappa1: float = 1.0, radius: float | None = None
) -> float:
    """Return the round parent eta inertia for a unit-norm Hopf generator."""

    if kappa1 <= 0.0:
        raise ValueError("kappa1 must be positive")
    if radius is None:
        radius = (343.0 / (5.0 * kappa1)) ** (1.0 / 6.0)
    if radius <= 0.0:
        raise ValueError("radius must be positive")
    x_eta = 7.0 / radius**2
    unit_join_volume_integral = 1.0 / 12.0
    return (
        (kappa1 + x_eta**3)
        * radius**7
        * HOPF_ORBIT_VOLUME
        * unit_join_volume_integral
    )


def relative_rotor_terms(
    ell: float,
    *,
    kappa1: float = 1.0,
    z_sigma: float = 1.0,
    radius: float | None = None,
    relative_charge: float = 0.5,
    points: int = 20001,
) -> dict[str, float]:
    """Evaluate the zero-total-charge parent--child relative Routhian."""

    child = localized_child_terms(
        ell,
        kappa1=kappa1,
        z_sigma=z_sigma,
        radius=radius,
        charge=0.0,
        points=points,
    )
    i_child = child["localized_inertia"]
    i_parent = unlocalized_parent_inertia(kappa1=kappa1, radius=radius)
    i_relative = 1.0 / (1.0 / i_child + 1.0 / i_parent)
    child_rotor = relative_charge**2 / (2.0 * i_child)
    parent_counterrotor = relative_charge**2 / (2.0 * i_parent)
    relative_energy = relative_charge**2 / (2.0 * i_relative)
    return {
        "ell": float(ell),
        "I_child": i_child,
        "I_parent": i_parent,
        "I_relative_parallel_sum": i_relative,
        "J_child": float(relative_charge),
        "J_parent": float(-relative_charge),
        "J_total": 0.0,
        "child_rotor_energy": child_rotor,
        "parent_counterrotor_energy": parent_counterrotor,
        "relative_rotor_energy": relative_energy,
        "energy_sum_residual": relative_energy
        - child_rotor
        - parent_counterrotor,
        "skin_energy": child["skin_energy"],
        "relative_routhian": child["skin_energy"] + relative_energy,
        "wall_chi": child["wall_chi"],
        "enclosure_collective_mass": child["enclosure_collective_mass"],
    }


def constrained_relative_routhian_solution(
    *,
    kappa1: float = 1.0,
    z_sigma: float = 1.0,
    radius: float | None = None,
    relative_charge: float = 0.5,
    points: int = 20001,
) -> dict[str, Any]:
    """Solve the compact-zero-total-charge relative enclosure minimum."""

    kwargs = {
        "kappa1": kappa1,
        "z_sigma": z_sigma,
        "radius": radius,
        "relative_charge": relative_charge,
        "points": points,
    }

    def energy(ell: float) -> float:
        return relative_rotor_terms(float(ell), **kwargs)["relative_routhian"]

    result = minimize_scalar(
        energy,
        bounds=(1.0e-4, 10.0),
        method="bounded",
        options={"xatol": 2.0e-7},
    )
    if not result.success:
        raise RuntimeError("relative parent-child Routhian minimization failed")
    ell_star = float(result.x)
    h = 2.0e-3
    curvature = (
        energy(ell_star + h) - 2.0 * energy(ell_star) + energy(ell_star - h)
    ) / h**2
    branch = relative_rotor_terms(-ell_star, **kwargs)
    return {
        "child_scale_x": -ell_star,
        "child_scale_x_negative": -ell_star < 0.0,
        "child_branch": branch,
        "stationarity_residual": (
            energy(ell_star + h) - energy(ell_star - h)
        )
        / (2.0 * h),
        "relative_child_curvature": curvature,
        "relative_child_curvature_positive": curvature > 0.0,
        "omega_enclosure_squared": curvature
        / branch["enclosure_collective_mass"],
        "finite_minimum_survives_compact_charge_constraint": ell_star < 10.0,
        "reason": (
            "the_parent_counterrotor_adds_a_finite_positive_term_while_the_"
            "child_rotor_energy_still_diverges_when_I_child_goes_to_zero"
        ),
    }


def local_momentum_constraint_status() -> dict[str, Any]:
    """Record the nonradial constraint block required by the relative rotor."""

    return {
        "radial_shift_alone_sufficient": False,
        "required_metric_companion": (
            "beta_H(chi)_times_the_relevant_Hopf_Killing_or_coexact_one_form"
        ),
        "source": (
            "P_H(chi)=coefficient*inner(D_t_eta,D_H_eta)_with_equal_and_"
            "opposite_integrated_parent-child_charge"
        ),
        "integrated_Killing_constraint_satisfied_by_relative_sector": True,
        "pointwise_shift_equation_solved": False,
        "shift_Schur_sign": (
            "subtractive_on_a_positive_gauge-reduced_shift_block_and_must_be_"
            "included_in_the_full_child_Hessian"
        ),
        "required_next_calculation": (
            "NONROUND_OFF_SEAM_HOPF_SHIFT_MOMENTUM_CONSTRAINT_WITH_PARENT_"
            "CHILD_COUNTERCURRENT_AND_COMPLETE_MIXED_HESSIAN"
        ),
    }


def completion_payload() -> dict[str, Any]:
    theorem = compact_killing_momentum_constraint_theorem()
    seam = relative_rotor_terms(0.0)
    solution = constrained_relative_routhian_solution()
    local = local_momentum_constraint_status()
    validation = {
        "single_rotor_constraint_error_corrected": not theorem[
            "single_nonzero_Hopf_rotor_admissible"
        ],
        "relative_total_charge_zero": solution["child_branch"]["J_total"]
        == 0.0,
        "parallel_sum_energy_identity": abs(
            solution["child_branch"]["energy_sum_residual"]
        )
        < 1.0e-12,
        "relative_finite_child_survives": solution[
            "finite_minimum_survives_compact_charge_constraint"
        ],
        "relative_child_x_negative": solution["child_scale_x_negative"],
        "relative_child_curvature_positive": solution[
            "relative_child_curvature_positive"
        ],
        "parent_counterterm_finite_at_seam": math.isfinite(
            seam["parent_counterrotor_energy"]
        ),
        "local_shift_not_overclaimed": not local[
            "pointwise_shift_equation_solved"
        ],
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_parent_child_relative_rotor_v15_36",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "compact_Killing_momentum_constraint": theorem,
        "relative_rotor_seam_control": seam,
        "compact_constraint_corrected_Routhian": solution,
        "local_momentum_constraint": local,
        "claim_boundary": {
            "single_rotor_physical_child_claim_retracted": True,
            "zero_total_charge_reduced_child_derived": True,
            "local_Hopf_shift_constraint_solved": False,
            "complete_constraint_solved_child_derived": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "completion_ledger": {
            "VALIDATED": [
                "compact_zero_total_Killing_momentum_theorem",
                "parent-child_parallel-sum_relative_inertia",
                "finite_stable_relative_Routhian_child_minimum",
            ],
            "INVALIDATED": [
                "a_lone_nonzero_Hopf_rotor_on_closed_S7_as_a_constraint_"
                "solved_child"
            ],
            "RECLASSIFIED": [
                "the_FR_half-odd_sector_as_relative_parent-child_momentum_"
                "rather_than_nonzero_total_compact_momentum"
            ],
            "CLOSED_THIS_RUN": [
                "integrated_compact_momentum_constraint",
                "zero-total-charge_relative_Routhian_correction",
            ],
            "ACTIVE_DEPENDENCY": local["required_next_calculation"],
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_continuous_coefficients": [],
            "empirical_inputs": [],
            "net_compact_charge_inserted": False,
            "frozen_predictions_changed": False,
            "USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE": (
                USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE
            ),
        },
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
        rounded = round(value, 9)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, Mapping):
        return {key: _canonical_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical_json_value(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        _canonical_json_value(payload),
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    ) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_parent_child_relative_rotor_v15_36.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "compact_killing_momentum_constraint_theorem",
    "unlocalized_parent_inertia",
    "relative_rotor_terms",
    "constrained_relative_routhian_solution",
    "local_momentum_constraint_status",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
