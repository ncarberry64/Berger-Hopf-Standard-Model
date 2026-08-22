"""Promote the direct N12 child only when every existing gate is proved."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_CHECKPOINT", ".tmp_direct_n12_corrected_branch_state.npz"
))
RADII = Path(os.environ.get(
    "BHSM_N12_FULL_RADII_RESULT", ".tmp_direct_n12_full_action_radii.json"
))
DIRECTED = Path(os.environ.get(
    "BHSM_N12_DIRECTED_CENTER_AUDIT",
    ".tmp_direct_n12_directed_rounding_center.json",
))
NEIGHBORHOOD = Path(os.environ.get(
    "BHSM_N12_NEIGHBORHOOD_RESULT",
    ".tmp_direct_n12_physical_neighborhood_transfer.json",
))
PERSISTENCE = Path(os.environ.get(
    "BHSM_N12_PERSISTENCE_RESULT",
    ".tmp_direct_n12_candidate_positive_duration_persistence.json",
))
RESULT = Path(os.environ.get(
    "BHSM_N12_PROMOTION_RESULT",
    ".tmp_direct_n12_complete_persistent_child_promotion.json",
))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> None:
    radii = json.loads(RADII.read_text(encoding="utf-8"))
    directed = json.loads(DIRECTED.read_text(encoding="utf-8"))
    neighborhood = json.loads(NEIGHBORHOOD.read_text(encoding="utf-8"))
    persistence = json.loads(PERSISTENCE.read_text(encoding="utf-8"))
    numerical_root = bool(
        radii["radii_polynomial"]["numerical_radii_candidate_closed"]
        and directed["validation_passed"]
        and directed["directed_radii_polynomial_at_radius"] < 0.0
        and directed["directed_contraction_bound"] < 1.0
    )
    physical_neighborhoods = bool(
        neighborhood["validation"][
            "existing_eta_event_Dirac_persistence_neighborhoods_closed"
        ]
    )
    persistence_gate = bool(
        persistence["validation"]["local_positive_duration_existence"]
        and persistence["validation"]["coarse_fine_numerical_witness"]
        and persistence["validation"]["nonzero_motion_retained"]
    )
    promoted = bool(
        numerical_root and physical_neighborhoods and persistence_gate
    )
    payload = {
        "classification": (
            "DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED"
            if promoted else "DIRECT_N12_PROMOTION_FAILED_CLOSED"
        ),
        "order": 12,
        "points": 96,
        "source_checkpoint": str(CHECKPOINT),
        "source_checkpoint_SHA256": _sha256(CHECKPOINT),
        "certificate_inputs": {
            str(path): _sha256(path)
            for path in (RADII, DIRECTED, NEIGHBORHOOD, PERSISTENCE)
        },
        "certified_root_ball": {
            "coordinate_system": "EXISTING_ACTION_COORDINATES",
            "center_exact_F12_norm": radii["center"]["exact_F12_norm"],
            "radius": radii["action_coordinate_ball_radius"],
            "directed_Y_upper": directed["directed_Y_upper"],
            "directed_Z0_upper": directed["directed_Frobenius_Z0_upper"],
            "Z2_upper": directed["replayed_Z2"],
            "radii_polynomial_at_radius": directed[
                "directed_radii_polynomial_at_radius"
            ],
            "contraction_bound": directed["directed_contraction_bound"],
            "unique_unchanged_F12_root_exists_in_ball": numerical_root,
            "center_itself_claimed_as_exact_root": False,
        },
        "existing_physical_gates": {
            "corrected_action_owned_ordered_branch": True,
            "eta_ball_lower": neighborhood["eta_neighborhood"][
                "ball_lower_bound"
            ],
            "Dirac_relative_ball_perturbation": neighborhood[
                "Dirac_neighborhood"
            ]["relative_ball_perturbation_bound"],
            "Dirac_invertible_on_ball": neighborhood[
                "Dirac_neighborhood"
            ]["invertible_on_ball"],
            "boundary_lapse_ball_lower": neighborhood[
                "remaining_existing_gates"
            ]["boundary_lapse_ball_lower"],
            "nonzero_velocity_ball_lower": neighborhood[
                "remaining_existing_gates"
            ]["nonzero_velocity_ball_lower"],
            "canonical_lifts_invertible_on_ball": neighborhood[
                "remaining_existing_gates"
            ]["canonical_bordered_lifts_invertible_on_ball"],
            "positive_duration_proper_time": persistence[
                "fine_evolution"
            ]["child_proper_duration"],
            "coarse_fine_relative_difference": persistence[
                "coarse_fine_relative_difference"
            ],
            "maximum_constraint_residual_on_witness": max(
                persistence["coarse_evolution"][
                    "maximum_constraint_residual"
                ],
                persistence["fine_evolution"][
                    "maximum_constraint_residual"
                ],
            ),
            "minimum_eta_on_witness": min(
                persistence["coarse_evolution"]["minimum_eta_Legendre"],
                persistence["fine_evolution"]["minimum_eta_Legendre"],
            ),
            "nonzero_relative_evolution_retained": persistence[
                "validation"
            ]["nonzero_motion_retained"],
        },
        "validation": {
            "unchanged_57_row_F12_root_certified": numerical_root,
            "eta_event_Dirac_and_boundary_gates_transfer_to_root": (
                physical_neighborhoods
            ),
            "existing_positive_duration_persistence_gate": persistence_gate,
            "componentwise_monotonicity_required": False,
            "solver_parameter_promoted_as_physics": False,
            "new_equation_constraint_gate_scale_or_selector": False,
        },
        "validation_passed": promoted,
        "DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED": promoted,
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "exact_next_dependency": (
            "APPEND_THE_ACTION_DERIVED_INVERSE_SQUARE_HIGH_MODE_TAIL_"
            "TO_THE_CERTIFIED_N12_ANCHOR_AND_CLOSE_THE_GENERAL_N_"
            "CONTINUUM_EVENT_CHILD_CONSTRUCTION"
            if promoted else
            "REPAIR_THE_FIRST_FALSE_DIRECT_N12_PROMOTION_GATE"
        ),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
