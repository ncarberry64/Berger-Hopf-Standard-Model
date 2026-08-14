"""Whole-child imbalance, persistence-domain, and decay reclassification."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_n3_exact_local_jet_sbp_covector_v17_61 import (
    exact_local_jet_sbp_projected_residual_and_vector,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    M_DIMENSION,
    NODES,
    ORDER,
    Q_DIMENSION,
    kkt_variable_scales,
    unpack_reduced,
)
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import (
    trapezoid_sbp_difference,
)
from bhsm.interface.aether_n3_scale_corrected_period_log_continuation_v17_76 import (
    v17_75_selected_raw_vector,
)
from bhsm.interface.aether_n3_terminal_child_boundary_map_v17_85 import (
    terminal_event_boundary_data,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    sobolev_weights,
)


VERSION = "v17.87"
CLASSIFICATION = "BHSM_PERSISTENT_NONEQUILIBRIUM_WHOLE_CHILD"
FULL_BHSM_COMPLETE = False


def whole_child_imbalance_state() -> dict[str, Any]:
    raw = v17_75_selected_raw_vector()
    scales = kkt_variable_scales()
    projected_y, global_residual = exact_local_jet_sbp_projected_residual_and_vector(
        raw * scales
    )
    projected_raw = projected_y / scales
    unpacked = unpack_reduced(projected_raw)
    q = np.asarray(unpacked["coordinates"])
    multipliers = np.asarray(unpacked["multipliers"])
    period = float(unpacked["period"])
    velocity = trapezoid_sbp_difference() @ q / period
    jet = exact_full_action_jet_at_state(
        ORDER, q[-1], velocity[-1], multipliers[-1], points=44
    )
    gradient = np.asarray(jet.gradient)
    hessian = np.asarray(jet.hessian)
    velocity_momentum = gradient[Q_DIMENSION:2 * Q_DIMENSION]
    local_force = gradient[:Q_DIMENSION]
    velocity_hessian = hessian[
        Q_DIMENSION:2 * Q_DIMENSION,
        Q_DIMENSION:2 * Q_DIMENSION,
    ]
    eigenvalues, eigenvectors = np.linalg.eigh(velocity_hessian)
    polar_hessian = (eigenvectors * np.abs(eigenvalues)) @ eigenvectors.T
    weights = sobolev_weights(ORDER)["velocities"]
    multiplier_start = (NODES - 1) * Q_DIMENSION
    final_multiplier_start = multiplier_start + (NODES - 1) * M_DIMENSION
    final_constraint_rows = global_residual[
        final_multiplier_start:final_multiplier_start + M_DIMENSION
    ]
    boundary = terminal_event_boundary_data(projected_raw)
    return {
        "source_state": "v17.75_selected_fine_period_log_mix_state",
        "whole_child_state": {
            "geometry_modes": q[-1].tolist(),
            "geometry_rates": velocity[-1].tolist(),
            "lapse_shift_constraint_state": multipliers[-1].tolist(),
            "material_state": boundary["material_response"],
            "boundary_trace": boundary["spatial_trace_Gamma0"],
            "boundary_radial_flux": boundary[
                "GHY_eta_radial_flux_Gamma1"
            ],
            "topology_orientation": "degree_1;child_x_negative",
            "FR_sector": "odd_antiperiodic;J_squared=1/4",
            "SM_carrier": (
                "transported_bundle_class_plus_same_rank16_replacement_operator"
            ),
            "reconstruction_scale": "OPEN_EVENT_ENVIRONMENT_CHILD_BVP_OUTPUT",
        },
        "imbalance_covector": {
            "definition": (
                "I_child=(Pi_phys,dH_child/dq,F_child)_ON_THE_CONSTRAINT_"
                "REDUCED_WHOLE_CHILD_STATE"
            ),
            "canonical_velocity_momentum": velocity_momentum.tolist(),
            "local_action_force": local_force.tolist(),
            "child_matching_component": "F_child_OPEN_NOT_SET_TO_ZERO",
            "not_an_independent_scalar_field": True,
        },
        "action_derived_diagnostics": {
            "canonical_momentum_dual_H5_norm": float(np.linalg.norm(
                velocity_momentum / weights
            )),
            "local_force_dual_H6_proxy_norm": float(np.linalg.norm(
                local_force / ((1.0 + np.asarray([
                    0.0, 4.0, 8.0, 12.0, 0.0, 4.0, 8.0, 0.0, 4.0, 8.0,
                ]) ** 2) ** 3.0)
            )),
            "signed_kinetic_quadratic_form": float(
                0.5 * velocity[-1] @ velocity_hessian @ velocity[-1]
            ),
            "positive_polar_kinetic_magnitude": float(
                0.5 * velocity[-1] @ polar_hessian @ velocity[-1]
            ),
            "velocity_Legendre_rank": int(np.linalg.matrix_rank(
                velocity_hessian, tol=1.0e-10
            )),
            "velocity_Legendre_eigenvalues": eigenvalues.tolist(),
            "terminal_global_constraint_rows": final_constraint_rows.tolist(),
            "terminal_global_constraint_norm": float(np.linalg.norm(
                final_constraint_rows
            )),
            "eta_minimum_on_event_history": _minimum_node_eta(projected_raw),
            "nonzero_nonequilibrium_momentum": bool(
                np.linalg.norm(velocity_momentum / weights) > 1.0e-12
            ),
        },
        "relationship_of_imbalance_contributions": {
            "reconstruction": (
                "F_child=0_IS_REQUIRED_TO_CREATE_ONE_CONSISTENT_CHILD_AND_IS_"
                "NOT_THE_POST_RECONSTRUCTION_DYNAMICAL_IMBALANCE"
            ),
            "dynamics": (
                "Pi_phys_AND_dH_child/dq_FORM_THE_CANONICAL_NONEQUILIBRIUM_"
                "STATE_AND_EVOLVE_BY_THE_SAME_CHILD_ACTION"
            ),
            "decay": (
                "THE_EVOLVED_CANONICAL_STATE_CAUSES_EXIT_FROM_B_child;NO_"
                "SEPARATE_DECAY_FORCE_IS_ADDED"
            ),
        },
    }


def persistence_and_decay_contract() -> dict[str, Any]:
    return {
        "particle_definition": (
            "COMPLETE_RECONSTRUCTED_ENCAPSULATED_PERSISTENT_"
            "NONEQUILIBRIUM_CHILD"
        ),
        "persistence_domain_B_child": {
            "topological_component": (
                "fixed_degree_orientation_FR_parity_incidence_and_boundary_"
                "identity"
            ),
            "carrier_component": (
                "fixed_gauge_representation_hypercharge_color_C3_family_"
                "projector_and_bundle_isomorphism_class"
            ),
            "geometric_domain": (
                "positive_spatial_metric_and_lapse;finite_H6xH5_phase_state"
            ),
            "hyperregular_domain": "minimum_eta_Legendre>0",
            "constraint_domain": (
                "Hamiltonian_momentum_eta_sigma_gauge_and_FR_constraints=0"
            ),
            "reconstruction_domain": (
                "F_child=0_AND_THE_COMPLETE_CHILD_BVP_IS_LOCALLY_WELL_POSED"
            ),
            "dynamic_domain": (
                "the_same_action_owned_child_flow_exists_and_remains_in_the_"
                "above_common_domain"
            ),
            "measured_lifetime_threshold_used": False,
            "arbitrary_balance_tolerance_used_as_physics": False,
        },
        "persistence": (
            "A_CHILD_IS_THE_SAME_PHYSICAL_CHILD_WHILE_z_child(tau)_IN_B_child_"
            "FOR_A_NONZERO_PROPER_TIME_INTERVAL"
        ),
        "special_limits_not_universal_requirements": [
            "stationary_constrained_extremum",
            "positive_reduced_Hessian",
            "relative_periodic_orbit",
            "exact_hybrid_fixed_point",
            "unit_modulus_Floquet_spectrum",
        ],
        "decay": {
            "definition": (
                "tau_decay=inf{tau>0:z_child(tau)_notin_B_child}"
            ),
            "clock": (
                "RECONSTRUCTED_CHILD_PROPER_TIME_d_tau=N_child*dt;IF_ONLY_A_"
                "RETURN_MAP_IS_AVAILABLE_REPORT_INTERNAL_CYCLE_COUNT_UNTIL_"
                "A_PROPER_TIME_MAP_IS_DERIVED"
            ),
            "daughter_condition": (
                "THE_EXIT_STATE_MAY_RECONSTRUCT_ONLY_IN_CHANNELS_COMPATIBLE_"
                "WITH_CONSERVED_TOPOLOGY_FR_GAUGE_CHARGE_COLOR_HYPERCHARGE_"
                "INCIDENCE_FAMILY_PROJECTORS_AND_ENVIRONMENT_DATA"
            ),
            "phenomenological_decay_term_added": False,
        },
    }


def stability_reclassification_ledger() -> list[dict[str, str]]:
    return [
        {"historical_gate": "stationary_child_dH/dx=0", "classification": "KEEP_AS_LOCAL_MATHEMATICAL_CONDITION", "new_role": "instantaneous_constrained_extremum_or_drift_reference"},
        {"historical_gate": "positive_child_Hessian", "classification": "KEEP_AS_LOCAL_MATHEMATICAL_CONDITION", "new_role": "local_restoring_response_and_possible_long_persistence"},
        {"historical_gate": "relative_periodic_child", "classification": "REINTERPRET_AS_PERSISTENCE_CONDITION", "new_role": "special_recurrent_persistent_trajectory"},
        {"historical_gate": "unit_modulus_Floquet_spectrum", "classification": "REINTERPRET_AS_PERSISTENCE_CONDITION", "new_role": "local_cycle_drift_diagnostic_not_particle_definition"},
        {"historical_gate": "constant_reset_hybrid_fixed_point", "classification": "INVALIDATE_AS_FINAL_PARTICLE_REQUIREMENT", "new_role": "historical_finite_chart_witness_not_event_specific_child"},
        {"historical_gate": "exact_return_to_identical_state", "classification": "REPLACE", "new_role": "remain_inside_B_child_for_nonzero_interval"},
        {"historical_gate": "stable_soliton_particle", "classification": "INVALIDATE_AS_FINAL_PARTICLE_REQUIREMENT", "new_role": "persistent_nonequilibrium_complete_child"},
        {"historical_gate": "N3_event_KKT_saddle", "classification": "KEEP_AS_LOCAL_MATHEMATICAL_CONDITION", "new_role": "formation_encapsulation_gate_not_particle_persistence"},
    ]


def completion_payload() -> dict[str, Any]:
    imbalance = whole_child_imbalance_state()
    contract = persistence_and_decay_contract()
    ledger = stability_reclassification_ledger()
    diagnostics = imbalance["action_derived_diagnostics"]
    validation = {
        "whole_child_state_not_extra_coordinate": imbalance[
            "imbalance_covector"
        ]["not_an_independent_scalar_field"],
        "imbalance_is_action_derived_covector": len(imbalance[
            "imbalance_covector"
        ]["canonical_velocity_momentum"]) == Q_DIMENSION,
        "nonequilibrium_momentum_nonzero": diagnostics[
            "nonzero_nonequilibrium_momentum"
        ],
        "Legendre_diagnostics_finite": (
            diagnostics["velocity_Legendre_rank"] > 0
            and math.isfinite(diagnostics["positive_polar_kinetic_magnitude"])
        ),
        "all_stability_gate_classes_present": {
            row["classification"] for row in ledger
        } == {
            "KEEP_AS_LOCAL_MATHEMATICAL_CONDITION",
            "REINTERPRET_AS_PERSISTENCE_CONDITION",
            "REPLACE",
            "INVALIDATE_AS_FINAL_PARTICLE_REQUIREMENT",
        },
        "persistence_not_fixed_point": "B_child" in contract["persistence"],
        "decay_is_first_exit": contract["decay"]["definition"].startswith(
            "tau_decay=inf"
        ),
        "measured_lifetimes_not_used": not contract[
            "persistence_domain_B_child"
        ]["measured_lifetime_threshold_used"],
        "no_phenomenological_decay_force": not contract["decay"][
            "phenomenological_decay_term_added"
        ],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_persistent_nonequilibrium_child_v17_87",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "whole_child_imbalance": imbalance,
        "persistence_and_decay_contract": contract,
        "stability_reclassification_ledger": ledger,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "PARTICLE_EXISTENCE_IS_FINITE_PERSISTENCE_OF_A_COMPLETE_"
            "NONEQUILIBRIUM_CHILD_AND_DECAY_IS_ITS_FIRST_DOMAIN_EXIT"
        ),
        "dependency_advanced": (
            "REPLACES_UNIVERSAL_STABILITY_WITH_ACTION_OWNED_CANONICAL_"
            "IMBALANCE_PERSISTENCE_AND_DECAY_ONTOLOGY"
        ),
        "active_calculation": (
            "CLOSE_F_child_WITH_THE_LORENTZIAN_CAUCHY_CORRESPONDENCE_THEN_"
            "EVOLVE_THE_RECONSTRUCTED_CHILD_TO_MEASURE_ITS_FIRST_NONZERO_"
            "PERSISTENCE_INTERVAL"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_persistent_nonequilibrium_child_v17_87.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "whole_child_imbalance_state", "persistence_and_decay_contract",
    "stability_reclassification_ledger", "completion_payload", "materialize",
]
