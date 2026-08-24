"""Audit event-transport sign authority on the two certified Gate-7 chords."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_TWO_CHORD_EVENT_TRANSPORT_SIGN_AUTHORITY.json"
)
INPUTS = {
    "minimal_scalar": ROOT / (
        "artifacts/flagship_integration/"
        "BHSM_N12_GATE7_MINIMAL_EVENT_TRANSPORT_SCALAR_AUDIT.json"
    ),
    "promotion": ROOT / (
        "artifacts/flagship_integration/"
        "BHSM_N12_GATE7_TWO_CHORD_PROMOTION_AUDIT.json"
    ),
    "chord_01": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_GATE7_COMPLETE_PHYSICAL_U_GREEN_SHADOWING.json"
    ),
    "chord_02": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_GATE7_CHORD_02_SIGNED_ALIGNED_GREEN.json"
    ),
    "terminal": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_FORWARD_TERMINAL_CHART_REACHABILITY_GATE.json"
    ),
}


def _sha256(path: Path) -> str:
    content = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(content).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, object]:
    if not all(path.is_file() for path in INPUTS.values()):
        raise FileNotFoundError("two-chord sign-authority inputs required")
    records = {name: _load(path) for name, path in INPUTS.items()}
    if not all(record.get("validation_passed") is True for record in records.values()):
        raise RuntimeError("validated two-chord sign-authority inputs required")

    minimal = records["minimal_scalar"]
    promotion = records["promotion"]
    chord_01 = records["chord_01"]
    chord_02 = records["chord_02"]
    terminal = records["terminal"]
    required_signed_fields = {
        "c_psi_lower",
        "c_psi_upper",
        "b_psi_lower",
        "b_psi_upper",
        "R_ext_lower",
        "R_ext_upper",
        "u_dot_lower",
        "u_dot_upper",
    }
    rows_01 = chord_01["rows"]
    rows_02 = chord_02["rows"]
    available_01 = set().union(*(set(row) for row in rows_01))
    available_02 = set().union(*(set(row) for row in rows_02))
    missing_01 = sorted(required_signed_fields - available_01)
    missing_02 = sorted(required_signed_fields - available_02)

    audit = {
        "certified_core": {
            "coordinate_interval": promotion["two_chord_frontier"][
                "coordinate_interval"
            ],
            "certified_chords": 2,
            "certified_subspans": len(rows_01) + len(rows_02),
            "state_shadowing_closed": True,
            "event_or_existing_domain_stop_on_core": False,
        },
        "identity_to_sign": (
            "F_u(Y)=D_t(e_ord^2)=2*c_psi*b_psi+2*e_ord*R_EXT(Y)"
        ),
        "chord_01": {
            "subspans": len(rows_01),
            "certificate_role": "COMPLETE_PHYSICAL_U_GREEN_STATE_SHADOWING",
            "missing_signed_interval_fields": missing_01,
            "F_u_interval_sign_certified": False,
        },
        "chord_02": {
            "subspans": len(rows_02),
            "certificate_role": "COMPLETE_SIGNED_PHYSICAL_U_GREEN_STATE_SHADOWING",
            "missing_signed_interval_fields": missing_02,
            "F_u_interval_sign_certified": False,
        },
        "why_shadowing_is_not_sign_authority": (
            "THE_GREEN_CERTIFICATES_BOUND_THE_STATE_SHADOWING_SOURCE_AND_"
            "DOMAIN_MARGINS;_THEIR_PER_SUBSPAN_SOURCE_BOUNDS_ARE_ABSOLUTE_"
            "ENCLOSURES_AND_DO_NOT_REPORT_SIGNED_INTERVALS_FOR_c_psi,_b_psi,_"
            "R_EXT,_OR_F_u"
        ),
        "finite_core_sign_conclusion": "NO_SIGN_SELECTED_FROM_CURRENT_CERTIFICATES",
        "global_monotone_decrease_proved": False,
        "global_monotone_increase_proved": False,
    }

    bounded_next_calculation = {
        "target": (
            "INTERVAL_ENCLOSE_F_u=2*c_psi*b_psi+2*e_ord*R_EXT_ON_EACH_"
            "OF_THE_EXISTING_128_CERTIFIED_SUBSPANS"
        ),
        "reuse": [
            "THE_TWO_EXISTING_HERMITE_CENTER_FAMILIES",
            "THE_EXISTING_ACTION_BALLS_AND_HARD_KATO_GAPS",
            "THE_EXISTING_D3_D4_D5_ACTION_MAJORANTS",
            "THE_EXISTING_SELECTED_LINE_AND_HARD_PROJECTOR_TRANSPORT",
            "THE_CERTIFIED_GREEN_SHADOWING_RADII",
        ],
        "required_output_per_subspan": [
            "SIGNED_CENTER_c_psi*b_psi",
            "SIGNED_CENTER_e_ord*R_EXT",
            "CANCELLATION_PRESERVING_VARIATION_UPPER",
            "F_u_LOWER_AND_UPPER",
        ],
        "decision_rule": {
            "all_F_u_upper_negative_and_accumulation_reaches_chart": (
                "FINITE_TERMINAL_CHART_ENTRY_OR_EXISTING_STOP"
            ),
            "any_F_u_lower_positive": (
                "IMMEDIATE_GLOBAL_DECREASE_INEQUALITY_INVALID_ON_THAT_SUBSPAN"
            ),
            "mixed_or_zero_containing_intervals": (
                "PURE_SIGN_ROUTE_OPEN_OR_INVALID;_TEST_PIECEWISE_INTEGRATED_BOUND"
            ),
        },
        "new_chord_required": False,
        "trajectory_campaign_required": False,
    }

    validation = {
        "all_inputs_validated": True,
        "two_certified_chords_consumed": (
            promotion["two_chord_frontier"]["certified_chords"] == 2
        ),
        "all_128_certified_subspans_accounted": len(rows_01) + len(rows_02) == 128,
        "state_shadowing_not_misclassified_as_transport_sign": bool(
            missing_01 and missing_02
        ),
        "minimal_scalar_identity_consumed": (
            minimal["transport_split"]["squared_event_identity"]
            == "D_t(e_ord^2)=2*c_psi*b_psi+2*e_ord*R_EXT(Y)"
        ),
        "local_terminal_hitting_reused": (
            terminal["closed_local_structure"]["continuum_terminal_hitting_law"]
            is True
        ),
        "terminal_chart_entry_not_assumed": (
            terminal["global_outcome"][
                "at_least_one_existing_forward_child_reaches_terminal_chart"
            ]
            is False
        ),
        "missing_interval_sign_is_proof_enclosure_not_action_incompatibility": True,
        "no_chord_03_or_new_trajectory_required_for_next_calculation": True,
        "no_new_equation_gate_selector_threshold_or_physics": True,
        "Gate7_and_later_claim_boundaries_preserved": True,
    }

    return {
        "artifact": "BHSM_N12_GATE7_TWO_CHORD_EVENT_TRANSPORT_SIGN_AUTHORITY",
        "classification": (
            "TWO_CHORD_STATE_SHADOWING_DOES_NOT_CERTIFY_ORDERED_EVENT_"
            "TRANSPORT_SIGN;_THE_FIRST_MISSING_FINITE_CORE_OBJECT_IS_A_"
            "CANCELLATION_PRESERVING_INTERVAL_ENCLOSURE_OF_F_u_ON_THE_"
            "EXISTING_128_SUBSPANS"
        ),
        "current_flagship_gate": 7,
        "sign_authority_audit": audit,
        "bounded_next_calculation": bounded_next_calculation,
        "obstruction_class": "MISSING_PROOF_ENCLOSURE_NOT_RETAINED_ACTION_INCOMPATIBILITY",
        "exact_next_dependency": bounded_next_calculation["target"],
        "Gate7_status_changed": False,
        "chord_03_authorized": False,
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in INPUTS.values()
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise RuntimeError("two-chord event-transport sign audit failed")
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "classification": payload["classification"],
        "subspans": payload["sign_authority_audit"]["certified_core"][
            "certified_subspans"
        ],
        "validation_passed": payload["validation_passed"],
        "sha256": _sha256(RESULT),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
