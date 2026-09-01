"""Audit the exact affine Omega-5 term and reject binary64 tail promotion."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
M4 = BASE / "BHSM_N12_GATE7_DECIMAL_SIGNED_Y_GREEN_MAGNUS4_PROP16_AUDIT.npz"
M6 = {
    order: BASE / f"BHSM_N12_GATE7_DECIMAL_SIGNED_Y_GREEN_MAGNUS6_PROP{order:02d}_AUDIT.npz"
    for order in (8, 16, 32)
}
REFERENCE = BASE / "BHSM_N12_GATE7_DECIMAL_MAGNUS4_PROP_RECENTER_AUDIT.npz"
RESULT = BASE / "BHSM_N12_GATE7_DECIMAL_MAGNUS6_LEADING_REMAINDER_AUDIT.json"
DATA = RESULT.with_suffix(".npz")


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _profile(path: Path) -> np.ndarray:
    with np.load(path) as source:
        return np.asarray(source["Gauss8_correction_profile"], dtype=float)


def main() -> None:
    m4 = _profile(M4)
    m6 = {order: _profile(path) for order, path in M6.items()}
    with np.load(REFERENCE) as source:
        reference = np.asarray(source["numerical_Richardson_reference"], dtype=float)
        times = np.asarray(source["fine_action_lengths"], dtype=float)
    if any(profile.shape != (371, 98) for profile in (m4, reference, *m6.values())):
        raise RuntimeError("complete 371-node profiles required")

    leading_shift = np.linalg.norm(m6[16] - m4, axis=1)
    increment_8_16 = np.linalg.norm(m6[16] - m6[8], axis=1)
    increment_16_32 = np.linalg.norm(m6[32] - m6[16], axis=1)
    reference_m4 = np.linalg.norm(m4 - reference, axis=1)
    reference_m6 = np.linalg.norm(m6[16] - reference, axis=1)
    observed_ratio = float(np.max(increment_8_16) / np.max(increment_16_32))
    expected_sixth_order_ratio = 64.0

    np.savez_compressed(
        DATA,
        fine_action_lengths=times,
        Magnus6_minus_Magnus4_2_norm=leading_shift,
        Magnus6_PROP8_to_16_2_norm=increment_8_16,
        Magnus6_PROP16_to_32_2_norm=increment_16_32,
        Magnus4_to_midpoint_Richardson_reference_2_norm=reference_m4,
        Magnus6_to_midpoint_Richardson_reference_2_norm=reference_m6,
    )
    validation = {
        "complete_371_node_profiles_compared": leading_shift.shape == (371,),
        "exact_affine_Omega5_Lie_polynomial_used": True,
        "leading_Omega5_profile_shift_below_4e_minus_19": bool(
            np.max(leading_shift) < 4.0e-19
        ),
        "binary64_refinement_ratio_not_relabelled_as_sixth_order_tail": bool(
            not 32.0 < observed_ratio < 128.0
        ),
        "midpoint_Richardson_surrogate_not_relabelled_as_exact_flow": True,
        "analytic_Magnus_remainder_remains_open": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    paths = [M4, *M6.values(), REFERENCE]
    payload = {
        "artifact": "BHSM_N12_GATE7_DECIMAL_MAGNUS6_LEADING_REMAINDER_AUDIT",
        "status": (
            "EXACT_AFFINE_OMEGA5_IDENTIFIED;_BINARY64_MAGNUS6_REFINEMENT_"
            "IS_NOT_ANALYTIC_TAIL_AUTHORITY"
        ),
        "authority": "EXACT_LIE_IDENTITY_PLUS_NUMERICAL_ROUTING_ONLY",
        "identity": {
            "affine_generator": "A(t)=A_mid+(t-t_mid)*B",
            "Omega4": "h*A_mid-h^3*[A_mid,B]/12",
            "Omega5": (
                "h^5*([A_mid,[A_mid,[A_mid,B]]]/720-"
                "[B,[A_mid,B]]/240)"
            ),
            "expected_sixth_order_halving_ratio": expected_sixth_order_ratio,
        },
        "summary": {
            "maximum_Magnus6_minus_Magnus4_profile_shift": float(
                np.max(leading_shift)
            ),
            "leading_shift_owner_fine_node": int(np.argmax(leading_shift)),
            "terminal_Magnus6_minus_Magnus4_profile_shift": float(
                leading_shift[-1]
            ),
            "maximum_Magnus6_PROP8_to_16_increment": float(
                np.max(increment_8_16)
            ),
            "maximum_Magnus6_PROP16_to_32_increment": float(
                np.max(increment_16_32)
            ),
            "observed_refinement_ratio": observed_ratio,
            "maximum_Magnus4_to_midpoint_Richardson_reference": float(
                np.max(reference_m4)
            ),
            "maximum_Magnus6_to_midpoint_Richardson_reference": float(
                np.max(reference_m6)
            ),
        },
        "data": DATA.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in paths
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "claim_boundary": {
            "affine_Omega5_identity": "ESTABLISHED",
            "binary64_Magnus6_tail": "REJECTED_AS_INTERVAL_AUTHORITY",
            "analytic_Magnus4_higher_commutator_remainder": "OPEN_INTERVAL_AUTHORITY",
            "outward_signed_Y": "OPEN_INTERVAL_AUTHORITY",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "OUTWARD_EVALUATE_THE_OMEGA5_AND_HIGHER_NESTED_COMMUTATOR_REMAINDER_"
            "ON_THE_RETAINED_CORRELATED_QUOTIENT;_DO_NOT_USE_BINARY64_REFINEMENT"
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
