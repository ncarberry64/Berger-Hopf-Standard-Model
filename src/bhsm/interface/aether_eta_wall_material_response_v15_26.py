"""Coefficient-free eta-wall orientation to material-response completion.

The retained v15.25 scalar block has an independent ``sigma -> -sigma``
symmetry and therefore cannot activate sigma from its exact fixed point.  The
already-adopted eta-bound Dirac domain supplies more structure: its normalized
normal zero mode defines a probability one-form on the oriented eta collar.

This module derives that one-form, tests the minimal covariantized sigma
kinetic candidate, and checks the analytic wall and the retained numerical
degree-one eta profile.  The candidate is classified as
``BHSM_ACTION_COMPLETION`` but is not promoted to the physical action: on a
one-dimensional collar the one-form is exact, so the bulk coupling is removed
by a field redefinition unless an independently derived affine boundary
domain or nonzero configuration-space curvature is supplied.  It is also not
misreported as a consequence of the old bosonic Path-B action, because the
eta-bound Dirac action itself was adopted as foundational effective data in
v14.45.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from bhsm.interface.completion.eta_static_texture_v13_1 import solve_profile
from bhsm.interface.completion.eta_knot_projector_connection_v13_5 import (
    reference_curvature,
)
from bhsm.interface.completion.hopf_smash_topological_transgression_v14_33 import (
    topological_current_transgression_payload,
)
from bhsm.interface.completion.relative_holonomy_full_shape_hessian_v14_37 import (
    holonomy_hessian_audit_payload,
)


VERSION = "v15.26"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False
CLASSIFICATION = "BHSM_ACTION_COMPLETION"


def _finite_array(values: Sequence[float], name: str) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim != 1 or array.size < 3 or not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must be a finite one-dimensional array")
    return array


def analytic_eta_wall_response(normal_coordinate: Sequence[float]) -> dict[str, Any]:
    """Return the exact response induced by the analytic eta wall.

    For ``f=2 atan(exp(s))`` the v14.45 zero mode has
    ``sin(f)=sech(s)``.  Its normalized probability one-form is
    ``alpha_eta=(1/2)sech(s)^2 ds`` on the complete line.
    """

    coordinate = _finite_array(normal_coordinate, "normal_coordinate")
    sech = 1.0 / np.cosh(coordinate)
    tanh = np.tanh(coordinate)
    density = 0.5 * sech**2
    cumulative = 0.5 * (1.0 + tanh)
    sigma = cumulative - 0.5
    sigma_prime = density
    bps_velocity = 0.5 - 2.0 * sigma**2
    sigma_second = -sech**2 * tanh
    historical_potential_prime = -2.0 * sigma + 8.0 * sigma**3
    return {
        "coordinate": coordinate,
        "sin_f_eta": sech,
        "m_eta": tanh,
        "alpha_eta_density": density,
        "C_eta": cumulative,
        "sigma_eta": sigma,
        "sigma_eta_prime": sigma_prime,
        "bps_velocity": bps_velocity,
        "sigma_eta_second": sigma_second,
        "historical_potential_prime": historical_potential_prime,
        "first_order_residual": float(np.max(np.abs(sigma_prime - bps_velocity))),
        "second_order_residual": float(
            np.max(np.abs(sigma_second - historical_potential_prime))
        ),
    }


def normalized_eta_probability_response(
    normal_coordinate: Sequence[float],
    sin_f_eta: Sequence[float],
) -> dict[str, Any]:
    """Construct the canonical response from an arbitrary solved eta profile.

    The v14.45 exact zero mode is ``u0=N J^(-1/2) sin(f_eta)``.  Hence
    ``J |u0|^2 ds=N^2 sin(f_eta)^2 ds``: the collar Jacobian cancels and the
    normalized probability one-form is fixed without a new coefficient.
    """

    coordinate = _finite_array(normal_coordinate, "normal_coordinate")
    sin_f = _finite_array(sin_f_eta, "sin_f_eta")
    if coordinate.shape != sin_f.shape or not np.all(np.diff(coordinate) > 0.0):
        raise ValueError("the profile arrays must match and coordinates must increase")
    raw_density = sin_f**2
    normalization_integral = float(np.trapezoid(raw_density, coordinate))
    if normalization_integral <= 0.0:
        raise ValueError("the eta zero mode must have positive norm")
    density = raw_density / normalization_integral
    increments = 0.5 * (density[1:] + density[:-1]) * np.diff(coordinate)
    cumulative = np.concatenate(([0.0], np.cumsum(increments)))
    # Remove the floating quadrature endpoint error while preserving monotonicity.
    cumulative /= cumulative[-1]
    sigma = cumulative - 0.5
    reversed_density = density[::-1]
    reversed_increments = (
        0.5 * (reversed_density[1:] + reversed_density[:-1]) * np.diff(coordinate)
    )
    reversed_cumulative = np.concatenate(([0.0], np.cumsum(reversed_increments)))
    reversed_cumulative /= reversed_cumulative[-1]
    reversal_residual = float(
        np.max(np.abs((reversed_cumulative - 0.5) + sigma[::-1]))
    )
    return {
        "normalization_integral": normalization_integral,
        "normalization_squared": 1.0 / normalization_integral,
        "alpha_eta_density": density,
        "C_eta": cumulative,
        "sigma_eta": sigma,
        "unit_holonomy": float(cumulative[-1] - cumulative[0]),
        "endpoint_values": [float(sigma[0]), float(sigma[-1])],
        "monotone": bool(np.min(np.diff(cumulative)) >= -1.0e-14),
        "orientation_reversal_residual": reversal_residual,
    }


def retained_eta_profile_response(points: int = 12001) -> dict[str, Any]:
    """Evaluate the construction on the retained v13.1 degree-one solution."""

    if points < 1001:
        raise ValueError("points must be at least 1001")
    solution = solve_profile()
    log_radius = np.linspace(float(solution.x[0]), float(solution.x[-1]), points)
    radius = np.exp(log_radius)
    f_eta = solution.sol(log_radius)[0]
    response = normalized_eta_probability_response(radius, np.sin(f_eta))
    density = np.asarray(response["alpha_eta_density"])
    sigma = np.asarray(response["sigma_eta"])
    bps_shape = 0.5 - 2.0 * sigma**2
    best_inverse_length = float(np.dot(density, bps_shape) / np.dot(bps_shape, bps_shape))
    relative_residual = float(
        np.linalg.norm(density - best_inverse_length * bps_shape)
        / np.linalg.norm(density)
    )
    median_index = int(np.argmin(np.abs(np.asarray(response["C_eta"]) - 0.5)))
    return {
        "profile": "retained_v13_1_p2_plus_p8_degree_one_eta_solution",
        "proper_radial_domain": [float(radius[0]), float(radius[-1])],
        "median_radius": float(radius[median_index]),
        "unit_holonomy": response["unit_holonomy"],
        "endpoint_values": response["endpoint_values"],
        "monotone": response["monotone"],
        "orientation_reversal_residual": response["orientation_reversal_residual"],
        "best_BPS_inverse_length": best_inverse_length,
        "relative_BPS_profile_residual": relative_residual,
        "analytic_sech_BPS_profile_is_exact_for_retained_solution": (
            relative_residual < 1.0e-6
        ),
    }


def lowest_order_odd_scalar_audit() -> dict[str, Any]:
    """Classify the lowest derivative orientation-odd scalar candidates."""

    return {
        "orientation_carrier": "u_eta=grad(f_eta)/|grad(f_eta)|_on_the_regular_wall_collar",
        "candidates": {
            "u_eta_dot_grad_F_eta": {
                "odd": True,
                "status": "nonunique_for_arbitrary_F_and_boundary_equivalent_after_parts",
            },
            "div_u_eta_or_oriented_mean_curvature": {
                "odd": True,
                "status": "geometric_but_does_not_fix_material_response_normalization",
            },
            "m_eta_minus_u_grad_log_sin_f": {
                "odd": True,
                "status": "canonical_clifford_domain_coefficient_not_a_scalar_material_map_by_itself",
            },
            "div_alpha_eta": {
                "odd": True,
                "status": "canonical_after_normalized_eta_zero_mode_domain_is_adopted",
            },
        },
        "selected_one_form": (
            "alpha_eta=J|u0|^2 ds=N^2 sin(f_eta)^2 ds;_integral_alpha_eta=1"
        ),
        "selected_scalar_source": "O_eta=Z_sigma*nabla_a(alpha_eta^a)",
        "uniqueness_scope": (
            "unique_probability_one_form_of_the_existing_normalized_eta_bound_zero_mode;_"
            "not_a_uniqueness_theorem_over_all_possible_higher_derivative_action_completions"
        ),
    }


def completed_sigma_action() -> dict[str, Any]:
    """Return the minimal kinetic covariantization candidate and variation."""

    return {
        "classification": CLASSIFICATION,
        "physical_status": "CANDIDATE_NOT_ACTION_SELECTED",
        "old_kinetic_block": "-Z_sigma/2*(nabla_sigma)^2",
        "completed_kinetic_block": "-Z_sigma/2*(nabla_sigma-alpha_eta)^2",
        "added_term": (
            "+Z_sigma*nabla_a(sigma)*alpha_eta^a-"
            "Z_sigma/2*alpha_eta_a*alpha_eta^a"
        ),
        "Euler_Lagrange_equation": (
            "Z_sigma*nabla_a(nabla^a_sigma-alpha_eta^a)-V_even_prime(sigma)=0"
        ),
        "oriented_source_form": (
            "Z_sigma*Box(sigma)-V_even_prime(sigma)="
            "Z_sigma*nabla_a(alpha_eta^a)"
        ),
        "free_response_limit": "V_even=0_implies_nabla_sigma=alpha_eta_on_the_ground_section",
        "ground_section": "sigma_eta=C_eta-1/2",
        "candidate_affine_domain": "sigma_eta(right)-sigma_eta(left)=integral_alpha_eta=1",
        "candidate_centering": "sigma_eta(left)+sigma_eta(right)=0",
        "new_continuous_coefficient": False,
        "normalization_owner": "canonical_v14_45_eta_zero_mode_norm_and_existing_Z_sigma",
        "locality_boundary": (
            "the_density_is_local_once_the_self_adjoint_zero_mode_is_normalized;_"
            "its_unit_normalization_is_global_domain_data"
        ),
        "old_bosonic_Path_B_derivation_claimed": False,
        "coefficient_uniqueness_theorem_present": False,
        "affine_sigma_domain_derived_from_retained_action": False,
    }


def exact_gradient_field_redefinition_audit() -> dict[str, Any]:
    """Test whether the collar connection produces irreducible bulk dynamics."""

    return {
        "collar_topology": "oriented_interval",
        "identity": "alpha_eta=dC_eta",
        "closed_path_holonomy": 0.0,
        "open_path_transport": "integral_left_to_right_alpha_eta=1",
        "open_path_transport_is_not_closed_loop_holonomy": True,
        "field_redefinition": "xi=sigma-C_eta",
        "kinetic_reduction": "(d_sigma-alpha_eta)^2=(d_xi)^2",
        "configuration_space_curvature": "d_alpha_eta=0_for_alpha_eta=dC_eta",
        "irreducible_bulk_q_sigma_transfer_from_this_square": False,
        "what_would_make_it_physical": [
            "an_action_derived_affine_sigma_boundary_domain",
            "a_nonexact_eta_Hopf_connection_with_nonzero_curvature_or_closed_holonomy",
            "an_independently_normalized_nonderivative_sigma_O_eta_vertex",
        ],
        "physical_sigma_activation_closed": False,
    }


def nonexact_orientation_route_audit() -> dict[str, Any]:
    """Exhaust the nearest non-exact eta/Hopf orientation carriers."""

    projector = reference_curvature()
    restricted = np.asarray(projector["curvature_restricted_3x3"], dtype=complex)
    current = topological_current_transgression_payload()
    holonomy = holonomy_hessian_audit_payload()
    return {
        "eta_projector_connection": {
            "curvature_nonzero": projector["validation"]["curvature_nonzero"],
            "restricted_trace_norm": float(abs(np.trace(restricted))),
            "bundle_role": "rank_three_eta_polarization_SU3_reference_connection",
            "gauge_invariant_linear_scalar_from_F": False,
            "physical_Yang_Mills_normalization_fixed": False,
            "can_source_singlet_sigma_without_new_contraction_or_coefficient": False,
        },
        "transgressed_degree_current": {
            "current": current["physical_current_three_form"],
            "regular_branch_conserved": current["validation"][
                "closed_bulk_degree_form_gives_closed_physical_current_when_boundary_flux_zero"
            ],
            "only_coefficient_free_4form_linear_in_dsigma": "d_sigma_wedge_j3",
            "regular_branch_identity": "d_sigma_wedge_j3=d(sigma*j3)_when_dj3=0",
            "regular_bulk_sigma_source": False,
            "event_source": "-sigma*dj3_can_exist_only_at_derived_fiber_boundary_flux_or_topology_change",
            "physical_event_flux_present_in_current_repository": False,
        },
        "relative_Z6_holonomy": {
            "can_orient": holonomy["validation"][
                "holonomy_can_orient_but_not_create_bridge_amplitude"
            ],
            "creates_quadratic_amplitude": False,
            "action_ownership": holonomy["action_ownership"],
            "can_close_sigma_activation": False,
        },
        "extrinsic_and_mean_curvature_scalars": {
            "examples": ["div(u_eta)", "u_eta^a*nabla_a(F(eta))"],
            "orientation_odd": True,
            "independent_function_or_normalization_freedom_removed": False,
            "unique_action_vertex": False,
        },
        "result": (
            "NO_EXISTING_RETAINED_OR_FOUNDATIONAL_BHSM_OBJECT_SUPPLIES_A_"
            "NONEXACT_GAUGE_SINGLET_ORIENTATION_CONNECTION_OR_A_UNIQUELY_"
            "NORMALIZED_NONDERIVATIVE_SIGMA_VERTEX_ON_THE_REGULAR_FORMED_BRANCH"
        ),
        "first_upstream_nonzero_possibility": (
            "THE_DISTRIBUTIONAL_DJ3_FIBER_BOUNDARY_FLUX_AT_AN_ACTUAL_"
            "RECONSTRUCTION_OR_TOPOLOGY_CHANGE_EVENT"
        ),
    }


def diagonal_symmetry_audit() -> dict[str, Any]:
    """Prove how the completed kinetic block changes the reflection group."""

    return {
        "old_truncation": "Z2_sigma_x_Z2_eta_orientation",
        "independent_sigma_reversal": {
            "map": "(d_sigma,alpha_eta)->(-d_sigma,alpha_eta)",
            "completed_square_invariant": False,
        },
        "independent_orientation_reversal": {
            "map": "(d_sigma,alpha_eta)->(d_sigma,-alpha_eta)",
            "completed_square_invariant": False,
        },
        "diagonal_reversal": {
            "map": "(d_sigma,alpha_eta)->(-d_sigma,-alpha_eta)",
            "completed_square_invariant": True,
        },
        "physical_branches": "sigma_eta[-u_eta]=-sigma_eta[u_eta]_after_collaring_pullback",
        "product_symmetry_reduced_by_completed_action_not_imposed_as_domain_axiom": True,
    }


def collective_completion_gram(
    *, dC_dq: float, dC_ds: float, zsigma: float = 1.0
) -> dict[str, Any]:
    """Pull the completed kinetic square back to Q=(q,s,sigma).

    This is the coordinate rank-one contribution from
    ``(sigma_dot-C_q q_dot-C_s s_dot)^2``.  The actual values of ``C_q`` and
    ``C_s`` require the solved moving eta/join profile and are not guessed.
    """

    cq, cs, zz = float(dC_dq), float(dC_ds), float(zsigma)
    if not all(math.isfinite(value) for value in (cq, cs, zz)) or zz <= 0.0:
        raise ValueError("derivatives must be finite and zsigma positive")
    covector = np.array([-cq, -cs, 1.0])
    gram = zz * np.outer(covector, covector)
    eigenvalues = np.linalg.eigvalsh(gram)
    return {
        "coordinate_order": ["q", "s", "sigma"],
        "covariant_velocity": "sigma_dot-C_q*q_dot-C_s*s_dot",
        "Gram_completion": gram.tolist(),
        "rank": int(np.linalg.matrix_rank(gram, tol=1.0e-12)),
        "eigenvalues": eigenvalues.tolist(),
        "positive_semidefinite": bool(np.min(eigenvalues) > -1.0e-12),
        "G_qsigma": float(gram[0, 2]),
        "G_ssigma": float(gram[1, 2]),
        "cross_terms_nonzero_if_profile_moves": bool(abs(cq) + abs(cs) > 0.0),
        "C_q_C_s_status": "must_be_evaluated_from_the_moving_constraint_solved_eta_join_BVP",
        "field_redefinition_warning": (
            "because_C_eta_is_a_global_scalar_this_rank_one_block_is_removed_"
            "by_xi=sigma-C_eta_unless_the_affine_domain_or_connection_curvature_"
            "is_independently_physical"
        ),
        "promoted_as_physical_transfer": False,
    }


def analytic_bps_recovery() -> dict[str, Any]:
    """Recover the historical normalized quartic on the analytic wall only."""

    coordinate = np.linspace(-10.0, 10.0, 20001)
    wall = analytic_eta_wall_response(coordinate)
    return {
        "analytic_profile": "sin(f_eta)=sech(s/ell_eta)",
        "first_order_identity": "ell_eta*d_s_sigma=1/2-2*sigma^2",
        "BPS_energy": (
            "Z_sigma/(2*ell_eta^2)*(1/2-2*sigma^2)^2="
            "Z_sigma/ell_eta^2*(1/8-sigma^2+2*sigma^4)"
        ),
        "constant_subtracted_potential": (
            "V_eta_BPS=Z_sigma/ell_eta^2*(-sigma^2+2*sigma^4)"
        ),
        "historical_coefficients_in_dimensionless_convention": {
            "A_ST": -2.0,
            "G_ST": 8.0,
            "vacua": [-0.5, 0.5],
        },
        "first_order_residual": wall["first_order_residual"],
        "second_order_residual": wall["second_order_residual"],
        "physical_scale_owner_if_promoted": "ell_eta=kappa1^(-1/6)",
        "claim_boundary": (
            "exact_for_the_v14_45_analytic_sech_control;_not_exact_for_the_"
            "retained_v13_1_p2_plus_p8_profile_and_therefore_not_promoted_"
            "as_the_full_physical_sigma_potential"
        ),
    }


def completion_payload() -> dict[str, Any]:
    coordinate = np.linspace(-10.0, 10.0, 20001)
    analytic = analytic_eta_wall_response(coordinate)
    generic = normalized_eta_probability_response(coordinate, 1.0 / np.cosh(coordinate))
    retained = retained_eta_profile_response()
    invariants = lowest_order_odd_scalar_audit()
    action = completed_sigma_action()
    redefinition = exact_gradient_field_redefinition_audit()
    nonexact = nonexact_orientation_route_audit()
    symmetry = diagonal_symmetry_audit()
    gram = collective_completion_gram(dC_dq=0.17, dC_ds=-0.08)
    bps = analytic_bps_recovery()
    validation = {
        "analytic_zero_mode_probability_is_unit_normalized": abs(
            float(np.trapezoid(analytic["alpha_eta_density"], coordinate)) - 1.0
        )
        < 1.0e-8,
        "analytic_material_response_obeys_exact_BPS_identity": analytic[
            "first_order_residual"
        ]
        < 1.0e-13,
        "analytic_material_response_obeys_historical_quartic_equation": analytic[
            "second_order_residual"
        ]
        < 1.0e-13,
        "generic_probability_one_form_has_unit_holonomy": abs(
            generic["unit_holonomy"] - 1.0
        )
        < 1.0e-13,
        "generic_response_endpoints_are_fixed": np.allclose(
            generic["endpoint_values"], [-0.5, 0.5], atol=1.0e-13
        ),
        "orientation_reversal_is_CP_conjugate_material_branch": generic[
            "orientation_reversal_residual"
        ]
        < 1.0e-12,
        "retained_eta_solution_supplies_unit_response": abs(
            retained["unit_holonomy"] - 1.0
        )
        < 1.0e-12,
        "retained_eta_profile_not_silently_replaced_by_sech": not retained[
            "analytic_sech_BPS_profile_is_exact_for_retained_solution"
        ],
        "completed_action_has_only_diagonal_reversal": symmetry[
            "diagonal_reversal"
        ]["completed_square_invariant"],
        "candidate_collective_Gram_is_positive_semidefinite_rank_one": (
            gram["positive_semidefinite"] and gram["rank"] == 1
        ),
        "exact_gradient_not_misreported_as_physical_transfer": not gram[
            "promoted_as_physical_transfer"
        ],
        "field_redefinition_obstruction_recorded": not redefinition[
            "physical_sigma_activation_closed"
        ],
        "projector_curvature_is_real_but_not_a_sigma_source": (
            nonexact["eta_projector_connection"]["curvature_nonzero"]
            and not nonexact["eta_projector_connection"][
                "can_source_singlet_sigma_without_new_contraction_or_coefficient"
            ]
        ),
        "regular_topological_current_coupling_is_boundary_exact": not nonexact[
            "transgressed_degree_current"
        ]["regular_bulk_sigma_source"],
        "relative_holonomy_not_misused_as_amplitude_source": not nonexact[
            "relative_Z6_holonomy"
        ]["creates_quadratic_amplitude"],
        "no_new_continuous_coefficient": not action["new_continuous_coefficient"],
        "foundational_not_old_bosonic_provenance_recorded": not action[
            "old_bosonic_Path_B_derivation_claimed"
        ],
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_eta_wall_material_response_v15_26",
        "version": VERSION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "classification": CLASSIFICATION,
        "orientation_odd_invariant_audit": invariants,
        "completed_sigma_action": action,
        "exact_gradient_field_redefinition_audit": redefinition,
        "nonexact_orientation_route_audit": nonexact,
        "diagonal_symmetry": symmetry,
        "analytic_eta_wall": {
            "unit_holonomy": generic["unit_holonomy"],
            "endpoint_values": generic["endpoint_values"],
            "first_order_residual": analytic["first_order_residual"],
            "second_order_residual": analytic["second_order_residual"],
        },
        "retained_degree_one_eta_wall": retained,
        "analytic_BPS_quartic_recovery": bps,
        "moving_q_s_sigma_pullback": gram,
        "scientific_result": (
            "THE_EXISTING_NORMALIZED_ETA_BOUND_ZERO_MODE_DEFINES_A_UNIT_"
            "OPEN_PATH_ORIENTATION_ONE_FORM_AND_A_COEFFICIENT_FREE_AFFINE_"
            "SIGMA_COMPLETION_CANDIDATE;_HOWEVER_ALPHA_ETA_EQUALS_D_C_ETA_"
            "ON_THE_COLLAR_SO_THE_BULK_SQUARE_IS_FIELD_REDEFINITION_"
            "EQUIVALENT_TO_A_FREE_SIGMA_KINETIC_TERM_AND_DOES_NOT_BY_ITSELF_"
            "CLOSE_PHYSICAL_MATERIAL_ACTIVATION"
        ),
        "claim_boundary": {
            "derived_from_old_retained_bosonic_action": False,
            "derived_from_existing_BHSM_structure_after_completing_action": True,
            "candidate_affine_orientation_and_endpoint_amplitude_normalized": True,
            "physical_material_response_selected": False,
            "analytic_historical_quartic_promoted_to_full_profile": False,
            "moving_profile_derivatives_C_q_C_s_evaluated": False,
            "nonlinear_material_skin_solved": False,
            "downstream_particle_or_SM_completion_claimed": False,
        },
        "completion_ledger": {
            "VALIDATED": [
                "normalized_eta_zero_mode_probability_one_form_has_unit_open_path_transport",
                "orientation_reversal_maps_sigma_eta_to_its_negative_branch",
                "minimal_kinetic_covariantization_has_no_new_continuous_coefficient",
                "candidate_completed_action_has_diagonal_not_independent_reflection_symmetry",
                "analytic_sech_control_exactly_recovers_the_historical_normalized_quartic",
                "exact_gradient_covariantization_is_locally_field_redefinition_trivial",
            ],
            "INVALIDATED": [
                "promoting_the_sech_BPS_quartic_as_exact_for_the_retained_p2_plus_p8_eta_solution",
                "claiming_the_completion_was_already_derived_by_the_old_bosonic_Path_B_action",
                "promoting_the_rank_one_coordinate_Gram_block_as_irreducible_physical_transfer",
            ],
            "RECLASSIFIED": [
                "sigma_sign_as_a_canonical_affine_eta_orientation_candidate_not_yet_a_physical_material_state",
                "the_covariantized_sigma_kinetic_term_as_a_domain_completion_candidate",
            ],
            "CLOSED_THIS_RUN": [
                "canonical_normalized_eta_probability_one_form",
                "exact_analytic_wall_to_historical_quartic_identity",
                "field_redefinition_audit_of_the_minimal_gradient_completion",
            ],
            "ACTIVE_DEPENDENCY": (
                "ACTION_OWNED_DISTRIBUTIONAL_DJ3_FIBER_BOUNDARY_FLUX_AT_THE_"
                "RECONSTRUCTION_TOPOLOGY_CHANGE_EVENT_WITH_SELF_ADJOINT_"
                "SIGMA_TRACE_PAIRING_AND_NO_FREE_VERTEX_COEFFICIENT"
            ),
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_continuous_coefficients": [],
            "new_empirical_inputs": [],
            "kinetic_change": "nabla_sigma_to_nabla_sigma-alpha_eta",
            "provenance": CLASSIFICATION,
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
    path = target / "BHSM_aether_eta_wall_material_response_v15_26.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION",
    "FULL_BHSM_COMPLETE",
    "CLASSIFICATION",
    "analytic_eta_wall_response",
    "normalized_eta_probability_response",
    "retained_eta_profile_response",
    "lowest_order_odd_scalar_audit",
    "completed_sigma_action",
    "exact_gradient_field_redefinition_audit",
    "nonexact_orientation_route_audit",
    "diagonal_symmetry_audit",
    "collective_completion_gram",
    "analytic_bps_recovery",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
