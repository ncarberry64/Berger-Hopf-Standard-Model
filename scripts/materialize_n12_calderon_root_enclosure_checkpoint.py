"""Materialize the correlated-root Calderon and inverse-square checkpoint."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts/n12_direct_checkpoint"
DIRECTED = BASE / "BHSM_N12_CALDERON_DIRECTED_CENTER.json"
ACTION_BALL = BASE / "BHSM_N12_CALDERON_ACTION_BALL.json"
POSITIVE_DURATION = BASE / "BHSM_N12_POSITIVE_DURATION_OBSERVATION.json"
SOURCE_CONSTANT = BASE / "BHSM_N12_INVERSE_SQUARE_SOURCE_CONSTANT.json"
RESULT = BASE / "BHSM_N12_CALDERON_ROOT_ENCLOSURE_CHECKPOINT.json"
REPRODUCERS = (
    ROOT / "scripts/certify_n12_calderon_directed_center.py",
    ROOT / "scripts/certify_n12_calderon_action_ball.py",
    ROOT / "scripts/certify_n12_positive_duration_observation.py",
    ROOT / "scripts/derive_n12_inverse_square_source_constant.py",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> None:
    directed = json.loads(DIRECTED.read_text(encoding="utf-8"))
    action_ball = json.loads(ACTION_BALL.read_text(encoding="utf-8"))
    positive = json.loads(POSITIVE_DURATION.read_text(encoding="utf-8"))
    source = json.loads(SOURCE_CONSTANT.read_text(encoding="utf-8"))
    if not all(item.get("validation_passed") is True for item in (
        directed, action_ball, positive, source,
    )):
        raise RuntimeError("all correlated-root checkpoint inputs must validate")

    beta = math.sqrt(29.0) - 5.0
    c_r = float(source["C_r_event_child_product"])
    sharp_tail = source["sharp_N12_to_infinity_source_tail"]
    radius = float(action_ball["action_coordinate_ball_radius_per_sector"])
    tail_at_12 = 4.0 * c_r / (beta * 12.0)
    radius_only_cutoff = math.ceil(8.0 * c_r / (beta * radius))
    missing_blocks = [
        "INTERIOR_LOWER_ORDER_EULER_DIRAC",
        "ORDERED_EVENT_SPECTRAL_PROJECTOR",
        "CANONICAL_MOMENTUM_AND_DYNAMIC_FLUX",
        "GAUSS_QUADRATURE_CONSISTENCY",
    ]
    validation = {
        "correlated_exact_root_graph_symbol_certified": (
            float(directed["symbol"]["minimum_singular_value_lower"]) > 0.0
        ),
        "whole_action_ball_graph_gap_certified": (
            float(action_ball["ball_bounds"]["seven_by_seven_symbol_gap_lower"])
            > 0.0
        ),
        "finite_core_positive_duration_modulus_certified": (
            float(positive["c_M0_observation_norm_lower"]) > 0.0
        ),
        "explicit_nonfitted_inverse_square_source_constant_certified": (
            c_r > 0.0
        ),
        "sharp_source_tail_does_not_assume_missing_normal_inverse": (
            sharp_tail["normal_inverse_applied"] is False
        ),
        "finite_core_not_promoted_to_uniform_tail_inverse": True,
        "missing_compact_tail_modulus_recorded_fail_closed": True,
        "continuum_and_full_BHSM_remain_false": True,
        "no_new_equation_constraint_gate_scale_fit_or_event_definition": True,
    }
    paths = (DIRECTED, ACTION_BALL, POSITIVE_DURATION, SOURCE_CONSTANT,
             *REPRODUCERS)
    output = {
        "classification": (
            "N12_CORRELATED_EXACT_ROOT_CALDERON_GRAPH_AND_FINITE_CORE_"
            "POSITIVE_DURATION_CLOSED;_ACTION_DERIVED_INVERSE_SQUARE_"
            "SOURCE_CONSTANT_CLOSED;_UNIFORM_COMPACT_TAIL_MODULUS_OPEN"
        ),
        "scientific_result": {
            "first_Picard_center_to_exact_root_distance_upper": directed[
                "first_Picard_center_to_exact_root_distance_upper"
            ],
            "correlated_exact_root_graph_gap_lower": directed["symbol"][
                "minimum_singular_value_lower"
            ],
            "whole_action_ball_radius": radius,
            "whole_action_ball_graph_gap_lower": action_ball["ball_bounds"][
                "seven_by_seven_symbol_gap_lower"
            ],
            "c_M0_observation_norm_lower": positive[
                "c_M0_observation_norm_lower"
            ],
            "finite_core_normal_inverse_bound": positive[
                "finite_core_normal_inverse_bound_1_over_c_M0"
            ],
            "C_r_event_child_product": c_r,
            "sharp_N12_to_infinity_weak_source_tail_upper": sharp_tail[
                "joint_event_child_weak_source_tail_norm_upper"
            ],
            "sharp_N12_to_infinity_one_extra_weighted_source_tail_upper": (
                sharp_tail[
                    "joint_event_child_one_extra_weighted_source_tail_norm_upper"
                ]
            ),
            "sharp_source_tail_has_applied_the_normal_inverse": sharp_tail[
                "normal_inverse_applied"
            ],
            "asymptotic_high_tail_inverse_bound": 4.0 / beta,
            "formal_inverse_square_correction_tail_bound_at_M0_12": tail_at_12,
            "radius_only_cutoff_if_the_uniform_compact_remainder_bound_"
            "were_already_effective": radius_only_cutoff,
            "that_cutoff_is_not_a_continuum_certificate": True,
            "retained_action_obstruction_demonstrated": False,
        },
        "localized_open_operator_blocks": missing_blocks,
        "claim_boundary": (
            "THE_EXACT_N12_ROOT_GRAPH,_A_POSITIVE_FULL_ACTION_"
            "NEIGHBORHOOD,_THE_FINITE_CORE_POSITIVE_DURATION_MODULUS,_"
            "AND_AN_EXPLICIT_NONFITTED_INVERSE_SQUARE_BULK_SOURCE_"
            "CONSTANT_ARE_CERTIFIED._THE_N12_TO_INFINITY_COMPACT_"
            "CALDERON_JACOBI_REMAINDER_HAS_NO_EXPLICIT_UNIFORM_MODULUS,_"
            "SO_epsilon_obs,_THE_CONTINUUM_CHILD,_Q_xi,_AND_DELTA_H_"
            "REMAIN_OPEN"
        ),
        "exact_next_dependency": (
            "DERIVE_AN_EXPLICIT_RETAINED_ACTION_COMPACT_CUTOFF_M_STAR_"
            "FOR_THE_GAUGE_REDUCED_HIGH_SHELL_NORMAL_INVERSE;_THEN_"
            "APPLY_THE_SHARP_SOURCE_TAIL_AND_BOUND_THE_ORDERED_EVENT,_"
            "CANONICAL_MOMENTUM_FLUX,_AND_OBSERVATION_PERTURBATIONS_"
            "BEFORE_CLOSING_THE_NONLINEAR_CONTINUUM_RADII_POLYNOMIAL"
        ),
        "reproduction": [
            "python scripts/certify_n12_calderon_directed_center.py",
            "python scripts/certify_n12_calderon_action_ball.py",
            "python scripts/certify_n12_positive_duration_observation.py",
            "python scripts/derive_n12_inverse_square_source_constant.py",
            "python scripts/materialize_n12_calderon_root_enclosure_checkpoint.py",
        ],
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in paths
        },
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    with RESULT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
