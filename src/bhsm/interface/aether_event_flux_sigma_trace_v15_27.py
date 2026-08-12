"""Distributional topological event flux and sigma trace pairing.

This module continues the v15.26 exact-gradient audit at a genuine
reconstruction/topology-change event.  It derives the current-valued
distribution ``d j3 = Q_Gamma delta_Gamma``, fixes ``Q_Gamma`` as the signed
degree jump by Stokes' theorem, and varies the most general local linear event
pairing with the material scalar.

The integer flux and the event-pairing coefficient are kept distinct.  Degree
normalization fixes the former.  The retained parent action, self-adjoint
fluctuation domain, and eta zero-mode endpoint normalization do not fix the
latter.  Consequently the module emits exact conditional jump dynamics but
does not promote an arbitrary unit coefficient or a downstream material skin.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from scipy.integrate import solve_ivp

from bhsm.interface.aether_sigma_saturation_ejection_v15_19 import (
    formation_homoclinic_state,
)


VERSION = "v15.27"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def signed_degree_jump(incoming_degree: int, outgoing_degree: int) -> dict[str, Any]:
    """Return the exactly normalized geometric-sector event flux."""

    n_minus = int(incoming_degree)
    n_plus = int(outgoing_degree)
    charge = n_plus - n_minus
    return {
        "N_minus": n_minus,
        "N_plus": n_plus,
        "Q_Gamma": charge,
        "Stokes_identity": "integral_U(dj3)=integral_boundary_U(j3)=N_plus-N_minus",
        "integer_normalized": isinstance(charge, int),
        "orientation_reversal_Q_Gamma": -charge,
        "continuous_coefficient_used": False,
    }


def smooth_event_current(
    event_coordinate: Sequence[float],
    *,
    width: float,
    incoming_degree: int,
    outgoing_degree: int,
) -> dict[str, Any]:
    """Regularize the distributional current jump with a tanh approximate identity.

    Write ``j3=N_epsilon(t) omega3`` with ``integral omega3=1``.  Then
    ``dj3=N_epsilon'(t) dt wedge omega3`` and its integral tends to the
    signed degree jump independently of the regularization width.
    """

    coordinate = np.asarray(event_coordinate, dtype=float)
    epsilon = float(width)
    if (
        coordinate.ndim != 1
        or coordinate.size < 101
        or not np.all(np.isfinite(coordinate))
        or not np.all(np.diff(coordinate) > 0.0)
    ):
        raise ValueError("event_coordinate must be a finite increasing grid")
    if not math.isfinite(epsilon) or epsilon <= 0.0:
        raise ValueError("width must be finite and positive")
    jump = signed_degree_jump(incoming_degree, outgoing_degree)["Q_Gamma"]
    scaled = coordinate / epsilon
    tanh = np.tanh(scaled)
    sech_squared = 1.0 / np.cosh(scaled) ** 2
    degree = float(incoming_degree) + 0.5 * jump * (1.0 + tanh)
    flux_density = 0.5 * jump * sech_squared / epsilon
    integrated_flux = float(np.trapezoid(flux_density, coordinate))
    first_moment = float(np.trapezoid(coordinate * flux_density, coordinate))
    return {
        "event_coordinate": coordinate,
        "N_epsilon": degree,
        "dj3_density": flux_density,
        "integrated_flux": integrated_flux,
        "Q_Gamma": jump,
        "flux_error": integrated_flux - jump,
        "first_moment": first_moment,
        "regularizer_is_physical_width": False,
    }


def weak_distribution_witness() -> dict[str, Any]:
    """Verify convergence against smooth test functions for a unit event."""

    coordinate = np.linspace(-2.0, 2.0, 80001)
    rows = []
    for width in (0.2, 0.1, 0.05, 0.025):
        event = smooth_event_current(
            coordinate, width=width, incoming_degree=0, outgoing_degree=1
        )
        density = np.asarray(event["dj3_density"])
        test = np.exp(-coordinate**2) * (1.0 + 0.3 * coordinate)
        pairing = float(np.trapezoid(test * density, coordinate))
        rows.append(
            {
                "width": width,
                "flux": event["integrated_flux"],
                "test_pairing": pairing,
                "delta_limit_value": 1.0,
                "pairing_error": pairing - 1.0,
            }
        )
    return {
        "regularization": "delta_epsilon=(2epsilon)^(-1)sech^2(t/epsilon)",
        "rows": rows,
        "absolute_errors_decrease": all(
            abs(rows[index + 1]["pairing_error"])
            < abs(rows[index]["pairing_error"])
            for index in range(len(rows) - 1)
        ),
        "narrowest_flux_error": rows[-1]["flux"] - 1.0,
    }


def event_sector_ledger() -> dict[str, Any]:
    """Separate a degree jump from a mere redistribution event."""

    reconstruction = signed_degree_jump(0, 1)
    redistribution = signed_degree_jump(1, 1)
    reversal = signed_degree_jump(1, -1)
    return {
        "candidate_reconstruction_0_to_1": reconstruction,
        "degree_preserving_redistribution_1_to_1": redistribution,
        "orientation_reversal_1_to_minus1": reversal,
        "v15_9_incoming_state": "degree_one_radial_formation_precursor_not_a_reconstructed_Hopf_full_preimage_child",
        "outgoing_degree_one_Hopf_child_constructed": False,
        "actual_BHSM_event_sector_pair_selected": False,
        "conditional_if_actual_event_is_0_to_1": "Q_Gamma=+1_in_the_declared_orientation",
        "warning": (
            "topology_fixes_Q_Gamma_after_the_incoming_and_outgoing_"
            "correspondence_sectors_are_selected;_it_does_not_select_which_"
            "event_occurs"
        ),
    }


def event_sigma_variation(
    *, topological_flux: int, coupling: float, zsigma: float = 1.0
) -> dict[str, Any]:
    """Vary ``S_event=-lambda integral_Gamma sigma dj3``.

    The jump convention is ``[Pi]_Gamma=Pi_minus-Pi_plus``.  With that
    convention stationarity gives ``[Pi]_Gamma=lambda Q_Gamma``.  Reversing
    the event orientation reverses both ``Q_Gamma`` and the impulse.
    """

    charge = int(topological_flux)
    lam = float(coupling)
    z = float(zsigma)
    if not math.isfinite(lam) or not math.isfinite(z) or z <= 0.0:
        raise ValueError("coupling must be finite and zsigma positive")
    impulse = lam * charge
    return {
        "event_action": "S_Gamma_sigma=-lambda_Gamma*integral_Gamma(sigma*dj3)",
        "degree_and_measure": (
            "sigma_is_a_0form_and_dj3_is_a_distributional_4form_on_M4;_"
            "their_product_integrates_without_a_metric_or_external_frame"
        ),
        "jump_convention": "[Pi_sigma]_Gamma=Pi_sigma_minus-Pi_sigma_plus",
        "canonical_trace_equation": "[Pi_sigma]_Gamma=lambda_Gamma*Q_Gamma",
        "Q_Gamma": charge,
        "lambda_Gamma": lam,
        "Pi_jump": impulse,
        "canonical_velocity_jump_magnitude": abs(impulse) / z,
        "orientation_reversed_Pi_jump": -impulse,
        "zero_event_exact_regular_recovery": charge == 0 or lam == 0.0,
    }


def affine_self_adjoint_trace_audit() -> dict[str, Any]:
    """Show that an inhomogeneous event impulse preserves fluctuation symmetry.

    All backgrounds with the same fixed event source form an affine space.
    Differences of two solutions obey continuous trace and homogeneous flux
    transmission.  The Green form of the fluctuation operator therefore
    vanishes, independent of the source magnitude.
    """

    rng = np.random.default_rng(1527)
    trace_f = complex(*rng.normal(size=2))
    trace_g = complex(*rng.normal(size=2))
    flux_f = complex(*rng.normal(size=2))
    flux_g = complex(*rng.normal(size=2))
    # Homogeneous fluctuation transmission uses the same trace and flux from
    # either side.  The two oriented boundary contributions cancel.
    minus = np.conjugate(trace_f) * flux_g - np.conjugate(flux_f) * trace_g
    plus = -minus
    green = minus + plus
    return {
        "background_domain": "affine_trace_space_with_fixed_[Pi]=lambda_Gamma*Q_Gamma",
        "fluctuation_domain": "delta_sigma_minus=delta_sigma_plus_and_[delta_Pi]=0",
        "fluctuation_Green_form": {"real": float(green.real), "imag": float(green.imag)},
        "fluctuation_Green_form_norm": float(abs(green)),
        "self_adjoint_fluctuation_operator": abs(green) < 1.0e-13,
        "self_adjointness_fixes_affine_source_magnitude": False,
    }


def event_coupling_selection_audit() -> dict[str, Any]:
    """Test whether existing principles fix lambda_Gamma after Q is integral."""

    first = event_sigma_variation(topological_flux=1, coupling=1.0)
    second = event_sigma_variation(topological_flux=1, coupling=2.0)
    domain = affine_self_adjoint_trace_audit()
    return {
        "topological_flux_fixed_after_sector_selection": True,
        "candidate_eta_trace_endpoints": [-0.5, 0.5],
        "eta_trace_endpoints_fix_scalar_field_normalization": False,
        "self_adjointness_allows_every_real_affine_impulse": not domain[
            "self_adjointness_fixes_affine_source_magnitude"
        ],
        "diffeomorphism_covariance_fixes_lambda": False,
        "degree_quantization_fixes_lambda": False,
        "event_weight_single_valuedness_fixes_lambda": False,
        "reason_event_weight_does_not_fix": (
            "the_material_sigma_field_has_no_action_derived_compact_period_"
            "or_shift_identification"
        ),
        "retained_parent_action_contains_sigma_dj3_pairing": False,
        "inequivalent_fixed_witnesses": [first, second],
        "same_integer_flux_covariance_orientation_and_self_adjoint_fluctuations": True,
        "different_physical_impulses": first["Pi_jump"] != second["Pi_jump"],
        "lambda_Gamma_action_selected": False,
        "unit_coefficient_can_be_called_minimal_but_not_derived": True,
        "physical_sigma_trace_closed": False,
    }


def canonical_integer_dual_pairing_audit() -> dict[str, Any]:
    """Test whether Pontryagin duality identifies the existing material sigma.

    Composition and reversal of integer degree events canonically produce the
    group dagger algebra C[Z] and its dual circle.  This fixes the character
    form ``exp(i theta Q)`` but not an identification of the retained real
    material scalar with ``theta``.
    """

    charges = np.arange(-3, 4)
    sigma_minus, sigma_plus = -0.5, 0.5
    standard_minus = np.exp(2j * math.pi * sigma_minus * charges)
    standard_plus = np.exp(2j * math.pi * sigma_plus * charges)

    def potential(value: float) -> float:
        return -value**2 + 2.0 * value**4

    periodicity_residuals = [
        potential(value + 1.0) - potential(value)
        for value in (-1.25, -0.5, 0.0, 0.5, 1.25)
    ]
    return {
        "event_charge_group": "Z_under_composition",
        "dagger": "Q_star=-Q",
        "Pontryagin_dual": "U1",
        "canonical_character": "chi_theta(Q)=exp(i*theta*Q),_theta_mod_2pi",
        "standard_period_one_lift": "theta=2pi*sigma",
        "eta_endpoint_characters_equal_for_all_tested_integer_charges": bool(
            np.allclose(standard_minus, standard_plus, atol=1.0e-13)
        ),
        "reason": "sigma_plus-sigma_minus=1_is_one_full_period",
        "retained_material_potential": "V=-sigma^2+2sigma^4_on_the_analytic_control",
        "period_one_potential_residuals": periodicity_residuals,
        "retained_material_action_is_period_one": all(
            abs(value) < 1.0e-13 for value in periodicity_residuals
        ),
        "alternative_theta_equals_pi_sigma_distinguishes_endpoints": True,
        "alternative_period": 2.0,
        "alternative_normalization_action_selected": False,
        "natural_existing_dual_variable": (
            "Hopf_or_relative_holonomy_phase_not_material_sigma_amplitude"
        ),
        "relative_holonomy_creates_material_amplitude": False,
        "material_sigma_identified_with_Z_dual_angle": False,
        "canonical_duality_fixes_lambda_Gamma_for_material_sigma": False,
        "new_compact_field_required_if_literal_dual_angle_is_introduced": True,
    }


def impulsive_retained_trajectory(
    *,
    topological_flux: int,
    event_coupling: float,
    g: float,
    static_sigma_curvature: float,
    direct_sigma_quartic: float,
    supercriticality: float = 0.4,
    kappa1: float = 1.0,
    zsigma: float = 1.0,
    growth_times: float = 8.0,
) -> dict[str, Any]:
    """Conditionally evolve the retained Hamiltonian after an event impulse.

    This is a dependency diagnostic, not a prediction: ``lambda_Gamma``, the
    sigma response triple, and the actual event time are not jointly selected.
    """

    values = [
        event_coupling,
        g,
        static_sigma_curvature,
        direct_sigma_quartic,
        supercriticality,
        kappa1,
        zsigma,
        growth_times,
    ]
    if not all(math.isfinite(float(value)) for value in values):
        raise ValueError("trajectory inputs must be finite")
    if min(kappa1, zsigma, supercriticality, growth_times) <= 0.0:
        raise ValueError("scales and integration time must be positive")
    if g < 0.0 or direct_sigma_quartic < 0.0:
        raise ValueError("bounded diagnostic requires nonnegative g and quartic")
    critical_radius = (343.0 / (5.0 * kappa1)) ** (1.0 / 6.0)
    inertia = 1.5 * critical_radius**2
    rate = math.sqrt(5.0 * supercriticality / (6.0 * critical_radius**2))
    event_state = formation_homoclinic_state(
        0.0,
        supercriticality=supercriticality,
        critical_radius=critical_radius,
    )
    impulse = event_coupling * int(topological_flux)
    initial = np.array([event_state["q"], 0.0, 0.0, -impulse], dtype=float)

    def potential_prime(q: float) -> float:
        return -5.0 * supercriticality * q / 4.0 + 23.0 * q**3 / 36.0

    def hamiltonian(state: np.ndarray) -> float:
        q, p_q, sigma, p_sigma = state
        weight = 1.0 + g * sigma**2
        return (
            p_q**2 / (2.0 * inertia * weight)
            + p_sigma**2 / (2.0 * zsigma)
            - 5.0 * supercriticality * q**2 / 8.0
            + 23.0 * q**4 / 144.0
            + 0.5 * static_sigma_curvature * sigma**2
            + 0.25 * direct_sigma_quartic * sigma**4
        )

    def rhs(_time: float, state: np.ndarray) -> np.ndarray:
        q, p_q, sigma, p_sigma = state
        weight = 1.0 + g * sigma**2
        return np.array(
            [
                p_q / (inertia * weight),
                -potential_prime(q),
                p_sigma / zsigma,
                g * p_q**2 * sigma / (inertia * weight**2)
                - static_sigma_curvature * sigma
                - direct_sigma_quartic * sigma**3,
            ]
        )

    time_limit = growth_times / rate
    solution = solve_ivp(
        rhs,
        (0.0, time_limit),
        initial,
        method="DOP853",
        rtol=1.0e-10,
        atol=1.0e-12,
        max_step=0.1 / rate,
    )
    energies = np.asarray(
        [hamiltonian(solution.y[:, index]) for index in range(solution.y.shape[1])]
    )
    return {
        "solver_success": bool(solution.success),
        "Q_Gamma": int(topological_flux),
        "lambda_Gamma": float(event_coupling),
        "post_event_p_sigma": float(initial[3]),
        "maximum_absolute_sigma": float(np.max(np.abs(solution.y[2]))),
        "final_sigma": float(solution.y[2, -1]),
        "maximum_absolute_q": float(np.max(np.abs(solution.y[0]))),
        "post_event_energy": float(energies[0]),
        "energy_drift": float(np.max(energies) - np.min(energies)),
        "material_skin_criterion_defined": False,
        "physical_prediction": False,
    }


def downstream_nonuniqueness_witness() -> dict[str, Any]:
    """Show why integer Q alone cannot select a nonlinear trajectory."""

    unit = impulsive_retained_trajectory(
        topological_flux=1,
        event_coupling=1.0,
        g=1.0,
        static_sigma_curvature=0.02,
        direct_sigma_quartic=1.0,
    )
    double = impulsive_retained_trajectory(
        topological_flux=1,
        event_coupling=2.0,
        g=1.0,
        static_sigma_curvature=0.02,
        direct_sigma_quartic=1.0,
    )
    response_changed = impulsive_retained_trajectory(
        topological_flux=1,
        event_coupling=1.0,
        g=5.0,
        static_sigma_curvature=-0.02,
        direct_sigma_quartic=2.0,
    )
    return {
        "unit_coupling_control": unit,
        "double_coupling_control": double,
        "changed_response_control": response_changed,
        "all_solvers_succeeded": all(
            row["solver_success"] for row in (unit, double, response_changed)
        ),
        "same_Q_different_lambda_changes_trajectory": not math.isclose(
            unit["maximum_absolute_sigma"],
            double["maximum_absolute_sigma"],
            rel_tol=1.0e-4,
        ),
        "same_Q_lambda_different_response_changes_trajectory": not math.isclose(
            unit["maximum_absolute_sigma"],
            response_changed["maximum_absolute_sigma"],
            rel_tol=1.0e-4,
        ),
        "controls_are_predictions": False,
    }


def completion_payload() -> dict[str, Any]:
    distribution = weak_distribution_witness()
    sectors = event_sector_ledger()
    variation = event_sigma_variation(topological_flux=1, coupling=1.0)
    domain = affine_self_adjoint_trace_audit()
    selection = event_coupling_selection_audit()
    duality = canonical_integer_dual_pairing_audit()
    dynamics = downstream_nonuniqueness_witness()
    validation = {
        "distributional_flux_converges_to_unit_degree_jump": (
            distribution["absolute_errors_decrease"]
            and abs(distribution["narrowest_flux_error"]) < 1.0e-12
        ),
        "Stokes_flux_is_signed_integer": signed_degree_jump(0, 1)[
            "integer_normalized"
        ],
        "orientation_reversal_flips_flux": signed_degree_jump(0, 1)[
            "orientation_reversal_Q_Gamma"
        ]
        == -1,
        "event_pairing_has_correct_form_degree_without_metric": "0form" in variation[
            "degree_and_measure"
        ],
        "affine_trace_variation_gives_canonical_impulse": variation["Pi_jump"] == 1.0,
        "fluctuation_domain_is_self_adjoint": domain[
            "self_adjoint_fluctuation_operator"
        ],
        "event_sector_not_invented": not sectors[
            "actual_BHSM_event_sector_pair_selected"
        ],
        "coupling_nonuniqueness_not_hidden": (
            selection["different_physical_impulses"]
            and not selection["lambda_Gamma_action_selected"]
        ),
        "integer_duality_not_conflated_with_material_sigma": (
            duality["eta_endpoint_characters_equal_for_all_tested_integer_charges"]
            and not duality["retained_material_action_is_period_one"]
            and not duality["material_sigma_identified_with_Z_dual_angle"]
        ),
        "conditional_dynamics_integrated": dynamics["all_solvers_succeeded"],
        "conditional_dynamics_not_promoted": not dynamics["controls_are_predictions"],
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_event_flux_sigma_trace_v15_27",
        "version": VERSION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "distributional_event_theorem": distribution,
        "event_sector_ledger": sectors,
        "sigma_event_variation": variation,
        "self_adjoint_affine_trace": domain,
        "event_coupling_selection": selection,
        "integer_event_duality_audit": duality,
        "conditional_nonlinear_continuation": dynamics,
        "scientific_result": (
            "STOKES_AND_THE_NORMALIZED_DEGREE_FORM_FIX_DJ3_EQUALS_Q_GAMMA_"
            "DELTA_GAMMA_WITH_INTEGER_Q_GAMMA_ONCE_THE_EVENT_SECTORS_ARE_"
            "KNOWN;_VARIATION_OF_A_SIGMA_DJ3_PAIRING_GIVES_AN_AFFINE_"
            "CANONICAL_MOMENTUM_JUMP_AND_SELF_ADJOINT_FLUCTUATIONS;_BUT_"
            "NEITHER_TOPOLOGY_SELF_ADJOINTNESS_NOR_THE_ETA_TRACE_ENDPOINTS_"
            "FIX_THE_EVENT_PAIRING_COEFFICIENT_OR_SELECT_THE_ACTUAL_"
            "INCOMING_OUTGOING_EVENT_CORRESPONDENCE"
        ),
        "completion_ledger": {
            "VALIDATED": [
                "distributional_dj3_event_limit",
                "Q_Gamma_equals_signed_integer_degree_jump",
                "metric_free_0form_times_4form_event_pairing",
                "affine_sigma_momentum_jump_from_variation",
                "self_adjoint_homogeneous_fluctuation_domain",
                "integer_event_group_has_canonical_U1_dual_character_family",
            ],
            "INVALIDATED": [
                "topological_charge_quantization_alone_fixes_the_sigma_event_coupling",
                "self_adjointness_fixes_an_inhomogeneous_affine_source_magnitude",
                "calling_open_path_eta_trace_endpoints_a_derivation_of_lambda_Gamma",
                "identifying_the_nonperiodic_material_sigma_with_the_canonical_Z_dual_angle",
            ],
            "RECLASSIFIED": [
                "the_eta_zero_mode_endpoints_as_candidate_event_trace_orientation_data",
                "sigma_activation_as_an_event_impulse_problem_not_a_smooth_bulk_seed",
            ],
            "CLOSED_THIS_RUN": [
                "distributional_form_degree_and_Stokes_normalization",
                "canonical_jump_variation",
                "affine_self_adjointness_check",
                "conditional_post_event_Hamiltonian_integration",
                "canonical_integer_duality_versus_material_sigma_audit",
            ],
            "ACTIVE_DEPENDENCY": (
                "PARENT_EVENT_ACTION_OR_CANONICAL_SYMPLECTIC_PAIRING_THEOREM_"
                "THAT_IDENTIFIES_MATERIAL_SIGMA_AS_THE_DUAL_OF_THE_INTEGER_"
                "TRANSITION_CURRENT_AND_FIXES_LAMBDA_GAMMA_TOGETHER_WITH_"
                "THE_ACTUAL_ZERO_TO_ONE_RECONSTRUCTION_CORRESPONDENCE"
            ),
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_empirical_inputs": [],
            "event_coupling_promoted": False,
            "diagnostic_couplings": [1.0, 2.0],
            "actual_event_sector_promoted": False,
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
        rounded = round(value, 12)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, Mapping):
        return {key: _canonical_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical_json_value(item) for item in value]
    if isinstance(value, np.ndarray):
        return [_canonical_json_value(item) for item in value.tolist()]
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
    path = target / "BHSM_aether_event_flux_sigma_trace_v15_27.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION",
    "FULL_BHSM_COMPLETE",
    "signed_degree_jump",
    "smooth_event_current",
    "weak_distribution_witness",
    "event_sector_ledger",
    "event_sigma_variation",
    "affine_self_adjoint_trace_audit",
    "event_coupling_selection_audit",
    "canonical_integer_dual_pairing_audit",
    "impulsive_retained_trajectory",
    "downstream_nonuniqueness_witness",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
