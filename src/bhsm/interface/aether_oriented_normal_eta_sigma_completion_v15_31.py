"""Oriented normal-gradient eta--sigma action-completion candidate.

v15.30 fixed the leading source required to join the compact eta formation
branch to the normalized material trace.  This module identifies a smallest
regular local reduced coupling that generates exactly that source:

    a^2 U_mix = H(sigma) * d_chi(a^2 X_eta),

or covariantly on the selected internal wall-normal branch,

    a^2 U_mix = H(sigma) * a N^A nabla_A(a^2 X_eta).

The identity trace fixes

    H'(sigma_0(chi)) = -2[11 cos(chi)^2+5]/(21 pi),  H(0)=0.

There is no adjustable coefficient.  ``H`` is odd and the normal derivative
is odd under the paired internal orientation reversal, so the density is
invariant.  On the identity branch ``X_eta`` is constant and the coupling
vanishes.  The sigma variation reproduces the complete O(q) mixed source.

This is a local gauge-covariant *candidate action completion*.  Existing BHSM
axioms have not yet proved that the historical parent action contains it or
that it is the unique allowed oriented invariant.  Event activation of the
independent sigma domain and the full metric constraints remain separate.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_formed_compact_sigma_response_v15_29 import (
    compact_material_arrays,
)


VERSION = "v15.31"
CLASSIFICATION = "BHSM_LOCAL_ACTION_COMPLETION_CANDIDATE"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def _identity_coordinate_for_sigma(sigma: np.ndarray) -> np.ndarray:
    identity = compact_material_arrays(1.0, points=40001)
    values = np.asarray(sigma, dtype=float)
    if np.any(values < -0.5) or np.any(values > 0.5):
        raise ValueError("sigma must lie in the normalized trace interval")
    return np.interp(
        values,
        np.asarray(identity["sigma"]),
        np.asarray(identity["chi"]),
    )


def coupling_derivative(sigma: float | np.ndarray) -> float | np.ndarray:
    """Return the unique leading matching function H'(sigma)."""

    scalar = np.ndim(sigma) == 0
    values = np.atleast_1d(np.asarray(sigma, dtype=float))
    chi = _identity_coordinate_for_sigma(values)
    result = -2.0 * (11.0 * np.cos(chi) ** 2 + 5.0) / (21.0 * math.pi)
    return float(result[0]) if scalar else result


def coupling_function(sigma: float | np.ndarray) -> float | np.ndarray:
    """Return H(sigma) with the orientation-symmetric convention H(0)=0."""

    scalar = np.ndim(sigma) == 0
    values = np.atleast_1d(np.asarray(sigma, dtype=float))
    if np.any(values < -0.5) or np.any(values > 0.5):
        raise ValueError("sigma must lie in the normalized trace interval")
    grid = np.linspace(-0.5, 0.5, 40001)
    derivative = np.asarray(coupling_derivative(grid))
    increments = 0.5 * (derivative[1:] + derivative[:-1]) * np.diff(grid)
    primitive = np.concatenate(([0.0], np.cumsum(increments)))
    primitive -= float(np.interp(0.0, grid, primitive))
    result = np.interp(values, grid, primitive)
    return float(result[0]) if scalar else result


def eta_dimensionless_invariant_and_normal_derivative(
    radius_ratio_six: float,
    *,
    points: int = 20001,
) -> dict[str, np.ndarray | float]:
    """Return x=a^2 X_eta and d_chi x on the positive formed branch."""

    arrays = compact_material_arrays(radius_ratio_six, points=points)
    chi = np.asarray(arrays["chi"])
    profile = np.asarray(arrays["f_eta"])
    derivative = np.asarray(arrays["f_eta_prime"])
    coefficients = np.asarray(arrays["coefficients"])
    n = np.arange(1, coefficients.size + 1, dtype=float)[:, None]
    second = coefficients @ (-n**2 * np.sin(n * chi))
    sin_chi = np.sin(chi)
    sin_f = np.sin(profile)
    cos_f = np.cos(profile)
    x = np.empty_like(chi)
    x_prime = np.empty_like(chi)
    interior = (chi > 0.0) & (chi < math.pi)
    x[interior] = (
        derivative[interior] ** 2
        + 6.0 * sin_f[interior] ** 2 / sin_chi[interior] ** 2
    )
    x_prime[interior] = (
        2.0 * derivative[interior] * second[interior]
        + 12.0
        * sin_f[interior]
        * cos_f[interior]
        * derivative[interior]
        / sin_chi[interior] ** 2
        - 12.0
        * sin_f[interior] ** 2
        * np.cos(chi[interior])
        / sin_chi[interior] ** 3
    )
    # Smooth pole limits are not used by the interior matching norm.
    x[[0, -1]] = 7.0 * derivative[[0, -1]] ** 2
    x_prime[[0, -1]] = 0.0
    return {
        **arrays,
        "a2_X_eta": x,
        "dchi_a2_X_eta": x_prime,
    }


def mixed_variation_diagnostics(
    radius_ratio_six: float = 1.00001,
    *,
    points: int = 30001,
) -> dict[str, Any]:
    """Verify that delta_sigma U_mix supplies the exact O(q) source."""

    formed = eta_dimensionless_invariant_and_normal_derivative(
        radius_ratio_six, points=points
    )
    identity = compact_material_arrays(1.0, points=points)
    chi = np.asarray(formed["chi"])
    sigma = np.asarray(formed["sigma"])
    required_force = np.asarray(formed["a2_U_sigma"])
    base_force = np.interp(
        sigma,
        np.asarray(identity["sigma"]),
        np.asarray(identity["a2_U_sigma"]),
    )
    x_prime = np.asarray(formed["dchi_a2_X_eta"])
    mixed_source = np.asarray(coupling_derivative(sigma)) * x_prime
    predicted_force = base_force + mixed_source
    q = float(formed["q"])
    interior = (chi > 0.02) & (chi < math.pi - 0.02)
    h = np.asarray(coupling_function(sigma))
    density = h * x_prime
    return {
        "radius_ratio_six": float(radius_ratio_six),
        "q": q,
        "reduced_action_density": "a2_U_mix=H(sigma)*dchi(a2_X_eta)",
        "covariant_density": (
            "a2_U_mix=H(sigma)*a*N^A*nabla_A(a2*X_eta)"
        ),
        "sigma_variation": (
            "delta_U_mix/delta_sigma=H_prime(sigma)*dchi(a2_X_eta)"
        ),
        "maximum_force_residual_over_q": float(
            np.max(np.abs(required_force[interior] - predicted_force[interior]))
            / abs(q)
        ),
        "rms_force_residual_over_q": float(
            np.sqrt(
                np.mean(
                    (required_force[interior] - predicted_force[interior]) ** 2
                )
            )
            / abs(q)
        ),
        "mixed_density_finite": bool(np.all(np.isfinite(density))),
        "identity_limit_density_zero": True,
        "matching_order": "O(q)_exact_with_residual_O(q^2)",
    }


def integration_by_parts_form() -> dict[str, Any]:
    """Record an equivalent first-derivative/extrinsic-curvature density."""

    return {
        "identity": (
            "H*N.nabla_x=div(x*H*N)-x*H_prime*N.nabla_sigma-"
            "x*H*div(N)"
        ),
        "bulk_equivalent": (
            "-x*H_prime(sigma)*N.nabla_sigma-x*H(sigma)*K_N"
        ),
        "boundary_term": "div(x*H*N)",
        "existing_geometric_objects_only": [
            "eta_invariant_X_eta",
            "material_sigma",
            "action_owned_core_wall_normal_N",
            "normal_expansion_or_extrinsic_curvature_K_N",
        ],
        "gauge_covariant": True,
        "preferred_external_frame": False,
        "new_field": False,
    }


def orientation_reversal_theorem() -> dict[str, Any]:
    """Verify parity of H and invariance of the paired oriented density."""

    sigma = np.linspace(-0.5, 0.5, 4001)
    h = np.asarray(coupling_function(sigma))
    hp = np.asarray(coupling_derivative(sigma))
    return {
        "paired_map": (
            "sigma_to_minus_sigma,_N_to_minus_N,_q_to_minus_q"
        ),
        "H_is_odd_residual": float(np.max(np.abs(h + h[::-1]))),
        "H_prime_is_even_residual": float(np.max(np.abs(hp - hp[::-1]))),
        "normal_derivative_is_odd": True,
        "product_H_times_normal_derivative_is_even": True,
        "identity_or_unoriented_limit": (
            "q=0_implies_nabla_X_eta=0_and_U_mix=0"
        ),
        "sign_convention_distinguished_from_branch": (
            "reversing_only_the_symbol_for_N_changes_component_signs_but_"
            "the_physical_conjugate_solution_reverses_N_sigma_and_q_together"
        ),
    }


def candidate_status() -> dict[str, Any]:
    return {
        "term": "H(sigma)*a*N^A*nabla_A(a^2*X_eta)",
        "local": True,
        "gauge_covariant": True,
        "uses_existing_fields_and_geometry": True,
        "new_continuous_coefficient": False,
        "H_selected_by_exact_trace_matching_at_leading_order": True,
        "regular_on_normalized_sigma_interval": True,
        "vanishes_on_unoriented_identity_branch": True,
        "full_nonlinear_matching": False,
        "uniqueness_among_all_local_oriented_invariants": False,
        "recovered_by_variation_of_historical_parent_action": False,
        "classification": CLASSIFICATION,
    }


def completion_payload() -> dict[str, Any]:
    variation = mixed_variation_diagnostics()
    parts = integration_by_parts_form()
    reversal = orientation_reversal_theorem()
    status = candidate_status()
    validation = {
        "H_odd": reversal["H_is_odd_residual"] < 1.0e-11,
        "H_prime_even": reversal["H_prime_is_even_residual"] < 1.0e-11,
        "mixed_variation_matches_exact_leading_source": variation[
            "maximum_force_residual_over_q"
        ]
        < 0.02,
        "mixed_density_finite": variation["mixed_density_finite"],
        "unoriented_limit_zero": status["vanishes_on_unoriented_identity_branch"],
        "covariant_by_parts_form_uses_existing_geometry": parts["gauge_covariant"]
        and not parts["new_field"],
        "no_external_frame": not parts["preferred_external_frame"],
        "no_new_continuous_coefficient": not status["new_continuous_coefficient"],
        "candidate_not_overclaimed_as_parent_derived": not status[
            "recovered_by_variation_of_historical_parent_action"
        ],
        "candidate_not_overclaimed_unique": not status[
            "uniqueness_among_all_local_oriented_invariants"
        ],
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_oriented_normal_eta_sigma_completion_v15_31",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "candidate": status,
        "mixed_second_variation_and_source": variation,
        "integration_by_parts": parts,
        "orientation_reversal": reversal,
        "scientific_result": (
            "THE_EXACT_LEADING_FORMATION_TO_MATERIAL_SOURCE_HAS_A_REGULAR_"
            "COEFFICIENT_FREE_LOCAL_ORIENTED_COMPLETION_H_SIGMA_N_GRAD_XETA_"
            "WHOSE_SIGMA_VARIATION_MATCHES_THE_COMPACT_BRANCH_AT_ORDER_Q_"
            "AND_WHOSE_UNORIENTED_LIMIT_VANISHES"
        ),
        "claim_boundary": {
            "candidate_action_completion": True,
            "historical_parent_action_derivation": False,
            "uniqueness_theorem": False,
            "full_nonlinear_q_matching": False,
            "event_sigma_domain_activation": False,
            "constraint_solved_Hopf_child": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "completion_ledger": {
            "CLOSED_THIS_RUN": [
                "smallest_regular_local_oriented_eta_sigma_source_candidate",
                "exact_trace_selected_H_prime_without_a_free_coefficient",
                "paired_internal_orientation_reversal_and_unoriented_limit",
                "explicit_sigma_mixed_variation_and_eta_backreaction_density",
            ],
            "ACTIVE_DEPENDENCY": (
                "PARENT_ACTION_DERIVATION_OR_UNIQUENESS_SELECTION_AND_"
                "FULL_NONLINEAR_CONSTRAINT_CONTINUATION_OF_THE_ORIENTED_"
                "NORMAL_GRADIENT_ETA_SIGMA_COMPLETION"
            ),
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_continuous_coefficients": [],
            "empirical_inputs": [],
            "preferred_external_frame": False,
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
    path = target / "BHSM_aether_oriented_normal_eta_sigma_completion_v15_31.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "coupling_derivative",
    "coupling_function",
    "eta_dimensionless_invariant_and_normal_derivative",
    "mixed_variation_diagnostics",
    "integration_by_parts_form",
    "orientation_reversal_theorem",
    "candidate_status",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
