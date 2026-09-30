"""Try a signed FTC defect enclosure on at most two first-native subcells.

The exact common-parameter polynomial is retained in the output. Containing
boxes feed the unchanged outward rate owner; their wrapping is diagnosed
explicitly rather than inferred to be a collision on the stored curve.
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
from flint import arb, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src"), str(ROOT / "scripts")]
from bhsm.interface.current_native_curve import load_native_cell
from bhsm.interface.current_action_response_capture import evaluate_shared_rate
from scripts import certify_n12_current_dop853_endpoint_rates as points
from scripts.materialize_n12_current_stop_endpoint_defects import _ball, _norm_packet, _sha
from scripts.certify_n12_current_stop_curve_derivative_pilot import strings

DEFAULT_ANCHOR = ROOT / "artifacts/current_runtime/current_stop_curve_derivative_pilot"
DEFAULT_OUTPUT = ROOT / "artifacts/current_runtime/current_first_native_ftc_defect_pilot"


def bound_ball(bounds):
    lower, upper = bounds
    return _ball((lower + upper) / 2) + arb(0, _ball((upper - lower) / 2).upper())


def exception_locals(error, function):
    trace = error.__traceback__
    while trace:
        if trace.tb_frame.f_code is function.__code__:
            return trace.tb_frame.f_locals
        trace = trace.tb_next
    return {}


class DiagnosticEigenline(points.VerifiedPointEigenline):
    def __init__(self):
        super().__init__()
        self.failure_packet = None
        self.failure_arrays = {}

    def __call__(self, hessian, midpoint, reference):
        try:
            return super().__call__(hessian, midpoint, reference)
        except ArithmeticError as error:
            local = exception_locals(error, points.spectrum_gap)
            if "epsilon" in local:
                selected = points.SELECTED
                values = local["values"]
                left = points.exact(values[selected]) - points.exact(values[selected - 1])
                right = points.exact(values[selected + 1]) - points.exact(values[selected])
                epsilon = local["epsilon"]
                separation = min(left.lower(), right.lower())
                self.failure_packet = {
                    "owner": "FULL_BASIS_WEYL_CONTAINING_BOX_GAP",
                    "box_all_eigenvalue_error_upper": points.scalar_packet(epsilon),
                    "numerical_hessian_midpoint_negative_side_separation": points.scalar_packet(left),
                    "numerical_hessian_midpoint_positive_side_separation": points.scalar_packet(right),
                    "negative_side_gap_lower": points.scalar_packet(local["left"].lower()),
                    "positive_side_gap_lower": points.scalar_packet(local["right"].lower()),
                    "twice_spectral_error_over_minimum_midpoint_separation": points.scalar_packet(2 * epsilon / separation),
                    "full_basis_orthogonality_upper": points.scalar_packet(local["eta"]),
                    "full_basis_residual_upper": points.scalar_packet(local["residual"]),
                    "claim": "A_CONTAINING_BOX_ENCLOSURE_FAILURE_IS_NOT_A_SPECTRAL_COLLISION_ON_THE_NATIVE_CURVE",
                }
                self.failure_arrays = {
                    "box_full_approximate_eigenvalues_balls": strings([points.exact(v) for v in values]),
                    "box_full_approximate_basis_balls": strings([[points.exact(v) for v in row] for row in local["vectors"]]),
                }
            raise


def run(center: Path, anchor: Path, output: Path):
    ctx.prec = 384
    started = time.perf_counter()
    output.mkdir(parents=True, exist_ok=True)
    anchor_report = json.loads((anchor / "report.json").read_text())
    initial = anchor_report["points"]["native_initial"]
    if anchor_report["center_SHA256"] != _sha(center):
        raise ValueError("anchor must bind this exact current center")
    if _sha(anchor / "native_initial.npz") != initial["output_arrays_SHA256"]:
        raise ValueError("initial point operand hash differs")
    for path, expected in anchor_report["source_SHA256"].items():
        if _sha(path) != expected:
            raise ValueError("initial point source fingerprint differs")
    with np.load(anchor / "native_initial.npz", allow_pickle=False) as source:
        anchor_value = tuple(Fraction(str(v)) for v in source["native_value_exact"])
        anchor_first = tuple(Fraction(str(v)) for v in source["native_first_exact"])
        anchor_defect = np.asarray([arb(str(v)) for v in source["signed_defect_balls"]], dtype=object)
    paths = [center, anchor / "report.json", anchor / "native_initial.npz", Path(__file__),
             ROOT / "src/bhsm/interface/current_native_curve.py", Path(points.__file__),
             Path(points.owner.__file__), ROOT / "src/bhsm/interface/current_action_response_capture.py",
             ROOT / "scripts/materialize_n12_current_stop_endpoint_defects.py"]
    report = {"status": "CURRENT_FIRST_NATIVE_FTC_DEFECT_PILOT_IN_PROGRESS",
              "center_SHA256": _sha(center), "source_fingerprint_convention": "SHA256; .py/.md/.json line endings normalized to LF; binary files unchanged",
              "sources": {str(p.resolve()): _sha(p) for p in paths},
              "precision_bits": 384, "selected_branch": 24,
              "scope": "FIRST_NATIVE_SUBCELL_CONTAINING_BOX_TRIAL_WITH_EXACT_COMMON_PARAMETER_POLYNOMIAL_RETAINED",
              "definition": "d'=P''-DF(P)P' combined before bounds; d(t)=d(a)+integral_a^t d'(s)ds",
              "uniform_defect_enclosed": False, "uniform_defect_derivative_enclosed": False,
              "current_exact_history_shadowing_certified": False, "FULL_BHSM_COMPLETE": False,
              "attempts": []}
    for right in (Fraction(1, 8), Fraction(1, 16)):
        cell = load_native_cell(center, 0, Fraction(0), right)
        if cell.jet_value(0, Fraction(-1)) != anchor_value or cell.jet_value(1, Fraction(-1)) != anchor_first:
            raise ValueError("native anchor value/direction differs from exact cell endpoint")
        arc_length = 2 * cell.arc_radius
        jets = [[bound_ball(v) for v in cell.jet_bounds(order)] for order in range(3)]
        raw_box = np.asarray([jets[0][i] / _ball(cell.state_weights[i]) for i in range(98)], dtype=object)
        directions = np.asarray(jets[1], dtype=object)[:, None]
        arrays = {"raw_containing_box_balls": strings(raw_box),
                  "action_value_containing_box_balls": strings(jets[0]),
                  "action_first_containing_box_balls": strings(jets[1]),
                  "action_second_containing_box_balls": strings(jets[2]),
                  "anchor_signed_defect_balls": strings(anchor_defect),
                  "state_weights_exact": np.asarray([str(v) for v in cell.state_weights]),
                  "branch_reference_balls": strings([points.exact(v) for v in cell.branch_reference])}
        for order in range(4):
            arrays["native_jet_" + str(order) + "_theta_power_exact"] = np.asarray([[str(v) for v in row] for row in cell.jet_coefficients(order)])
        eigenline = DiagnosticEigenline()
        previous = points.owner._eigenline
        points.owner._eigenline = eigenline
        row = {"interval": 0, "fraction_left_exact": "0", "fraction_right_exact": str(right),
               "arc_midpoint_exact": str(cell.arc_midpoint), "arc_radius_exact": str(cell.arc_radius),
               "arc_length_exact": str(arc_length), "anchor_exactly_matches_cell_left": True,
               "enclosed": False}
        attempt_started = time.perf_counter()
        try:
            rate, internal = evaluate_shared_rate(points.owner, raw_box, jets[0][-1],
                                                  np.asarray([float(v) for v in cell.state_weights]),
                                                  np.asarray(cell.branch_reference), directions)
            if not internal["norm_G"] > 0 or not all(v.is_finite() for v in rate.derivative.flat):
                raise ArithmeticError("positive norm and finite complete directional derivative required")
            derivative_defect = np.asarray(jets[2], dtype=object) - rate.derivative[:, 0]
            integration_time = bound_ball((Fraction(0), arc_length))
            defect = anchor_defect + integration_time * derivative_defect
            arrays.update(normalized_field_box_balls=strings(rate.value),
                          directional_field_derivative_box_balls=strings(rate.derivative),
                          signed_derivative_defect_box_balls=strings(derivative_defect),
                          ftc_signed_defect_box_balls=strings(defect),
                          action_gradient_balls=strings(rate.action_jets.gradient_arb),
                          action_hessian_balls=strings(rate.action_jets.hessian_arb),
                          bordered_operator_balls=strings(internal["border"]),
                          bordered_combined_first_rhs_balls=strings(internal["hard_first_rhs"]),
                          bordered_response_first_balls=strings(internal["dhard_b"]))
            row.update(enclosed=True, spectral_enclosure=eigenline.packet,
                       augmented_signed_derivative_defect_norm=_norm_packet(derivative_defect),
                       augmented_ftc_defect_norm=_norm_packet(defect),
                       descriptor_derivative_defect=points.scalar_packet(derivative_defect[-1]),
                       descriptor_ftc_defect=points.scalar_packet(defect[-1]))
        except (ArithmeticError, ZeroDivisionError) as error:
            row.update(error=repr(error), failure_owner=(eigenline.failure_packet or {}).get("owner", "RATE_OWNER_AFTER_SPECTRAL_ISOLATION"),
                       spectral_enclosure=eigenline.packet, spectral_failure=eigenline.failure_packet)
            local = exception_locals(error, points.owner._rate_enclosure)
            if "jets" in local:
                arrays["action_gradient_balls"] = strings(local["jets"].gradient_arb)
                arrays["action_hessian_balls"] = strings(local["jets"].hessian_arb)
            arrays.update(eigenline.failure_arrays)
        finally:
            points.owner._eigenline = previous
        path = output / ("fraction_0_to_1_over_" + str(right.denominator) + ".npz")
        np.savez_compressed(path, **arrays)
        row.update(output_arrays_SHA256=_sha(path), output_arrays_path=str(path.resolve()),
                   elapsed_seconds=time.perf_counter() - attempt_started)
        report["attempts"].append(row)
        (output / "report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        print(json.dumps(row, allow_nan=False), flush=True)
        if row["enclosed"]:
            report.update(uniform_defect_enclosed=True, uniform_defect_derivative_enclosed=True)
            break
    report["status"] = ("CURRENT_FIRST_NATIVE_SUBCELL_FTC_SIGNED_DEFECT_ENCLOSED" if report["uniform_defect_enclosed"]
                        else "CURRENT_FIRST_NATIVE_FTC_DEFECT_PILOT_OPEN_AT_REPORTED_OWNER")
    report["elapsed_seconds"] = time.perf_counter() - started
    report["next_dependency"] = ("EXTEND_SHARED_CURVE_AND_CURRENT_CONSTRAINED_GREEN_Y_Z1_Z2" if report["uniform_defect_enclosed"]
                                 else "CURRENT_COMMON_PARAMETER_MOVING_EIGENPAIR_AND_SIGNED_IMPLICIT_RESIDUAL_INCLUSION_AVOIDING_STATE_BOX_SPECTRAL_WRAPPING")
    (output / "report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--center", type=Path, default=points.DEFAULT_CENTER)
    parser.add_argument("--anchor", type=Path, default=DEFAULT_ANCHOR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.center, args.anchor, args.output)
