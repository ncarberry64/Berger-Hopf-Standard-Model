"""Verify nonsingularity of the stored midpoint full bases with 512-bit Arb.

This certifies the exact binary64 direction matrices used by supplemental
contractions. It does not enclose the Hessian or a physical neighborhood.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
from flint import arb, arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import derive_n12_gate7_current_green_supplemental_midpoint_blocks as supplement
import derive_n12_gate7_current_green_signed_transverse_tensor_recovery as recovery

RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_SUPPLEMENTAL_BASIS_INVERSE.json"
PRECISION = 512


def certify_basis(values: np.ndarray) -> dict[str, object]:
    """Enclose an inverse and verify ||I - S B||_infinity < 1 rigorously."""
    values = np.asarray(values, dtype=float)
    if (values.ndim != 2 or values.shape[0] != values.shape[1]
            or values.shape[0] == 0 or not np.all(np.isfinite(values))):
        raise ValueError("basis must be a finite nonempty square matrix")
    previous_precision = ctx.prec
    ctx.prec = PRECISION
    try:
        matrix = arb_mat([[arb(float(value)) for value in row] for row in values])
        inverse = matrix.inv()
        size = values.shape[0]
        identity = arb_mat([[int(i == j) for j in range(size)] for i in range(size)])
        residual = identity - matrix * inverse
        error = max(sum(abs(residual[i, j]) for j in range(size)).upper()
                    for i in range(size))
        inverse_norm = max(sum(abs(inverse[i, j]) for j in range(size)).upper()
                           for i in range(size))
        if not (error.is_finite() and inverse_norm.is_finite() and error < 1):
            raise RuntimeError("stored full-basis inverse could not be verified")
        return {
            "dimension": size,
            "residual_infinity_upper": math.nextafter(float(error), math.inf),
            "inverse_infinity_upper": math.nextafter(float(inverse_norm), math.inf),
            "nonsingular": True,
        }
    finally:
        ctx.prec = previous_precision


def build_payload(indices: list[int]) -> dict[str, object]:
    if not indices or len(set(indices)) != len(indices) or any(i < 0 or i >= 370 for i in indices):
        raise ValueError("distinct midpoint indices in 0..369 are required")
    geometry = supplement._load_geometry()
    rows = []
    inputs = {}
    for index in sorted(indices):
        completion, recovered = supplement._completion(index, geometry)
        row = certify_basis(completion.full_basis)
        row["interval"] = index
        row["basis_binary64_SHA256"] = hashlib.sha256(
            np.asarray(completion.full_basis, dtype="<f8").tobytes(order="C")
        ).hexdigest().upper()
        rows.append(row)
        inputs[recovered.relative_to(ROOT).as_posix()] = supplement._sha(recovered)
    for source in (Path(__file__), Path(supplement.__file__),
                   ROOT / "src/bhsm/interface/current_green_supplemental_midpoint.py"):
        inputs[source.relative_to(ROOT).as_posix()] = supplement._sha(source)
    complete = sorted(indices) == list(range(370))
    return {
        "artifact": "BHSM_N12_GATE7_SUPPLEMENTAL_BASIS_INVERSE",
        "status": "ALL_370_STORED_FULL_BASES_VERIFIED" if complete else "PARTIAL_STORED_FULL_BASES_VERIFIED",
        "scope": "NONSINGULARITY_OF_EXACT_STORED_BINARY64_DIRECTION_MATRICES_ONLY",
        "arithmetic_precision_bits": PRECISION,
        "coverage": {"verified_midpoints": len(rows), "required_midpoints": 370, "complete": complete},
        "maximum_residual_infinity_upper": max(row["residual_infinity_upper"] for row in rows),
        "maximum_inverse_infinity_upper": max(row["inverse_infinity_upper"] for row in rows),
        "rows": rows,
        "campaign_fingerprint": supplement._fingerprint(),
        "recovery_campaign_fingerprint": recovery._fingerprint(),
        "inputs": inputs,
        "validation_passed": True,
        "claim_boundary": {
            "all_370_stored_full_bases_nonsingular": complete,
            "Hessian_rounding_enclosed": False,
            "physical_neighborhood_remainder_derived": False,
            "Gate7_closed": False,
            "FULL_BHSM_COMPLETE": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--indices", default=",".join(map(str, range(370))))
    parser.add_argument("--output", type=Path, default=RESULT)
    args = parser.parse_args()
    payload = build_payload([int(value) for value in args.indices.split(",")])
    if args.output.resolve() == RESULT.resolve() and not payload["coverage"]["complete"]:
        raise RuntimeError("partial verification must use a separate output path")
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("status", "coverage", "maximum_residual_infinity_upper")}))


if __name__ == "__main__":
    main()
