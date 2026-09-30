"""Two outward native-curve point defects and their signed derivatives.

The unchanged action rate consumes P' as one augmented action direction.
This is a point pilot; it does not supply a shared-curve or tube remainder.
"""
from __future__ import annotations

import os
for _key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_key] = "1"

import argparse
from fractions import Fraction
import json
from pathlib import Path
import sys
import time

import numpy as np
from flint import arb, arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src"), str(ROOT / "scripts")]
from scripts.certify_n12_current_dop853_endpoint_rates import (
    DEFAULT_CENTER, VerifiedPointEigenline, owner, scalar_packet,
)
from scripts.materialize_n12_current_stop_endpoint_defects import _ball, _norm_packet, _sha
from scripts.audit_n12_c2_stop_dense_descriptor_first_hit import _dense_power, _derivative, _evaluate
from bhsm.interface.current_action_response_capture import evaluate_shared_rate

DEFAULT_OUTPUT = ROOT / "artifacts/current_runtime/current_stop_curve_derivative_pilot"


def native_curve_jet(left, coefficients, fraction: Fraction, width: Fraction):
    """Exact P, P', P'' in action-arc units, from the native alternating basis."""
    if width <= 0:
        raise ValueError("positive native interval width required")
    result = [[], [], []]
    for coordinate, value in enumerate(left):
        poly = _dense_power(value, coefficients[:, coordinate])
        for order in range(3):
            result[order].append(_evaluate(poly, fraction) / width ** order)
            poly = _derivative(poly)
    return tuple(result)


def strings(values):
    if isinstance(values, arb_mat):
        values = [[values[i, j] for j in range(values.ncols())] for i in range(values.nrows())]
    array = np.asarray(values, dtype=object)
    return np.asarray([v.str(140) for v in array.ravel()]).reshape(array.shape)


def point_rate(values, first, weights, reference):
    raw = np.asarray([_ball(values[i]) / _ball(Fraction.from_float(float(weights[i])))
                      for i in range(owner.STATE)], dtype=object)
    direction = None if first is None else np.asarray([_ball(v) for v in first], dtype=object)[:, None]
    eigenline = VerifiedPointEigenline()
    previous = owner._eigenline
    owner._eigenline = eigenline
    try:
        rate, internal = evaluate_shared_rate(owner, raw, _ball(values[-1]), weights, reference, direction)
    finally:
        owner._eigenline = previous
    if not internal["norm_G"].is_finite() or not internal["norm_G"] > 0:
        raise ArithmeticError("native point normalization is not verified positive")
    outputs = [rate.value] + ([] if first is None else [rate.derivative])
    if not all(v.is_finite() for array in outputs for v in array.flat):
        raise ArithmeticError("nonfinite native point rate or directional derivative")
    return rate, internal, eigenline, raw


def finite_difference_check(left, coefficients, width, weights, reference, rate, derivative, step):
    """Independent forward second-order finite differences at the initial point."""
    samples, arrays = {}, {}
    for multiplier in (Fraction(1, 2), Fraction(1), Fraction(2)):
        fraction = multiplier * step / width
        if not 0 < fraction <= 1:
            raise ValueError("finite difference sample must lie in the first stored interval")
        values, _, _ = native_curve_jet(left, coefficients, fraction, width)
        value, _, eigenline, _ = point_rate(values, None, weights, reference)
        samples[multiplier] = value.value
        label = "half" if multiplier == Fraction(1, 2) else "one" if multiplier == 1 else "two"
        arrays[label + "_fraction_exact"] = np.asarray(str(fraction))
        arrays[label + "_rate_balls"] = strings(value.value)
        arrays[label + "_gap_ball"] = np.asarray(eigenline.packet["selected_gap_lower"]["ball"])
    h = _ball(step)
    coarse = (-3 * rate + 4 * samples[Fraction(1)] - samples[Fraction(2)]) / (2 * h)
    fine = (-3 * rate + 4 * samples[Fraction(1, 2)] - samples[Fraction(1)]) / h
    coarse_error, fine_error = _norm_packet(coarse - derivative), _norm_packet(fine - derivative)
    derivative_norm = _norm_packet(derivative)
    relative = fine_error["upper"] / max(derivative_norm["lower"], 1e-300)
    packet = {"scope": "INDEPENDENT_POINT_DIAGNOSTIC_NO_UNIFORM_TRUNCATION_BOUND",
              "action_arc_step_exact": str(step), "method": "FORWARD_SECOND_ORDER_AT_h_AND_h_over_2",
              "coarse_error_norm": coarse_error, "fine_error_norm": fine_error,
              "fine_relative_error_upper": relative,
              "observed_fine_to_coarse_error_ratio": fine_error["upper"] / max(coarse_error["lower"], 1e-300),
              "diagnostic_passed": bool(relative < 1e-5)}
    arrays.update(coarse_directional_rate_balls=strings(coarse), fine_directional_rate_balls=strings(fine))
    return packet, arrays


def run(center: Path, output: Path, points: tuple[str, ...], precision: int, finite_difference_step: Fraction | None):
    started = time.perf_counter()
    ctx.prec = precision
    with np.load(center, allow_pickle=False) as source:
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
        left = np.asarray(source["fine_grid_augmented_action_values"], dtype=float)
        coefficients = np.asarray(source["fine_grid_DOP853_dense_coefficients"], dtype=float)
        grid = np.asarray(source["fine_grid_action_lengths"], dtype=float)
        terminal = int(source["stop_bracket_fine_grid_index"][0])
        stop_fraction = Fraction.from_float(float(source["stop_dense_fraction"][0]))
    output.mkdir(parents=True, exist_ok=True)
    dependencies = (center, Path(__file__), Path(owner.__file__),
                    ROOT / "scripts/certify_n12_current_dop853_endpoint_rates.py",
                    ROOT / "scripts/materialize_n12_current_stop_endpoint_defects.py",
                    ROOT / "scripts/audit_n12_c2_stop_dense_descriptor_first_hit.py",
                    ROOT / "src/bhsm/interface/current_action_response_capture.py",
                    ROOT / "src/bhsm/interface/aether_forward_c2_descriptor_cover.py")
    report = {"status": "CURRENT_NATIVE_CURVE_POINT_DERIVATIVE_PILOT_IN_PROGRESS",
              "center_SHA256": _sha(center), "source_SHA256": {str(p.resolve()): _sha(p) for p in dependencies},
              "precision_bits": precision, "selected_branch": 24, "native_intervals": terminal + 1,
              "definition": "d=P_prime-F(P); d_prime=P_second-DF(P)*P_prime in the same native action99 coordinates",
              "bordered_derivative_definition": "K*x_prime=r_prime-K_prime*x; signed operands combined before the verified solve",
              "scope": "OUTWARD_POINTS_ONLY_CURRENT_NATIVE_CURVE_NO_UNIFORM_REMAINDER_OR_FLOW_TUBE",
              "uniform_curve_defect_enclosed": False, "uniform_curve_defect_derivative_enclosed": False,
              "current_exact_history_shadowing_certified": False, "FULL_BHSM_COMPLETE": False,
              "requested_points": list(points), "points": {}}
    for name in points:
        interval, fraction = (0, Fraction(0)) if name == "native_initial" else (terminal, stop_fraction)
        width = Fraction.from_float(float(grid[interval + 1])) - Fraction.from_float(float(grid[interval]))
        values, first, second = native_curve_jet(left[interval], coefficients[interval], fraction, width)
        point_started = time.perf_counter()
        rate, internal, eigenline, raw = point_rate(values, first, weights, reference)
        directional = rate.derivative[:, 0]
        defect = np.asarray([_ball(v) - f for v, f in zip(first, rate.value, strict=True)], dtype=object)
        derivative_defect = np.asarray([_ball(v) - f for v, f in zip(second, directional, strict=True)], dtype=object)
        n = owner.REDUCED
        response = arb_mat([[v] for v in list(internal["hard"]) + [internal["bpsi"]]])
        combined = internal["hard_first_rhs"]
        dresponse = internal["dhard_b"]
        Kprime_x = arb_mat(n + 1, 1)
        for i in range(n):
            Kprime_x[i, 0] = (internal["H_first_on_hard"][i, 0]
                             - internal["deigenvalue"][0] * internal["hard"][i]
                             + internal["dpsi"][i, 0] * internal["bpsi"])
        Kprime_x[n, 0] = sum((internal["dpsi"][i, 0] * internal["hard"][i] for i in range(n)), arb(0))
        rprime = combined + Kprime_x
        solve_residual = internal["border"] * dresponse - combined
        eig_rhs = arb_mat(n + 1, 1)
        for i in range(n):
            eig_rhs[i, 0] = -internal["H_first_on_psi"][i, 0] + internal["deigenvalue"][0] * internal["psi"][i]
        eigen_derivative_residual = internal["border"] * internal["dpsi"] - eig_rhs
        arrays = {"native_value_exact": np.asarray([str(v) for v in values]),
                  "native_first_exact": np.asarray([str(v) for v in first]),
                  "native_second_exact": np.asarray([str(v) for v in second]),
                  "raw_point_balls": strings(raw), "normalized_rate_balls": strings(rate.value),
                  "directional_normalized_rate_balls": strings(directional),
                  "signed_defect_balls": strings(defect), "signed_derivative_defect_balls": strings(derivative_defect),
                  "state_weights_balls": strings([_ball(Fraction.from_float(float(v))) for v in weights]),
                  "branch_reference_balls": strings([_ball(Fraction.from_float(float(v))) for v in reference]),
                  "action_gradient_balls": strings(rate.action_jets.gradient_arb),
                  "action_hessian_balls": strings(rate.action_jets.hessian_arb),
                  "full_approximate_basis_balls": strings(eigenline.approximate_basis),
                  "normalized_point_eigenvector_balls": strings(eigenline.normalized_point),
                  "bordered_operator_balls": strings(internal["border"]),
                  "bordered_response_balls": strings(response),
                  "bordered_response_first_balls": strings(dresponse),
                  "bordered_combined_first_rhs_balls": strings(combined),
                  "bordered_rprime_balls": strings(rprime), "bordered_Kprime_x_balls": strings(Kprime_x),
                  "bordered_first_solve_residual_balls": strings(solve_residual),
                  "eigenline_first_solve_residual_balls": strings(eigen_derivative_residual)}
        for key in ("psi", "eigenvalue", "rhs", "bpsi", "cpsi", "remainder", "delta", "norm_G",
                    "descriptor", "configuration", "dpsi", "deigenvalue", "H_first_on_psi",
                    "H_first_on_hard", "raw_directions", "descriptor_first", "scalar_first_dc_dR_db_ddelta"):
            value = internal[key]
            arrays[key + "_balls"] = strings([value] if isinstance(value, arb) else value)
        row = {"native_interval": interval, "fraction_exact": str(fraction), "interval_width_exact": str(width),
               "action_arc_exact": str(Fraction.from_float(float(grid[interval])) + fraction * width),
               "spectral_enclosure": eigenline.packet,
               "state_defect_action_norm": _norm_packet(defect[:98]),
               "descriptor_defect": scalar_packet(defect[-1]),
               "augmented_defect_norm": _norm_packet(defect),
               "state_derivative_defect_action_norm": _norm_packet(derivative_defect[:98]),
               "descriptor_derivative_defect": scalar_packet(derivative_defect[-1]),
               "augmented_derivative_defect_norm": _norm_packet(derivative_defect),
               "directional_field_derivative_norm": _norm_packet(directional),
               "bordered_combined_first_rhs_norm": _norm_packet([combined[i, 0] for i in range(n + 1)]),
               "bordered_rprime_norm": _norm_packet([rprime[i, 0] for i in range(n + 1)]),
               "bordered_Kprime_x_norm": _norm_packet([Kprime_x[i, 0] for i in range(n + 1)]),
               "bordered_first_solve_residual_norm": _norm_packet([solve_residual[i, 0] for i in range(n + 1)]),
               "eigenline_first_solve_residual_norm": _norm_packet([eigen_derivative_residual[i, 0] for i in range(n + 1)]),
               "bordered_first_residual_contains_zero": all(v.contains(0) for v in [solve_residual[i, 0] for i in range(n + 1)]),
               "eigenline_first_residual_contains_zero": all(v.contains(0) for v in [eigen_derivative_residual[i, 0] for i in range(n + 1)]),
               "same_native_point_and_native_Pprime_direction": True,
               "normalization_positive": True, "all_rate_and_directional_components_finite": True}
        # Save costly point operands before optional diagnostic evaluations.
        path = output / (name + ".npz")
        np.savez_compressed(path, **arrays)
        row["output_arrays_SHA256"] = _sha(path)
        row["elapsed_seconds"] = time.perf_counter() - point_started
        report["points"][name] = row
        (output / "report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        print(json.dumps({"point": name, "elapsed_seconds": row["elapsed_seconds"],
                          "defect_norm": row["augmented_defect_norm"],
                          "derivative_defect_norm": row["augmented_derivative_defect_norm"]}), flush=True)
        if name == "native_initial" and finite_difference_step is not None:
            row["finite_difference"], fd_arrays = finite_difference_check(
                left[interval], coefficients[interval], width, weights, reference,
                rate.value, directional, finite_difference_step)
            fdpath = output / "native_initial_finite_difference.npz"
            np.savez_compressed(fdpath, **fd_arrays)
            row["finite_difference"]["output_arrays_SHA256"] = _sha(fdpath)
            print(json.dumps({"finite_difference": row["finite_difference"]}), flush=True)
    report["status"] = "CURRENT_NATIVE_CURVE_POINT_DEFECT_AND_DERIVATIVE_ENCLOSED"
    report["all_requested_points_completed"] = set(report["points"]) == set(points)
    report["elapsed_seconds"] = time.perf_counter() - started
    report["next_dependency"] = "SHARED_NATIVE_CURVE_SIGNED_DEFECT_AND_UNIFORM_REMAINDER_THEN_CURRENT_CONSTRAINED_GREEN_Y_Z1_Z2"
    (output / "report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--center", type=Path, default=DEFAULT_CENTER)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--points", nargs="+", choices=("native_initial", "native_terminal"), default=["native_initial", "native_terminal"])
    parser.add_argument("--precision", type=int, default=384)
    parser.add_argument("--finite-difference-step", type=Fraction, default=Fraction(1, 10000))
    parser.add_argument("--skip-finite-difference", action="store_true")
    args = parser.parse_args()
    run(args.center, args.output, tuple(args.points), args.precision,
        None if args.skip_finite_difference else args.finite_difference_step)


if __name__ == "__main__":
    main()
