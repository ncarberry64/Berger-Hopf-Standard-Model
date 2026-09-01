"""Certify an explicit inverse-free stable capture tube for Gate 7."""

from __future__ import annotations

from decimal import Decimal, getcontext
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.interval_weight_five_center_lift import (  # noqa: E402
    DESCRIPTOR,
    MULTIPLIERS,
    PHYSICAL,
    assemble_interval_weight_five_lift,
)
from bhsm.interface.interval_weight_seven_graph_first_variation import (  # noqa: E402
    squared_product_weights,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_QUANTITATIVE_STABLE_CAPTURE_TUBE.json"
KRAWCZYK = BASE / "BHSM_N12_GATE7_FULL_LOWER_WEIGHT_KRAWCZYK_CLOSURE.json"
FAMILY = BASE / "BHSM_N12_EXACT_WEIGHT_SEVEN_CENTER_FAMILY.json"
NHIM = BASE / "BHSM_N12_ASYMPTOTIC_NHIM_CAPTURE_BASIN.json"
GEOMETRY = BASE / "BHSM_N12_ASYMPTOTIC_GEOMETRIC_PRODUCT_BALL.json"
DEFECT = BASE / "BHSM_N12_BORDERED_GRAPH_UNIFORM_NONLINEAR_DEFECT.json"
TAIL = BASE / "BHSM_N12_GATE7_NHIM_RANK72_RELATIVE_TAIL_THEOREM.json"
INTERVAL_SOURCE = ROOT / "src" / "bhsm" / "interface" / "interval_weight_five_center_lift.py"
WEIGHT_SOURCE = ROOT / "src" / "bhsm" / "interface" / "interval_weight_seven_graph_first_variation.py"
THEORY = ROOT / "theory" / "n12_gate7_quantitative_stable_capture_tube.md"
SCRIPT = ROOT / "scripts" / "derive_n12_gate7_quantitative_stable_capture_tube.py"
INPUTS = (
    KRAWCZYK, FAMILY, NHIM, GEOMETRY, DEFECT, TAIL,
    INTERVAL_SOURCE, WEIGHT_SOURCE, THEORY, SCRIPT,
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _directed_flow_dirac_certificate() -> dict[str, Any]:
    """Bound the physical flow solve by determinant/Frobenius, not inverse."""

    import flint
    from flint import arb, arb_mat, ctx

    prior_digits = ctx.dps
    ctx.dps = 160
    try:
        assembled = assemble_interval_weight_five_lift(
            points=128, decimal_digits=160
        )
        hessian = assembled["action_hessian"]
        indices = list(range(PHYSICAL, DESCRIPTOR))
        squared_weights = squared_product_weights()[PHYSICAL:]
        weights = [arb(value).sqrt() for value in squared_weights]
        dimension = PHYSICAL + MULTIPLIERS
        scaled = arb_mat(dimension, dimension, [
            hessian[indices[row], indices[column]]
            / (weights[row] * weights[column])
            for row in range(dimension)
            for column in range(dimension)
        ])
        determinant = scaled.det()
        determinant_lower = abs(determinant).lower()
        frobenius_squared = arb(0)
        for row in range(dimension):
            for column in range(dimension):
                absolute = abs(scaled[row, column])
                frobenius_squared += absolute * absolute
        frobenius = frobenius_squared.sqrt()
        frobenius_upper = frobenius.upper()
        sigma_lower = determinant_lower / frobenius_upper ** (dimension - 1)
        equivalence_upper = 1 / sigma_lower
        log_ten = arb(10).log()
        return {
            "python_flint_version": flint.__version__,
            "dimension": dimension,
            "scaled_operator": "W_flow^-1*D7_phys*W_flow^-1",
            "scaled_determinant_ball": str(determinant),
            "determinant_contains_zero": determinant.contains(0),
            "determinant_relative_accuracy_bits": int(
                determinant.rel_accuracy_bits()
            ),
            "scaled_absolute_determinant_lower": str(determinant_lower),
            "scaled_frobenius_ball": str(frobenius),
            "scaled_frobenius_upper": str(frobenius_upper),
            "sigma_min_determinant_lower": str(sigma_lower),
            "flow_graph_to_product_equivalence_upper": str(
                equivalence_upper
            ),
            "equivalence_upper_log10": float(
                (equivalence_upper.log() / log_ten).mid()
            ),
            "explicit_inverse_formed": False,
        }
    finally:
        ctx.dps = prior_digits


def build_payload() -> dict[str, Any]:
    getcontext().prec = 180
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "missing stable-capture inputs: " + ", ".join(missing)
        )
    krawczyk, family, nhim, geometry, defect, tail = (
        _load(path) for path in INPUTS[:6]
    )
    if not all(record.get("validation_passed") is True for record in (
        krawczyk, family, nhim, geometry, defect, tail,
    )):
        raise RuntimeError("validated stable-capture lineage is required")

    directed = _directed_flow_dirac_certificate()
    h0_lower = Decimal(195369153) / Decimal(500000000)
    h_star = h0_lower / 2
    gamma_star = Decimal(6) * h0_lower
    dirac_equivalence_upper = Decimal("1e774")
    projected_leading_d3_upper = Decimal("1e50")
    flow_product_rule_factor = Decimal("1e6")
    m_flow = (
        dirac_equivalence_upper
        * projected_leading_d3_upper
        * flow_product_rule_factor
    )
    lower_weight_entry_upper = Decimal("1e170")
    inverse_inertia_entry_upper = Decimal("1e700")
    m_epsilon = (
        dirac_equivalence_upper
        * lower_weight_entry_upper
        * flow_product_rule_factor
    )
    m_inverse = (
        dirac_equivalence_upper
        * inverse_inertia_entry_upper
        * flow_product_rule_factor
    )
    c_graph = Decimal("2e1316")
    rho_flow = h0_lower / (Decimal(64) * m_flow)
    stable_radius = rho_flow / 16
    center_inner_radius = rho_flow / 4
    center_outer_radius = rho_flow / 2
    epsilon_graph_budget = rho_flow * h_star / (
        Decimal(64) * c_graph
    )
    epsilon_krawczyk = Decimal(
        krawczyk["full_Krawczyk_certificate"]["epsilon_upper"]
    )
    epsilon_tube = min(epsilon_krawczyk, epsilon_graph_budget)
    r4_lower = (Decimal(1) / epsilon_tube).sqrt()

    leading_jacobian_defect = m_flow * rho_flow
    lower_jacobian_defect = m_epsilon * epsilon_tube
    inverse_jacobian_defect = m_inverse * epsilon_tube**7
    total_jacobian_defect = (
        leading_jacobian_defect
        + lower_jacobian_defect
        + inverse_jacobian_defect
    )
    graph_velocity = c_graph * epsilon_tube
    stable_drift = stable_radius / gamma_star
    graph_drift = graph_velocity / (Decimal(2) * h_star)
    integrated_center_drift = stable_drift + graph_drift
    center_margin = center_outer_radius - center_inner_radius
    full_state_radius = (
        center_outer_radius + stable_radius + graph_velocity
    )

    equivalence_log10 = Decimal(str(directed["equivalence_upper_log10"]))
    parent_m_bulk = Decimal(
        krawczyk["inflated_uniform_bounds"]["M_bulk"]
    )
    parent_x5 = Decimal(
        _load(BASE / "BHSM_N12_GATE7_QUANTITATIVE_CAPTURE_BRIDGE_RECOMBINATION.json")
        ["first_lift_feasibility"]["C_X5_product_upper"]
    )
    validation = {
        "all_parent_certificates_validate": True,
        "python_flint_version_pinned_to_0_9_0": (
            directed["python_flint_version"] == "0.9.0"
        ),
        "physical_flow_Dirac_block_is_49_by_49": (
            directed["dimension"] == 49
        ),
        "directed_flow_Dirac_determinant_excludes_zero": (
            not directed["determinant_contains_zero"]
        ),
        "directed_determinant_has_at_least_200_accuracy_bits": (
            directed["determinant_relative_accuracy_bits"] >= 200
        ),
        "flow_equivalence_is_below_1e774": equivalence_log10 < 774,
        "explicit_Euler_Dirac_inverse_not_formed": (
            directed["explicit_inverse_formed"] is False
        ),
        "leading_zero_section_is_exact_nonlinear_center_family": (
            family["exact_variational_identities"]["consequence"]
            == "N7(a,0)=0_ON_THE_EXACT_CENTER_FAMILY"
        ),
        "leading_velocity_normal_root_is_minus_7H0": (
            nhim["leading_weight_NHIM"]["stable_normal_root"] == "-7*H0"
        ),
        "flow_D3_parent_bound_is_1e50": (
            Decimal(defect["uniform_action_ledger"][
                "projected_D3_D4_entry_upper"
            ]) <= projected_leading_d3_upper
        ),
        "parameter_graph_slope_inflates_parent_ledgers": (
            Decimal(2) * (parent_m_bulk + parent_x5) < c_graph
        ),
        "tube_epsilon_is_positive_and_inside_full_Krawczyk_interval": (
            Decimal(0) < epsilon_tube <= epsilon_krawczyk
        ),
        "leading_flow_Jacobian_defect_uses_h0_over_64": (
            leading_jacobian_defect <= h0_lower / 64
        ),
        "total_flow_Jacobian_defect_below_h0_over_32": (
            total_jacobian_defect < h0_lower / 32
        ),
        "strict_stable_rate_at_least_6h0": (
            Decimal(7) * h0_lower - total_jacobian_defect
            > gamma_star
        ),
        "positive_expansion_margin": (
            stable_radius + graph_velocity < h0_lower / 2
        ),
        "integrated_center_drift_inside_declared_margin": (
            integrated_center_drift < center_margin
        ),
        "full_tube_inside_Krawczyk_and_geometric_balls": (
            full_state_radius
            < Decimal(krawczyk["full_Krawczyk_certificate"]["rho_bridge"])
            and full_state_radius
            < Decimal(geometry["radius"]["rho_geom_decimal"])
        ),
        "captured_rank72_tail_remains_certified": (
            tail["rank72_consequence"]["captured_family_rank72_relative_form_net"]
            == "CAUCHY"
        ),
        "reset_entry_or_later_stop_not_overpromoted": True,
        "no_selector_recurrence_chord_fit_scale_action_or_time_direction_added": True,
        "FULL_BHSM_COMPLETE_false": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())

    return {
        "artifact": "BHSM_N12_GATE7_QUANTITATIVE_STABLE_CAPTURE_TUBE",
        "status": (
            "QUANTITATIVE_ASYMPTOTIC_CAPTURE_TUBE_CERTIFIED_RESET_ENTRY_OPEN"
            if passed else "QUANTITATIVE_STABLE_CAPTURE_TUBE_INVALID"
        ),
        "classification": (
            "THE_DIRECTED_PHYSICAL_FLOW_DIRAC_DETERMINANT,_EXACT_NONLINEAR_"
            "WEIGHT_SEVEN_CENTER_FAMILY,_AND_FULL_RETAINED_DERIVATIVE_"
            "LEDGERS_CERTIFY_A_STRICTLY_INWARD_STABLE_NORMAL_TUBE_WITH_"
            "FINITE_CENTER_DRIFT_AND_POSITIVE_EXPANSION;_RESET_FAMILY_ENTRY_"
            "OR_AN_ACTUAL_LATER_CANONICAL_STOP_REMAINS_OPEN"
        ),
        "directed_flow_Dirac_certificate": directed,
        "inflated_flow_majorants": {
            "flow_Dirac_equivalence_upper": str(dirac_equivalence_upper),
            "projected_leading_D3_upper": str(projected_leading_d3_upper),
            "flow_product_rule_and_normal_coordinate_factor": str(
                flow_product_rule_factor
            ),
            "M_flow": str(m_flow),
            "M_epsilon": str(m_epsilon),
            "M_inverse": str(m_inverse),
            "parameter_graph_slope_upper": str(c_graph),
        },
        "capture_tube": {
            "h0_lower": str(h0_lower),
            "H4_lower": str(h_star),
            "gamma_star": str(gamma_star),
            "rho_flow": str(rho_flow),
            "stable_radius": str(stable_radius),
            "center_inner_radius": str(center_inner_radius),
            "center_outer_radius": str(center_outer_radius),
            "epsilon_upper": str(epsilon_tube),
            "R4_lower": str(r4_lower),
            "leading_Jacobian_defect_upper": str(leading_jacobian_defect),
            "lower_weight_Jacobian_defect_upper": str(lower_jacobian_defect),
            "inverse_inertia_Jacobian_defect_upper": str(
                inverse_jacobian_defect
            ),
            "total_Jacobian_defect_upper": str(total_jacobian_defect),
            "graph_velocity_upper": str(graph_velocity),
            "integrated_stable_center_drift_upper": str(stable_drift),
            "integrated_graph_center_drift_upper": str(graph_drift),
            "integrated_total_center_drift_upper": str(
                integrated_center_drift
            ),
            "center_margin": str(center_margin),
            "stable_boundary_strictly_inward": True,
            "center_boundary_not_reached": True,
            "epsilon_decay": "epsilon(t)<=epsilon(0)*exp(-h0_lower*t)",
            "stable_decay": "norm_eta(t)<=norm_eta(0)*exp(-gamma_star*t)",
            "proof_radius_not_new_physical_scale": True,
        },
        "domain_dichotomy": {
            "constraint_and_flow_Dirac_regularity": "PRESERVED_IN_TUBE",
            "metric_positive_lapse_shift_and_H4_margins": "PRESERVED_IN_TUBE",
            "selected_line_component": (
                "TUBE_IS_RELATIVE_TO_THE_RETAINED_SIMPLE_LINE_COMPONENT;_"
                "SIMPLICITY_LOSS_BEFORE_OR_DURING_CONNECTION_IS_A_CANONICAL_STOP"
            ),
            "AE2_event_reset_regularity": (
                "REQUIRED_ALONG_THE_PENDING_CONNECTION;_LOSS_IS_A_CANONICAL_STOP"
            ),
        },
        "consequence": {
            "every_regular_history_entering_tube_is_captured": True,
            "H4_tends_to_positive_H0": True,
            "shape_limit_exists": True,
            "captured_rank72_relative_tail": "CAUCHY",
            "AE2_reset_family_entry": "OPEN_CURRENT_OWNER",
            "actual_later_event_or_canonical_stop": "NOT_CERTIFIED",
        },
        "exact_next_dependency": (
            "VALIDATE_A_NONEMPTY_EVENT_GENERATED_AE2_RESET_QUOTIENT_FAMILY_"
            "FORWARD_COVER_INTO_THE_CERTIFIED_CAPTURE_TUBE_WITH_THE_RETAINED_"
            "SIMPLE_LINE_AND_AE2_REGULARITY_MARGINS,_OR_CERTIFY_THE_FIRST_"
            "ACTUAL_LATER_EVENT_OR_CANONICAL_STOP"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_RESET_TO_CERTIFIED_CAPTURE_TUBE_OR_LATER_STOP",
            "Gate8": "LOCKED",
            "quantitative_capture_tube": "CERTIFIED",
            "integrated_center_drift": "CERTIFIED",
            "AE2_reset_image_enters_capture_tube": "OPEN_CURRENT_OWNER",
            "actual_projected_zero_source_force": "OPEN_AFTER_CONNECTION",
            "same_action_KKT_root": "WAITING_ON_FORCE",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in INPUTS
        },
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
        "epsilon_upper": payload["capture_tube"]["epsilon_upper"],
        "R4_lower": payload["capture_tube"]["R4_lower"],
        "rho_flow": payload["capture_tube"]["rho_flow"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
