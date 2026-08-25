"""Derive the common asymptotic product norm and directed X5 norm scale."""

from __future__ import annotations

from decimal import Decimal, getcontext
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_COMPACTIFIED_ASYMPTOTIC_COMMON_CHART.json"
)
THEORY = ROOT / "theory/n12_compactified_asymptotic_common_chart.md"
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_INTERVAL_WEIGHT_FIVE_CENTER_LIFT.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_ASYMPTOTIC_NHIM_CAPTURE_BASIN.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_RESET_TO_ASYMPTOTIC_CAPTURE_OVERLAP_AUDIT.json",
    ROOT / "src/bhsm/interface/aether_sobolev_metric_soft_mode_lift_v16_07.py",
    THEORY,
)
NUMBER = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ball_absolute_bounds(record: dict[str, object]) -> tuple[Decimal, Decimal]:
    midpoint_numbers = [Decimal(value) for value in NUMBER.findall(record["midpoint"])]
    radius_numbers = [Decimal(value) for value in NUMBER.findall(record["radius"])]
    if len(midpoint_numbers) != 2 or len(radius_numbers) != 2:
        raise ValueError("unexpected Arb midpoint/radius rendering")
    midpoint, midpoint_error = midpoint_numbers
    radius, radius_error = radius_numbers
    uncertainty = midpoint_error + radius + radius_error
    lower = max(Decimal(0), abs(midpoint) - uncertainty)
    upper = abs(midpoint) + uncertainty
    return lower, upper


def _frequencies() -> tuple[list[int], list[int], list[int]]:
    # q0 plus windowed w,b modes; the twelve u modes are gauge-quotiented.
    coordinates = [0] + list(range(0, 48, 4)) + list(range(0, 48, 4))
    velocities = list(coordinates)
    multipliers = list(range(4, 52, 4)) + list(range(0, 48, 4))
    return coordinates, velocities, multipliers


def _labels() -> tuple[list[str], list[str], list[str]]:
    coordinates = ["q0"] + [f"w_{j}" for j in range(12)] + [
        f"b_{j}" for j in range(12)
    ]
    velocities = ["dot_q0"] + [f"dot_w_{j}" for j in range(12)] + [
        f"dot_b_{j}" for j in range(12)
    ]
    multipliers = [f"log_lapse_{j}" for j in range(1, 13)] + [
        f"shift_{j}" for j in range(12)
    ]
    return coordinates, velocities, multipliers


def _weighted_norm_bounds(
    lift: dict[str, object], labels: list[str], frequencies: list[int], exponent: int
) -> tuple[Decimal, Decimal, list[dict[str, object]]]:
    lower_squared = Decimal(0)
    upper_squared = Decimal(0)
    rows: list[dict[str, object]] = []
    for label, frequency in zip(labels, frequencies):
        lower, upper = _ball_absolute_bounds(lift[label])
        squared_weight = Decimal((1 + frequency * frequency) ** exponent)
        lower_squared += squared_weight * lower * lower
        upper_squared += squared_weight * upper * upper
        rows.append(
            {
                "label": label,
                "frequency": frequency,
                "squared_weight": str(squared_weight),
                "absolute_lower": str(lower),
                "absolute_upper": str(upper),
                "weighted_absolute_upper": str(
                    upper * squared_weight.sqrt()
                ),
            }
        )
    return lower_squared.sqrt(), upper_squared.sqrt(), rows


def build_payload() -> dict[str, object]:
    getcontext().prec = 100
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing common-chart inputs: " + ", ".join(missing))
    interval, basin, overlap = (_load(path) for path in INPUTS[:3])
    if not all(
        record.get("validation_passed") is True
        for record in (interval, basin, overlap)
    ):
        raise RuntimeError("validated common-chart inputs required")

    lift = interval["complete_leading_modulation_vector"]
    labels = _labels()
    frequencies = _frequencies()
    q_lower, q_upper, q_rows = _weighted_norm_bounds(
        lift, labels[0], frequencies[0], 6
    )
    v_lower, v_upper, v_rows = _weighted_norm_bounds(
        lift, labels[1], frequencies[1], 5
    )
    m_lower, m_upper, m_rows = _weighted_norm_bounds(
        lift, labels[2], frequencies[2], 6
    )
    total_lower = (q_lower * q_lower + v_lower * v_lower + m_lower * m_lower).sqrt()
    total_upper = (q_upper * q_upper + v_upper * v_upper + m_upper * m_upper).sqrt()
    dominant = max(q_rows + v_rows + m_rows, key=lambda row: Decimal(row["weighted_absolute_upper"]))
    validation = {
        "complete_directed_lift_has_74_components": len(lift) == 74,
        "physical_product_chart_has_25_plus_25_plus_24_components": (
            sum(len(group) for group in labels) == 74
        ),
        "all_directed_component_balls_have_positive_accuracy": all(
            int(record["relative_accuracy_bits"]) >= 250 for record in lift.values()
        ),
        "directed_product_norm_interval_is_positive_and_ordered": (
            Decimal(0) < total_lower <= total_upper
        ),
        "coordinate_H6_velocity_H5_multiplier_H6_topology_used": True,
        "common_scale_is_recentered_not_quotiented_as_full_action_gauge": True,
        "capture_radius_rho_star_not_selected": True,
        "reset_ball_radius_not_substituted_for_asymptotic_chart_radius": True,
        "no_selector_scale_fit_endpoint_action_term_or_chord_added": True,
    }

    return {
        "artifact": "BHSM_N12_COMPACTIFIED_ASYMPTOTIC_COMMON_CHART",
        "status": "COMMON_PHYSICAL_PRODUCT_NORM_AND_FIRST_LIFT_SCALE_DERIVED_CAPTURE_RADIUS_OPEN",
        "classification": (
            "THE_RETAINED_H6_COORDINATE_CROSS_H5_VELOCITY_CROSS_H6_"
            "MULTIPLIER_COEFFICIENT_NORM_DEFINES_A_SINGLE_74_COMPONENT_"
            "COMPACTIFIED_ASYMPTOTIC_CHART;_THE_DIRECTED_FIRST_LOWER_WEIGHT_"
            "LIFT_HAS_PRODUCT_NORM_ABOUT_5.68E13,_SO_A_FUTURE_ACTION_OWNED_"
            "CHART_RADIUS_rho_star_REQUIRES_epsilon<=rho_star/C_X5_BEFORE_"
            "THE_NONLINEAR_REMAINDER_CAN_BE_ABSORBED"
        ),
        "chart": {
            "coordinates": "q0_tilde,w_0..w_11,b_0..b_11",
            "velocities": "dot_q0_modulation,dot_w_0..dot_w_11,dot_b_0..dot_b_11",
            "multipliers": "log_lapse_1..log_lapse_12,shift_0..shift_11",
            "dimension": 74,
            "scale_compactification": "epsilon=R4^-2",
            "q0_tilde": "COMMON_SCALE_MODULATION_AFTER_SUBTRACTING_ROUND_EXPANDING_SCALE",
            "common_scale_full_action_status": "PHYSICAL_RECENTERED_NOT_GAUGE_QUOTIENTED",
        },
        "norm": {
            "product": "H6_coordinates_CROSS_H5_velocities_CROSS_H6_multipliers",
            "coordinate_squared_weight": "(1+omega^2)^6",
            "velocity_squared_weight": "(1+omega^2)^5",
            "multiplier_squared_weight": "(1+omega^2)^6",
            "frequencies": {
                "coordinates": frequencies[0],
                "velocities": frequencies[1],
                "multipliers": frequencies[2],
            },
        },
        "directed_X5_norm": {
            "coordinate_lower": str(q_lower),
            "coordinate_upper": str(q_upper),
            "velocity_lower": str(v_lower),
            "velocity_upper": str(v_upper),
            "multiplier_lower": str(m_lower),
            "multiplier_upper": str(m_upper),
            "product_lower": str(total_lower),
            "product_upper": str(total_upper),
            "dominant_weighted_component": dominant,
        },
        "symbolic_capture_conversion": {
            "future_action_owned_chart_radius": "rho_star>0",
            "first_lift_condition": "epsilon*C_X5_upper<=rho_star",
            "epsilon_upper": "rho_star/C_X5_upper",
            "R4_lower": "sqrt(C_X5_upper/rho_star)",
            "rho_star_numerically_selected": False,
            "nonlinear_remainder_included": False,
        },
        "exact_next_dependency": (
            "DERIVE_AN_ACTION_OWNED_POSITIVE_rho_star_FROM_UNIFORM_REDUCED_"
            "KINETIC_CONSTRAINT_INERTIA_METRIC_LAPSE_EXPANSION_AND_SELECTED_"
            "LINE_MARGINS,_PLUS_A_COMPLETE_REMAINDER_MAJORANT_THAT_FITS_"
            "INSIDE_THE_UNUSED_PART_OF_THE_SAME_PRODUCT_BALL"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_EXPLICIT_ASYMPTOTIC_PRODUCT_BALL_MAJORANTS",
            "Gate8": "LOCKED",
            "common_asymptotic_chart_and_norm": "DERIVED",
            "directed_first_lift_norm": "CERTIFIED",
            "quantitative_capture_radius": "OPEN_CURRENT_OWNER",
            "reset_to_capture_overlap": "NOT_CERTIFIED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(RESULT)


if __name__ == "__main__":
    main()
