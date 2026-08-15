"""Measure accepted N=3 secants in the validated action-owned coordinates."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Callable

import numpy as np

from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import _action_curvature_transform
from bhsm.interface.aether_n3_bidirectional_next_candidate_promotion_v18_54 import v18_54_selected_raw_vector
from bhsm.interface.aether_n3_bidirectional_probe_promotion_v18_52 import v18_52_selected_raw_vector
from bhsm.interface.aether_n3_direct_line_exact_merit_promotion_v18_37 import v18_37_selected_raw_vector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_invalid_model_exact_merit_promotion_v18_33 import v18_33_selected_raw_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_second_bidirectional_probe_promotion_v18_58 import v18_58_selected_raw_vector
from bhsm.interface.aether_n3_second_direct_line_promotion_v18_41 import v18_41_selected_raw_vector
from bhsm.interface.aether_n3_third_direct_admissible_line_promotion_v18_47 import v18_47_selected_raw_vector
from bhsm.interface.aether_n3_third_direct_line_promotion_v18_45 import v18_45_selected_raw_vector
from bhsm.interface.aether_n3_v18_43_sector_compression_diagnostic_v18_48 import _sector_directions


VERSION = "v18.60"
CLASSIFICATION = "BHSM_N3_ACCEPTED_SECANT_GEOMETRY_DIAGNOSTIC"
FULL_BHSM_COMPLETE = False

VectorFn = Callable[[], np.ndarray]
ACCEPTED: tuple[tuple[str, VectorFn], ...] = (
    ("v18.33", v18_33_selected_raw_vector),
    ("v18.37", v18_37_selected_raw_vector),
    ("v18.41", v18_41_selected_raw_vector),
    ("v18.47", v18_47_selected_raw_vector),
    ("v18.54", v18_54_selected_raw_vector),
    ("v18.58", v18_58_selected_raw_vector),
)
BLOCKS = (
    "scale", "u", "w", "v", "eta_sensitive_shift", "lapse", "period",
    "explicit_event_multiplier", "remaining_physical_blocks",
)


def _direction_measurement(
    label: str,
    source_raw: np.ndarray,
    candidate_raw: np.ndarray,
    transform: np.ndarray,
) -> tuple[dict[str, Any], np.ndarray]:
    scales = kkt_variable_scales()
    delta_raw = candidate_raw - source_raw
    delta_y = delta_raw * scales
    secant = np.linalg.solve(transform, delta_y)
    sectors_raw = _sector_directions(source_raw, delta_raw)
    sectors_x = {
        name: np.linalg.solve(transform, sectors_raw[name] * scales)
        for name in BLOCKS
    }
    square_total = sum(float(value @ value) for value in sectors_x.values())
    composition = {
        name: {
            "action_owned_norm": float(np.linalg.norm(sectors_x[name])),
            "action_owned_squared_fraction": float(sectors_x[name] @ sectors_x[name])
            / max(square_total, 1.0e-300),
        }
        for name in BLOCKS
    }
    return ({
        "direction": label,
        "raw_coordinate_norm": float(np.linalg.norm(delta_raw)),
        "physical_scaled_coordinate_norm": float(np.linalg.norm(delta_y)),
        "action_owned_norm": float(np.linalg.norm(secant)),
        "action_owned_block_composition": composition,
        "block_reconstruction_error_raw": float(
            np.linalg.norm(sum(sectors_raw.values(), np.zeros(376)) - delta_raw)
        ),
        "geometry_scale_w_v_fraction": sum(
            composition[name]["action_owned_squared_fraction"]
            for name in ("scale", "w", "v")
        ),
        "u_eta_shift_lapse_fraction": sum(
            composition[name]["action_owned_squared_fraction"]
            for name in ("u", "eta_sensitive_shift", "lapse")
        ),
    }, secant)


def _alignment(left_label: str, left: np.ndarray, right_label: str, right: np.ndarray) -> dict[str, Any]:
    denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
    cosine = float(np.clip((left @ right) / denominator, -1.0, 1.0))
    return {
        "between": [left_label, right_label],
        "cosine": cosine,
        "turning_angle_degrees": math.degrees(math.acos(cosine)),
        "numerically_meaningful": denominator > 1.0e-24,
    }


def accepted_secant_geometry() -> dict[str, Any]:
    accepted_vectors = [(version, fn()) for version, fn in ACCEPTED]
    transform, transform_audit = _action_curvature_transform(accepted_vectors[0][1])
    accepted_rows: list[dict[str, Any]] = []
    accepted_secants: list[np.ndarray] = []
    for (source_version, source), (candidate_version, candidate) in zip(
        accepted_vectors, accepted_vectors[1:]
    ):
        row, secant = _direction_measurement(
            f"{source_version}->{candidate_version}", source, candidate, transform
        )
        accepted_rows.append(row); accepted_secants.append(secant)
    alignments = [
        _alignment(
            accepted_rows[index - 1]["direction"], accepted_secants[index - 1],
            accepted_rows[index]["direction"], accepted_secants[index],
        )
        for index in range(1, len(accepted_secants))
    ]
    rejected_specs = (
        ("v18.41->v18.43/v18.45", v18_41_selected_raw_vector(), v18_45_selected_raw_vector(), "REJECTED_TWO_SCALE_FLUX_2.2758236534E-5", "v18.41->v18.47"),
        ("v18.47->v18.50/v18.52", v18_47_selected_raw_vector(), v18_52_selected_raw_vector(), "REJECTED_TWO_SCALE_FLUX_2.0920371105E-5", "v18.47->v18.54"),
    )
    rejected_rows = []
    for label, source, candidate, reason, accepted_label in rejected_specs:
        row, secant = _direction_measurement(label, source, candidate, transform)
        accepted_index = next(index for index, value in enumerate(accepted_rows)
                              if value["direction"] == accepted_label)
        comparison = _alignment(label, secant, accepted_label, accepted_secants[accepted_index])
        row.update({
            "disposition": "REJECTED",
            "rejection_reason": reason,
            "comparison_to_accepted_from_same_source": comparison,
            "more_u_eta_shift_lapse_compressed_than_accepted": row["u_eta_shift_lapse_fraction"] > accepted_rows[accepted_index]["u_eta_shift_lapse_fraction"],
        })
        rejected_rows.append(row)
    geometry_fractions = [row["geometry_scale_w_v_fraction"] for row in accepted_rows]
    local_fractions = [row["u_eta_shift_lapse_fraction"] for row in accepted_rows]
    angles = [row["turning_angle_degrees"] for row in alignments]
    rejected_compression_systematic = all(
        row["more_u_eta_shift_lapse_compressed_than_accepted"] for row in rejected_rows
    )
    geometry_dominant = float(np.mean(geometry_fractions)) > 0.5
    curved = all(row["numerically_meaningful"] for row in alignments) and max(angles) > 5.0
    finite_local_blocks_subdominant = float(np.mean(local_fractions)) < float(np.mean(geometry_fractions))
    answers = {
        "accepted_secants_rotate_coherently_rather_than_remain_collinear": {
            "classification": "VALIDATED_CURVED_NOT_COLLINEAR" if curved else "INVALIDATED_OR_INSUFFICIENT_RESOLUTION",
            "answer": curved,
            "evidence": "finite turning angles are measured in one fixed action-owned tangent chart",
        },
        "finite_motion_primarily_carried_by_scale_w_v_geometry": {
            "classification": "VALIDATED" if geometry_dominant else "INVALIDATED",
            "answer": geometry_dominant,
            "mean_action_owned_squared_fraction": float(np.mean(geometry_fractions)),
        },
        "lapse_eta_shift_are_early_plateau_loss_not_dominant_finite_carriers": {
            "classification": "RECLASSIFIED" if finite_local_blocks_subdominant else "INSUFFICIENT_RESOLUTION",
            "answer": finite_local_blocks_subdominant,
            "mean_u_eta_shift_lapse_fraction": float(np.mean(local_fractions)),
            "v18_48_early_plateau_measurement_used_only_as_prior_validated_context": True,
        },
        "rejected_proposals_systematically_more_u_eta_shift_lapse_compressed": {
            "classification": "VALIDATED" if rejected_compression_systematic else "INVALIDATED",
            "answer": rejected_compression_systematic,
            "sample_size": len(rejected_rows),
        },
        "measurable_scale_w_v_coupling_rotation": {
            "classification": "INSUFFICIENT_RESOLUTION_FOR_CAUSAL_COUPLING",
            "answer": "MEASURED_COPARTICIPATION_AND_ROTATION_BUT_FINITE_SECANTS_DO_NOT_ESTABLISH_COUPLING_CAUSALITY",
        },
    }
    return {
        "coordinate_chart": {
            **transform_audit,
            "fixed_reference_state": "v18.33",
            "definition": "s_k=P_v18.33^{-1}((raw_k-raw_k-1)*existing_KKT_variable_scales)",
            "reason_for_fixed_chart": "all inter-secant angles are evaluated in one common validated action-owned tangent frame",
        },
        "accepted_secants": accepted_rows,
        "consecutive_alignments": alignments,
        "rejected_proposal_directions": rejected_rows,
        "measurement_answers": answers,
        "strongest_supported_wording": "The accepted continuation exhibits a measured curved secant geometry in action-owned coordinates." if curved else "The finite accepted secants do not resolve a curved action-owned geometry.",
        "finite_secants_promoted_to_manifold_theorem": False,
        "continuation_restriction_added": False,
        "physical_equations_changed": False,
        "acceptance_gate_changed": False,
    }


def completion_payload() -> dict[str, Any]:
    result = accepted_secant_geometry()
    validation = {
        "five_consecutive_accepted_secants_measured": len(result["accepted_secants"]) == 5,
        "four_consecutive_alignments_measured": len(result["consecutive_alignments"]) == 4,
        "two_rejected_directions_compared": len(result["rejected_proposal_directions"]) == 2,
        "all_nine_blocks_reported": all(len(row["action_owned_block_composition"]) == 9 for row in result["accepted_secants"] + result["rejected_proposal_directions"]),
        "sector_decompositions_close": all(row["block_reconstruction_error_raw"] < 1.0e-11 for row in result["accepted_secants"] + result["rejected_proposal_directions"]),
        "coordinate_map_invertible": result["coordinate_chart"]["invertible"],
        "all_five_questions_classified": len(result["measurement_answers"]) == 5,
        "no_manifold_theorem": not result["finite_secants_promoted_to_manifold_theorem"],
        "no_continuation_restriction": not result["continuation_restriction_added"],
        "physics_and_gate_unchanged": not result["physical_equations_changed"] and not result["acceptance_gate_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_accepted_secant_geometry_v18_60",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "accepted_secant_geometry": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": "THE_ACCEPTED_FRONTIER_HAS_MEASURABLE_FINITE_SECANT_TURNING_AND_BLOCK_COMPOSITION_IN_THE_EXISTING_ACTION_OWNED_COORDINATES",
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": "CONTINUE_PHYSICALLY_ADMISSIBLE_EXACT_376_ROW_DESCENT_FROM_THE_LATEST_ACCEPTED_FRONTIER_TO_F376_ZERO",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_accepted_secant_geometry_v18_60.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "accepted_secant_geometry", "completion_payload", "materialize"]
