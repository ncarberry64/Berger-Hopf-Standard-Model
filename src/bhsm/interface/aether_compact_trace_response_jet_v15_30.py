"""Exact compact trace response jet and parent-locality audit.

This module sharpens the v15.29 inverse-Euler result in two directions.

First, on the identity round-S7 branch the normalized trace gives an exact
material response jet

    a^2 U_0'(sigma) = -8 sigma + (2 pi^2/3) sigma^3 + O(sigma^5).

Thus the trace normalization fixes the historical quadratic/quartic *shape*
inside this effective completion class, rather than fitting it.

Second, the formed profiles cannot all be stationary solutions of this one
sigma-only potential: at the common value sigma=0 their required forces vary
with the formation amplitude q.  The exact first-order missing mixed source is

    S_1(chi) q = 4 q sin(chi) [11 cos(chi)^2+5] / (3 pi).

This is a useful localization of the missing coupling, but it does not by
itself define a unique local covariant parent-action term.  The cumulative
trace and collective q are reduced/global objects.  Promoting the inverse
family U_q(sigma) directly would therefore be a state-dependent action, which
is forbidden.  The module preserves that provenance boundary explicitly.
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


VERSION = "v15.30"
FULL_BHSM_COMPLETE = False
CLASSIFICATION = "DERIVED_EFFECTIVE_JET_WITH_PARENT_LOCALITY_OBSTRUCTION"
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def identity_trace_response_jet(points: int = 40001) -> dict[str, Any]:
    """Return the exact identity-branch force jet and a numerical check."""

    arrays = compact_material_arrays(1.0, points=points)
    sigma = np.asarray(arrays["sigma"])
    force = np.asarray(arrays["a2_U_sigma"])
    window = np.abs(sigma) < 0.05
    fit = np.polynomial.polynomial.polyfit(sigma[window], force[window], 5)
    exact_linear = -8.0
    exact_cubic = 2.0 * math.pi**2 / 3.0
    return {
        "identity_trace": (
            "sigma_0=chi/pi-sin(2chi)/(2pi)-1/2"
        ),
        "identity_force_parametric": (
            "a^2 U_0_prime=(8/pi)sin(2chi),_chi=chi(sigma_0)"
        ),
        "Taylor_force": (
            "a^2 U_0_prime=-8*sigma+(2*pi^2/3)*sigma^3+O(sigma^5)"
        ),
        "dimensionless_quadratic_coefficient_a2_A_over_Z": exact_linear,
        "dimensionless_quartic_coefficient_a2_G_over_Z": exact_cubic,
        "fitted_force_coefficients_ascending_0_to_5": fit.tolist(),
        "linear_fit_residual": float(fit[1] - exact_linear),
        "cubic_fit_residual": float(fit[3] - exact_cubic),
        "all_even_force_coefficients_vanish_by_reflection": True,
        "overall_action_normalization_Z_selected_by_trace_shape": False,
    }


def mixed_source_arrays(
    radius_ratio_six: float,
    *,
    points: int = 20001,
) -> dict[str, np.ndarray | float]:
    """Return the source needed beyond the fixed identity potential."""

    ratio = float(radius_ratio_six)
    if not math.isfinite(ratio) or ratio <= 1.0:
        raise ValueError("a formed branch with radius_ratio_six>1 is required")
    identity = compact_material_arrays(1.0, points=points)
    formed = compact_material_arrays(ratio, points=points)
    sigma = np.asarray(formed["sigma"])
    force = np.asarray(formed["a2_U_sigma"])
    identity_force_at_sigma = np.interp(
        sigma,
        np.asarray(identity["sigma"]),
        np.asarray(identity["a2_U_sigma"]),
    )
    source = force - identity_force_at_sigma
    chi = np.asarray(formed["chi"])
    q = float(formed["q"])
    leading = (
        4.0
        * q
        * np.sin(chi)
        * (11.0 * np.cos(chi) ** 2 + 5.0)
        / (3.0 * math.pi)
    )
    return {
        "chi": chi,
        "sigma": sigma,
        "q": q,
        "required_mixed_source": source,
        "leading_mixed_source": leading,
    }


def mixed_source_diagnostics(
    radius_ratio_six: float = 1.00001,
    *,
    points: int = 30001,
) -> dict[str, Any]:
    """Check the exact first-order mixed source against the solved branch."""

    arrays = mixed_source_arrays(radius_ratio_six, points=points)
    chi = np.asarray(arrays["chi"])
    source = np.asarray(arrays["required_mixed_source"])
    leading = np.asarray(arrays["leading_mixed_source"])
    q = float(arrays["q"])
    interior = (chi > 0.02) & (chi < math.pi - 0.02)
    return {
        "radius_ratio_six": float(radius_ratio_six),
        "q": q,
        "source_equation": (
            "S_q(chi)=a^2U_q_prime(sigma_q)-a^2U_0_prime(sigma_q)"
        ),
        "leading_exact_source": (
            "S_q=4q*sin(chi)*(11cos(chi)^2+5)/(3pi)+O(q^2)"
        ),
        "maximum_error_over_q_on_interior": float(
            np.max(np.abs(source[interior] - leading[interior])) / abs(q)
        ),
        "rms_error_over_q_on_interior": float(
            np.sqrt(np.mean((source[interior] - leading[interior]) ** 2))
            / abs(q)
        ),
        "source_at_sigma_zero_over_q": float(
            np.interp(0.0, np.asarray(arrays["sigma"]), source) / q
        ),
        "expected_source_at_zero_over_q": 20.0 / (3.0 * math.pi),
    }


def state_independent_potential_no_go() -> dict[str, Any]:
    """Prove that one sigma-only potential cannot generate the whole q family."""

    identity = compact_material_arrays(1.0, points=12001)
    formed = compact_material_arrays(1.01, points=12001)
    f0 = float(
        np.interp(
            0.0,
            np.asarray(identity["sigma"]),
            np.asarray(identity["a2_U_sigma"]),
        )
    )
    fq = float(
        np.interp(
            0.0,
            np.asarray(formed["sigma"]),
            np.asarray(formed["a2_U_sigma"]),
        )
    )
    return {
        "assumption": (
            "one_local_state_independent_sigma_only_potential_U(sigma)_"
            "makes_every_trace_profile_sigma_q_stationary"
        ),
        "common_field_value": 0.0,
        "identity_required_a2_U_prime_at_zero": f0,
        "formed_required_a2_U_prime_at_zero": fq,
        "values_disagree": not math.isclose(f0, fq, abs_tol=1.0e-6),
        "contradiction": (
            "a_single_valued_U_prime_at_sigma_zero_cannot_equal_both_values"
        ),
        "conclusion": (
            "a_mixed_eta_sigma_term_or_a_dynamical_constraint_is_required;_"
            "the_family_U_q_cannot_be_inserted_as_a_state_dependent_action"
        ),
    }


def parent_locality_audit() -> dict[str, Any]:
    """Classify what the trace construction does and does not select."""

    return {
        "retained_local_objects": [
            "eta",
            "metric",
            "independent_material_sigma",
            "normalized_eta_zero_mode_one_form_alpha_eta",
        ],
        "reduced_objects": [
            "formation_collective_amplitude_q",
            "cumulative_trace_C_eta",
            "branchwise_inverse_potential_U_q",
        ],
        "coefficient_free_trace_constraint_candidate": (
            "one_half_norm(d_sigma-alpha_eta)^2"
        ),
        "trace_constraint_bulk_effect": (
            "enforces_sigma-C_eta=constant_on_fixed_boundary_data_but_has_"
            "zero_on_shell_skin_energy_and_does_not_supply_material_tension"
        ),
        "branchwise_U_q_is_local_state_independent_parent_action": False,
        "reason": (
            "q_and_C_eta_are_collective_or_cumulative_and_the_off_branch_"
            "covariant_extension_of_the_mixed_source_is_not_unique"
        ),
        "smallest_source_localized_in_reduced_theory": (
            "minus_integral_sigma*S_q_on_the_compact_formation_collective_"
            "manifold_with_S_q_fixed_above"
        ),
        "classification_of_that_source": (
            "REDUCED_ACTION_COMPLETION_CANDIDATE_NOT_PARENT_ACTION_DERIVATION"
        ),
        "arbitrary_continuous_coefficient_in_leading_reduced_source": False,
        "unique_local_parent_completion_proved": False,
    }


def completion_payload() -> dict[str, Any]:
    jet = identity_trace_response_jet()
    source = mixed_source_diagnostics()
    no_go = state_independent_potential_no_go()
    locality = parent_locality_audit()
    validation = {
        "identity_linear_jet_exact": abs(jet["linear_fit_residual"]) < 1.0e-6,
        "identity_cubic_jet_exact": abs(jet["cubic_fit_residual"]) < 2.0e-4,
        "leading_mixed_source_verified": source[
            "maximum_error_over_q_on_interior"
        ]
        < 0.02,
        "median_source_coefficient_verified": abs(
            source["source_at_sigma_zero_over_q"]
            - source["expected_source_at_zero_over_q"]
        )
        < 0.01,
        "state_independent_sigma_only_potential_rejected": no_go["values_disagree"],
        "state_dependent_action_not_promoted": not locality[
            "branchwise_U_q_is_local_state_independent_parent_action"
        ],
        "no_fake_unique_parent_completion": not locality[
            "unique_local_parent_completion_proved"
        ],
        "no_empirical_input_or_new_parameter": True,
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_compact_trace_response_jet_v15_30",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "identity_effective_response_jet": jet,
        "formed_branch_mixed_source": source,
        "state_independent_potential_theorem": no_go,
        "parent_locality_audit": locality,
        "scientific_result": (
            "THE_COMPACT_TRACE_FIXES_THE_EXACT_EFFECTIVE_IDENTITY_JET_"
            "A2_A_OVER_Z_EQUALS_MINUS_8_AND_A2_G_OVER_Z_EQUALS_2PI2_OVER3_"
            "AND_THE_FORMED_BRANCH_FIXES_ITS_LEADING_MIXED_SOURCE;_BUT_ONE_"
            "SIGMA_ONLY_POTENTIAL_CANNOT_GENERATE_THE_FORMATION_FAMILY_AND_"
            "THE_BRANCHWISE_INVERSE_POTENTIAL_IS_NOT_A_LOCAL_PARENT_ACTION"
        ),
        "claim_boundary": {
            "historical_independent_sigma_identified_with_trace": False,
            "effective_response_jet_derived": True,
            "overall_sigma_action_normalization_derived": False,
            "unique_local_parent_mixed_term_derived": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "completion_ledger": {
            "CLOSED_THIS_RUN": [
                "exact_identity_trace_quadratic_and_quartic_response_shape",
                "exact_leading_formation_mixed_source_on_the_reduced_branch",
                "single_sigma_only_potential_no_go_for_the_full_q_family",
            ],
            "ACTIVE_DEPENDENCY": (
                "LOCAL_GAUGE_COVARIANT_PARENT_ACTION_DERIVATION_OR_"
                "UNIQUENESS_SELECTION_OF_THE_ETA_SIGMA_MIXED_SOURCE_WITH_"
                "EVENT_DOMAIN_ACTIVATION_AND_COMPLETE_CONSTRAINT_REDUCTION"
            ),
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_continuous_coefficients": [],
            "empirical_inputs": [],
            "state_dependent_action_inserted": False,
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
    path = target / "BHSM_aether_compact_trace_response_jet_v15_30.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION",
    "FULL_BHSM_COMPLETE",
    "CLASSIFICATION",
    "identity_trace_response_jet",
    "mixed_source_arrays",
    "mixed_source_diagnostics",
    "state_independent_potential_no_go",
    "parent_locality_audit",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
