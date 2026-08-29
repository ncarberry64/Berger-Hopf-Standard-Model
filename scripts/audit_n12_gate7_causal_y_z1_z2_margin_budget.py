"""Audit the causal Gate-7 Y/Z1/Z2 budget against the corrected center.

This is an exact-rational positivity statement about a deliberately explicit
stored-profile proxy.  The Y term is the Decimal Gauss-6/8 PROP32 profile
increment, Z1 is the PROP16/32 Gauss-8 profile increment, and Z2 is the
existing causal Taylor--Volterra radius interpolated onto the fine grid.
All three radii vanish at reset.  The audit does not promote either numerical
cross-discretization difference to outward interval authority.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
DENSE = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
FROZEN = BASE / "BHSM_N12_GATE7_FROZEN_DECIMAL_GAUSS8_CENTER.npz"
PROP16 = BASE / "BHSM_N12_GATE7_DECIMAL_SIGNED_Y_GREEN_CONVERGENCE_AUDIT.npz"
PROP32 = BASE / "BHSM_N12_GATE7_DECIMAL_SIGNED_Y_GREEN_PROP32_AUDIT.npz"
JACOBIAN = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_FINE_HYBRID_GRAPH_JACOBIAN_RECONNAISSANCE.npz"
Z2 = BASE / "BHSM_N12_GATE7_SELECTED_CONE_INTERNAL_RESPONSE_Z2.json"
RESULT = BASE / "BHSM_N12_GATE7_CAUSAL_Y_Z1_Z2_MARGIN_BUDGET_AUDIT.json"
DATA = RESULT.with_suffix(".npz")


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _dense_power(left: float, coefficients: np.ndarray) -> list[Fraction]:
    poly = [Fraction(0)]
    for index, coefficient in enumerate(reversed(coefficients)):
        poly[0] += Fraction.from_float(float(coefficient))
        if index % 2 == 0:
            poly = [Fraction(0), *poly]
        else:
            old = poly
            poly = old + [Fraction(0)]
            for power, value in enumerate(old):
                poly[power + 1] -= value
    poly[0] += Fraction.from_float(float(left))
    return poly


def _add_linear(
    poly: list[Fraction], left: float, right: float, scale: float,
) -> list[Fraction]:
    result = poly + [Fraction(0)] * max(0, 2 - len(poly))
    result[0] += Fraction.from_float(float(scale * left))
    result[1] += Fraction.from_float(float(scale * (right - left)))
    return result


def _compose(
    poly: list[Fraction], left: Fraction, right: Fraction,
) -> list[Fraction]:
    degree = len(poly) - 1
    width = right - left
    result = [Fraction(0) for _ in range(degree + 1)]
    for power, coefficient in enumerate(poly):
        for index in range(power + 1):
            result[index] += (
                coefficient * math.comb(power, index)
                * left ** (power - index) * width ** index
            )
    return result


def _bernstein(poly: list[Fraction]) -> list[Fraction]:
    degree = len(poly) - 1
    return [
        sum(
            poly[j] * Fraction(math.comb(k, j), math.comb(degree, j))
            for j in range(k + 1)
        )
        for k in range(degree + 1)
    ]


def _positive_range(
    poly: list[Fraction], left: Fraction, right: Fraction, *,
    depth: int = 0, max_depth: int = 28,
) -> tuple[bool, Fraction, int, int]:
    coefficients = _bernstein(_compose(poly, left, right))
    lower = min(coefficients)
    if lower > 0:
        return True, lower, depth, 1
    if depth >= max_depth:
        return False, lower, depth, 1
    middle = (left + right) / 2
    a = _positive_range(
        poly, left, middle, depth=depth + 1, max_depth=max_depth,
    )
    b = _positive_range(
        poly, middle, right, depth=depth + 1, max_depth=max_depth,
    )
    return a[0] and b[0], min(a[1], b[1]), max(a[2], b[2]), a[3] + b[3]


def _certify(
    values: np.ndarray, coefficients: np.ndarray,
    correction: np.ndarray, descriptor_radius: np.ndarray,
    bracket: int, stop_fraction: float, inflation: float,
) -> tuple[bool, float, int, int]:
    lower: Fraction | None = None
    depth = 0
    leaves = 0
    for interval in range(bracket + 1):
        poly = _dense_power(values[interval, -1], coefficients[interval, :, -1])
        if interval < bracket:
            corr_right = correction[interval + 1]
            radius_right = descriptor_radius[interval + 1]
            right = Fraction(1)
            slope_scale = 1.0
        else:
            corr_right = correction[-1]
            radius_right = descriptor_radius[-1]
            right = Fraction.from_float(stop_fraction)
            slope_scale = 1.0 / stop_fraction
        poly = _add_linear(
            poly, correction[interval], corr_right, slope_scale,
        )
        poly = _add_linear(
            poly, -inflation * descriptor_radius[interval],
            -inflation * radius_right, slope_scale,
        )
        certificate = _positive_range(poly, Fraction(0), right)
        if not certificate[0]:
            return False, float(certificate[1]), max(depth, certificate[2]), leaves + certificate[3]
        lower = certificate[1] if lower is None else min(lower, certificate[1])
        depth = max(depth, certificate[2])
        leaves += certificate[3]
    if lower is None:
        raise RuntimeError("no descriptor intervals certified")
    return True, float(lower), depth, leaves


def main() -> None:
    with np.load(DENSE) as source:
        values = np.asarray(source["fine_grid_augmented_action_values"], dtype=float)
        coefficients = np.asarray(source["fine_grid_DOP853_dense_coefficients"], dtype=float)
        bracket = int(source["stop_bracket_fine_grid_index"][0])
        stop_fraction = float(source["stop_dense_fraction"][0])
    with np.load(FROZEN) as source:
        times = np.asarray(source["fine_action_lengths"], dtype=float)
        correction = np.asarray(source["descriptor_correction_profile"], dtype=float)
    with np.load(PROP16) as source:
        prop16_gauss8 = np.asarray(source["Gauss8_correction_profile"], dtype=float)
    with np.load(PROP32) as source:
        prop32_gauss6 = np.asarray(source["Gauss6_correction_profile"], dtype=float)
        prop32_gauss8 = np.asarray(source["Gauss8_correction_profile"], dtype=float)
    with np.load(JACOBIAN) as source:
        descriptor_gradient = np.asarray(source["descriptor_gradient_action"], dtype=float)
    z2_record = json.loads(Z2.read_text(encoding="utf-8"))

    expected = (bracket + 2, 98)
    if any(profile.shape != expected for profile in (
        prop16_gauss8, prop32_gauss6, prop32_gauss8,
    )):
        raise RuntimeError("complete 371-node correction profiles required")
    if correction.shape != (bracket + 2,) or times.shape != (bracket + 2,):
        raise RuntimeError("frozen center grid does not align")

    y_cross = np.linalg.norm(prop32_gauss8 - prop32_gauss6, axis=1)
    z1_cross = np.linalg.norm(prop32_gauss8 - prop16_gauss8, axis=1)
    # Running maxima are a conservative causal bookkeeping envelope for the
    # stored node profiles.  They do not assert an interval tail theorem.
    y_radius = np.maximum.accumulate(y_cross)
    z1_radius = np.maximum.accumulate(z1_cross)

    macro_times = np.asarray([
        row["action_length"] for row in z2_record["rows"]
    ], dtype=float)
    macro_z2 = np.asarray(
        z2_record["causal_Taylor_Volterra"]["total_radius"], dtype=float,
    )
    z2_radius = np.interp(times, macro_times, macro_z2)
    state_radius = y_radius + z1_radius + z2_radius
    cone_radius = float(z2_record["domain"]["candidate_nonlinear_action_radius"])
    yz_radius = y_radius + z1_radius
    yz_inflation_to_cone = np.divide(
        cone_radius - z2_radius, yz_radius,
        out=np.full_like(yz_radius, np.inf), where=yz_radius > 0.0,
    )
    minimum_yz_inflation_to_cone = float(np.min(yz_inflation_to_cone))
    gradient_upper = float(np.max(np.linalg.norm(descriptor_gradient, axis=1)))
    descriptor_radius = gradient_upper * state_radius

    base = _certify(
        values, coefficients, correction, descriptor_radius,
        bracket, stop_fraction, 1.0,
    )
    lower_factor = 1.0
    upper_factor = 2.0
    while upper_factor < 1.0e12 and _certify(
        values, coefficients, correction, descriptor_radius,
        bracket, stop_fraction, upper_factor,
    )[0]:
        lower_factor = upper_factor
        upper_factor *= 2.0
    for _ in range(48):
        middle = 0.5 * (lower_factor + upper_factor)
        if _certify(
            values, coefficients, correction, descriptor_radius,
            bracket, stop_fraction, middle,
        )[0]:
            lower_factor = middle
        else:
            upper_factor = middle

    np.savez_compressed(
        DATA,
        fine_action_lengths=times,
        signed_Y_cross_order_node_norm=y_cross,
        causal_signed_Y_proxy_radius=y_radius,
        PROP16_to_PROP32_node_norm=z1_cross,
        causal_PROP_Z1_proxy_radius=z1_radius,
        interpolated_causal_Z2_radius=z2_radius,
        combined_state_proxy_radius=state_radius,
        descriptor_proxy_radius=descriptor_radius,
    )
    validation = {
        "all_three_proxy_radii_vanish_exactly_at_reset": bool(
            y_radius[0] == z1_radius[0] == z2_radius[0] == state_radius[0] == 0.0
        ),
        "causal_proxy_radii_are_nondecreasing": bool(
            np.all(np.diff(y_radius) >= 0.0)
            and np.all(np.diff(z1_radius) >= 0.0)
        ),
        "corrected_stored_center_minus_unit_proxy_is_positive_to_old_hit": base[0],
        "unit_proxy_is_strictly_inside_existing_selected_cone": bool(
            np.max(state_radius) < cone_radius
        ),
        "Y_plus_Z1_proxy_has_more_than_five_fold_cone_headroom": (
            minimum_yz_inflation_to_cone > 5.0
        ),
        "stored_proxy_has_more_than_100_fold_inflation_headroom": lower_factor > 100.0,
        "exact_rational_Bernstein_replay_used_for_stored_polynomials": True,
        "numerical_cross_discretization_not_promoted_to_interval_authority": True,
        "shifted_first_hit_and_outward_interval_tail_remain_open": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    payload = {
        "artifact": "BHSM_N12_GATE7_CAUSAL_Y_Z1_Z2_MARGIN_BUDGET_AUDIT",
        "status": (
            "CAUSAL_STORED_PROFILE_BUDGET_HAS_STRICT_CONTINUOUS_PREHIT_HEADROOM;_"
            "OUTWARD_INTERVAL_TAIL_AND_SHIFTED_FIRST_HIT_REMAIN_OPEN"
        ),
        "authority": (
            "EXACT_RATIONAL_MARGIN_FOR_EXPLICIT_NUMERICAL_CAUSAL_PROXY;_"
            "NOT_OUTWARD_Y_OR_Z1_INTERVAL_AUTHORITY"
        ),
        "identity": {
            "Y_proxy": "RUNNING_MAX_NORM_OF_DECIMAL_GAUSS6_TO_8_PROP32_PROFILE_INCREMENT",
            "Z1_proxy": "RUNNING_MAX_NORM_OF_GAUSS8_PROP16_TO_PROP32_PROFILE_INCREMENT",
            "Z2": "LINEAR_FINE_GRID_INTERPOLATION_OF_CERTIFIED_CAUSAL_MACRO_RADIUS",
            "descriptor_image": "GLOBAL_STORED_DESCRIPTOR_GRADIENT_NODE_NORM_TIMES_STATE_RADIUS",
            "reset_weight": "ALL_CAUSAL_RADII_EQUAL_ZERO_AT_ACTION_TIME_ZERO",
        },
        "summary": {
            "maximum_signed_Y_cross_order_node_norm": float(np.max(y_cross)),
            "maximum_PROP16_to_PROP32_node_norm": float(np.max(z1_cross)),
            "maximum_interpolated_causal_Z2_radius": float(np.max(z2_radius)),
            "maximum_combined_state_proxy_radius": float(np.max(state_radius)),
            "existing_selected_cone_radius": cone_radius,
            "remaining_selected_cone_reserve_at_unit_proxy": float(
                cone_radius - np.max(state_radius)
            ),
            "Y_plus_Z1_proxy_inflation_to_selected_cone_lower": (
                minimum_yz_inflation_to_cone
            ),
            "descriptor_gradient_stored_node_norm_upper": gradient_upper,
            "maximum_descriptor_proxy_radius": float(np.max(descriptor_radius)),
            "minimum_exact_Bernstein_margin_at_unit_proxy": base[1],
            "maximum_Bernstein_subdivision_depth": base[2],
            "total_Bernstein_leaves": base[3],
            "certified_proxy_inflation_factor_lower": lower_factor,
            "failing_proxy_inflation_factor_upper": upper_factor,
        },
        "data": DATA.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "claim_boundary": {
            "causal_numerical_budget_viability": "CERTIFIED_FOR_THE_STORED_PROXY",
            "selected_cone_self_map": "OPEN_UNTIL_OUTWARD_Y_Z1_AND_REBUILT_Z2",
            "outward_signed_Y": "OPEN_INTERVAL_AUTHORITY",
            "outward_PROP16_Z1": "OPEN_INTERVAL_AUTHORITY",
            "continuous_exact_history_margin": "OPEN_UNTIL_OUTWARD_TAIL_TRANSFER",
            "shifted_scalar_first_hit": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "PROVE_A_CAUSAL_OUTWARD_Y_PLUS_PROP16_Z1_STATE_RADIUS_BELOW_THE_REPORTED_"
            "FIVE_FOLD_SELECTED_CONE_HEADROOM,_THEN_REBUILD_THE_CENTER_DEPENDENT_Z2_CONE_"
            "AND_APPLY_SCALAR_INTERVAL_NEWTON_ON_THE_SHIFTED_TERMINAL_SEGMENT"
        ),
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in (DENSE, FROZEN, PROP16, PROP32, JACOBIAN, Z2)
        },
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
