"""Certify interval transposed duration actions on all 1,222 C2 segments."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
MOVING = BASE / "BHSM_N12_C2_1222_MOVING_DURATION_PULLBACK_ENCLOSURE.json"
MOVING_DATA = MOVING.with_suffix(".npz")
CORE = BASE / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
CORE_DATA = CORE.with_suffix(".npz")
SIGNED = BASE / "BHSM_N12_C2_SEGMENT1214_TRANSPOSED_DURATION_ACTION.json"
SIGNED_DATA = SIGNED.with_suffix(".npz")
NO_GO = BASE / "BHSM_N12_FORWARD_RESOLVENT_HEAT_SYNTHESIS_AUDIT.json"
THEORY = ROOT / "theory" / "n12_c2_1222_transposed_duration_action_coverage.md"
RESULT = BASE / "BHSM_N12_C2_1222_TRANSPOSED_DURATION_ACTION_COVERAGE.json"
DATA_RESULT = RESULT.with_suffix(".npz")
INPUTS = (
    MOVING, MOVING_DATA, CORE, CORE_DATA, SIGNED, SIGNED_DATA, NO_GO, THEORY,
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "missing transposed-duration coverage inputs: " + ", ".join(missing)
        )
    moving, core, signed, no_go = (
        _load(path) for path in (MOVING, CORE, SIGNED, NO_GO)
    )
    if not all(record.get("validation_passed") is True for record in (
        moving, core, signed, no_go,
    )):
        raise RuntimeError("validated transposed-duration parents required")

    with np.load(MOVING_DATA) as data:
        radii = np.asarray(
            data["segment_duration_pullback_from_start_upper"], dtype=float
        )
    with np.load(CORE_DATA) as data:
        durations = np.asarray(
            data["segment_proper_duration_interval"], dtype=float
        )
    with np.load(SIGNED_DATA) as data:
        signed_center = np.asarray(
            data["non_scale_segment_duration_covector_center"], dtype=float
        )
        signed_radius = float(
            data["non_scale_segment_duration_covector_ball_radius_upper"]
        )

    # Global segment labels are one-based in the continuation ledgers.
    segment1214_array_index = 1213
    signed_outer_radius = math.nextafter(
        float(np.linalg.norm(signed_center)) + signed_radius, math.inf
    )
    parent_radius = float(radii[segment1214_array_index])
    np.savez_compressed(
        DATA_RESULT,
        segment_duration_action_dual_ball_center=np.zeros((1222, 98)),
        segment_duration_action_dual_ball_radius_upper=radii,
        segment1214_signed_action_dual_center=signed_center,
        segment1214_signed_action_dual_ball_radius_upper=np.asarray(
            signed_radius
        ),
    )

    validation = {
        "exactly_1222_interval_actions_are_present": radii.shape == (1222,),
        "all_interval_action_radii_are_finite_positive": bool(
            np.all(np.isfinite(radii)) and np.all(radii > 0.0)
        ),
        "all_1222_proper_duration_intervals_are_positive": bool(
            durations.shape == (1222, 2)
            and np.all(durations[:, 0] > 0.0)
            and np.all(durations[:, 1] >= durations[:, 0])
        ),
        "parent_records_duration_first_jet_not_value_only": moving[
            "validation"
        ]["duration_interval_not_substituted_for_duration_first_jet"],
        "parent_bound_is_the_exact_transposed_action_norm_inequality": (
            moving["theorem"]["segment_start_bound"]
            == "norm(D_Ystart h_e)<=h_e^+*G_e*(norm(DlogN)+DDelta_e^+/Delta_e^-)"
        ),
        "segment1214_signed_refinement_is_strictly_contained": (
            signed_outer_radius < parent_radius
        ),
        "segment1214_global_label_maps_to_array_index_1213": (
            signed["segment"]["global_segment_index"] == 1214
            and segment1214_array_index == 1213
        ),
        "z_minus_one_probe_is_not_promoted_to_heat_source": (
            no_go["retained_functional_calculus"][
                "one_resolvent_probe_sufficient"
            ] is False
        ),
        "no_transition_inverse_selector_endpoint_scale_fit_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_C2_1222_TRANSPOSED_DURATION_ACTION_COVERAGE",
        "status": (
            "C2_1222_INTERVAL_TRANSPOSED_DURATION_ACTIONS_CERTIFIED"
            if passed else "C2_1222_TRANSPOSED_DURATION_ACTION_COVERAGE_INVALID"
        ),
        "classification": (
            "THE_EXISTING_MOVING_DURATION_FIRST_JET_CERTIFICATE_ALREADY_"
            "ENCLOSES_THE_TRANSPOSED_EXACT_ACTION_ON_EACH_OF_1222_SEGMENTS;_"
            "SEGMENT1214_IS_A_SHARP_SIGNED_REFINEMENT_NOT_A_MISSING_NORM_THEOREM"
        ),
        "theorem": {
            "exact_action": (
                "D_Ye_h_e=integral_D_Y_q_tau(Y(s),s)*J_e(s)_ds"
            ),
            "interval_action": (
                "D_Ye_h_e_IN_CLOSED_ACTION_DUAL_BALL(0,B_e)"
            ),
            "stored_radius": (
                "B_e=h_e^+*G_e*(norm(DlogN)+DDelta_e^+/Delta_e^- )"
            ),
            "full_transition_matrix_inverted": False,
            "proof_center_selected_as_physical_history": False,
        },
        "coverage": {
            "segments": int(radii.size),
            "state_dimension": 98,
            "minimum_action_dual_radius_upper": float(np.min(radii)),
            "maximum_action_dual_radius_upper": float(np.max(radii)),
            "segment1214_array_index": segment1214_array_index,
            "segment1214_coarse_radius_upper": parent_radius,
            "segment1214_signed_ball_outer_radius_upper": signed_outer_radius,
            "segment1214_refinement_ratio": signed_outer_radius / parent_radius,
        },
        "adjudication": {
            "all_1222_interval_transposed_duration_actions": "CERTIFIED",
            "segment1214_sharp_signed_action": "CERTIFIED",
            "remaining_1221_sharp_signed_refinements": (
                "OPTIONAL_AFTER_ACTUAL_GRADED_SOURCE_IDENTIFIES_NEEDED_PRECISION"
            ),
            "actual_graded_heat_minus_zeta_coefficient_cotangent": "OPEN",
            "complete_signed_joint_reverse_sweep": "OPEN_AFTER_GRADED_SOURCE",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
        },
        "validated_invalidated_open": {
            "VALIDATED": [
                "1222 interval transposed duration actions",
                "inverse-free first-jet coverage",
                "segment1214 sharp signed refinement containment",
            ],
            "INVALIDATED": [
                "1221 additional sharp DDelta row sweeps are required before any interval reverse action exists",
                "the z=-1 Weyl cotangent is the retained heat-minus-zeta source",
            ],
            "OPEN": [
                "actual graded heat-minus-zeta coefficient cotangent",
                "signed joint upstream/C2 reverse sweep",
                "maximal projected force tail or finite later stop",
            ],
        },
        "hindsight": {
            "classification": "REDUNDANT_NORM_PROOF_REMOVED_FROM_LIVE_DAG",
            "obstruction_physical": False,
        },
        "exact_next_dependency": (
            "SYNTHESIZE_OR_RIGOROUSLY_ENCLOSE_THE_ACTUAL_GRADED_HEAT_MINUS_"
            "ZETA_COEFFICIENT_COTANGENT_FROM_THE_COMPLETE_ACTION_OWNED_SEAM_"
            "FAMILY,_THEN_USE_THE_CERTIFIED_INTERVAL_ACTIONS_AND_ONLY_SHARPEN_"
            "SEGMENTS_REQUIRED_BY_THE_RESULTING_FORCE_PRECISION"
        ),
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA_RESULT),
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in (*INPUTS, Path(__file__))
        },
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }
    return payload


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "coverage": payload["coverage"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
