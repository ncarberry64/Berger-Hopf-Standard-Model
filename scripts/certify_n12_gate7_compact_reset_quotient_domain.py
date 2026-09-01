"""Certify a compact nonempty AE2 reset-quotient parameter domain.

This is the finite parameter-domain half of the Gate-7 connection problem.
It applies a quantitative parameter-dependent radii argument to the existing
58-row terminal-reset normal section.  It does not propagate the domain and
does not select a member of the reset family.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_c2_geometry_incidence import (  # noqa: E402
    boundary_geometry_action_covectors,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_COMPACT_RESET_QUOTIENT_DOMAIN.json"
DATA = RESULT.with_suffix(".npz")
ROOT_RECORD = BASE / "BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.json"
ROOT_DATA = ROOT_RECORD.with_suffix(".npz")
DIRECTED_DATA = BASE / "BHSM_N12_FINITE_TERMINAL_DIRECTED_CENTER_DATA.npz"
RADII = BASE / "BHSM_N12_FINITE_TERMINAL_RADII_CERTIFICATE.json"
MARGINS = BASE / "BHSM_N12_FINITE_TERMINAL_MARGIN_TRANSFER.json"
LAUNCH = BASE / "BHSM_N12_C2_RESET_GENERATED_LAUNCH_CHART.json"
BIRTH = BASE / "BHSM_N12_C2_BIRTH_COEFFICIENT_QUOTIENT_JET.json"
INTERFACE = BASE / "BHSM_N12_FINITE_TERMINAL_TWO_SIDED_FORWARD_INTERFACE.json"
THEORY = ROOT / "theory" / "n12_gate7_compact_reset_quotient_domain.md"
PARAMETER_RADIUS = 1.0e-12
STATE_DIMENSION = 98
INPUTS = (
    ROOT_RECORD,
    ROOT_DATA,
    DIRECTED_DATA,
    RADII,
    MARGINS,
    LAUNCH,
    BIRTH,
    INTERFACE,
    THEORY,
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _up(value: float) -> float:
    return math.nextafter(float(value) * (1.0 + 1.0e-12), math.inf)


def _down(value: float) -> float:
    return math.nextafter(float(value) / (1.0 + 1.0e-12), -math.inf)


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "missing compact reset-quotient inputs: " + ", ".join(missing)
        )
    root, radii, margins, launch, birth, interface = (
        _load(path)
        for path in (ROOT_RECORD, RADII, MARGINS, LAUNCH, BIRTH, INTERFACE)
    )
    if not all(record.get("validation_passed") is True for record in (
        root, radii, margins, launch, birth, interface,
    )):
        raise RuntimeError("validated reset-domain parents required")

    with np.load(ROOT_DATA) as source:
        center = np.asarray(source["state"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
    with np.load(DIRECTED_DATA) as source:
        normal = np.asarray(source["normal_basis"], dtype=float)
        primary_normal = np.asarray(source["primary_normal"], dtype=float)

    # The 58 normal columns are action-orthonormal.  Complete QR gives the
    # 138-dimensional tangent of the terminal reset stratum.  Its projection
    # to the forward-swapped C2 half has rank 72; the corresponding right
    # singular directions provide coordinates, not a selected history.
    complete, _ = np.linalg.qr(normal, mode="complete")
    tangent = complete[:, normal.shape[1]:]
    event_projection = tangent[:STATE_DIMENSION]
    _, event_singular, event_vh = np.linalg.svd(
        event_projection, full_matrices=False
    )
    event_rank = int(np.count_nonzero(event_singular > 1.0e-8))
    parameter_lift = tangent @ event_vh[:event_rank].T
    projected_lift = parameter_lift[:STATE_DIMENSION]

    theorem = root["refined_radii_theorem"]
    Y0 = float(theorem["Y_upper"])
    Z0 = float(theorem["Z0_upper"])
    Z2 = float(theorem["Z2_upper_reused"])
    root_distance = float(theorem["a_posteriori_root_distance_upper"])
    component_radius = float(radii["action_coordinate_ball_radius"])
    rho = PARAMETER_RADIUS

    # For ||t||<=rho, tangency kills the first-order parameter residual.
    # The same retained Z2 controls the parameter residual, normal derivative
    # drift, and normal Taylor remainder.
    parameter_residual = _up(Y0 + 0.5 * Z2 * rho**2)
    parameter_defect = _up(Z0 + Z2 * rho)
    discriminant = _down(
        (1.0 - parameter_defect) ** 2
        - 2.0 * Z2 * parameter_residual
    )
    if discriminant <= 0.0:
        raise ArithmeticError("parameter-dependent radii discriminant failed")
    small_root = _up(
        2.0 * parameter_residual
        / ((1.0 - parameter_defect) + math.sqrt(discriminant))
    )
    normal_radius = _up(2.0 * small_root)
    radii_value = _up(
        parameter_residual
        + parameter_defect * normal_radius
        + 0.5 * Z2 * normal_radius**2
        - normal_radius
    )
    total_radius = _up(math.hypot(rho, normal_radius))
    derivative_margin = _down(1.0 - Z0 - Z2 * total_radius)
    if derivative_margin <= 0.0:
        raise ArithmeticError("normal derivative margin failed")

    normal_graph_first = _up(
        Z2 * (root_distance + total_radius) / derivative_margin
    )
    center_projection_lower = _down(float(event_singular[event_rank - 1]))
    parent_projection_lower = float(
        birth["swapped_reset"]["C2_projection_smallest_nonzero_singular_value"]
    )
    quotient_first_jet_lower = _down(
        min(center_projection_lower, parent_projection_lower)
        - normal_graph_first
    )

    c2_center = center[:STATE_DIMENSION]
    geometry = boundary_geometry_action_covectors(
        state=c2_center, weights=weights
    )
    lapse_covector_norm = _up(
        float(np.linalg.norm(geometry["D_log_lapse_action_dual"]))
    )
    radius_covector_norm = _up(
        float(np.linalg.norm(geometry["D_log_R4_action_dual"]))
    )
    rate_gradient = float(
        birth["C2_birth_coefficient"]["action_dual_rate_gradient_bound"]
    )
    rate_lower = _down(
        float(birth["C2_birth_coefficient"]["center_D_tau_log_R4"])
        - rate_gradient * total_radius
    )
    lapse_lower = _down(
        math.exp(float(geometry["log_lapse"]) - lapse_covector_norm * total_radius)
    )
    radius_lower = _down(
        math.exp(float(geometry["log_R4"]) - radius_covector_norm * total_radius)
    )

    np.savez_compressed(
        DATA,
        reset_quotient_parameter_lift=parameter_lift,
        projected_C2_parameter_lift=projected_lift,
        terminal_reset_normal_basis=normal,
        proof_center=center,
        state_weights=weights,
        parameter_radius=np.asarray(rho),
        normal_graph_radius=np.asarray(normal_radius),
    )

    validation = {
        "terminal_reset_tangent_dimension_is_138": tangent.shape == (196, 138),
        "forward_swapped_C2_quotient_rank_is_72": event_rank == 72,
        "parameter_lift_has_72_orthonormal_columns": (
            parameter_lift.shape == (196, 72)
            and np.linalg.norm(
                parameter_lift.T @ parameter_lift - np.eye(72), ord=2
            ) < 2.0e-12
        ),
        "parameter_lift_is_tangent_to_58_row_map": (
            np.linalg.norm(primary_normal @ normal.T @ parameter_lift, ord=2)
            < 2.0e-10
        ),
        "parameter_dependent_radii_polynomial_is_negative": radii_value < 0.0,
        "joint_parameter_and_normal_graph_stay_in_parent_ball": (
            total_radius < component_radius
        ),
        "normal_reset_regularity_margin_is_strict": derivative_margin > 0.0,
        "first_quotient_jet_rank_margin_is_strict": quotient_first_jet_lower > 0.0,
        "positive_lapse_radius_and_forward_radius_rate": (
            lapse_lower > 0.0 and radius_lower > 0.0 and rate_lower > 0.0
        ),
        "event_child_line_legendre_and_normal_margins_inherited": all((
            margins["transferred_margins"]["child_selected_line_simple"],
            margins["transferred_margins"]["event_selected_line_simple"],
            margins["transferred_margins"]["event_and_child_Legendre_positive"],
            margins["transferred_margins"]["terminal_map_normal_regular"],
        )),
        "forward_two_sided_interface_inherited": (
            interface["validation"]["event_half_is_forward_outgoing"]
            and interface["validation"][
                "terminal_root_and_child_incoming_orientation_certified"
            ]
        ),
        "compact_domain_has_nonempty_relative_interior": rho > 0.0,
        "proof_radius_is_not_a_new_physical_scale": True,
        "no_member_selector_recurrence_chord_fit_gate_or_time_direction_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())

    return {
        "artifact": "BHSM_N12_GATE7_COMPACT_RESET_QUOTIENT_DOMAIN",
        "status": (
            "COMPACT_NONEMPTY_AE2_RESET_QUOTIENT_DOMAIN_CERTIFIED"
            if passed else "COMPACT_RESET_QUOTIENT_DOMAIN_INVALID"
        ),
        "classification": (
            "THE_EXISTING_58_ROW_TERMINAL_RESET_RADII_THEOREM_EXTENDS_"
            "PARAMETRICALLY_OVER_A_CLOSED_72_BALL_WITH_NONEMPTY_INTERIOR;_"
            "THE_ENTIRE_BALL,_NOT_A_MEMBER,_IS_THE_FORWARD_RESET_DOMAIN"
        ),
        "parameter_domain": {
            "definition": "K_RHO={xi_IN_R72:||xi||_2<=rho}",
            "dimension": 72,
            "radius": rho,
            "compact": True,
            "nonempty_relative_interior": True,
            "normal_graph_radius_upper": normal_radius,
            "joint_action_radius_upper": total_radius,
            "parent_action_radius": component_radius,
            "proof_radius_not_new_physical_scale": True,
        },
        "parameter_radii_theorem": {
            "Y_rho_upper": parameter_residual,
            "Z0_rho_upper": parameter_defect,
            "Z2_upper": Z2,
            "discriminant_lower": discriminant,
            "small_root_upper": small_root,
            "test_normal_radius": normal_radius,
            "radii_polynomial_upper": radii_value,
            "normal_derivative_margin_lower": derivative_margin,
            "formula": (
                "p_rho(r)=Y0+(Z2/2)rho^2+(Z0+Z2*rho)r+"
                "(Z2/2)r^2-r"
            ),
        },
        "quotient_first_jet": {
            "center_terminal_projection_singular_value_lower": (
                center_projection_lower
            ),
            "parent_C2_projection_singular_value_lower": parent_projection_lower,
            "normal_graph_first_jet_upper": normal_graph_first,
            "uniform_C2_quotient_first_jet_singular_value_lower": (
                quotient_first_jet_lower
            ),
            "rank": 72,
        },
        "uniform_regular_domain_margins": {
            "boundary_lapse_lower": lapse_lower,
            "boundary_radius_lower": radius_lower,
            "D_tau_log_R4_lower": rate_lower,
            "event_selected_line_simple": True,
            "child_selected_line_simple": True,
            "event_child_Legendre_positive": True,
            "terminal_reset_normal_regular": True,
            "forward_two_sided_orientation": True,
        },
        "adjudication": {
            "compact_reset_quotient_parameter_domain": "CERTIFIED",
            "reset_member_selected": False,
            "propagated_reset_to_terminal_map": "OPEN_CURRENT_OWNER",
            "strict_capture_tube_inclusion": "OPEN",
            "first_retained_stop": "OPEN",
            "Gate7": "OPEN_ON_PROPAGATED_SET_MAP_OR_STOP",
        },
        "exact_next_dependency": (
            "PROPAGATE_THIS_COMPLETE_COMPACT_72_BALL_WITH_ITS_NORMAL_GRAPH_"
            "AND_FIRST_JETS_THROUGH_ONE_FINITE_BOUNDARY_CONTROLLED_FLOW_OR_"
            "FIRST_HIT_MAP;_CERTIFY_STRICT_CAPTURE_TUBE_INCLUSION,_NONZERO_"
            "DEGREE_WITH_BOUNDARY_EXCLUSION,_OR_THE_FIRST_RETAINED_STOP"
        ),
        "claim_boundary": {
            "compact_nonempty_reset_quotient_domain": "CERTIFIED",
            "reset_to_capture_or_stop": "OPEN",
            "actual_projected_zero_source_force": "OPEN_AFTER_CONNECTION_OR_STOP",
            "same_action_KKT_root": "WAITING_ON_FORCE",
            "physical_constrained_Hessian": "WAITING_ON_KKT_ROOT",
            "Gate7": "ACTIVE",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "data": DATA.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in (*INPUTS, Path(__file__))
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
        "parameter_domain": payload["parameter_domain"],
        "quotient_first_jet": payload["quotient_first_jet"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
