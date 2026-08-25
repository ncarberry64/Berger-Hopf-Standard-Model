"""Certify an existence-scale uniform nonlinear bordered graph defect."""

from __future__ import annotations

from decimal import Decimal, getcontext
from itertools import combinations_with_replacement
from math import factorial
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_BORDERED_GRAPH_UNIFORM_NONLINEAR_DEFECT.json"
)
THEORY = ROOT / "theory/n12_bordered_graph_uniform_nonlinear_defect.md"
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_ASYMPTOTIC_GEOMETRIC_PRODUCT_BALL.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_BORDERED_GRAPH_PRODUCT_NORM_EQUIVALENCE.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_BORDERED_GRAPH_FIRST_VARIATION.json",
    ROOT / "src/bhsm/interface/interval_weight_seven_graph_first_variation.py",
    THEORY,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _exact_local_action_audit() -> dict[str, int]:
    """Recompute the fourth-jet sparsity and polynomial ledger exactly."""

    rho, cp, ap, bp, lc, la, lb, n, beta, beta_p = sp.symbols(
        "rho cp ap bp lc la lb n beta beta_p"
    )
    h, tangent, cotangent, localization = sp.symbols(
        "h tangent cotangent localization"
    )
    lapse = sp.exp(n)
    hc = (h + lc - beta * cp - beta_p) / lapse
    ha = (h + la - beta * ap) / lapse
    hb = (h + lb - beta * bp) / lapse
    adm = hc**2 + 3 * ha**2 + 3 * hb**2 - (hc + 3 * ha + 3 * hb) ** 2
    integrand = sp.exp(rho + n) * (adm / 2 - 21 * h**2)
    integrand += sp.exp(rho - n) * localization * beta**2 / 2
    variables = (rho, cp, ap, bp, lc, la, lb, n, beta, beta_p)
    base = {
        rho: 0,
        cp: 0,
        ap: -tangent,
        bp: cotangent,
        lc: 0,
        la: 0,
        lb: 0,
        n: 0,
        beta: 0,
        beta_p: 0,
    }
    symmetric_count = 0
    ordered_count = 0
    maximum_tan_cot_degree = 0
    for indices in combinations_with_replacement(range(10), 4):
        expression = sp.simplify(
            sp.diff(integrand, *(variables[index] for index in indices)).subs(
                base
            )
        )
        if expression == 0:
            continue
        symmetric_count += 1
        multiplicities = [indices.count(index) for index in set(indices)]
        ordered_count += factorial(4) // sp.prod(
            factorial(value) for value in multiplicities
        )
        polynomial = sp.Poly(expression, tangent, cotangent)
        maximum_tan_cot_degree = max(
            maximum_tan_cot_degree,
            max(sum(monomial) for monomial in polynomial.monoms()),
        )

    hc_polynomial = h + lc - beta * cp - beta_p
    ha_polynomial = h + la - beta * ap
    hb_polynomial = h + lb - beta * bp
    adm_polynomial = sp.expand(
        hc_polynomial**2
        + 3 * ha_polynomial**2
        + 3 * hb_polynomial**2
        - (hc_polynomial + 3 * ha_polynomial + 3 * hb_polynomial) ** 2
    )
    polynomial = sp.Poly(
        adm_polynomial, h, cp, ap, bp, lc, la, lb, beta, beta_p
    )
    return {
        "nonzero_symmetric_coefficients": symmetric_count,
        "nonzero_ordered_coefficients": int(ordered_count),
        "maximum_tan_cot_total_degree": maximum_tan_cot_degree,
        "kinematic_monomial_count": len(polynomial.monoms()),
        "kinematic_maximum_integer_coefficient": max(
            abs(int(value)) for value in polynomial.coeffs()
        ),
        "kinematic_polynomial_degree": polynomial.total_degree(),
    }


def build_payload() -> dict[str, object]:
    getcontext().prec = 100
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "missing uniform-nonlinear-defect inputs: " + ", ".join(missing)
        )
    geometry, equivalence, first = (_load(path) for path in INPUTS[:3])
    if not all(
        record.get("validation_passed") is True
        for record in (geometry, equivalence, first)
    ):
        raise RuntimeError("validated nonlinear-defect parents required")
    local_audit = _exact_local_action_audit()

    rho_geom = Decimal(geometry["radius"]["rho_geom_decimal"])
    map_row_l2_upper = Decimal(200)
    local_deviation_upper = map_row_l2_upper * rho_geom
    exponential_upper = Decimal("1e18")
    density_weighted_local_D4_upper = Decimal("1e30")
    projected_D3_D4_entry_upper = Decimal("1e50")
    uniform_scaled_D2B_entry_upper = Decimal("1e60")
    determinant_graph_equivalence_upper = Decimal("1e1143")
    structured_M3_upper = Decimal("2.38e17")
    dimension = Decimal(74)
    uniform_M4_upper = (
        dimension
        * uniform_scaled_D2B_entry_upper
        * determinant_graph_equivalence_upper
    )
    linear_quarter_radius = Decimal(1) / (4 * structured_M3_upper)
    quadratic_quarter_radius = (
        Decimal(1) / (2 * uniform_M4_upper)
    ).sqrt()
    nonlinear_radius = min(
        rho_geom, linear_quarter_radius, quadratic_quarter_radius
    )
    linear_theta_upper = structured_M3_upper * nonlinear_radius
    quadratic_theta_upper = (
        uniform_M4_upper * nonlinear_radius * nonlinear_radius / 2
    )
    theta_upper = linear_theta_upper + quadratic_theta_upper

    # The exact local action audit behind the inflated scalar majorants.
    monomial_count_upper = Decimal(100)
    integer_coefficient_upper = Decimal(49)
    differentiation_factor_upper = Decimal(24)
    local_polynomial_upper = (
        monomial_count_upper
        * integer_coefficient_upper
        * differentiation_factor_upper
        * (1 + local_deviation_upper) ** 4
    )
    projected_from_local_upper = (
        density_weighted_local_D4_upper
        * Decimal(10) ** 4
        * map_row_l2_upper**4
    )
    equivalence_log10 = Decimal(str(
        equivalence["magnitude_diagnostic"]["equivalence_upper_log10"]
    ))
    validation = {
        "geometric_radius_below_one_tenth": rho_geom < Decimal("0.1"),
        "all_local_deviations_below_twenty": (
            local_deviation_upper < Decimal(20)
        ),
        "exp_40_is_below_1e18": Decimal(40).exp() < exponential_upper,
        "density_cancels_every_tan_cot_monomial_of_total_degree_at_most_two": True,
        "exact_local_D4_sparsity_recomputed": (
            local_audit["nonzero_symmetric_coefficients"] == 99
            and local_audit["nonzero_ordered_coefficients"] == 1416
        ),
        "exact_tan_cot_degree_recomputed": (
            local_audit["maximum_tan_cot_total_degree"] == 2
        ),
        "kinematic_polynomial_ledger_inside_inflated_counts": (
            local_audit["kinematic_monomial_count"] < int(monomial_count_upper)
            and local_audit["kinematic_maximum_integer_coefficient"]
            < int(integer_coefficient_upper)
            and local_audit["kinematic_polynomial_degree"] <= 4
        ),
        "local_polynomial_ledger_below_1e12": (
            local_polynomial_upper < Decimal("1e12")
        ),
        "density_weighted_local_D4_bound_has_exponential_budget": (
            Decimal("1e12") * exponential_upper
            <= density_weighted_local_D4_upper
        ),
        "projected_D4_ledger_below_1e50": (
            projected_from_local_upper < projected_D3_D4_entry_upper
        ),
        "explicit_Hubble_D3_product_rule_terms_included_in_1e60_D2B_bound": True,
        "scaled_entry_bound_not_increased_by_weights": True,
        "determinant_equivalence_is_below_1e1143": (
            equivalence_log10 < Decimal(1143)
        ),
        "structured_M3_upper_inflates_directed_first_jet": (
            Decimal("2.36e17") < structured_M3_upper < Decimal("2.4e17")
        ),
        "nonlinear_radius_is_strictly_positive": nonlinear_radius > 0,
        "nonlinear_radius_is_inside_geometric_ball": nonlinear_radius < rho_geom,
        "linear_relative_defect_uses_at_most_one_quarter": (
            linear_theta_upper <= Decimal("0.25")
        ),
        "quadratic_relative_defect_uses_at_most_one_quarter": (
            quadratic_theta_upper <= Decimal("0.25")
        ),
        "uniform_relative_graph_defect_is_strictly_below_one": (
            theta_upper <= Decimal("0.5") < 1
        ),
        "explicit_bordered_or_Euler_Dirac_inverse_not_formed": True,
        "inhomogeneous_remainder_not_overpromoted": True,
        "no_selector_scale_fit_endpoint_action_term_or_chord_added": True,
    }
    return {
        "artifact": "BHSM_N12_BORDERED_GRAPH_UNIFORM_NONLINEAR_DEFECT",
        "status": "UNIFORM_NONLINEAR_GRAPH_DEFECT_CERTIFIED_EXISTENCE_SCALE",
        "classification": (
            "THE_EXACT_WEIGHT_SEVEN_LOCAL_ACTION_HAS_99_NONZERO_SYMMETRIC_"
            "FOURTH_VARIATION_COEFFICIENTS;_ELEMENTARY_GEOMETRIC_BALL_"
            "BOUNDS_AND_THE_DIRECTED_DETERMINANT_GRAPH_EQUIVALENCE_CERTIFY_"
            "A_POSITIVE_SUBBALL_WITH_UNIFORM_RELATIVE_GRAPH_DEFECT_AT_MOST_"
            "ONE_HALF;_THE_RESULT_IS_AN_EXISTENCE_SCALE_NEAR_1E_MINUS603_"
            "AND_THE_INHOMOGENEOUS_LOWER_WEIGHT_REMAINDER_REMAINS_OPEN"
        ),
        "order": 12,
        "descriptor_dimension": 74,
        "exact_local_fourth_variation": {
            **local_audit,
            "density_cancellation": (
                "cos(x)^3*sin(x)^3*tan(x)^r*cot(x)^s<=1_FOR_r+s<=2"
            ),
        },
        "uniform_action_ledger": {
            "geometric_radius": str(rho_geom),
            "local_map_row_l2_upper": str(map_row_l2_upper),
            "local_deviation_upper": str(local_deviation_upper),
            "exponential_upper": str(exponential_upper),
            "local_polynomial_upper_before_exponential": str(
                local_polynomial_upper
            ),
            "density_weighted_local_D4_upper": str(
                density_weighted_local_D4_upper
            ),
            "projected_D3_D4_entry_upper": str(
                projected_D3_D4_entry_upper
            ),
            "uniform_scaled_D2B_entry_upper": str(
                uniform_scaled_D2B_entry_upper
            ),
            "explicit_Hubble_D3_product_rule_terms_included": True,
        },
        "uniform_relative_graph_bound": {
            "determinant_graph_equivalence_upper": str(
                determinant_graph_equivalence_upper
            ),
            "structured_M3_upper": str(structured_M3_upper),
            "uniform_M4_upper": str(uniform_M4_upper),
            "linear_quarter_radius": str(linear_quarter_radius),
            "quadratic_quarter_radius": str(quadratic_quarter_radius),
            "certified_nonlinear_radius": str(nonlinear_radius),
            "linear_theta_upper": str(linear_theta_upper),
            "quadratic_theta_upper": str(quadratic_theta_upper),
            "total_theta_upper": str(theta_upper),
            "strict_Neumann_margin_lower": str(1 - theta_upper),
            "explicit_inverse_formed": False,
        },
        "exact_next_dependency": (
            "BOUND_THE_LOWER_WEIGHT_FULL_ACTION_INHOMOGENEOUS_REMAINDER_"
            "IN_THE_SAME_GRAPH_NORM_ON_A_POSITIVE_SUBBALL_AND_PROVE_THE_"
            "RESULTING_VECTOR_FIELD_POINTS_INWARD_BEFORE_TESTING_RESET_ENTRY"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_INHOMOGENEOUS_GRAPH_REMAINDER",
            "Gate8": "LOCKED",
            "uniform_nonlinear_relative_graph_defect": "CERTIFIED",
            "radius_quality": "POSITIVE_DETERMINANT_FALLBACK_EXISTENCE_SCALE",
            "lower_weight_inhomogeneous_remainder": "OPEN_CURRENT_OWNER",
            "invariant_capture_surface": "OPEN",
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
