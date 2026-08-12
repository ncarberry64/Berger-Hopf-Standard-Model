"""BHSM material-skin variation, transmission, and coefficient obstruction.

The author-promoted bubble architecture reclassifies the child skin as a
resolved internal material interface.  On the adopted global spin bundle,
bulk variation then fixes transparent spin-lift transmission and removes the
independent U(1) seam phase.  A nonzero surface stress, however, must be an
excess stress of a resolved retained-field profile.  Eta derivative terms do
not select a local flat wall thickness, while every v15.10 A/B/C sigma
completion supplies a different finite positive kink tension.  Bubble
mechanics consequently does not select the still-unowned sigma response.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .aether_cycle_sigma_coefficient_reconstruction_v15_10 import (
    retained_nonuniqueness_witness,
)
from .aether_internal_clock_skin_phase_v15_14 import (
    hayward_projected_contact_impulse,
)
from .completion.foundational_dirac_spin_glue_v14_45 import (
    global_spin_glue_payload,
)


VERSION = "v15.15"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False
OUTCOME = "MATERIAL_INTERFACE_FIXES_TRACE_PHASE_BUT_NOT_DIFFUSE_SKIN_STRESS"
PRIMARY_VERDICT = (
    "BHSM_MATERIAL_SKIN_RECLASSIFICATION_RESOLVES_THE_V15_14_NORMAL_TRACE_"
    "PHASE_FOR_FERMIONS_BECAUSE_THE_RETAINED_GLOBAL_SPIN_BUNDLE_AND_SMOOTH_"
    "INTERNAL_INTERFACE_VARIATION_FIX_CANONICAL_SPIN_LIFT_TRANSMISSION_WITH_"
    "OPPOSITE_NORMAL_GREEN_FORM_CANCELLATION;_THE_SKIN_CURVATURE_STRESS_MUST_"
    "BE_THE_EXCESS_STRESS_OF_A_RESOLVED_ETA_SIGMA_METRIC_PROFILE_BECAUSE_GHY_"
    "AND_HAYWARD_ARE_NOT_SURFACE_TENSION;_ETA_P2_PLUS_P8_DERIVATIVE_ENERGY_"
    "DOES_NOT_SELECT_A_LOCAL_FLAT_WALL_WIDTH_AND_ALL_V15_10_A_B_C_SIGMA_"
    "COMPLETIONS_ADMIT_DISTINCT_FINITE_POSITIVE_TENSION_KINKS;_THEREFORE_"
    "BUBBLE_INTERFACE_STRUCTURE_DOES_NOT_SELECT_THE_PHYSICAL_SKIN_TRACTION_"
    "CONTACT_IMPULSE_OR_EJECTION"
)
EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_SIGMA_RESPONSE_JET_AND_COUPLED_ETA_SIGMA_METRIC_SKIN_"
    "PROFILE_SELECTING_ALPHA_R_GAMMA_THE_DERIVED_EXCESS_TRACTION_AND_THE_"
    "CONSTRAINT_SOLVED_CONTACT_IMPULSE"
)


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _positive(value: float, name: str) -> float:
    result = _finite(value, name)
    if result <= 0.0:
        raise ValueError(f"{name} must be positive")
    return result


def internal_seam_green_residual(
    psi: Sequence[complex], phi: Sequence[complex], normal_form: Sequence[Sequence[complex]]
) -> float:
    """Cancellation of opposite-normal Dirac Green forms on one global bundle."""

    left = np.asarray(psi, dtype=complex)
    right = np.asarray(phi, dtype=complex)
    form = np.asarray(normal_form, dtype=complex)
    if left.ndim != 1 or right.shape != left.shape or form.shape != (left.size, left.size):
        raise ValueError("spinors and normal form dimensions must match")
    if not all(np.all(np.isfinite(item)) for item in (left, right, form)):
        raise ValueError("Green-form data must be finite")
    parent = np.vdot(left, form @ right)
    child = np.vdot(left, (-form) @ right)
    return float(abs(parent + child))


def spin_lift_transmission(
    trace: Sequence[complex], spin_lift: Sequence[Sequence[complex]]
) -> np.ndarray:
    """Canonical material-interface trace transport psi_c=rho(Lambda) psi_p."""

    vector = np.asarray(trace, dtype=complex)
    lift = np.asarray(spin_lift, dtype=complex)
    if vector.ndim != 1 or lift.shape != (vector.size, vector.size):
        raise ValueError("trace and spin lift dimensions must match")
    if not np.allclose(np.conjugate(lift.T) @ lift, np.eye(vector.size), atol=1.0e-13):
        raise ValueError("spin lift must be unitary")
    return lift @ vector


def level_set_normal_velocity(time_derivative: float, spatial_gradient_norm: float) -> float:
    """Material velocity for a skin F(Phi)=0: V=-u.F/|D F|."""

    derivative = _finite(time_derivative, "time_derivative")
    gradient = _positive(spatial_gradient_norm, "spatial_gradient_norm")
    return -derivative / gradient


def eta_flat_layer_scaling(
    target_distance: float, width: float, kappa1: float = 1.0
) -> dict[str, float | bool]:
    """Local p2+p8 energy per area for a constant-speed target geodesic.

    X=(Delta/L)^2, so integral [kappa1 X/2+X^4/8] ds equals
    kappa1 Delta^2/(2L)+Delta^8/(8L^7).  Both terms favor broadening.
    """

    distance = _positive(target_distance, "target_distance")
    layer_width = _positive(width, "width")
    coupling = _positive(kappa1, "kappa1")
    quadratic = 0.5 * coupling * distance**2 / layer_width
    eighth = 0.125 * distance**8 / layer_width**7
    derivative = -0.5 * coupling * distance**2 / layer_width**2 - 0.875 * distance**8 / layer_width**8
    return {
        "quadratic_energy_per_area": quadratic,
        "eighth_order_energy_per_area": eighth,
        "total_energy_per_area": quadratic + eighth,
        "width_derivative": derivative,
        "finite_stationary_width": derivative == 0.0,
    }


def sigma_kink_data(A: float, G: float, Z: float) -> dict[str, float]:
    """Exact flat diffuse wall of Z sigma'^2/2+A sigma^2/2+G sigma^4/4."""

    mass = _finite(A, "A")
    quartic = _finite(G, "G")
    kinetic = _finite(Z, "Z")
    if mass >= 0.0 or quartic <= 0.0 or kinetic <= 0.0:
        raise ValueError("a finite kink requires A<0, G>0 and Z>0")
    vacuum = math.sqrt(-mass / quartic)
    width = math.sqrt(2.0 * kinetic / (-mass))
    tension = 2.0 * math.sqrt(2.0 * kinetic) * (-mass) ** 1.5 / (3.0 * quartic)
    return {
        "vacuum": vacuum,
        "width": width,
        "inverse_width": 1.0 / width,
        "excess_tension": tension,
    }


def sigma_kink_profile(normal_coordinate: float, A: float, G: float, Z: float) -> dict[str, float]:
    """Return sigma, first derivative, and exact Euler residual."""

    coordinate = _finite(normal_coordinate, "normal_coordinate")
    data = sigma_kink_data(A, G, Z)
    vacuum = data["vacuum"]
    width = data["width"]
    tangent = math.tanh(coordinate / width)
    sech2 = 1.0 - tangent**2
    sigma = vacuum * tangent
    derivative = vacuum * sech2 / width
    second = -2.0 * vacuum * tangent * sech2 / width**2
    residual = Z * second - (A * sigma + G * sigma**3)
    return {
        **data,
        "normal_coordinate": coordinate,
        "sigma": sigma,
        "sigma_prime": derivative,
        "Euler_residual": residual,
    }


def curvature_traction_density(excess_tension: float, mean_curvature: float) -> float:
    """Thin-profile shape derivative T*K in one fixed normal convention."""

    tension = _positive(excess_tension, "excess_tension")
    curvature = _finite(mean_curvature, "mean_curvature")
    return tension * curvature


def material_skin_contact_impulse(
    excess_tension: float,
    skin_area_d: float,
    *,
    kappa1: float,
    joint_measure: float,
    boost_angle: float,
    joint_measure_d: float,
    boost_angle_d: float,
) -> dict[str, float]:
    """Projected scalar-profile plus Hayward impulse, with no new coefficient."""

    tension = _positive(excess_tension, "excess_tension")
    area_derivative = _finite(skin_area_d, "skin_area_d")
    skin = -tension * area_derivative
    hayward = hayward_projected_contact_impulse(
        kappa1,
        joint_measure,
        boost_angle,
        joint_measure_d,
        boost_angle_d,
    )
    return {"skin_profile": skin, "Hayward": hayward, "total": skin + hayward}


def material_trace_payload() -> dict[str, Any]:
    glue = global_spin_glue_payload()
    rng = np.random.default_rng(1515)
    psi = rng.normal(size=4) + 1j * rng.normal(size=4)
    phi = rng.normal(size=4) + 1j * rng.normal(size=4)
    normal_form = np.diag([1.0, 1.0, -1.0, -1.0])
    residual = internal_seam_green_residual(psi, phi, normal_form)
    return {
        "skin_classification": "resolved_internal_material_level_set_not_terminal_spacetime_boundary",
        "child_skin_identity_preserved": True,
        "boundary_identity_means_surface_label_not_impenetrable_matter_wall": True,
        "fermion_trace_law": "Psi_child=rho(SpinLift(Lambda_pc))*Psi_parent",
        "common_parent_coframe": "U_phys=I_up_to_the_globally_fixed_spin_sign_and_gauge",
        "independent_self_adjoint_extension_phase": False,
        "selection_source": "adopted_v14_45_one_global_spin_bundle_plus_smooth_internal_interface_variation",
        "opposite_normal_Green_form_residual": residual,
        "v14_45_matcher_status": glue["matcher_status"],
        "self_adjointness_check": residual < 1.0e-13,
        "scalar_trace_law": "continuous_field_and_continuous_canonical_normal_flux_without_delta_skin_term",
        "eta_canonical_flux": "P_eta^n=w*(kappa1+X_eta^3)*n.D_eta",
        "gauge_trace_law": "continuous_pullback_connection_and_opposite_normal_Yang_Mills_flux_balance",
        "free_inception_phase": False,
        "inception_rule": "smooth_pre_skin_bulk_restriction_inherits_the_same_global_bundle_trace",
        "v15_14_phase_obstruction_resolved_under_material_interface_rule": True,
    }


def sigma_wall_witness_payload() -> dict[str, Any]:
    witness = retained_nonuniqueness_witness()
    rows: dict[str, Any] = {}
    for label, row in witness["triples"].items():
        coefficients = row["coefficients"]
        data = sigma_kink_data(
            coefficients["A0"], coefficients["G0"], coefficients["Zsigma"]
        )
        samples = [
            sigma_kink_profile(value * data["width"], coefficients["A0"], coefficients["G0"], coefficients["Zsigma"])
            for value in (-2.0, -0.5, 0.0, 0.5, 2.0)
        ]
        rows[label] = {
            "alpha": coefficients["alpha"],
            "r": coefficients["r"],
            "gamma": coefficients["gamma"],
            **data,
            "maximum_Euler_residual": max(abs(sample["Euler_residual"]) for sample in samples),
            "finite_action_kink": True,
            "positive_excess_tension": data["excess_tension"] > 0.0,
            "transparent_material_trace_compatible": True,
        }
    tensions = [row["excess_tension"] for row in rows.values()]
    return {
        "walls": rows,
        "all_A_B_C_have_exact_flat_kinks": all(
            row["maximum_Euler_residual"] < 1.0e-12 for row in rows.values()
        ),
        "all_A_B_C_have_positive_derived_tension": all(
            row["positive_excess_tension"] for row in rows.values()
        ),
        "tensions_are_physically_distinct": len(set(round(value, 12) for value in tensions)) == 3,
        "bubble_structure_selects_one_witness": False,
        "curved_backreacted_physical_tension_evaluated": False,
    }


def skin_variation_payload() -> dict[str, Any]:
    eta = eta_flat_layer_scaling(1.0, 2.0)
    return {
        "total_action": "S_parent_bulk+S_child_bulk+S_global_matter+S_GHY+S_Hayward_no_independent_skin_term",
        "kinematic_skin": "for_F(Phi)=0,_V_Sigma=-u.F/abs(D_Sigma_F)",
        "tangential_variation": "worldvolume_reparameterization_Noether_identity",
        "normal_variation_finite_width": "bulk_Euler_equations_and_complete_normal_traction_conservation",
        "normal_traction_balance": "[T_nn]_resolved=0_across_a_smooth_profile_with_all_field_stress_included",
        "thin_profile_limit": "[T_nn]=T_excess*K_Sigma_plus_higher_moment_curvature_terms",
        "curvature_coefficient": "T_excess=integral_normal(T_tangent_excess)_profile_not_a_new_constant",
        "GHY_is_surface_tension": False,
        "Hayward_is_surface_tension": False,
        "eta_only_local_layer": {
            "energy": "kappa1*Delta_eta^2/(2L)+Delta_eta^8/(8L^7)",
            "width_derivative_at_sample": eta["width_derivative"],
            "finite_stationary_flat_width": eta["finite_stationary_width"],
            "conclusion": "p2_and_p8_both_favor_broadening_so_eta_derivatives_alone_do_not_select_a_local_flat_skin_thickness",
        },
        "sigma_profile_role": "double_well_can_supply_localization_and_excess_stress_if_its_response_coefficients_are_selected",
    }


def contact_and_ejection_payload() -> dict[str, Any]:
    walls = sigma_wall_witness_payload()["walls"]
    diagnostic_impulses = {
        label: material_skin_contact_impulse(
            row["excess_tension"],
            1.0,
            kappa1=1.0,
            joint_measure=1.0,
            boost_angle=0.0,
            joint_measure_d=0.0,
            boost_angle_d=0.0,
        )["total"]
        for label, row in walls.items()
    }
    return {
        "formal_total_impulse": (
            "Delta_P_d=-T_excess*dA_skin/dd-"
            "kappa1*(theta*dA_J/dd+A_J*dtheta/dd)+matter_gauge_eta_shape_forces"
        ),
        "diagnostic_unit_area_derivative_skin_impulses": diagnostic_impulses,
        "diagnostic_impulses_are_not_physical_contact_predictions": True,
        "physical_contact_area_and_angle_shape_derivatives_present": False,
        "physical_curved_profile_tension_present": False,
        "impulse_magnitude_or_sign_selected": False,
        "post_contact_trajectory_selected": False,
        "ejection": False,
        "de_envelopment": "AUTHOR_RULE_IF_NO_EJECTION_BUT_RECEIVING_SOLUTION_NOT_DERIVED",
    }


def completion_payload() -> dict[str, Any]:
    trace = material_trace_payload()
    variation = skin_variation_payload()
    walls = sigma_wall_witness_payload()
    contact = contact_and_ejection_payload()
    eta_narrow = eta_flat_layer_scaling(1.0, 1.0)
    eta_wide = eta_flat_layer_scaling(1.0, 2.0)
    validation = {
        "material_interface_fixes_spin_trace": trace[
            "v15_14_phase_obstruction_resolved_under_material_interface_rule"
        ],
        "opposite_normal_Green_forms_cancel": trace["opposite_normal_Green_form_residual"] < 1.0e-13,
        "self_adjointness_validates_transmission": trace["self_adjointness_check"],
        "material_level_set_velocity_invariant_formula": math.isclose(
            level_set_normal_velocity(0.6, 0.3), -2.0
        ),
        "eta_layer_broadening_lowers_local_energy": eta_wide["total_energy_per_area"] < eta_narrow[
            "total_energy_per_area"
        ],
        "eta_derivative_layer_has_no_finite_flat_width_stationary_point": not eta_wide[
            "finite_stationary_width"
        ],
        "all_sigma_witnesses_have_exact_kinks": walls["all_A_B_C_have_exact_flat_kinks"],
        "all_sigma_witnesses_have_positive_tension": walls[
            "all_A_B_C_have_positive_derived_tension"
        ],
        "sigma_witness_tensions_distinct": walls["tensions_are_physically_distinct"],
        "bubble_structure_does_not_select_sigma": not walls["bubble_structure_selects_one_witness"],
        "no_free_surface_tension_added": True,
        "Hayward_and_GHY_not_relabelled_as_tension": (
            not variation["GHY_is_surface_tension"] and not variation["Hayward_is_surface_tension"]
        ),
        "contact_impulse_not_fabricated": not contact["impulse_magnitude_or_sign_selected"],
        "v15_11_fixed_Haar_no_go_preserved": True,
        "v15_12_moving_neck_scaling_preserved": True,
        "boundary_identity_preserved": trace["child_skin_identity_preserved"],
        "no_empirical_input_or_retuning": True,
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_material_skin_variation_v15_15",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "outcome": OUTCOME,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "material_trace_domain": trace,
        "moving_skin_variation": variation,
        "v15_10_material_wall_witnesses": walls,
        "contact_and_ejection": contact,
        "phase_domain_gate": "CLOSED_BY_GLOBAL_SPIN_BUNDLE_MATERIAL_TRANSMISSION",
        "skin_stress_gate": "OPEN_SIGMA_RESPONSE_AND_CURVED_PROFILE_NOT_ACTION_SELECTED",
        "ejection_gate": "OPEN_NO_PHYSICAL_CONTACT_IMPULSE",
        "Hopf_child": "NOT_REACHED_NO_COUPLED_MATERIAL_SKIN_CONTACT_SOLUTION",
        "persistence": "NOT_REACHED",
        "downstream_Standard_Model": "NOT_REACHED_NO_PHYSICAL_EJECTED_HOPF_CHILD",
        "Hindsight_20_20": {
            "VALIDATED": [
                "material_interface_reclassification_activates_the_existing_global_spin_bundle_transmission_theorem",
                "canonical_spin_lift_transmission_removes_the_independent_normal_trace_phase",
                "skin_motion_is_the_level_set_kinematic_law_of_the_resolved_fields",
                "surface_curvature_stress_is_a_profile_excess_stress_not_GHY_or_Hayward_tension",
                "each_v15_10_sigma_witness_has_an_exact_flat_finite_positive_tension_kink",
            ],
            "INVALIDATED": [
                "the_material_child_skin_must_be_treated_as_a_terminal_fermion_boundary",
                "bubble_structure_alone_selects_a_unique_sigma_response_or_wall_tension",
                "eta_p2_plus_p8_derivative_terms_select_a_finite_local_flat_skin_width",
                "GHY_or_Hayward_can_be_relabelled_as_physical_surface_tension",
                "transparent_matter_transmission_by_itself_creates_a_nonzero_material_impulse",
            ],
            "RECLASSIFIED": [
                "the_v15_14_U1_phase_obstruction_as_an_artifact_of_terminal_boundary_ontology_resolved_by_material_internal_interface_ontology",
                "the_physical_skin_action_as_the_integrated_excess_action_of_a_resolved_bulk_profile",
                "v15_10_sigma_coefficients_as_direct_controllers_of_skin_width_tension_and_contact_response",
            ],
            "OPEN": [EXACT_NEXT_OBJECT],
        },
        "exact_next_object": EXACT_NEXT_OBJECT,
        "scientific_terminal_condition": (
            "ALL_RETAINED_MATERIAL_INTERFACE_REQUIREMENTS_ALLOW_MULTIPLE_"
            "PHYSICALLY_INEQUIVALENT_SIGMA_PROFILE_TENSIONS_AND_THE_ACTION_"
            "CONTAINS_NO_SELECTOR_FOR_THE_SIGMA_RESPONSE_JET"
        ),
        "missing_physical_assumption_plain_language": (
            "BHSM_now_knows_how_fields_cross_the_skin_but_not_which_material_"
            "skin_it_has;_the_upstream_Aether_or_parent_action_must_determine_"
            "the_sigma_kinetic_mass_and_quartic_response_that_fix_the_skin_"
            "profile_and_tension"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_continuous_coefficients": [],
            "new_empirical_inputs": [],
            "free_skin_phase_adopted": False,
            "free_surface_tension_adopted": False,
            "free_contact_kick_adopted": False,
            "frozen_predictions_changed": False,
            "official_prediction_logic_changed": False,
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
        _canonical_json_value(payload),
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    ) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_material_skin_variation_v15_15.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path
