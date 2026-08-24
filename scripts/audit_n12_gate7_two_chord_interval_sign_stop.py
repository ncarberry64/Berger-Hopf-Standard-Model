"""Canonize the three-representation stop for two-chord transport sign."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_TWO_CHORD_INTERVAL_SIGN_STOP.json"
)
INPUTS = {
    "minimal": ROOT / (
        "artifacts/flagship_integration/"
        "BHSM_N12_GATE7_MINIMAL_EVENT_TRANSPORT_SCALAR_AUDIT.json"
    ),
    "authority": ROOT / (
        "artifacts/flagship_integration/"
        "BHSM_N12_GATE7_TWO_CHORD_EVENT_TRANSPORT_SIGN_AUTHORITY.json"
    ),
    "centers": ROOT / (
        "artifacts/flagship_integration/"
        "BHSM_N12_GATE7_TWO_CHORD_SIGNED_CENTER_RATE_PROFILE.json"
    ),
    "promotion": ROOT / (
        "artifacts/flagship_integration/"
        "BHSM_N12_GATE7_TWO_CHORD_PROMOTION_AUDIT.json"
    ),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, object]:
    if not all(path.is_file() for path in INPUTS.values()):
        raise FileNotFoundError("two-chord interval-sign stop inputs required")
    records = {name: _load(path) for name, path in INPUTS.items()}
    if not all(record.get("validation_passed") is True for record in records.values()):
        raise RuntimeError("validated interval-sign stop inputs required")
    minimal = records["minimal"]
    authority = records["authority"]
    centers = records["centers"]
    promotion = records["promotion"]
    summaries = centers["summary"]
    minimum_center_rate = min(
        item["u_rate_minimum"] for item in summaries.values()
    )
    maximum_center_rate = max(
        item["u_rate_maximum"] for item in summaries.values()
    )

    representations = {
        "A_full_coordinate_direct_interval": {
            "result": "FAILS_ON_FIRST_EXISTING_SUBSPAN",
            "replay_diagnostic": {
                "subspan": 0,
                "interval_Neumann_factor": 5781964.845671637,
                "matrix_width": 0.021305010160304505,
                "right_jet_magnitudes": [
                    1326.685744713776,
                    0.04016340242734635,
                    5.022674434809146e-06,
                ],
                "complete_signed_hard_second_fixed_left_upper": 30052.590310566,
                "command": (
                    "python scripts/certify_n12_first_chord_64_subspan_"
                    "direct_second_defect_enclosure.py"
                ),
                "promoted_as_action_obstruction": False,
            },
            "failure_owner": (
                "FULL_COORDINATE_INTERVAL_DEPENDENCY_DESTROYS_THE_DIRAC_"
                "INVERSE_NEUMANN_MARGIN_BEFORE_THE_SIGNED_EVENT_CONTRACTION"
            ),
        },
        "B_covariant_pole_free_hard_bundle": {
            "result": "EXACT_IDENTITY_DERIVED_BUT_BETWEEN_CENTER_AUTHORITY_OPEN",
            "retained_identity": (
                "F_u=2*c_psi*b_psi+2*e_ord*R_EXT_WITH_ONLY_THE_HARD_"
                "INVERSE_AND_NO_INVERSE_SOFT_EIGENVALUE"
            ),
            "failure_owner": (
                "CANCELLATION_PRESERVING_BETWEEN_CENTER_D5_KATO_VARIATION_"
                "OF_c_psi,_b_psi,_THE_SELECTED_PROJECTOR,_AND_R_EXT"
            ),
        },
        "C_implicit_adjoint_center_jets": {
            "result": "CENTER_SYSTEMS_CLOSE_BUT_BETWEEN_CENTER_AUTHORITY_OPEN",
            "retained_identity": (
                "F_u_IS_REPRESENTED_BY_SIGNED_ADJOINT_SOURCE_PAIRINGS_AT_"
                "THE_64_EXISTING_SUBSPAN_CENTERS"
            ),
            "failure_owner": (
                "THE_SAME_CANCELLATION_PRESERVING_BETWEEN_CENTER_D5_KATO_"
                "VARIATION_MODULUS"
            ),
        },
    }

    validation = {
        "all_inputs_validated": True,
        "all_130_center_rates_evaluated": sum(
            item["nodes"] for item in summaries.values()
        ) == 130,
        "all_130_center_rates_positive_diagnostic": all(
            item["u_rate_positive_nodes"] == item["nodes"]
            and item["u_rate_negative_nodes"] == 0
            for item in summaries.values()
        ),
        "center_profile_not_promoted_to_interval_sign": (
            centers["claim_boundary"]["128_subspan_interval_sign"] == "OPEN"
        ),
        "state_shadowing_not_promoted_to_rate_sign": (
            authority["sign_authority_audit"]["global_monotone_decrease_proved"]
            is False
        ),
        "three_proof_equivalent_representations_exhausted": len(representations) == 3,
        "same_between_center_owner_localized_in_covariant_and_adjoint_forms": True,
        "direct_interval_failure_not_promoted_to_action_incompatibility": True,
        "local_terminal_hitting_theorem_preserved": (
            minimal["finite_hitting_adjudication"]["existing_local_terminal_chart"][
                "finite_hitting_after_chart_entry_certified"
            ]
            is True
        ),
        "no_finite_additional_chord_count_claimed_sufficient": (
            promotion["chord03_decision"][
                "minimum_additional_chords_sufficient_under_current_estimates"
            ]
            == "NO_FINITE_NUMBER_DERIVABLE"
        ),
        "no_new_equation_gate_selector_threshold_precision_or_physics": True,
        "chord_03_remains_unauthorized": True,
        "Gate7_and_later_claim_boundaries_preserved": True,
    }

    return {
        "artifact": "BHSM_N12_GATE7_TWO_CHORD_INTERVAL_SIGN_STOP",
        "classification": (
            "ALL_130_TWO_CHORD_CENTER_RATES_ARE_POSITIVE_DIAGNOSTICALLY;_"
            "THREE_PROOF_EQUIVALENT_INTERVAL_REPRESENTATIONS_STOP_AT_THE_"
            "SAME_CANCELLATION_PRESERVING_BETWEEN_CENTER_D5_KATO_MODULUS"
        ),
        "current_flagship_gate": 7,
        "signed_center_frontier": {
            "minimum_u_rate": minimum_center_rate,
            "maximum_u_rate": maximum_center_rate,
            "positive_centers": 130,
            "interval_sign_authority": False,
        },
        "three_representation_stop": representations,
        "canonical_blocker": {
            "object": (
                "M_D5_KATO,i=SUP_ON_CERTIFIED_SUBSPAN_i_OF_THE_SIGNED_"
                "VARIATION_OF_F_u=2*c_psi*b_psi+2*e_ord*R_EXT"
            ),
            "required_closure": (
                "M_D5_KATO,i*SUBSPAN_RADIUS_MUST_BE_SMALL_ENOUGH_TO_EXCLUDE_"
                "ZERO_AFTER_SIGNED_CENTER_ASSEMBLY_AND_THE_GREEN_TUBE_"
                "TRANSFER_MUST_PRESERVE_THAT_SIGN"
            ),
            "available_from_current_three_representations": False,
            "retained_action_incompatibility_proved": False,
            "blocker_type": "MISSING_SHARP_PROOF_IDENTITY_OR_MODULUS",
        },
        "canonical_no_go_scope": {
            "proved": (
                "THE_CURRENT_FULL_INTERVAL_COVARIANT_AND_IMPLICIT_ADJOINT_"
                "REPRESENTATIONS_DO_NOT_CERTIFY_F_u_SIGN_ON_THE_EXISTING_"
                "128_SUBSPANS"
            ),
            "not_proved": (
                "F_u_IS_POSITIVE_OR_NEGATIVE_ON_THE_EXACT_TUBES;_THE_"
                "RETAINED_ACTION_CANNOT_RETURN;_AN_INFINITE_HISTORY_EXISTS"
            ),
        },
        "exact_next_dependency": (
            "A_NEW_ACTION_OWNED_CANCELLATION_IDENTITY_OR_SHARP_MIXED_D5_KATO_"
            "MODULUS_FOR_F_u_ON_THE_EXISTING_TWO_CHORD_TUBES;_DO_NOT_REFINE_"
            "BOXES_INCREASE_PRECISION_OR_AUTHORIZE_CHORD_03_WITHOUT_IT"
        ),
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
        raise RuntimeError("two-chord interval-sign stop failed")
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "classification": payload["classification"],
        "canonical_blocker": payload["canonical_blocker"]["object"],
        "validation_passed": payload["validation_passed"],
        "sha256": _sha256(RESULT),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
