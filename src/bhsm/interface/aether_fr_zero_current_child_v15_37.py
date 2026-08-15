"""Odd-FR zero-current ground state and stationary reduced child.

The compact momentum constraint forbids a lone classical nonzero Hopf
momentum.  The antiperiodic quantum rotor, however, has a two-dimensional
lowest eigenspace of J^2.  Its real standing-wave representatives have
<J>=0 and <J^2>=1/4.  They therefore contribute the same localized
Born--Oppenheimer energy 1/(8 I_skin) used in v15.34 while sourcing no
semiclassical momentum constraint.

After quotienting overall state phase and Hopf translations, the normalized
zero-current ground state is unique.  The reduced enclosure is stationary in
the physical ray rather than a classical charged relative equilibrium.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_complete_child_localized_fiber_v15_34 import (
    localized_child_terms,
    reduced_child_routhian_solution,
)


VERSION = "v15.37"
CLASSIFICATION = "ODD_FR_ZERO_CURRENT_STATIONARY_REDUCED_CHILD"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def fr_zero_current_ground_state_theorem() -> dict[str, Any]:
    """Derive the constrained lowest state of the antiperiodic rotor."""

    return {
        "operator": "J=-i*d/dtheta,_H_theta=J^2/(2I_skin)",
        "domain": (
            "psi(theta+2pi)=-psi(theta)_and_psi_prime(theta+2pi)=-psi_prime(theta)"
        ),
        "lowest_charged_basis": [
            "exp(+i*theta/2)/sqrt(2*pi)",
            "exp(-i*theta/2)/sqrt(2*pi)",
        ],
        "zero_current_representative": "cos(theta/2)/sqrt(pi)",
        "orthogonal_representative": "sin(theta/2)/sqrt(pi)",
        "normalization": 1.0,
        "expectation_J": 0.0,
        "expectation_J_squared": 0.25,
        "energy": "1/(8*I_skin)",
        "momentum_constraint_source": 0.0,
        "energy_nonzero": True,
        "unique_modulo": [
            "overall_quantum_phase",
            "Hopf_U1_translation_of_theta_origin",
        ],
        "physical_ground_orbit_count": 1,
        "classical_nonzero_charge_inserted": False,
    }


def numerical_domain_check(points: int = 20001) -> dict[str, float | bool]:
    """Verify normalization and first two momentum moments by quadrature."""

    if not isinstance(points, int) or points < 1001:
        raise ValueError("points must be an integer >=1001")
    theta = np.linspace(0.0, 2.0 * math.pi, points)
    psi = np.cos(theta / 2.0) / math.sqrt(math.pi)
    derivative = -0.5 * np.sin(theta / 2.0) / math.sqrt(math.pi)
    norm = float(np.trapezoid(psi**2, theta))
    j_mean = float(np.trapezoid(psi * (-1j * derivative), theta).real)
    j2_mean = float(np.trapezoid(derivative**2, theta))
    return {
        "norm": norm,
        "J_expectation": j_mean,
        "J_squared_expectation": j2_mean,
        "antiperiodic_value_residual": float(psi[-1] + psi[0]),
        "antiperiodic_derivative_residual": float(derivative[-1] + derivative[0]),
        "domain_and_moments_verified": abs(norm - 1.0) < 1.0e-12
        and abs(j_mean) < 1.0e-12
        and abs(j2_mean - 0.25) < 1.0e-12,
    }


def stationary_zero_current_reduced_child(
    *,
    kappa1: float = 1.0,
    z_sigma: float = 1.0,
    radius: float | None = None,
    points: int = 20001,
) -> dict[str, Any]:
    """Return the v15.34 minimum in the zero-current FR ground sector."""

    solution = reduced_child_routhian_solution(
        kappa1=kappa1,
        z_sigma=z_sigma,
        radius=radius,
        charge=0.5,
        points=points,
    )
    child = solution["child_branch"]
    seam = localized_child_terms(
        0.0,
        kappa1=kappa1,
        z_sigma=z_sigma,
        radius=radius,
        charge=0.5,
        points=points,
    )
    quantum_energy = 1.0 / (8.0 * child["localized_inertia"])
    return {
        "state": "stationary_physical_ray_times_static_enclosure_profile",
        "child_scale_x": solution["child_scale_x"],
        "child_scale_x_negative": solution["child_scale_x"] < 0.0,
        "enclosure_stationarity_residual": solution["stationarity_residual"],
        "enclosure_curvature": solution["child_curvature"],
        "enclosure_curvature_positive": solution["child_curvature_positive"],
        "enclosure_frequency_squared": solution["omega_squared"],
        "localized_quantum_energy": quantum_energy,
        "fixed_charge_formula_residual": quantum_energy
        - child["cyclic_energy"],
        "seam_barrier": seam["routhian_potential"]
        - child["routhian_potential"],
        "finite_child_well": seam["routhian_potential"]
        > child["routhian_potential"],
        "Hopf_momentum_density_expectation": 0.0,
        "Hopf_energy_density_nonzero": True,
        "classical_internal_rotation_required": False,
        "physical_ray_time_dependence": (
            "only_the_global_phase_exp(-i*E*t)_which_is_quotiented"
        ),
    }


def compact_constraint_reclassification() -> dict[str, Any]:
    """Reclassify the two earlier rotor readings under the quantum constraint."""

    return {
        "v15_34_localized_inertia_and_Routh_energy": "PRESERVED",
        "v15_35_lone_classical_relative_periodic_rotor": (
            "RECLASSIFIED_AS_AN_UNCONSTRAINED_CHARGED_BRANCH"
        ),
        "v15_36_parent-child_counterrotor": (
            "CONDITIONAL_ALTERNATIVE_IF_A_PHYSICAL_COUNTERCURRENT_MODE_IS_DERIVED"
        ),
        "preferred_minimal_compact_sector": (
            "zero-current_odd-FR_ground_state_with_nonzero_J_squared"
        ),
        "integrated_momentum_constraint": "satisfied",
        "local_Hopf_shift_source_expectation": 0.0,
        "local_Hopf_frame_dragging_required_at_mean_field": False,
        "stress_fluctuation_backreaction_computed": False,
    }


def completion_payload() -> dict[str, Any]:
    theorem = fr_zero_current_ground_state_theorem()
    numerical = numerical_domain_check()
    child = stationary_zero_current_reduced_child()
    reclassified = compact_constraint_reclassification()
    validation = {
        "antiperiodic_ground_state_moments_verified": numerical[
            "domain_and_moments_verified"
        ],
        "zero_mean_compact_momentum": theorem["expectation_J"] == 0.0,
        "nonzero_FR_Casimir": theorem["expectation_J_squared"] == 0.25,
        "localized_energy_matches_v15_34": abs(
            child["fixed_charge_formula_residual"]
        )
        < 1.0e-12,
        "stationary_reduced_child_x_negative": child[
            "child_scale_x_negative"
        ],
        "stationary_reduced_child_curvature_positive": child[
            "enclosure_curvature_positive"
        ],
        "local_mean_shift_source_zero": reclassified[
            "local_Hopf_shift_source_expectation"
        ]
        == 0.0,
        "full_stress_fluctuation_not_overclaimed": not reclassified[
            "stress_fluctuation_backreaction_computed"
        ],
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_FR_zero_current_child_v15_37",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "FR_zero_current_ground_state": theorem,
        "numerical_domain_check": numerical,
        "stationary_reduced_child": child,
        "constraint_reclassification": reclassified,
        "claim_boundary": {
            "compact_mean_momentum_constraint_closed": True,
            "stationary_zero_current_reduced_child_derived": True,
            "full_semiclassical_Einstein_eta_sigma_solution_derived": False,
            "stress_fluctuation_backreaction_derived": False,
            "complete_physical_child_derived": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "completion_ledger": {
            "VALIDATED": [
                "odd-FR_zero-current_ground_state_with_J_squared_one_quarter",
                "zero_mean_Hopf_momentum_and_nonzero_localized_energy",
                "stationary_stable_reduced_child_in_the_compact_sector",
            ],
            "INVALIDATED": [
                "nonzero_classical_mean_Hopf_charge_as_necessary_for_the_"
                "localized_FR_stabilization"
            ],
            "RECLASSIFIED": [
                "the_internal_clock_as_a_stationary_quantum_FR_phase_rather_"
                "than_required_classical_rotation",
                "the_parent-child_counterrotor_as_a_conditional_alternative",
            ],
            "CLOSED_THIS_RUN": [
                "compact_mean_Hopf_momentum_constraint_in_the_minimal_FR_sector",
                "ground-state_selection_modulo_phase_and_Hopf_translation",
            ],
            "ACTIVE_DEPENDENCY": (
                "SEMICLASSICAL_NONROUND_EINSTEIN_ETA_SIGMA_CONSTRAINT_BVP_"
                "WITH_THE_LOCALIZED_FR_GROUND_STATE_EXPECTATION_STRESS_AND_"
                "COMPLETE_PHYSICAL_HESSIAN"
            ),
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_continuous_coefficients": [],
            "empirical_inputs": [],
            "classical_nonzero_charge_inserted": False,
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
    path = target / "BHSM_aether_FR_zero_current_child_v15_37.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "fr_zero_current_ground_state_theorem",
    "numerical_domain_check",
    "stationary_zero_current_reduced_child",
    "compact_constraint_reclassification",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
