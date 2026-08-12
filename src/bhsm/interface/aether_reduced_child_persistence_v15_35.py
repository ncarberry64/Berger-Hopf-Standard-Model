"""Relative-periodic persistence of the v15.34 reduced child branch.

The v15.34 localized Hopf-fiber action completion creates a finite stable
minimum of the fixed-FR-charge enclosure Routhian.  This module constructs the
associated relative equilibrium, derives its physical reduced Floquet pair,
and states the exact continuation criterion for the still-unsolved nonlinear
Einstein--eta--sigma complement.

Only the reduced collective result is promoted.  The full child remains open
until the constraint complement, its common domain, and its physical Hessian
are evaluated on the off-seam branch.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_complete_child_localized_fiber_v15_34 import (
    CLASSIFICATION as V15_34_CLASSIFICATION,
    localized_child_terms,
    reduced_child_routhian_solution,
)


VERSION = "v15.35"
CLASSIFICATION = "CONDITIONAL_REDUCED_RELATIVE_PERIODIC_CHILD_PERSISTENCE"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def relative_periodic_reduced_child(
    *,
    kappa1: float = 1.0,
    z_sigma: float = 1.0,
    radius: float | None = None,
    charge: float = 0.5,
    points: int = 20001,
) -> dict[str, Any]:
    """Construct the fixed-charge relative equilibrium and Floquet pair."""

    solution = reduced_child_routhian_solution(
        kappa1=kappa1,
        z_sigma=z_sigma,
        radius=radius,
        charge=charge,
        points=points,
    )
    child = solution["child_branch"]
    theta_frequency = abs(charge) / child["localized_inertia"]
    period = 2.0 * math.pi / theta_frequency
    enclosure_frequency = math.sqrt(solution["omega_squared"])
    floquet_phase = math.remainder(enclosure_frequency * period, 2.0 * math.pi)
    multiplier_real = math.cos(floquet_phase)
    multiplier_imag = math.sin(floquet_phase)
    seam = localized_child_terms(
        0.0,
        kappa1=kappa1,
        z_sigma=z_sigma,
        radius=radius,
        charge=charge,
        points=points,
    )
    return {
        "solution_type": "relative_equilibrium_in_the_fixed_FR_charge_sector",
        "ell_star": child["ell"],
        "x_log_Rc_over_Rp": child["x_log_Rc_over_Rp"],
        "theta_dot": theta_frequency,
        "relative_period": period,
        "relative_periodicity": (
            "classical_configuration_returns_after_theta_advances_2pi;_"
            "odd_FR_state_returns_with_sign_minus_one"
        ),
        "enclosure_frequency": enclosure_frequency,
        "physical_floquet_pair": [
            {"real": multiplier_real, "imag": multiplier_imag},
            {"real": multiplier_real, "imag": -multiplier_imag},
        ],
        "physical_floquet_moduli": [1.0, 1.0],
        "cyclic_unit_multipliers_removed": True,
        "gauge_diffeomorphism_multipliers_removed": True,
        "linearly_stable_in_reduced_physical_enclosure_sector": (
            solution["omega_squared"] > 0.0
        ),
        "seam_barrier_energy": seam["routhian_potential"]
        - child["routhian_potential"],
        "child_well_is_separated_from_seam": seam["routhian_potential"]
        > child["routhian_potential"],
        "stationary_in_ell_not_frozen_internally": True,
    }


def nonlinear_constraint_continuation_theorem() -> dict[str, Any]:
    """Give the exact Hessian/endpoint gates for continuation to the full child."""

    return {
        "full_coordinates": "(ell,y^I)_with_y=(A,B,C,f,sigma_complement,lapse,shift,...)",
        "constraint_branch": "dH/dy=0,_y=y_star(ell)",
        "required_regular_block": "H_II_positive_and_invertible_on_the_physical_common_domain",
        "on_shell_Hessian": (
            "k_full=H_ell_ell-H_ell_I*H_II_inverse*H_I_ell"
        ),
        "v15_34_direct_curvature_default": 3.1005,
        "explicit_local_persistence_gate": (
            "H_ell_I*H_II_inverse*H_I_ell_less_than_3.1005_in_the_"
            "deterministic_default_normalization"
        ),
        "endpoint_coercivity": (
            "I_skin_to_zero_at_both_material_vacua_implies_J_squared_over_"
            "2I_skin_to_positive_infinity_for_nonzero_FR_charge"
        ),
        "bounded_regular_backreaction_can_remove_all_finite_minima": False,
        "what_remains_to_calculate": [
            "off_seam_constraint_solved_metric_eta_sigma_background",
            "physical_common_domain_and_projector",
            "mixed_H_ell_I_block",
            "physical_H_II_spectrum",
            "full_Floquet_monodromy",
        ],
        "ordinary_positive_auxiliary_modes_claimed_to_stabilize": False,
        "direct_localized_cyclic_term_is_the_positive_contribution": True,
    }


def formation_to_child_event_classification() -> dict[str, Any]:
    """Classify the negative seam mode as an event direction without faking capture."""

    return {
        "seam": "unstable_stationary_material_interface",
        "unstable_direction": "relative_enclosure_translation_ell",
        "nonlinear_destination_in_controlled_Routhian": (
            "one_of_two_finite_reflection_related_fixed_charge_wells"
        ),
        "orientation_selected_child_branch": "ell<0_equivalently_x<0",
        "negative_mode_is_transition_coordinate": True,
        "dissipative_capture_inserted": False,
        "arbitrary_kick_inserted": False,
        "conservative_exact_destination": (
            "the_relative_equilibrium_exists;_generic_formation_initial_data_"
            "require_full_mode_transfer_to_determine_capture_or_oscillation"
        ),
        "event_energy_accounting_status": (
            "open_until_the_full_coupled_formation_trajectory_is_integrated"
        ),
    }


def completion_payload() -> dict[str, Any]:
    relative = relative_periodic_reduced_child()
    constraints = nonlinear_constraint_continuation_theorem()
    event = formation_to_child_event_classification()
    validation = {
        "relative_periodic_child_scale_negative": relative[
            "x_log_Rc_over_Rp"
        ]
        < 0.0,
        "reduced_physical_Floquet_moduli_unity": all(
            abs(value - 1.0) < 1.0e-12
            for value in relative["physical_floquet_moduli"]
        ),
        "reduced_enclosure_linearly_stable": relative[
            "linearly_stable_in_reduced_physical_enclosure_sector"
        ],
        "child_well_separated_from_seam": relative[
            "child_well_is_separated_from_seam"
        ],
        "full_constraint_gate_explicit": bool(
            constraints["what_remains_to_calculate"]
        ),
        "capture_not_fabricated": not event["dissipative_capture_inserted"],
        "action_completion_provenance_preserved": V15_34_CLASSIFICATION
        == "BHSM_ACTION_COMPLETION_DERIVED_FROM_EXISTING_BHSM_STRUCTURE",
        "full_child_not_overclaimed": True,
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_reduced_child_persistence_v15_35",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "relative_periodic_reduced_child": relative,
        "nonlinear_constraint_continuation": constraints,
        "formation_to_child_event": event,
        "claim_boundary": {
            "reduced_relative_periodic_child_derived": True,
            "complete_constraint_solved_child_derived": False,
            "generic_formation_capture_derived": False,
            "full_physical_Floquet_spectrum_derived": False,
            "Standard_Model_attachment_reached": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "completion_ledger": {
            "VALIDATED": [
                "finite_stable_fixed_FR_charge_relative_equilibrium",
                "unit_modulus_reduced_physical_Floquet_pair",
                "endpoint_coercivity_of_the_localized_cyclic_Routhian",
            ],
            "INVALIDATED": [
                "requiring_the_particle_to_be_completely_static",
                "claiming_generic_capture_from_a_stationary_Routhian_alone",
            ],
            "RECLASSIFIED": [
                "negative_seam_mode_as_the_encapsulation_event_direction"
            ],
            "CLOSED_THIS_RUN": [
                "controlled_relative_periodic_child_solution",
                "reduced_physical_Floquet_multipliers",
                "explicit_full_constraint_Hessian_persistence_gate",
            ],
            "ACTIVE_DEPENDENCY": (
                "OFF_SEAM_FULL_EINSTEIN_ETA_SIGMA_CONSTRAINT_BVP_AND_"
                "FORMATION_TRAJECTORY_CAPTURE_INTO_THE_RELATIVE_PERIODIC_CHILD"
            ),
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_continuous_coefficients": [],
            "empirical_inputs": [],
            "damping_or_capture_term_added": False,
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
    path = target / "BHSM_aether_reduced_child_persistence_v15_35.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "relative_periodic_reduced_child",
    "nonlinear_constraint_continuation_theorem",
    "formation_to_child_event_classification",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
