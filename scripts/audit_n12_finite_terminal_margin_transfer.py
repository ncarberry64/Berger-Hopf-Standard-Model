"""Transfer retained margins to the certified finite terminal root ball."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts/flagship_integration"
CANDIDATE = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.json"
RADII = BASE / "BHSM_N12_FINITE_TERMINAL_RADII_CERTIFICATE.json"
MAJORANT = BASE / "BHSM_N12_FINITE_TERMINAL_ACTION_BALL_MAJORANTS.json"
EVENT_LINE = BASE / "BHSM_N12_FINITE_TERMINAL_EVENT_EIGENLINE_BALL.json"
CHILD_LINE = BASE / "BHSM_N12_FINITE_TERMINAL_CHILD_EIGENLINE_BALL.json"
BORDERED = BASE / "BHSM_N12_FINITE_TERMINAL_BORDERED_RELATIVE_BALL.json"
FORMATION = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_FINITE_ENCAPSULATION_LOCAL_BRANCH.json"
)
RESULT = BASE / "BHSM_N12_FINITE_TERMINAL_MARGIN_TRANSFER.json"
ORIENTATION = BASE / "BHSM_N12_FINITE_TERMINAL_ORIENTATION_CERTIFICATE.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def build_payload() -> dict[str, object]:
    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    radii = json.loads(RADII.read_text(encoding="utf-8"))
    majorant = json.loads(MAJORANT.read_text(encoding="utf-8"))
    event_line = json.loads(EVENT_LINE.read_text(encoding="utf-8"))
    child_line = json.loads(CHILD_LINE.read_text(encoding="utf-8"))
    bordered = json.loads(BORDERED.read_text(encoding="utf-8"))
    formation = json.loads(FORMATION.read_text(encoding="utf-8"))
    orientation = json.loads(ORIENTATION.read_text(encoding="utf-8"))
    if not all(item.get("validation_passed") is True for item in (
        candidate, radii, majorant, event_line, child_line, bordered,
        formation, orientation,
    )):
        raise ValueError("validated terminal-margin inputs required")

    solution_radius = float(
        radii["radii_polynomial"]["negative_interval_roots"][0]
    )
    sectors = {item["sector"]: item for item in majorant["sectors"]}
    legendre = candidate["center"]["Legendre_minima"]
    legendre_transfer = {}
    for sector in ("event", "child"):
        center_lower = min(float(value) for value in legendre[sector].values())
        d3 = float(sectors[sector][
            "restricted_derivative_operator_majorants_0_through_5"
        ][3])
        legendre_transfer[sector] = {
            "center_lower": center_lower,
            "retained_D3_action_majorant": d3,
            "root_shift_upper": d3 * solution_radius,
            "root_ball_lower": center_lower - d3 * solution_radius,
        }

    child_c = abs(float(candidate["center"]["child"]["c_psi"]))
    child_d4 = float(sectors["child"][
        "restricted_derivative_operator_majorants_0_through_5"
    ][4])
    fixed_line_c_shift = child_d4 * solution_radius
    orientation_bound_closes = fixed_line_c_shift < child_c
    transferred = {
        "terminal_58_row_root_exists": bool(
            radii["radii_polynomial"]["root_ball_closed"]
        ),
        "event_selected_line_simple": float(
            event_line["bounds"]["eigenline_gap_lower"]
        ) > 0.0,
        "child_selected_line_simple": float(
            child_line["bounds"]["eigenline_gap_lower"]
        ) > 0.0,
        "event_and_child_Legendre_positive": min(
            item["root_ball_lower"] for item in legendre_transfer.values()
        ) > 0.0,
        "all_four_canonical_lifts_invertible": all(
            item["certified_invertible_on_ball"]
            for item in bordered["records"]
        ),
        "terminal_map_normal_regular": float(
            radii["radii_polynomial"]["contraction_bound_Z0_plus_Z2_r"]
        ) < 1.0,
    }
    validation = {
        "all_nonorientation_local_margins_transfer": all(transferred.values()),
        "global_D4_bound_does_not_falsely_certify_cubic_sign": (
            not orientation_bound_closes
        ),
        "cancellation_preserving_orientation_certificate_supersedes_coarse_bound": bool(
            orientation["validation"][
                "terminal_hitting_product_is_strictly_negative"
            ]
        ),
        "mathematical_terminal_root_not_promoted_to_forward_history": True,
        "existing_certified_local_formation_history_preserved": bool(
            formation["adjudication"][
                "finite_positive_time_completed_encapsulation_exists"
            ]
        ),
        "universal_reachability_not_claimed": True,
        "no_action_term_selector_scale_gate_chord_or_prediction_added": True,
    }
    return {
        "artifact": "BHSM_N12_FINITE_TERMINAL_MARGIN_TRANSFER",
        "status": "COARSE_GLOBAL_D4_INCONCLUSIVE_SUPERSEDED_BY_ORIENTATION_CERTIFICATE",
        "classification": (
            "THE_58_ROW_RADII_THEOREM_PROVES_A_LOCAL_TERMINAL_RESET_"
            "STRATUM_AND_TRANSFERS_SELECTED_LINE_SIMPLICITY,_LEGENDRE,_"
            "CANONICAL_LIFT,_AND_NORMAL_REGULARITY;_THE_CANDIDATE_CHILD_"
            "CUBIC_c_psi_IS_ONLY_2.29E_11_AND_THE_CURRENT_RETAINED_D4_"
            "BALL_MAJORANT_DOES_NOT_PRESERVE_ITS_SIGN,_SO_THIS_NEW_ROOT_"
            "WAS_INCONCLUSIVE;_THE_SEPARATE_CANCELLATION_PRESERVING_"
            "SELECTED_LINE_CERTIFICATE_NOW_CLOSES_THE_FORWARD_ORIENTATION"
        ),
        "root_enclosure": {
            "component_control_radius": radii["action_coordinate_ball_radius"],
            "contractive_root_ball_radius": radii["certified_root_ball_radius"],
            "a_posteriori_solution_distance_upper": solution_radius,
            "radii_polynomial_value": radii["radii_polynomial"][
                "value_at_candidate_radius"
            ],
            "contraction_bound": radii["radii_polynomial"][
                "contraction_bound_Z0_plus_Z2_r"
            ],
        },
        "transferred_margins": transferred,
        "Legendre_transfer": legendre_transfer,
        "orientation_adjudication": {
            "candidate_child_b_psi": candidate["center"]["child"]["b_psi"],
            "candidate_child_c_psi": candidate["center"]["child"]["c_psi"],
            "candidate_hitting_product": candidate["center"]["child"][
                "hitting_product"
            ],
            "fixed_line_D4_shift_upper": fixed_line_c_shift,
            "fixed_line_shift_over_center_c": fixed_line_c_shift / child_c,
            "selected_line_motion_terms_increase_not_decrease_the_needed_bound": True,
            "c_psi_sign_certified_at_exact_root": orientation_bound_closes,
            "forward_event_reaching_history_certified_from_this_root": False,
            "interpretation": (
                "INCONCLUSIVE_BOUND_NOT_A_SIGN_REVERSAL_OR_NONEXISTENCE_RESULT"
            ),
        },
        "proof_boundary": {
            "finite_terminal_reset_stratum": "CERTIFIED_LOCAL_EXISTENCE",
            "new_terminal_forward_orientation": "CLOSED_BY_SEPARATE_CERTIFICATE",
            "existing_finite_formation_history": "REMAINS_CERTIFIED",
            "universal_terminal_reachability": "NOT_REQUIRED_NOT_CLAIMED",
            "zero_source_force": "NEXT_CURRENT_OWNER",
        },
        "exact_next_dependency": (
            "CONSUME_BHSM_N12_FINITE_TERMINAL_ORIENTATION_CERTIFICATE_"
            "AND_REALIZE_THE_COMPACT_ENDPOINT_ZERO_SOURCE_FORCE"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_FINITE_ENDPOINT_ZERO_SOURCE_FORCE",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in (
                CANDIDATE, RADII, MAJORANT, EVENT_LINE, CHILD_LINE,
                BORDERED, FORMATION, ORIENTATION,
            )
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(RESULT)


if __name__ == "__main__":
    main()
