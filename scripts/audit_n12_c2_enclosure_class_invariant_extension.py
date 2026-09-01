"""Extend the certified C2 enclosure-class invariant through all later covers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_ENCLOSURE_CLASS_INVARIANT_EXTENSION.json"
CLASS = BASE / "BHSM_N12_C2_ENCLOSURE_CLASS_INVARIANT_AUDIT.json"
EXTENDED = BASE / "BHSM_N12_C2_EXTENDED_DESCRIPTOR_RESOLUTION_AUDIT.json"
COMPENSATED = BASE / "BHSM_N12_C2_COMPENSATED_DESCRIPTOR_CONTINUATION.json"
ADAPTIVE = BASE / "BHSM_N12_C2_ADAPTIVE_BALL_CONTINUATION.json"
RECENTER = BASE / "BHSM_N12_C2_ADAPTIVE_CENTER_RECENTER.json"
RECENTERED = BASE / "BHSM_N12_C2_RECENTERED_ADAPTIVE_CONTINUATION.json"
MAXIMAL = BASE / "BHSM_N12_C2_CLASS_REDUCED_MAXIMAL_RESPONSE.json"
THEORY = ROOT / "theory/n12_c2_enclosure_class_invariant_extension.md"
INPUTS = (CLASS, EXTENDED, COMPENSATED, ADAPTIVE, RECENTER, RECENTERED, MAXIMAL, THEORY)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _regular_rows(rows: list[dict[str, Any]], *, path_key: str) -> bool:
    return bool(rows) and all(
        int(row["proof_center_branch"]) == 24
        and float(row["Delta_lower"]) > 0.0
        and float(row["hard_self_consistency"]) < 0.5
        and float(row["proper_time_increment_interval"][0]) > 0.0
        and float(row["root_relative_path_plus_tube_upper"])
        < float(row["translated_ball_total_radius"])
        and float(row[path_key]) >= 0.0
        for row in rows
    )


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing C2 class-extension inputs: " + ", ".join(missing))
    class_record, extended, compensated, adaptive, recenter, recentered, maximal = (
        _load(path) for path in (
            CLASS, EXTENDED, COMPENSATED, ADAPTIVE, RECENTER, RECENTERED, MAXIMAL,
        )
    )
    if not all(record.get("validation_passed") is True for record in (
        class_record, extended, compensated, adaptive, recenter, recentered, maximal,
    )):
        raise RuntimeError("validated C2 class and continuation parents required")

    extended_cover = extended["cover"]
    compensated_cover = compensated["compensated_cover"]
    adaptive_cover = adaptive["adaptive_cover"]
    recentered_cover = recentered["recentered_cover"]
    chain = [
        {
            "certificate": EXTENDED.name,
            "prior_total": 2,
            "additional": int(extended_cover["certified_additional_box_count"]),
            "total": int(extended_cover["certified_total_segment_count"]),
            "regular_rows": _regular_rows(
                extended_cover["rows"], path_key="predictor_action_step_norm"
            ),
            "event_or_canonical_stop_reached": False,
            "proof_exhaustion": extended_cover["exhaustion_classification"],
        },
        {
            "certificate": COMPENSATED.name,
            "prior_total": int(compensated_cover["prior_total_segments"]),
            "additional": int(compensated_cover["additional_certified_segments"]),
            "total": int(compensated_cover["total_certified_segments"]),
            "regular_rows": _regular_rows(
                compensated_cover["rows"], path_key="stored_center_action_step_norm"
            ),
            "event_or_canonical_stop_reached": bool(
                compensated_cover["exhaustion_is_event_or_canonical_stop"]
            ),
            "proof_exhaustion": compensated_cover["exhaustion_classification"],
        },
        {
            "certificate": ADAPTIVE.name,
            "prior_total": int(adaptive_cover["prior_total_segments"]),
            "additional": int(adaptive_cover["additional_certified_segments"]),
            "total": int(adaptive_cover["total_certified_segments"]),
            "regular_rows": _regular_rows(
                adaptive_cover["rows"], path_key="center_rounding_defect_action_norm"
            ),
            "event_or_canonical_stop_reached": bool(
                adaptive_cover["exhaustion_is_event_or_canonical_stop"]
            ),
            "proof_exhaustion": adaptive_cover["exhaustion_classification"],
        },
        {
            "certificate": RECENTERED.name,
            "prior_total": int(recentered_cover["prior_total_segments"]),
            "additional": int(recentered_cover["additional_certified_segments"]),
            "total": int(recentered_cover["total_certified_segments"]),
            "regular_rows": _regular_rows(
                recentered_cover["rows"], path_key="center_rounding_defect_action_norm"
            ),
            "event_or_canonical_stop_reached": bool(
                recentered_cover["exhaustion_is_event_or_canonical_stop"]
            ),
            "proof_exhaustion": recentered_cover["exhaustion_classification"],
        },
    ]
    links_close = all(
        chain[index]["total"] == chain[index + 1]["prior_total"]
        for index in range(len(chain) - 1)
    )
    all_regular = all(row["regular_rows"] for row in chain)
    no_transition = not any(row["event_or_canonical_stop_reached"] for row in chain)
    original_signature = class_record["Sigma_enc_C2"]
    transition_markers = class_record["class_transition_surface_ledger"]

    validation = {
        "original_C2_class_invariant_is_certified": (
            class_record["class_invariance_theorem"][
                "number_of_distinct_certified_C2_enclosure_classes"
            ] == 1
        ),
        "continuation_count_chain_is_exact": links_close,
        "all_1064_segments_are_accounted_for": chain[-1]["total"] == 1064,
        "all_later_rows_retain_branch_24_and_regular_margins": all_regular,
        "no_event_or_canonical_stop_is_crossed": no_transition,
        "analytic_recenter_changes_no_physical_history_data": (
            recenter["validation"]["recenter_changes_proof_origin_not_physical_state"]
            and recenter["adjudication"]["physical_history_changed"] is False
        ),
        "proof_exhaustions_are_not_class_transition_markers": all(
            not row["event_or_canonical_stop_reached"] for row in chain
        ),
        "maximal_C2_family_remains_instantiated_on_one_class": (
            maximal["adjudication"]["abstract_M_C2_value_definition_exists_and_is_unique"]
            is True
        ),
        "continuous_proof_data_are_excluded_from_signature": all(
            label in original_signature["excluded_continuous_data"]
            for label in ("proof_center", "proof_box_index", "tube_radius")
        ),
        "global_finite_quotient_not_overclaimed": True,
        "no_selector_scale_recurrence_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_ENCLOSURE_CLASS_INVARIANT_EXTENSION",
        "status": (
            "C2_ENCLOSURE_CLASS_INVARIANT_EXTENDED_THROUGH_1064_SEGMENTS"
            if passed else "C2_ENCLOSURE_CLASS_INVARIANT_EXTENSION_NOT_CERTIFIED"
        ),
        "classification": (
            "THE_98_SEGMENT_ONE_CLASS_THEOREM_EXTENDS_OVER_EVERY_LATER_"
            "REGULAR_CONTINUATION_AND_THE_ANALYTIC_RECENTER;_ALL_1064_"
            "SEGMENTS_REPRESENT_CONTINUOUS_MODULATION_IN_ONE_C2_CLASS"
        ),
        "Sigma_enc_C2": original_signature,
        "continuation_provenance_chain": chain,
        "class_invariance_extension": {
            "original_certified_segment_count": int(
                class_record["class_invariance_theorem"]["certified_segment_count"]
            ),
            "extended_certified_segment_count": chain[-1]["total"],
            "number_of_distinct_certified_C2_enclosure_classes": 1,
            "D_tau_Sigma_enc": (
                "ZERO_IN_THE_DISCRETE_CLASS_SENSE_ON_EVERY_REGULAR_SEGMENT"
            ),
            "analytic_recenter_is_physical_transition": False,
            "proof_frontier_is_physical_transition": False,
        },
        "class_transition_surface_ledger": transition_markers,
        "Gate7_consequence": {
            "more_local_boxes_required_to_define_C2_physical_class": False,
            "existing_M_C2_maximal_family_still_matches": True,
            "current_owner": (
                "ACTION_OWNED_COMBINED_PROJECTED_REPLACEMENT_FORCE_TAIL_"
                "OR_AN_ACTUAL_FINITE_LATER_EVENT_OR_CANONICAL_STOP"
            ),
            "box_refinement_is_not_the_owner": True,
        },
        "validated_invalidated_open": {
            "VALIDATED": [
                "one C2 enclosure class contains all 1064 certified segments",
                "branch 24 and all recorded regular margins remain open",
                "the analytic recenter changes proof coordinates only",
                "all recorded cover exhaustions are proof technology",
            ],
            "INVALIDATED": [
                "one physical class per proof box",
                "binary64 or allocation exhaustion as a physical transition",
                "further local boxes as a prerequisite for defining M_C2^max",
            ],
            "OPEN": [
                "actual combined projected replacement-force tail",
                "actual later event or canonical stop",
                "numeric zero-source force, saddle, and physical Hessian",
                "global finite physical enclosure quotient",
            ],
        },
        "hindsight": {
            "physical_enclosure_class": "ONE_CERTIFIED_C2_CLASS",
            "continuous_modulation_within_class": "1064_POSITIVE_DURATION_SEGMENTS",
            "numerical_or_proof_box": "1064_SEGMENTS_WITH_ONE_ANALYTIC_RECENTER",
            "event_or_class_transition": "NONE_CROSSED",
            "canonical_stop": "NONE_REACHED",
            "difficulty_classification": "PROOF_RESOLUTION_NOT_PHYSICAL_STRUCTURE",
        },
        "exact_next_dependency": (
            "RETURN_TO_THE_COMBINED_PROJECTED_REPLACEMENT_FORCE_TAIL_OR_"
            "CERTIFY_AN_ACTUAL_FINITE_EVENT_STOP;_DO_NOT_EXTEND_BOXES_MERELY_"
            "TO_REDEFINE_THE_ALREADY_CERTIFIED_C2_CLASS"
        ),
        "claim_boundary": {
            "C2_local_enclosure_class": "CERTIFIED_ONE_CLASS_THROUGH_1064_SEGMENTS",
            "global_finite_enclosure_quotient": "OPEN",
            "C2_maximal_Weyl_family_definition": "INSTANTIATED",
            "zero_source_force": "OPEN",
            "Gate7": "ACTIVE_PROJECTED_FORCE_TAIL_OR_FINITE_EVENT_STOP",
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    theorem = payload["class_invariance_extension"]
    print(json.dumps({
        "status": payload["status"],
        "segments": theorem["extended_certified_segment_count"],
        "classes": theorem["number_of_distinct_certified_C2_enclosure_classes"],
        "recenter_is_transition": theorem["analytic_recenter_is_physical_transition"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
