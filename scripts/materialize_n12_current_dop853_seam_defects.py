"""Retain signed dyadic seam jumps for the current correlated shadow equation.

At the right endpoint the native DOP853 dense polynomial is exactly
left+F[0]. Recorded binary64 next-left values can differ from that exact sum.
An exact continuous history therefore obeys e_plus=e_minus-jump at a seam.
These point sources must accompany the continuous source minus the defect.
No flow evaluation, reintegration, or shadowing claim is made here.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

from flint import arb, ctx, fmpq
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CENTER = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
DEFAULT_OUTPUT = ROOT / "artifacts/current_runtime/current_stop_seam_defects"


def endpoint_jumps(values: np.ndarray, coefficients: np.ndarray, stop_interval: int) -> list[list[Fraction]]:
    """Return next-left minus exact prior-right in all augmented coordinates."""
    values, coefficients = np.asarray(values), np.asarray(coefficients)
    if (values.ndim != 2 or coefficients.shape != (values.shape[0]-1, 7, values.shape[1])
            or not 0 <= stop_interval < coefficients.shape[0]
            or not np.all(np.isfinite(values)) or not np.all(np.isfinite(coefficients))):
        raise ValueError("finite aligned native degree-seven dense arrays required")
    return [[Fraction.from_float(float(values[i+1, j]))
             - Fraction.from_float(float(values[i, j]))
             - Fraction.from_float(float(coefficients[i, 0, j]))
             for j in range(values.shape[1])] for i in range(stop_interval)]


def norm_upper(vector: list[Fraction]) -> float:
    squared = sum((value*value for value in vector), Fraction(0))
    if squared == 0:
        return 0.0
    with ctx.workprec(256):
        bound = arb(fmpq(squared.numerator, squared.denominator)).sqrt().upper()
        return math.nextafter(float(bound), math.inf)


def run(center: Path, output: Path) -> dict:
    with np.load(center, allow_pickle=False) as source:
        values = source["fine_grid_augmented_action_values"]
        coefficients = source["fine_grid_DOP853_dense_coefficients"]
        grid = source["fine_grid_action_lengths"]
        stop = int(source["stop_bracket_fine_grid_index"][0])
        weights = source["state_weights"]
    if values.shape[1] != 99 or weights.shape != (98,) or not np.all(np.diff(grid) > 0):
        raise ValueError("current N12 augmented action coordinates required")
    jumps = endpoint_jumps(values, coefficients, stop)
    rows = [dict(seam=i+1, action_length=float(grid[i+1]),
                 state_jump_2_norm_upper=norm_upper(row[:-1]),
                 descriptor_jump_exact=str(row[-1]),
                 nonzero_coordinates=sum(value != 0 for value in row))
            for i, row in enumerate(jumps)]
    signed_sum = [sum((row[j] for row in jumps), Fraction(0)) for j in range(99)]
    absolute_sum = sum((Fraction.from_float(row["state_jump_2_norm_upper"]) for row in rows), Fraction(0))
    output.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(output / "arrays.npz",
        seam_action_lengths=grid[1:stop+1],
        signed_jump_exact=np.asarray([[str(value) for value in row] for row in jumps]),
        signed_jump_binary64=np.asarray([[float(value) for value in row] for row in jumps]),
        state_jump_2_norm_upper=np.asarray([row["state_jump_2_norm_upper"] for row in rows]),
        state_weights=weights,
        center_SHA256=np.asarray(hashlib.sha256(center.read_bytes()).hexdigest().upper()))
    report = dict(status="CURRENT_DOP853_SIGNED_DYADIC_SEAM_DEFECTS_MATERIALIZED",
        center=str(center.resolve()), center_SHA256=hashlib.sha256(center.read_bytes()).hexdigest().upper(),
        source_script_SHA256=hashlib.sha256(Path(__file__).read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper(),
        retained_native_intervals=stop+1, preterminal_seams=len(rows),
        maximum_state_jump_2_norm_upper=max((row["state_jump_2_norm_upper"] for row in rows), default=0),
        untransported_state_jump_norm_sum_upper=math.nextafter(float(absolute_sum), math.inf) if absolute_sum else 0,
        untransported_signed_state_jump_sum_2_norm_upper=norm_upper(signed_sum[:-1]),
        signed_descriptor_jump_sum_exact=str(signed_sum[-1]), rows=rows,
        shadow_equation_seam_sign="e_plus=e_minus-jump; causal Green source is -jump",
        authority="EXACT_RATIONAL_BINARY64_INPUTS; OUTWARD_ARB256_NORMS; SIGNED_VECTORS_RETAINED",
        validation_passed=len(rows) == stop,
        exact_flow_shadowing_certified=False,
        next="COMPOSE_SIGNED_SEAM_SOURCES_WITH_CONTINUOUS_MINUS_DEFECT_IN_THE_SAME_CORRELATED_GREEN_FRAME",
        outputs=dict(arrays=str((output / "arrays.npz").resolve())))
    (output / "report.json").write_text(json.dumps(report, indent=2, allow_nan=False)+"\n", encoding="utf-8", newline="\n")
    print(json.dumps({key:value for key,value in report.items() if key not in ("rows",)}, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--center", type=Path, default=DEFAULT_CENTER)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.center, args.output)
