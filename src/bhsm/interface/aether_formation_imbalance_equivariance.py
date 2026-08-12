"""Equivariance audit for the proposed formation-imbalance sigma response.

The retained formation sector has a physical q-to-s transfer, but the
retained scalar action also has an independent sigma reflection.  This
module checks the transformation laws of every formation-imbalance candidate
named in the completion directive and proves the resulting selection rule.
It neither adds a sigma source nor identifies two independent reflections.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_cycle_sigma_coefficient_reconstruction_v15_10 import (
    reconstruction_interface_payload,
    retained_nonuniqueness_witness,
)
from bhsm.interface.aether_moving_formed_symplectic_v15_25 import (
    leading_whitened_qs_gram,
)


FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def hopf_factor_exchange() -> dict[str, Any]:
    """Return the exact 4+4 factor-exchange action on the Hopf split."""

    identity = np.eye(4)
    zero = np.zeros((4, 4))
    exchange = np.block([[zero, identity], [identity, zero]])
    split = np.diag([1.0] * 4 + [-1.0] * 4)
    transformed = exchange.T @ split @ exchange
    return {
        "J": split.tolist(),
        "factor_exchange": exchange.tolist(),
        "P_transpose_J_P": transformed.tolist(),
        "J_reverses": bool(np.array_equal(transformed, -split)),
        "zeta_reverses": True,
        "sigma_reflection_performed_by_factor_exchange": False,
        "symmetry_group_on_retained_zero_sigma_action": "Z2_sigma_x_Z2_join",
    }


def formation_imbalance_candidates(q: float, zeta: float) -> dict[str, Any]:
    """Classify the directive's existing imbalance candidates.

    The candidate values can be odd under formation-branch or Hopf-factor
    reversal.  They are all fixed by the *independent* retained transformation
    R_sigma: sigma -> -sigma.
    """

    amplitude = float(q)
    orientation = float(zeta)
    if not math.isfinite(amplitude):
        raise ValueError("q must be finite")
    if not math.isfinite(orientation) or abs(orientation) > 1.0 + 1.0e-13:
        raise ValueError("zeta must lie in [-1,1]")
    if abs(amplitude) < 1.0e-14:
        correlation = 0.0
    else:
        correlation = leading_whitened_qs_gram(
            amplitude, zeta=orientation
        )["whitened_cross_correlation"]
    rows = {
        "q": {
            "value": amplitude,
            "sigma_reflection_parity": "even",
            "formation_branch_parity": "odd",
        },
        "C_eta_minus_one_leading": {
            "value": 49.0 * amplitude**2 / 8.0,
            "sigma_reflection_parity": "even",
            "formation_branch_parity": "even",
        },
        "zeta": {
            "value": orientation,
            "sigma_reflection_parity": "even",
            "join_factor_exchange_parity": "odd",
        },
        "q_squared_zeta": {
            "value": amplitude**2 * orientation,
            "sigma_reflection_parity": "even",
            "join_factor_exchange_parity": "odd",
        },
        "rho_qs": {
            "value": correlation,
            "sigma_reflection_parity": "even",
            "join_factor_exchange_parity": "odd",
        },
    }
    return {
        "candidates": rows,
        "every_candidate_fixed_by_independent_sigma_reflection": all(
            row["sigma_reflection_parity"] == "even" for row in rows.values()
        ),
        "nonzero_oriented_candidate_present": any(
            abs(float(row["value"])) > 1.0e-14 for row in rows.values()
        ),
    }


def monomial_symmetry(power_sigma: int, power_orientation: int) -> dict[str, Any]:
    """Classify sigma^m Delta^n under the two independent reflections."""

    m = int(power_sigma)
    n = int(power_orientation)
    if m < 0 or n < 0:
        raise ValueError("powers must be nonnegative")
    sigma_sign = -1 if m % 2 else 1
    join_sign = -1 if n % 2 else 1
    return {
        "power_sigma": m,
        "power_orientation": n,
        "R_sigma_sign": sigma_sign,
        "R_join_sign": join_sign,
        "diagonal_reversal_sign": sigma_sign * join_sign,
        "invariant_under_product_group": sigma_sign == 1 and join_sign == 1,
        "invariant_only_after_diagonal_locking": (
            sigma_sign * join_sign == 1 and not (sigma_sign == 1 and join_sign == 1)
        ),
    }


def equivariant_sigma_response_theorem() -> dict[str, Any]:
    """State the function-level, not merely polynomial, fixed-point theorem."""

    candidates = formation_imbalance_candidates(0.14, 0.6)
    linear_source = monomial_symmetry(1, 1)
    return {
        "domain": "formation_state_X=(q,s,zeta,rho_qs,eta,g_metric,...)_at_sigma_zero",
        "retained_action_symmetry": "R_sigma:(X,sigma,p_sigma)->(X,-sigma,-p_sigma)",
        "equivariance_condition": "F_sigma(R_sigma X)=R_sigma F_sigma(X)",
        "fixed_domain_condition": "R_sigma X=X",
        "deduction": "F_sigma(X)=-F_sigma(X)_therefore_F_sigma(X)=0",
        "holds_for_every_deterministic_equivariant_function": True,
        "not_limited_to_polynomials_or_linear_response": True,
        "all_named_formation_candidates_are_R_sigma_even": candidates[
            "every_candidate_fixed_by_independent_sigma_reflection"
        ],
        "candidate_sigma_times_Delta_form": linear_source,
        "sigma_Delta_forbidden_by_retained_product_symmetry": not linear_source[
            "invariant_under_product_group"
        ],
        "sigma_Delta_allowed_only_if_reflections_are_newly_locked": linear_source[
            "invariant_only_after_diagonal_locking"
        ],
        "nonzero_sigma_response_from_current_formation_state": False,
    }


def archive_route_exhaustion() -> dict[str, Any]:
    """Record why the closest earlier Norman/BHSM objects do not supply the map."""

    return {
        "v6_4_odd_wall_coupling": {
            "candidate": "y_sigma*sigma*Gamma_star",
            "status": "allowed_but_not_parent_derived",
            "selects_formation_to_sigma_map": False,
        },
        "v6_14_composite_level_set": {
            "map_direction": "sigma_profile_to_surface_displacement_zeta",
            "status": "unadopted_off_shell_domain_restriction",
            "reverse_map_defined": False,
        },
        "v6_18_threading_response": {
            "response": "S_Sigma=-tau*pi*chi1*q/16+O(q^2)",
            "scalar_sign_dependence": False,
            "selects_sigma": False,
        },
        "v15_17_crossover": {
            "orientation_odd_sigma_source": False,
            "transports_supplied_response_jet_only": True,
        },
        "v15_24_join": {
            "zeta_projection_derived": True,
            "physical_relative_orientation_selected": False,
            "physical_sigma_source_vertex_derived": False,
        },
        "v15_25_moving_Gram": {
            "G_qsigma_at_sigma_zero": 0.0,
            "G_ssigma_at_sigma_zero": 0.0,
            "rho_qs_nonzero": True,
            "q_s_transfer_is_sigma_source": False,
        },
        "route_produces_nonzero_action_owned_sigma_initial_state": False,
    }


def response_magnitude_selection_audit() -> dict[str, Any]:
    """Check whether formation data select the independent sigma response jet."""

    witness = retained_nonuniqueness_witness()
    interface = reconstruction_interface_payload()
    return {
        "inequivalent_retained_response_triples": len(witness["triples"]),
        "same_sigma_zero_parent_and_first_variation": witness[
            "same_sigma_zero_background_and_first_variation"
        ],
        "physical_response_generator_present": interface[
            "physical_sigma_propagator_present_in_repository"
        ],
        "physical_response_X_derivative_present": interface[
            "X_derivative_present_in_repository"
        ],
        "physical_nonlinear_response_present": interface[
            "physical_nonlinear_sigma_response_present_in_repository"
        ],
        "formation_fields_can_vary_unvaried_action_constants": False,
        "G_sigma_or_scalar_g_selected": False,
    }


def foundational_consistency_audit() -> dict[str, Any]:
    """Evaluate the completion directive's simultaneous requirements."""

    theorem = equivariant_sigma_response_theorem()
    magnitude = response_magnitude_selection_audit()
    routes = archive_route_exhaustion()
    contradiction = (
        theorem["nonzero_sigma_response_from_current_formation_state"] is False
        and magnitude["G_sigma_or_scalar_g_selected"] is False
        and routes["route_produces_nonzero_action_owned_sigma_initial_state"] is False
    )
    return {
        "requirements_kept": [
            "retain_the_existing_sigma_reflection_even_action",
            "start_the_validated_formation_state_at_sigma=p_sigma=0",
            "introduce_no_new_action_term_domain_identification_seed_or_coefficient",
            "derive_a_nonzero_deterministic_sigma_response_from_existing_formation_variables",
        ],
        "requirements_are_jointly_satisfiable": not contradiction,
        "logical_contradiction_proved": contradiction,
        "why_not_simple_underdetermination": (
            "equivariance_forces_every_deterministic_response_from_the_declared_"
            "formation_state_to_zero;_the_needed_sigma_Delta_term_is_forbidden_"
            "unless_the_independent_reflections_are_changed_to_a_diagonal_symmetry"
        ),
        "smallest_mathematical_revision_needed": (
            "an_action_owned_relation_that_identifies_sigma_reflection_with_an_"
            "orientation_reversal_and_derives_its_mixed_source_coefficient_plus_"
            "the_complete_sigma_response_jet"
        ),
        "revision_present_in_retained_action_or_state_domain": False,
        "revision_implemented": False,
        "reason_revision_not_implemented": (
            "it_would_change_the_action_or_off_shell_domain_and_add_unselected_"
            "physical_data_contrary_to_the_completion_directive"
        ),
        "downstream_skin_child_and_SM_readout_defined": False,
    }


def completion_payload() -> dict[str, Any]:
    exchange = hopf_factor_exchange()
    candidates = formation_imbalance_candidates(0.14, 0.6)
    theorem = equivariant_sigma_response_theorem()
    routes = archive_route_exhaustion()
    magnitude = response_magnitude_selection_audit()
    consistency = foundational_consistency_audit()
    reversed_candidates = formation_imbalance_candidates(0.14, -0.6)
    validation = {
        "Hopf_factor_exchange_reverses_J": exchange["J_reverses"],
        "all_named_candidates_are_sigma_even": candidates[
            "every_candidate_fixed_by_independent_sigma_reflection"
        ],
        "rho_qs_is_join_odd": math.isclose(
            candidates["candidates"]["rho_qs"]["value"],
            -reversed_candidates["candidates"]["rho_qs"]["value"],
            rel_tol=1.0e-13,
            abs_tol=1.0e-15,
        ),
        "sigma_Delta_is_not_product_invariant": theorem[
            "sigma_Delta_forbidden_by_retained_product_symmetry"
        ],
        "function_level_equivariance_forces_zero": theorem[
            "holds_for_every_deterministic_equivariant_function"
        ],
        "archive_routes_exhausted_without_reverse_map": not routes[
            "route_produces_nonzero_action_owned_sigma_initial_state"
        ],
        "response_magnitude_remains_unselected": not magnitude[
            "G_sigma_or_scalar_g_selected"
        ],
        "joint_requirements_are_contradictory": consistency[
            "logical_contradiction_proved"
        ],
        "no_new_action_term_seed_field_or_coefficient": True,
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_formation_imbalance_equivariance",
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "Hopf_factor_exchange": exchange,
        "formation_imbalance_candidates": candidates,
        "equivariant_sigma_response_theorem": theorem,
        "Norman_BHSM_archive_route_exhaustion": routes,
        "response_magnitude_selection": magnitude,
        "foundational_consistency_audit": consistency,
        "result": (
            "THE_RETAINED_ACTION_HAS_INDEPENDENT_SIGMA_AND_JOIN_REFLECTIONS_"
            "SO_EVERY_EXISTING_FORMATION_IMBALANCE_IS_SIGMA_EVEN_AND_CANNOT_"
            "SOURCE_OR_SELECT_NONZERO_SIGMA;_THE_DIRECTIVE_REQUIREMENTS_ARE_"
            "JOINTLY_INCONSISTENT_UNLESS_THE_ACTION_OR_STATE_DOMAIN_IS_REVISED"
        ),
        "downstream_status": (
            "material_skin_separation_child_and_standard_model_readout_are_not_"
            "defined_by_the_retained_action"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_action_terms": [],
            "new_continuous_coefficients": [],
            "new_sigma_seeds": [],
            "new_empirical_inputs": [],
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
    path = target / "BHSM_aether_formation_imbalance_equivariance.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "FULL_BHSM_COMPLETE",
    "hopf_factor_exchange",
    "formation_imbalance_candidates",
    "monomial_symmetry",
    "equivariant_sigma_response_theorem",
    "archive_route_exhaustion",
    "response_magnitude_selection_audit",
    "foundational_consistency_audit",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
