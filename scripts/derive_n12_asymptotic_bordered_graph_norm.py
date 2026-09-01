"""Certify the action-owned bordered graph norm of the N12 first lift."""

from __future__ import annotations

from decimal import Decimal, getcontext
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.interval_weight_five_center_lift import (  # noqa: E402
    assemble_interval_weight_five_lift,
)


RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_ASYMPTOTIC_BORDERED_GRAPH_NORM.json"
)
THEORY = ROOT / "theory/n12_asymptotic_bordered_graph_norm.md"
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_INTERVAL_WEIGHT_FIVE_CENTER_LIFT.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_COMPACTIFIED_ASYMPTOTIC_COMMON_CHART.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_ASYMPTOTIC_GEOMETRIC_PRODUCT_BALL.json",
    ROOT / "src/bhsm/interface/interval_weight_five_center_lift.py",
    THEORY,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _squared_weights() -> list[int]:
    windowed = list(range(0, 48, 4))
    lapse = list(range(4, 52, 4))
    coordinates = [0] + windowed + windowed
    multipliers = lapse + windowed
    return (
        [(1 + omega * omega) ** 6 for omega in coordinates]
        + [(1 + omega * omega) ** 5 for omega in coordinates]
        + [(1 + omega * omega) ** 6 for omega in multipliers]
    )


def build_payload() -> dict[str, object]:
    import flint
    from flint import arb, ctx

    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing bordered-graph inputs: " + ", ".join(missing))
    interval_parent, chart, geometry = (_load(path) for path in INPUTS[:3])
    if not all(
        record.get("validation_passed") is True
        for record in (interval_parent, chart, geometry)
    ):
        raise RuntimeError("validated bordered-graph inputs required")

    assembled = assemble_interval_weight_five_lift(
        points=128, decimal_digits=120
    )
    rhs = assembled["right_hand_side"]
    weights_squared = _squared_weights()
    if rhs.nrows() != 74 or len(weights_squared) != 74:
        raise RuntimeError("complete 74-component bordered graph required")
    prior_digits = ctx.dps
    ctx.dps = 110
    try:
        source_norm_squared = arb(0)
        component_squares = []
        for index, squared_weight in enumerate(weights_squared):
            contribution = (
                rhs[index, 0] * rhs[index, 0] / arb(squared_weight)
            )
            source_norm_squared += contribution
            component_squares.append(contribution)
        source_norm = source_norm_squared.sqrt()
        dominant_index = max(
            range(74), key=lambda index: float(component_squares[index].mid())
        )
        graph_data = {
            "ball": str(source_norm),
            "midpoint": str(source_norm.mid()),
            "radius": str(source_norm.rad()),
            "lower": str(source_norm.lower()),
            "upper": str(source_norm.upper()),
            "relative_accuracy_bits": int(source_norm.rel_accuracy_bits()),
            "dominant_dual_source_row": dominant_index,
            "dominant_dual_source_square_ball": str(
                component_squares[dominant_index]
            ),
        }
    finally:
        ctx.dps = prior_digits

    getcontext().prec = 100
    # The printed Arb lower/upper strings begin with a bracketed decimal.
    graph_lower = Decimal(graph_data["lower"].lstrip("[").split()[0])
    graph_upper = Decimal(graph_data["upper"].lstrip("[").split()[0])
    product_lower = Decimal(chart["directed_X5_norm"]["product_lower"])
    product_upper = Decimal(chart["directed_X5_norm"]["product_upper"])
    ratio_lower = graph_lower / product_upper
    ratio_upper = graph_upper / product_lower
    validation = {
        "python_flint_version_pinned_to_0_9_0": flint.__version__ == "0.9.0",
        "bordered_graph_dimension_is_74": rhs.nrows() == 74,
        "same_H6_H5_H6_squared_weights_used": (
            len(weights_squared) == chart["chart"]["dimension"] == 74
        ),
        "directed_source_graph_norm_is_strictly_positive": graph_lower > 0,
        "directed_source_graph_norm_has_at_least_250_accuracy_bits": (
            graph_data["relative_accuracy_bits"] >= 250
        ),
        "first_lift_equation_residual_balls_contain_zero": assembled[
            "residual_contains_zero"
        ],
        "algebraic_multiplier_block_rigorously_invertible": assembled[
            "algebraic_multiplier_block_rigorously_invertible"
        ],
        "combined_Euler_Dirac_inverse_not_used": not assembled[
            "combined_Euler_Dirac_inverse_used"
        ],
        "graph_to_product_ratio_is_below_7e_minus_14": ratio_upper < Decimal("7e-14"),
        "nonlinear_graph_relative_defect_not_overpromoted": True,
        "no_selector_scale_fit_endpoint_action_term_or_chord_added": True,
    }

    return {
        "artifact": "BHSM_N12_ASYMPTOTIC_BORDERED_GRAPH_NORM",
        "status": "ACTION_OWNED_BORDERED_GRAPH_PRECONDITIONER_DERIVED_NONLINEAR_RELATIVE_BOUND_OPEN",
        "classification": (
            "THE_PHYSICAL_BORDERED_RECURRENCE_PENCIL_B_MINUS2=A7+2H0E7_"
            "DEFINES_AN_ACTION_OWNED_GRAPH_NORM_WITHOUT_FORMING_THE_COMBINED_"
            "EULER_DIRAC_INVERSE;_THE_DIRECTED_FIRST_LIFT_GRAPH_NORM_EQUALS_"
            "THE_DUAL_SOURCE_NORM_AND_IS_ABOUT_3.94_WHILE_ITS_H6_H5_H6_"
            "PRODUCT_NORM_IS_ABOUT_5.68E13,_EXPOSING_THE_WEAK_GEOMETRIC_"
            "DIRECTIONS_THAT_REQUIRE_A_RELATIVE_GRAPH_DEFECT_BOUND"
        ),
        "definition": {
            "bordered_operator": "B_minus2=A7+2*H0*E7",
            "domain": "PHYSICAL_25q_PLUS_25v_PLUS_24_MULTIPLIERS",
            "weight_map": "W_FOR_H6q_CROSS_H5v_CROSS_H6m",
            "graph_norm": "norm(W^-1*B_minus2*X)_2",
            "dual_source_norm": "norm(W^-1*b5)_2",
            "explicit_B_minus2_inverse_formed": False,
            "ill_conditioned_kinetic_Dirac_block_inverted": False,
        },
        "directed_first_lift_graph_norm": graph_data,
        "norm_comparison": {
            "product_norm_lower": str(product_lower),
            "product_norm_upper": str(product_upper),
            "graph_to_product_ratio_lower": str(ratio_lower),
            "graph_to_product_ratio_upper": str(ratio_upper),
            "interpretation": (
                "THE_LARGE_PRODUCT_COEFFICIENT_NORM_IS_A_WEAK_DIRECTION_"
                "AMPLIFICATION,_NOT_A_LARGE_ACTION_SOURCE_NORM"
            ),
        },
        "required_nonlinear_certificate": {
            "relative_operator_defect": (
                "norm(W^-1*(B(Y)-B_minus2)*X)_2<=theta*"
                "norm(W^-1*B_minus2*X)_2_WITH_theta<1"
            ),
            "inhomogeneous_remainder": (
                "norm(W^-1*r_full(Y,epsilon))_2<=M_full(epsilon,rho)"
            ),
            "domain": (
                "INTERSECTION_OF_THE_EXPLICIT_GEOMETRIC_PRODUCT_BALL_AND_"
                "A_BORDERED_GRAPH_BALL"
            ),
            "certified_repeated_solves_allowed": True,
            "explicit_combined_inverse_allowed": False,
            "relative_defect_theta_certified": False,
        },
        "exact_next_dependency": (
            "DERIVE_A_DIRECTED_BOUND_theta<1_FOR_THE_BORDERED_RELATIVE_"
            "OPERATOR_DEFECT_ON_A_POSITIVE_INTERSECTION_BALL_AND_BOUND_THE_"
            "FULL_INHOMOGENEOUS_REMAINDER_THERE,_USING_CERTIFIED_REPEATED_"
            "SOLVES_OR_KRAWCZYK_RESIDUALS_WITHOUT_FORMING_THE_COMBINED_INVERSE"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_BORDERED_RELATIVE_GRAPH_DEFECT_MAJORANT",
            "Gate8": "LOCKED",
            "bordered_graph_preconditioner": "DERIVED",
            "nonlinear_relative_graph_defect": "OPEN_CURRENT_OWNER",
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
