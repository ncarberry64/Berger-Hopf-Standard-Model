"""Bind certified core inclusion and exact scalar center replay to current DOP853.

This supplies inputs to the existence-only canonical-stop witness.  The exact
1222 member, rather than the floating proof center, is the physical initial
condition.  The scalar polynomial replay does not prove a retained-action
orbit remains near that center.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
from flint import arb, ctx, fmpq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"scripts"))
from audit_n12_c2_stop_dense_descriptor_first_hit import (
    _bernstein, _compose_interval, _dense_power, _derivative, _evaluate,
)

BASE = ROOT/"artifacts/flagship_integration"
DEFAULT_CENTER = BASE/"BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
DEFAULT_OUT = ROOT/"artifacts/current_runtime/current_stop_scalar_inputs"
CORE = BASE/"BHSM_N12_C2_LOHNER_STEP_1222.json"
FAMILY = BASE/"BHSM_N12_C2_1222_PARAMETRIC_BASE_FAMILY.json"
THEORY = ROOT/"theory/n12_current_single_witness_initial_scalar_inputs.md"


def _sha(path):
    path = Path(path)
    data = path.read_bytes()
    if path.suffix.lower() in {".py", ".md", ".json"}:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest().upper()


def _down(value):
    return math.nextafter(float(value), -math.inf)


def _up(value):
    return math.nextafter(float(value), math.inf)


def exact_action_distance_upper(raw_left, raw_right, weights):
    """Outward Euclidean action distance of exact binary64 inputs."""
    difference = [Fraction.from_float(float(w))*(Fraction.from_float(float(a))-Fraction.from_float(float(b)))
                  for a, b, w in zip(raw_left, raw_right, weights, strict=True)]
    squared = sum((value*value for value in difference), Fraction(0))
    with ctx.workprec(256):
        distance = arb(fmpq(squared.numerator, squared.denominator)).sqrt()
        upper = _up(distance.upper()) if squared else 0.0
        enclosure = str(distance)
    return upper, enclosure


def exact_action_coordinate_distance_upper(action_left, raw_right, weights):
    difference = [Fraction.from_float(float(a))-Fraction.from_float(float(w))*Fraction.from_float(float(b))
                  for a, b, w in zip(action_left, raw_right, weights, strict=True)]
    squared = sum((value*value for value in difference), Fraction(0))
    with ctx.workprec(256):
        distance = arb(fmpq(squared.numerator, squared.denominator)).sqrt()
        return (_up(distance.upper()) if squared else 0.0), str(distance)


def signed_range(poly, left, right, *, positive, depth=0, max_depth=24):
    """Exact Bernstein range, with early failure on an opposite-sign box."""
    coefficients = _bernstein(_compose_interval(poly, left, right))
    lo, hi = min(coefficients), max(coefficients)
    if (lo > 0 if positive else hi < 0):
        return True, lo, hi, depth, 1
    if (hi <= 0 if positive else lo >= 0) or depth >= max_depth:
        return False, lo, hi, depth, 1
    middle = (left+right)/2
    a = signed_range(poly, left, middle, positive=positive, depth=depth+1, max_depth=max_depth)
    b = signed_range(poly, middle, right, positive=positive, depth=depth+1, max_depth=max_depth)
    return a[0] and b[0], min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]), a[4]+b[4]


def strict_root_bracket(poly, iterations=100):
    """Retain strict signs even when a bisection midpoint is the exact root."""
    left, right = Fraction(0), Fraction(1)
    if not _evaluate(poly, left) > 0 > _evaluate(poly, right):
        raise ValueError("terminal polynomial has no strict positive-to-negative bracket")
    for _ in range(iterations):
        middle = (left+right)/2
        value = _evaluate(poly, middle)
        if value > 0:
            left = middle
        elif value < 0:
            right = middle
        else:
            left, right = (left+middle)/2, (middle+right)/2
    return left, right


def scalar_replay(values, coefficients, grid, bracket):
    """Replay all complete prefix cells and the entire terminal native cell."""
    records, minimum, leaves, depth = [], None, 0, 0
    for index in range(bracket):
        poly = _dense_power(values[index], coefficients[index])
        success, lo, hi, local_depth, count = signed_range(poly, Fraction(0), Fraction(1), positive=True)
        minimum = lo if minimum is None else min(minimum, lo)
        leaves += count; depth = max(depth, local_depth)
        records.append(dict(interval=index, action_interval=[float(grid[index]), float(grid[index+1])],
            center_scalar_positive=success, Bernstein_lower=_down(lo), Bernstein_upper=_up(hi)))
    terminal = _dense_power(values[bracket], coefficients[bracket])
    derivative = signed_range(_derivative(terminal), Fraction(0), Fraction(1), positive=False)
    root_left, root_right = strict_root_bracket(terminal)
    terminal_before = signed_range(terminal, Fraction(0), root_left, positive=True)
    root_times = [Fraction.from_float(float(grid[bracket]))+fraction*(Fraction.from_float(float(grid[bracket+1]))-Fraction.from_float(float(grid[bracket])))
                  for fraction in (root_left, root_right)]
    width = Fraction.from_float(float(grid[bracket+1]))-Fraction.from_float(float(grid[bracket]))
    first = _dense_power(values[0], coefficients[0])
    # (s_center(a)-s_center(0))/a on the first native cell has no constant
    # division singularity; this is useful for a causal scalar error budget.
    first_width = Fraction.from_float(float(grid[1]))-Fraction.from_float(float(grid[0]))
    growth = [value/first_width for value in first[1:]]
    growth_certificate = signed_range(growth, Fraction(0), Fraction(1), positive=True)
    validation = dict(all_complete_preterminal_center_cells_positive=all(row["center_scalar_positive"] for row in records),
        terminal_native_cell_scalar_derivative_negative=derivative[0],
        terminal_center_positive_before_root_bracket=terminal_before[0],
        strict_terminal_center_root_bracket=_evaluate(terminal, root_left)>0>_evaluate(terminal, root_right),
        first_cell_causal_scalar_growth_positive=growth_certificate[0])
    return dict(authority="EXACT_RATIONAL_BINARY64_DOP853_SCALAR_POLYNOMIAL_REPLAY", validation=validation,
        validation_passed=all(validation.values()), complete_preterminal_intervals=int(bracket),
        native_intervals=int(len(coefficients)), rows=records,
        minimum_preterminal_Bernstein_lower=_down(minimum),
        terminal_native_action_interval=[float(grid[bracket]), float(grid[bracket+1])],
        terminal_root_fraction_interval_exact=[str(root_left), str(root_right)],
        terminal_root_action_interval=[_down(root_times[0]), _up(root_times[1])],
        terminal_root_fraction_width_upper=_up(root_right-root_left),
        terminal_root_bracket_scalar_interval=[_down(_evaluate(terminal, root_right)), _up(_evaluate(terminal, root_left))],
        terminal_scalar_derivative_per_action_interval=[_down(derivative[1]/width), _up(derivative[2]/width)],
        terminal_native_right_scalar_upper=_up(_evaluate(terminal, Fraction(1))),
        first_cell_causal_growth_lower_per_action=_down(growth_certificate[1]),
        maximum_subdivision_depth=max(depth, derivative[3], terminal_before[3], growth_certificate[3]),
        total_Bernstein_leaves=leaves+derivative[4]+terminal_before[4]+growth_certificate[4],
        exact_history_first_hit_certified=False,
        next_input="CURRENT_CAUSAL_SCALAR_GRAPH_ERROR_AND_STATE_SHADOWING_RADIUS_WITH_STRICT_EARLIER_DOMAIN_AND_TERMINAL_DELTA_MARGINS")


def run(center: Path, out: Path):
    core, family = (json.loads(path.read_text(encoding="utf-8")) for path in (CORE, FAMILY))
    core_data = ROOT/core["endpoint_data"]
    if not core["validation_passed"] or not family["validation_passed"] or _sha(core_data)!=core["endpoint_data_SHA256"]:
        raise ValueError("validated certified1222 initial member required")
    with np.load(core_data, allow_pickle=False) as z:
        predictor, core_weights, core_reference = (np.array(z[key]) for key in ("endpoint_predictor_center", "state_weights", "branch_reference"))
    with np.load(center, allow_pickle=False) as z:
        initial, weights, reference = (np.array(z[key]) for key in ("centers", "state_weights", "branch_reference"))
        initial = initial[0]
        values, coefficients, grid = (np.array(z[key]) for key in
            ("fine_grid_augmented_action_values", "fine_grid_DOP853_dense_coefficients", "fine_grid_action_lengths"))
        descriptors = np.array(z["signed_descriptors"])
        bracket = int(np.ravel(z["stop_bracket_fine_grid_index"])[0])
    if not np.array_equal(weights, core_weights) or not np.array_equal(reference, core_reference):
        raise ValueError("current center weights/eigenline reference differ from certified core")
    s_exact = Fraction(core["segment"]["signed_descriptor_end"])
    s_center = Fraction.from_float(float(descriptors[0]))
    if float(s_exact) != float(descriptors[0]) or Fraction.from_float(float(values[0,-1])) != s_center:
        raise ValueError("current initial scalar is not the binary64 image of the certified descriptor fiber")
    initial_scalar_offset = s_center-s_exact
    translation, translation_text = exact_action_distance_upper(initial, predictor, weights)
    native_translation, native_text = exact_action_coordinate_distance_upper(values[0,:98], predictor, weights)
    radius = float(core["segment"]["endpoint_tube_radius_upper"])
    total_radius, native_radius = _up(radius+translation), _up(radius+native_translation)
    scalar = scalar_replay(values[:,-1], coefficients[:,:,-1], grid, bracket)
    inclusion = dict(authority="CERTIFIED_RESET_MEMBER_PROPAGATED_THROUGH1222_FIXED_S_SEGMENTS_PLUS_EXACT_BINARY64_CENTER_TRANSLATION",
        certified_endpoint_action_radius_upper=radius,
        raw_center_action_translation_upper=translation, raw_center_translation_Arb256=translation_text,
        current_raw_center_initial_action_radius_upper=total_radius,
        native_action_center_translation_upper=native_translation, native_translation_Arb256=native_text,
        current_native_action_center_initial_action_radius_upper=native_radius,
        exact_initial_descriptor_fiber=str(s_exact), exact_initial_descriptor_value=float(s_exact),
        stored_center_initial_descriptor_exact=str(s_center),
        stored_center_minus_exact_member_descriptor_exact=str(initial_scalar_offset),
        stored_center_minus_exact_member_descriptor_interval=[_down(initial_scalar_offset), _up(initial_scalar_offset)],
        descriptor_error_relative_to_certified_fiber_at_initial_member=0,
        causal_descriptor_error_after_known_initial_offset=0,
        descriptor_fiber_owner="FIXED_S_1222_EXACT_MEMBER:lambda24(Y_initial)=s1222;NOT_A_GENERIC98_BALL_EIGENVALUE_BOUND",
        proof_center_is_exact_initial_member=False, physical_member_selector_introduced=False,
        initial_core_domains={key:core["domain"][key] for key in ("Delta_interval", "b_psi_interval", "c_interval", "lapse_interval", "D_tau_log_R4_interval")},
        certified_reset_root_inclusion_inherited=family["validation"]["certified_exact_normal_root_is_in_the_initial_flow_tube"],
        validation_passed=True)
    sources = [center, CORE, core_data, FAMILY, Path(__file__), THEORY,
               ROOT/"scripts/audit_n12_c2_stop_dense_descriptor_first_hit.py"]
    report = dict(status="CURRENT1222_INITIAL_MEMBER_INCLUSION_AND185_DOP853_CENTER_SCALAR_FIRST_HIT_INPUTS_MATERIALIZED",
        center=str(center.resolve()), center_SHA256=_sha(center), state_dimension=98,
        witness_scope="ONE_RESET_CONNECTED_EXACT_MEMBER;NO_WHOLE_FAMILY_STOP_OR99_FLOW_BOX_CLAIM",
        initial_inclusion=inclusion, scalar_center_replay=scalar,
        validation_passed=inclusion["validation_passed"] and scalar["validation_passed"],
        current_exact_retained_history_first_hit_certified=False,
        current_terminal_Delta_negative_certified=False,
        first_unresolved_dependency="CORRELATED_CURRENT_STATE_SHADOWING_AND_CAUSAL_DESCRIPTOR_ERROR_BOUND;THEN_STRICT_EARLIER_DOMAIN_AND_TERMINAL_NEGATIVE_DELTA_TRANSFER",
        source_SHA256={str(path.resolve()):_sha(path) for path in sources}, FULL_BHSM_COMPLETE=False)
    out.mkdir(parents=True, exist_ok=True)
    (out/"report.json").write_text(json.dumps(report, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(json.dumps({key:report[key] for key in ("status", "center_SHA256", "initial_inclusion", "validation_passed", "first_unresolved_dependency")}, indent=2))
    print(json.dumps({key:value for key,value in scalar.items() if key not in ("rows",)}, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--center", type=Path, default=DEFAULT_CENTER)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    run(args.center, args.out)
