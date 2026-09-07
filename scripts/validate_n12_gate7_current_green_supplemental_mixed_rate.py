"""Validate the supplemental rectangular kernel against a recovered UU slice.

Run this only after the signed midpoint recovery has completed.  The check is
an implementation identity at the unchanged binary64 center, not an outward
or Gate-7 certificate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import derive_n12_gate7_current_green_full_transverse_quadratic_center as center  # noqa: E402
import derive_n12_gate7_current_green_signed_transverse_tensor_recovery as recovery  # noqa: E402
import derive_n12_gate7_current_green_supplemental_mixed_rate as supplemental  # noqa: E402
from derive_n12_gate7_current_green_supplemental_mixed_rate import (  # noqa: E402
    mixed_rate_map,
)


RESULT = (
    ROOT / "artifacts/current_semantics/"
    "BHSM_N12_GATE7_SUPPLEMENTAL_MIXED_RATE_UU_VALIDATION.json"
)
THIS_SCRIPT = Path(__file__).resolve()


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _comparison(actual: np.ndarray, expected: np.ndarray) -> dict[str, float]:
    actual = np.asarray(actual, dtype=float)
    expected = np.asarray(expected, dtype=float)
    if actual.shape != expected.shape or actual.ndim != 2:
        raise ValueError("comparison arrays must have one identical matrix shape")
    if not (np.all(np.isfinite(actual)) and np.all(np.isfinite(expected))):
        raise ValueError("comparison arrays must be finite")
    difference = actual - expected
    tiny = np.finfo(float).tiny
    return {
        "maximum_absolute_difference": float(np.max(abs(difference))),
        "Frobenius_difference": float(np.linalg.norm(difference)),
        "relative_Frobenius_difference": float(
            np.linalg.norm(difference) / max(np.linalg.norm(expected), tiny)
        ),
    }


def validate(interval: int, left: int, rights: list[int]) -> dict[str, object]:
    if not 0 <= interval < 370 or not 0 <= left < 73:
        raise ValueError("validation index outside the midpoint tensor")
    if not rights or any(not 0 <= value < 73 for value in rights):
        raise ValueError("at least one valid right tensor index is required")
    fingerprint = recovery._fingerprint()
    path = recovery._path("midpoint", interval)
    if not recovery._valid(path, "midpoint", interval, fingerprint):
        raise RuntimeError(f"validated signed midpoint shard required: {interval}")
    with np.load(path) as source:
        tensor = np.asarray(source["quadratic_tensor"], dtype=float)
        basis = np.asarray(source["transverse_basis"], dtype=float)
    inputs = center._load_inputs()
    states, descriptors, tangents = inputs["midpoint"][:3]
    directions = center._frame(tangents[interval]) @ basis
    started = time.perf_counter()
    actual, diagnostics = mixed_rate_map(
        states[interval], float(descriptors[interval]),
        inputs["weights"], inputs["reference"], directions[:, left],
        directions[:, rights],
    )
    elapsed = time.perf_counter() - started
    comparison = _comparison(actual, tensor[:, left, rights])
    diagnostic_values = {
        "base_response_residual_2_norm": diagnostics.base_response_residual_2_norm,
        "left_first_response_relative_residual": diagnostics.left_first_response_relative_residual,
        "right_first_response_relative_residual": diagnostics.right_first_response_relative_residual,
        "mixed_response_relative_residual": diagnostics.mixed_response_relative_residual,
        "mixed_eigenline_normalization_residual": diagnostics.mixed_eigenline_normalization_residual,
    }
    passed = bool(
        comparison["relative_Frobenius_difference"] < 5.0e-10
        and all(np.isfinite(value) for value in diagnostic_values.values())
    )
    sources = (
        path, THIS_SCRIPT, Path(supplemental.__file__).resolve(),
        Path(center.__file__).resolve(), Path(recovery.__file__).resolve(),
    )
    return {
        "artifact": "BHSM_N12_GATE7_SUPPLEMENTAL_MIXED_RATE_UU_VALIDATION",
        "status": "PASSED" if passed else "FAILED_CLOSED",
        "scope": "BINARY64_CENTER_IMPLEMENTATION_IDENTITY_ONLY",
        "interval": interval,
        "left_index": left,
        "right_indices": rights,
        "elapsed_seconds": elapsed,
        "comparison": comparison,
        "diagnostics": diagnostic_values,
        "recovery_campaign_fingerprint": fingerprint,
        "inputs": {_relative(source): _sha(source) for source in sources},
        "validation_passed": passed,
        "claim_boundary": {
            "supplemental_rectangular_kernel_matches_recovered_UU_slice": passed,
            "outward_remainder_derived": False,
            "Gate7_closed": False,
            "FULL_BHSM_COMPLETE": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=0)
    parser.add_argument("--left", type=int, default=0)
    parser.add_argument("--rights", default="0,1")
    args = parser.parse_args()
    payload = validate(
        args.interval, args.left,
        [int(value) for value in args.rights.split(",") if value],
    )
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not payload["validation_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
