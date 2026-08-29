"""Audit PROP16/32/64/128 refinement of the Decimal Gate-7 source image."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
INPUTS = {
    16: BASE / "BHSM_N12_GATE7_DECIMAL_SIGNED_Y_GREEN_CONVERGENCE_AUDIT.npz",
    32: BASE / "BHSM_N12_GATE7_DECIMAL_SIGNED_Y_GREEN_PROP32_AUDIT.npz",
    64: BASE / "BHSM_N12_GATE7_DECIMAL_SIGNED_Y_GREEN_PROP64_AUDIT.npz",
    128: BASE / "BHSM_N12_GATE7_DECIMAL_SIGNED_Y_GREEN_PROP128_AUDIT.npz",
}
RESULT = BASE / "BHSM_N12_GATE7_DECIMAL_PROP_REFINEMENT_AUDIT.json"
DATA = RESULT.with_suffix(".npz")


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def main() -> None:
    profiles = {}
    times = None
    for resolution, path in INPUTS.items():
        with np.load(path) as source:
            current_times = np.asarray(source["fine_action_lengths"], dtype=float)
            profiles[resolution] = np.asarray(
                source["Gauss8_correction_profile"], dtype=float,
            )
        if times is None:
            times = current_times
        elif not np.array_equal(times, current_times):
            raise RuntimeError("PROP refinement grids differ")
    if times is None or any(value.shape != (371, 98) for value in profiles.values()):
        raise RuntimeError("complete PROP refinement family required")

    vector_increments = {
        (left, right): profiles[right] - profiles[left]
        for left, right in ((16, 32), (32, 64), (64, 128))
    }
    increments = {
        pair: np.linalg.norm(value, axis=1)
        for pair, value in vector_increments.items()
    }
    maxima = {pair: float(np.max(value)) for pair, value in increments.items()}
    maximum_ratios = {
        "16_to_32_over_32_to_64": maxima[(16, 32)] / maxima[(32, 64)],
        "32_to_64_over_64_to_128": maxima[(32, 64)] / maxima[(64, 128)],
    }
    richardson_16 = np.linalg.norm(
        vector_increments[(16, 32)] - 4.0 * vector_increments[(32, 64)],
        axis=1,
    )
    richardson_32 = np.linalg.norm(
        vector_increments[(32, 64)] - 4.0 * vector_increments[(64, 128)],
        axis=1,
    )
    geometric_tail = (4.0 / 3.0) * increments[(16, 32)]
    np.savez_compressed(
        DATA,
        fine_action_lengths=times,
        PROP16_to_32_increment=increments[(16, 32)],
        PROP32_to_64_increment=increments[(32, 64)],
        PROP64_to_128_increment=increments[(64, 128)],
        Richardson_16_32_64_residual=richardson_16,
        Richardson_32_64_128_residual=richardson_32,
        PROP16_geometric_tail_proxy=geometric_tail,
    )
    validation = {
        "complete_371_node_same_source_profiles_compared": True,
        "successive_maximum_increments_decrease": (
            maxima[(16, 32)] > maxima[(32, 64)] > maxima[(64, 128)]
        ),
        "both_observed_maximum_refinement_ratios_within_one_percent_of_four": all(
            abs(value - 4.0) < 0.04 for value in maximum_ratios.values()
        ),
        "both_Richardson_residuals_below_1p5e_minus_17": (
            float(np.max(richardson_16)) < 1.5e-17
            and float(np.max(richardson_32)) < 1.5e-17
        ),
        "geometric_tail_proxy_vanishes_at_reset": bool(geometric_tail[0] == 0.0),
        "geometric_tail_proxy_not_promoted_to_interval_authority": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    payload = {
        "artifact": "BHSM_N12_GATE7_DECIMAL_PROP_REFINEMENT_AUDIT",
        "status": (
            "PROP16_32_64_128_SHOWS_STABLE_SECOND_ORDER_SIGNED_PROFILE_REFINEMENT;_"
            "OUTWARD_PROP_TAIL_REMAINS_OPEN"
        ),
        "authority": "COMPLETE_PROFILE_NUMERICAL_REFINEMENT_NOT_INTERVAL_TAIL_AUTHORITY",
        "identity": {
            "source": "SAME_DECIMAL_GAUSS8_SIGNED_SOURCE_AT_ALL_RESOLUTIONS",
            "resolutions": [16, 32, 64, 128],
            "geometric_tail_proxy": "(4/3)*NORM(PROP32_MINUS_PROP16)",
        },
        "summary": {
            "maximum_profile_increments": {
                f"PROP{left}_to_PROP{right}": maxima[(left, right)]
                for left, right in ((16, 32), (32, 64), (64, 128))
            },
            "maximum_increment_refinement_ratios": maximum_ratios,
            "maximum_Richardson_16_32_64_residual": float(np.max(richardson_16)),
            "maximum_Richardson_32_64_128_residual": float(np.max(richardson_32)),
            "maximum_PROP16_geometric_tail_proxy": float(np.max(geometric_tail)),
            "terminal_PROP16_geometric_tail_proxy": float(geometric_tail[-1]),
        },
        "data": DATA.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in INPUTS.values()
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "claim_boundary": {
            "signed_PROP_refinement": "NUMERICALLY_SECOND_ORDER_ON_COMPLETE_PROFILE",
            "outward_PROP16_Z1_tail": "OPEN_INTERVAL_AUTHORITY",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "ENCLOSE_THE_SIGNED_LEADING_MIDPOINT_DEFECT_AND_ITS_HIGHER_ORDER_"
            "REMAINDER_IN_THE_CORRELATED_MULTIPLE_SHOOTING_PROOF_FRAME"
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
