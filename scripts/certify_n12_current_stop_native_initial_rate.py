"""Outward rate and signed defect at the exact native initial DOP853 point.

This independent packet removes the stored-raw-to-native rate translation
obligation at the initial point. It does not enclose a curve or an orbit.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path
import sys
import time

import numpy as np
from flint import arb, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from scripts.certify_n12_current_dop853_endpoint_rates import (
    DEFAULT_CENTER, VerifiedPointEigenline, scalar_packet, owner,
)
from scripts.materialize_n12_current_stop_endpoint_defects import (
    native_value_derivative, _ball, _norm_packet, _sha,
)
from bhsm.interface.current_action_response_capture import evaluate_shared_rate

DEFAULT_OUTPUT = ROOT / "artifacts/current_runtime/current_stop_native_initial_rate"


def strings(values):
    a = np.asarray(values, dtype=object)
    return np.asarray([v.str(140) for v in a.ravel()]).reshape(a.shape)


def run(center: Path, output: Path):
    started = time.perf_counter()
    ctx.prec = 384
    with np.load(center, allow_pickle=False) as z:
        weights = np.asarray(z["state_weights"], dtype=float)
        reference = np.asarray(z["branch_reference"], dtype=float)
        grid = np.asarray(z["fine_grid_action_lengths"], dtype=float)
        initial = np.asarray(z["centers"][0], dtype=float)
        width = Fraction.from_float(float(grid[1])) - Fraction.from_float(float(grid[0]))
        values, derivative = native_value_derivative(
            z["fine_grid_augmented_action_values"][0],
            z["fine_grid_DOP853_dense_coefficients"][0], Fraction(0), width,
        )
    w = np.asarray([_ball(Fraction.from_float(float(v))) for v in weights], dtype=object)
    raw = np.asarray([_ball(values[i]) / w[i] for i in range(98)], dtype=object)
    descriptor = _ball(values[-1])
    eigenline = VerifiedPointEigenline()
    previous = owner._eigenline
    owner._eigenline = eigenline
    try:
        rate, internal = evaluate_shared_rate(owner, raw, descriptor, weights, reference, None)
    finally:
        owner._eigenline = previous
    if not internal["norm_G"].is_finite() or not internal["norm_G"] > 0:
        raise ArithmeticError("native initial field norm is not verified positive")
    if not all(v.is_finite() for v in rate.value):
        raise ArithmeticError("nonfinite native initial rate")
    defect = np.asarray([_ball(d) - f for d, f in zip(derivative, rate.value, strict=True)], dtype=object)
    source = -defect
    reference_difference = np.asarray([_ball(values[i]) - w[i] * _ball(Fraction.from_float(float(initial[i]))) for i in range(98)], dtype=object)
    graph_residual = internal["eigenvalue"] - descriptor
    output.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output / "arrays.npz",
        state_weights_balls=strings(w),
        branch_reference_balls=strings([_ball(Fraction.from_float(float(v))) for v in reference]),
        native_initial_raw_point_balls=strings(raw),
        native_initial_action_value_exact=np.asarray([str(v) for v in values]),
        native_initial_action_arc_derivative_exact=np.asarray([str(v) for v in derivative]),
        native_initial_normalized_rate_balls=strings(rate.value),
        native_initial_signed_defect_balls=strings(defect),
        native_initial_signed_source_balls=strings(source),
        native_to_stored_action_reference_difference_balls=strings(reference_difference),
        native_initial_eigenvector_balls=strings(internal["psi"]),
        native_initial_hard_response_balls=strings(internal["hard"]),
        native_initial_reduced_hessian_balls=strings(eigenline.reduced_hessian),
        native_initial_full_approximate_basis_balls=strings(eigenline.approximate_basis),
        native_initial_normalized_point_eigenvector_balls=strings(eigenline.normalized_point),
    )
    paths = [center, Path(__file__), Path(owner.__file__),
             ROOT / "scripts/certify_n12_current_dop853_endpoint_rates.py",
             ROOT / "scripts/materialize_n12_current_stop_endpoint_defects.py",
             ROOT / "scripts/audit_n12_c2_stop_dense_descriptor_first_hit.py",
             ROOT / "src/bhsm/interface/current_action_response_capture.py"]
    report = {
        "status": "CURRENT_NATIVE_INITIAL_POINT_RATE_AND_SIGNED_DEFECT_ENCLOSED",
        "center_SHA256": _sha(center), "precision_bits": 384,
        "definition": "Exact native interval0 fraction0 action point divided by exact imported weights; d=P_prime-F and signed source=-d at that identical point.",
        "native_interval": 0, "fraction_exact": "0", "action_arc_width_exact": str(width),
        "initial_native_rate_translation_enclosed": True,
        "stored_raw_reference_translation_required": False,
        "same_point_signed_defect_enclosed": True,
        "state_defect_action_norm": _norm_packet(defect[:98]),
        "augmented_defect_norm": _norm_packet(defect),
        "descriptor_defect": scalar_packet(defect[-1]),
        "descriptor_signed_source": scalar_packet(source[-1]),
        "descriptor_arc_rate": scalar_packet(rate.value[-1]),
        "Delta": scalar_packet(internal["delta"]),
        "cancelled_field_norm": scalar_packet(internal["norm_G"]),
        "native_to_stored_action_reference_difference_norm": _norm_packet(reference_difference),
        "selected_descriptor_graph_residual": scalar_packet(graph_residual),
        "selected_descriptor_graph_residual_contains_zero": graph_residual.contains(0),
        "spectral_enclosure": eigenline.packet,
        "source_fingerprint_convention": "SHA256; .py/.md/.json LF-normalized; binaries unchanged",
        "source_SHA256": {str(path.resolve()): _sha(path) for path in paths},
        "output_arrays_SHA256": _sha(output / "arrays.npz"),
        "scope": "EXACT_NATIVE_INITIAL_POINT_ONLY",
        "uniform_curve_defect_enclosed": False,
        "current_exact_history_shadowing_certified": False,
        "elapsed_seconds": time.perf_counter() - started,
    }
    (output / "report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in
                     ("status", "center_SHA256", "state_defect_action_norm", "descriptor_defect", "descriptor_arc_rate", "elapsed_seconds")}), flush=True)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--center", type=Path, default=DEFAULT_CENTER)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.center, args.output)
