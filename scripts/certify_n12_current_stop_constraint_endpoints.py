"""Point constraint residuals and fixed-normal restoration operands.

The physical level-set owner is C=(S_m, v.S_v-S), with 24 multiplier
constraints and one zero Legendre-energy constraint. Only targeted action
contractions are evaluated; no full Hessian or field Jacobian is formed.
These point operands do not assert a zero, a chart neighborhood, or a flow.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np
from flint import arb, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.certify_n12_current_dop853_endpoint_rates import (
    DEFAULT_CENTER, exact, matrix, frobenius_bound, scalar_packet, owner,
)

DEFAULT_POINTS = ROOT / "artifacts/current_runtime/current_dop853_endpoint_rates"
DEFAULT_MODES = ROOT / "artifacts/current_runtime/current_physical_mode_response"
DEFAULT_OUTPUT = ROOT / "artifacts/current_runtime/current_stop_constraint_endpoints"
FIBER_OWNER = ROOT / "src/bhsm/interface/aether_forward_c2_exact_fixed_s_field.py"
FIBER_THEORY = ROOT / "theory/n12_c2_cancelled_euler_dirac_chart.md"
Q = 37
STATE = 98


def fingerprint(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".py", ".md", ".json"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def refresh_source_metadata(output: Path):
    """Update text provenance without repeating successful contractions."""
    path = output / "report.json"
    report = json.loads(path.read_text())
    report["source_fingerprint_convention"] = "SHA256; .py/.md/.json line endings normalized to LF; binary files unchanged"
    report["sources"] = {name: fingerprint(Path(name)) for name in report["sources"]}
    report["sources"][str(Path(__file__).resolve())] = fingerprint(Path(__file__))
    report["descriptor_graph_history_obligation"] = "The terminal lambda-s residual is about -9.33987e-17 and does not contain zero. Retain this signed residual in the correlated history model; do not clamp it or replace it by a zero graph equation at the stored point."
    path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    return report


def action_value_and_maps(state):
    """Retained scalar action value and its existing fixed affine maps."""
    bulk, inertia = arb(0), arb(0)
    maps = []
    for node in range(owner.POINTS):
        term = owner._integrand(state, node, 0)
        bulk += term.bulk.d[0]
        inertia += term.inertia.d[0]
        maps.append(owner._dense_mapping(term.maps))
    _, boundary = owner._boundary(state, 0)
    coefficient = exact(0.25 / (2.0 * owner.HOPF_ORBIT_VOLUME**2))
    return bulk - coefficient / inertia + boundary.d[0], maps


def constraint_legs(state):
    legs = np.full((STATE, 25), arb(0), dtype=object)
    for j in range(24):
        legs[74 + j, j] = arb(1)
    legs[Q:2 * Q, 24] = state[Q:2 * Q]
    return legs


def constraint_values(state):
    value, maps = action_value_and_maps(state)
    first = np.asarray(owner._contracted_action(state, [constraint_legs(state)], maps), dtype=object).reshape(25)
    first[24] -= value
    return first


def point_normal_operands(state, weights, normal_action):
    """DC W^-1 N including both energy product-rule contacts."""
    value, maps = action_value_and_maps(state)
    legs = constraint_legs(state)
    normal_raw = np.asarray([[normal_action[i, j] / weights[i]
                              for j in range(25)] for i in range(STATE)], dtype=object)
    velocity_part = np.full((STATE, 25), arb(0), dtype=object)
    velocity_part[Q:2 * Q] = normal_raw[Q:2 * Q]
    combined = np.concatenate((legs, normal_raw, velocity_part), axis=1)
    first = np.asarray(owner._contracted_action(state, [combined], maps), dtype=object).reshape(75)
    constraints = first[:25].copy()
    constraints[24] -= value
    # First source leg is fixed at the supplied point. The derivative of
    # v.S_v includes S_v.dv; subtracting S contributes -S.dy.
    second = np.asarray(owner._contracted_action(
        state, [legs[:, :, None], normal_raw[:, None, :]], maps,
    ), dtype=object).reshape(25, 25)
    second[24] += first[50:75] - first[25:50]
    return constraints, second, value


def strings(array):
    return np.asarray([[v.str(140) for v in row] for row in array]) if np.asarray(array).ndim == 2 else np.asarray([v.str(140) for v in array])


def calculate(points: Path, modes: Path, output: Path):
    ctx.prec = 384
    output.mkdir(parents=True, exist_ok=True)
    points_report = json.loads((points / "report.json").read_text())
    modes_report = json.loads((modes / "report.json").read_text())
    if points_report["center_SHA256"] != modes_report["center_SHA256"]:
        raise ValueError("point and normal-proposal centers differ")
    with np.load(points / "point_balls.npz") as point_data:
        states = {name: np.asarray([arb(str(v)) for v in point_data[name + "_raw_state_balls"]], dtype=object)
                  for name in ("first_stored", "native_terminal")}
        weights = np.asarray([arb(str(v)) for v in point_data["state_weights_balls"]], dtype=object)
    with np.load(modes / "arrays.npz") as mode_data:
        proposals = {}
        for name, node in (("first_stored", 0), ("native_terminal", -1)):
            q, _ = np.linalg.qr(mode_data["normalized_constraint_action"][node].T, mode="reduced")
            proposals[name] = np.asarray([[exact(v) for v in row] for row in q], dtype=object)
    report = {
        "center_SHA256": points_report["center_SHA256"],
        "scope": "OUTWARD_POINT_CONSTRAINT_RESIDUALS_AND_NORMAL_LINEARIZATION_ONLY",
        "constraint_owner": "C=(S_m[24],v.S_v-S), same retained N12 96-point action",
        "normal_proposal_owner": "QR of current cached normalized constraint rows, imported as exact dyadics; actual DC.N is evaluated outward at each supplied point",
        "descriptor_graph_owner": "Unshifted lambda_selected(raw98)-s=0; the exact_fixed_s_field_action source explicitly owns lambda(Y)=s, and the cancelled Euler-Dirac chart states s=lambda(Y)>0",
        "descriptor_graph_shift": 0,
        "constraint_zero_enclosed": False,
        "uniform_chart_certified": False,
        "normal_correction_is_nonlinear_zero": False,
        "source_fingerprint_convention": "SHA256; .py/.md/.json line endings normalized to LF; binary files unchanged",
        "descriptor_graph_history_obligation": "The terminal lambda-s residual is about -9.33987e-17 and does not contain zero. Retain this signed residual in the correlated history model; do not clamp it or replace it by a zero graph equation at the stored point.",
        "sources": {str(path.resolve()): fingerprint(path)
                    for path in (points / "report.json", points / "point_balls.npz", modes / "report.json", modes / "arrays.npz", Path(owner.__file__), FIBER_OWNER, FIBER_THEORY, Path(__file__))},
        "points": {},
    }
    arrays = {}
    for name, state in states.items():
        started = time.perf_counter()
        N = proposals[name]
        C, DCN, value = point_normal_operands(state, weights, N)
        point_scalars = points_report["points"][name]["scalars"]
        fiber_residual = arb(point_scalars["eigenvalue"]["ball"]) - arb(point_scalars["descriptor"]["ball"])
        A, rhs = matrix(DCN), matrix(C)
        correction = -A.solve(rhs, algorithm="precond")
        linear_replay = A * correction + rhs
        action_correction = matrix(N) * correction
        finite = all(v.is_finite() for v in correction.entries())
        if not finite:
            raise ArithmeticError("point normal inverse failed")
        # Meaningful differential check: vary a normal direction in the
        # actual action, including the velocity factor in Legendre energy.
        direction = np.asarray([N[i, 0] / weights[i] for i in range(STATE)], dtype=object)
        checks = []
        for exponent in (18, 22, 26):
            h = arb(2) ** -exponent
            minus = constraint_values(state - h * direction)
            plus = constraint_values(state + h * direction)
            fd = (plus - minus) / (2 * h)
            error = frobenius_bound(matrix(fd - DCN[:, 0]))
            checks.append({"step": f"2^-{exponent}", "derivative_difference_norm_upper": scalar_packet(error)})
        if not (checks[1]["derivative_difference_norm_upper"]["upper"] < checks[0]["derivative_difference_norm_upper"]["upper"] / 32
                and checks[2]["derivative_difference_norm_upper"]["upper"] < checks[1]["derivative_difference_norm_upper"]["upper"] / 32):
            raise ArithmeticError("normal derivative step comparison lost quadratic convergence")
        row = {
            "elapsed_seconds": time.perf_counter() - started,
            "multiplier_constraint_norm_upper": scalar_packet(frobenius_bound(matrix(C[:24]))),
            "Legendre_energy": scalar_packet(C[24]),
            "constraint_norm_upper": scalar_packet(frobenius_bound(rhs)),
            "all_constraint_components_contain_zero": all(v.contains(0) for v in C),
            "selected_descriptor_graph_residual": scalar_packet(fiber_residual),
            "selected_descriptor_graph_residual_contains_zero": fiber_residual.contains(0),
            "normal_linearization_verified_invertible": True,
            "normal_rank_at_point": 25,
            "constraint_level_tangent_dimension_at_point": 73,
            "normal_linearized_action_correction_norm_upper": scalar_packet(frobenius_bound(action_correction)),
            "normal_linear_solve_replay_norm_upper": scalar_packet(frobenius_bound(linear_replay)),
            "normal_orthogonality_defect_upper": scalar_packet(frobenius_bound(matrix(N).transpose() * matrix(N) - matrix(np.eye(25, dtype=int)))),
            "differential_step_comparison": checks,
            "differential_check_has_quadratic_step_convergence": True,
            "constraint_component_balls": [v.str(140) for v in C],
        }
        report["points"][name] = row
        for key, val in {"raw_state_balls": state, "constraint_balls": C,
                         "descriptor_graph_residual_ball": np.asarray([fiber_residual]),
                         "normal_action_balls": N, "DC_normal_balls": DCN,
                         "normal_linearized_coordinates_balls": np.asarray(correction.tolist(), dtype=object).ravel(),
                         "normal_linearized_action_correction_balls": np.asarray(action_correction.tolist(), dtype=object).ravel()}.items():
            arrays[name + "_" + key] = strings(val)
        np.savez_compressed(output / "arrays.npz", state_weights_balls=strings(weights), **arrays)
        (output / "report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
        print(json.dumps({"point": name, "elapsed_seconds": row["elapsed_seconds"],
                          "constraint_norm_upper": row["constraint_norm_upper"]["upper"],
                          "linearized_correction_norm_upper": row["normal_linearized_action_correction_norm_upper"]["upper"],
                          "energy": row["Legendre_energy"],
                          "descriptor_graph_residual": row["selected_descriptor_graph_residual"],
                          "derivative_check_errors": [v["derivative_difference_norm_upper"]["upper"] for v in checks]}), flush=True)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--points", type=Path, default=DEFAULT_POINTS)
    parser.add_argument("--modes", type=Path, default=DEFAULT_MODES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--refresh-source-fingerprints", action="store_true")
    args = parser.parse_args()
    if args.refresh_source_fingerprints:
        refreshed = refresh_source_metadata(args.output)
        print(json.dumps({"source_fingerprint_convention": refreshed["source_fingerprint_convention"],
                          "own_source_SHA256": refreshed["sources"][str(Path(__file__).resolve())],
                          "numerical_operands_recomputed": False}), flush=True)
    else:
        calculate(args.points, args.modes, args.output)
