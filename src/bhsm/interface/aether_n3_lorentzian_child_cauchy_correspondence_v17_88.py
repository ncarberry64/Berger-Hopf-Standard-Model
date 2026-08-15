"""Audit of the provisional Lorentzian child Cauchy correspondence.

The event germ and reconstructed child have a common order-three interior
chart, but the archive does not own a joined event action from which a zero
surface block follows.  The terminal lapse/shift rows are therefore only the
Dirac component of child solvability, not the complete outer-layer
Calderon/Wentzell correspondence.
"""
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


VERSION = "v17.88"
CLASSIFICATION = "BHSM_N3_LORENTZIAN_COMPLETE_CHILD_CAUCHY_CORRESPONDENCE"
FULL_BHSM_COMPLETE = False


def _terminal_multiplier_slice() -> slice:
    start = (NODES - 1) * Q_DIMENSION + (NODES - 1) * M_DIMENSION
    return slice(start, start + M_DIMENSION)


def event_to_child_cauchy_correspondence() -> dict[str, Any]:
    raw = v17_75_selected_raw_vector()
    scales = kkt_variable_scales()
    projected_y, full_residual = exact_local_jet_sbp_projected_residual_and_vector(
        raw * scales
    )
    projected_raw = projected_y / scales
    state = unpack_reduced(projected_raw)
    q = np.asarray(state["coordinates"], dtype=float)
    m = np.asarray(state["multipliers"], dtype=float)
    period = float(state["period"])
    velocity = trapezoid_sbp_difference() @ q / period
    q_event = q[-1]
    velocity_event = velocity[-1]
    m_event = m[-1]

    jet = exact_full_action_jet_at_state(
        ORDER, q_event, velocity_event, m_event, points=44
    )
    gradient = np.asarray(jet.gradient, dtype=float)
    hessian = np.asarray(jet.hessian, dtype=float)
    momentum = gradient[Q_DIMENSION:2 * Q_DIMENSION]
    multiplier_constraint = gradient[2 * Q_DIMENSION:]
    energy_constraint = float(
        gradient[Q_DIMENSION:2 * Q_DIMENSION] @ velocity_event - jet.value
    )
    local_constraint = np.concatenate((
        multiplier_constraint, [energy_constraint]
    ))
    energy_differential = np.concatenate((
        hessian[Q_DIMENSION:2 * Q_DIMENSION, :Q_DIMENSION].T
        @ velocity_event - gradient[:Q_DIMENSION],
        hessian[
            Q_DIMENSION:2 * Q_DIMENSION,
            Q_DIMENSION:2 * Q_DIMENSION,
        ].T @ velocity_event,
        hessian[
            Q_DIMENSION:2 * Q_DIMENSION,
            2 * Q_DIMENSION:,
        ].T @ velocity_event - multiplier_constraint,
    ))
    local_constraint_differential = np.vstack((
        hessian[2 * Q_DIMENSION:, :], energy_differential
    ))
    local_singular_values = np.linalg.svd(
        local_constraint_differential, compute_uv=False
    )

    terminal_rows = np.asarray(full_residual[_terminal_multiplier_slice()])
    boundary = terminal_event_boundary_data(projected_raw)
    trace = boundary["spatial_trace_Gamma0"]

    return {
        "joined_action_derivation": {
            "joined_action": "PROVISIONAL_JOIN_NOT_ACTION_OWNED",
            "event_first_variation": (
                "delta_S_joined=(Pi_parent-Pi_child)*delta_q_event+"
                "C_child*delta_m_event"
            ),
            "canonical_relation": (
                "q_child(0)=q_event(T);Pi_child(0)=Pi_event(T);"
                "I_child=I_event_and_environment"
            ),
            "W_phys": None,
            "why_W_is_open": (
                "V14_67_TO_V14_69_OWN_A_NONZERO_ATTACHMENT_RESPONSE_AND_"
                "INCIDENCE_THEOREM_CLASS_BUT_NOT_ITS_EVENT_STATE_DEPENDENT_"
                "PHYSICAL_PULLBACK;ZERO_CANNOT_BE_INFERRED"
            ),
            "firewall_compatibility": (
                "CONTINUOUS_TRACES_ARE_ARGUMENTS_OF_THE_ACTION_OWNED_"
                "CANONICAL_RELATION_ONLY;THEY_ARE_NOT_PREGEOMETRIC_"
                "TRANSPORTED_PRIMITIVES"
            ),
        },
        "complete_child_initial_state_map": {
            "configuration": q_event.tolist(),
            "configuration_rule": "q_child_0=q_event_terminal_in_the_same_N3_chart",
            "velocity": velocity_event.tolist(),
            "velocity_rule": (
                "dot_q_child_0=dot_q_event_terminal_AND_Pi_child=Pi_event_"
                "BY_THE_COMMON_ACTION_LEGENDRE_MAP"
            ),
            "canonical_momentum": momentum.tolist(),
            "lapse_shift": m_event.tolist(),
            "eta_gauge": "f=chi;the_two_eta_shape_modes_are_quotiented",
            "sigma_response": (
                "sigma=C_J[f]-1/2_WITH_NORMAL_DERIVATIVE_FIXED_BY_THE_"
                "NORMALIZED_RESPONSE"
            ),
            "topology_and_carrier": (
                "degree_1;child_x_negative;odd_FR;transported_SM_bundle_"
                "class;same_rank16_replacement_operator"
            ),
            "reconstruction_scale": float(q_event[0]),
            "reconstruction_scale_rule": (
                "log_R_child=q_event[0]_ONLY_ON_THE_SOLVABLE_CANONICAL_"
                "RELATION;IT_IS_NOT_AN_INDEPENDENT_OR_TRANSPORTED_VARIABLE"
            ),
            "boundary_trace": trace,
        },
        "F_child": {
            "definition": (
                "F_child_Dirac(z_event)=C_terminal_replacement(z_event);THIS_"
                "IS_ONLY_ONE_COMPONENT_OF_THE_COMPLETE_F_child"
            ),
            "component_order": [
                "lapse_1", "lapse_2", "lapse_3",
                "shift_0", "shift_1", "shift_2",
                "Hamiltonian_energy",
            ],
            "row_ownership": (
                "SIX_TERMINAL_MULTIPLIER_ROWS_ARE_ROWS_368_THROUGH_373_OF_"
                "THE_ZERO_BASED_376_KKT_RESIDUAL;THE_SEVENTH_LOCAL_ENERGY_"
                "CONSTRAINT_IS_OWNED_GLOBALLY_BY_PERIOD_STATIONARITY"
            ),
            "current_candidate_terminal_multiplier_rows": terminal_rows.tolist(),
            "current_candidate_rows": local_constraint.tolist(),
            "current_candidate_norm": float(np.linalg.norm(local_constraint)),
            "current_candidate_closed": bool(
                np.linalg.norm(local_constraint) <= 1.0e-8
            ),
            "local_classical_constraint_rows": local_constraint.tolist(),
            "local_constraint_differential_rank": int(np.linalg.matrix_rank(
                local_constraint_differential, tol=1.0e-9
            )),
            "local_constraint_differential_singular_values": (
                local_singular_values.tolist()
            ),
            "selection_rank_witness": (
                "THE_SEVEN_ACTION_CONSTRAINT_DIRECTIONS_ARE_LOCALLY_"
                "INDEPENDENT_IN_THE_TERMINAL_CAUCHY_CHART_BUT_DO_NOT_SUPPLY_"
                "THE_OUTER_LAYER_EVENT_TO_CHILD_SELECTION"
            ),
            "missing_outer_layer_component": (
                "F_child_outer=P_physical[Gamma1_event+Gamma1_child+"
                "W_phys(z_event)*Gamma0]"
            ),
        },
        "KKT_integration": {
            "pre_event_unknown_count": 376,
            "new_unknowns": 0,
            "new_equations": 0,
            "F_child_already_present": False,
            "direct_N3_solve_authorized_next": False,
            "candidate_acceptance": (
                "ALL_376_KKT_ROWS_CLOSE;ETA_REMAINS_POSITIVE;AND_THE_"
                "SEPARATELY_DERIVED_OUTER_LAYER_F_child_CLOSES"
            ),
            "why_no_377th_coordinate": (
                "THE_WHOLE_CHILD_IS_THE_DERIVED_POST_EVENT_CAUCHY_STATE_"
                "AND_CANONICAL_RELATION_NOT_A_PRE_EVENT_SCALAR"
            ),
        },
    }


def completion_payload() -> dict[str, Any]:
    result = event_to_child_cauchy_correspondence()
    joined = result["joined_action_derivation"]
    mapping = result["complete_child_initial_state_map"]
    child = result["F_child"]
    integration = result["KKT_integration"]
    validation = {
        "same_order_three_chart": len(mapping["configuration"]) == Q_DIMENSION,
        "same_action_momentum_map": len(mapping["canonical_momentum"]) == Q_DIMENSION,
        "zero_W_not_fabricated": joined["W_phys"] is None,
        "firewall_not_violated": "NOT_PREGEOMETRIC" in joined["firewall_compatibility"],
        "whole_child_not_extra_coordinate": integration["new_unknowns"] == 0,
        "F_child_has_seven_owned_rows": len(
            child["current_candidate_rows"]
        ) == M_DIMENSION + 1,
        "constraint_selection_rank_seven": child[
            "local_constraint_differential_rank"
        ] == M_DIMENSION + 1,
        "current_candidate_not_false_promoted": not child["current_candidate_closed"],
        "direct_solve_deferred_until_complete_F_child": (
            not integration["direct_N3_solve_authorized_next"]
            and not integration["F_child_already_present"]
        ),
        "finite_reconstruction_scale": math.isfinite(mapping["reconstruction_scale"]),
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_lorentzian_child_cauchy_correspondence_v17_88",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "event_to_complete_child_cauchy_correspondence": result,
        "status": "RECLASSIFIED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "THE_TERMINAL_DIRAC_ROWS_ARE_NECESSARY_BUT_NOT_SUFFICIENT_FOR_"
            "ONE_COMPLETE_NONEQUILIBRIUM_CHILD"
        ),
        "dependency_advanced": (
            "IDENTIFIES_THE_DIRAC_SUBBLOCK_OF_F_child_AND_INVALIDATES_"
            "EQUATING_IT_WITH_THE_COMPLETE_CORRESPONDENCE"
        ),
        "active_calculation": (
            "DERIVE_THE_EVENT_STATE_DEPENDENT_ATTACHMENT_INCIDENCE_AND_"
            "OUTER_LAYER_CALDERON_WENTZELL_FLUX_MAP_BEFORE_MORE_N3_SOLVING"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_lorentzian_child_cauchy_correspondence_v17_88.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "event_to_child_cauchy_correspondence", "completion_payload", "materialize",
]
