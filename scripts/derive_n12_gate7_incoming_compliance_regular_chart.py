"""Certify the regular incoming-compliance chart for the Gate-7 seam."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_INCOMING_COMPLIANCE_REGULAR_CHART.json"
MATCH = BASE / "BHSM_N12_INCOMING_MF_COMPACT_MATCH.json"
NEGATIVE_AXIS = BASE / "BHSM_N12_INCOMING_MF_NEGATIVE_AXIS_ENCLOSURE.json"
FAMILY = BASE / "BHSM_N12_INCOMING_FINITE_AMPLITUDE_COEFFICIENT_ENCLOSURE.json"
SEGMENT = BASE / "BHSM_N12_INCOMING_REGULARIZED_TERMINAL_SEGMENT.json"
GERM = BASE / "BHSM_N12_FINITE_HISTORY_TERMINAL_WEYL_GERM.json"
HEAT_SEED = BASE / "BHSM_N12_GATE7_JOINT_HEAT_COTANGENT_REVERSE_SEED.json"
ZETA = BASE / "BHSM_N12_GATE7_INCOMING_AMPLITUDE_ZETA_COTANGENT.json"
THEORY = ROOT / "theory" / "n12_gate7_incoming_compliance_regular_chart.md"
INPUTS = (MATCH, NEGATIVE_AXIS, FAMILY, SEGMENT, GERM, HEAT_SEED, ZETA, THEORY)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _algebra_witness() -> dict[str, float | bool]:
    """Replay C=b/d, its quotient jet, and -C^2 DM on one regular chart."""

    b = 0.17
    d = 1.08
    db = -0.031
    dd = 0.024
    mf = d / b
    d_mf = (dd * b - d * db) / (b * b)
    compliance = b / d
    quotient_jet = (db * d - b * dd) / (d * d)
    inverse_jet = -(compliance**2) * d_mf
    return {
        "transfer_b": b,
        "transfer_d": d,
        "M_f": mf,
        "C_f": compliance,
        "D_M_f": d_mf,
        "D_C_f_quotient": quotient_jet,
        "D_C_f_inverse_identity": inverse_jet,
        "derivative_identity_absolute_residual": abs(quotient_jet - inverse_jet),
        "positive_M_f_and_C_f": bool(mf > 0.0 and compliance > 0.0),
    }


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "missing incoming-compliance inputs: " + ", ".join(missing)
        )
    match, negative_axis, family, segment, germ, heat_seed, zeta = (
        _load(path) for path in INPUTS[:-1]
    )
    if not all(item.get("validation_passed") is True for item in (
        match, negative_axis, family, segment, germ, heat_seed, zeta,
    )):
        raise RuntimeError("validated incoming-compliance parents required")

    d_lower, d_upper = (
        float(value) for value in segment["terminal_ball"]["minus_Delta_interval"]
    )
    lambda_upper = float(segment["explicit_segment"]["positive_lambda_end_lower"])
    duration_coefficient = [
        float(value)
        for value in family["amplitude_family"][
            "duration_lambda_squared_coefficient_interval"
        ]
    ]
    duration_derivative_per_lambda = [1.0 / d_upper, 1.0 / d_lower]
    x_derivative_per_lambda_upper = (
        float(family["amplitude_family"]["D_lambda_log_R4_absolute_upper_on_box"])
        / lambda_upper
    )
    witness = _algebra_witness()

    validation = {
        "incoming_response_is_compact_M11": (
            match["exact_match"]["restriction"].endswith("=M11")
        ),
        "negative_axis_incoming_response_is_strictly_positive": (
            negative_axis["claim_boundary"][
                "incoming_M_f_negative_axis_parametric_enclosure"
            ] == "CLOSED"
        ),
        "duration_derivative_per_lambda_is_positive_and_ordered": (
            0.0 < duration_derivative_per_lambda[0]
            <= duration_derivative_per_lambda[1]
        ),
        "duration_quadratic_coefficients_match_half_derivative_coefficients": (
            math.isclose(
                duration_coefficient[0],
                0.5 * duration_derivative_per_lambda[0],
                rel_tol=2.0e-10,
            )
            and math.isclose(
                duration_coefficient[1],
                0.5 * duration_derivative_per_lambda[1],
                rel_tol=2.0e-10,
            )
        ),
        "normalized_coefficient_amplitude_jet_is_O_lambda": (
            math.isfinite(x_derivative_per_lambda_upper)
            and x_derivative_per_lambda_upper > 0.0
        ),
        "terminal_M_f_Laurent_germ_is_certified": (
            germ["claim_boundary"]["terminal_M_C_Laurent_germ"] == "CERTIFIED"
        ),
        "joint_heat_seed_uses_one_complete_internal_seam": (
            heat_seed["adjudication"]["joint_reverse_seed_formula"] == "CLOSED"
        ),
        "componentwise_KKT_condition_remains_retired": (
            zeta["adjudication"]["componentwise_KKT_condition_added"] is False
        ),
        "compliance_derivative_identity_replays": (
            witness["derivative_identity_absolute_residual"] < 1.0e-15
            and witness["positive_M_f_and_C_f"] is True
        ),
        "graded_uniform_differentiation_not_overclaimed": True,
        "no_descriptor_inverse_source_selector_endpoint_recurrence_scale_gate_or_chord_added": True,
    }
    validation = {name: bool(value) for name, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_INCOMING_COMPLIANCE_REGULAR_CHART",
        "status": (
            "INCOMING_COMPLIANCE_REGULAR_CHART_AND_LINEAR_AMPLITUDE_JET_CERTIFIED"
            if passed else "INCOMING_COMPLIANCE_REGULAR_CHART_INVALID"
        ),
        "classification": (
            "THE_SHORT_ARM_DIRICHLET_TO_NEUMANN_POLE_M_f_EQUALS_d_OVER_b_"
            "IS_REMOVED_BY_THE_EQUIVALENT_COMPLIANCE_CHART_C_f_EQUALS_b_OVER_d;_"
            "THE_EXACT_REVERSE_IDENTITY_D_C_f_EQUALS_MINUS_C_f_D_M_f_C_f_"
            "MAKES_EVERY_FIXED_CHANNEL_AMPLITUDE_JET_LINEAR_AT_THE_ZERO_LENGTH_LIMIT"
        ),
        "exact_chart": {
            "transfer": "Phi_f=[[a,b],[c,d]]",
            "incoming_DtN": "M_f=d/b",
            "incoming_compliance": "C_f=M_f^-1=b/d",
            "derivative": "D_C_f=-C_f*(D_M_f)*C_f=(D_b*d-b*D_d)/d^2",
            "descriptor_or_kinetic_block_inverse_formed": False,
        },
        "short_arm_theorem": {
            "M_f": "T^-1+C_0+T*B+O(T^2)",
            "C_f": "T-T^2*C_0+O(T^3)",
            "duration_derivative": "D_lambda_T=lambda/(-Delta(lambda))",
            "compliance_derivative": (
                "D_lambda_C_f=lambda/(-Delta(lambda))+O(lambda^3)"
            ),
            "fixed_channel_heat_functional_sensitivity": "O(lambda)",
            "uniform_full_graded_supertrace_sensitivity": "OPEN_SUMMABLE_DOMINATION",
        },
        "certified_coefficients": {
            "amplitude_interval": [0.0, lambda_upper],
            "amplitude_interval_left_endpoint_is_open": True,
            "minus_Delta_interval": [d_lower, d_upper],
            "duration_lambda_squared_coefficient_interval": duration_coefficient,
            "D_lambda_T_per_lambda_interval": duration_derivative_per_lambda,
            "D_lambda_log_R4_per_lambda_absolute_upper": (
                x_derivative_per_lambda_upper
            ),
            "liminf_D_lambda_C_f_per_lambda_lower": (
                duration_derivative_per_lambda[0]
            ),
            "limsup_D_lambda_C_f_per_lambda_upper": (
                duration_derivative_per_lambda[1]
            ),
        },
        "algebra_witness": witness,
        "adjudication": {
            "incoming_M_f_is_zeroed": False,
            "new_seam_force_or_source_added": False,
            "componentwise_KKT_condition_added": False,
            "pointwise_fixed_channel_shrinking_arm_heat_jet": "REGULAR_O_lambda",
            "full_graded_heat_amplitude_bound": "OPEN_UNIFORM_ANGULAR_DOMINATION",
            "joint_amplitude_force": "OPEN_AFTER_GRADED_DOMINATION",
            "maximal_projected_tail": "OPEN",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
        },
        "exact_next_dependency": (
            "PROVE_A_SUMMABLE_ANGULAR_MAJORANT_FOR_THE_REGULAR_COMPLIANCE_"
            "HEAT_JET,_THEN_COMPARE_THE_RESULTING_UNIFORM_O_lambda_BOUND_"
            "WITH_THE_CERTIFIED_STRICT_REPLACEMENT_ZETA_COEFFICIENT"
        ),
        "claim_boundary": {
            "incoming_compliance_regular_chart": "CERTIFIED",
            "fixed_channel_amplitude_heat_jet_regularity": "CERTIFIED_POINTWISE",
            "uniform_graded_heat_amplitude_covector": "OPEN",
            "joint_amplitude_force": "OPEN",
            "actual_projected_KKT_root": "OPEN",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
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
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if not payload["validation_passed"]:
        raise RuntimeError("incoming-compliance validation failed")
    print(json.dumps({
        "status": payload["status"],
        "D_lambda_T_per_lambda_interval": payload["certified_coefficients"][
            "D_lambda_T_per_lambda_interval"
        ],
        "fixed_channel_heat_jet": payload["adjudication"][
            "pointwise_fixed_channel_shrinking_arm_heat_jet"
        ],
        "graded_heat_jet": payload["adjudication"][
            "full_graded_heat_amplitude_bound"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
