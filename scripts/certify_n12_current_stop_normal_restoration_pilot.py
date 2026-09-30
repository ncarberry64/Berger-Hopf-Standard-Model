"""Fixed-tangent C25 normal restoration at the native current terminal point.

The unknown is nu in an action-coordinate Euclidean 25-ball, with
Y(nu)=P+W^-1 N nu and C(Y)=(S_m, v.S_v-S).  A fixed exact midpoint
preconditioner B defines T(nu)=nu-B C(Y(nu)).  An outward enclosure of
DC(Y) W^-1 N on a containing raw-coordinate box gives the Banach bound
||DT||_2 <= ||I-B DC(Y) W^-1 N||_F.  This is one point normal slice,
not a continuous history or a fixed-descriptor chart certificate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

import numpy as np
from flint import arb, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.certify_n12_current_stop_constraint_endpoints import (
    DEFAULT_OUTPUT as DEFAULT_CONSTRAINTS,
    DEFAULT_POINTS,
    action_value_and_maps,
    fingerprint,
    point_normal_operands,
)
from scripts.certify_n12_current_dop853_endpoint_rates import (
    DEFAULT_CENTER, exact, frobenius_bound, matrix, owner, scalar_packet,
)

DEFAULT_OUTPUT = ROOT / "artifacts/current_runtime/current_stop_normal_restoration_pilot"


def read_balls(array):
    values = np.asarray(array)
    return np.asarray([arb(str(v)) for v in values.flat], dtype=object).reshape(values.shape)


def write_balls(array):
    values = np.asarray(array, dtype=object)
    return np.asarray([v.str(140) for v in values.flat]).reshape(values.shape)


def as_array(value):
    return np.asarray(value.entries(), dtype=object).reshape(value.nrows(), value.ncols())


def calculate(constraints: Path, points: Path, output: Path, radius_factor=2, spectral_jet=True):
    started = time.perf_counter()
    ctx.prec = 384
    output.mkdir(parents=True, exist_ok=True)
    constraint_report = json.loads((constraints / "report.json").read_text())
    point_report = json.loads((points / "report.json").read_text())
    center_sha = fingerprint(DEFAULT_CENTER)
    if not constraint_report["center_SHA256"] == point_report["center_SHA256"] == center_sha:
        raise ValueError("normal operands, selected line, and current center differ")
    with np.load(constraints / "arrays.npz") as data:
        state = read_balls(data["native_terminal_raw_state_balls"])
        weights = read_balls(data["state_weights_balls"])
        normal = read_balls(data["native_terminal_normal_action_balls"])
        point_constraints = read_balls(data["native_terminal_constraint_balls"])
        point_derivative = read_balls(data["native_terminal_DC_normal_balls"])
        graph_residual = read_balls(data["native_terminal_descriptor_graph_residual_ball"])[0]
    if (state.shape, weights.shape, normal.shape, point_derivative.shape) != ((98,), (98,), (98, 25), (25, 25)):
        raise ValueError("current raw98 C25 normal operand dimensions differ")
    if not all(w > 0 for w in weights):
        raise ValueError("positive current action weights required")
    A0, C0 = matrix(point_derivative), matrix(point_constraints)
    # The Arb inverse is only used to propose the exact fixed matrix B.
    # All final bounds multiply that fixed midpoint matrix outward.
    B = matrix(np.asarray([v.mid() for v in A0.inv().entries()], dtype=object).reshape(25, 25))
    BC = B * C0
    Y = frobenius_bound(BC)
    r = (exact(radius_factor) * Y).upper()
    if not r > 0:
        raise ValueError("a positive normal trial radius is required")
    normal_raw = np.asarray([[normal[i, j] / weights[i] for j in range(25)] for i in range(98)], dtype=object)
    row_norms = np.asarray([frobenius_bound(matrix(row)) for row in normal_raw], dtype=object)
    spread = np.asarray([(r * value).upper() for value in row_norms], dtype=object)
    # For every ||nu||_2<=r, Cauchy--Schwarz puts N_raw nu in these
    # row-norm boxes. The tiny imported point balls are retained as well.
    state_box = np.asarray([state[i] + arb(0, spread[i]) for i in range(98)], dtype=object)
    box_started = time.perf_counter()
    box_constraints, box_derivative, box_action = point_normal_operands(state_box, weights, normal)
    box_seconds = time.perf_counter() - box_started
    identity = matrix(np.eye(25, dtype=int))
    K = identity - B * matrix(box_derivative)
    q = frobenius_bound(K)
    image_radius = (Y + q * r).upper()
    slack = (r - image_radius).lower()
    closes = bool(q < 1 and slack > 0)
    center_defect = frobenius_bound(identity - B * A0)
    linear_nu = -A0.solve(C0, algorithm="precond")
    arrays = {
        "raw_native_terminal_point_balls": state,
        "state_weights_balls": weights,
        "normal_action_balls": normal,
        "normal_raw_balls": normal_raw,
        "normal_raw_row_norm_upper_balls": row_norms,
        "raw_coordinate_spread_upper_balls": spread,
        "raw_containing_box_balls": state_box,
        "point_constraints_balls": point_constraints,
        "point_DC_normal_balls": point_derivative,
        "fixed_midpoint_inverse_balls": as_array(B),
        "fixed_inverse_times_point_constraints_balls": as_array(BC).ravel(),
        "box_constraints_balls": box_constraints,
        "box_DC_normal_balls": box_derivative,
        "banach_derivative_defect_balls": as_array(K),
        "linearized_normal_coordinates_balls": as_array(linear_nu).ravel(),
        "selected_descriptor_graph_residual_ball": np.asarray([graph_residual]),
    }
    spectral = {"evaluated": False, "graph_zero_certified": False}
    if spectral_jet:
        jet_started = time.perf_counter()
        with np.load(points / "point_balls.npz") as data:
            psi = read_balls(data["native_terminal_eigenvector_balls"])
            endpoint_state = read_balls(data["native_terminal_raw_state_balls"])
        if not all((a - b).contains(0) for a, b in zip(state, endpoint_state)):
            raise ValueError("selected line and normal pilot use different terminal points")
        psi_raw = np.r_[np.full(37, arb(0), dtype=object), psi]
        _, maps = action_value_and_maps(state)
        lambda_normal = np.asarray(owner._contracted_action(
            state, [psi_raw[:, None], psi_raw[:, None], normal_raw], maps,
        ), dtype=object).reshape(25)
        linear_graph = graph_residual + (matrix(lambda_normal).transpose() * linear_nu)[0, 0]
        arrays["selected_eigenvector_point_balls"] = psi
        arrays["point_Dlambda_normal_balls"] = lambda_normal
        arrays["linearized_descriptor_correction_ball"] = np.asarray([linear_graph])
        spectral = {
            "evaluated": True,
            "elapsed_seconds": time.perf_counter() - jet_started,
            "scope": "Selected eigenvalue first derivative at the original terminal point only",
            "identity": "Dlambda[Nraw]=D3S[psi,psi,Nraw], with the saved enclosure of the true normalized selected eigenvector",
            "point_Dlambda_normal_norm_upper": scalar_packet(frobenius_bound(matrix(lambda_normal))),
            "original_selected_descriptor_residual": scalar_packet(graph_residual),
            "linearized_descriptor_correction": scalar_packet(linear_graph),
            "graph_zero_certified": False,
            "linearized_correction_is_actual_root_descriptor": False,
        }
    paths = [DEFAULT_CENTER, constraints / "report.json", constraints / "arrays.npz",
             points / "report.json", points / "point_balls.npz", Path(__file__),
             ROOT / "scripts/certify_n12_current_stop_constraint_endpoints.py",
             ROOT / "scripts/certify_n12_current_dop853_endpoint_rates.py", Path(owner.__file__)]
    report = {
        "status": "NATIVE_TERMINAL_FIXED_NORMAL_C25_ZERO_CERTIFIED" if closes else "NATIVE_TERMINAL_FIXED_NORMAL_C25_BANACH_BOUND_NOT_CLOSED",
        "center_SHA256": center_sha,
        "scope": "ONE_CURRENT_NATIVE_TERMINAL_FIXED_TANGENT_NORMAL_SLICE",
        "constraint_owner": "C25=(S_m[24], v.S_v-S), unchanged retained N12 96-point action",
        "unknown_domain": "Euclidean normal-coordinate ball ||nu||_2<=r; raw state Y=P+W^-1N nu; fixed exact imported normal columns",
        "proof": "T(nu)=nu-B C(Y(nu)); q=||I-B DC(Y)W^-1N||_F bounds its Euclidean Lipschitz constant on the complete containing raw box. Y+q*r<r and q<1 prove a unique C25 zero in this normal ball.",
        "precision_bits": ctx.prec,
        "normal_dimension": 25,
        "raw_dimension": 98,
        "trial_radius_factor": radius_factor,
        "Y_upper": scalar_packet(Y),
        "normal_trial_radius": scalar_packet(r),
        "q_upper": scalar_packet(q),
        "Banach_image_radius_upper": scalar_packet(image_radius),
        "strict_inclusion_slack_lower": scalar_packet(slack),
        "fixed_inverse_point_defect_upper": scalar_packet(center_defect),
        "normal_action_orthogonality_defect_upper": scalar_packet(frobenius_bound(matrix(normal).transpose() * matrix(normal) - identity)),
        "original_constraint_norm_upper": scalar_packet(frobenius_bound(C0)),
        "original_descriptor_graph_residual": scalar_packet(graph_residual),
        "box_action_ball": scalar_packet(box_action),
        "box_evaluation_seconds": box_seconds,
        "C25_normal_zero_certified": closes,
        "unique_only_in_this_normal_ball": closes,
        "nonlinear_root_value_computed": False,
        "continuous_history_certified": False,
        "fixed_descriptor_zero_certified": False,
        "birth_slice_selected": False,
        "descriptor_spectral_first_jet": spectral,
        "source_fingerprint_convention": "SHA256; .py/.md/.json line endings normalized to LF; binary files unchanged",
        "sources": {str(path.resolve()): fingerprint(path) for path in paths},
    }
    if closes:
        root_distance = (Y / (1 - q)).upper()
        action_correction = (frobenius_bound(matrix(normal)) * root_distance).upper()
        # N has almost-orthonormal columns. A sharper spectral norm bound
        # follows directly from the same exact imported Gram matrix.
        eta = frobenius_bound(matrix(normal).transpose() * matrix(normal) - identity)
        if eta < 1:
            action_correction = ((1 + eta).sqrt() * root_distance).upper()
        report["root_normal_distance_upper"] = scalar_packet(root_distance)
        report["root_action_correction_norm_upper"] = scalar_packet(action_correction)
        arrays["root_normal_distance_upper_ball"] = np.asarray([root_distance])
        arrays["root_action_correction_norm_upper_ball"] = np.asarray([action_correction])
    report["elapsed_seconds"] = time.perf_counter() - started
    np.savez_compressed(output / "arrays.npz", **{key: write_balls(value) for key, value in arrays.items()})
    report["arrays_SHA256"] = fingerprint(output / "arrays.npz")
    (output / "report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({key: report[key] for key in ("status", "Y_upper", "normal_trial_radius", "q_upper", "strict_inclusion_slack_lower", "elapsed_seconds")}), flush=True)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--constraints", type=Path, default=DEFAULT_CONSTRAINTS)
    parser.add_argument("--points", type=Path, default=DEFAULT_POINTS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--radius-factor", type=int, default=2)
    parser.add_argument("--skip-spectral-jet", action="store_true")
    args = parser.parse_args()
    if args.radius_factor <= 1:
        parser.error("radius-factor must exceed one")
    calculate(args.constraints, args.points, args.output, args.radius_factor, not args.skip_spectral_jet)
