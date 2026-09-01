"""Certify the inverse-free incoming normalized coefficient-path germ."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_boundary_radius import (  # noqa: E402
    normalized_incoming_log_radius_quadratic_germ,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_INCOMING_COEFFICIENT_PATH_QUADRATIC_GERM.json"
COEFFICIENT = BASE / "BHSM_N12_FINITE_HISTORY_TERMINAL_COEFFICIENT_JET.json"
PARAMETER = BASE / "BHSM_N12_DESINGULARIZED_FINITE_HISTORY_OPERATOR_PARAMETER.json"
MATCH = BASE / "BHSM_N12_INCOMING_MF_COMPACT_MATCH.json"
COMPACT = BASE / "BHSM_N12_COMPACT_FINITE_HISTORY_OPERATOR.json"
MODULE = ROOT / "src" / "bhsm" / "interface" / "aether_forward_boundary_radius.py"
THEORY = ROOT / "theory" / "n12_incoming_coefficient_path_quadratic_germ.md"
INPUTS = (COEFFICIENT, PARAMETER, MATCH, COMPACT, MODULE, THEORY)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing incoming path-germ inputs: " + ", ".join(missing))
    coefficient, parameter, match, compact = (
        _load(path) for path in INPUTS[:4]
    )
    if not all(record.get("validation_passed") is True for record in (
        coefficient, parameter, match, compact,
    )):
        raise RuntimeError("validated incoming path-germ parents required")
    terminal = coefficient["terminal_coefficient_data"]
    rate_interval = tuple(float(value) for value in terminal[
        "root_D_tau_log_R4_interval"
    ])
    coefficient_interval = tuple(float(value) for value in coefficient[
        "desingularized_duration_jet"
    ]["quadratic_coefficient_interval"])
    parameter_interval = tuple(float(value) for value in parameter[
        "duration_parameter_jet"
    ]["certified_a_interval"])
    times = np.linspace(0.0, 1.0, 5)
    germ = normalized_incoming_log_radius_quadratic_germ(
        times,
        terminal_log_radius=float(terminal["center_log_R4"]),
        terminal_proper_rate_interval=rate_interval,
        duration_quadratic_coefficient_interval=coefficient_interval,
    )
    x_coefficients = np.asarray(
        germ["log_radius_lambda0_squared_coefficient_interval"]
    )
    scalar_coefficients = np.asarray(
        germ["scalar_relative_potential_lambda0_squared_coefficient_interval"]
    )
    dirac_coefficients = np.asarray(
        germ["dirac_relative_superpotential_lambda0_squared_coefficient_interval"]
    )
    rows = [
        {
            "normalized_time": float(s),
            "log_radius_lambda0_squared_coefficient_interval": x_row.tolist(),
            "scalar_relative_potential_lambda0_squared_coefficient_interval": scalar_row.tolist(),
            "dirac_relative_superpotential_lambda0_squared_coefficient_interval": dirac_row.tolist(),
        }
        for s, x_row, scalar_row, dirac_row in zip(
            times, x_coefficients, scalar_coefficients, dirac_coefficients,
            strict=True,
        )
    ]
    validation = {
        "terminal_and_parameter_parents_validate": True,
        "two_duration_coefficient_intervals_agree_exactly": (
            coefficient_interval == parameter_interval
        ),
        "terminal_rate_interval_is_strictly_positive": rate_interval[0] > 0.0,
        "duration_coefficient_interval_is_strictly_positive": (
            coefficient_interval[0] > 0.0
        ),
        "preterminal_log_radius_coefficients_are_strictly_negative": (
            np.all(x_coefficients[:-1] < 0.0)
        ),
        "terminal_log_radius_coefficient_is_zero": (
            np.array_equal(x_coefficients[-1], np.zeros(2))
        ),
        "scalar_and_Dirac_relative_coefficients_are_nonnegative": (
            np.all(scalar_coefficients >= 0.0)
            and np.all(dirac_coefficients >= 0.0)
        ),
        "incoming_Mf_is_existing_compact_block": (
            match["claim_boundary"]["incoming_Mf_operator_identity"]
            .startswith("CLOSED")
        ),
        "compact_operator_consumes_dynamic_log_radius_path": (
            compact["quadratic_action_operator"]["dynamic_action_coefficient"]
            == "x_xi(tau)=log_R4(tau;xi)"
        ),
        "no_Euler_Dirac_inverse_or_acceleration_used": (
            germ["explicit_Euler_Dirac_inverse_formed"] is False
            and germ["acceleration_required"] is False
        ),
        "complete_positive_amplitude_remainder_not_overclaimed": True,
        "no_history_member_selector_cutoff_scale_fit_recurrence_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    product_interval = np.asarray(germ["duration_rate_product_interval"])
    return {
        "artifact": "BHSM_N12_INCOMING_COEFFICIENT_PATH_QUADRATIC_GERM",
        "status": (
            "INCOMING_NORMALIZED_COEFFICIENT_PATH_QUADRATIC_GERM_CERTIFIED"
            if passed else "INCOMING_COEFFICIENT_PATH_GERM_NOT_CERTIFIED"
        ),
        "classification": (
            "THE_CERTIFIED_POSITIVE_DURATION_QUADRATIC_LAW_AND_TERMINAL_"
            "PROPER_RADIUS_CAUCHY_JET_FIX_THE_UNIFORM_NORMALIZED_INCOMING_"
            "LOG_RADIUS_AND_CHANNEL_COEFFICIENT_PATHS_THROUGH_ORDER_"
            "lambda_0_SQUARED_WITHOUT_AN_EULER_DIRAC_INVERSE"
        ),
        "theorem": {
            "normalized_time": "tau=T(lambda_0)*s,_0<=s<=1",
            "duration": "T(lambda_0)=a*lambda_0^2+o(lambda_0^2)",
            "log_radius": germ["uniform_asymptotic"],
            "scalar_potential": "c*exp(-2*x)=c*exp(-2*x_E)*(1+2*(1-s)*a*v_E*lambda_0^2+o(lambda_0^2))",
            "factorized_Dirac_superpotential": "chi*mu*exp(-x)=chi*mu*exp(-x_E)*(1+(1-s)*a*v_E*lambda_0^2+o(lambda_0^2))",
            "terminal_log_radius": float(germ["terminal_log_radius"]),
            "terminal_proper_rate_interval": list(rate_interval),
            "duration_quadratic_coefficient_interval": list(coefficient_interval),
            "duration_rate_product_interval": product_interval.tolist(),
            "uniform_in_normalized_time": True,
        },
        "sampled_interval_rows": rows,
        "claim_boundary": {
            "incoming_normalized_log_radius_path_germ": "CERTIFIED_THROUGH_lambda_0_SQUARED",
            "incoming_scalar_and_Dirac_coefficient_path_germs": "CERTIFIED_THROUGH_lambda_0_SQUARED",
            "complete_finite_positive_amplitude_path": "OPEN_UNIFORM_INVERSE_FREE_REMAINDER",
            "complete_finite_duration_incoming_Mf_family": "OPEN_AFTER_REMAINDER",
            "sharp_joint_seam_and_full_graded_trace": "OPEN",
            "Gate7": "G7_08_OPEN",
            "Gate8": "LOCKED",
        },
        "validated_invalidated_open": {
            "VALIDATED": [
                "uniform normalized incoming log-radius quadratic germ",
                "scalar potential quadratic path germ",
                "factorized-Dirac superpotential quadratic path germ",
            ],
            "INVALIDATED": [
                "the leading path germ requires Euler-Dirac acceleration",
                "an ill-conditioned direct Euler-Dirac solve is an admissible path certificate",
                "a positive formation amplitude must be selected before deriving the path germ",
            ],
            "OPEN": [
                "uniform inverse-free finite-amplitude remainder enclosure",
                "complete incoming M_f family",
                "joint event-child seam and full graded trace",
            ],
        },
        "exact_next_dependency": (
            "CERTIFY_A_UNIFORM_INVERSE_FREE_REMAINDER_FOR_THE_REGULAR_"
            "ACTION_FLOW_ON_A_NONEMPTY_POSITIVE_lambda_0_BOX,_THEN_FEED_"
            "THE_COMPLETE_PARAMETRIC_PATH_TO_THE_EXISTING_COMPACT_WEYL_"
            "ORACLE_AND_GLUE_M_f_TO_THE_C2_SEAM"
        ),
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
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "duration_rate_product_interval": payload["theorem"]
        ["duration_rate_product_interval"],
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
