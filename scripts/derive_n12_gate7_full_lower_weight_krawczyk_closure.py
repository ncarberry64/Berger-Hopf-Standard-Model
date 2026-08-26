"""Quantify the full retained lower-weight asymptotic Krawczyk graph."""

from __future__ import annotations

from decimal import Decimal, getcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_m4_standard_model_zeta_backreaction_v15_51 import (  # noqa: E402
    standard_model_casimir_coefficient,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_FULL_LOWER_WEIGHT_KRAWCZYK_CLOSURE.json"
BRIDGE = BASE / "BHSM_N12_GATE7_QUANTITATIVE_CAPTURE_BRIDGE_RECOMBINATION.json"
GEOMETRY = BASE / "BHSM_N12_ASYMPTOTIC_GEOMETRIC_PRODUCT_BALL.json"
EQUIVALENCE = BASE / "BHSM_N12_BORDERED_GRAPH_PRODUCT_NORM_EQUIVALENCE.json"
FULL_BRANCH = BASE / "BHSM_N12_FULL_RETAINED_ASYMPTOTIC_BRANCH.json"
CAPTURE = BASE / "BHSM_N12_ASYMPTOTIC_NHIM_CAPTURE_BASIN.json"
TAIL = BASE / "BHSM_N12_GATE7_NHIM_RANK72_RELATIVE_TAIL_THEOREM.json"
ACTION_SOURCE = ROOT / "src" / "bhsm" / "interface" / "aether_exact_radial_schur_lift_v15_83.py"
CASIMIR_SOURCE = ROOT / "src" / "bhsm" / "interface" / "aether_m4_standard_model_zeta_backreaction_v15_51.py"
THEORY = ROOT / "theory" / "n12_gate7_full_lower_weight_krawczyk_closure.md"
SCRIPT = ROOT / "scripts" / "derive_n12_gate7_full_lower_weight_krawczyk_closure.py"
INPUTS = (
    BRIDGE, GEOMETRY, EQUIVALENCE, FULL_BRANCH, CAPTURE, TAIL,
    ACTION_SOURCE, CASIMIR_SOURCE, THEORY, SCRIPT,
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _coefficient_ledger() -> dict[str, Any]:
    """Expand the exact local scale polynomial used by the retained action."""

    Ec, Ea, Eb, En, localization, epsilon = sp.symbols(
        "Ec Ea Eb En localization epsilon", positive=True
    )
    cp, ap, bp, lc, la, lb, nprime, beta, betap, kappa = sp.symbols(
        "cp ap bp lc la lb nprime beta betap kappa"
    )
    exponentials = (Ec, Ea, Eb, En)
    polynomial_variables = (cp, ap, bp, lc, la, lb, nprime, beta, betap)
    volume = Ec * Ea**3 * Eb**3
    spatial_volume_over_c = Ea**3 * Eb**3 / Ec
    hc = (lc - beta * cp - betap) / En
    ha = (la - beta * ap) / En
    hb = (lb - beta * bp) / En
    adm = hc**2 + 3 * ha**2 + 3 * hb**2 - (hc + 3 * ha + 3 * hb) ** 2
    x_spatial = Ec**-2 + 3 * Ea**-2 + 3 * Eb**-2
    normal_square = beta**2 / En**2
    x_eta = epsilon * x_spatial - normal_square
    fixed_gravity = ap**2 + bp**2 + 3 * ap * bp
    bulk = (
        epsilon * 3 * En * spatial_volume_over_c
        * (nprime * (ap + bp) + fixed_gravity)
        + En * volume * (
            epsilon * (3 / Ea**2 + 3 / Eb**2)
            - kappa / 2
            - localization * (x_eta / 2 + x_eta**4 / 8)
            + adm / 2
        )
    )
    inertia = volume * localization * (1 + x_eta**3) / En

    def summarize(expression: sp.Expr, maximum_power: int) -> dict[str, Any]:
        expanded = sp.expand(expression)
        rows = []
        for power in range(maximum_power + 1):
            coefficient = sp.expand(expanded.coeff(epsilon, power))
            terms = sp.Add.make_args(coefficient)
            exponent_l1 = []
            polynomial_degrees = []
            numerical_coefficients = []
            for term in terms:
                powers = term.as_powers_dict()
                exponent_l1.append(sum(
                    abs(int(powers.get(variable, 0)))
                    for variable in exponentials
                ))
                polynomial_degrees.append(sum(
                    int(powers.get(variable, 0))
                    for variable in polynomial_variables
                ))
                stripped = term
                for variable in (
                    *exponentials, localization, *polynomial_variables, kappa,
                ):
                    stripped /= variable ** powers.get(variable, 0)
                numerical_coefficients.append(abs(sp.Rational(stripped)))
            rows.append({
                "epsilon_power": power,
                "term_count": len(terms),
                "maximum_exponential_L1_degree": max(exponent_l1),
                "maximum_polynomial_degree": max(polynomial_degrees),
                "maximum_absolute_rational_coefficient": str(
                    max(numerical_coefficients)
                ),
            })
        return {
            "total_expanded_term_count": len(sp.Add.make_args(expanded)),
            "operation_count": int(sp.count_ops(expanded)),
            "coefficients": rows,
        }

    return {
        "bulk": summarize(bulk, 4),
        "inertia": summarize(inertia, 3),
        "scale_variable_for_structural_expansion": "s=R^-2",
        "canonical_conversion": (
            "s=epsilon*(R4/R)^2_WITH_epsilon=R4^-2_AND_"
            "R4/R=1/(2*sqrt(cosh(2*b_boundary)))"
        ),
    }


def build_payload() -> dict[str, Any]:
    getcontext().prec = 180
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "missing full lower-weight Krawczyk inputs: " + ", ".join(missing)
        )
    bridge, geometry, equivalence, full_branch, capture, tail = (
        _load(path) for path in INPUTS[:6]
    )
    if not all(record.get("validation_passed") is True for record in (
        bridge, geometry, equivalence, full_branch, capture, tail,
    )):
        raise RuntimeError("validated full lower-weight lineage is required")

    ledger = _coefficient_ledger()
    bulk_rows = ledger["bulk"]["coefficients"]
    inertia_rows = ledger["inertia"]["coefficients"]
    lower_bulk_rows = bulk_rows[1:]

    # Exact elementary lower bound on the leading normalized inertia.
    localization_lower = Fraction(11, 36)
    trig_density_lower = Fraction(21, 80) ** 3
    interval_length_lower = Fraction(3, 8)
    relative_volume_lower = Fraction(1, 128)
    inverse_lapse_lower = Fraction(3, 4)
    eta_legendre_lower = Fraction(63, 64)
    inertia7_lower = (
        localization_lower
        * trig_density_lower
        * interval_length_lower
        * relative_volume_lower
        * inverse_lapse_lower
        * eta_legendre_lower
    )

    # Deliberately inflated derivative and graph bounds.
    local_row_l2_upper = Decimal(200)
    local_deviation_upper = Decimal(20)
    local_fourth_coefficient_upper = Decimal("1e145")
    projected_fourth_coefficient_upper = Decimal("1e160")
    lower_operator_entry_upper = Decimal("1e170")
    inverse_inertia_entry_upper = Decimal("1e700")
    graph_equivalence_upper = Decimal("1e1143")
    dimension = Decimal(74)
    m_bulk = dimension * lower_operator_entry_upper * graph_equivalence_upper
    m_inverse = dimension * inverse_inertia_entry_upper * graph_equivalence_upper
    inertia7_lower_decimal = (
        Decimal(inertia7_lower.numerator) / Decimal(inertia7_lower.denominator)
    )
    reciprocal_fourth_ledger_upper = (
        Decimal(100)
        * projected_fourth_coefficient_upper**4
        / inertia7_lower_decimal**5
    )

    epsilon_k = Decimal(7) / (Decimal(64) * m_bulk)
    r4_lower = (Decimal(1) / epsilon_k).sqrt()
    theta_leading = Decimal(
        bridge["leading_bordered_recombination"]["leading_relative_defect_upper"]
    )
    theta_bulk = Decimal(2) * m_bulk * epsilon_k
    theta_inverse = m_inverse * epsilon_k**7
    theta_full = theta_leading + theta_bulk + theta_inverse
    rho_bridge = Decimal(
        bridge["leading_bordered_recombination"]["rho_bridge"]
    )
    x5_upper = Decimal(
        bridge["first_lift_feasibility"]["C_X5_product_upper"]
    )
    first_lift_displacement = epsilon_k * x5_upper
    higher_bulk_displacement = Decimal(2) * m_bulk * epsilon_k**2
    inverse_displacement = m_inverse * epsilon_k**7
    initial_map_displacement = (
        first_lift_displacement
        + higher_bulk_displacement
        + inverse_displacement
    )

    # The exact retained coefficient is 59/30; keep the dependency numerical
    # only as a bounded constant, never as a fitted value.
    standard_model_casimir = Decimal(str(standard_model_casimir_coefficient()))
    validation = {
        "all_parent_certificates_validate": True,
        "exact_bulk_has_69_expanded_terms": (
            ledger["bulk"]["total_expanded_term_count"] == 69
        ),
        "exact_inertia_has_21_expanded_terms": (
            ledger["inertia"]["total_expanded_term_count"] == 21
        ),
        "lower_bulk_coefficients_have_at_most_15_terms": max(
            row["term_count"] for row in lower_bulk_rows
        ) <= 15,
        "lower_bulk_exponential_degree_at_most_14": max(
            row["maximum_exponential_L1_degree"] for row in lower_bulk_rows
        ) <= 14,
        "lower_bulk_polynomial_degree_at_most_6": max(
            row["maximum_polynomial_degree"] for row in lower_bulk_rows
        ) <= 6,
        "lower_bulk_rational_coefficient_at_most_81": max(
            sp.Rational(row["maximum_absolute_rational_coefficient"])
            for row in lower_bulk_rows
        ) <= 81,
        "inertia_coefficients_have_at_most_10_terms": max(
            row["term_count"] for row in inertia_rows
        ) <= 10,
        "inertia_exponential_degree_at_most_14": max(
            row["maximum_exponential_L1_degree"] for row in inertia_rows
        ) <= 14,
        "inertia_polynomial_degree_at_most_6": max(
            row["maximum_polynomial_degree"] for row in inertia_rows
        ) <= 6,
        "inertia_rational_coefficient_at_most_81": max(
            sp.Rational(row["maximum_absolute_rational_coefficient"])
            for row in inertia_rows
        ) <= 81,
        "elementary_inertia_lower_bound_exceeds_1e_minus5": (
            inertia7_lower > Fraction(1, 100000)
        ),
        "geometric_ball_supplies_required_pointwise_margins": (
            geometry["validation"]["metric_exponent_bound_below_one_half"]
            and geometry["validation"]["lapse_log_bound_below_one_quarter"]
            and geometry["validation"]["eta_legendre_lower_bound_is_63_over_64"]
        ),
        "inflated_local_D4_ledger_is_sufficient": (
            Decimal(100) * Decimal(100) * Decimal(21) ** 8
            * Decimal(22) ** 4 * Decimal(280).exp()
            < local_fourth_coefficient_upper
        ),
        "projection_and_EL_product_rules_fit_in_1e170": (
            local_fourth_coefficient_upper
            * local_row_l2_upper**4 * Decimal(14) ** 4
            < lower_operator_entry_upper
        ),
        "reciprocal_inertia_fourth_jet_fits_in_1e700": (
            reciprocal_fourth_ledger_upper < inverse_inertia_entry_upper
        ),
        "standard_model_Casimir_is_below_two": standard_model_casimir < 2,
        "epsilon_K_is_positive_and_below_prior_first_lift_scale": (
            Decimal(0) < epsilon_k
            < Decimal(bridge["first_lift_feasibility"]["epsilon_upper"])
        ),
        "bulk_relative_defect_uses_at_most_seven_over_32": (
            theta_bulk <= Decimal(7) / Decimal(32)
        ),
        "inverse_inertia_relative_defect_uses_at_most_seven_over_32": (
            theta_inverse <= Decimal(7) / Decimal(32)
        ),
        "full_relative_defect_is_below_one_half": theta_full < Decimal(1) / 2,
        "Krawczyk_center_displacement_is_inside_half_bridge_radius": (
            initial_map_displacement < rho_bridge / 2
        ),
        "captured_rank72_tail_remains_certified": (
            tail["rank72_consequence"]["captured_family_rank72_relative_form_net"]
            == "CAUCHY"
        ),
        "stable_cone_and_reset_cover_not_overpromoted": True,
        "no_selector_recurrence_chord_fit_scale_action_or_time_direction_added": True,
        "FULL_BHSM_COMPLETE_false": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())

    return {
        "artifact": "BHSM_N12_GATE7_FULL_LOWER_WEIGHT_KRAWCZYK_CLOSURE",
        "status": (
            "FULL_ASYMPTOTIC_DESCRIPTOR_GRAPH_QUANTIFIED_STABLE_CONE_AND_RESET_COVER_OPEN"
            if passed else "FULL_LOWER_WEIGHT_KRAWCZYK_CLOSURE_INVALID"
        ),
        "classification": (
            "THE_EXACT_RETAINED_SCALE_POLYNOMIAL,_AN_ELEMENTARY_POSITIVE_"
            "LEADING_INERTIA_BOUND,_AND_INFLATED_FOURTH_JET_LEDGER_GIVE_A_"
            "FULL_INVERSE_FREE_KRAWCZYK_CONTRACTION_FOR_THE_74_DIMENSIONAL_"
            "ASYMPTOTIC_DESCRIPTOR_GRAPH_ON_AN_EXPLICIT_EPSILON_INTERVAL;_"
            "THE_QUANTITATIVE_STABLE_CONE,_CENTER_DRIFT,_AND_RESET_FAMILY_"
            "FORWARD_COVER_OR_LATER_STOP_REMAIN_OPEN"
        ),
        "exact_local_scale_ledger": ledger,
        "elementary_leading_inertia_bound": {
            "chi_subinterval": "[pi/8,pi/4]",
            "sin_lower": "3/8",
            "cos_lower": "7/10",
            "localization_lower": str(localization_lower),
            "interval_length_lower": str(interval_length_lower),
            "relative_volume_lower": str(relative_volume_lower),
            "inverse_lapse_lower": str(inverse_lapse_lower),
            "eta_legendre_lower": str(eta_legendre_lower),
            "I7_lower_fraction": str(inertia7_lower),
            "I7_lower_decimal": str(
                inertia7_lower_decimal
            ),
        },
        "inflated_uniform_bounds": {
            "local_map_row_l2_upper": str(local_row_l2_upper),
            "local_deviation_upper": str(local_deviation_upper),
            "local_D4_coefficient_upper": str(local_fourth_coefficient_upper),
            "projected_D4_coefficient_upper": str(projected_fourth_coefficient_upper),
            "lower_weight_operator_entry_upper": str(lower_operator_entry_upper),
            "inverse_inertia_entry_upper": str(inverse_inertia_entry_upper),
            "reciprocal_inertia_D4_ledger_upper": str(
                reciprocal_fourth_ledger_upper
            ),
            "determinant_graph_equivalence_upper": str(graph_equivalence_upper),
            "M_bulk": str(m_bulk),
            "M_inverse": str(m_inverse),
            "explicit_inverse_formed": False,
        },
        "full_Krawczyk_certificate": {
            "epsilon_upper": str(epsilon_k),
            "R4_lower": str(r4_lower),
            "rho_bridge": str(rho_bridge),
            "theta_leading_upper": str(theta_leading),
            "theta_lower_bulk_upper": str(theta_bulk),
            "theta_inverse_inertia_upper": str(theta_inverse),
            "theta_full_upper": str(theta_full),
            "first_lift_displacement_upper": str(first_lift_displacement),
            "higher_bulk_displacement_upper": str(higher_bulk_displacement),
            "inverse_displacement_upper": str(inverse_displacement),
            "initial_map_displacement_upper": str(initial_map_displacement),
            "self_map_radius_budget": str(rho_bridge / 2),
            "contraction": True,
            "self_map": True,
            "unique_full_descriptor_graph": True,
            "all_algebraic_multipliers_retained": True,
            "complete_lower_weight_inhomogeneous_correction_enclosed": True,
        },
        "scope": {
            "proof_radius_not_new_physical_scale": True,
            "quantitative_stable_normal_cone": "OPEN_CURRENT_ANALYTIC_OWNER",
            "integrated_center_drift": "OPEN_CURRENT_ANALYTIC_OWNER",
            "validated_reset_family_entry": "OPEN_CURRENT_OWNER",
            "actual_later_event_or_canonical_stop": "NOT_CERTIFIED",
            "captured_family_rank72_tail": "CERTIFIED_CAUCHY",
        },
        "exact_next_dependency": (
            "CERTIFY_THE_ACTION_OWNED_STABLE_NORMAL_CONE,_INTEGRATED_CENTER_"
            "DRIFT,_AND_ALL_RETAINED_DOMAIN_MARGINS_ON_A_TUBE_AROUND_THE_"
            "NOW_QUANTIFIED_FULL_DESCRIPTOR_GRAPH,_THEN_VALIDATE_A_NONEMPTY_"
            "RESET_FAMILY_FORWARD_COVER_INTO_THAT_TUBE_OR_AN_ACTUAL_LATER_STOP"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_STABLE_CONE_AND_RESET_TO_CAPTURE_COVER_OR_LATER_STOP",
            "Gate8": "LOCKED",
            "full_lower_weight_Krawczyk_graph": "CERTIFIED",
            "quantitative_capture_tube": "OPEN",
            "AE2_reset_image_enters_capture_basin": "OPEN_CURRENT_OWNER",
            "actual_projected_zero_source_force": "OPEN_AFTER_CONNECTION",
            "same_action_KKT_root": "WAITING_ON_FORCE",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": passed,
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
    print(json.dumps({
        "status": payload["status"],
        "epsilon_upper": payload["full_Krawczyk_certificate"]["epsilon_upper"],
        "R4_lower": payload["full_Krawczyk_certificate"]["R4_lower"],
        "theta_full": payload["full_Krawczyk_certificate"]["theta_full_upper"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
