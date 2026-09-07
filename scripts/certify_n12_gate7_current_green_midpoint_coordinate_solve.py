"""Enclose solve error for the exact binary64 midpoint basis and input map.

The bound is ||X-Xhat||_inf <= ||S^-1||_inf ||M-S Xhat||_inf.
This does not enclose construction of S or M from physical ball inputs, or
any Hessian contraction. It supplies one explicitly scoped rounding operand.
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
import certify_n12_gate7_current_green_supplemental_basis_inverse as basis_certificate
import certify_n12_gate7_current_green_signed_transverse_causal_center as causal
import derive_n12_gate7_current_green_supplemental_midpoint_blocks as supplement

RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_MIDPOINT_COORDINATE_SOLVE.json"


def certify_solve(basis: np.ndarray, target: np.ndarray, approximate: np.ndarray) -> dict:
    """Bound the full matrix infinity-norm error without discarding residuals."""
    basis, target, approximate = [np.asarray(value, dtype=float)
                                  for value in (basis, target, approximate)]
    if (basis.ndim != 2 or basis.shape[0] != basis.shape[1]
            or target.ndim != 2 or target.shape[0] != basis.shape[0]
            or target.shape[1] == 0 or approximate.shape != target.shape
            or not all(np.all(np.isfinite(value))
                       for value in (basis, target, approximate))):
        raise ValueError("finite compatible square-basis solve inputs required")
    verified = basis_certificate.certify_basis(basis)
    previous = ctx.prec
    ctx.prec = basis_certificate.PRECISION
    try:
        def exact(values):
            return arb_mat([[arb(float(value)) for value in row] for row in values])

        residual = exact(target) - exact(basis) * exact(approximate)
        residual_upper = max(
            sum(abs(residual[i, j]) for j in range(target.shape[1])).upper()
            for i in range(target.shape[0])
        )
        error_upper = (arb(verified["inverse_infinity_upper"]) * residual_upper).upper()
        bounds = [math.nextafter(float(value), math.inf)
                  for value in (residual_upper, error_upper)]
        if not all(math.isfinite(value) and value >= 0 for value in bounds):
            raise RuntimeError("coordinate solve error bound is not finite")
        return dict(verified, solve_residual_infinity_upper=bounds[0],
                    coordinate_error_infinity_upper=bounds[1])
    finally:
        ctx.prec = previous


def _array_hash(value):
    return hashlib.sha256(np.asarray(value, dtype="<f8").tobytes(order="C")).hexdigest().upper()


def build_payload(indices: list[int]) -> dict:
    if not indices or len(set(indices)) != len(indices) or any(i < 0 or i >= 370 for i in indices):
        raise ValueError("distinct midpoint indices in 0..369 are required")
    geometry = supplement._load_geometry()
    source_inputs = geometry["inputs"]
    endpoint_tangents, axes = source_inputs["endpoint"][2:4]
    midpoint_tangents = source_inputs["midpoint"][2]
    with np.load(causal.ENDPOINT.with_suffix(".npz")) as source:
        times = np.asarray(source["collocation_arc_parameters"], dtype=float)
    paths = {Path(__file__), Path(basis_certificate.__file__), Path(causal.__file__),
             Path(supplement.__file__), Path(causal.center.__file__),
             Path(causal.cert.__file__), Path(causal.component.scalar.__file__),
             ROOT / "src/bhsm/interface/current_green_supplemental_midpoint.py"}
    paths.update(path.with_suffix(".npz") for path in (
        causal.center.ENDPOINT, causal.center.REPLAY, causal.center.JACOBIAN,
        causal.center.PARTITION, causal.center.SCALAR))
    rows = []
    for index in sorted(indices):
        completion, recovered = supplement._completion(index, geometry)
        midpoint = causal._kinematic_midpoint_map(
            index, float(times[index + 1] - times[index]), axes,
            endpoint_tangents, midpoint_tangents,
        ).augmented
        approximate = np.linalg.solve(completion.full_basis, midpoint)
        row = certify_solve(completion.full_basis, midpoint, approximate)
        row.update(interval=index, basis_binary64_SHA256=_array_hash(completion.full_basis),
                   target_binary64_SHA256=_array_hash(midpoint),
                   approximate_coordinates_binary64_SHA256=_array_hash(approximate))
        rows.append(row)
        paths.add(recovered)
        paths.update(causal.MIXED_WORK / f"endpoint_{node:03d}.npz"
                     for node in (index, index + 1) if node > 0)
    complete = sorted(indices) == list(range(370))
    return {
        "artifact": "BHSM_N12_GATE7_MIDPOINT_COORDINATE_SOLVE",
        "status": "ALL_370_STORED_COORDINATE_SOLVES_ENCLOSED" if complete else "PARTIAL_STORED_COORDINATE_SOLVES_ENCLOSED",
        "scope": "SOLVE_ERROR_FOR_EXACT_BINARY64_BASIS_AND_TARGET_ONLY",
        "arithmetic_precision_bits": basis_certificate.PRECISION,
        "coverage": {"verified_midpoints": len(rows), "required_midpoints": 370, "complete": complete},
        "maximum_coordinate_error_infinity_upper": max(row["coordinate_error_infinity_upper"] for row in rows),
        "rows": rows,
        "inputs": {path.relative_to(ROOT).as_posix(): supplement._sha(path)
                   for path in sorted(paths)},
        "campaign_fingerprint": supplement._fingerprint(),
        "validation_passed": True,
        "claim_boundary": {
            "all_370_stored_coordinate_solve_errors_enclosed": complete,
            "physical_direction_construction_rounding_enclosed": False,
            "Hessian_rounding_enclosed": False,
            "physical_neighborhood_remainder_derived": False,
            "Gate7_closed": False,
            "FULL_BHSM_COMPLETE": False,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--indices", default=",".join(map(str, range(370))))
    parser.add_argument("--output", type=Path, default=RESULT)
    args = parser.parse_args()
    indices = [int(value) for value in args.indices.split(",")]
    if args.output.resolve() == RESULT.resolve() and sorted(indices) != list(range(370)):
        raise RuntimeError("partial verification must use a separate output path")
    payload = build_payload(indices)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in
                     ("status", "coverage", "maximum_coordinate_error_infinity_upper")}))


if __name__ == "__main__":
    main()
