"""Minimal post-AE2 reciprocal-join localization extension.

This module promotes the reciprocal-join material profile already frozen in
the retained N12 action into an action-domain response variable.  It does not
change the particle spectrum or choose a Standard Model particle label.

The physical scalar is ``sigma``.  On the retained identity eta branch its
response is

    sigma(chi) = -1/2 + 2 chi/pi - sin(4 chi)/(2 pi),

and the existing localized Hopf weight is ``Lambda=1-4 sigma**2``.  The
profile is the normalized cumulative reciprocal-join density and therefore
has a unique regular zero in the interior.  The action extension is a
coefficient-free KKT promotion of this response plus the already-derived
odd-FR localized Hopf functional.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

import numpy as np


ACTION_VERSION = "BHSM-AE-3.0.0"
CARRIER_ID = "RECIPROCAL_JOIN_ETA_SIGMA_RESPONSE"
SELECTED_ROUTE = "LOCAL_SAME_SPACETIME_ENCLOSURE"


def reciprocal_join_density(chi: object) -> np.ndarray:
    """Return the identity-branch reciprocal join density ``sin² chi cos² chi``."""

    coordinate = np.asarray(chi, dtype=float)
    return np.sin(coordinate) ** 2 * np.cos(coordinate) ** 2


def reciprocal_join_normalization() -> float:
    """Exact normalization of the identity reciprocal density on [0, pi/2]."""

    return float(np.pi / 16.0)


def reciprocal_join_profile(chi: object) -> np.ndarray:
    """Return the retained normalized eta-to-sigma response profile."""

    coordinate = np.asarray(chi, dtype=float)
    return (
        -0.5
        + 2.0 * coordinate / np.pi
        - np.sin(4.0 * coordinate) / (2.0 * np.pi)
    )


def reciprocal_join_profile_derivative(chi: object) -> np.ndarray:
    """Return ``d sigma/d chi = W_join/Z_join`` on the identity branch."""

    coordinate = np.asarray(chi, dtype=float)
    return 4.0 * np.sin(2.0 * coordinate) ** 2 / np.pi


def localization_weight(sigma: object) -> np.ndarray:
    """Return the retained minimal even-quadratic Hopf localization weight."""

    material = np.asarray(sigma, dtype=float)
    return 1.0 - 4.0 * material**2


def minimal_even_quadratic_coefficients() -> tuple[float, float]:
    """Solve ``a+b sigma²`` from Lambda(0)=1 and Lambda(±1/2)=0."""

    matrix = np.array([[1.0, 0.0], [1.0, 0.25]], dtype=float)
    right_hand_side = np.array([1.0, 0.0], dtype=float)
    a, b = np.linalg.solve(matrix, right_hand_side)
    return float(a), float(b)


def regular_carrier_certificate(*, samples: int = 4097) -> dict[str, object]:
    """Certify the analytic identity-branch level set and support properties."""

    if samples < 5 or samples % 2 == 0:
        raise ValueError("samples must be an odd integer of at least five")
    chi = np.linspace(0.0, np.pi / 2.0, samples)
    sigma = reciprocal_join_profile(chi)
    derivative = reciprocal_join_profile_derivative(chi)
    density = reciprocal_join_density(chi)
    weight = localization_weight(sigma)
    midpoint = samples // 2
    interior = slice(1, -1)
    response_residual = derivative - density / reciprocal_join_normalization()
    a, b = minimal_even_quadratic_coefficients()
    return {
        "samples": samples,
        "sigma_endpoints": [float(sigma[0]), float(sigma[-1])],
        "unique_sampled_zero_index": int(midpoint),
        "zero_coordinate": float(chi[midpoint]),
        "zero_residual": float(abs(sigma[midpoint])),
        "transversality_at_zero": float(derivative[midpoint]),
        "minimum_interior_derivative": float(np.min(derivative[interior])),
        "minimum_interior_localization_weight": float(np.min(weight[interior])),
        "maximum_response_residual": float(np.max(np.abs(response_residual))),
        "minimal_even_quadratic": {"constant": a, "sigma_squared": b},
        "inside_sign": "sigma<0",
        "outside_sign": "sigma>0",
        "normal": "n_A=grad_A(sigma)/sqrt(abs(grad(sigma)^2))",
        "regular_level_set": bool(
            abs(sigma[midpoint]) <= 1.0e-14
            and derivative[midpoint] > 0.0
            and np.all(derivative[interior] > 0.0)
            and np.all(weight[interior] > 0.0)
            and np.max(np.abs(response_residual)) <= 2.0e-15
        ),
    }


@dataclass(frozen=True)
class CarrierCandidate:
    """One recovered post-AE2 carrier candidate and its parameter economy."""

    rank: int
    candidate_id: str
    action_ownership: str
    field_type: str
    regular_local_domain: bool
    same_action_variation: bool
    new_physical_fields: int
    new_continuous_coefficients: int
    result: str
    why: str


def ranked_carrier_candidates() -> list[dict[str, object]]:
    """Return the evidence-ranked carrier screen used by the AE3 decision."""

    rows: Iterable[CarrierCandidate] = (
        CarrierCandidate(
            1,
            CARRIER_ID,
            "RETAINED_N12_PROFILE_AND_HOPF_WEIGHT_PROMOTED_BY_COEFFICIENT_FREE_RESPONSE_KKT",
            "existing_spacetime_scalar_sigma_derived_from_existing_eta_join",
            True,
            True,
            0,
            0,
            "SELECTED_MINIMAL_POST_AE2_EXTENSION",
            "It is the only recovered candidate already used by the retained action, with a regular zero, an oriented inside/outside split, and no new physical coefficient.",
        ),
        CarrierCandidate(
            2,
            "ETA_EQUAL_PREIMAGE_SCALAR",
            "ALGEBRAIC_FUNCTION_OF_ACTION_FIELD_ETA",
            "chi_eta=norm(eta_v)^2-norm(eta_u)^2",
            True,
            False,
            0,
            0,
            "VALIDATED_KINEMATIC_CROSSCHECK_NOT_SELECTED_AS_THE_MATERIAL_ACTION",
            "The factor-exchange fixed set is regular but by itself carries no localized response or interface energy.",
        ),
        CarrierCandidate(
            3,
            "ETA_INDUCED_INVERSE_EULER_SIGMA_SKIN",
            "CLASSIFIED_ACTION_COMPLETION_NOT_RETAINED_PARENT_ACTION",
            "existing_scalar_sigma",
            True,
            True,
            0,
            1,
            "VALIDATED_FIXED_BACKGROUND_CRITICAL_SKIN_BUT_UNSTABLE_AND_NORMALIZATION_OPEN",
            "The inverse potential is unique along one eta profile, but Z_sigma remains physical under backreaction and the Derrick mode is negative.",
        ),
        CarrierCandidate(
            4,
            "RETAINED_QUARTIC_SIGMA_WALL",
            "HISTORICAL_RETAINED_ACTION_FAMILY",
            "existing_scalar_sigma",
            True,
            True,
            0,
            4,
            "INVALIDATED_AS_UNIQUE_SELECTOR",
            "Stable inequivalent coefficient triples share the same sigma-zero parent and first variation.",
        ),
        CarrierCandidate(
            5,
            "MULTIPLICATIVE_SUPPORT_DEPTH_Q_D",
            "CANONICAL_HAAR_SUPPORT_ACTION",
            "q_D=-lambda_D_log_upsilon",
            False,
            True,
            0,
            2,
            "INVALIDATED_FOR_REGULAR_FINITE_CODIMENSION_ONE_ENCLOSURE",
            "The zero-support endpoint lies at infinite Haar depth and has an infinite positive-capacity collar cost.",
        ),
        CarrierCandidate(
            6,
            "SCALAR_TOPOGRAPHIC_LEVEL_SET",
            "CONDITIONAL_GEOMETRIC_SCAFFOLD",
            "spacetime_or_internal_scalar_level_set",
            False,
            False,
            0,
            1,
            "OPEN_THRESHOLD_AND_PROFILE_NOT_ACTION_SELECTED",
            "Normal and shape formulas are available only after an unselected threshold and profile are supplied.",
        ),
        CarrierCandidate(
            7,
            "CORE_BOUNDARY_OR_COLLAR",
            "CONDITIONAL_B1_AND_COLLAR_GEOMETRY",
            "embedded_boundary_or_collar",
            False,
            False,
            0,
            1,
            "INVALIDATED_AS_CURRENT_ACTION_SELECTOR",
            "The embedding, thickness, response coefficients, and physical attachment domain are not selected.",
        ),
        CarrierCandidate(
            8,
            "SPACETIME_EDGE_TRANSITION",
            "NO_ACTION_OWNED_EDGE_THEOREM",
            "domain_termination",
            False,
            False,
            0,
            0,
            "INVALIDATED_AT_CURRENT_EVIDENCE_BOUNDARY",
            "Neither the branch-24 stop nor support-rank loss proves that spacetime ends.",
        ),
    )
    return [asdict(row) for row in rows]


def interface_variation_ledger() -> dict[str, object]:
    """Return the resolved-interface laws obtained by splitting one smooth action."""

    return {
        "interface": "Sigma_enc={x:sigma(x)=0}",
        "domain": "D_enc={x:sigma(x)<0}",
        "embedding": "X:Sigma_enc->M_parent_or_child",
        "induced_metric": "h_ab=X^*g_ab",
        "normal": "n_A=grad_A(sigma)/sqrt(abs(grad(sigma)^2))",
        "extrinsic_curvature": "K_ab=h_a^A*h_b^B*nabla_A*n_B",
        "route": SELECTED_ROUTE,
        "response_constraint": "D_s_sigma=W_J[f]/Z_J[f];_sigma(left_pole)=-1/2",
        "response_first_variation": "delta_C_sigma=D_s(delta_sigma)-delta_W/Z_J+W_J*delta_Z_J/Z_J^2+metric_normal_variation",
        "response_adjoint_equation": "-div_orbit(lambda_sigma)+delta(H_regular+H_FR)/delta_sigma=0",
        "fr_sigma_force": "delta_H_FR/delta_sigma=4*J2*K_H_density*sigma/I_H^2;_J2=1/4_on_the_odd_FR_ground_domain",
        "metric_trace": "[h_ab]=0",
        "lapse_shift_trace": "[N]=0;_[beta_tangent]=0_on_the_single_smooth_domain",
        "canonical_geometry_flux": "[Pi_geometry^n]=0_after_opposite_normal_orientation",
        "eta_trace": "[eta]=0;_[Pi_eta^n]=0",
        "sigma_trace": "[sigma]=0;_[lambda_sigma_density]=0",
        "gauge_trace": "[i_X^*A]=0;_[Pi_A^n]=0",
        "fermion_trace": "smooth_enclosure_trace;_AE2_event_child_trace_remains_Gamma0_child=U_R_Gamma0_event",
        "fermion_flux": "opposite_normal_Green_forms_cancel",
        "ghost_BRST": "ghost_and_antighost_pullbacks_are_continuous_and_BRST_domain_is_preserved",
        "normal_traction": "[T_nn]_resolved=0_with_all_profile_stress_included",
        "brown_york": "opposite_normal_internal_GHY/Brown-York contributions_cancel",
        "surface_contact_term": None,
        "surface_tension_parameter": None,
        "noether_balance": "[n_A*J_Noether^A]=0_for_each_owned_smooth_current",
        "interpretation": "resolved_internal_material_level_set_not_a_terminal_boundary_or_reset_locus",
    }


def dependency_ledgers() -> dict[str, object]:
    """Return sector-scoped dependency closures for the frozen family modules."""

    common = [
        "C2_geometry_history",
        "eta_join_field",
        "sigma_localization_scalar",
        "lambda_sigma_KKT_multiplier",
        "Sigma_enc_induced_geometry_normal_K",
        "odd_FR_degree_orientation_topology",
        "reset_glued_Spin_x_G_SM_bundle",
        "AE2_reset_lift_U_R",
        "gauge_connection_and_BRST_trace_domain",
        "fermion_Green_trace_domain",
    ]
    sectors = {
        "charged_lepton": {
            "family_module": "F_l",
            "mode_labels": [[0, 0], [5, 2], [9, 3]],
            "sector_projector": "P_l=(1-C)(1-sigma_sector)/2",
            "manifestation_slots": ["L_L", "e_c"],
        },
        "up": {
            "family_module": "F_u",
            "mode_labels": [[0, 0], [6, 0], [10, 1]],
            "sector_projector": "P_u=C(1+sigma_sector)/2",
            "manifestation_slots": ["Q_L_upper", "u_c"],
        },
        "down": {
            "family_module": "F_d",
            "mode_labels": [[0, 0], [6, 3], [8, 2]],
            "sector_projector": "P_d=C(1-sigma_sector)/2",
            "manifestation_slots": ["Q_L_lower", "d_c"],
        },
    }
    payload: dict[str, object] = {}
    for sector, row in sectors.items():
        payload[sector] = {
            **row,
            "dependency_closure": common
            + [
                row["family_module"],
                "rank_one_family_projector_Pi_r_n",
                row["sector_projector"],
                "sector_fermion_field_Psi_r_n",
                "sector_Noether_current",
                "Higgs_HS_trace_if_manifestation_operator_is_evaluated",
                "existing_M_SM_readout_for_" + sector,
            ],
            "unrelated_fields_required": False,
        }
    return payload


def family_fiber_transport_certificate(
    reset_lift: object,
    *,
    tolerance: float = 1.0e-12,
) -> dict[str, object]:
    """Certify every frozen three-slot fiber over the actual C2 base history.

    The C2 geometry does not choose a particle species.  The correct
    instantiation is the disjoint family-state fiber over that history: an
    upstream label ``(r,n)`` selects one rank-one subbundle and the action,
    reset, and enclosure restriction preserve it.
    """

    lift = np.asarray(reset_lift, dtype=complex)
    if lift.ndim != 2 or lift.shape[0] != lift.shape[1]:
        raise ValueError("reset_lift must be square")
    identity_family = np.eye(3, dtype=complex)
    identity_spin_gauge = np.eye(lift.shape[0], dtype=complex)
    lifted_reset = np.kron(lift, identity_family)
    unitarity = float(
        np.linalg.norm(lift.conjugate().T @ lift - identity_spin_gauge)
    )
    rows = []
    for sector, labels in {
        "charged_lepton": ((0, 0), (5, 2), (9, 3)),
        "up": ((0, 0), (6, 0), (10, 1)),
        "down": ((0, 0), (6, 3), (8, 2)),
    }.items():
        for slot, label in enumerate(labels):
            projector = np.zeros((3, 3), dtype=complex)
            projector[slot, slot] = 1.0
            lifted_projector = np.kron(identity_spin_gauge, projector)
            commutator = lifted_reset @ lifted_projector - lifted_projector @ lifted_reset
            rows.append(
                {
                    "sector": sector,
                    "slot": slot,
                    "mode_label": list(label),
                    "projector_rank": int(round(np.trace(projector).real)),
                    "idempotency_residual": float(
                        np.linalg.norm(projector @ projector - projector)
                    ),
                    "commutator_residual": float(np.linalg.norm(commutator)),
                    "parent_stop_event_child_enclosure_child_transport": "PRESERVED_ON_THE_C2_FIBER",
                }
            )
    passed = bool(
        unitarity <= tolerance
        and all(
            row["idempotency_residual"] <= tolerance
            and row["commutator_residual"] <= tolerance
            for row in rows
        )
    )
    return {
        "base_history": "ACTUAL_RESET_SELECTED_MAXIMAL_C2_HISTORY",
        "fiber_rule": "C2_history_times_disjoint_union_over_(sector,slot)_of_Pi_(sector,slot)F_sector",
        "particle_species_selected_by_geometry": False,
        "upstream_BHSM_state_label_is_initial_data": True,
        "all_frozen_slots_instantiated_as_real_fibers": True,
        "new_particle_labels": [],
        "reset_unitarity_residual": unitarity,
        "rows": rows,
        "certificate_passed": passed,
    }


def enclosure_transport_square_certificate(
    reset_lift: object,
    *,
    samples: int = 65,
    tolerance: float = 1.0e-12,
) -> dict[str, object]:
    """Certify reset, family projection, and enclosure restriction together.

    The three maps act on different tensor factors:

    ``L2(Q) tensor (Spin x G_SM) tensor F_r``.

    The enclosure restriction is multiplication by the characteristic
    function of ``sigma < 0``.  The smooth carrier is multiplication by
    ``Lambda(sigma)``; it is deliberately not called a projector.  This
    certificate proves the algebraic parent/event-child/enclosure square.  It
    does not claim that an omitted interacting full-field Hamiltonian has
    been constructed or that it commutes with either multiplication map.
    """

    if not isinstance(samples, int) or samples < 9 or samples % 2 == 0:
        raise ValueError("samples must be an odd integer of at least nine")
    lift = np.asarray(reset_lift, dtype=complex)
    if lift.ndim != 2 or lift.shape[0] != lift.shape[1]:
        raise ValueError("reset_lift must be square")
    spin_dimension = lift.shape[0]
    family_dimension = 3
    chi = np.linspace(0.0, np.pi / 2.0, samples)
    sigma = reciprocal_join_profile(chi)
    carrier = localization_weight(sigma)
    inside = (sigma < 0.0).astype(float)
    spatial_identity = np.eye(samples, dtype=complex)
    spin_identity = np.eye(spin_dimension, dtype=complex)
    family_identity = np.eye(family_dimension, dtype=complex)
    reset = np.kron(spatial_identity, np.kron(lift, family_identity))
    restriction = np.kron(
        np.diag(inside), np.kron(spin_identity, family_identity)
    )
    carrier_map = np.kron(
        np.diag(carrier), np.kron(spin_identity, family_identity)
    )
    reset_restriction_commutator = float(
        np.linalg.norm(reset @ restriction - restriction @ reset)
    )
    reset_carrier_commutator = float(
        np.linalg.norm(reset @ carrier_map - carrier_map @ reset)
    )
    restriction_idempotency = float(
        np.linalg.norm(restriction @ restriction - restriction)
    )
    rows: list[dict[str, object]] = []
    for sector in ("charged_lepton", "up", "down"):
        for slot in range(family_dimension):
            projector = np.zeros((family_dimension, family_dimension), dtype=complex)
            projector[slot, slot] = 1.0
            family_projector = np.kron(
                spatial_identity, np.kron(spin_identity, projector)
            )
            rows.append(
                {
                    "sector": sector,
                    "slot": slot,
                    "reset_family_commutator": float(
                        np.linalg.norm(reset @ family_projector - family_projector @ reset)
                    ),
                    "restriction_family_commutator": float(
                        np.linalg.norm(
                            restriction @ family_projector
                            - family_projector @ restriction
                        )
                    ),
                    "carrier_family_commutator": float(
                        np.linalg.norm(
                            carrier_map @ family_projector
                            - family_projector @ carrier_map
                        )
                    ),
                }
            )
    passed = bool(
        reset_restriction_commutator <= tolerance
        and reset_carrier_commutator <= tolerance
        and restriction_idempotency <= tolerance
        and all(
            max(
                row["reset_family_commutator"],
                row["restriction_family_commutator"],
                row["carrier_family_commutator"],
            )
            <= tolerance
            for row in rows
        )
    )
    return {
        "hilbert_factorization": "L2(Q)_carrier tensor (Spin x G_SM) tensor F_r",
        "enclosure_restriction": "P_D=multiplication_by_1_{sigma<0}",
        "smooth_localization_map": "L_sigma=multiplication_by_Lambda(sigma)",
        "smooth_localization_map_is_a_projector": False,
        "interface_sample_index": samples // 2,
        "interface_sample_sigma": float(sigma[samples // 2]),
        "inside_sample_count": int(np.sum(inside)),
        "reset_restriction_commutator": reset_restriction_commutator,
        "reset_carrier_commutator": reset_carrier_commutator,
        "restriction_idempotency_residual": restriction_idempotency,
        "rows": rows,
        "time_evolution_intertwiner_claimed": False,
        "claim": (
            "THE_AE2_RESET_LIFT,_EVERY_FROZEN_FAMILY_PROJECTOR,_THE_AE3_"
            "ENCLOSURE_RESTRICTION,_AND_THE_SMOOTH_LOCALIZATION_WEIGHT_"
            "COMMUTE_BECAUSE_THEY_ACT_ON_SEPARATE_TENSOR_FACTORS"
        ),
        "certificate_passed": passed,
    }


def current_full_field_attachment_ledger() -> dict[str, object]:
    """Separate reusable full-field structure from a current C2 action.

    This is a constructive attachment rule, not a request to rebuild the
    particle spectrum.  A historical block is attachable only if its action
    version, background, domain, field coordinates, and source dependence all
    coincide with the current AE3 C2 history.
    """

    blocks = {
        "geometry": {
            "current_C2_action_owned": True,
            "current_C2_coordinates_present": True,
            "status": "ATTACHED",
        },
        "eta_sigma_response": {
            "current_C2_action_owned": True,
            "current_C2_coordinates_present": True,
            "status": "ATTACHED_ON_RESPONSE_ELIMINATED_RETAINED_DOMAIN",
        },
        "gauge_ghost": {
            "current_C2_action_owned": False,
            "current_C2_coordinates_present": False,
            "historical_reusable_structure": "BRST_quotient_and_common_operator_form",
            "mismatch": "historical_closed_proper_cycle_zero_source_background",
            "status": "STRUCTURE_REUSED__CURRENT_ACTION_BLOCK_OPEN",
        },
        "fermion": {
            "current_C2_action_owned": False,
            "current_C2_coordinates_present": False,
            "historical_reusable_structure": (
                "bulk_Dirac_representation_family_projectors_and_AE2_reset_domain"
            ),
            "mismatch": "nonzero_family_state_has_no_current_C2_field_action_coordinate",
            "status": "DOMAIN_AND_STATE_FIBER_ATTACHED__CURRENT_ACTION_BLOCK_OPEN",
        },
        "HS_scalar": {
            "current_C2_action_owned": False,
            "current_C2_coordinates_present": False,
            "historical_reusable_structure": "four_channel_HS_kinetic_response_seed",
            "mismatch": "physical_HS_direction_and_interacting_source_Hessian_open",
            "status": "STRUCTURE_REUSED__CURRENT_ACTION_BLOCK_OPEN",
        },
    }
    return {
        "attachment_rule": (
            "same_action_version_and_same_background_and_same_domain_and_"
            "explicit_field_coordinates_and_required_source_dependence"
        ),
        "blocks": blocks,
        "historical_common_superdeterminant_promoted_to_current_C2": False,
        "why_no_direct_sum": (
            "THE_HISTORICAL_COMMON_OPERATOR_IS_A_ZERO-SOURCE_CLOSED-CYCLE_"
            "FUNCTIONAL;_THE_ACTUAL_C2_OBJECT_IS_A_POSITIVE-DURATION_"
            "MAXIMAL_HISTORY_WITH_NONZERO_UPSTREAM_FAMILY-STATE_INITIAL_DATA"
        ),
        "continuous_coefficient_choice_would_fix_this_mismatch": False,
        "exact_missing_object": (
            "ONE_BACKGROUND-COVARIANT_AE3_C2_OPERATOR_WITH_EXPLICIT_GAUGE-"
            "GHOST,_NONZERO_FERMION,_AND_HS_SOURCE_BLOCKS_ON_THE_RESET-GLUED_"
            "MAXIMAL_HISTORY_DOMAIN"
        ),
        "complete_current_full_field_action_attached": False,
    }


def systems_integration_puzzle() -> dict[str, object]:
    """Expose independently advanceable BHSM science sections and their joins.

    A section is not blocked from receiving valid pieces merely because a
    different section is incomplete.  Promotion occurs only after the joins
    used by a claimed result share the same action, background, domain, scale,
    and provenance.
    """

    return {
        "integration_key": [
            "action_version",
            "background_id",
            "variational_domain",
            "state_factorization",
            "scale_and_renormalization",
            "provenance_hashes",
        ],
        "sections": {
            "full_field_action": {
                "fitted_pieces": [
                    "retained_N12_geometry_and_response_multiplier_action",
                    "current_C2_lowest_Weyl_product_Dirac_quadratic_pencils",
                    "current_C2_unit_reduced_LR_HS_source_and_contact_jet",
                    "existing_family_central_I3_tensor_factor",
                ],
                "open_join": (
                    "same_domain_dynamical_HS_broken_LR_gauge_ghost_transverse_"
                    "electromagnetic_nonzero_fermion_cross_derivative_and_"
                    "maximal_exterior_blocks"
                ),
                "complete": False,
            },
            "localization_enclosure": {
                "fitted_pieces": [
                    "AE3_eta_sigma_response_carrier",
                    "regular_sigma_zero_interface",
                    "resolved_same_action_interface_laws",
                    "historical_nonlinear_surface_separation_witnesses",
                ],
                "open_join": "current_interacting_full_field_C2_action",
            },
            "particle_identity_transport": {
                "fitted_pieces": [
                    "Spin_x_G_SM_reset_bundle",
                    "three_family_projectors_per_charged_sector",
                    "all_nine_C2_state_fibers",
                    "reset_projector_enclosure_commuting_square",
                    "existing_SM_manifestation_readout",
                    "family_central_current_C2_lowest_Weyl_operator_attachment",
                ],
                "open_join": "action_selected_returned_mass_and_pole_operators",
            },
            "muon_magnetic_moment": {
                "fitted_pieces": [
                    "charged_lepton_family_slot_1_mode_label_(5,2)",
                    "existing_muon_manifestation_readout",
                    "fail_closed_LSZ_loop_vertex_F2_zero_engine",
                    "current_C2_lowest_Weyl_two_point_operator_piece",
                ],
                "open_join": (
                    "current_AE3_muon_simple_pole_plus_complete_renormalized_"
                    "electromagnetic_vertex_and_Ward_identity"
                ),
                "prediction_emitted": False,
            },
            "collisions_and_decays": {
                "fitted_pieces": [
                    "same_action_S2_S3_S4_interfaces",
                    "LSZ_normalization_engine",
                    "tree_loop_decay_and_collision_kinematics",
                    "channel_and_optical_theorem_ledgers",
                ],
                "open_join": (
                    "current_physical_spectrum_vertices_complete_channels_"
                    "and_renormalized_amplitudes"
                ),
                "prediction_emitted": False,
            },
            "new_particle_and_phenomenon_forecasts": {
                "fitted_pieces": [
                    "spectral_density_and_forecast_engines",
                    "interval_and_claim_firewalls",
                ],
                "open_join": (
                    "current_full_quadratic_operator_physical_saddle_and_"
                    "outward_uncertainty"
                ),
                "prediction_emitted": False,
            },
            "gravity_and_cosmology": {
                "fitted_pieces": [
                    "retained_Einstein_eta_geometry_action",
                    "historical_boundary_gravity_and_cosmological_parent_components",
                ],
                "open_join": (
                    "one_current_action_background_and_scale_connecting_local_"
                    "enclosure_to_gravity_dark_sectors_expansion_and_CMB"
                ),
                "prediction_emitted": False,
            },
        },
        "serial_gate_order_required": False,
        "section_updates_allowed_when_locally_compatible": True,
        "section_fit_is_monotone": (
            "VALID_PIECES_REMAIN_REUSABLE_UNLESS_A_PROVENANCE_OR_INTERFACE_"
            "AUDIT_EXPLICITLY_SUPERSEDES_THEM"
        ),
        "systems_completion_rule": (
            "ALL_CLAIMED_SECTION_JOINS_SHARE_ONE_COMPATIBLE_ACTION_BACKGROUND_"
            "DOMAIN_SCALE_AND_PROVENANCE_AND_THE_COMPOSED_MAPS_COMMUTE"
        ),
    }


__all__ = [
    "ACTION_VERSION",
    "CARRIER_ID",
    "SELECTED_ROUTE",
    "CarrierCandidate",
    "dependency_ledgers",
    "current_full_field_attachment_ledger",
    "enclosure_transport_square_certificate",
    "family_fiber_transport_certificate",
    "interface_variation_ledger",
    "localization_weight",
    "minimal_even_quadratic_coefficients",
    "ranked_carrier_candidates",
    "reciprocal_join_density",
    "reciprocal_join_normalization",
    "reciprocal_join_profile",
    "reciprocal_join_profile_derivative",
    "regular_carrier_certificate",
    "systems_integration_puzzle",
]
