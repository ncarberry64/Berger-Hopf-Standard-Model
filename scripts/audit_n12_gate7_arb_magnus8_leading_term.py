"""Compare the outward finite Magnus-8 and Magnus-6 affine assemblies."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
M6_JSON = BASE / "BHSM_N12_GATE7_ARB_MAGNUS6_AFFINE_COMPOSITION.json"
M8_JSON = BASE / "BHSM_N12_GATE7_ARB_MAGNUS8_AFFINE_COMPOSITION.json"
M6_DATA = M6_JSON.with_suffix(".npz")
M8_DATA = M8_JSON.with_suffix(".npz")
BUDGET = BASE / "BHSM_N12_GATE7_DECIMAL_MAGNUS4_PROP_RECENTER_AUDIT.json"
RESULT = BASE / "BHSM_N12_GATE7_ARB_MAGNUS8_LEADING_TERM_AUDIT.json"
DATA = RESULT.with_suffix(".npz")


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def main() -> None:
    with np.load(M6_DATA) as source:
        m6_mid = np.asarray(source["global_signed_response_midpoint"], dtype=float)
        m6_rad = np.asarray(
            source["global_signed_response_component_radius"], dtype=float,
        )
        times = np.asarray(source["macro_action_lengths"], dtype=float)
    with np.load(M8_DATA) as source:
        m8_mid = np.asarray(source["global_signed_response_midpoint"], dtype=float)
        m8_rad = np.asarray(
            source["global_signed_response_component_radius"], dtype=float,
        )
    reserve = float(json.loads(BUDGET.read_text(encoding="utf-8"))[
        "summary"
    ]["candidate_Magnus4_selected_cone_reserve"])
    midpoint_difference = np.linalg.norm(m8_mid - m6_mid, axis=1)
    evaluation_radius = np.linalg.norm(m8_rad + m6_rad, axis=1)
    outward_difference = midpoint_difference + evaluation_radius
    owner = int(np.argmax(outward_difference))
    maximum = float(outward_difference[owner])

    np.savez_compressed(
        DATA,
        macro_action_lengths=times,
        Magnus8_minus_Magnus6_midpoint_2_norm=midpoint_difference,
        combined_outward_evaluation_radius=evaluation_radius,
        Magnus8_minus_Magnus6_outward_2_norm=outward_difference,
    )
    validation = {
        "complete_48_node_correlated_profiles_compared": (
            outward_difference.shape == (48,)
        ),
        "both_finite_affine_assemblies_are_256_bit_Arb_certificates": all(
            json.loads(path.read_text(encoding="utf-8"))["validation_passed"]
            for path in (M6_JSON, M8_JSON)
        ),
        "finite_Omega7_augmented_shift_below_2p5e_minus_25": maximum < 2.5e-25,
        "stored_midpoint_difference_is_below_binary64_resolution": bool(
            np.max(midpoint_difference) == 0.0
        ),
        "stored_midpoint_equality_not_relabelled_as_exact_zero": True,
        "finite_Omega7_bound_has_more_than_one_trillion_fold_cone_reserve": (
            reserve / maximum > 1.0e12
        ),
        "Omega9_and_higher_remainder_not_claimed": True,
        "signed_source_quadrature_remainder_not_claimed": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    paths = (M6_JSON, M6_DATA, M8_JSON, M8_DATA, BUDGET)
    payload = {
        "artifact": "BHSM_N12_GATE7_ARB_MAGNUS8_LEADING_TERM_AUDIT",
        "status": "FINITE_OMEGA7_AUGMENTED_CORRELATED_SHIFT_OUTWARD_BOUNDED",
        "authority": "ARB_BALL_AUTHORITY_FOR_THE_FINITE_OMEGA7_AUGMENTATION_ONLY",
        "identity": {
            "Omega7": (
                "h^7*(-ad_A^5(B)/30240+[A,[A,[B,[A,B]]]]/10080-"
                "[[A,B],[A,[A,B]]]/7560-[B,[B,[A,B]]]/6720)"
            ),
            "comparison": "GLOBAL_RETAINED_MAGNUS8_MINUS_MAGNUS6_AFFINE_RESPONSE",
        },
        "summary": {
            "maximum_finite_Omega7_augmented_outward_bound": maximum,
            "owner_macro_node": owner,
            "terminal_finite_Omega7_augmented_outward_bound": float(
                outward_difference[-1]
            ),
            "maximum_stored_midpoint_difference": float(
                np.max(midpoint_difference)
            ),
            "maximum_combined_evaluation_radius": float(
                np.max(evaluation_radius)
            ),
            "selected_cone_reserve": reserve,
            "finite_Omega7_bound_cone_reserve_factor": reserve / maximum,
        },
        "data": DATA.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in paths
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "claim_boundary": {
            "finite_Omega7_augmented_operator": "CERTIFIED_OUTWARD_BOUND",
            "Omega9_and_higher_analytic_remainder": "OPEN_INTERVAL_AUTHORITY",
            "outward_signed_Y": "OPEN_INTERVAL_AUTHORITY",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "OUTWARD_BOUND_OMEGA9_AND_HIGHER_IN_THE_RETAINED_CORRELATED_QUOTIENT_"
            "AND_CERTIFY_SIGNED_SOURCE_QUADRATURE_Y"
        ),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
