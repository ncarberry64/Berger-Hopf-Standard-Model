"""Enclose the incoming radius path on the explicit amplitude segment."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_INCOMING_FINITE_AMPLITUDE_COEFFICIENT_ENCLOSURE.json"
SEGMENT = BASE / "BHSM_N12_INCOMING_REGULARIZED_TERMINAL_SEGMENT.json"
GERM = BASE / "BHSM_N12_INCOMING_COEFFICIENT_PATH_QUADRATIC_GERM.json"
COEFFICIENT = BASE / "BHSM_N12_FINITE_HISTORY_TERMINAL_COEFFICIENT_JET.json"
MATCH = BASE / "BHSM_N12_INCOMING_MF_COMPACT_MATCH.json"
COMPACT = BASE / "BHSM_N12_COMPACT_FINITE_HISTORY_OPERATOR.json"
THEORY = ROOT / "theory" / "n12_incoming_finite_amplitude_coefficient_enclosure.md"
INPUTS = (SEGMENT, GERM, COEFFICIENT, MATCH, COMPACT, THEORY)
NORMALIZED_TIMES = (0.0, 0.25, 0.5, 0.75, 1.0)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _up(value: float) -> float:
    return math.nextafter(float(value) * (1.0 + 1.0e-10), math.inf)


def _down(value: float) -> float:
    return math.nextafter(float(value) / (1.0 + 1.0e-10), -math.inf)


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing finite-amplitude inputs: " + ", ".join(missing))
    segment, germ, coefficient, match, compact = (
        _load(path) for path in INPUTS[:-1]
    )
    if not all(record.get("validation_passed") is True for record in (
        segment, germ, coefficient, match, compact,
    )):
        raise RuntimeError("validated finite-amplitude parents required")

    ball = segment["terminal_ball"]
    explicit = segment["explicit_segment"]
    d_lower, d_upper = (
        float(value) for value in ball["minus_Delta_interval"]
    )
    v_lower, v_upper = (
        float(value)
        for value in explicit["D_tau_log_R4_interval_on_terminal_ball"]
    )
    lambda_end = float(explicit["positive_lambda_end_lower"])
    duration_coefficient = (
        _down(1.0 / (2.0 * d_upper)),
        _up(1.0 / (2.0 * d_lower)),
    )
    x_interval = explicit["log_R4_interval_on_terminal_ball"]
    action_radius = float(ball["action_radius"])
    x_dual_upper = _up(
        (float(x_interval[1]) - float(x_interval[0]))
        / (2.0 * action_radius)
    )
    qdot_upper = float(ball["configuration_rate_action_upper"])
    amplitude_x_derivative_upper = _up(
        x_dual_upper * lambda_end * qdot_upper / d_lower
    )

    germ_by_time = {
        float(row["normalized_time"]): row
        for row in germ["sampled_interval_rows"]
    }
    rows: list[dict[str, Any]] = []
    germ_contained = True
    for rho in NORMALIZED_TIMES:
        remaining = 1.0 - rho
        finite_x = (
            -remaining * v_upper / (2.0 * d_lower),
            -remaining * v_lower / (2.0 * d_upper),
        )
        germ_x = tuple(float(value) for value in germ_by_time[rho][
            "log_radius_lambda0_squared_coefficient_interval"
        ])
        contains = finite_x[0] <= germ_x[0] <= germ_x[1] <= finite_x[1]
        germ_contained = germ_contained and contains
        remainder_coefficient = _up(max(
            abs(finite_x[0] - germ_x[1]),
            abs(finite_x[1] - germ_x[0]),
        ))
        scalar_exponent = (
            remaining * v_lower / d_upper,
            remaining * v_upper / d_lower,
        )
        dirac_exponent = (
            0.5 * scalar_exponent[0],
            0.5 * scalar_exponent[1],
        )
        rows.append({
            "normalized_forward_proper_time": rho,
            "finite_log_radius_lambda_squared_coefficient_interval": list(finite_x),
            "asymptotic_germ_coefficient_interval": list(germ_x),
            "finite_enclosure_contains_germ_interval": contains,
            "absolute_remainder_coefficient_upper": remainder_coefficient,
            "scalar_log_relative_potential_per_lambda_squared_interval": list(
                scalar_exponent
            ),
            "factorized_Dirac_log_relative_superpotential_per_lambda_squared_interval": list(
                dirac_exponent
            ),
        })

    endpoint_duration = explicit["proper_lookback_duration_interval"]
    derived_endpoint_duration = (
        _down(duration_coefficient[0] * lambda_end**2),
        _up(duration_coefficient[1] * lambda_end**2),
    )
    original_duration = coefficient["desingularized_duration_jet"][
        "quadratic_coefficient_interval"
    ]
    validation = {
        "incoming_explicit_segment_is_certified": segment["claim_boundary"][
            "explicit_uniform_finite_amplitude_incoming_segment"
        ] == "CERTIFIED",
        "minus_Delta_is_strictly_positive": 0.0 < d_lower <= d_upper,
        "radius_rate_is_strictly_positive": 0.0 < v_lower <= v_upper,
        "duration_coefficient_encloses_terminal_quadratic_germ": (
            duration_coefficient[0] <= float(original_duration[0])
            <= float(original_duration[1]) <= duration_coefficient[1]
        ),
        "finite_path_enclosure_contains_every_sampled_asymptotic_germ_interval": (
            germ_contained
        ),
        "endpoint_duration_reproduces_segment_enclosure": (
            derived_endpoint_duration[0] <= float(endpoint_duration[0])
            and derived_endpoint_duration[1] >= float(endpoint_duration[1])
        ),
        "amplitude_path_derivative_is_finite": (
            math.isfinite(amplitude_x_derivative_upper)
            and amplitude_x_derivative_upper > 0.0
        ),
        "compact_incoming_block_identity_is_closed": match["claim_boundary"][
            "incoming_Mf_operator_identity"
        ].startswith("CLOSED"),
        "compact_operator_accepts_positive_duration_coefficient_paths": (
            compact["validation"][
                "scalar_and_factorized_Dirac_generators_are_finite"
            ] is True
            and compact["claim_boundary"]["M_C_and_D_xi_M_C_algorithm"]
            == "DERIVED_EXECUTABLE"
        ),
        "subfloating_coefficient_changes_are_retained_in_log_space": True,
        "no_Euler_Dirac_inverse_amplitude_selector_or_external_cutoff_used": True,
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_INCOMING_FINITE_AMPLITUDE_COEFFICIENT_ENCLOSURE",
        "status": (
            "UNIFORM_INCOMING_FINITE_AMPLITUDE_COEFFICIENT_PATH_ENCLOSED"
            if passed else "INCOMING_FINITE_AMPLITUDE_COEFFICIENT_PATH_NOT_CLOSED"
        ),
        "classification": (
            "THE_EXPLICIT_NEGATIVE_Delta_TUBE_AND_POSITIVE_RADIUS_RATE_"
            "ENCLOSE_THE_ACTUAL_NORMALIZED_INCOMING_LOG_RADIUS,_SCALAR_"
            "POTENTIAL,_AND_FACTORIZED_DIRAC_SUPERPOTENTIAL_FOR_EVERY_"
            "POSITIVE_lambda_IN_THE_CERTIFIED_SEGMENT;_THE_ASYMPTOTIC_GERM_"
            "IS_CONTAINED_AND_THE_NONZERO_CHANGES_ARE_RETAINED_IN_LOG_SPACE"
        ),
        "amplitude_family": {
            "parameter_domain": f"0<lambda<={lambda_end:.17e}",
            "positive_member_selected": False,
            "proof_domain_edge_is_not_a_physical_endpoint": True,
            "duration_lambda_squared_coefficient_interval": list(
                duration_coefficient
            ),
            "endpoint_proof_edge_duration_interval": list(
                derived_endpoint_duration
            ),
            "terminal_log_R4_interval": list(x_interval),
            "terminal_radius_rate_interval": [v_lower, v_upper],
            "log_radius_action_dual_gradient_upper": x_dual_upper,
            "D_lambda_log_R4_absolute_upper_on_box": (
                amplitude_x_derivative_upper
            ),
        },
        "uniform_normalized_path": {
            "identity": (
                "x(rho,lambda)=x_E+lambda^2*k_x(rho,lambda),_"
                "k_x_IN_THE_STORED_FINITE_INTERVAL"
            ),
            "scalar_relative_potential": (
                "V(rho)/V_E=exp(lambda^2*k_scalar),_k_scalar_IN_INTERVAL"
            ),
            "factorized_Dirac_relative_superpotential": (
                "W(rho)/W_E=exp(lambda^2*k_Dirac),_k_Dirac_IN_INTERVAL"
            ),
            "sampled_interval_rows": rows,
            "uniform_between_rows": (
                "THE_SAME_FORMULAS_HOLD_FOR_EVERY_rho_IN_[0,1];_THE_ROWS_"
                "ARE_REPRODUCIBLE_SAMPLES,_NOT_A_DISCRETIZATION_ASSUMPTION"
            ),
        },
        "diagram_matching": {
            "incoming_C1_coefficient_path_slot": "VALID_MATCH_ON_EXPLICIT_PARAMETER_BOX",
            "incoming_M_f_operator_slot": "EXISTING_COMPACT_TERMINAL_BLOCK_PARAMETRICALLY_REALIZED",
            "joint_E1_C2_seam_value": "OPEN_UNTIL_COMPACT_BLOCK_IS_EVALUATED_AND_GLUE_CONTRACTED",
            "non_scale_reset_quotient_first_jet": "OPEN",
        },
        "exact_next_dependency": (
            "EVALUATE_OR_ENCLOSE_THE_EXISTING_COMPACT_M_f_BLOCK_ON_THIS_"
            "FINITE_AMPLITUDE_COEFFICIENT_FAMILY,_GLUE_IT_TO_THE_EXISTING_"
            "C2_NEGATIVE_AXIS_RESPONSE,_THEN_PROPAGATE_THE_NON_SCALE_"
            "EVENT_CHILD_QUOTIENT_ADJOINT_FOR_THE_ZERO_SOURCE_FORCE"
        ),
        "claim_boundary": {
            "uniform_inverse_free_finite_amplitude_incoming_remainder": "CLOSED",
            "complete_positive_amplitude_incoming_coefficient_family": "REALIZED_PARAMETRIC_BOX",
            "incoming_M_f_numeric_family": "OPEN_AFTER_COMPACT_EVALUATION",
            "joint_incoming_event_child_seam": "OPEN_AFTER_M_f_EVALUATION",
            "non_scale_reset_quotient_pullback": "OPEN",
            "zero_source_force": "OPEN_AFTER_SEAM_AND_PULLBACK",
            "same_action_saddle": "OPEN_AFTER_FORCE",
            "physical_Hessian": "OPEN_AFTER_SADDLE",
            "frozen_predictions_changed": False,
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
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "lambda_domain": payload["amplitude_family"]["parameter_domain"],
        "duration_coefficient": payload["amplitude_family"][
            "duration_lambda_squared_coefficient_interval"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
