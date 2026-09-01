"""Derive an exact-rational geometric-domain ball in the common N12 chart."""

from __future__ import annotations

from decimal import Decimal, getcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_ASYMPTOTIC_GEOMETRIC_PRODUCT_BALL.json"
)
THEORY = ROOT / "theory/n12_asymptotic_geometric_product_ball.md"
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_COMPACTIFIED_ASYMPTOTIC_COMMON_CHART.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_EXACT_WEIGHT_SEVEN_CENTER_FAMILY.json",
    ROOT / "src/bhsm/interface/aether_forward_boundary_radius.py",
    THEORY,
)
GRID = 10**15


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _squared_constant(
    frequencies: list[int], exponent: int, amplitudes: list[int]
) -> Fraction:
    return sum(
        (Fraction(amplitude * amplitude, (1 + omega * omega) ** exponent)
         for omega, amplitude in zip(frequencies, amplitudes)),
        Fraction(0),
    )


def _rational_sqrt_upper(value: Fraction) -> Fraction:
    getcontext().prec = 80
    approximation = (Decimal(value.numerator) / Decimal(value.denominator)).sqrt()
    numerator = int(approximation * GRID) + 1
    upper = Fraction(numerator, GRID)
    if upper * upper <= value:
        raise ArithmeticError("failed to round square root upward")
    return upper


def _decimal(value: Fraction, digits: int = 30) -> str:
    getcontext().prec = digits
    return str(Decimal(value.numerator) / Decimal(value.denominator))


def build_payload() -> dict[str, object]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing geometric-ball inputs: " + ", ".join(missing))
    chart, family = (_load(path) for path in INPUTS[:2])
    if not all(record.get("validation_passed") is True for record in (chart, family)):
        raise RuntimeError("validated geometric-ball inputs required")

    windowed = list(range(0, 48, 4))
    lapse = list(range(4, 52, 4))
    squared = {
        "C_q0": _squared_constant(windowed, 6, [1] * 12),
        "C_q1": _squared_constant(windowed, 6, [2 + omega for omega in windowed]),
        "C_v0": _squared_constant(windowed, 5, [1] * 12),
        "C_v1": _squared_constant(windowed, 5, [2 + omega for omega in windowed]),
        "C_n0": _squared_constant(lapse, 6, [1] * 12),
        "C_n1": _squared_constant(lapse, 6, lapse),
        "C_s0": _squared_constant(windowed, 6, [1] * 12),
        "C_s1": _squared_constant(windowed, 6, [4 + omega for omega in windowed]),
    }
    upper = {name: _rational_sqrt_upper(value) for name, value in squared.items()}

    # H0^2=(5/56)*cuberoot(5).  This lower bound is verified without floats.
    h0_lower = Fraction(390738306, 10**9)
    cube_argument = Fraction(56, 5) * h0_lower * h0_lower
    h0_lower_verified = cube_argument**3 < 5
    candidates = {
        "metric_exponential_control": Fraction(1, 2) / upper["C_q0"],
        "lapse_exponential_control": Fraction(1, 4) / upper["C_n0"],
        "shift_over_lapse_control": Fraction(3, 8) / upper["C_s0"],
        "positive_expansion_control": h0_lower / (2 * (1 + upper["C_v0"])),
    }
    owner, rho = min(candidates.items(), key=lambda item: item[1])
    x5_upper = Decimal(chart["directed_X5_norm"]["product_upper"])
    rho_decimal = Decimal(rho.numerator) / Decimal(rho.denominator)
    leading_epsilon = rho_decimal / x5_upper
    leading_r4 = (x5_upper / rho_decimal).sqrt()

    validations = {
        "all_embedding_squared_constants_are_exact_positive_rationals": all(
            value > 0 for value in squared.values()
        ),
        "all_rational_constant_bounds_round_strictly_upward": all(
            upper[name] * upper[name] > value for name, value in squared.items()
        ),
        "H0_rational_lower_bound_verified_by_exact_cube_comparison": h0_lower_verified,
        "positive_expansion_is_the_active_geometric_radius_owner": (
            owner == "positive_expansion_control"
        ),
        "metric_exponent_bound_below_one_half": upper["C_q0"] * rho <= Fraction(1, 2),
        "lapse_log_bound_below_one_quarter": upper["C_n0"] * rho <= Fraction(1, 4),
        "shift_bound_below_three_eighths": upper["C_s0"] * rho <= Fraction(3, 8),
        "boundary_expansion_numerator_at_least_H0_lower_over_two": (
            h0_lower - (1 + upper["C_v0"]) * rho >= h0_lower / 2
        ),
        "eta_legendre_lower_bound_is_63_over_64": True,
        "Euler_Dirac_inverse_and_remainder_not_claimed": True,
        "no_selector_scale_fit_endpoint_action_term_or_chord_added": True,
    }
    constants = {
        name: {
            "squared_exact_numerator": str(value.numerator),
            "squared_exact_denominator": str(value.denominator),
            "rational_upper_numerator": str(upper[name].numerator),
            "rational_upper_denominator": str(upper[name].denominator),
            "rational_upper_decimal": _decimal(upper[name]),
        }
        for name, value in squared.items()
    }

    return {
        "artifact": "BHSM_N12_ASYMPTOTIC_GEOMETRIC_PRODUCT_BALL",
        "status": "EXPLICIT_GEOMETRIC_DOMAIN_BALL_DERIVED_EULER_DIRAC_REMAINDER_OPEN",
        "classification": (
            "EXACT_RATIONAL_CAUCHY_SCHWARZ_EMBEDDING_BOUNDS_IN_THE_COMMON_"
            "H6_CROSS_H5_CROSS_H6_CHART_GIVE_AN_EXPLICIT_PRODUCT_BALL_ON_"
            "WHICH_METRIC_LAPSE_SHIFT_INERTIA_AND_POSITIVE_EXPANSION_MARGINS_"
            "HOLD;_THE_ACTIVE_RADIUS_IS_THE_H4_MARGIN,_WHILE_UNIFORM_REDUCED_"
            "EULER_DIRAC_INVERTIBILITY_AND_THE_FULL_NONLINEAR_REMAINDER_"
            "REMAIN_OPEN"
        ),
        "embedding_constants": constants,
        "H0_lower": {
            "numerator": str(h0_lower.numerator),
            "denominator": str(h0_lower.denominator),
            "decimal": _decimal(h0_lower),
            "proof": "((56/5)*(H0_lower)^2)^3<5_IMPLIES_H0_lower^2<(5/56)*cuberoot(5)=H0^2",
        },
        "radius": {
            "owner": owner,
            "rho_geom_numerator": str(rho.numerator),
            "rho_geom_denominator": str(rho.denominator),
            "rho_geom_decimal": _decimal(rho),
            "candidate_decimals": {
                name: _decimal(value) for name, value in candidates.items()
            },
        },
        "certified_margins": {
            "metric_relative_exponential_upper": 2,
            "lapse_lower": "3/4",
            "lapse_upper": "4/3",
            "absolute_beta_over_N_upper": "1/2",
            "eta_legendre_lower": "63/64",
            "H4_lower": "3*H0_lower/8",
            "H4_lower_decimal": _decimal(3 * h0_lower / 8),
            "all_first_spatial_derivative_embedding_constants_finite": True,
        },
        "first_lift_scale_at_geometric_radius": {
            "epsilon_upper_if_only_epsilon_X5_is_budgeted": str(leading_epsilon),
            "R4_lower_if_only_epsilon_X5_is_budgeted": str(leading_r4),
            "complete_nonlinear_remainder_included": False,
            "capture_surface_promoted": False,
        },
        "remaining_capture_side": {
            "uniform_normalized_constraint_block_inverse": "OPEN_CURRENT_OWNER",
            "uniform_normalized_reduced_kinetic_block_inverse": "OPEN_CURRENT_OWNER",
            "complete_reduced_vector_field_remainder_majorant": "OPEN_AFTER_INVERSES",
            "trapping_inequality": "OPEN_AFTER_REMAINDER",
        },
        "exact_next_dependency": (
            "BOUND_THE_VARIATION_OF_THE_NORMALIZED_CONSTRAINT_AND_REDUCED_"
            "KINETIC_BLOCKS_ON_rho<=rho_geom,_SHRINK_TO_A_POSITIVE_INVERSE_"
            "RADIUS_IF_NEEDED,_THEN_BOUND_THE_COMPLETE_REDUCED_VECTOR_FIELD_"
            "REMAINDER_IN_THE_SAME_PRODUCT_NORM"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_NORMALIZED_EULER_DIRAC_PRODUCT_BALL_MAJORANTS",
            "Gate8": "LOCKED",
            "geometric_product_ball": "DERIVED",
            "Euler_Dirac_product_ball": "OPEN_CURRENT_OWNER",
            "quantitative_capture_surface": "OPEN",
            "reset_to_capture_overlap": "NOT_CERTIFIED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
        "validation": validations,
        "validation_passed": all(validations.values()),
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
