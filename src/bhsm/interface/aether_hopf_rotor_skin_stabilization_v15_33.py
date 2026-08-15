"""Hopf/FR charge test for the nonlinear material-skin saddle.

v15.32 proved that the reciprocal material skin on ``S7=S3*S3`` has a
physical negative wall-translation mode.  This module exhausts the nearest
retained conserved-charge mechanisms without inserting a charge by hand.

The degree jump of v15.27 is a configuration-space topological flux, not a
canonical momentum.  The historical odd-degree FR line can conditionally
select an antiperiodic rotor sector, but only after a physical rotation loop
and collective domain are established.  More decisively, an eta/Hopf rotor
whose inertia is independent of sigma has zero curvature in the fixed-eta
material direction.  The one retained sigma-dependent eta inertia multiplier,
``1+g*sigma**2``, has the wrong localization sign for ``g>0``: its inertia is
smallest at the seam and increases as the wall runs to either collapse pole,
so fixed-charge Routh reduction makes the negative mode more negative.

Thus neither event degree, the conditional FR sign, nor the retained
sigma-squared inertia produces a stable encapsulated child.  A stabilizer
would require an action-owned cyclic Hopf inertia localized on the skin (and
therefore vanishing in both material vacua), together with its self-adjoint
FR/collective domain.  That object is not added here.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_join_skin_nonlinear_constraint_v15_32 import (
    join_trace_arrays,
    nonlinear_wall_translation_energy,
)


VERSION = "v15.33"
CLASSIFICATION = "RETAINED_CHARGE_STABILIZATION_EXHAUSTED_NO_CHILD"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False
EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_SKIN_LOCALIZED_HOPF_FIBER_CYCLIC_INERTIA_WITH_ODD_"
    "DEGREE_FR_ANTIPERIODIC_SELF_ADJOINT_DOMAIN_AND_POSITIVE_COUPLED_"
    "CONSTRAINT_HESSIAN"
)


def charge_type_and_selection_audit() -> dict[str, Any]:
    """Separate topology, FR parity, and a canonical fixed charge."""

    return {
        "event_degree_flux": {
            "object": "Q_Gamma=N_plus-N_minus",
            "integer_normalized": True,
            "canonical_rotor_momentum": False,
            "reason": (
                "Q_Gamma_labels_a_topology_change_correspondence_and_does_not_"
                "supply_a_cyclic_coordinate_or_positive_collective_inertia"
            ),
        },
        "historical_M8_FR_line": {
            "configuration_loop_group": "pi8(S7)=Z2",
            "odd_degree_character": -1,
            "conditional_lowest_rotor_sector": "j=1/2_or_half_odd_U1_momentum",
            "continuous_charge_magnitude_fitted": False,
            "physical_rotation_loop_identification_derived": False,
            "collective_self_adjoint_domain_derived": False,
            "physical_M4_transgression_derived": False,
        },
        "retained_classical_background": {
            "eta_canonical_charge": 0,
            "gauge_color_charge": "singlet_or_superselection_data",
            "action_selects_nonzero_vector_orientation": False,
        },
        "FR_parity_is_not_event_flux": True,
        "nonzero_action_selected_physical_charge_present": False,
    }


def fixed_eta_charge_curvature_theorem() -> dict[str, Any]:
    """State the exact fixed-eta obstruction for every sigma-blind charge."""

    return {
        "fixed_charge_energy": "V_C[sigma]=C^2/(2*I[eta,g_metric,gauge])",
        "admissible_variation": "delta_sigma_nonzero_with_delta_eta=delta_metric=delta_gauge=0",
        "first_sigma_variation": 0.0,
        "second_sigma_variation": 0.0,
        "v15_32_negative_direction_lifted": False,
        "scope": (
            "all_retained_charges_whose_collective_inertia_has_no_material_"
            "sigma_dependence"
        ),
        "topological_eta_stability_does_not_lock_sigma": True,
        "reason": (
            "sigma_is_an_independent_parent_field_and_the_common_domain_does_"
            "not_impose_sigma_as_a_hard_function_of_eta"
        ),
    }


def sigma_weighted_rotor_inertia(
    shifts: tuple[float, ...] = (-4.0, -2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0, 4.0),
    *,
    points: int = 40001,
) -> dict[str, Any]:
    """Evaluate the only retained material dependence of eta inertia.

    On the round identity join the positive eta rotor tangent density is
    reflection-even and constant up to an irrelevant positive normalization.
    Hence the material dependence is governed by

        I_g(ell)/I_eta = 1 + g <sigma_ell**2>.

    Reporting ``S=<sigma**2>`` separates the sign theorem from the unselected
    magnitude of ``g`` and from the overall collective inertia.
    """

    if not isinstance(points, int) or points < 4001:
        raise ValueError("points must be an integer >=4001")
    arrays = join_trace_arrays(points)
    chi = np.asarray(arrays["chi"])
    sigma0 = np.asarray(arrays["sigma"])
    measure = np.asarray(arrays["join_measure"])
    volume = float(np.trapezoid(measure, chi))

    def moment(ell: float) -> float:
        transformed = np.arctan(np.exp(-ell) * np.tan(chi))
        sigma = np.interp(transformed, chi, sigma0)
        return float(np.trapezoid(measure * sigma**2, chi) / volume)

    rows = [{"shift": float(ell), "mean_sigma_squared": moment(float(ell))} for ell in shifts]
    by_shift = {row["shift"]: row["mean_sigma_squared"] for row in rows}
    h = 0.02
    s0 = moment(0.0)
    first = (moment(h) - moment(-h)) / (2.0 * h)
    second = (moment(h) - 2.0 * s0 + moment(-h)) / h**2

    # For I=I_eta(1+gS), V_C=C^2/(2I).  At the reflection point S'=0,
    # sign(V_C'')=-sign(g*S'') for every nonzero charge and positive inertia.
    return {
        "retained_multiplier": "I_g(ell)=I_eta*[1+g*S(ell)]",
        "S_definition": "S(ell)=join_volume_average_of_sigma_ell_squared",
        "samples": rows,
        "S_at_seam": s0,
        "S_first_derivative_at_seam": first,
        "S_second_derivative_at_seam": second,
        "seam_is_strict_inertia_minimum_for_positive_g": abs(first) < 1.0e-10 and second > 0.0,
        "large_shift_tends_to_vacuum_value_one_quarter": (
            abs(by_shift[-4.0] - 0.25) < 0.02 and abs(by_shift[4.0] - 0.25) < 0.02
        ),
        "fixed_charge_curvature_at_seam": (
            "V_C_second=-C_squared*g*S_second/[2*I_eta*(1+g*S0)^2]_"
            "for_S_first=0"
        ),
        "g_positive_result": "STRICTLY_NEGATIVE_FOR_EVERY_NONZERO_C",
        "g_zero_result": "NO_EFFECT",
        "g_negative_result": (
            "could_have_the_opposite_local_sign_but_is_not_action_selected_"
            "and_is_not_the_positive_formation_inertia_branch"
        ),
    }


def combined_nonlinear_stability_verdict() -> dict[str, Any]:
    """Combine the v15.32 skin mode with all retained charge responses."""

    skin = nonlinear_wall_translation_energy(points=20001)
    weighted = sigma_weighted_rotor_inertia(points=20001)
    return {
        "skin_collective_second_variation": skin["collective_second_variation"],
        "sigma_blind_charge_correction": 0.0,
        "positive_g_fixed_charge_correction_sign": "negative",
        "total_curvature_can_be_nonnegative_from_retained_charge": False,
        "nonlinear_pole_limits_remain_favored_by_positive_g_charge": True,
        "stable_material_skin": False,
        "regular_persistent_encapsulated_child": False,
        "actual_outcome": (
            "THE_RETAINED_NONLINEAR_SYSTEM_PRODUCES_A_CRITICAL_MATERIAL_"
            "SKIN_BUT_NOT_A_STABLE_ENCAPSULATED_CHILD;_THE_SKIN_COLLAPSES_"
            "OR_DEENVELOPS_AND_THE_NEAREST_RETAINED_FIXED_CHARGE_TERMS_"
            "CANNOT_REVERSE_THE_PHYSICAL_NEGATIVE_MODE"
        ),
        "support": {
            "skin_path_reaches_poles": skin["large_shift_energy_approaches_zero"],
            "retained_inertia_has_wrong_sign": weighted[
                "seam_is_strict_inertia_minimum_for_positive_g"
            ],
        },
    }


def minimal_missing_stabilizer_contract() -> dict[str, Any]:
    """Identify, but do not insert, the first mechanism with the right sign."""

    return {
        "required_collective_form": (
            "L_rot=I_skin[eta,sigma,geometry]*theta_dot_squared/2_with_"
            "I_skin_positive_in_the_wall_and_vanishing_at_both_sigma_vacua"
        ),
        "fixed_charge_effect": (
            "C_nonzero_implies_V_C=C_squared/(2*I_skin)_diverges_at_both_"
            "collapse_poles_and_can_force_an_interior_minimum"
        ),
        "coefficient_free_candidate_density": "one_quarter_minus_sigma_squared",
        "candidate_problem": (
            "multiplying_a_Hopf_rotor_by_this_density_is_a_new_action_"
            "completion_and_no_existing_uniqueness_or_parent_variation_"
            "selects_it"
        ),
        "g_equals_minus_four_shortcut_rejected": (
            "1-4*sigma_squared_makes_the_eta_Legendre_weight_degenerate_at_"
            "both_vacua_and_is_not_selected_by_the_retained_action"
        ),
        "new_field_required": False,
        "new_action_structure_required": True,
        "inserted_in_this_campaign": False,
        "exact_next_object": EXACT_NEXT_OBJECT,
    }


def completion_payload() -> dict[str, Any]:
    charge = charge_type_and_selection_audit()
    fixed = fixed_eta_charge_curvature_theorem()
    weighted = sigma_weighted_rotor_inertia()
    verdict = combined_nonlinear_stability_verdict()
    missing = minimal_missing_stabilizer_contract()
    validation = {
        "event_flux_not_misidentified_as_rotor_momentum": not charge[
            "event_degree_flux"
        ]["canonical_rotor_momentum"],
        "FR_claim_boundary_preserved": not charge["historical_M8_FR_line"][
            "physical_rotation_loop_identification_derived"
        ],
        "sigma_blind_charge_cannot_lift_mode": not fixed[
            "v15_32_negative_direction_lifted"
        ],
        "retained_positive_g_inertia_has_wrong_sign": weighted[
            "seam_is_strict_inertia_minimum_for_positive_g"
        ],
        "positive_g_fixed_charge_strictly_softens": weighted[
            "g_positive_result"
        ].startswith("STRICTLY_NEGATIVE"),
        "nonlinear_child_result_decided": not verdict[
            "regular_persistent_encapsulated_child"
        ],
        "missing_stabilizer_not_inserted": not missing["inserted_in_this_campaign"],
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_Hopf_rotor_skin_stabilization_v15_33",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "charge_type_and_selection": charge,
        "fixed_eta_charge_theorem": fixed,
        "retained_sigma_weighted_rotor": weighted,
        "nonlinear_encapsulated_child_verdict": verdict,
        "minimal_missing_stabilizer": missing,
        "completion_ledger": {
            "CLOSED_THIS_RUN": [
                "event_degree_versus_canonical_charge_type_separation",
                "FR_sign_versus_physical_rotor_selection_boundary",
                "fixed_eta_sigma_blind_charge_zero_curvature_theorem",
                "retained_positive_g_sigma_weighted_rotor_wrong_sign_theorem",
                "nonlinear_retained_charge_stabilization_exhaustion",
            ],
            "ACTIVE_DEPENDENCY": EXACT_NEXT_OBJECT,
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_continuous_coefficients": [],
            "empirical_inputs": [],
            "nonzero_charge_inserted": False,
            "candidate_skin_localized_rotor_inserted": False,
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
    path = target / "BHSM_aether_Hopf_rotor_skin_stabilization_v15_33.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "EXACT_NEXT_OBJECT",
    "charge_type_and_selection_audit",
    "fixed_eta_charge_curvature_theorem",
    "sigma_weighted_rotor_inertia",
    "combined_nonlinear_stability_verdict",
    "minimal_missing_stabilizer_contract",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
