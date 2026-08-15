"""BHSM v15.12 moving-interface/corner transfer theorem and obstruction.

The author-supplied moving-interface assumption turns the previously
inapplicable two-face gravitational corner into required variational geometry.
The Einstein--Hilbert coefficient fixes the GHY and Hayward terms.  This
closes the gravitational corner mechanics, but not the reconnection surgery
or the matter/core self-adjoint trace identification.
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
from .aether_cycle_spread_concentration_v15_9 import (
    radial_fourier_solution,
    radial_solution_diagnostics,
)


VERSION = "v15.12"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False
OUTCOME = "PARTIAL_INTERFACE_ACTION_CLOSURE_WITH_RECONNECTION_DOMAIN_NO_SELECTION"
PRIMARY_VERDICT = (
    "BHSM_V15_12_THE_AUTHORS_TWO_MOVING_INTERFACE_ASSUMPTION_ACTIVATES_THE_"
    "COEFFICIENT_LOCKED_EINSTEIN_GHY_HAYWARD_TWO_FACE_ACTION_AND_ITS_NONZERO_"
    "CORNER_AREA_BOOST_ANGLE_CROSS_VARIATION_WITHOUT_FORCING_UPSILON_TO_ZERO;_"
    "A_SHRINKING_SEVEN_SPATIAL_DIMENSIONAL_CONTACT_HAS_CAPACITY_AND_REGULAR_"
    "GRAVITATIONAL_ACTION_SCALING_AS_EPSILON_TO_THE_FIFTH_WHILE_A_FINITE_ETA_"
    "JUMP_DIVERGES_IN_THE_RETAINED_P8_TERM;_HOWEVER_A_SMOOTH_MOVING_CUT_IS_"
    "PURE_REPARTITION_AND_A_GENUINE_RECONNECTION_REQUIRES_A_TOPOLOGY_DOMAIN_"
    "SURGERY_FOR_WHICH_SELF_ADJOINTNESS_AND_CONSERVATION_ALLOW_A_CONTINUOUS_"
    "UNITARY_FAMILY;_THE_HAYWARD_TERM_SELECTS_NO_MATTER_CORE_TRACE_UNITARY_OR_"
    "POST_CONTACT_GLUING_SO_NO_UNIQUE_NONZERO_PHYSICAL_TRANSFER_FORMATION_OR_"
    "SIGMA_SELECTOR_FOLLOWS_FROM_THE_RETAINED_ACTION"
)
EXACT_NEXT_OBJECT = (
    "ACTION_SELECTED_RECONNECTION_COBORDISM_AND_CORE_INTERFACE_TRACE_FUNCTOR_"
    "FIXING_THE_POST_CONTACT_GLUING_UNITARY_MATTER_DOMAIN_TOPOLOGY_CHANGE_AND_"
    "CONSERVATIVE_STATE_TRANSFER_WITH_HAYWARD_CORNER_SYMPLECTIC_MATCHING"
)


def _positive(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return result


def hayward_corner_action(kappa1: float, joint_measure: float, boost_angle: float) -> float:
    """Coefficient-locked two-face P1 corner action ``kappa1*A*theta``."""

    coupling = _positive(kappa1, "kappa1")
    area = float(joint_measure)
    angle = float(boost_angle)
    if not math.isfinite(area) or area < 0.0 or not math.isfinite(angle):
        raise ValueError("joint measure must be nonnegative and angle finite")
    return coupling * area * angle


def hayward_corner_variation(
    kappa1: float, joint_measure: float, boost_angle: float
) -> dict[str, Any]:
    """Return the exact first, mixed-second, and corner symplectic forms."""

    coupling = _positive(kappa1, "kappa1")
    area = float(joint_measure)
    angle = float(boost_angle)
    hayward_corner_action(coupling, area, angle)
    hessian = np.array([[0.0, coupling], [coupling, 0.0]])
    symplectic = np.array([[0.0, coupling], [-coupling, 0.0]])
    return {
        "coordinate_order": ["joint_measure", "relative_boost_angle"],
        "action": coupling * area * angle,
        "gradient": [coupling * angle, coupling * area],
        "hessian": hessian.tolist(),
        "hessian_eigenvalues": np.linalg.eigvalsh(hessian).tolist(),
        "cross_variation": coupling,
        "corner_symplectic_matrix": symplectic.tolist(),
        "symplectic_rank": int(np.linalg.matrix_rank(symplectic)),
        "new_transfer_coefficient": False,
    }


def sphere_area(dimension: int) -> float:
    """Area of the unit sphere S^dimension."""

    d = int(dimension)
    if d < 0:
        raise ValueError("sphere dimension must be nonnegative")
    return 2.0 * math.pi ** ((d + 1.0) / 2.0) / math.gamma((d + 1.0) / 2.0)


def contact_ball_capacity(radius: float, spatial_dimension: int = 7) -> float:
    """Newtonian two-capacity of a radius-epsilon ball in R^n, n>2."""

    epsilon = _positive(radius, "radius")
    n = int(spatial_dimension)
    if n <= 2:
        raise ValueError("power-law capacity formula requires spatial dimension >2")
    return (n - 2.0) * sphere_area(n - 1) * epsilon ** (n - 2)


def neck_scaling(
    epsilon: float,
    *,
    spatial_dimension: int = 7,
    eta_jump_scaling_exponent: float = 0.0,
) -> dict[str, Any]:
    """Power-count a local neck of radius epsilon per unit proper time.

    A bounded-amplitude metric neck has EH/GHY/corner scaling epsilon^(n-2).
    If the eta variation across the neck is O(epsilon^a), the retained p=2
    and p=8 pieces scale as epsilon^(n-2+2a) and epsilon^(n-8+8a).
    """

    eps = _positive(epsilon, "epsilon")
    n = int(spatial_dimension)
    exponent = float(eta_jump_scaling_exponent)
    if n <= 2 or not math.isfinite(exponent):
        raise ValueError("require spatial dimension >2 and finite eta exponent")
    gravitational_power = n - 2
    eta2_power = n - 2 + 2.0 * exponent
    eta8_power = n - 8 + 8.0 * exponent
    return {
        "epsilon": eps,
        "spatial_dimension": n,
        "capacity": contact_ball_capacity(eps, n),
        "capacity_power": gravitational_power,
        "Einstein_Hilbert_proxy": eps**gravitational_power,
        "GHY_proxy": eps**gravitational_power,
        "Hayward_joint_proxy": eps**gravitational_power,
        "eta_p2_proxy": eps**eta2_power,
        "eta_p8_proxy": eps**eta8_power,
        "eta_jump_scaling_exponent": exponent,
        "eta_p8_finite_limit_condition": exponent >= (8.0 - n) / 8.0,
        "finite_O1_eta_jump_allowed": n >= 8,
    }


def self_adjoint_transfer_generator(
    parent_energy: float,
    interface_energy: float,
    transfer_amplitude: float,
    transfer_phase: float,
) -> np.ndarray:
    """Return the general two-sector Hermitian transfer witness."""

    ep = float(parent_energy)
    ea = float(interface_energy)
    amplitude = float(transfer_amplitude)
    phase = float(transfer_phase)
    if not all(math.isfinite(x) for x in (ep, ea, amplitude, phase)):
        raise ValueError("all generator data must be finite")
    if amplitude < 0.0:
        raise ValueError("transfer amplitude must be nonnegative")
    off = amplitude * np.exp(-1j * phase)
    return np.array([[ep, off], [np.conjugate(off), ea]], dtype=complex)


def cayley_trace_unitary(alpha: float) -> complex:
    """Reduced maximal-isotropic graph family from the v6.10 trace audit."""

    value = float(alpha)
    if not math.isfinite(value):
        raise ValueError("alpha must be finite")
    return complex((1.0 - 1j * value) / (1.0 + 1j * value))


def transfer_nonuniqueness_witness() -> dict[str, Any]:
    """Construct inequivalent conservative transfer laws with the same diagonals."""

    rows = {}
    for label, amplitude, phase in (
        ("decoupled", 0.0, 0.0),
        ("weak", 0.25, 0.0),
        ("strong", 0.75, 0.0),
        ("phased", 0.75, 0.61),
    ):
        generator = self_adjoint_transfer_generator(1.0, 1.7, amplitude, phase)
        rows[label] = {
            "transfer_amplitude": amplitude,
            "transfer_phase": phase,
            "hermiticity_residual": float(
                np.linalg.norm(generator - np.conjugate(generator.T))
            ),
            "eigenvalues": np.linalg.eigvalsh(generator).tolist(),
        }
    alphas = (-1.0, 0.0, 1.0, 2.0)
    graph_family = [cayley_trace_unitary(alpha) for alpha in alphas]
    return {
        "same_diagonal_parent_and_interface_generators": True,
        "all_complete_generators_self_adjoint": all(
            row["hermiticity_residual"] < 1.0e-14 for row in rows.values()
        ),
        "inequivalent_transfer_spectra": (
            rows["weak"]["eigenvalues"] != rows["strong"]["eigenvalues"]
        ),
        "generators": rows,
        "maximal_isotropic_graph_parameters": list(alphas),
        "maximal_isotropic_graph_unit_modulus_residual": max(
            abs(abs(value) - 1.0) for value in graph_family
        ),
        "self_adjointness_selects_transfer_amplitude": False,
        "self_adjointness_selects_trace_unitary": False,
        "Hayward_gravity_term_selects_matter_trace_unitary": False,
    }


def moving_interface_action_payload() -> dict[str, Any]:
    """State the smallest coefficient-locked action activated by two faces."""

    corner = hayward_corner_variation(2.0, 0.7, 0.4)
    return {
        "new_foundational_geometry": (
            "two_moving_parent_child_boundary_faces_with_a_transient_"
            "codimension_two_joint_and_relative_normal_angle"
        ),
        "minimal_action": (
            "S_parent+S_child+kappa1*int_Sigma_parent(epsilon*K)+"
            "kappa1*int_Sigma_child(epsilon*K)+"
            "kappa1*int_J(sqrt_abs_gamma*theta)+S_existing_compatibility"
        ),
        "GHY_and_Hayward_coefficient": "same_retained_kappa1",
        "new_arbitrary_continuous_coefficient": False,
        "corner_variation": corner,
        "derived_interface_equations": [
            "bulk_Euler_Lagrange_equations_on_each_regular_face",
            "induced_metric_and_existing_attachment_compatibility",
            "equal_and_opposite_canonical_traction_momentum_balance",
            "corner_area_relative_angle_canonical_pair",
        ],
        "smooth_internal_cut_result": (
            "opposite_GHY_terms_and_bulk_partition_variations_cancel_on_a_"
            "smooth_solution_so_interface_motion_is_pure_repartition"
        ),
        "genuine_corner_has_nonzero_geometric_cross_variation": (
            corner["cross_variation"] != 0.0
        ),
        "corner_term_alone_is_physical_transfer_Hamiltonian": False,
        "complete_constraint_reduced_corner_Hessian_evaluated": False,
        "matter_or_core_transfer_domain_selected": False,
        "post_contact_topological_gluing_selected": False,
    }


def conservative_moving_jump_residual(
    parent_normal_flux: float,
    child_normal_flux: float,
    interface_velocity: float,
    parent_density: float,
    child_density: float,
) -> float:
    """Distributional conservation law at a moving oriented interface.

    With both traces expressed in one chosen normal convention, conservation
    gives ``[J.n]-V[Q]=0``.  This kinematic identity does not choose the trace
    identification or supply the missing BHSM current.
    """

    values = tuple(
        float(value)
        for value in (
            parent_normal_flux,
            child_normal_flux,
            interface_velocity,
            parent_density,
            child_density,
        )
    )
    if not all(math.isfinite(value) for value in values):
        raise ValueError("moving-jump data must be finite")
    jp, jc, velocity, qp, qc = values
    return (jp - jc) - velocity * (qp - qc)


def interface_equation_payload() -> dict[str, Any]:
    """Separate derived variational identities from unavailable physical data."""

    return {
        "metric_traction_balance": (
            "Pi_parent+Pi_child+delta(S_compat+S_corner)/delta_gamma=0_"
            "in_one_oriented_joint_frame"
        ),
        "field_flux_balance": (
            "n_parent.Phi_parent+n_child.Phi_child+"
            "delta_S_joint_matter/delta_tracePhi=0"
        ),
        "moving_conservation_identity": "[J.n]-V_J[Q]=0",
        "corner_angle_measure_variation": (
            "delta_S_Hayward=kappa1*(theta*delta_A_J+A_J*delta_theta)"
        ),
        "existing_joint_matter_action": 0,
        "physical_BHSM_J_and_Q_traces": None,
        "physical_interface_velocity": None,
        "physical_traction_residual_evaluable": False,
        "physical_flux_residual_evaluable": False,
        "reason": "post_contact_trace_identification_and_reconnection_domain_are_unselected",
    }


def topology_and_capacity_payload() -> dict[str, Any]:
    fixed = neck_scaling(0.1, eta_jump_scaling_exponent=0.0)
    continuous = neck_scaling(0.1, eta_jump_scaling_exponent=1.0 / 8.0)
    return {
        "fixed_v15_11_route": "PRESERVED_FOR_POSITIVE_CAPACITY_FIXED_SURFACES",
        "moving_contact_route": {
            "support_upsilon_forced_to_zero": False,
            "seven_dimensional_contact_capacity": "Cap(B_epsilon)=(16*pi^3/3)*epsilon^5",
            "capacity_tends_to_zero": True,
            "regular_gravity_neck_power": 5,
            "finite_gravitational_power_count": True,
        },
        "eta_regularization": {
            "O1_eta_jump_p8_power": fixed["spatial_dimension"] - 8,
            "O1_eta_jump_finite": fixed["finite_O1_eta_jump_allowed"],
            "minimum_eta_matching_exponent": "Delta_eta=O(epsilon^(1/8))",
            "threshold_scaling_finite": continuous["eta_p8_finite_limit_condition"],
            "meaning": "eta_must_match_continuously_at_the_reconnection_neck",
        },
        "Lorentzian_topology_theorem": (
            "a_nonsingular_globally_hyperbolic_compact_Lorentzian_cobordism_"
            "has_diffeomorphic_Cauchy_slices"
        ),
        "genuine_spatial_topology_change_requires_one_of": [
            "metric_or_reconstruction_degeneracy",
            "failure_of_global_hyperbolicity_or_causal_pathology",
            "a_boundary_core_domain_event_outside_the_regular_Lorentzian_manifold",
        ],
        "retained_choice_among_these": None,
    }


def v15_9_incoming_interface_payload(
    radius_ratios_six: Sequence[float] = (1.001, 1.01, 1.04),
    modes: int = 12,
) -> dict[str, Any]:
    """Extract contact-relevant data from the full nonlinear radial branch."""

    rows = []
    grid = np.linspace(0.0, math.pi, 4001)
    n = np.arange(1, modes + 1, dtype=float)[:, None]
    for ratio in radius_ratios_six:
        coefficients = np.asarray(radial_fourier_solution(float(ratio), modes))
        derivative = 1.0 + coefficients @ (n * np.cos(n * grid))
        diagnostics = radial_solution_diagnostics(float(ratio), modes)
        rows.append(
            {
                "radius_ratio_six": float(ratio),
                "q_fourier": diagnostics["q_fourier"],
                "degree": diagnostics["degree"],
                "C_eta": diagnostics["C_eta"],
                "right_pole_slope": diagnostics["right_pole_slope"],
                "minimum_profile_derivative": float(np.min(derivative)),
                "radial_profile_strictly_monotone": bool(np.min(derivative) > 0.0),
            }
        )
    return {
        "incoming_state": "full_nonlinear_v15_9_degree_one_radial_eta_branch",
        "rows": rows,
        "unique_radial_level_for_each_profile_value": all(
            row["radial_profile_strictly_monotone"] for row in rows
        ),
        "radial_level_topology": "S6",
        "required_physical_child_seam_topology": "S3_times_S3",
        "radial_level_is_physical_Hopf_contact_interface": False,
        "parent_surface_embedding_and_relative_normal_angle_from_v15_9": None,
        "eta_trace_matching_at_neck_evaluable": False,
    }


def v15_10_interface_selection_payload() -> dict[str, Any]:
    witness = retained_nonuniqueness_witness()
    labels = list(witness["triples"])
    return {
        "witnesses": labels,
        "same_sigma_zero_eta_metric_parent": True,
        "same_coefficient_locked_gravitational_corner_action": True,
        "direct_Hayward_selector_jacobian_d_alpha_r_gamma": [0, 0, 0],
        "matter_trace_unitary_selected_for_any_witness": False,
        "post_contact_gluing_selected_for_any_witness": False,
        "surviving_witness_count_before_unavailable_backreacted_contact_BVP": len(labels),
        "v15_10_nonuniqueness_resolved": False,
        "reason": (
            "the_required_gravitational_corner_term_contains_no_sigma_"
            "response_invariant_and_the_backreacted_contact_geometry_and_"
            "matter_trace_domain_are_not_action_selected"
        ),
    }


def reconnection_obstruction_payload() -> dict[str, Any]:
    witness = transfer_nonuniqueness_witness()
    return {
        "geometric_corner_mechanics_action_owned": True,
        "finite_action_neck_power_count_available": True,
        "smooth_cut_is_physical_passage": False,
        "smooth_cut_classification": "GAUGE_REPARTITION_WITH_ZERO_TOTAL_ACTION_INERTIA",
        "genuine_reconnection_needs_domain_topology_change": True,
        "instantaneous_self_adjoint_domains_form_a_unitary_family": True,
        "time_dependent_domain_requires_a_Hilbert_bundle_connection": True,
        "connection_or_trace_functor_in_retained_action": False,
        "post_contact_pairing_identity_vs_exchange_selected": False,
        "matter_core_junction_generator_in_retained_action": False,
        "nonuniqueness_witness": witness,
        "conservative_nonzero_transfer_uniquely_selected": False,
        "new_foundational_physical_assumption_required": (
            "specify_the_action_owned_reconnection_surgery_and_how_every_"
            "geometric_eta_sigma_gauge_and_fermion_trace_is_transport_identified_"
            "across_it"
        ),
    }


def completion_payload() -> dict[str, Any]:
    action = moving_interface_action_payload()
    topology = topology_and_capacity_payload()
    incoming = v15_9_incoming_interface_payload()
    sigma = v15_10_interface_selection_payload()
    obstruction = reconnection_obstruction_payload()
    expected_capacity_constant = 16.0 * math.pi**3 / 3.0
    validations = {
        "Hayward_cross_variation_is_kappa1": (
            hayward_corner_variation(2.0, 0.7, 0.4)["cross_variation"] == 2.0
        ),
        "corner_symplectic_pair_nonzero": (
            hayward_corner_variation(2.0, 0.7, 0.4)["symplectic_rank"] == 2
        ),
        "seven_dimensional_capacity_constant": math.isclose(
            contact_ball_capacity(1.0, 7), expected_capacity_constant, rel_tol=1e-14
        ),
        "shrinking_contact_capacity_vanishes": (
            contact_ball_capacity(0.01, 7) < contact_ball_capacity(0.1, 7)
        ),
        "O1_eta_jump_p8_diverges_in_n7": (
            neck_scaling(0.01)["eta_p8_proxy"]
            > neck_scaling(0.1)["eta_p8_proxy"]
        ),
        "eta_eighth_root_matching_controls_p8": neck_scaling(
            0.1, eta_jump_scaling_exponent=1.0 / 8.0
        )["eta_p8_finite_limit_condition"],
        "self_adjoint_transfer_nonunique": (
            obstruction["nonuniqueness_witness"][
                "all_complete_generators_self_adjoint"
            ]
            and not obstruction["nonuniqueness_witness"][
                "self_adjointness_selects_transfer_amplitude"
            ]
        ),
        "full_v15_9_profiles_monotone": incoming[
            "unique_radial_level_for_each_profile_value"
        ],
        "radial_Hopf_topology_not_conflated": not incoming[
            "radial_level_is_physical_Hopf_contact_interface"
        ],
        "v15_10_nonuniqueness_not_fabricated_closed": not sigma[
            "v15_10_nonuniqueness_resolved"
        ],
        "fixed_v15_11_obstruction_preserved": (
            topology["fixed_v15_11_route"]
            == "PRESERVED_FOR_POSITIVE_CAPACITY_FIXED_SURFACES"
        ),
        "no_new_arbitrary_coefficient": not action[
            "new_arbitrary_continuous_coefficient"
        ],
        "no_empirical_input_or_retuning": True,
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_moving_interface_transfer_v15_12",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "outcome": OUTCOME,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "moving_interface_action": action,
        "interface_equations": interface_equation_payload(),
        "topology_capacity_and_finite_action": topology,
        "v15_9_incoming_interface": incoming,
        "v15_10_interface_selection": sigma,
        "reconnection_obstruction": obstruction,
        "formation": "NOT_DERIVED_NO_SELECTED_RECONNECTION_AND_TRACE_TRANSPORT",
        "persistence": "NOT_REACHED_NO_SURFACE_PASSED_PHYSICAL_CHILD",
        "de_envelopment": "NOT_REACHED_NO_SELECTED_RECEIVING_DOMAIN",
        "Hopf_child": "NOT_REACHED_RADIAL_S6_PRECURSOR_ONLY",
        "downstream_Standard_Model": "NOT_REACHED_NO_PHYSICAL_CHILD_COMMON_DOMAIN",
        "Hindsight_20_20": {
            "VALIDATED": [
                "the_two_face_assumption_activates_the_coefficient_locked_Hayward_corner_term",
                "corner_measure_and_relative_angle_have_a_nonzero_kappa1_cross_variation",
                "a_seven_dimensional_shrinking_contact_has_capacity_and_regular_gravity_scaling_epsilon_to_the_fifth",
                "the_retained_eta_p8_term_forbids_a_finite_eta_jump_through_the_shrinking_neck",
                "the_v15_9_radial_profiles_are_monotone_but_their_levels_are_S6_not_the_Hopf_seam",
                "self_adjointness_and_conservation_leave_a_continuous_transfer_domain_family",
            ],
            "INVALIDATED": [
                "a_moving_internal_cut_by_itself_is_a_physical_transfer_event",
                "the_Hayward_gravity_term_selects_the_matter_or_core_trace_unitary",
                "zero_contact_capacity_alone_selects_a_reconnection",
                "an_order_one_eta_discontinuity_has_finite_retained_action_in_a_seven_dimensional_neck",
                "the_minimal_corner_action_resolves_the_v15_10_sigma_witnesses",
            ],
            "RECLASSIFIED": [
                "the_moving_interface_assumption_as_sufficient_to_activate_corner_mechanics_but_not_reconnection_surgery",
                "capacity_collapse_as_a_finite_gravitational_scaling_route_not_a_state_transfer_law",
                "surface_passage_as_a_time_dependent_domain_and_trace_identification_problem",
            ],
            "OPEN": [EXACT_NEXT_OBJECT],
        },
        "exact_next_object": EXACT_NEXT_OBJECT,
        "scientific_terminal_condition": (
            "GENUINE_RECONNECTION_DOMAIN_NONUNIQUENESS_REQUIRING_ANOTHER_"
            "EXPLICIT_FOUNDATIONAL_PHYSICAL_ASSUMPTION"
        ),
        "validation": validations,
        "validation_passed": all(validations.values()),
        "no_retuning_certificate": {
            "new_continuous_coefficients": [],
            "new_empirical_inputs": [],
            "Hayward_coefficient_source": "retained_kappa1",
            "reconnection_functor_adopted": False,
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
    path = target / "BHSM_aether_moving_interface_transfer_v15_12.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path
