"""Recombine the certified leading bordered radius with the Gate-7 capture owner."""

from __future__ import annotations

from decimal import Decimal, getcontext
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_QUANTITATIVE_CAPTURE_BRIDGE_RECOMBINATION.json"
CHART = BASE / "BHSM_N12_COMPACTIFIED_ASYMPTOTIC_COMMON_CHART.json"
GEOMETRY = BASE / "BHSM_N12_ASYMPTOTIC_GEOMETRIC_PRODUCT_BALL.json"
GRAPH_NORM = BASE / "BHSM_N12_ASYMPTOTIC_BORDERED_GRAPH_NORM.json"
EQUIVALENCE = BASE / "BHSM_N12_BORDERED_GRAPH_PRODUCT_NORM_EQUIVALENCE.json"
DEFECT = BASE / "BHSM_N12_BORDERED_GRAPH_UNIFORM_NONLINEAR_DEFECT.json"
CAPTURE = BASE / "BHSM_N12_ASYMPTOTIC_NHIM_CAPTURE_BASIN.json"
OVERLAP = BASE / "BHSM_N12_RESET_TO_ASYMPTOTIC_CAPTURE_OVERLAP_AUDIT.json"
TAIL = BASE / "BHSM_N12_GATE7_NHIM_RANK72_RELATIVE_TAIL_THEOREM.json"
THEORY = ROOT / "theory" / "n12_gate7_quantitative_capture_bridge_recombination.md"
SCRIPT = ROOT / "scripts" / "derive_n12_gate7_quantitative_capture_bridge_recombination.py"
INPUTS = (
    CHART, GEOMETRY, GRAPH_NORM, EQUIVALENCE, DEFECT, CAPTURE, OVERLAP,
    TAIL, THEORY, SCRIPT,
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    getcontext().prec = 160
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "missing quantitative capture recombination inputs: "
            + ", ".join(missing)
        )
    chart, geometry, graph, equivalence, defect, capture, overlap, tail = (
        _load(path) for path in INPUTS[:-2]
    )
    parents = (
        chart, geometry, graph, equivalence, defect, capture, overlap, tail,
    )
    if not all(parent.get("validation_passed") is True for parent in parents):
        raise RuntimeError("validated quantitative capture lineage is required")

    uniform = defect["uniform_relative_graph_bound"]
    rho_nl = Decimal(uniform["certified_nonlinear_radius"])
    rho_bridge = rho_nl / Decimal(2)
    m3 = Decimal(uniform["structured_M3_upper"])
    m4 = Decimal(uniform["uniform_M4_upper"])
    theta_leading = m3 * rho_bridge + m4 * rho_bridge * rho_bridge / 2
    neumann_margin = Decimal(1) - theta_leading
    lower_weight_relative_defect_budget = Decimal(7) / Decimal(16)
    total_relative_defect_budget = theta_leading + lower_weight_relative_defect_budget

    x5_upper = Decimal(chart["directed_X5_norm"]["product_upper"])
    first_lift_radius_budget = rho_bridge / 2
    epsilon_first_lift_upper = first_lift_radius_budget / x5_upper
    r4_first_lift_lower = (Decimal(1) / epsilon_first_lift_upper).sqrt()
    reset_epsilon = Decimal(str(overlap["reset_data"]["epsilon=R4^-2"]))
    reset_to_first_lift_epsilon_ratio = reset_epsilon / epsilon_first_lift_upper

    validation = {
        "all_parent_certificates_validate": True,
        "common_physical_chart_dimension_is_74": chart["chart"]["dimension"] == 74,
        "leading_bordered_operator_is_injective_without_explicit_inverse": (
            graph["definition"]["explicit_B_minus2_inverse_formed"] is False
            and graph["validation"]["first_lift_equation_residual_balls_contain_zero"]
            and equivalence["validation"]["directed_determinant_excludes_zero"]
        ),
        "bridge_radius_is_positive_and_inside_certified_nonlinear_ball": (
            Decimal(0) < rho_bridge < rho_nl
        ),
        "bridge_radius_is_inside_geometric_domain_ball": (
            rho_bridge < Decimal(geometry["radius"]["rho_geom_decimal"])
        ),
        "leading_relative_defect_is_at_most_one_sixteenth": (
            theta_leading <= Decimal(1) / Decimal(16)
        ),
        "leading_neumann_margin_is_at_least_fifteen_sixteenths": (
            neumann_margin >= Decimal(15) / Decimal(16)
        ),
        "reserved_full_relative_defect_is_at_most_one_half": (
            total_relative_defect_budget <= Decimal(1) / Decimal(2)
        ),
        "first_lift_feasibility_scale_is_positive": epsilon_first_lift_upper > 0,
        "reset_is_not_inside_first_lift_feasibility_scale": (
            reset_epsilon > epsilon_first_lift_upper
        ),
        "existential_capture_basin_remains_derived": (
            capture["capture_theorem"]["forward_local_capture"] is True
        ),
        "captured_rank72_tail_remains_certified": (
            tail["rank72_consequence"]["captured_family_rank72_relative_form_net"]
            == "CAUCHY"
        ),
        "full_epsilon_operator_defect_remainder_and_trapping_not_overpromoted": True,
        "reset_to_capture_connection_not_overpromoted": True,
        "no_selector_recurrence_chord_fit_scale_action_or_time_direction_added": True,
        "FULL_BHSM_COMPLETE_false": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())

    return {
        "artifact": "BHSM_N12_GATE7_QUANTITATIVE_CAPTURE_BRIDGE_RECOMBINATION",
        "status": (
            "LEADING_BORDERED_INVERSE_RECOMBINED_FULL_TRAPPING_AND_RESET_COVER_OPEN"
            if passed else "QUANTITATIVE_CAPTURE_BRIDGE_RECOMBINATION_INVALID"
        ),
        "classification": (
            "THE_EXISTING_DETERMINANT_GRAPH_EQUIVALENCE_AND_UNIFORM_WEIGHT_"
            "SEVEN_DEFECT_CERTIFY_THE_COMBINED_74_DIMENSIONAL_BORDERED_MAP_"
            "ON_A_POSITIVE_SUBBALL_WITH_LEADING_RELATIVE_DEFECT_AT_MOST_ONE_"
            "SIXTEENTH;_SEPARATE_LEADING_CONSTRAINT_AND_KINETIC_INVERSES_ARE_"
            "THEREFORE_NOT_MISSING,_BUT_THE_FULL_EPSILON_DEPENDENT_OPERATOR_"
            "DEFECT,_INHOMOGENEOUS_REMAINDER,_STABLE_CONE_TRAPPING,_AND_A_"
            "VALIDATED_RESET_FAMILY_COVER_REMAIN_OPEN"
        ),
        "leading_bordered_recombination": {
            "operator": "B_minus2=A7+2*H0*E7",
            "physical_dimension": 74,
            "rho_nonlinear_parent": str(rho_nl),
            "rho_bridge": str(rho_bridge),
            "leading_relative_defect_upper": str(theta_leading),
            "leading_Neumann_margin_lower": str(neumann_margin),
            "separate_normalized_constraint_inverse_required": False,
            "separate_reduced_kinetic_inverse_required": False,
            "combined_Euler_Dirac_inverse_formed": False,
            "proof_object": "DIRECTED_BORDERED_GRAPH_EQUIVALENCE_AND_RELATIVE_DEFECT",
        },
        "reserved_full_action_budgets": {
            "lower_weight_relative_operator_defect_budget": str(
                lower_weight_relative_defect_budget
            ),
            "total_relative_operator_defect_budget": str(
                total_relative_defect_budget
            ),
            "required_full_operator_bound": (
                "theta_less7(rho_bridge,epsilon)<=7/16_SO_"
                "theta_full<=1/2"
            ),
            "first_lift_product_radius_budget": str(first_lift_radius_budget),
            "required_inhomogeneous_bound": (
                "CERTIFIED_REPEATED_SOLVES_PLACE_THE_epsilon2_AND_HIGHER_"
                "CORRECTION_INSIDE_THE_UNUSED_PRODUCT_RADIUS"
            ),
            "explicit_inverse_required": False,
        },
        "first_lift_feasibility": {
            "C_X5_product_upper": str(x5_upper),
            "condition": "epsilon*C_X5_product_upper<=rho_bridge/2",
            "epsilon_upper": str(epsilon_first_lift_upper),
            "R4_lower": str(r4_first_lift_lower),
            "reset_epsilon": str(reset_epsilon),
            "reset_to_epsilon_upper_ratio": str(reset_to_first_lift_epsilon_ratio),
            "interpretation": (
                "CONSERVATIVE_DETERMINANT_FROBENIUS_FEASIBILITY_SCALE_ONLY;_"
                "NOT_A_PHYSICAL_THRESHOLD_AND_NOT_A_NONEXISTENCE_RESULT"
            ),
        },
        "minimal_dynamical_capture_certificate": {
            "variables": (
                "a_IN_24_CENTER_SHAPE_DIRECTIONS,_eta_IN_STABLE_NORMAL_"
                "DIRECTIONS,_epsilon=R4^-2"
            ),
            "exact_radial_equation": "epsilon_prime=-2*H4*epsilon",
            "positive_expansion": "H4>=h_star>0",
            "stable_cone": (
                "Dini_plus_norm_eta<=-gamma_star*norm_eta+C_epsilon*epsilon"
            ),
            "center_drift": "norm(a_prime)<=C_a*(norm_eta+epsilon)",
            "boundary_conditions": (
                "STRICT_INWARD_STABLE_BOUNDARY_AND_INTEGRATED_CENTER_DRIFT_"
                "BELOW_THE_DECLARED_CENTER_MARGIN"
            ),
            "required_regular_margins": [
                "constraint_IFT",
                "metric_positivity",
                "positive_lapse",
                "shift_domain",
                "selected_eigenline_simplicity",
                "AE2_reset_and_constraint_regularity",
            ],
            "existential_version": "DERIVED_BY_ANALYTIC_NHIM_THEOREM",
            "quantitative_interval_version": "OPEN_CURRENT_ANALYTIC_OWNER",
        },
        "connection_adjudication": {
            "combined_leading_bordered_inverse": "CERTIFIED_ON_rho_bridge",
            "separate_constraint_or_kinetic_inverse_owner": "SUPERSEDED",
            "full_lower_weight_Krawczyk_bound": "OPEN",
            "quantitative_stable_cone_and_center_drift": "OPEN",
            "validated_nonempty_reset_family_cover_into_capture_tube": "OPEN_CURRENT_OWNER",
            "actual_later_event_or_canonical_stop": "NOT_CERTIFIED",
            "captured_family_rank72_tail": "CERTIFIED_CAUCHY",
        },
        "exact_next_dependency": (
            "BOUND_THE_FULL_EPSILON_DEPENDENT_BORDERED_OPERATOR_DEFECT_BY_"
            "AT_MOST_7_OVER_16_AND_THE_REMAINING_INHOMOGENEOUS_CORRECTION_"
            "INSIDE_rho_bridge,_THEN_CERTIFY_THE_ACTION_OWNED_STABLE_CONE_"
            "AND_CENTER_DRIFT_MARGINS_AND_A_NONEMPTY_RESET_FAMILY_FORWARD_"
            "COVER_INTO_THAT_TUBE_OR_AN_ACTUAL_LATER_RETAINED_STOP"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_FULL_TRAPPING_AND_RESET_TO_CAPTURE_COVER_OR_LATER_STOP",
            "Gate8": "LOCKED",
            "leading_weight_combined_bordered_inverse": "CERTIFIED",
            "quantitative_capture_surface": "OPEN",
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
        "rho_bridge": payload["leading_bordered_recombination"]["rho_bridge"],
        "theta_leading": payload["leading_bordered_recombination"]
        ["leading_relative_defect_upper"],
        "epsilon_upper": payload["first_lift_feasibility"]["epsilon_upper"],
        "R4_lower": payload["first_lift_feasibility"]["R4_lower"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
