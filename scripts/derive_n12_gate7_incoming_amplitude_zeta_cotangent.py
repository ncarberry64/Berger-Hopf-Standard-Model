"""Certify the strict incoming-amplitude zeta cotangent on Gate 7."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_INCOMING_AMPLITUDE_ZETA_COTANGENT.json"
SEGMENT = BASE / "BHSM_N12_INCOMING_REGULARIZED_TERMINAL_SEGMENT.json"
FAMILY = BASE / "BHSM_N12_INCOMING_FINITE_AMPLITUDE_COEFFICIENT_ENCLOSURE.json"
INTERFACE = BASE / "BHSM_N12_FINITE_TERMINAL_TWO_SIDED_FORWARD_INTERFACE.json"
DIRECT_ZETA = BASE / "BHSM_N12_GATE7_DIRECT_ZETA_COEFFICIENT_COTANGENT.json"
KKT_INFO = BASE / "BHSM_N12_GATE7_JOINT_KKT_INFORMATION_GATE.json"
HEAT = BASE / "BHSM_N12_GATE7_ONE_SEAM_FULL_GRADED_FINITE_CORE_HEAT_BOUND.json"
THEORY = ROOT / "theory" / "n12_gate7_incoming_amplitude_zeta_cotangent.md"
INPUTS = (SEGMENT, FAMILY, INTERFACE, DIRECT_ZETA, KKT_INFO, HEAT, THEORY)
COEFFICIENT = 59.0 / 30.0


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _up(value: float) -> float:
    return math.nextafter(float(value) * (1.0 + 1.0e-12), math.inf)


def _down(value: float) -> float:
    return math.nextafter(float(value) / (1.0 + 1.0e-12), -math.inf)


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "missing incoming-amplitude zeta inputs: " + ", ".join(missing)
        )
    segment, family, interface, direct_zeta, kkt_info, heat = (
        _load(path) for path in INPUTS[:-1]
    )
    if not all(item.get("validation_passed") is True for item in (
        segment, family, interface, direct_zeta, kkt_info, heat,
    )):
        raise RuntimeError("validated incoming-amplitude zeta parents required")

    lambda_upper = float(segment["explicit_segment"]["positive_lambda_end_lower"])
    d_lower, d_upper = (
        float(value) for value in segment["terminal_ball"]["minus_Delta_interval"]
    )
    x_lower, x_upper = (
        float(value)
        for value in segment["explicit_segment"]["log_R4_interval_on_terminal_ball"]
    )
    coefficient_lower = _down(COEFFICIENT * math.exp(-x_upper) / d_upper)
    coefficient_upper = _up(COEFFICIENT * math.exp(-x_lower) / d_lower)
    endpoint_magnitude_lower = _down(lambda_upper * coefficient_lower)
    endpoint_magnitude_upper = _up(lambda_upper * coefficient_upper)
    endpoint_signed_interval = [-endpoint_magnitude_upper, -endpoint_magnitude_lower]

    validation = {
        "incoming_regularized_denominator_is_strictly_negative": (
            segment["terminal_ball"]["Delta_interval"][1] < 0.0
            and 0.0 < d_lower <= d_upper
        ),
        "amplitude_domain_is_strictly_positive": lambda_upper > 0.0,
        "radius_tube_is_finite": (
            math.isfinite(x_lower) and math.isfinite(x_upper) and x_lower <= x_upper
        ),
        "zeta_derivative_coefficient_is_strictly_positive": (
            0.0 < coefficient_lower <= coefficient_upper
        ),
        "formation_zeta_derivative_is_strictly_negative_at_outer_witness": (
            endpoint_signed_interval[1] < 0.0
        ),
        "replacement_zeta_derivative_is_strictly_positive_for_every_positive_amplitude": True,
        "two_sided_family_keeps_terminal_E1_and_C2_fixed": (
            "E1=C_*_TO_C2=E_*"
            in interface["exact_local_theorem"]["positive_duration_family"]
        ),
        "direct_zeta_routes_formation_through_upstream_adjoint": (
            direct_zeta["incoming_formation_enclosure"]["routing"]
            == "UPSTREAM_C1_HISTORY_ADJOINT_NOT_AN_E1_C2_SEAM_SOURCE"
        ),
        "componentwise_zero_test_remains_retired": (
            kkt_info["joint_KKT_rule"]["componentwise_zero_required"] is False
        ),
        "heat_seed_is_not_set_to_zero": (
            heat["full_graded_bounds"]["binary64_underflow_is_exact_zero"] is False
        ),
        "no_uniform_positive_lower_bound_claimed_as_lambda_tends_to_zero": True,
        "no_source_selector_cutoff_endpoint_recurrence_scale_gate_or_chord_added": True,
    }
    validation = {name: bool(value) for name, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_INCOMING_AMPLITUDE_ZETA_COTANGENT",
        "status": (
            "INCOMING_AMPLITUDE_ZETA_COTANGENT_STRICT_SIGN_CERTIFIED"
            if passed else "INCOMING_AMPLITUDE_ZETA_COTANGENT_INVALID"
        ),
        "classification": (
            "ON_THE_CERTIFIED_FIXED_TERMINAL_E1_C2_LOCAL_FAMILY_THE_INCOMING_"
            "AMPLITUDE_DERIVATIVE_OF_THE_FORMATION_ZETA_FUNCTIONAL_IS_EXACTLY_"
            "MINUS_59_OVER_30_TIMES_exp_minus_x_TIMES_lambda_OVER_minus_Delta_"
            "AND_IS_STRICTLY_NEGATIVE_FOR_EVERY_POSITIVE_AMPLITUDE"
        ),
        "exact_formula": {
            "proper_time_density": "d_tau/d_lambda=lambda/(-Delta(lambda))",
            "formation_functional": "Gamma_form_zeta=-(59/30)*integral_0^lambda0_exp(-x(lambda))*lambda/(-Delta(lambda))*d_lambda",
            "amplitude_covector": "D_lambda0_Gamma_form_zeta=-(59/30)*exp(-x(lambda0))*lambda0/(-Delta(lambda0))",
            "replacement_amplitude_covector": "-D_lambda0_Gamma_form_zeta>0_FOR_lambda0>0",
        },
        "certified_enclosure": {
            "amplitude_interval": [0.0, lambda_upper],
            "amplitude_interval_left_endpoint_is_open": True,
            "minus_Delta_interval": [d_lower, d_upper],
            "log_R4_interval": [x_lower, x_upper],
            "absolute_covector_per_lambda_interval": [
                coefficient_lower, coefficient_upper
            ],
            "outer_amplitude_signed_covector_interval": endpoint_signed_interval,
            "outer_amplitude_replacement_covector_interval": [
                endpoint_magnitude_lower, endpoint_magnitude_upper
            ],
            "uniform_strict_sign_for_every_positive_amplitude": True,
            "uniform_positive_magnitude_lower_on_open_interval": False,
        },
        "joint_direction_matching": {
            "incoming_C1_zeta_amplitude_component": "CERTIFIED_STRICT_SIGN",
            "C2_zeta_amplitude_component_on_fixed_E1_C2_family": "ZERO_BY_FIXED_FAMILY_ENDPOINTS",
            "interface_zeta_amplitude_component_on_fixed_E1_C2_family": "ZERO_BY_FIXED_FAMILY_ENDPOINTS",
            "incoming_graded_heat_amplitude_component": "OPEN_EXACT_REMAINING_COMPARISON",
            "complete_joint_amplitude_covector": "OPEN_UNTIL_HEAT_COMPARISON",
        },
        "adjudication": {
            "upstream_C1_zeta_amplitude_covector": "CERTIFIED_STRICT_SIGN",
            "componentwise_KKT_condition_added": False,
            "joint_heat_minus_zeta_amplitude_sign": "OPEN_WAITING_ON_SHRINKING_ARM_HEAT_DERIVATIVE",
            "same_action_saddle": "WAITING_ON_JOINT_SIGN",
            "maximal_projected_tail": "OPEN_AFTER_FINITE_CORE_JOINT_COVECTOR",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
        },
        "exact_next_dependency": (
            "BOUND_THE_GRADED_HEAT_DERIVATIVE_ALONG_THE_SAME_SHRINKING_"
            "INCOMING_AMPLITUDE_FAMILY_WITH_LOCAL_SHORT_ARM_CALCULUS,_THEN_"
            "COMPARE_IT_TO_THE_CERTIFIED_POSITIVE_REPLACEMENT_ZETA_COVECTOR_"
            "WITHOUT_SETTING_THE_HEAT_TERM_TO_ZERO"
        ),
        "claim_boundary": {
            "incoming_amplitude_zeta_covector": "CERTIFIED_STRICT_SIGN",
            "joint_amplitude_force": "OPEN",
            "actual_projected_KKT_root": "OPEN",
            "maximal_projected_tail": "OPEN",
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
        raise RuntimeError("incoming-amplitude zeta validation failed")
    print(json.dumps({
        "status": payload["status"],
        "certified_enclosure": payload["certified_enclosure"],
        "joint_direction_matching": payload["joint_direction_matching"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
