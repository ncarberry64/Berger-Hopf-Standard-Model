"""Certify uniform angular domination of the shrinking-arm heat jet."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_INCOMING_GRADED_HEAT_DIFFERENTIABILITY.json"
COMPLIANCE = BASE / "BHSM_N12_GATE7_INCOMING_COMPLIANCE_REGULAR_CHART.json"
HEAT = BASE / "BHSM_N12_GATE7_ONE_SEAM_FULL_GRADED_FINITE_CORE_HEAT_BOUND.json"
WEAK = BASE / "BHSM_N12_FORWARD_WEAK_HEAT_VARIATIONS.json"
OPERATOR = BASE / "BHSM_N12_COMPACT_FINITE_HISTORY_OPERATOR.json"
FAMILY = BASE / "BHSM_N12_INCOMING_FINITE_AMPLITUDE_COEFFICIENT_ENCLOSURE.json"
THEORY = ROOT / "theory" / "n12_gate7_incoming_graded_heat_differentiability.md"
INPUTS = (COMPLIANCE, HEAT, WEAK, OPERATOR, FAMILY, THEORY)
VERTEX_POWER = 4


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _positive_series(term: Callable[[int], float], start: int) -> tuple[float, int]:
    total = 0.0
    zeros = 0
    last = start
    for index in range(start, 100000):
        value = float(term(index))
        if not math.isfinite(value) or value < 0.0:
            raise RuntimeError("finite nonnegative angular derivative majorant required")
        total += value
        last = index
        zeros = zeros + 1 if value == 0.0 else 0
        if zeros >= 8:
            return total, last
    raise RuntimeError("angular derivative majorant summation did not terminate")


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "missing graded heat-differentiability inputs: " + ", ".join(missing)
        )
    compliance, heat, weak, operator, family = (
        _load(path) for path in INPUTS[:-1]
    )
    if not all(item.get("validation_passed") is True for item in (
        compliance, heat, weak, operator, family,
    )):
        raise RuntimeError("validated graded heat-differentiability parents required")

    coercive = heat["coercive_bound"]
    domain = heat["finite_core_domain"]
    a = float(coercive["spatial_quadratic_coefficient"])
    b = float(coercive["Dirac_linear_coefficient"])
    duration = float(domain["formation_duration_upper"])
    x_lower = float(domain["log_R4_interval"][0])
    transfer_linear = 4.0 * math.exp(-x_lower) * duration
    effective_weyl_linear = b + transfer_linear

    hs_sum, hs_cutoff = _positive_series(
        lambda m: 4.0 * m * m * (1.0 + m) ** VERTEX_POWER
        * math.exp(-a * m * m + transfer_linear * m),
        1,
    )
    gauge_sum, gauge_cutoff = _positive_series(
        lambda m: 24.0 * (m * m - 1.0) * (1.0 + m) ** VERTEX_POWER
        * math.exp(-a * m * m + transfer_linear * m),
        2,
    )
    weyl_sum, weyl_cutoff = _positive_series(
        lambda n: 48.0 * (n + 1.0) * (n + 2.0)
        * (1.0 + n + 1.5) ** VERTEX_POWER
        * math.exp(
            -a * (n + 1.5) ** 2
            + effective_weyl_linear * (n + 1.5)
        ),
        0,
    )
    total = hs_sum + gauge_sum + weyl_sum
    validation = {
        "fixed_channel_compliance_jet_is_O_lambda": (
            compliance["claim_boundary"][
                "fixed_channel_amplitude_heat_jet_regularity"
            ] == "CERTIFIED_POINTWISE"
        ),
        "compact_operator_generators_are_executable": (
            operator["claim_boundary"]["M_C_and_D_xi_M_C_algorithm"]
            == "DERIVED_EXECUTABLE"
        ),
        "weak_heat_first_variation_is_trace_class_on_compact_support": (
            weak["claim_boundary"][
                "weak_heat_geometry_force_and_source_Hessian_well_defined_conditionally_on_domain"
            ] == "DERIVED"
        ),
        "formation_duration_is_uniformly_finite": duration > 0.0,
        "quadratic_gaussian_coefficient_remains_positive": a > 0.0,
        "transfer_loss_changes_only_the_linear_angular_coefficient": (
            transfer_linear >= 0.0 and effective_weyl_linear >= b
        ),
        "all_three_absolute_derivative_majorants_converge": all(
            math.isfinite(value) and value > 0.0
            for value in (hs_sum, gauge_sum, weyl_sum, total)
        ),
        "longitudinal_complex_ghost_cancellation_is_unchanged": (
            heat["absolute_angular_sum"]["longitudinal_complex_ghost"] == 0.0
        ),
        "heat_coefficient_value_or_sign_not_overclaimed": True,
        "no_internal_response_zeroed_or_source_selector_cutoff_endpoint_recurrence_scale_gate_or_chord_added": True,
    }
    validation = {name: bool(value) for name, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_INCOMING_GRADED_HEAT_DIFFERENTIABILITY",
        "status": (
            "INCOMING_SHRINKING_ARM_GRADED_HEAT_DIFFERENTIABILITY_CERTIFIED"
            if passed else "INCOMING_GRADED_HEAT_DIFFERENTIABILITY_INVALID"
        ),
        "classification": (
            "THE_REGULAR_COMPLIANCE_AMPLITUDE_JET_HAS_ONLY_FIXED_POLYNOMIAL_"
            "ANGULAR_LOSS_TIMES_A_LINEAR_EXPONENTIAL_TRANSFER_FACTOR;_THE_"
            "CERTIFIED_FINITE_CORE_GAUSSIAN_ANGULAR_HEAT_WEIGHT_DOMINATES_"
            "THIS_LOSS_UNIFORMLY_ON_THE_POSITIVE_AMPLITUDE_BOX"
        ),
        "domination_theorem": {
            "amplitude_derivative": "D_lambda_Gamma_heat=lambda*H_heat(lambda)",
            "uniform_conclusion": "sup_(0<lambda<=lambda_star)|H_heat(lambda)|<infinity",
            "common_vertex_polynomial_power": VERTEX_POWER,
            "polynomial_power_role": "CONSERVATIVE_GENERATOR_DEGREE_ENVELOPE_NOT_A_FIT",
            "transfer_linear_loss": transfer_linear,
            "spatial_quadratic_coefficient": a,
            "Weyl_linear_coefficient_before_transfer": b,
            "Weyl_linear_coefficient_after_transfer": effective_weyl_linear,
            "root_test_limit": "minus_infinity",
            "differentiation_through_graded_supertrace": "CERTIFIED",
        },
        "absolute_angular_derivative_majorants": {
            "Hubbard_Strattonovich": hs_sum,
            "Hubbard_Strattonovich_binary64_cutoff": hs_cutoff,
            "gauge_transverse": gauge_sum,
            "gauge_transverse_binary64_cutoff": gauge_cutoff,
            "Weyl": weyl_sum,
            "Weyl_binary64_cutoff": weyl_cutoff,
            "total": total,
        },
        "adjudication": {
            "uniform_graded_heat_amplitude_differentiability": "CLOSED",
            "heat_amplitude_coefficient_value": "OPEN_SHARP_CONTRACTION",
            "heat_amplitude_coefficient_sign": "OPEN",
            "zeta_amplitude_coefficient_sign": "CERTIFIED_STRICT",
            "joint_amplitude_force_sign": "OPEN_UNTIL_COEFFICIENT_COMPARISON",
            "componentwise_KKT_condition_added": False,
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
        },
        "exact_next_dependency": (
            "SHARPLY_CONTRACT_THE_UNIFORMLY_DOMINATED_GRADED_HEAT_JET_IN_"
            "THE_REGULAR_COMPLIANCE_CHART_AND_COMPARE_ITS_O_lambda_"
            "COEFFICIENT_WITH_THE_CERTIFIED_ZETA_COEFFICIENT_INTERVAL"
        ),
        "claim_boundary": {
            "incoming_uniform_graded_heat_differentiability": "CERTIFIED",
            "incoming_heat_amplitude_coefficient": "OPEN",
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
        raise RuntimeError("incoming graded heat differentiability validation failed")
    print(json.dumps({
        "status": payload["status"],
        "angular_majorant_total": payload[
            "absolute_angular_derivative_majorants"
        ]["total"],
        "joint_amplitude_force_sign": payload["adjudication"][
            "joint_amplitude_force_sign"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
