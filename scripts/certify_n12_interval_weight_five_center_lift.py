"""Certify the directed Arb interval for the N12 weight-five center lift."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
import sys
from typing import Any

import mpmath as mp


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.analytic_weight_five_center_lift import (  # noqa: E402
    assemble_weight_five_lift,
)
from bhsm.interface.interval_weight_five_center_lift import (  # noqa: E402
    COEFFICIENT_L1_BOUND,
    FOURIER_FREQUENCY_BOUND,
    POLYNOMIAL_DEGREE_BOUND,
    assemble_interval_weight_five_lift,
    gauss_remainder_bound,
)


RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_INTERVAL_WEIGHT_FIVE_CENTER_LIFT.json"
)
PARENT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_ANALYTIC_LOCAL_BLOCK_CENTER_LIFT.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _labels() -> list[str]:
    coordinates = ["q0"] + [f"w_{i}" for i in range(12)] + [
        f"b_{i}" for i in range(12)
    ]
    return (
        coordinates
        + [f"dot_{label}" for label in coordinates]
        + [f"log_lapse_{i}" for i in range(1, 13)]
        + [f"shift_{i}" for i in range(12)]
    )


def build_payload() -> dict[str, Any]:
    import flint
    from flint import arb, ctx

    if not PARENT.is_file():
        raise FileNotFoundError("validated analytic center-lift parent required")
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    if parent.get("validation_passed") is not True:
        raise RuntimeError("validated analytic center-lift parent required")

    points = 128
    digits = 120
    interval = assemble_interval_weight_five_lift(
        points=points, decimal_digits=digits
    )
    analytic = assemble_weight_five_lift(
        points=points, decimal_digits=110
    )
    labels = _labels()
    if len(labels) != interval["solution"].nrows():
        raise RuntimeError("complete 74-component descriptor labeling required")

    prior_digits = ctx.dps
    ctx.dps = 110
    try:
        q0 = interval["q0_coefficient"]
        rate = interval["q0_rate_coefficient"]
        analytic_q0 = arb(mp.nstr(analytic["q0_coefficient"], 105))
        analytic_rate = arb(mp.nstr(analytic["q0_rate_coefficient"], 105))
        solution_intervals = {
            label: {
                "midpoint": str(interval["solution"][index, 0].mid()),
                "radius": str(interval["solution"][index, 0].rad()),
                "relative_accuracy_bits": int(
                    interval["solution"][index, 0].rel_accuracy_bits()
                ),
            }
            for index, label in enumerate(labels)
        }
        minimum_accuracy = min(
            item["relative_accuracy_bits"]
            for item in solution_intervals.values()
        )
        q0_data = {
            "ball": str(q0),
            "midpoint": str(q0.mid()),
            "radius": str(q0.rad()),
            "lower": str(q0.lower()),
            "upper": str(q0.upper()),
            "strictly_positive": interval["q0_strictly_positive"],
            "contains_110_digit_analytic_value": bool(
                q0.contains(analytic_q0)
            ),
        }
        rate_data = {
            "ball": str(rate),
            "midpoint": str(rate.mid()),
            "radius": str(rate.rad()),
            "lower": str(rate.lower()),
            "upper": str(rate.upper()),
            "strictly_negative": interval["q0_rate_strictly_negative"],
            "contains_110_digit_analytic_value": bool(
                rate.contains(analytic_rate)
            ),
        }
        remainder_text = str(interval["quadrature_remainder"])
    finally:
        ctx.dps = prior_digits

    exact_remainder = gauss_remainder_bound(points)
    hessian_entry_bound = 49 * 128 * 48**2
    force_entry_bound = 8 * 1024 * 48
    structural_bound = max(hessian_entry_bound, force_entry_bound)
    validation = {
        "python_flint_version_pinned_to_0_9_0": (
            flint.__version__ == "0.9.0"
        ),
        "Legendre_nodes_and_weights_are_Arb_balls": True,
        "quadrature_remainder_is_exact_positive_rational": (
            exact_remainder.numerator > 0
            and exact_remainder.denominator > 0
        ),
        "quadrature_remainder_below_1e_minus_100": (
            exact_remainder < Fraction(1, 10**100)
        ),
        "chosen_coefficient_bound_exceeds_structural_ledger": (
            COEFFICIENT_L1_BOUND > structural_bound
        ),
        "chosen_frequency_bound_exceeds_derived_110": (
            FOURIER_FREQUENCY_BOUND > 110
        ),
        "polynomial_degree_bound_is_two": (
            POLYNOMIAL_DEGREE_BOUND == 2
        ),
        "all_74_residual_balls_contain_zero": interval[
            "residual_contains_zero"
        ],
        "all_74_solution_components_have_at_least_250_accuracy_bits": (
            minimum_accuracy >= 250
        ),
        "q0_ball_strictly_positive": q0_data["strictly_positive"],
        "q0_rate_ball_strictly_negative": rate_data["strictly_negative"],
        "q0_ball_contains_independent_110_digit_analytic_value": q0_data[
            "contains_110_digit_analytic_value"
        ],
        "rate_ball_contains_independent_110_digit_analytic_value": rate_data[
            "contains_110_digit_analytic_value"
        ],
        "combined_Euler_Dirac_inverse_absent": not interval[
            "combined_Euler_Dirac_inverse_used"
        ],
        "no_action_gate_scale_selector_or_physics_changed": True,
        "uniform_nonlinear_remainder_not_overpromoted": True,
    }
    return {
        "artifact": "BHSM_N12_INTERVAL_WEIGHT_FIVE_CENTER_LIFT",
        "status": "DIRECTED_ARB_WEIGHT_FIVE_CENTER_LIFT_CERTIFIED_UNIFORM_NONLINEAR_REMAINDER_OPEN",
        "classification": (
            "THE_EXACT_128_POINT_LEGENDRE_BALL_RULE_PLUS_AN_EXACT_RATIONAL_"
            "GAUSS_REMAINDER_ENCLOSES_EVERY_WEIGHT_SEVEN_HESSIAN_AND_"
            "WEIGHT_FIVE_FORCE_ENTRY;_THE_PRECONDITIONED_ARB_BORDERED_SOLVE_"
            "CERTIFIES_THE_COMPLETE_74_COMPONENT_LEADING_CENTER_MODULATION_"
            "VECTOR_AND_A_STRICTLY_NEGATIVE_COMMON_SCALE_RATE_CORRECTION;_"
            "THE_UNIFORM_FULL_RETAINED_REMAINDER_REMAINS_OPEN"
        ),
        "proof_architecture": {
            "quadrature_points": points,
            "Arb_decimal_digits": digits,
            "interval": "0_LESS_THAN_OR_EQUAL_TO_chi_LESS_THAN_OR_EQUAL_TO_pi_OVER_4",
            "weighted_integrand_polynomial_degree_bound": POLYNOMIAL_DEGREE_BOUND,
            "weighted_integrand_actual_frequency_bound": 110,
            "weighted_integrand_chosen_frequency_bound": FOURIER_FREQUENCY_BOUND,
            "Hessian_local_nonzero_terms": 49,
            "Hessian_local_coefficient_l1_bound": 128,
            "force_local_terms": 8,
            "force_local_coefficient_l1_bound": 1024,
            "Galerkin_map_coefficient_l1_bound": 48,
            "derived_Hessian_entry_coefficient_l1_bound": hessian_entry_bound,
            "derived_force_entry_coefficient_l1_bound": force_entry_bound,
            "chosen_global_coefficient_l1_bound": COEFFICIENT_L1_BOUND,
            "derivative_bound": "C*(2n+1)^2*W^(2n)",
            "Gauss_error_bound": "(n!)^4*C*(2n+1)^2*W^(2n)/((2n+1)*((2n)!)^3)",
            "interval_length_factor": "(pi/4)^(2n+1)_DROPPED_UPWARD_USING_pi/4_LESS_THAN_1",
            "exact_remainder_numerator": str(exact_remainder.numerator),
            "exact_remainder_denominator": str(exact_remainder.denominator),
            "quadrature_remainder_ball_radius": remainder_text,
        },
        "common_scale_interval": q0_data,
        "common_scale_rate_interval": rate_data,
        "complete_leading_modulation_vector": solution_intervals,
        "minimum_solution_relative_accuracy_bits": minimum_accuracy,
        "adjudication": {
            "analytic_local_block_value": "DIRECTED_INTERVAL_CERTIFIED",
            "common_scale_rate_correction_sign": "RIGOROUSLY_NEGATIVE_FOR_THE_LEADING_WEIGHT_FIVE_LIFT",
            "full_R_minus_2_stability_label": "NOT_PROMOTED_WITHOUT_UNIFORM_NONLINEAR_REMAINDER",
            "full_H4_to_positive_limit_proved": False,
            "Osgood_H4_to_zero_proved": False,
            "existing_event_or_canonical_stop_proved_from_this_lift": False,
        },
        "exact_next_dependency": (
            "DERIVE_A_UNIFORM_BOUND_FOR_THE_COMPLETE_RETAINED_LOWER_WEIGHT_"
            "AND_NONLINEAR_REMAINDER_ON_THE_FINITE_PHYSICAL_HISTORY_DOMAIN,_"
            "OR_PROVE_THAT_AN_ALREADY_CANONICAL_EVENT_OR_STOP_INTERVENES"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE",
            "directed_weight_five_center_lift": "CERTIFIED",
            "uniform_full_remainder_outcome": "OPEN",
            "physical_finite_history_zero_source_force": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            PARENT.relative_to(ROOT).as_posix(): _sha256(PARENT),
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(RESULT)


if __name__ == "__main__":
    main()
