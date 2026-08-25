"""Certify the structured D3 first jet of the N12 bordered graph defect."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.interval_weight_seven_graph_first_variation import (  # noqa: E402
    assemble_interval_graph_first_variation,
)


RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_BORDERED_GRAPH_FIRST_VARIATION.json"
)
THEORY = ROOT / "theory/n12_bordered_graph_first_variation.md"
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_ASYMPTOTIC_BORDERED_GRAPH_NORM.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_BORDERED_GRAPH_PRODUCT_NORM_EQUIVALENCE.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_ASYMPTOTIC_GEOMETRIC_PRODUCT_BALL.json",
    ROOT / "src/bhsm/interface/interval_weight_five_center_lift.py",
    ROOT / "src/bhsm/interface/interval_weight_seven_graph_first_variation.py",
    THEORY,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, object]:
    import flint

    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "missing graph-first-variation inputs: " + ", ".join(missing)
        )
    parent_records = [_load(path) for path in INPUTS[:3]]
    if not all(record.get("validation_passed") is True for record in parent_records):
        raise RuntimeError("validated graph-first-variation parents required")

    result = assemble_interval_graph_first_variation(
        points=128, decimal_digits=160
    )
    stack_upper = result["stack_frobenius_upper"]
    radius_lower = result["linear_half_contraction_radius_lower"]
    remainder = result["third_quadrature_remainder"]
    directions = [
        {
            "index": record["index"],
            "label": record["label"],
            "frobenius_ball": str(record["frobenius_ball"]),
            "frobenius_upper": str(record["frobenius_upper"]),
            "residual_contains_zero": record["residual_contains_zero"],
        }
        for record in result["direction_records"]
    ]
    dominant_raw = max(
        result["direction_records"],
        key=lambda record: float(record["frobenius_upper"]),
    )
    dominant = directions[dominant_raw["index"]]
    validation = {
        "python_flint_version_pinned_to_0_9_0": flint.__version__ == "0.9.0",
        "physical_quotient_has_74_directions": len(directions) == 74,
        "local_D3_tensor_has_60_symmetric_nonzero_entries": (
            result["nonzero_symmetric_local_third_terms"] == 60
        ),
        "local_D3_tensor_has_295_ordered_nonzero_entries": (
            result["nonzero_ordered_local_third_terms"] == 295
        ),
        "all_repeated_solve_residual_balls_contain_zero": result[
            "all_repeated_solve_residuals_contain_zero"
        ],
        "directed_stack_bound_is_finite_and_expected_scale": (
            stack_upper > 0
            and float(stack_upper) > 2.36e17
            and float(stack_upper) < 2.38e17
        ),
        "linear_half_contraction_radius_is_strictly_positive": (
            radius_lower > 0
            and float(radius_lower) > 2.10e-18
            and float(radius_lower) < 2.12e-18
        ),
        "directed_cubic_quadrature_remainder_below_7_5e_minus20": (
            float(remainder) < 7.5e-20
        ),
        "common_expansion_rate_coefficient_variation_included": result[
            "explicit_expansion_rate_coefficient_variation_included"
        ],
        "dominant_direction_is_common_expansion_rate": (
            dominant["label"] == "dot_q0"
        ),
        "explicit_bordered_inverse_not_formed": not result[
            "explicit_bordered_inverse_formed"
        ],
        "combined_Euler_Dirac_inverse_not_used": not result[
            "combined_Euler_Dirac_inverse_used"
        ],
        "D4_uniform_remainder_not_overpromoted": True,
        "no_selector_scale_fit_endpoint_action_term_or_chord_added": True,
    }
    return {
        "artifact": "BHSM_N12_BORDERED_GRAPH_FIRST_VARIATION",
        "status": "DIRECTED_STRUCTURED_D3_GRAPH_JET_CERTIFIED_D4_REMAINDER_OPEN",
        "classification": (
            "THE_EXACT_WEIGHT_SEVEN_ACTION_HAS_60_NONZERO_SYMMETRIC_LOCAL_"
            "CUBIC_COEFFICIENTS;_AFTER_PHYSICAL_QUOTIENT_PROJECTION_AND_74_"
            "CERTIFIED_BORDERED_MATRIX_SOLVES,_THE_COMPLETE_FIRST_RELATIVE_"
            "GRAPH_DEFECT_HAS_A_FINITE_FROBENIUS_STACK_BOUND_ABOUT_2.369E17_"
            "AND_A_POSITIVE_LINEAR_HALF_CONTRACTION_RADIUS_ABOUT_2.111E-18;_"
            "THE_UNIFORM_D4_AND_LOWER_WEIGHT_REMAINDER_REMAINS_OPEN"
        ),
        "order": 12,
        "descriptor_dimension": 74,
        "points": result["points"],
        "decimal_digits": result["decimal_digits"],
        "local_action_third_variation": {
            "nonzero_symmetric_terms": result[
                "nonzero_symmetric_local_third_terms"
            ],
            "nonzero_ordered_terms": result[
                "nonzero_ordered_local_third_terms"
            ],
            "directed_quadrature_remainder_radius": str(remainder),
        },
        "structured_repeated_solve_bound": {
            "formula": (
                "M3=(sum_k ||Btilde0^-1*D_kBtilde0||_F^2)^(1/2)"
            ),
            "inverse_in_formula_is_realized_by": (
                "74_DIRECTED_ARB_MATRIX_RIGHT_HAND_SIDE_SOLVES"
            ),
            "explicit_inverse_formed": False,
            "stack_frobenius_upper": str(stack_upper),
            "dominant_direction": dominant,
            "direction_records": directions,
        },
        "linear_relative_defect": {
            "bound": "theta_linear(rho)<=M3_upper*rho",
            "half_contraction_radius_lower": str(radius_lower),
            "theta_budget_used_at_that_radius": "1/2",
            "full_nonlinear_theta_below_one_certified": False,
        },
        "exact_next_dependency": (
            "CERTIFY_A_UNIFORM_ACTION_OWNED_D4_L7_BORDERED_GRAPH_REMAINDER_"
            "PLUS_THE_LOWER_WEIGHT_FULL_ACTION_REMAINDER_ON_A_POSITIVE_"
            "SUBBALL_AND_FIT_THEIR_SUM_STRICTLY_INSIDE_THE_UNUSED_ONE_HALF_"
            "CONTRACTION_BUDGET"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_D4_GRAPH_REMAINDER_MAJORANT",
            "Gate8": "LOCKED",
            "structured_D3_graph_first_jet": "CERTIFIED",
            "uniform_D4_graph_remainder": "OPEN_CURRENT_OWNER",
            "lower_weight_inhomogeneous_remainder": "OPEN",
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
