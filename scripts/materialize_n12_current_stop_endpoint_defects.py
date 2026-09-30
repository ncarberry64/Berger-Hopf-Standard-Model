"""Exact native DOP853 derivative minus cached outward endpoint action rate.

The native terminal rate has the same polynomial point as the derivative.
The first cached rate instead uses the stored raw center; its tiny reference
translation is retained explicitly and is not silently turned into a native
initial defect enclosure. No action or eigenline is reevaluated here.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
from flint import arb, ctx, fmpq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from audit_n12_c2_stop_dense_descriptor_first_hit import _dense_power, _derivative, _evaluate

DEFAULT_CENTER = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
DEFAULT_RATES = ROOT / "artifacts/current_runtime/current_dop853_endpoint_rates"
DEFAULT_OUT = ROOT / "artifacts/current_runtime/current_stop_endpoint_defects"
THEORY = ROOT / "theory/n12_current_stop_endpoint_defects.md"


def _sha(path):
    path = Path(path)
    data = path.read_bytes()
    if path.suffix in {".py", ".md", ".json"}:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest().upper()


def _ball(value: Fraction):
    return arb(fmpq(value.numerator, value.denominator))


def native_value_derivative(left, coefficients, fraction, width):
    """Exact action value and action-arc derivative of all 99 coordinates."""
    values, derivatives = [], []
    for index, value in enumerate(left):
        poly = _dense_power(value, coefficients[:, index])
        values.append(_evaluate(poly, fraction))
        derivatives.append(_evaluate(_derivative(poly), fraction) / width)
    return values, derivatives


def _packet(value):
    if not value.is_finite():
        raise ArithmeticError("nonfinite endpoint defect")
    return {"ball": value.str(140),
            "lower": math.nextafter(float(value.lower()), -math.inf),
            "upper": math.nextafter(float(value.upper()), math.inf)}


def _norm_packet(values):
    absolute_lower = [abs(value).lower() for value in values]
    # Arb may return a tiny negative outward lower endpoint for abs(x) when
    # x contains zero; squaring that endpoint would invent a positive lower
    # norm bound. The mathematical absolute lower bound is max(0, endpoint).
    lower = sum(((value if value > 0 else arb(0)) ** 2 for value in absolute_lower), arb(0)).sqrt().lower()
    upper = sum((abs(value).upper() ** 2 for value in values), arb(0)).sqrt().upper()
    return {"lower": max(0.0, math.nextafter(float(lower), -math.inf)),
            "upper": math.nextafter(float(upper), math.inf)}


def run(center: Path, rates: Path, out: Path):
    start = time.perf_counter()
    rate_report = json.loads((rates / "report.json").read_text(encoding="utf-8"))
    center_sha = _sha(center)
    if rate_report["center_SHA256"] != center_sha or not rate_report["all_requested_point_rates_finite"]:
        raise ValueError("cached endpoint rate packet must bind this center")
    with np.load(center, allow_pickle=False) as z:
        left = np.array(z["fine_grid_augmented_action_values"])
        coefficients = np.array(z["fine_grid_DOP853_dense_coefficients"])
        grid = np.array(z["fine_grid_action_lengths"])
        weights = np.array(z["state_weights"])
        initial_raw = np.array(z["centers"][0])
        initial_s = float(z["signed_descriptors"][0])
        terminal_index = int(np.ravel(z["stop_bracket_fine_grid_index"])[0])
        terminal_fraction = float(np.ravel(z["stop_dense_fraction"])[0])
    if rate_report["terminal_interval"] != terminal_index or rate_report["terminal_fraction"] != terminal_fraction:
        raise ValueError("cached terminal point definition changed")
    arrays, points = {"state_weights": weights}, {}
    with np.load(rates / "point_balls.npz", allow_pickle=False) as z, ctx.workprec(384):
        for name, index, fraction_float in (("first_stored", 0, 0.0),
                                            ("native_terminal", terminal_index, terminal_fraction)):
            fraction = Fraction.from_float(fraction_float)
            width = Fraction.from_float(float(grid[index + 1])) - Fraction.from_float(float(grid[index]))
            values, derivative = native_value_derivative(left[index], coefficients[index], fraction, width)
            cached_raw = [arb(str(value)) for value in z[name + "_raw_state_balls"]]
            cached_rate = [arb(str(value)) for value in z[name + "_normalized_rate_balls"]]
            reference_difference = [_ball(values[i]) - _ball(Fraction.from_float(float(weights[i]))) * cached_raw[i]
                                    for i in range(98)]
            if name == "native_terminal":
                matching = all(value.contains(0) for value in reference_difference)
                if not matching:
                    raise ValueError("cached terminal raw point does not enclose native polynomial point")
            else:
                matching = all(values[i] == Fraction.from_float(float(weights[i])) * Fraction.from_float(float(initial_raw[i])) for i in range(98))
                if values[-1] != Fraction.from_float(initial_s):
                    raise ValueError("initial scalar reference differs")
                if not all((cached_raw[i] - _ball(Fraction.from_float(float(initial_raw[i])))).contains(0) for i in range(98)):
                    raise ValueError("cached initial raw point differs from stored center")
            defect = [_ball(value) - rate for value, rate in zip(derivative, cached_rate, strict=True)]
            source = [-value for value in defect]
            worst = max(range(98), key=lambda i: float(abs(defect[i]).upper()))
            points[name] = {"native_interval": index, "fraction_exact": str(fraction),
                "action_arc": float(Fraction.from_float(float(grid[index])) + fraction * width),
                "rate_reference_matches_native_point": matching,
                "native_state_defect_enclosed": matching,
                "descriptor_reference_is_same_polynomial_scalar": True,
                "state_defect_action_norm": _norm_packet(defect[:98]),
                "descriptor_defect": _packet(defect[-1]),
                "descriptor_signed_source": _packet(source[-1]),
                "maximum_absolute_state_defect_coordinate": worst,
                "maximum_state_defect_component": _packet(defect[worst]),
                "native_to_cached_action_reference_difference_norm": _norm_packet(reference_difference),
                "scope": "NATIVE_POINT_DEFECT" if matching else "NATIVE_DERIVATIVE_MINUS_STORED_RAW_REFERENCE_RATE_REQUIRES_TRANSLATION_BOUND"}
            arrays[name + "_native_value_exact"] = np.array([str(value) for value in values])
            arrays[name + "_native_derivative_exact"] = np.array([str(value) for value in derivative])
            arrays[name + "_defect_balls"] = np.array([value.str(140) for value in defect])
            arrays[name + "_signed_source_balls"] = np.array([value.str(140) for value in source])
            arrays[name + "_action_reference_difference_balls"] = np.array([value.str(140) for value in reference_difference])
    out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out / "arrays.npz", **arrays)
    sources = [center, rates / "report.json", rates / "point_balls.npz", Path(__file__), THEORY,
               ROOT / "scripts/audit_n12_c2_stop_dense_descriptor_first_hit.py"]
    report = {"status": "CURRENT_DOP853_CACHED_ENDPOINT_SIGNED_DEFECT_INPUTS_MATERIALIZED",
        "center_SHA256": center_sha, "native_intervals": len(coefficients), "precision_bits": 384,
        "definition": "d=P_prime-F; signed causal source=-d; first98 coordinates are action weighted, scalar99 is the stored descriptor",
        "points": points, "source_SHA256": {str(path.resolve()): _sha(path) for path in sources},
        "cached_rate_owner_source_SHA256": rate_report.get("source_SHA256", {}),
        "output_arrays_SHA256": _sha(out / "arrays.npz"),
        "native_terminal_signed_point_defect_enclosed": points["native_terminal"]["native_state_defect_enclosed"],
        "initial_native_rate_translation_enclosed": points["first_stored"]["rate_reference_matches_native_point"],
        "uniform_curve_defect_enclosed": False, "current_exact_history_shadowing_certified": False,
        "next_dependency": "COMMON_PARAMETER_CURVE_DEFECT_AND_UNIFORM_REMAINDER_ON1395_COVER;PHYSICAL_CONSTRAINT_NORMAL_RESTORATION;CURRENT_CAUSAL_GREEN_Y_Z1_Z2",
        "elapsed_seconds": time.perf_counter() - start, "FULL_BHSM_COMPLETE": False}
    (out / "report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("status", "center_SHA256", "points", "elapsed_seconds")}, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--center", type=Path, default=DEFAULT_CENTER)
    parser.add_argument("--rates", type=Path, default=DEFAULT_RATES)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    run(args.center, args.rates, args.out)
