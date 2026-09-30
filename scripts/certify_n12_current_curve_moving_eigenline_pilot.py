"""A common-curve moving eigenline predictor, certified by spectral residual.

No coordinate-box Hessian or new eigenpair Newton inverse is used. The
unchanged retained action evaluates H(theta)*p_hat(theta) as one contracted
shared Taylor gradient. The existing current spectral gap supplies isolation.
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
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
from bhsm.interface.current_native_curve import load_native_cell, bernstein_range
from bhsm.interface.shared_action_taylor import Taylor, TaylorDomain
from bhsm.interface.shared_action_gradient import gradient
from scripts.certify_n12_current_dop853_endpoint_rates import DEFAULT_CENTER, owner, scalar_packet
from scripts.certify_n12_current_stop_constraint_endpoints import fingerprint

DEFAULT_POINTS = ROOT / "artifacts/current_runtime/current_stop_curve_derivative_pilot"
DEFAULT_SPECTRUM = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_STOP_DOP853_PROJECTOR_REFINED_BOUNDARY_CLUSTER_SPECTRUM.json"
DEFAULT_OUTPUT = ROOT / "artifacts/current_runtime/current_first_native_moving_eigenline_pilot"


def ball(value):
    value = Fraction(value)
    return arb(value.numerator) / arb(value.denominator)


def models(array, domain):
    """Complete affine model plus containing Bernstein bound of its exact tail."""
    result = []
    for column in np.asarray(array, dtype=object).T:
        tail = [Fraction(0), Fraction(0), *column[2:]]
        lo, hi = bernstein_range(tail)
        radius = ball(max(abs(lo), abs(hi))).upper()
        result.append(domain.affine(ball(column[0]), [ball(column[1])], radius))
    return result


def save_models(values):
    return np.asarray([[v.c.str(140), v.a[0, 0].str(140), v.r.str(140)] for v in values])


def support_norm(values):
    return sum((v.support() ** 2 for v in values), arb(0)).sqrt().upper()


def read_balls(values):
    a = np.asarray(values)
    return np.asarray([arb(str(v)) for v in a.flat], dtype=object).reshape(a.shape)


def run(center, points, spectrum, output, right):
    started = time.perf_counter()
    ctx.prec = 384
    output.mkdir(parents=True, exist_ok=True)
    cell = load_native_cell(center, 0, Fraction(0), right)
    point_report = json.loads((points / "report.json").read_text())
    spectral = json.loads(spectrum.read_text())
    if point_report["center_SHA256"] != cell.source_sha256:
        raise ValueError("native point jets and common curve have different centers")
    if not spectral["validation_passed"] or spectral["unresolved_cells"]:
        raise ValueError("completed current same-curve spectral proof required")
    if cell.source_sha256 not in json.dumps(spectral["inputs"]):
        raise ValueError("current spectral proof does not bind this center")
    rows = sorted((row for row in spectral["rows"] if row["interval"] == 0),
                  key=lambda r: Fraction(r["dyadic_start"]))
    cover, end = [], Fraction(0)
    for row in rows:
        lo, hi = Fraction(row["dyadic_start"]), Fraction(row["dyadic_end"])
        if lo != end:
            raise ValueError("current spectral prefix is not a complete cover")
        cover.append(row)
        end = hi
        if end >= right:
            break
    if end < right:
        raise ValueError("common curve pilot is outside the current spectral cover")
    gap = min(arb(float(row[key])) for row in cover
              for key in ("negative_selected_gap_lower", "selected_positive_gap_lower"))
    if not gap > 0:
        raise ValueError("strict current selected-to-hard gap required")
    with np.load(points / "native_initial.npz", allow_pickle=False) as a:
        if tuple(Fraction(str(v)) for v in a["native_value_exact"]) != cell.jet_value(0, Fraction(-1)):
            raise ValueError("native left endpoint is not the saved point")
        if tuple(Fraction(str(v)) for v in a["native_first_exact"]) != cell.jet_value(1, Fraction(-1)):
            raise ValueError("native initial jet is not the saved point jet")
        psi = read_balls(a["psi_balls"])
        dpsi = read_balls(a["dpsi_balls"])[:61, 0]
        lam = read_balls(a["eigenvalue_balls"])[0]
        dlam = read_balls(a["deigenvalue_balls"])[0]
    domain = TaylorDomain([(0, 1, "interval")], 1)
    action_models = models(cell.jet_coefficients(), domain)
    state = [v / ball(w) for v, w in zip(action_models[:98], cell.state_weights, strict=True)]
    radius = ball(cell.arc_radius)
    # Exact midpoint coefficients define a fixed continuous proposal.
    p = [domain.affine(v.mid() + radius * dv.mid(), [radius * dv.mid()])
         for v, dv in zip(psi, dpsi, strict=True)]
    eigenvalue = domain.affine(lam.mid() + radius * dlam.mid(), [radius * dlam.mid()])
    raw_leg = [arb(0)] * 37 + p
    packet = {"status": "CURRENT_MOVING_EIGENLINE_SHARED_CURVE_PILOT_IN_PROGRESS",
              "scope": "ONE_NATIVE_CURVE_CELL_VALUE_EIGENLINE_ONLY",
              "center_SHA256": cell.source_sha256, "interval": 0,
              "fraction_left": "0", "fraction_right": str(right),
              "arc_radius": str(cell.arc_radius), "precision_bits": ctx.prec,
              "selected_branch": 24, "spectral_owners": cover,
              "selected_to_other_gap_lower": scalar_packet(gap),
              "continuous_history_certified": False,
              "uniform_curve_defect_certified": False}
    arrays = {"native_common_theta_coefficients_exact": np.asarray([[str(v) for v in row] for row in cell.jet_coefficients()]),
              "raw_state_taylor_c_a_r_balls": save_models(state),
              "predictor_eigenvector_taylor_c_a_r_balls": save_models(p),
              "predictor_eigenvalue_taylor_c_a_r_balls": save_models([eigenvalue])}
    output_arrays = output / "arrays.npz"
    np.savez_compressed(output_arrays, **arrays)
    (output / "report.json").write_text(json.dumps(packet, indent=2) + "\n")
    def progress(done, total):
        print(json.dumps({"shared_Hpsi_nodes": done, "total": total}), flush=True)
    full_hpsi = gradient(owner, state, [raw_leg], progress)
    hpsi = full_hpsi[37:]
    residual = [h - eigenvalue * v for h, v in zip(hpsi, p, strict=True)]
    squared = sum((v * v for v in p), domain.affine(0))
    norm_squared = squared.enclosure()
    if not norm_squared > 0:
        raise ArithmeticError("moving eigenvector proposal normalization crosses zero")
    norm_lower = norm_squared.sqrt().lower()
    raw_residual = support_norm(residual)
    normalized_residual = (raw_residual / norm_lower).upper()
    # At the left endpoint, both the reference eigenline and lambda are
    # already certified for this exact same native point.
    initial_distance = sum((abs(v.c - v.a[0, 0] - truth).upper() ** 2
                            for v, truth in zip(p, psi, strict=True)), arb(0)).sqrt().upper()
    initial_lambda_error = abs(eigenvalue.c - eigenvalue.a[0, 0] - lam).upper()
    matched = bool(initial_distance < arb(1)/2 and initial_lambda_error < gap/4)
    closed = bool(matched and 2 * normalized_residual < gap)
    # For continuous H, p_hat, lambda_hat, the selected and hard residual
    # neighborhoods stay disjoint when 2*r<gap. Initial matching therefore
    # fixes branch24 on the whole connected cell. The other spectrum is at
    # distance at least gap-r from lambda_hat. Spectral expansion gives the
    # oriented unit-vector distance <=2*r/(gap-r).
    packet.update(status="CURRENT_MOVING_EIGENLINE_COMMON_CURVE_RESIDUAL_CERTIFIED" if closed
                  else "CURRENT_MOVING_EIGENLINE_COMMON_CURVE_RESIDUAL_TOO_WIDE",
                  unnormalized_residual_norm_upper=scalar_packet(raw_residual),
                  predictor_norm_squared_enclosure=scalar_packet(norm_squared),
                  predictor_norm_lower=scalar_packet(norm_lower),
                  normalized_residual_norm_upper=scalar_packet(normalized_residual),
                  residual_to_gap_ratio=scalar_packet(normalized_residual / gap),
                  initial_point_line_distance_upper=scalar_packet(initial_distance),
                  initial_point_eigenvalue_error_upper=scalar_packet(initial_lambda_error),
                  initial_branch_matched=matched, uniform_value_eigenline_certified=closed,
                  method="One common-theta affine predictor; exact polynomial tails and all action Taylor remainders retained; H*p_hat contracted before signed residual support",
                  branch_matching="Continuity from the certified identical native initial point; disjoint selected/hard residual neighborhoods because 2*r<g",
                  normalization_is_physical_state_only=True)
    if closed:
        packet["eigenvalue_error_upper"] = scalar_packet(normalized_residual)
        packet["oriented_unit_eigenvector_distance_upper"] = scalar_packet((2 * normalized_residual / (gap-normalized_residual)).upper())
    arrays.update(action_Hpsi_taylor_c_a_r_balls=save_models(full_hpsi),
                  signed_eigenline_residual_taylor_c_a_r_balls=save_models(residual),
                  predictor_norm_squared_taylor_c_a_r_balls=save_models([squared]))
    np.savez_compressed(output_arrays, **arrays)
    paths = [center, points / "report.json", points / "native_initial.npz", spectrum, Path(__file__),
             Path(owner.__file__), ROOT / "src/bhsm/interface/current_native_curve.py",
             ROOT / "src/bhsm/interface/shared_action_taylor.py",
             ROOT / "src/bhsm/interface/shared_action_gradient.py",
             ROOT / "src/bhsm/interface/factored_arb_integrand.py",
             ROOT / "src/bhsm/interface/shared_parameter_residual.py"]
    packet["source_fingerprint_convention"] = "SHA256 with LF-normalized .py/.md/.json; raw binary bytes"
    packet["sources"] = {str(path.resolve()): fingerprint(path) for path in paths}
    packet["arrays_SHA256"] = fingerprint(output_arrays)
    packet["elapsed_seconds"] = time.perf_counter() - started
    (output / "report.json").write_text(json.dumps(packet, indent=2, allow_nan=False) + "\n")
    print(json.dumps({key: packet[key] for key in ("status", "normalized_residual_norm_upper", "residual_to_gap_ratio", "elapsed_seconds")}), flush=True)
    return packet


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--center", type=Path, default=DEFAULT_CENTER)
    parser.add_argument("--points", type=Path, default=DEFAULT_POINTS)
    parser.add_argument("--spectrum", type=Path, default=DEFAULT_SPECTRUM)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--right", type=Fraction, default=Fraction(1, 8))
    args = parser.parse_args()
    run(args.center, args.points, args.spectrum, args.output, args.right)
