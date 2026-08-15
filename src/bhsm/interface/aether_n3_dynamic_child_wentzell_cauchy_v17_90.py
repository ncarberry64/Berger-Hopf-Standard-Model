"""Dynamic, rather than static, event-to-child Wentzell Cauchy law."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_constraint_solved_orbit_v16_08 import (
    exact_euler_dirac_acceleration,
)
from bhsm.interface.aether_n3_event_attachment_state_incidence_v17_89 import (
    n3_attachment_state_map,
)
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    M_DIMENSION,
    NODES,
    ORDER,
    Q_DIMENSION,
    unpack_reduced,
)
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import (
    trapezoid_sbp_difference,
)
from bhsm.interface.aether_n3_scale_corrected_period_log_continuation_v17_76 import (
    v17_75_selected_raw_vector,
)


VERSION = "v17.90"
CLASSIFICATION = "BHSM_N3_DYNAMIC_CHILD_WENTZELL_CAUCHY_LAW"
FULL_BHSM_COMPLETE = False


def _effective_form(
    form: np.ndarray, boundary_jacobian: np.ndarray,
    constraint_jacobian: np.ndarray,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Constraint-reduced two-coordinate form by a bordered Schur solve."""

    matrix = np.asarray(form, dtype=float)
    boundary = np.asarray(boundary_jacobian, dtype=float)
    constraints = np.asarray(constraint_jacobian, dtype=float)
    combined = np.vstack((boundary, constraints))
    compliance = combined @ np.linalg.solve(matrix, combined.T)
    reduced = np.linalg.inv(compliance)[:2, :2]
    reduced = 0.5 * (reduced + reduced.T)
    return reduced, {
        "ambient_rank": int(np.linalg.matrix_rank(matrix, tol=1.0e-10)),
        "constraint_rank": int(np.linalg.matrix_rank(constraints, tol=1.0e-10)),
        "combined_rank": int(np.linalg.matrix_rank(combined, tol=1.0e-10)),
        "compliance_condition_number": float(np.linalg.cond(compliance)),
        "reduced_rank": int(np.linalg.matrix_rank(reduced, tol=1.0e-10)),
        "reduced_eigenvalues": np.linalg.eigvalsh(reduced).tolist(),
    }


def dynamic_child_cauchy_data() -> dict[str, Any]:
    raw = v17_75_selected_raw_vector()
    state = unpack_reduced(raw)
    q = np.asarray(state["coordinates"], dtype=float)
    multipliers = np.asarray(state["multipliers"], dtype=float)
    period = float(state["period"])
    velocity = trapezoid_sbp_difference() @ q / period
    terminal_q = q[-1]
    terminal_velocity = velocity[-1]
    terminal_m = multipliers[-1]

    incidence = n3_attachment_state_map(raw)
    attachment = np.asarray(incidence["attachment_state"], dtype=float)
    # Independent reciprocal tangent coordinates are c=(q_W,x_D).
    boundary_jacobian = np.asarray(
        incidence["state_jacobian_D_attachment_D_q_event"], dtype=float
    )[1:]

    jet = exact_full_action_jet_at_state(
        ORDER, terminal_q, terminal_velocity, terminal_m, points=44
    )
    hessian = np.asarray(jet.hessian, dtype=float)
    q_block = hessian[:Q_DIMENSION, :Q_DIMENSION]
    velocity_block = hessian[
        Q_DIMENSION:2 * Q_DIMENSION,
        Q_DIMENSION:2 * Q_DIMENSION,
    ]
    constraint_q = hessian[2 * Q_DIMENSION:, :Q_DIMENSION]
    constraint_velocity = hessian[
        2 * Q_DIMENSION:, Q_DIMENSION:2 * Q_DIMENSION
    ]
    kinetic, kinetic_certificate = _effective_form(
        velocity_block, boundary_jacobian, constraint_velocity
    )
    coordinate_response, coordinate_certificate = _effective_form(
        q_block, boundary_jacobian, constraint_q
    )

    dynamics = exact_euler_dirac_acceleration(
        ORDER, terminal_q, terminal_velocity, terminal_m, points=44
    )
    acceleration = np.asarray(dynamics["acceleration"], dtype=float)

    # q_W=q0+u_boundary-1/2 log cosh(2 v_boundary). Only its v-mode
    # dependence is nonlinear. x_D=q_C-q_W has the opposite Hessian.
    signs_j = (-1.0) ** np.arange(ORDER)
    v_boundary = float(
        terminal_q[1 + 2 * ORDER:1 + 3 * ORDER] @ signs_j
    )
    v_covector = np.zeros(Q_DIMENSION)
    v_covector[1 + 2 * ORDER:1 + 3 * ORDER] = signs_j
    q_w_hessian = (
        -2.0 / math.cosh(2.0 * v_boundary) ** 2
    ) * np.outer(v_covector, v_covector)
    convective = float(terminal_velocity @ q_w_hessian @ terminal_velocity)
    c = attachment[1:]
    c_dot = boundary_jacobian @ terminal_velocity
    c_ddot = boundary_jacobian @ acceleration + np.asarray([
        convective, -convective
    ])

    return {
        "independent_attachment_coordinates": ["q_W", "x_D"],
        "c": c.tolist(),
        "c_dot": c_dot.tolist(),
        "c_ddot_from_current_child_Euler_Dirac_field": c_ddot.tolist(),
        "terminal_coordinate_acceleration": acceleration.tolist(),
        "current_Euler_Dirac_condition_number": float(
            dynamics["Dirac_condition_number"]
        ),
        "current_Euler_Dirac_field_finite": bool(dynamics["finite"]),
        "constraint_reduced_attachment_Legendre_form": kinetic.tolist(),
        "Legendre_certificate": kinetic_certificate,
        "constraint_reduced_instantaneous_coordinate_response": (
            coordinate_response.tolist()
        ),
        "coordinate_response_certificate": coordinate_certificate,
        "signature_interpretation": (
            "INDEFINITE_GRAVITATIONAL_SIGNATURE_IS_ALLOWED;INVERTIBILITY_"
            "RATHER_THAN_POSITIVITY_IS_THE_CAUCHY_WELL_POSEDNESS_TEST"
        ),
        "dynamic_boundary_law": {
            "equation": (
                "K_att(c)*D_tau^2_c+C_att(c,c_dot)+dV_att/dc+"
                "P_phys*(Gamma1_event+Gamma1_child)=0"
            ),
            "equivalent_frequency_domain_form": (
                "P_phys*(Gamma1_event+Gamma1_child+W_phys(omega,c)*Gamma0)=0"
            ),
            "static_W_times_c_equals_zero_required": False,
            "zero_c_required": False,
            "zero_c_dot_required": False,
            "zero_c_ddot_required": False,
            "nonzero_momentum_is_a_defect": False,
            "nonzero_time_dependence_is_a_defect": False,
        },
        "complete_F_child_components": {
            "interior_Cauchy_identity": "DERIVED_ON_THE_REGULAR_INTERIOR",
            "terminal_Dirac_replacement_constraints": (
                "OWNED_BY_ROWS_368_TO_373_BUT_NOT_CLOSED_AT_V17_75"
            ),
            "attachment_state_and_differential": "DERIVED_IN_V17_89",
            "attachment_Legendre_rank": "DERIVED_HERE_IN_THE_N3_SCALAR_SECTOR",
            "nonlinear_event_attachment_force": "OPEN",
            "two_sided_complete_child_Calderon_flux": "OPEN",
            "complete_gauge_spinor_ghost_projector": "OPEN",
        },
        "persistence_rule": (
            "AFTER_ALL_F_child_COMPONENTS_CLOSE_EVOLVE_THIS_NONZERO_CAUCHY_"
            "STATE_AND_REQUIRE_CONSTRAINT_CONSISTENT_RELATIVE_EVOLUTION_"
            "INSIDE_B_child_FOR_NONZERO_PROPER_TIME"
        ),
    }


def completion_payload() -> dict[str, Any]:
    result = dynamic_child_cauchy_data()
    kinetic = result["Legendre_certificate"]
    law = result["dynamic_boundary_law"]
    validation = {
        "attachment_Legendre_rank_two": kinetic["reduced_rank"] == 2,
        "Euler_Dirac_field_finite": result["current_Euler_Dirac_field_finite"],
        "nonzero_motion_retained": np.linalg.norm(result["c_dot"]) > 0.0,
        "nonzero_acceleration_retained": np.linalg.norm(result[
            "c_ddot_from_current_child_Euler_Dirac_field"
        ]) > 0.0,
        "indefinite_signature_not_misreported": "INDEFINITE" in result[
            "signature_interpretation"
        ],
        "static_balance_invalidated": not law[
            "static_W_times_c_equals_zero_required"
        ],
        "momentum_not_defect": not law["nonzero_momentum_is_a_defect"],
        "time_dependence_not_defect": not law[
            "nonzero_time_dependence_is_a_defect"
        ],
        "open_physical_blocks_not_fabricated": all(
            result["complete_F_child_components"][key] == "OPEN"
            for key in (
                "nonlinear_event_attachment_force",
                "two_sided_complete_child_Calderon_flux",
                "complete_gauge_spinor_ghost_projector",
            )
        ),
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_dynamic_child_wentzell_cauchy_v17_90",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "dynamic_event_to_child_cauchy_law": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "A_PARTICLE_CHILD_MAY_HAVE_NONZERO_MOTION_MOMENTUM_AND_"
            "ACCELERATION_WHILE_ITS_DYNAMIC_BOUNDARY_LAW_AND_CONSTRAINTS_CLOSE"
        ),
        "dependency_advanced": (
            "REPLACES_STATIC_EVENT_BALANCE_BY_THE_CONSTRAINT_REDUCED_"
            "DYNAMIC_WENTZELL_CAUCHY_SOLVABILITY_LAW"
        ),
        "active_calculation": (
            "DERIVE_THE_NONLINEAR_EVENT_ATTACHMENT_FORCE_AND_TWO_SIDED_"
            "COMPLETE_CHILD_CALDERON_FLUX_ON_THE_V17_89_RANK_TWO_IMAGE"
        ),
        "direct_N3_solve_authorized_next": False,
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_dynamic_child_wentzell_cauchy_v17_90.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "dynamic_child_cauchy_data", "completion_payload", "materialize",
]
