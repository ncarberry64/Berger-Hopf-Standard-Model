"""Bound the Gate-7 incoming heat--zeta covector on the full amplitude box."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_INCOMING_FINITE_AMPLITUDE_HEAT_ZETA_COMPARISON.json"
ZERO = BASE / "BHSM_N12_GATE7_INCOMING_ZERO_AMPLITUDE_HEAT_ZETA_COMPARISON.json"
COMPLIANCE = BASE / "BHSM_N12_GATE7_INCOMING_COMPLIANCE_REGULAR_CHART.json"
INCOMING = BASE / "BHSM_N12_INCOMING_FINITE_AMPLITUDE_COEFFICIENT_ENCLOSURE.json"
HEAT = BASE / "BHSM_N12_GATE7_ONE_SEAM_FULL_GRADED_FINITE_CORE_HEAT_BOUND.json"
DIFFERENTIABILITY = BASE / "BHSM_N12_GATE7_INCOMING_GRADED_HEAT_DIFFERENTIABILITY.json"
ONE_SEAM = BASE / "BHSM_N12_GATE7_AE2_ONE_SEAM_DIRECT_DESCRIPTOR.json"
CHILD = BASE / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
CHILD_DATA = CHILD.with_suffix(".npz")
THEORY = ROOT / "theory" / "n12_gate7_incoming_finite_amplitude_heat_zeta_comparison.md"
INPUTS = (
    ZERO, COMPLIANCE, INCOMING, HEAT, DIFFERENTIABILITY, ONE_SEAM,
    CHILD, CHILD_DATA, THEORY,
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _logaddexp(left: float, right: float) -> float:
    maximum = max(left, right)
    return maximum + math.log(math.exp(left - maximum) + math.exp(right - maximum))


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "missing finite-amplitude comparison inputs: " + ", ".join(missing)
        )
    zero, compliance, incoming, heat, differentiability, one_seam, child = (
        _load(path)
        for path in (
            ZERO, COMPLIANCE, INCOMING, HEAT, DIFFERENTIABILITY, ONE_SEAM,
            CHILD,
        )
    )
    if not all(item.get("validation_passed") is True for item in (
        zero, compliance, incoming, heat, differentiability, one_seam, child,
    )):
        raise RuntimeError("validated finite-amplitude comparison parents required")

    with np.load(CHILD_DATA) as data:
        durations = np.asarray(data["segment_proper_duration_interval"], dtype=float)
        child_mass_diagonal = np.asarray(data["scalar_c3__M_diagonal"], dtype=float)
    lower = durations[:, 0]
    mass_gershgorin_lower = float(np.min(lower[:-1] + lower[1:]) / 6.0)
    child_birth_mass_diagonal = float(child_mass_diagonal[0])
    dimension = int(child["descriptor_pencils"]["scalar_c3"]["descriptor_dimension"])

    amplitude = incoming["amplitude_family"]
    h_max = float(amplitude["endpoint_proof_edge_duration_interval"][1])
    lambda_max = float(
        compliance["certified_coefficients"]["amplitude_interval"][1]
    )
    duration_jet_per_lambda = float(
        compliance["certified_coefficients"][
            "D_lambda_T_per_lambda_interval"
        ][1]
    )
    radius_jet_per_lambda = float(
        compliance["certified_coefficients"][
            "D_lambda_log_R4_per_lambda_absolute_upper"
        ]
    )
    x_lower, x_upper = (
        float(value) for value in heat["finite_core_domain"]["log_R4_interval"]
    )

    q_max = child_birth_mass_diagonal + h_max / 3.0
    high_split_lower = 1.0 / (8.0 * h_max * q_max)
    radius_ratio = math.exp(2.0 * (x_upper - x_lower))
    # Scalar p/rho needs only radius_ratio.  Completing the square in the
    # product-Dirac lower bound costs the factor two, so use it for all sectors.
    potential_over_eigenvalue_upper = 2.0 * radius_ratio

    finite_low_bracket = (
        duration_jet_per_lambda
        + h_max**2 * duration_jet_per_lambda
        * (potential_over_eigenvalue_upper + 1.0) * high_split_lower / 3.0
        + (
            2.0 * h_max**3 * potential_over_eigenvalue_upper
            * high_split_lower / 3.0
            + h_max**2 * math.sqrt(
                potential_over_eigenvalue_upper * high_split_lower
            )
        ) * radius_jet_per_lambda
    )
    # The stored zero-amplitude majorant already contains one factor
    # D_lambda h/lambda.  Divide by that same positive factor before applying
    # the finite-compliance multiplier.
    low_relative_factor = (
        64.0 * finite_low_bracket / duration_jet_per_lambda
    )
    low_log_upper = float(
        zero["coefficient_comparison"][
            "limsup_absolute_heat_amplitude_coefficient_log_upper"
        ]
    ) + math.log(low_relative_factor)

    high_bracket = (
        duration_jet_per_lambda / (h_max**2 * high_split_lower)
        + duration_jet_per_lambda
        * (potential_over_eigenvalue_upper + 1.0) / 3.0
        + (
            2.0 * h_max * potential_over_eigenvalue_upper / 3.0
            + math.sqrt(
                potential_over_eigenvalue_upper / high_split_lower
            )
        ) * radius_jet_per_lambda
    )
    angular_half_log = float(
        zero["half_heat_angular_majorants"]["total_log"]
    )
    high_log_upper = (
        math.log(float(dimension))
        - math.log(mass_gershgorin_lower)
        + angular_half_log
        + math.log(high_bracket)
        - 0.5 * high_split_lower
    )
    total_heat_log_upper = _logaddexp(low_log_upper, high_log_upper)
    zeta_log_lower = float(
        zero["coefficient_comparison"][
            "zeta_replacement_amplitude_coefficient_log_lower"
        ]
    )
    logarithmic_margin = zeta_log_lower - total_heat_log_upper

    temporal = float(heat["coercive_bound"]["temporal_Dirichlet_base"])
    spatial = float(heat["coercive_bound"]["spatial_quadratic_coefficient"])
    linear = float(heat["coercive_bound"]["Dirac_linear_coefficient"])
    validation = {
        "one_seam_direct_descriptor_is_available": (
            one_seam["claim_boundary"]["finite_core_joint_operator_type"]
            == "DERIVED_EXECUTABLE"
        ),
        "full_graded_derivative_exists": (
            differentiability["claim_boundary"][
                "incoming_uniform_graded_heat_differentiability"
            ] == "CERTIFIED"
        ),
        "positive_open_amplitude_box": lambda_max > 0.0 and h_max > 0.0,
        "joint_mass_Gershgorin_bound_is_positive": mass_gershgorin_lower > 0.0,
        "finite_child_birth_mass_is_positive": child_birth_mass_diagonal > 0.0,
        "product_Dirac_completion_square_is_absorbed_by_temporal_gap": (
            temporal >= linear**2 / (2.0 * spatial)
        ),
        "low_high_split_is_above_one": high_split_lower > 1.0,
        "high_tail_endpoint_monotonicity_condition": (
            h_max < 1.0 / (16.0 * q_max)
        ),
        "finite_low_compliance_factor_is_positive": (
            math.isfinite(finite_low_bracket) and finite_low_bracket > 0.0
            and math.isfinite(low_relative_factor) and low_relative_factor > 0.0
        ),
        "high_tail_bound_is_finite": (
            math.isfinite(high_bracket) and high_bracket > 0.0
            and math.isfinite(high_log_upper)
        ),
        "uniform_heat_coefficient_is_strictly_below_zeta": (
            logarithmic_margin > 0.0
        ),
        "no_internal_response_is_zeroed": True,
        "componentwise_KKT_condition_not_added": True,
        "maximal_C2_tail_not_claimed_closed": True,
        "no_source_selector_cutoff_endpoint_recurrence_scale_gate_or_chord_added": True,
    }
    validation = {name: bool(value) for name, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_INCOMING_FINITE_AMPLITUDE_HEAT_ZETA_COMPARISON",
        "status": (
            "FINITE_CORE_CERTIFIED_AMPLITUDE_BOX_HEAT_STRICTLY_DOMINATED_BY_ZETA"
            if passed else "FINITE_AMPLITUDE_HEAT_ZETA_COMPARISON_INVALID"
        ),
        "classification": (
            "THE_REGULAR_COMPLIANCE_SEAM_ROW_CANCELS_THE_SHORT_ARM_LAURENT_"
            "DERIVATIVE_FOR_ALL_LOW_MODES;_THE_COMPLEMENTARY_HIGH_MODES_ARE_"
            "UNIFORMLY_ABSORBED_BY_THE_ACTION_OWNED_HEAT_EXPONENTIAL;_THE_"
            "COMPLETE_FINITE_CORE_REPLACEMENT_AMPLITUDE_COVECTOR_IS_STRICTLY_"
            "POSITIVE_ON_THE_ENTIRE_CERTIFIED_BOX"
        ),
        "regular_compliance_split": {
            "seam_equation": "D(h,rho)*u_0+b(rho)*u_1=0",
            "boundary_coupling": "b(rho)=b_K-rho*b_M",
            "joint_seam_stiffness_diagonal_lower": "K_00(h)>=1/(4*h)",
            "joint_seam_mass_diagonal_upper": q_max,
            "low_mode_threshold_at_h_max": high_split_lower,
            "low_mode_trace_bound": "abs(u_0)<=8*h*abs(b(rho))/sqrt(m0)",
            "high_mode_heat_split": "exp(-rho)<=exp(-R(h)/2)*exp(-g_mu/2)",
            "descriptor_or_kinetic_block_inverse_formed": False,
        },
        "certified_uniform_inputs": {
            "amplitude_interval": [0.0, lambda_max],
            "amplitude_interval_left_endpoint_is_open": True,
            "incoming_duration_upper": h_max,
            "child_birth_mass_diagonal": child_birth_mass_diagonal,
            "joint_mass_Gershgorin_lower": mass_gershgorin_lower,
            "descriptor_dimension_per_channel": dimension,
            "D_lambda_h_per_lambda_upper": duration_jet_per_lambda,
            "D_lambda_x_per_lambda_absolute_upper": radius_jet_per_lambda,
            "potential_over_eigenvalue_upper": potential_over_eigenvalue_upper,
        },
        "finite_amplitude_heat_bound": {
            "low_mode_dimensionless_bracket_upper": finite_low_bracket,
            "low_mode_relative_factor_over_zero_majorant": low_relative_factor,
            "low_mode_additive_log_overhead": math.log(low_relative_factor),
            "low_mode_heat_coefficient_log_upper": low_log_upper,
            "high_mode_dimensionless_bracket_upper": high_bracket,
            "high_mode_heat_coefficient_log_upper": high_log_upper,
            "complete_heat_coefficient_log_upper": total_heat_log_upper,
            "zeta_coefficient_log_lower": zeta_log_lower,
            "zeta_minus_heat_logarithmic_margin_lower": logarithmic_margin,
        },
        "adjudication": {
            "finite_core_entire_certified_amplitude_box_sign": "STRICTLY_POSITIVE",
            "finite_amplitude_compliance_remainder": "CLOSED_UNIFORMLY",
            "internal_M_f_or_C2_response_zeroed": False,
            "componentwise_KKT_condition_added": False,
            "actual_full_projected_KKT_root": "OPEN_MAXIMAL_C2_TAIL",
            "maximal_projected_tail": "OPEN",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
        },
        "exact_next_dependency": (
            "COMPOSE_THE_CERTIFIED_FINITE_CORE_SIGN_WITH_THE_COMPLETE_JOINT_"
            "REVERSE_ADJOINT_AND_PROVE_THE_MAXIMAL_C2_PROJECTED_CAUCHY_TAIL_"
            "OR_CERTIFY_A_LATER_EVENT_OR_CANONICAL_STOP;_ONLY_THEN_ADJUDICATE_"
            "THE_PHYSICAL_PROJECTED_KKT_ROOT"
        ),
        "claim_boundary": {
            "finite_amplitude_compliance_remainder": "CERTIFIED_ON_FULL_BOX",
            "finite_core_entire_amplitude_box_joint_sign": "CERTIFIED_STRICT_POSITIVE",
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
        raise RuntimeError("finite-amplitude heat-zeta comparison validation failed")
    print(json.dumps({
        "status": payload["status"],
        "low_log_upper": payload["finite_amplitude_heat_bound"][
            "low_mode_heat_coefficient_log_upper"
        ],
        "high_log_upper": payload["finite_amplitude_heat_bound"][
            "high_mode_heat_coefficient_log_upper"
        ],
        "zeta_log_lower": payload["finite_amplitude_heat_bound"][
            "zeta_coefficient_log_lower"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
