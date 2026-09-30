"""Parameter-uniform fixed-normal C25 restoration on one native curve cell.

This deliberately tests the coordinate-box enclosure owner.  The trajectory
is the unchanged degree-seven native polynomial with one shared theta.  A
fixed normal N and complementary T provide Y(theta,xi,nu)=P(theta)+
W^-1(T xi+N nu).  The trial radius includes the whole cell's outward
constraint enclosure, rather than substituting its initial point residual.
No continuation across cells or physical flow assertion is made.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
from flint import arb, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.current_native_curve import load_native_cell, bernstein_range
from bhsm.interface.shared_action_taylor import TaylorDomain, scalar_taylor_action
from bhsm.interface.shared_action_gradient import gradient
from scripts.certify_n12_current_stop_constraint_endpoints import (
    DEFAULT_OUTPUT as DEFAULT_CONSTRAINTS, action_value_and_maps, constraint_values, fingerprint,
    point_normal_operands,
)
from scripts.certify_n12_current_dop853_endpoint_rates import (
    DEFAULT_CENTER, exact, frobenius_bound, matrix, owner,
)
from scripts.certify_n12_current_stop_normal_restoration_pilot import (
    as_array, read_balls, write_balls,
)

DEFAULT_OUTPUT = ROOT / "artifacts/current_runtime/current_first_cell_normal_restoration"


def ball(value):
    value = Fraction(value)
    return arb(value.numerator) / arb(value.denominator)


def containing_range(bounds):
    lo, hi = bounds
    return ball((lo + hi) / 2) + arb(0, ball((hi - lo) / 2).upper())


def packet(value):
    """Keep a finite Arb result even when its display float would overflow."""
    if not value.is_finite():
        return {"ball": value.str(140), "lower": None, "upper": None}
    lo, hi = float(value.lower()), float(value.upper())
    return {"ball": value.str(140),
            "lower": math.nextafter(lo, -math.inf) if math.isfinite(lo) else None,
            "upper": math.nextafter(hi, math.inf) if math.isfinite(hi) else None}


def calculate_coordinate_box(output, constraints=DEFAULT_CONSTRAINTS, fraction_right=Fraction(1, 4), tangent_radius=Fraction(0)):
    started = time.perf_counter()
    ctx.prec = 384
    output.mkdir(parents=True, exist_ok=True)
    cell = load_native_cell(DEFAULT_CENTER, 0, Fraction(0), fraction_right)
    inherited = json.loads((constraints / "report.json").read_text())
    if cell.source_sha256 != inherited["center_SHA256"]:
        raise ValueError("current native curve and normal proposal source differ")
    if tangent_radius < 0:
        raise ValueError("nonnegative explicitly supplied tangent radius required")
    with np.load(constraints / "arrays.npz") as data:
        normal = read_balls(data["first_stored_normal_action_balls"])
        A0 = matrix(read_balls(data["first_stored_DC_normal_balls"]))
        initial_C = read_balls(data["first_stored_constraint_balls"])
    weights = np.asarray([ball(value) for value in cell.state_weights], dtype=object)
    if not all(value > 0 for value in weights):
        raise ValueError("positive retained action weights required")
    B = matrix(np.asarray([v.mid() for v in A0.inv().entries()], dtype=object).reshape(25, 25))
    # This QR is a proposal for a common affine complement, imported exactly.
    # The complete frame's Gram enclosure below verifies its nonsingularity;
    # it is not called the actual nonlinear constraint tangent.
    normal_mid = np.asarray([[float(v.mid()) for v in row] for row in normal])
    complement = np.linalg.qr(normal_mid, mode="complete")[0][:, 25:]
    tangent = np.asarray([[exact(v) for v in row] for row in complement], dtype=object)
    frame = np.concatenate((normal, tangent), axis=1)
    identity98 = matrix(np.eye(98, dtype=int))
    frame_eta = frobenius_bound(matrix(frame).transpose() * matrix(frame) - identity98)
    if not frame_eta < 1:
        raise ArithmeticError("common affine normal/complement frame is not verified invertible")
    normal_raw = np.asarray([[normal[i, j] / weights[i] for j in range(25)] for i in range(98)], dtype=object)
    tangent_raw = np.asarray([[tangent[i, j] / weights[i] for j in range(73)] for i in range(98)], dtype=object)
    raw_bounds = [(lo / cell.state_weights[j], hi / cell.state_weights[j])
                  for j, (lo, hi) in enumerate(cell.jet_bounds(0)[:98])]
    curve_box = np.asarray([containing_range(bounds) for bounds in raw_bounds], dtype=object)
    rho = ball(tangent_radius)
    tangent_spread = np.asarray([(rho * frobenius_bound(matrix(row))).upper() for row in tangent_raw], dtype=object)
    parameter_box = np.asarray([curve_box[i] + arb(0, tangent_spread[i]) for i in range(98)], dtype=object)
    residual_started = time.perf_counter()
    C_parameter = constraint_values(parameter_box)
    residual_seconds = time.perf_counter() - residual_started
    BC = B * matrix(C_parameter)
    Y = frobenius_bound(BC)
    r = (2 * Y).upper()
    if not Y.is_finite() or not r > 0:
        raise ArithmeticError("finite positive cell constraint radius required")
    normal_rows = np.asarray([frobenius_bound(matrix(row)) for row in normal_raw], dtype=object)
    normal_spread = np.asarray([(r * value).upper() for value in normal_rows], dtype=object)
    full_box = np.asarray([parameter_box[i] + arb(0, normal_spread[i]) for i in range(98)], dtype=object)
    arrays = {
        "state_weights_balls": weights,
        "normal_action_balls": normal,
        "tangent_complement_action_balls": tangent,
        "normal_raw_balls": normal_raw,
        "tangent_complement_raw_balls": tangent_raw,
        "raw_native_curve_box_balls": curve_box,
        "raw_parameter_box_balls": parameter_box,
        "raw_normal_enlarged_box_balls": full_box,
        "normal_row_norm_upper_balls": normal_rows,
        "normal_spread_upper_balls": normal_spread,
        "tangent_spread_upper_balls": tangent_spread,
        "fixed_midpoint_inverse_balls": as_array(B),
        "inherited_initial_DC_normal_balls": as_array(A0),
        "inherited_initial_constraint_balls": initial_C,
        "parameter_constraint_balls": C_parameter,
        "fixed_inverse_parameter_constraints_balls": as_array(BC).ravel(),
        "normal_radius_ball": np.asarray([r]),
        "Y_upper_ball": np.asarray([Y]),
    }
    # Save the actual curve and radius operands before the larger derivative
    # evaluation. Exact rational coefficients retain the common theta.
    rational_arrays = {f"native_arc_jet{order}_theta_coefficients_rational":
                       np.asarray([[str(value) for value in row] for row in cell.jet_coefficients(order)])
                       for order in (0, 1, 2)}
    rational_arrays["raw_native_curve_bounds_rational"] = np.asarray([[str(lo), str(hi)] for lo, hi in raw_bounds])
    paths = [DEFAULT_CENTER, constraints / "report.json", constraints / "arrays.npz", Path(__file__),
             ROOT / "src/bhsm/interface/current_native_curve.py",
             ROOT / "scripts/certify_n12_current_stop_normal_restoration_pilot.py",
             ROOT / "scripts/certify_n12_current_stop_constraint_endpoints.py", Path(owner.__file__)]
    report = {
        "status": "FIRST_NATIVE_CELL_C25_RESIDUAL_AND_NORMAL_RADIUS_OPERANDS_SAVED",
        "center_SHA256": cell.source_sha256,
        "scope": "ONE_PARAMETER_UNIFORM_C25_FIXED_NORMAL_NATIVE_CURVE_CELL_COORDINATE_BOX_PILOT",
        "interval": 0,
        "fraction_left": "0",
        "fraction_right": str(fraction_right),
        "arc_midpoint_rational": str(cell.arc_midpoint),
        "arc_radius_rational": str(cell.arc_radius),
        "common_theta": "theta in [-1,1] shared by all99 native coordinate polynomial rows; exact polynomial is preserved",
        "constraint_owner": "C25=(S_m[24],v.S_v-S), unchanged retained N12 96-point action",
        "common_chart": "Y(theta,xi,nu)=P_raw(theta)+T_raw xi+N_raw nu; fixed normal/complement frame verified invertible",
        "tangent_complement_is_nonlinear_physical_tangent": False,
        "tangent_radius_rational": str(tangent_radius),
        "tangent_parameter_dimension": 73,
        "normal_dimension": 25,
        "normal_trial_radius_owner": "r=2*sup_{theta,||xi||<=rho}||B C(P_raw(theta)+T_raw xi)||_2, using outward containing boxes",
        "Y_upper": packet(Y),
        "normal_trial_radius": packet(r),
        "parameter_constraint_norm_upper": packet(frobenius_bound(matrix(C_parameter))),
        "common_frame_Gram_defect_upper": packet(frame_eta),
        "fixed_inverse_initial_defect_upper": packet(frobenius_bound(matrix(np.eye(25, dtype=int)) - B * A0)),
        "parameter_constraint_evaluation_seconds": residual_seconds,
        "C25_parameter_uniform_normal_zero_certified": False,
        "physical_defect_chart_certified": False,
        "continuous_history_certified": False,
        "descriptor_graph_zero_certified": False,
        "source_fingerprint_convention": "SHA256; .py/.md/.json line endings normalized to LF; binary files unchanged",
        "sources": {str(path.resolve()): fingerprint(path) for path in paths},
    }

    def save():
        np.savez_compressed(output / "arrays.npz", **rational_arrays,
                            **{key: write_balls(value) for key, value in arrays.items()})
        report["arrays_SHA256"] = fingerprint(output / "arrays.npz")
        (output / "report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")

    save()
    print(json.dumps({"stage": "cell_residual_saved", "fraction_right": str(fraction_right), "Y_upper": packet(Y), "trial_radius": packet(r)}), flush=True)
    derivative_started = time.perf_counter()
    try:
        C_box, A_box, S_box = point_normal_operands(full_box, weights, normal)
    except ArithmeticError as error:
        report.update({
            "status": "FIRST_NATIVE_CELL_C25_COORDINATE_BOX_ARITHMETIC_ENCLOSURE_NOT_CLOSED",
            "normal_derivative_evaluation_seconds": time.perf_counter() - derivative_started,
            "normal_derivative_enclosure_error": str(error),
            "q_upper": None,
            "Banach_image_radius_upper": None,
            "strict_inclusion_slack_lower": None,
            "C25_parameter_uniform_normal_zero_certified": False,
            "unique_only_per_fixed_theta_and_tangent_parameter": False,
            "physical_domain_sign_or_birth_cone_certified": False,
            "owner_result": "The coordinate-box constraint residual inflated the normal radius until the existing action reciprocal enclosure failed. This is an enclosure-width outcome, not nonexistence of the physical constraint chart.",
            "elapsed_seconds": time.perf_counter() - started,
        })
        save()
        print(json.dumps({key: report[key] for key in ("status", "fraction_right", "Y_upper", "normal_trial_radius", "normal_derivative_enclosure_error", "elapsed_seconds")}), flush=True)
        return report
    derivative_seconds = time.perf_counter() - derivative_started
    K = matrix(np.eye(25, dtype=int)) - B * matrix(A_box)
    q = frobenius_bound(K)
    image = (Y + q * r).upper()
    slack = (r - image).lower()
    closes = bool(q.is_finite() and q < 1 and slack > 0)
    arrays.update({"normal_enlarged_constraints_balls": C_box,
                   "normal_enlarged_DC_normal_balls": A_box,
                   "Banach_derivative_defect_balls": as_array(K),
                   "q_upper_ball": np.asarray([q]),
                   "inclusion_slack_lower_ball": np.asarray([slack])})
    report.update({
        "status": "FIRST_NATIVE_CELL_PARAMETER_UNIFORM_C25_NORMAL_ZERO_CERTIFIED" if closes else "FIRST_NATIVE_CELL_C25_COORDINATE_BOX_BANACH_BOUND_NOT_CLOSED",
        "q_upper": packet(q),
        "Banach_image_radius_upper": packet(image),
        "strict_inclusion_slack_lower": packet(slack),
        "normal_enlarged_action_ball": packet(S_box),
        "normal_derivative_evaluation_seconds": derivative_seconds,
        "C25_parameter_uniform_normal_zero_certified": closes,
        "physical_defect_chart_certified": False,
        "unique_only_per_fixed_theta_and_tangent_parameter": closes,
        "physical_domain_sign_or_birth_cone_certified": False,
        "owner_result": "The fixed-normal Banach ball closes on this explicit parameter cell." if closes else "The coordinate-box enclosure does not establish this cell's normal graph. This is an enclosure-width outcome, not nonexistence of the physical constraint chart.",
        "elapsed_seconds": time.perf_counter() - started,
    })
    if closes:
        report["uniform_root_normal_distance_upper"] = packet((Y / (1-q)).upper())
    save()
    print(json.dumps({key: report[key] for key in ("status", "fraction_right", "Y_upper", "normal_trial_radius", "q_upper", "strict_inclusion_slack_lower", "elapsed_seconds")}), flush=True)
    return report


def calculate_shared_taylor(output, constraints=DEFAULT_CONSTRAINTS, fraction_right=Fraction(1, 4), tangent_radius=Fraction(0)):
    """Keep the common theta through C25 before applying the fixed inverse."""
    started = time.perf_counter()
    ctx.prec = 384
    output.mkdir(parents=True, exist_ok=True)
    cell = load_native_cell(DEFAULT_CENTER, 0, Fraction(0), fraction_right)
    inherited = json.loads((constraints / "report.json").read_text())
    if cell.source_sha256 != inherited["center_SHA256"]:
        raise ValueError("current shared curve and normal proposal source differ")
    if tangent_radius < 0:
        raise ValueError("nonnegative tangent radius required")
    with np.load(constraints / "arrays.npz") as data:
        normal = read_balls(data["first_stored_normal_action_balls"])
        A0 = matrix(read_balls(data["first_stored_DC_normal_balls"]))
    weights = np.asarray([ball(value) for value in cell.state_weights], dtype=object)
    B = matrix(np.asarray([v.mid() for v in A0.inv().entries()], dtype=object).reshape(25, 25))
    normal_mid = np.asarray([[float(v.mid()) for v in row] for row in normal])
    complement = np.linalg.qr(normal_mid, mode="complete")[0][:, 25:]
    tangent = np.asarray([[exact(v) for v in row] for row in complement], dtype=object)
    frame = np.concatenate((normal, tangent), axis=1)
    frame_eta = frobenius_bound(matrix(frame).transpose() * matrix(frame) - matrix(np.eye(98, dtype=int)))
    if not frame_eta < 1:
        raise ArithmeticError("common normal/complement frame is not verified invertible")
    normal_raw = np.asarray([[normal[i, j] / weights[i] for j in range(25)] for i in range(98)], dtype=object)
    tangent_raw = np.asarray([[tangent[i, j] / weights[i] for j in range(73)] for i in range(98)], dtype=object)
    has_tangent = tangent_radius > 0
    domain = TaylorDomain([(0, 1, 'interval'), (1, 74, 'euclidean')] if has_tangent else [(0, 1, 'interval')], 74 if has_tangent else 1)
    powers = cell.jet_coefficients(0)
    state_models, tails = [], []
    for j in range(98):
        coefficients = tuple(value / cell.state_weights[j] for value in powers[:, j])
        tail = (Fraction(0), Fraction(0), *coefficients[2:])
        lo, hi = bernstein_range(tail)
        tail_bound = ball(max(abs(lo), abs(hi))).upper()
        linear = [ball(coefficients[1])]
        if has_tangent:
            linear.extend(ball(tangent_radius) * tangent_raw[j, k] for k in range(73))
        state_models.append(domain.affine(ball(coefficients[0]), linear, tail_bound))
        tails.append(tail_bound)
    model_started = time.perf_counter()
    raw_gradient = gradient(owner, state_models, [])
    with scalar_taylor_action(owner):
        action_value, _ = action_value_and_maps(state_models)
    energy = sum((state_models[37+i] * raw_gradient[37+i] for i in range(37)), domain.affine(0)) - action_value
    C_models = [*raw_gradient[74:98], energy]
    BC_models = [sum((C_models[j] * B[i, j] for j in range(25)), domain.affine(0)) for i in range(25)]
    model_seconds = time.perf_counter() - model_started
    C_enclosures = np.asarray([value.enclosure() for value in C_models], dtype=object)
    BC_supports = np.asarray([value.support() for value in BC_models], dtype=object)
    Y = frobenius_bound(matrix(BC_supports))
    r = (2 * Y).upper()
    parameter_box = np.asarray([value.enclosure() for value in state_models], dtype=object)
    normal_rows = np.asarray([frobenius_bound(matrix(row)) for row in normal_raw], dtype=object)
    normal_spread = np.asarray([(r * value).upper() for value in normal_rows], dtype=object)
    full_box = np.asarray([parameter_box[i] + arb(0, normal_spread[i]) for i in range(98)], dtype=object)
    arrays = {
        "state_weights_balls": weights,
        "normal_action_balls": normal,
        "tangent_complement_action_balls": tangent,
        "normal_raw_balls": normal_raw,
        "tangent_complement_raw_balls": tangent_raw,
        "fixed_midpoint_inverse_balls": as_array(B),
        "raw_parameter_box_balls": parameter_box,
        "raw_normal_enlarged_box_balls": full_box,
        "native_high_degree_tail_bounds_balls": np.asarray(tails),
        "normal_spread_upper_balls": normal_spread,
        "constraint_enclosure_balls": C_enclosures,
        "fixed_inverse_constraint_support_upper_balls": BC_supports,
        "normal_radius_ball": np.asarray([r]),
    }
    for prefix, models in (("state", state_models), ("raw_gradient", raw_gradient), ("constraint", C_models), ("fixed_inverse_constraint", BC_models)):
        arrays[prefix + "_Taylor_constant_balls"] = np.asarray([value.c for value in models], dtype=object)
        arrays[prefix + "_Taylor_linear_balls"] = np.asarray([value.a.entries() for value in models], dtype=object)
        arrays[prefix + "_Taylor_remainder_upper_balls"] = np.asarray([value.r for value in models], dtype=object)
    paths = [DEFAULT_CENTER, constraints / "report.json", constraints / "arrays.npz", Path(__file__),
             ROOT / "src/bhsm/interface/current_native_curve.py",
             ROOT / "src/bhsm/interface/shared_action_taylor.py",
             ROOT / "src/bhsm/interface/shared_action_gradient.py",
             ROOT / "src/bhsm/interface/factored_arb_integrand.py",
             ROOT / "scripts/certify_n12_current_stop_constraint_endpoints.py", Path(owner.__file__)]
    report = {
        "status": "FIRST_NATIVE_CELL_SHARED_THETA_C25_NORMAL_RADIUS_OPERANDS_SAVED",
        "center_SHA256": cell.source_sha256,
        "scope": "ONE_NATIVE_CELL_C25_COMMON_THETA_VALUE_MODEL_AND_NORMAL_BOX_DERIVATIVE_PILOT",
        "method": "COMMON_THETA_FIRST_ORDER_TAYLOR_WITH_EXACT_NATIVE_HIGH_DEGREE_BERNSTEIN_TAIL",
        "interval": 0,
        "fraction_left": "0",
        "fraction_right": str(fraction_right),
        "arc_midpoint_rational": str(cell.arc_midpoint),
        "arc_radius_rational": str(cell.arc_radius),
        "tangent_radius_rational": str(tangent_radius),
        "shared_parameter_dimension": domain.dimension,
        "normal_trial_radius_owner": "r=2*||support(B*C_Taylor)||_2; B acts on signed common constant/linear coefficients before support norms",
        "constraint_owner": "C25=(S_m[24],v.S_v-S), unchanged retained N12 96-point action",
        "shared_C25_model_seconds": model_seconds,
        "Y_upper": packet(Y),
        "normal_trial_radius": packet(r),
        "constraint_constant_norm_upper": packet(frobenius_bound(matrix(arrays['constraint_Taylor_constant_balls']))),
        "constraint_linear_norm_upper": packet(frobenius_bound(matrix(arrays['constraint_Taylor_linear_balls']))),
        "constraint_remainder_norm_upper": packet(frobenius_bound(matrix(arrays['constraint_Taylor_remainder_upper_balls']))),
        "common_frame_Gram_defect_upper": packet(frame_eta),
        "C25_parameter_uniform_normal_zero_certified": False,
        "physical_defect_chart_certified": False,
        "continuous_history_certified": False,
        "descriptor_graph_zero_certified": False,
        "source_fingerprint_convention": "SHA256; .py/.md/.json line endings normalized to LF; binary files unchanged",
        "sources": {str(path.resolve()): fingerprint(path) for path in paths},
    }

    def save():
        np.savez_compressed(output / "arrays.npz", **{key: write_balls(value) for key, value in arrays.items()})
        report['arrays_SHA256'] = fingerprint(output / "arrays.npz")
        (output / "report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")

    save()
    print(json.dumps({"stage": "shared_C25_radius_saved", "fraction_right": str(fraction_right), "Y_upper": packet(Y), "trial_radius": packet(r)}), flush=True)
    derivative_started = time.perf_counter()
    try:
        C_box, A_box, S_box = point_normal_operands(full_box, weights, normal)
    except ArithmeticError as error:
        report.update(status="FIRST_NATIVE_CELL_SHARED_THETA_NORMAL_DERIVATIVE_BOX_NOT_CLOSED",
                      normal_derivative_enclosure_error=str(error),
                      normal_derivative_evaluation_seconds=time.perf_counter()-derivative_started,
                      q_upper=None, elapsed_seconds=time.perf_counter()-started)
        save()
        print(json.dumps({"status": report['status'], "Y_upper": packet(Y), "normal_derivative_enclosure_error": str(error), "elapsed_seconds": report['elapsed_seconds']}), flush=True)
        return report
    K = matrix(np.eye(25, dtype=int)) - B * matrix(A_box)
    q = frobenius_bound(K)
    image = (Y + q * r).upper()
    slack = (r - image).lower()
    closes = bool(q.is_finite() and q < 1 and slack > 0)
    arrays.update(normal_enlarged_DC_normal_balls=A_box, Banach_derivative_defect_balls=as_array(K),
                  q_upper_ball=np.asarray([q]), inclusion_slack_lower_ball=np.asarray([slack]))
    report.update(status="FIRST_NATIVE_CELL_SHARED_THETA_PARAMETER_UNIFORM_C25_NORMAL_ZERO_CERTIFIED" if closes else "FIRST_NATIVE_CELL_SHARED_THETA_C25_NORMAL_BOX_BANACH_BOUND_NOT_CLOSED",
                  q_upper=packet(q), strict_inclusion_slack_lower=packet(slack),
                  Banach_image_radius_upper=packet(image), normal_enlarged_action_ball=packet(S_box),
                  normal_derivative_evaluation_seconds=time.perf_counter()-derivative_started,
                  C25_parameter_uniform_normal_zero_certified=closes,
                  unique_only_per_fixed_theta_and_tangent_parameter=closes,
                  elapsed_seconds=time.perf_counter()-started)
    if closes:
        report['uniform_root_normal_distance_upper'] = packet((Y/(1-q)).upper())
    save()
    print(json.dumps({key: report[key] for key in ('status', 'fraction_right', 'Y_upper', 'normal_trial_radius', 'q_upper', 'strict_inclusion_slack_lower', 'elapsed_seconds')}), flush=True)
    return report


def calculate(output, fraction_right=Fraction(1, 4), tangent_radius=Fraction(0), method='both'):
    methods = {}
    if method in ('coordinate-box', 'both'):
        methods['coordinate_box'] = calculate_coordinate_box(output, fraction_right=fraction_right, tangent_radius=tangent_radius)
    if method in ('shared-taylor', 'both'):
        methods['shared_theta_taylor'] = calculate_shared_taylor(output / 'shared_taylor', fraction_right=fraction_right, tangent_radius=tangent_radius)
    summary = {'center_SHA256': fingerprint(DEFAULT_CENTER), 'methods': methods,
               'physical_defect_chart_certified': False, 'continuous_history_certified': False}
    (output / 'methods_report.json').write_text(json.dumps(summary, indent=2, allow_nan=False) + '\n')
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--fraction-right", type=Fraction, default=Fraction(1, 4))
    parser.add_argument("--tangent-radius", type=Fraction, default=Fraction(0))
    parser.add_argument("--method", choices=('coordinate-box', 'shared-taylor', 'both'), default='both')
    args = parser.parse_args()
    if not 0 < args.fraction_right <= 1:
        parser.error("fraction-right must belong to (0,1]")
    calculate(args.output, fraction_right=args.fraction_right, tangent_radius=args.tangent_radius, method=args.method)
