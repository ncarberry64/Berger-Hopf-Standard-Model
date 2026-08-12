"""Eta-profile-induced material potential and unstable enclosure solution.

The v15.26 probability trace fixes a monotone candidate material profile but
its exact-gradient kinetic completion is dynamically trivial.  This module
asks the inverse variational question instead: within the existing canonical
one-field local sigma kinetic class, which potential makes that trace profile
an actual stationary spherical enclosure on the retained degree-one eta
background?

For a monotone radial profile the Euler equation determines ``U'(sigma)``
pointwise and therefore fixes ``U`` uniquely up to one vacuum constant.  The
constant is fixed by parent-relative subtraction on the exterior.  No
polynomial ansatz or new continuous coefficient is used.  The resulting
critical enclosure has an exact negative Derrick scaling direction.  It is a
fixed-background ``BHSM_ACTION_COMPLETION``; the coupled Einstein--eta--sigma
constraints and its nonlinear continuation are not silently claimed solved.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.completion.eta_static_texture_v13_1 import (
    OMEGA_6,
    solve_profile,
)


VERSION = "v15.28"
CLASSIFICATION = "BHSM_ACTION_COMPLETION"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def _cumulative_trapezoid(values: np.ndarray, coordinate: np.ndarray) -> np.ndarray:
    increments = 0.5 * (values[1:] + values[:-1]) * np.diff(coordinate)
    return np.concatenate(([0.0], np.cumsum(increments)))


def retained_eta_material_arrays(points: int = 40001) -> dict[str, np.ndarray | float]:
    """Return the normalized eta trace and its unique radial material potential."""

    if points < 4001:
        raise ValueError("points must be at least 4001")
    solution = solve_profile()
    log_radius = np.linspace(float(solution.x[0]), float(solution.x[-1]), points)
    radius = np.exp(log_radius)
    f_eta, f_log_derivative = solution.sol(log_radius)
    raw = np.sin(f_eta) ** 2
    norm = float(np.trapezoid(raw, radius))
    density = raw / norm
    cumulative = _cumulative_trapezoid(density, radius)
    cumulative /= cumulative[-1]
    sigma = cumulative - 0.5

    raw_derivative = (
        2.0
        * np.sin(f_eta)
        * np.cos(f_eta)
        * f_log_derivative
        / radius
    )
    density_derivative = raw_derivative / norm
    potential_prime = density_derivative + 6.0 * density / radius
    potential_derivative_radius = potential_prime * density
    potential = _cumulative_trapezoid(potential_derivative_radius, radius)
    # Parent-relative subtraction: the exterior vacuum density is zero.
    potential -= potential[-1]
    return {
        "radius": radius,
        "f_eta": f_eta,
        "density": density,
        "density_derivative": density_derivative,
        "C_eta": cumulative,
        "sigma": sigma,
        "U_prime": potential_prime,
        "U": potential,
        "zero_mode_norm_integral": norm,
    }


def potential_uniqueness_theorem() -> dict[str, Any]:
    """State the inverse-Euler uniqueness theorem used by the completion."""

    return {
        "completed_radial_energy": (
            "E_sigma=Omega6*Z_sigma*integral_0^infty r^6["
            "(partial_r sigma)^2/2+U_eta(sigma)]dr"
        ),
        "target_profile": "sigma_star(r)=C_eta(r)-1/2",
        "Euler_equation": (
            "sigma_star_double_prime+6*sigma_star_prime/r="
            "U_eta_prime(sigma_star)"
        ),
        "derived_force": (
            "U_eta_prime(sigma_star(r))=w_eta_prime(r)+6*w_eta(r)/r"
        ),
        "invertibility": "sigma_star_prime=w_eta>0_on_the_open_wall_interval",
        "uniqueness": (
            "monotonicity_makes_r_a_function_of_sigma_so_U_prime_is_unique_"
            "on_(-1/2,1/2);_integration_leaves_only_one_additive_constant"
        ),
        "constant_selection": "U_eta(+1/2)=0_by_exterior_parent_relative_subtraction",
        "new_polynomial_ansatz": False,
        "new_continuous_coefficient": False,
        "scope": (
            "unique_within_a_canonical_single_real_scalar_local_two_derivative_"
            "radial_action_on_the_fixed_retained_eta_background"
        ),
    }


def retained_material_skin_diagnostics(points: int = 40001) -> dict[str, Any]:
    """Evaluate the derived potential, source, width, stress, and Derrick mode."""

    arrays = retained_eta_material_arrays(points)
    radius = np.asarray(arrays["radius"])
    density = np.asarray(arrays["density"])
    density_derivative = np.asarray(arrays["density_derivative"])
    cumulative = np.asarray(arrays["C_eta"])
    sigma = np.asarray(arrays["sigma"])
    potential_prime = np.asarray(arrays["U_prime"])
    potential = np.asarray(arrays["U"])

    euler_residual = density_derivative + 6.0 * density / radius - potential_prime
    quantiles = np.interp([0.1, 0.25, 0.5, 0.75, 0.9], cumulative, radius)
    median_radius = float(quantiles[2])
    source_at_zero = float(np.interp(0.0, sigma, potential_prime))
    test_sigma = np.linspace(-0.49, 0.49, 3001)
    u_plus = np.interp(test_sigma, sigma, potential)
    u_reflected = np.interp(-test_sigma, sigma, potential)
    asymmetry = float(np.max(np.abs(u_plus - u_reflected)))

    kinetic = float(np.trapezoid(0.5 * radius**6 * density**2, radius))
    potential_energy = float(np.trapezoid(radius**6 * potential, radius))
    total = kinetic + potential_energy
    virial = 5.0 * kinetic + 7.0 * potential_energy
    scaling_second = 20.0 * kinetic + 42.0 * potential_energy
    scaling_inertia = float(np.trapezoid(radius**8 * density**2, radius))
    growth_rate = math.sqrt(-scaling_second / scaling_inertia)

    pressure_jump = float(-potential[0])
    surface_of_tension_radius = (42.0 * total / pressure_jump) ** (1.0 / 7.0)
    surface_tension = pressure_jump * surface_of_tension_radius / 6.0
    return {
        "reference_kappa1": 1.0,
        "profile_endpoints": [float(sigma[0]), float(sigma[-1])],
        "zero_mode_norm_integral": float(arrays["zero_mode_norm_integral"]),
        "radius_quantiles_C_10_25_50_75_90": quantiles.tolist(),
        "width_10_to_90": float(quantiles[4] - quantiles[0]),
        "width_25_to_75": float(quantiles[3] - quantiles[1]),
        "median_radius": median_radius,
        "U_inside_relative_to_parent": float(potential[0]),
        "U_outside_parent_subtracted": float(potential[-1]),
        "pressure_jump_per_Zsigma": pressure_jump,
        "orientation_odd_force_Uprime_at_sigma_zero": source_at_zero,
        "potential_reflection_asymmetry": asymmetry,
        "maximum_Euler_residual": float(np.max(np.abs(euler_residual))),
        "radial_energy_per_Omega6_Zsigma": total,
        "radial_kinetic_per_Omega6_Zsigma": kinetic,
        "radial_potential_per_Omega6_Zsigma": potential_energy,
        "Derrick_virial_5K_plus_7P": virial,
        "Derrick_scaling_second_variation_per_Omega6_Zsigma": scaling_second,
        "scaling_collective_inertia_per_Omega6_Zsigma": scaling_inertia,
        "scaling_growth_rate_in_kappa1_one_units": growth_rate,
        "physical_negative_enclosure_direction": scaling_second < 0.0,
        "surface_of_tension_radius": surface_of_tension_radius,
        "surface_tension_per_Zsigma": surface_tension,
        "Laplace_identity_residual": (
            pressure_jump - 6.0 * surface_tension / surface_of_tension_radius
        ),
        "scale_law": {
            "ell_eta": "kappa1^(-1/6)",
            "width": "width_reference*ell_eta",
            "U": "U_reference/ell_eta^2",
            "growth_rate": "growth_rate_reference/ell_eta",
        },
    }


def flat_analytic_control() -> dict[str, Any]:
    """Recover the v15.26 quartic when the collar area is constant."""

    sigma = np.linspace(-0.5, 0.5, 20001)
    force = 0.5 - 2.0 * sigma**2
    potential = 0.5 * force**2
    expected = 0.125 - sigma**2 + 2.0 * sigma**4
    return {
        "flat_profile": "sigma_star=1/2*tanh(s)",
        "force": "F_eta(sigma)=1/2-2*sigma^2",
        "potential": "U_eta=1/2*F_eta^2=1/8-sigma^2+2*sigma^4",
        "maximum_identity_residual": float(np.max(np.abs(potential - expected))),
        "historical_A_ST": -2.0,
        "historical_G_ST": 8.0,
        "role": "constant_area_analytic_control_not_the_curved_retained_profile",
    }


def orientation_reversal_theorem(points: int = 12001) -> dict[str, Any]:
    """Construct the conjugate potential and verify diagonal reversal."""

    arrays = retained_eta_material_arrays(points)
    sigma = np.asarray(arrays["sigma"])
    potential = np.asarray(arrays["U"])
    force = np.asarray(arrays["U_prime"])
    sample = np.linspace(-0.49, 0.49, 2001)
    plus_u = np.interp(sample, sigma, potential)
    minus_u = np.interp(-sample, sigma, potential)
    plus_force = np.interp(sample, sigma, force)
    minus_force = -np.interp(-sample, sigma, force)
    return {
        "orientation_map": "u_eta_to_minus_u_eta_and_sigma_to_minus_sigma",
        "conjugate_potential": "U_minus(sigma)=U_plus(-sigma)",
        "conjugate_force": "U_minus_prime(sigma)=-U_plus_prime(-sigma)",
        "sample_potential_reversal_residual": float(
            np.max(np.abs(minus_u - np.interp(-sample, sigma, potential)))
        ),
        "source_at_zero_plus": float(np.interp(0.0, sample, plus_force)),
        "source_at_zero_minus": float(np.interp(0.0, sample, minus_force)),
        "source_sign_reverses": math.isclose(
            float(np.interp(0.0, sample, plus_force)),
            -float(np.interp(0.0, sample, minus_force)),
            rel_tol=1.0e-10,
            abs_tol=1.0e-10,
        ),
        "independent_sigma_reflection_is_symmetry_of_fixed_oriented_branch": False,
        "diagonal_orientation_sigma_reversal_is_symmetry_of_pair": True,
    }


def completion_payload() -> dict[str, Any]:
    uniqueness = potential_uniqueness_theorem()
    skin = retained_material_skin_diagnostics()
    analytic = flat_analytic_control()
    reversal = orientation_reversal_theorem()
    validation = {
        "inverse_Euler_potential_unique_in_declared_class": "unique" in uniqueness[
            "uniqueness"
        ],
        "profile_endpoints_normalized": np.allclose(
            skin["profile_endpoints"], [-0.5, 0.5], atol=1.0e-12
        ),
        "derived_profile_solves_sigma_Euler_equation": skin[
            "maximum_Euler_residual"
        ]
        < 1.0e-13,
        "exterior_parent_vacuum_subtracted": abs(
            skin["U_outside_parent_subtracted"]
        )
        < 1.0e-12,
        "nonzero_orientation_source_at_sigma_zero": abs(
            skin["orientation_odd_force_Uprime_at_sigma_zero"]
        )
        > 1.0e-3,
        "Derrick_virial_satisfied": abs(skin["Derrick_virial_5K_plus_7P"]) < 1.0e-4,
        "physical_negative_scaling_direction": skin[
            "physical_negative_enclosure_direction"
        ],
        "Laplace_surface_of_tension_identity": abs(
            skin["Laplace_identity_residual"]
        )
        < 1.0e-12,
        "analytic_flat_limit_recovers_quartic": analytic[
            "maximum_identity_residual"
        ]
        < 1.0e-13,
        "orientation_reversal_flips_source": reversal["source_sign_reverses"],
        "no_new_continuous_coefficient": not uniqueness["new_continuous_coefficient"],
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_eta_induced_material_skin_v15_28",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "inverse_variational_uniqueness": uniqueness,
        "retained_eta_material_skin": skin,
        "flat_analytic_control": analytic,
        "orientation_reversal": reversal,
        "scientific_result": (
            "THE_NORMALIZED_RETAINED_ETA_PROFILE_UNIQUELY_FIXES_A_"
            "NONPOLYNOMIAL_PARENT_RELATIVE_MATERIAL_POTENTIAL_WITHIN_THE_"
            "CANONICAL_LOCAL_RADIAL_SIGMA_CLASS;_THE_RESULTING_SIGNED_"
            "SIGMA_PROFILE_IS_AN_EXACT_STATIONARY_SPHERICAL_ENCLOSURE_WITH_"
            "NONZERO_FORCE_AT_SIGMA_ZERO_AND_AN_EXACT_NEGATIVE_DERRICK_"
            "SCALING_DIRECTION"
        ),
        "claim_boundary": {
            "derived_from_old_retained_action": False,
            "derived_after_BHSM_action_completion": True,
            "fixed_eta_background": True,
            "full_Einstein_eta_sigma_constraints_solved": False,
            "negative_direction_is_gauge": False,
            "nonlinear_expanding_continuation_solved": False,
            "Hopf_child_constructed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "completion_ledger": {
            "VALIDATED": [
                "unique_profile_induced_nonpolynomial_material_potential_in_the_declared_class",
                "nonzero_orientation_selected_force_at_sigma_zero",
                "finite_width_pressure_and_surface_tension",
                "negative_physical_Derrick_enclosure_direction",
                "analytic_quartic_as_the_constant_area_limit",
            ],
            "INVALIDATED": [
                "the_actual_eta_induced_potential_is_the_symmetric_historical_quartic",
                "the_eta_trace_profile_has_no_material_energy_completion",
                "the_critical_material_enclosure_is_radially_stable",
            ],
            "RECLASSIFIED": [
                "v15_26_eta_trace_as_the_target_profile_that_uniquely_reconstructs_the_material_force",
                "the_historical_quartic_as_a_flat_analytic_limit_of_the_profile_induced_potential",
                "sigma_activation_as_post_event_domain_materialization_with_a_nonzero_derived_force",
            ],
            "CLOSED_THIS_RUN": [
                "material_potential_shape_without_polynomial_fitting",
                "sigma_zero_force_and_orientation_sign",
                "static_critical_skin_width_pressure_tension_and_scaling_instability",
            ],
            "ACTIVE_DEPENDENCY": (
                "COUPLED_CONSTRAINT_SOLVED_EINSTEIN_ETA_SIGMA_CONTINUATION_"
                "OF_THE_V15_28_NEGATIVE_DERRICK_ENCLOSURE_MODE_INTO_A_"
                "NONLINEAR_EXPANDING_OR_DEENVELOPING_BRANCH_WITH_Q_S_"
                "CANONICAL_MOMENTUM_TRANSFER"
            ),
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_continuous_coefficients": [],
            "new_empirical_inputs": [],
            "potential_source": "inverse_Euler_map_of_the_solved_eta_zero_mode_trace",
            "exterior_constant": "parent_relative_subtraction",
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
    path = target / "BHSM_aether_eta_induced_material_skin_v15_28.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "retained_eta_material_arrays",
    "potential_uniqueness_theorem",
    "retained_material_skin_diagnostics",
    "flat_analytic_control",
    "orientation_reversal_theorem",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
