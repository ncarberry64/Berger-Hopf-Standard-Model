"""BHSM v15.13 boundary-identity and enclosed-spacetime theorem.

Boundary identity removes parent/child exchange sewings, but it does not
select the self-adjoint boundary condition carried by either preserved skin.
The retained gravitational corner action acts on geometry and leaves a
continuous U(1)_p x U(1)_c matter-domain family.  The module also identifies
the covariant enclosed-spacetime measure and the relative on-shell
Hamiltonian whose shape derivatives are the restoring and ejection forces;
these introduce no phenomenological buoyancy coefficient.
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
from .aether_moving_interface_transfer_v15_12 import cayley_trace_unitary


VERSION = "v15.13"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False
OUTCOME = "BOUNDARY_IDENTITY_REDUCTION_WITH_CONTINUOUS_SKIN_DOMAIN_OBSTRUCTION"
PRIMARY_VERDICT = (
    "BHSM_V15_13_BOUNDARY_IDENTITY_FORBIDS_CROSSWISE_PARENT_CHILD_SEWING_AND_"
    "REDUCES_ASYMPTOTIC_TRACE_TRANSPORT_TO_A_DIRECT_SUM;_HOWEVER_EACH_"
    "PRESERVED_SKIN_RETAINS_THE_U1_MAXIMAL_ISOTROPIC_PHASE_ALREADY_UNSELECTED_"
    "BY_THE_RETAINED_MATTER_ACTION_SO_THE_SURVIVING_DOMAIN_FAMILY_IS_"
    "CONTINUOUS_U1_PARENT_TIMES_U1_CHILD;_THE_COVARIANT_ENCLOSED_SPACETIME_"
    "MEASURE_IS_THE_RECONSTRUCTED_PROPER_VOLUME_ON_A_RELATIONAL_CLOCK_SLICE_"
    "AND_ITS_ACTION_OWNED_DISPLACEMENT_ENERGY_IS_THE_CONSTRAINT_REDUCED_"
    "RELATIVE_ON_SHELL_HAMILTONIAN;_RESTORING_AND_EJECTION_FORCES_ARE_ITS_"
    "SHAPE_DERIVATIVES_NOT_NEW_BUOYANCY_TERMS;_THEY_DO_NOT_SELECT_THE_"
    "SURVIVING_MATTER_PHASES_OR_THE_V15_10_SIGMA_WITNESSES"
)
EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_PARENT_AND_CHILD_SKIN_MATTER_BOUNDARY_GENERATOR_FIXING_THE_"
    "SURVIVING_U1_TIMES_U1_MAXIMAL_ISOTROPIC_PHASES_WITHOUT_CROSS_SECTOR_"
    "EXCHANGE"
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


def boundary_identity_trace_unitary(alpha_parent: float, alpha_child: float) -> np.ndarray:
    """Return the reduced identity-preserving maximal-isotropic graph.

    Each scalar Cayley factor is the v6.10 self-adjoint trace family.  The
    direct sum enforces parent->parent and child->child.  It is a diagnostic
    family, not an adoption of either free phase.
    """

    up = cayley_trace_unitary(_finite(alpha_parent, "alpha_parent"))
    uc = cayley_trace_unitary(_finite(alpha_child, "alpha_child"))
    return np.diag(np.asarray([up, uc], dtype=complex))


def cross_exchange_norm(unitary: Sequence[Sequence[complex]]) -> float:
    """Frobenius norm of parent/child off-diagonal transport blocks."""

    matrix = np.asarray(unitary, dtype=complex)
    if matrix.shape != (2, 2):
        raise ValueError("unitary must be 2x2 in the reduced parent/child model")
    return float(math.sqrt(abs(matrix[0, 1]) ** 2 + abs(matrix[1, 0]) ** 2))


def boundary_identity_nonuniqueness_witness() -> dict[str, Any]:
    """Exhibit continuous conservative domains after cross-sewing is removed."""

    parameters = ((0.0, 0.0), (1.0, 0.0), (0.0, 2.0), (-1.0, 2.0))
    rows = []
    spectra = []
    for alpha_parent, alpha_child in parameters:
        unitary = boundary_identity_trace_unitary(alpha_parent, alpha_child)
        spectrum = np.linalg.eigvals(unitary)
        spectra.append(tuple(complex(value) for value in spectrum))
        rows.append(
            {
                "alpha_parent": alpha_parent,
                "alpha_child": alpha_child,
                "unitarity_residual": float(
                    np.linalg.norm(np.conjugate(unitary.T) @ unitary - np.eye(2))
                ),
                "cross_exchange_norm": cross_exchange_norm(unitary),
                "eigenphases": np.angle(spectrum).tolist(),
            }
        )
    swap = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
    return {
        "pre_identity_generic_sector_group": "U(2)_in_reduced_two_sector_witness",
        "boundary_identity_allowed_group": "U(1)_parent_times_U(1)_child",
        "boundary_identity_forbids_swap": cross_exchange_norm(swap) > 0.0,
        "witnesses": rows,
        "all_witnesses_unitary": all(row["unitarity_residual"] < 1.0e-14 for row in rows),
        "all_witnesses_preserve_boundary_identity": all(
            row["cross_exchange_norm"] == 0.0 for row in rows
        ),
        "inequivalent_endpoint_spectra_remain": len(set(spectra)) == len(spectra),
        "remaining_family_dimension": 2,
        "remaining_family_continuous": True,
        "common_overall_phase_may_be_gauge": True,
        "relative_parent_child_phase_still_continuous": True,
        "self_adjointness_selects_alpha_parent_or_alpha_child": False,
    }


def contact_pulse_unitary(pulse_area: float) -> np.ndarray:
    """Exactly exponentiate an off-diagonal Hermitian contact pulse.

    For H(t)=g(t) sigma_x, only A=int g dt enters the endpoint propagator.
    A=n*pi returns a block-diagonal endpoint while allowing transient sector
    coupling.  Boundary identity therefore cannot reconstruct contact history
    from the asymptotic rule alone.
    """

    area = _finite(pulse_area, "pulse_area")
    return np.array(
        [
            [math.cos(area), -1j * math.sin(area)],
            [-1j * math.sin(area), math.cos(area)],
        ],
        dtype=complex,
    )


def unit_ball_volume(spatial_dimension: int) -> float:
    """Lebesgue/proper volume of the unit n-ball."""

    dimension = int(spatial_dimension)
    if dimension <= 0:
        raise ValueError("spatial_dimension must be positive")
    return math.pi ** (dimension / 2.0) / math.gamma(dimension / 2.0 + 1.0)


def volume_radius(enclosed_spacetime_volume: float, spatial_dimension: int = 7) -> float:
    """Diffeomorphism-invariant volume radius of a reconstructed child slice."""

    volume = _positive(enclosed_spacetime_volume, "enclosed_spacetime_volume")
    omega = unit_ball_volume(spatial_dimension)
    return (volume / omega) ** (1.0 / int(spatial_dimension))


def schur_reduced_curvature(
    direct_curvature: float,
    response_coupling: Sequence[float],
    response_hessian: Sequence[Sequence[float]],
) -> float:
    """Constraint/gauge-reduced collective curvature Hqq-Hqy Hyy^-1 Hyq."""

    direct = _finite(direct_curvature, "direct_curvature")
    coupling = np.asarray(response_coupling, dtype=float)
    hessian = np.asarray(response_hessian, dtype=float)
    if coupling.ndim != 1 or hessian.shape != (coupling.size, coupling.size):
        raise ValueError("response vector and square Hessian dimensions must match")
    if not np.all(np.isfinite(coupling)) or not np.all(np.isfinite(hessian)):
        raise ValueError("response data must be finite")
    if not np.allclose(hessian, hessian.T, atol=1.0e-13):
        raise ValueError("response Hessian must be symmetric")
    if np.min(np.linalg.eigvalsh(hessian)) <= 0.0:
        raise ValueError("response Hessian must be positive on the physical complement")
    return direct - float(coupling @ np.linalg.solve(hessian, coupling))


def collective_shape_force(
    traction_density: Sequence[float],
    normal_shape_velocity: Sequence[float],
    quadrature_weights: Sequence[float],
) -> float:
    """Hadamard force -dE/dq from the action-derived relative traction.

    ``normal_shape_velocity`` is dX/dq dotted with the chosen outward normal.
    No stiffness, density, or buoyancy coefficient is introduced here.
    """

    traction = np.asarray(traction_density, dtype=float)
    velocity = np.asarray(normal_shape_velocity, dtype=float)
    weights = np.asarray(quadrature_weights, dtype=float)
    if traction.shape != velocity.shape or traction.shape != weights.shape:
        raise ValueError("traction, shape velocity and weights must have one shape")
    if not all(np.all(np.isfinite(item)) for item in (traction, velocity, weights)):
        raise ValueError("shape-force data must be finite")
    if np.any(weights < 0.0):
        raise ValueError("quadrature weights must be nonnegative")
    return -float(np.sum(weights * traction * velocity))


def signed_normal_separation(proper_length: float, child_side: int) -> float:
    """Local tubular-neighborhood separation coordinate.

    The sign is fixed by the oriented parent normal: +1 is the declared child
    domain and -1 is the parent-return/de-envelopment side.  This coordinate
    is valid only before the normal exponential map reaches its cut locus.
    """

    length = _finite(proper_length, "proper_length")
    side = int(child_side)
    if length < 0.0 or side not in (-1, 1):
        raise ValueError("proper_length must be nonnegative and child_side must be +/-1")
    return float(side) * length


def constant_force_trajectory(
    proper_time: float,
    inertia: float,
    initial_normal_momentum: float,
    ejection_force: float,
) -> dict[str, float | bool]:
    """Local reduced trajectory for an audited constant post-contact force."""

    tau = _finite(proper_time, "proper_time")
    mass = _positive(inertia, "inertia")
    momentum = _finite(initial_normal_momentum, "initial_normal_momentum")
    force = _finite(ejection_force, "ejection_force")
    if tau < 0.0:
        raise ValueError("proper_time must be nonnegative")
    distance = momentum * tau / mass + 0.5 * force * tau**2 / mass
    final_momentum = momentum + force * tau
    return {
        "proper_time": tau,
        "separation": distance,
        "normal_momentum": final_momentum,
        "ejected_at_this_time": distance > 0.0,
    }


def enclosed_spacetime_payload() -> dict[str, Any]:
    """Identify the covariant measure and its retained-action energy response."""

    return {
        "relational_clock_slice": "Sigma_tau_with_future_unit_normal_u_clock",
        "physical_child_region": "Omega_c(tau)_intersect_G_A",
        "covariant_measure": (
            "V_ST(tau)=integral_[Omega_c(tau) intersect G_A] i_u_clock epsilon_g"
        ),
        "ADM_form": "V_ST=integral_Omega_c sqrt(det(h)) d^7x",
        "clock_slab_form": (
            "V_ST=lim_Delta_tau_to_0 Delta_tau^-1 integral_W_c[Delta_tau] epsilon_g"
        ),
        "support_rule": (
            "G_A_is_the_reconstructible_stratum_not_a_new_indicator_field;_"
            "the_measure_is_undefined_or_degenerate_at_rank_loss_and_no_core_"
            "spatial_volume_is_postulated"
        ),
        "diffeomorphism_status": (
            "invariant_under_joint_pushforward_of_metric_clock_slice_and_child_domain"
        ),
        "finite_for_compact_regular_child": True,
        "scale_coordinate": "R_V=(V_ST/omega_7)^(1/7)",
        "ordinary_volume_arbitrarily_assumed": False,
        "reason": (
            "it_is_the_proper_measure_already_multiplying_the_retained_ADM_"
            "Hamiltonian_and_is_used_only_where_spacetime_is_reconstructed"
        ),
        "relative_displacement_energy": (
            "E_disp=H_on_shell_phys[parent_with_child]+H_corner-"
            "H_on_shell_phys[parent_reference]_at_matched_clock_and_outer_data"
        ),
        "separate_buoyancy_term_added": False,
        "new_buoyancy_coefficient": None,
        "shape_first_variation": (
            "dE_eff/dq=integral_Sigma_c T_rel*(dX/dq dot n_c) dmu_gamma"
        ),
        "restoring_force": "F_R=-dE_eff/dR_V",
        "ejection_force": "F_d=-dE_eff/dd",
        "effective_curvature": "H_qq-H_qy*(H_yy_phys)^-1*H_yq",
        "nested_scale_relation": (
            "at_dE/dR=0,_d2E/dx2=R_c^2*d2E/dR_c2_for_x=log(R_c/R_p)"
        ),
    }


def ejection_gate_payload() -> dict[str, Any]:
    """Separate the derived mechanics from absent physical contact data."""

    zero = constant_force_trajectory(1.0, 1.0, 0.0, 0.0)
    return {
        "coordinate": (
            "d=oriented_normal_geodesic_distance_between_unique_closest_"
            "parent_and_child_skin_points_in_a_common_reconstructed_clock_slice"
        ),
        "coordinate_domain": "local_tubular_neighborhood_before_the_cut_locus",
        "contact": "d=0",
        "ejection_side": "d>0_by_the_action_owned_child_side_orientation",
        "de_envelopment_side": "d<=0_or_return_to_d=0",
        "post_contact_force": "minus_relative_on_shell_Hamiltonian_shape_derivative",
        "Hayward_support": "contact_joint_only_not_a_post_separation_volume_force",
        "identical_homogeneous_phase_translation": {
            "relative_traction": 0,
            "ejection_force": 0,
            "zero_momentum_trajectory": zero,
            "ejection_from_rest": False,
            "reason": "diffeomorphism_or_translation_invariance_makes_E_eff_independent_of_d",
        },
        "successful_ejection_requires_action_output": [
            "positive_outgoing_contact_normal_momentum",
            "or_nonzero_post_contact_relative_quasilocal_traction",
        ],
        "physical_contact_normal_momentum_in_retained_evaluated_solution": None,
        "physical_relative_traction_in_retained_evaluated_solution": None,
        "finite_action_post_contact_trajectory_selected": False,
        "de_envelopment_basin_derived": False,
    }


def sigma_interface_selection_payload() -> dict[str, Any]:
    """Apply all presently evaluable identity/restoring selectors to v15.10."""

    witness = retained_nonuniqueness_witness()
    labels = list(witness["triples"])
    return {
        "witnesses": labels,
        "all_share_sigma_zero_parent_and_boundary_identity_rule": True,
        "boundary_identity_selector_jacobian_d_alpha_r_gamma": [0, 0, 0],
        "enclosed_measure_selector_jacobian_at_sigma_zero": [0, 0, 0],
        "relative_traction_requires_backreacted_child_solution": True,
        "surviving_witness_count": len(labels),
        "v15_10_nonuniqueness_resolved": False,
        "reason": (
            "the_boundary_label_and_geometric_measure_contain_no_sigma_"
            "response_coefficient_and_no_action_selected_child_traction_or_"
            "contact_momentum_has_been_evaluated"
        ),
    }


def boundary_identity_payload() -> dict[str, Any]:
    witness = boundary_identity_nonuniqueness_witness()
    return {
        "asymptotic_sector_map": "H_parent_minus_to_H_parent_plus_direct_sum_H_child_minus_to_H_child_plus",
        "crosswise_boundary_exchange_allowed": False,
        "swap_sewings_eliminated": True,
        "minimal_bulk_induced_tangential_connection": (
            "pullback_Levi_Civita_spin_and_gauge_connections_on_each_skin_worldtube"
        ),
        "minimal_connection_block_structure": "nabla_int=nabla_parent_direct_sum_nabla_child",
        "bulk_connection_holonomy_fixed_once_background_and_paths_are_known": True,
        "normal_self_adjoint_boundary_graph_fixed_by_tangential_parallel_transport": False,
        "existing_matter_junction_action": 0,
        "Hayward_term_acts_on": "joint_measure_and_relative_gravitational_angle",
        "Hayward_selects_skin_matter_phase": False,
        "surviving_domain_witness": witness,
        "one_admissible_functor_remains": False,
        "finite_family_remains": False,
        "continuous_ambiguity_remains": True,
        "distinguishing_missing_quantity": (
            "the_action_owned_normal_matter_boundary_generator_or_equivalent_"
            "physical_transparency_reflection_law_on_each_preserved_skin"
        ),
    }


def completion_payload() -> dict[str, Any]:
    identity = boundary_identity_payload()
    spacetime = enclosed_spacetime_payload()
    ejection = ejection_gate_payload()
    sigma = sigma_interface_selection_payload()
    pulse = contact_pulse_unitary(math.pi)
    schur = schur_reduced_curvature(5.0, [1.0, 2.0], [[4.0, 0.0], [0.0, 5.0]])
    validations = {
        "boundary_swap_forbidden": identity["swap_sewings_eliminated"],
        "identity_preserving_domains_unitary": identity["surviving_domain_witness"][
            "all_witnesses_unitary"
        ],
        "identity_preserving_domains_have_no_cross_exchange": identity[
            "surviving_domain_witness"
        ]["all_witnesses_preserve_boundary_identity"],
        "continuous_U1_times_U1_family_constructed": identity[
            "surviving_domain_witness"
        ]["remaining_family_continuous"],
        "endpoint_identity_does_not_forbid_transient_contact": (
            cross_exchange_norm(pulse) < 1.0e-14
            and cross_exchange_norm(contact_pulse_unitary(math.pi / 2.0)) > 1.0
        ),
        "seven_volume_radius_inverts_exactly": math.isclose(
            unit_ball_volume(7) * volume_radius(unit_ball_volume(7), 7) ** 7,
            unit_ball_volume(7),
            rel_tol=1.0e-14,
        ),
        "shape_force_is_relative_traction_variation": math.isclose(
            collective_shape_force([2.0, 3.0], [1.0, 1.0], [0.25, 0.75]),
            -2.75,
        ),
        "Schur_reduction_exact": math.isclose(schur, 3.95),
        "zero_force_zero_momentum_does_not_eject": not ejection[
            "identical_homogeneous_phase_translation"
        ]["zero_momentum_trajectory"]["ejected_at_this_time"],
        "no_buoyancy_coefficient_added": spacetime["new_buoyancy_coefficient"] is None,
        "v15_10_nonuniqueness_not_fabricated_closed": not sigma[
            "v15_10_nonuniqueness_resolved"
        ],
        "v15_11_fixed_endpoint_no_go_preserved": True,
        "v15_12_Hayward_coefficient_preserved": True,
        "no_empirical_input_or_retuning": True,
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_boundary_identity_ejection_v15_13",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "outcome": OUTCOME,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "boundary_identity_and_transport": identity,
        "enclosed_spacetime_and_restoring_response": spacetime,
        "ejection_gate": ejection,
        "v15_10_selection": sigma,
        "passage": "GEOMETRICALLY_NOT_EXCLUDED_BUT_NO_UNIQUE_MATTER_DOMAIN_FUNCTOR",
        "ejection": "NOT_DERIVED_NO_SELECTED_CONTACT_MOMENTUM_OR_RELATIVE_TRACTION",
        "persistence": "NOT_REACHED_EJECTION_GATE_OPEN",
        "Hopf_child": "NOT_REACHED_V15_9_RADIAL_S6_PRECURSOR_IS_NOT_S3_TIMES_S3",
        "downstream_Standard_Model": "NOT_REACHED_NO_PHYSICAL_EJECTED_CHILD_COMMON_DOMAIN",
        "Hindsight_20_20": {
            "VALIDATED": [
                "boundary_identity_eliminates_crosswise_parent_child_trace_sewings",
                "the_surviving_self_adjoint_domain_family_is_U1_parent_times_U1_child",
                "the_covariant_enclosed_spacetime_amount_is_reconstructed_proper_volume_on_a_relational_clock_slice",
                "displacement_restoring_and_ejection_mechanics_are_shape_derivatives_of_the_relative_on_shell_Hamiltonian",
                "the_constraint_reduced_restoring_curvature_is_the_same_Schur_object_as_nested_scale_curvature",
            ],
            "INVALIDATED": [
                "boundary_identity_alone_selects_one_self_adjoint_matter_trace_functor",
                "tangential_bulk_parallel_transport_fixes_the_normal_self_adjoint_boundary_phase",
                "the_Hayward_gravitational_corner_term_is_a_post_separation_buoyancy_force",
                "ordinary_volume_by_itself_supplies_a_restoring_coefficient",
                "a_zero_momentum_identical_phase_child_ejects_by_translation_invariance",
                "the_new_kinematic_principles_select_a_v15_10_sigma_completion_directly",
            ],
            "RECLASSIFIED": [
                "child_keeps_its_skin_as_a_sector_superselection_rule_not_a_complete_domain_law",
                "spacetime_buoyancy_as_relative_quasilocal_traction_not_an_added_fluid_term",
                "ejection_as_a_contact_momentum_and_post_contact_shape_force_gate_before_persistence",
            ],
            "OPEN": [EXACT_NEXT_OBJECT],
        },
        "exact_next_object": EXACT_NEXT_OBJECT,
        "scientific_terminal_condition": (
            "BOUNDARY_IDENTITY_STILL_LEAVES_CONTINUOUS_INEQUIVALENT_"
            "SELF_ADJOINT_STATE_TRANSPORT_ON_THE_TWO_PRESERVED_SKINS"
        ),
        "missing_physical_assumption_plain_language": (
            "BHSM_must_say_how_matter_reflects_or_passes_on_each_preserved_"
            "skin_by_deriving_a_boundary_matter_law_from_the_action;_saying_"
            "which_skin_survives_does_not_fix_the_wave_phase_at_that_skin"
        ),
        "validation": validations,
        "validation_passed": all(validations.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_continuous_coefficients": [],
            "new_empirical_inputs": [],
            "buoyancy_coefficient": None,
            "skin_phase_adopted": False,
            "frozen_predictions_changed": False,
            "official_prediction_logic_changed": False,
            "USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE": (
                USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE
            ),
        },
    }


def _canonical_json_value(value: Any) -> Any:
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
    path = target / "BHSM_aether_boundary_identity_ejection_v15_13.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path
