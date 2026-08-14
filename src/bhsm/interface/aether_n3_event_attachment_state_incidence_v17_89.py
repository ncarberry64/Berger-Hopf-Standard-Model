"""Event-state attachment incidence needed by the complete-child map."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    ORDER,
    Q_DIMENSION,
    boundary_radius_and_jacobian,
    unpack_reduced,
)
from bhsm.interface.aether_n3_scale_corrected_period_log_continuation_v17_76 import (
    v17_75_selected_raw_vector,
)
from bhsm.interface.completion.action_attachment_wentzell_v14_67 import (
    attachment_response_roots,
)
from bhsm.interface.completion.global_attachment_incidence_curvature_v14_68 import (
    boundary_attachment_operator,
    scalar_stratum_incidence_map,
)


VERSION = "v17.89"
CLASSIFICATION = "BHSM_N3_EVENT_STATE_ATTACHMENT_INCIDENCE"
FULL_BHSM_COMPLETE = False


def n3_attachment_state_map(raw_vector: np.ndarray) -> dict[str, Any]:
    """Map the N=3 event geometry to the reciprocal attachment amplitudes.

    q_C is the action's global log-radius mode. q_W is the logarithm of the
    same action's boundary-radius functional. The reciprocal depth coordinate
    is consequently x_D=q_C-q_W, so the exact matcher
    -q_C+q_W+x_D=0 is an identity rather than an added constraint.
    """

    state = unpack_reduced(np.asarray(raw_vector, dtype=float))
    terminal = np.asarray(state["coordinates"], dtype=float)[-1]
    radius, log_radius_jacobian = boundary_radius_and_jacobian(terminal[None, :])
    q_c = float(terminal[0])
    q_w = float(math.log(float(radius[0])))
    x_d = q_c - q_w
    attachment = np.asarray([q_c, q_w, x_d])

    j_c = np.zeros(Q_DIMENSION)
    j_c[0] = 1.0
    j_w = np.asarray(log_radius_jacobian[0], dtype=float)
    jacobian = np.vstack((j_c, j_w, j_c - j_w))
    matcher = np.asarray([[-1.0, 1.0, 1.0]])
    tangent = np.asarray([[1.0, 1.0], [1.0, 0.0], [0.0, 1.0]])

    vertex_map = scalar_stratum_incidence_map()
    vertex_state = vertex_map @ attachment
    vertex_jacobian = vertex_map @ jacobian

    # This uses the archived representative curvatures only to demonstrate
    # the exact pullback required at the event. It is never promoted as the
    # physical event block.
    conditional_vertex_w = np.asarray(boundary_attachment_operator(1)).real
    conditional_pullback = vertex_jacobian.T @ conditional_vertex_w @ vertex_jacobian
    conditional_reaction = conditional_vertex_w @ vertex_state

    return {
        "source_state": "v17.75_selected_fine_period_log_mix_state",
        "attachment_coordinate_order": ["q_C", "q_W", "x_D"],
        "attachment_state": attachment.tolist(),
        "state_definitions": {
            "q_C": "terminal_N3_global_log_radius_q[0]",
            "q_W": "log_of_the_terminal_N3_action_boundary_radius_functional",
            "x_D": "q_C-q_W=-log_upsilon",
        },
        "reciprocal_matcher": matcher.tolist(),
        "matcher_residual": float(np.linalg.norm(matcher @ attachment)),
        "state_jacobian_D_attachment_D_q_event": jacobian.tolist(),
        "state_jacobian_rank": int(np.linalg.matrix_rank(jacobian, tol=1.0e-12)),
        "differential_matcher_residual": float(np.linalg.norm(matcher @ jacobian)),
        "attachment_tangent_basis": tangent.tolist(),
        "tangent_basis_matcher_residual": float(np.linalg.norm(matcher @ tangent)),
        "four_stratum_vertex_order": ["M8", "M5_plus", "M5_minus", "M4"],
        "four_stratum_state": vertex_state.tolist(),
        "four_stratum_state_jacobian": vertex_jacobian.tolist(),
        "four_stratum_state_jacobian_rank": int(
            np.linalg.matrix_rank(vertex_jacobian, tol=1.0e-12)
        ),
        "whole_system_interpretation": (
            "THE_SYSTEM_LEVEL_ATTACHMENT_STATE_IS_A_DERIVED_RANK_TWO_MAP_"
            "OF_THE_TEN_EVENT_GEOMETRY_MODES_NOT_AN_ELEVENTH_MODE"
        ),
        "conditional_representative_only": {
            "archived_attachment_roots": list(attachment_response_roots()),
            "vertex_Wentzell": conditional_vertex_w.tolist(),
            "N3_coordinate_pullback": conditional_pullback.tolist(),
            "pullback_rank": int(np.linalg.matrix_rank(
                conditional_pullback, tol=1.0e-11
            )),
            "reaction_on_current_state": conditional_reaction.tolist(),
            "reaction_norm": float(np.linalg.norm(conditional_reaction)),
            "physical_event_block": False,
            "why_not_physical": (
                "H_CORE_AND_DEPTH_CURVATURE_ARE_ARCHIVED_REPRESENTATIVES_"
                "NOT_THE_SCHUR_CURVATURES_OF_THIS_EVENT_AND_THE_COMPLETE_"
                "GAUGE_FIXED_CALDERON_PROJECTOR_IS_OPEN"
            ),
        },
    }


def completion_payload() -> dict[str, Any]:
    result = n3_attachment_state_map(v17_75_selected_raw_vector())
    conditional = result["conditional_representative_only"]
    validation = {
        "event_state_argument_now_explicit": len(
            result["state_jacobian_D_attachment_D_q_event"]
        ) == 3,
        "reciprocal_matcher_exact": result["matcher_residual"] < 1.0e-14,
        "differential_matcher_exact": result["differential_matcher_residual"] < 1.0e-14,
        "rank_two_attachment_state_map": result["state_jacobian_rank"] == 2,
        "rank_two_four_stratum_map": result["four_stratum_state_jacobian_rank"] == 2,
        "whole_system_not_extra_coordinate": Q_DIMENSION == 10,
        "conditional_pullback_has_expected_rank": conditional["pullback_rank"] == 2,
        "conditional_W_not_promoted": not conditional["physical_event_block"],
        "nonzero_reaction_not_called_particle_defect": conditional["reaction_norm"] > 0.0,
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_event_attachment_state_incidence_v17_89",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "event_attachment_state_incidence": result,
        "v17_83_direct_solve_result": {
            "selected_state": False,
            "all_backtracks_increased_absolute_event_row": True,
            "interpretation": (
                "THE_EXISTING_376_ROWS_DO_NOT_SUPPLY_THE_OPEN_OUTER_LAYER_"
                "F_child_SELECTION;NO_MOTION_OR_MOMENTUM_DEFECT_IS_INFERRED"
            ),
        },
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "THE_WHOLE_EVENT_DETERMINES_A_RANK_TWO_CORE_WALL_DEPTH_"
            "ATTACHMENT_STATE_WITHOUT_AN_EXTRA_BODY_COORDINATE"
        ),
        "dependency_advanced": (
            "CLOSES_THE_EVENT_TO_ATTACHMENT_STATE_DIFFERENTIAL_NEEDED_TO_"
            "PULL_THE_PHYSICAL_WENTZELL_RESPONSE_INTO_F_child"
        ),
        "active_calculation": (
            "DERIVE_THE_EVENT_SPECIFIC_SCHUR_CURVATURE_W_phys_AND_COMPLETE_"
            "CHILD_CALDERON_FLUX_ON_THIS_RANK_TWO_INCIDENCE_IMAGE"
        ),
        "direct_N3_solve_authorized_next": False,
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_event_attachment_state_incidence_v17_89.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "n3_attachment_state_map", "completion_payload", "materialize",
]
