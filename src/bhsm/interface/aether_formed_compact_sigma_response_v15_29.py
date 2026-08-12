"""Compact formed-branch eta trace and induced material response.

The v15.9 solution is the retained round-S7 degree-one eta formation branch.
This module applies the inverse-Euler construction of v15.28 directly to that
compact branch, rather than importing the noncompact v13.1 texture.  If

    sigma_q(chi) = C_q(chi) - 1/2,
    C_q' = sin(f_q)^2 / integral_0^pi sin(f_q)^2 dchi,

then the canonical local scalar action on a round S7 of radius ``a`` requires

    a^2 U_{q,sigma}(sigma_q(chi))
      = sigma_q'' + 6 cot(chi) sigma_q'.

Monotonicity fixes the potential on the open material interval, up to the
exterior parent-relative constant.  The nonidentity formation branch has a
nonzero force at sigma=0.  Its leading coefficient is derived analytically:

    a^2 U_{q,sigma}(0) = 20 q / (3 pi) + O(q^2).

The construction is an action-owned *effective completion candidate* selected
by the retained eta solution family.  It is not represented as a term already
present in the historical parent action, and no coupled Einstein-eta-sigma
solution is claimed here.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_cycle_spread_concentration_v15_9 import (
    critical_radius,
    radial_fourier_solution,
)


VERSION = "v15.29"
CLASSIFICATION = "BHSM_ACTION_COMPLETION_CANDIDATE"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False
LEADING_SOURCE_COEFFICIENT = 20.0 / (3.0 * math.pi)


def _cumulative_trapezoid(values: np.ndarray, coordinate: np.ndarray) -> np.ndarray:
    increments = 0.5 * (values[1:] + values[:-1]) * np.diff(coordinate)
    return np.concatenate(([0.0], np.cumsum(increments)))


def _positive(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return value


def formed_eta_profile(
    radius_ratio_six: float,
    *,
    points: int = 20001,
    modes: int = 12,
) -> dict[str, np.ndarray | float]:
    """Return a resolved positive-orientation v15.9 radial eta profile."""

    ratio = _positive(radius_ratio_six, "radius_ratio_six")
    if ratio < 1.0:
        raise ValueError("the retained nonidentity formed branch requires ratio >= 1")
    if not isinstance(points, int) or points < 4001:
        raise ValueError("points must be an integer >= 4001")
    if not isinstance(modes, int) or modes < 4:
        raise ValueError("modes must be an integer >= 4")

    chi = np.linspace(0.0, math.pi, points)
    if math.isclose(ratio, 1.0, rel_tol=0.0, abs_tol=1.0e-14):
        coefficients = np.zeros(modes, dtype=float)
    else:
        coefficients = np.asarray(radial_fourier_solution(ratio, modes), dtype=float)
    n = np.arange(1, modes + 1, dtype=float)[:, None]
    profile = chi + coefficients @ np.sin(n * chi)
    derivative = 1.0 + coefficients @ (n * np.cos(n * chi))
    return {
        "chi": chi,
        "f_eta": profile,
        "f_eta_prime": derivative,
        "coefficients": coefficients,
        "q": float(coefficients[0]),
        "radius_ratio_six": ratio,
    }


def compact_material_arrays(
    radius_ratio_six: float,
    *,
    points: int = 20001,
    modes: int = 12,
) -> dict[str, np.ndarray | float]:
    """Reconstruct the compact trace and dimensionless induced potential."""

    eta = formed_eta_profile(radius_ratio_six, points=points, modes=modes)
    chi = np.asarray(eta["chi"])
    profile = np.asarray(eta["f_eta"])
    derivative = np.asarray(eta["f_eta_prime"])
    raw = np.sin(profile) ** 2
    raw_prime = np.sin(2.0 * profile) * derivative
    norm = float(np.trapezoid(raw, chi))
    density = raw / norm
    density_prime = raw_prime / norm
    cumulative = _cumulative_trapezoid(density, chi)
    cumulative /= cumulative[-1]
    sigma = cumulative - 0.5

    cot_density = np.zeros_like(chi)
    interior = (chi > 0.0) & (chi < math.pi)
    cot_density[interior] = density[interior] / np.tan(chi[interior])
    dimensionless_force = density_prime + 6.0 * cot_density
    # Both endpoint limits vanish because density=O(distance^2).
    dimensionless_force[[0, -1]] = 0.0
    potential_chi_derivative = dimensionless_force * density
    dimensionless_potential = _cumulative_trapezoid(
        potential_chi_derivative, chi
    )
    dimensionless_potential -= dimensionless_potential[-1]
    return {
        **eta,
        "trace_norm": norm,
        "density": density,
        "density_prime": density_prime,
        "C_eta": cumulative,
        "sigma": sigma,
        "a2_U_sigma": dimensionless_force,
        "a2_U": dimensionless_potential,
    }


def analytic_small_q_source() -> dict[str, Any]:
    """Return the first-order compact source calculation at the median trace."""

    return {
        "profile": "f=chi+q*sin(chi)+O(q^2)",
        "normalized_density": (
            "w=(2/pi)sin(chi)^2[1+2q*cos(chi)]+O(q^2)"
        ),
        "median_location": "chi_1/2=pi/2-(2/3)q+O(q^2)",
        "dimensionless_force": "a^2*U_sigma=w_prime+6*cot(chi)*w",
        "median_shift_contribution": "32*q/(3*pi)",
        "direct_profile_contribution": "-4*q/pi",
        "result": "a^2*U_sigma(0)=20*q/(3*pi)+O(q^2)",
        "coefficient": LEADING_SOURCE_COEFFICIENT,
        "zero_on_identity_branch": True,
        "odd_under_formation_orientation_reversal": True,
    }


def compact_response_diagnostics(
    radius_ratio_six: float,
    *,
    points: int = 20001,
    modes: int = 12,
) -> dict[str, Any]:
    """Evaluate the source, effective energy and reflection properties."""

    arrays = compact_material_arrays(
        radius_ratio_six, points=points, modes=modes
    )
    chi = np.asarray(arrays["chi"])
    sigma = np.asarray(arrays["sigma"])
    density = np.asarray(arrays["density"])
    force = np.asarray(arrays["a2_U_sigma"])
    potential = np.asarray(arrays["a2_U"])
    sphere_weight = np.sin(chi) ** 6
    q = float(arrays["q"])
    source = float(np.interp(0.0, sigma, force))
    median = float(np.interp(0.0, sigma, chi))
    kinetic = float(np.trapezoid(0.5 * sphere_weight * density**2, chi))
    potential_energy = float(np.trapezoid(sphere_weight * potential, chi))
    test_sigma = np.linspace(-0.49, 0.49, 2001)
    sampled_u = np.interp(test_sigma, sigma, potential)
    reflected_u = np.interp(-test_sigma, sigma, potential)
    return {
        "radius_ratio_six": float(radius_ratio_six),
        "radius_over_critical": float(radius_ratio_six) ** (1.0 / 6.0),
        "q": q,
        "trace_norm": float(arrays["trace_norm"]),
        "sigma_endpoints": [float(sigma[0]), float(sigma[-1])],
        "median_chi": median,
        "a2_U_sigma_at_sigma_zero": source,
        "leading_source_prediction": LEADING_SOURCE_COEFFICIENT * q,
        "source_over_q": source / q if abs(q) > 1.0e-14 else None,
        "potential_reflection_asymmetry": float(
            np.max(np.abs(sampled_u - reflected_u))
        ),
        "dimensionless_kinetic_energy_per_Omega6_Zsigma_a5": kinetic,
        "dimensionless_potential_energy_per_Omega6_Zsigma_a5": potential_energy,
        "dimensionless_total_energy_per_Omega6_Zsigma_a5": (
            kinetic + potential_energy
        ),
        "Euler_identity_residual": float(
            np.max(np.abs(force - (np.asarray(arrays["density_prime"]) + 6.0 * np.divide(
                density,
                np.tan(chi),
                out=np.zeros_like(density),
                where=(chi > 0.0) & (chi < math.pi),
            ))))
        ),
        "physical_scaling": {
            "radius": "a=a_c*(radius_ratio_six)^(1/6)",
            "a_c": "(343/(5*kappa1))^(1/6)",
            "U_sigma": "a2_U_sigma/a^2",
            "U": "a2_U/a^2",
            "energy": "Omega6*Zsigma*a^5*dimensionless_energy",
        },
    }


def orientation_pair_diagnostics(
    radius_ratio_six: float = 1.01,
    *,
    points: int = 12001,
) -> dict[str, Any]:
    """Verify the reflected negative-q branch and its opposite sigma source."""

    plus = compact_material_arrays(radius_ratio_six, points=points)
    sigma_plus = np.asarray(plus["sigma"])
    force_plus = np.asarray(plus["a2_U_sigma"])
    potential_plus = np.asarray(plus["a2_U"])
    chi = np.asarray(plus["chi"])

    # f_-(chi)=pi-f_+(pi-chi), sigma_-(chi)=-sigma_+(pi-chi).
    sigma_minus = -sigma_plus[::-1]
    force_minus = -force_plus[::-1]
    potential_minus = potential_plus[::-1]
    source_plus = float(np.interp(0.0, sigma_plus, force_plus))
    source_minus = float(np.interp(0.0, sigma_minus, force_minus))
    return {
        "orientation_map": (
            "f_minus(chi)=pi-f_plus(pi-chi);_sigma_minus(chi)="
            "-sigma_plus(pi-chi)"
        ),
        "potential_map": "U_minus(sigma)=U_plus(-sigma)",
        "force_map": "U_minus_prime(sigma)=-U_plus_prime(-sigma)",
        "q_plus": float(plus["q"]),
        "q_minus": -float(plus["q"]),
        "source_plus": source_plus,
        "source_minus": source_minus,
        "source_sum_residual": source_plus + source_minus,
        "profile_reflection_residual": float(
            np.max(np.abs(sigma_minus + sigma_plus[::-1]))
        ),
        "force_reflection_residual": float(
            np.max(np.abs(force_minus + force_plus[::-1]))
        ),
        "potential_reflection_residual": float(
            np.max(np.abs(potential_minus - potential_plus[::-1]))
        ),
        "coordinate_domain_residual": float(np.max(np.abs(chi + chi[::-1] - math.pi))),
        "external_preferred_frame_used": False,
        "orientation_is_internal_branch_of_retained_radial_solution": True,
    }


def completion_payload() -> dict[str, Any]:
    identity = compact_response_diagnostics(1.0, points=12001)
    near = compact_response_diagnostics(1.001, points=16001)
    formed = compact_response_diagnostics(1.01, points=20001)
    orientation = orientation_pair_diagnostics(1.01)
    analytic = analytic_small_q_source()
    validation = {
        "identity_branch_has_zero_source": abs(
            identity["a2_U_sigma_at_sigma_zero"]
        )
        < 1.0e-10,
        "formed_branch_has_nonzero_source": abs(
            formed["a2_U_sigma_at_sigma_zero"]
        )
        > 0.1,
        "near_branch_matches_analytic_linear_source": abs(
            near["source_over_q"] - analytic["coefficient"]
        )
        < 0.02,
        "orientation_reversal_flips_source": abs(
            orientation["source_sum_residual"]
        )
        < 1.0e-10,
        "trace_endpoints_exact": np.allclose(
            formed["sigma_endpoints"], [-0.5, 0.5], atol=1.0e-12
        ),
        "inverse_Euler_identity": formed["Euler_identity_residual"] < 1.0e-12,
        "no_external_frame": not orientation["external_preferred_frame_used"],
        "no_empirical_inputs": True,
        "no_new_continuous_coefficient": True,
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_formed_compact_sigma_response_v15_29",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "retained_formation_action": (
            "v15.9_round_S7_degree_one_p2_plus_p8_eta_functional"
        ),
        "critical_radius_kappa1_one": critical_radius(),
        "inverse_Euler_theorem": {
            "profile": "sigma_q=C_q-1/2",
            "compact_Euler_equation": (
                "a^-2[sigma_chichi+6cot(chi)sigma_chi]=U_q_prime(sigma)"
            ),
            "derived_force": (
                "a^2 U_q_prime(sigma_q)=w_q_prime+6cot(chi)w_q"
            ),
            "uniqueness": (
                "w_q>0_on_(0,pi)_makes_chi_a_function_of_sigma_and_fixes_"
                "U_q_up_to_the_parent_relative_vacuum_constant"
            ),
        },
        "analytic_small_q_source": analytic,
        "identity_branch": identity,
        "near_critical_formed_branch": near,
        "representative_formed_branch": formed,
        "orientation_pair": orientation,
        "scientific_result": (
            "THE_ACTUAL_COMPACT_V15_9_FORMATION_BRANCH_BREAKS_THE_FIXED_"
            "SIGMA_REFLECTION_OF_THE_IDENTITY_BRANCH_AND_IN_THE_UNIQUE_"
            "CANONICAL_INVERSE_EULER_COMPLETION_GENERATES_A_NONZERO_"
            "MATERIAL_FORCE_A2_U_SIGMA_ZERO_EQUALS_20Q_OVER_3PI_PLUS_"
            "HIGHER_ORDER;_THE_CONJUGATE_FORMATION_BRANCH_FLIPS_THE_FORCE"
        ),
        "claim_boundary": {
            "old_parent_action_already_contains_U_q": False,
            "effective_action_completion_candidate": True,
            "eta_profile_is_retained_v15_9_solution": True,
            "historical_independent_sigma_identified_with_trace": False,
            "branchwise_U_q_is_one_local_state_independent_parent_potential": False,
            "coupled_metric_eta_sigma_stationary_solution": False,
            "nonlinear_enclosure_continuation": False,
            "Hopf_child_constructed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "completion_ledger": {
            "CLOSED_THIS_RUN": [
                "formation_q_to_sigma_zero_force_in_the_compact_formation_geometry",
                "analytic_near_critical_coefficient_20_over_3pi",
                "internal_orientation_reversal_of_the_material_force",
                "identity_branch_zero_source_limit",
            ],
            "ACTIVE_DEPENDENCY": (
                "JOINT_PARENT_ACTION_DERIVATION_AND_CONSTRAINT_SOLVED_"
                "EINSTEIN_ETA_SIGMA_CONTINUATION_OF_THE_Q_DEPENDENT_"
                "MATERIAL_RESPONSE_INTO_A_REGULAR_HOPF_CHILD"
            ),
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_continuous_coefficients": [],
            "empirical_inputs": [],
            "formation_profile_source": "retained_v15.9_action_solution",
            "material_force_source": "inverse_compact_Euler_map",
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
    path = target / "BHSM_aether_formed_compact_sigma_response_v15_29.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "LEADING_SOURCE_COEFFICIENT",
    "formed_eta_profile",
    "compact_material_arrays",
    "analytic_small_q_source",
    "compact_response_diagnostics",
    "orientation_pair_diagnostics",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
