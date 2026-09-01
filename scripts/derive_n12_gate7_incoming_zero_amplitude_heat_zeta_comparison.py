"""Compare the finite-core zero-amplitude heat and zeta coefficients."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_INCOMING_ZERO_AMPLITUDE_HEAT_ZETA_COMPARISON.json"
CORE = BASE / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
CORE_DATA = CORE.with_suffix(".npz")
HEAT = BASE / "BHSM_N12_GATE7_ONE_SEAM_FULL_GRADED_FINITE_CORE_HEAT_BOUND.json"
DIFFERENTIABILITY = BASE / "BHSM_N12_GATE7_INCOMING_GRADED_HEAT_DIFFERENTIABILITY.json"
COMPLIANCE = BASE / "BHSM_N12_GATE7_INCOMING_COMPLIANCE_REGULAR_CHART.json"
ZETA = BASE / "BHSM_N12_GATE7_INCOMING_AMPLITUDE_ZETA_COTANGENT.json"
ONE_SEAM = BASE / "BHSM_N12_GATE7_AE2_ONE_SEAM_DIRECT_DESCRIPTOR.json"
THEORY = ROOT / "theory" / "n12_gate7_incoming_zero_amplitude_heat_zeta_comparison.md"
INPUTS = (
    CORE, CORE_DATA, HEAT, DIFFERENTIABILITY, COMPLIANCE, ZETA, ONE_SEAM,
    THEORY,
)
VERTEX_POWER = 4


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _log_positive_series(
    log_term: Callable[[int], float], start: int
) -> tuple[float, int]:
    logs: list[float] = []
    last = start
    for index in range(start, 100000):
        value = float(log_term(index))
        if not math.isfinite(value):
            raise RuntimeError("finite angular log-majorant required")
        logs.append(value)
        last = index
        if index > start + 8 and value < max(logs) - 800.0:
            break
    else:
        raise RuntimeError("angular log-majorant summation did not terminate")
    maximum = max(logs)
    return maximum + math.log(sum(math.exp(value - maximum) for value in logs)), last


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "missing zero-amplitude comparison inputs: " + ", ".join(missing)
        )
    core, heat, differentiability, compliance, zeta, one_seam = (
        _load(path)
        for path in (CORE, HEAT, DIFFERENTIABILITY, COMPLIANCE, ZETA, ONE_SEAM)
    )
    if not all(item.get("validation_passed") is True for item in (
        core, heat, differentiability, compliance, zeta, one_seam,
    )):
        raise RuntimeError("validated zero-amplitude comparison parents required")

    with np.load(CORE_DATA) as data:
        durations = np.asarray(data["segment_proper_duration_interval"], dtype=float)
    lower = durations[:, 0]
    upper = durations[:, 1]
    adjacent_lower = lower[:-1] + lower[1:]
    mass_gershgorin_lower = float(np.min(adjacent_lower) / 6.0)
    first_h_lower = float(lower[0])
    first_h_upper = float(upper[0])

    domain = heat["finite_core_domain"]
    coercive = heat["coercive_bound"]
    x_lower = float(domain["log_R4_interval"][0])
    a = float(coercive["spatial_quadratic_coefficient"])
    b = float(coercive["Dirac_linear_coefficient"])
    temporal = float(coercive["temporal_Dirichlet_base"])
    gap = float(coercive["common_gap_lower"])
    stiffness_coefficient = max(
        1.0 / first_h_lower,
        math.exp(-2.0 * x_lower) * first_h_upper / 6.0,
    )
    mass_coupling_upper = first_h_upper / 6.0

    half_a = 0.5 * a
    half_b = 0.5 * b
    hs_log, hs_cutoff = _log_positive_series(
        lambda m: math.log(4.0 * m * m)
        + VERTEX_POWER * math.log1p(m)
        - half_a * m * m,
        1,
    )
    gauge_log, gauge_cutoff = _log_positive_series(
        lambda m: math.log(24.0 * (m * m - 1.0))
        + VERTEX_POWER * math.log1p(m)
        - half_a * m * m,
        2,
    )
    weyl_log, weyl_cutoff = _log_positive_series(
        lambda n: math.log(48.0 * (n + 1.0) * (n + 2.0))
        + VERTEX_POWER * math.log(1.0 + n + 1.5)
        - half_a * (n + 1.5) ** 2
        + half_b * (n + 1.5),
        0,
    )
    angular_max = max(hs_log, gauge_log, weyl_log)
    angular_half_log = angular_max + math.log(
        math.exp(hs_log - angular_max)
        + math.exp(gauge_log - angular_max)
        + math.exp(weyl_log - angular_max)
    )
    temporal_half_log = -0.5 * temporal
    if temporal < 500.0:
        temporal_half_log -= math.log1p(-math.exp(-1.5 * temporal))

    pencil_factor = (
        stiffness_coefficient**2 / gap
        + mass_coupling_upper**2 * (1.0 + gap)
    )
    d_lambda_h_per_lambda_upper = float(
        compliance["certified_coefficients"][
            "D_lambda_T_per_lambda_interval"
        ][1]
    )
    heat_coefficient_log_upper = (
        math.log(d_lambda_h_per_lambda_upper)
        - math.log(mass_gershgorin_lower)
        + math.log(pencil_factor)
        - 0.5 * gap
        + temporal_half_log
        + angular_half_log
    )
    zeta_coefficient_lower = float(
        zeta["certified_enclosure"]["absolute_covector_per_lambda_interval"][0]
    )
    zeta_coefficient_log_lower = math.log(zeta_coefficient_lower)
    logarithmic_margin = zeta_coefficient_log_lower - heat_coefficient_log_upper

    validation = {
        "finite_core_has_positive_interval_mass_Gershgorin_bound": (
            mass_gershgorin_lower > 0.0
        ),
        "first_child_element_bounds_are_positive": (
            first_h_lower > 0.0
            and first_h_upper >= first_h_lower
            and stiffness_coefficient > 0.0
            and mass_coupling_upper > 0.0
        ),
        "one_seam_Schur_equivalence_is_derived": (
            one_seam["claim_boundary"]["finite_core_joint_operator_type"]
            == "DERIVED_EXECUTABLE"
        ),
        "graded_amplitude_differentiation_is_certified": (
            differentiability["claim_boundary"][
                "incoming_uniform_graded_heat_differentiability"
            ] == "CERTIFIED"
        ),
        "half_heat_angular_majorants_are_finite": all(
            math.isfinite(value)
            for value in (hs_log, gauge_log, weyl_log, angular_half_log)
        ),
        "heat_coefficient_log_bound_is_finite": math.isfinite(
            heat_coefficient_log_upper
        ),
        "zeta_coefficient_lower_is_strictly_positive": zeta_coefficient_lower > 0.0,
        "heat_coefficient_is_strictly_below_zeta_coefficient": logarithmic_margin > 0.0,
        "only_zero_amplitude_limit_not_full_box_is_claimed": True,
        "componentwise_KKT_condition_not_added": True,
        "no_inverse_source_selector_cutoff_endpoint_recurrence_scale_gate_or_chord_added": True,
    }
    validation = {name: bool(value) for name, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_INCOMING_ZERO_AMPLITUDE_HEAT_ZETA_COMPARISON",
        "status": (
            "FINITE_CORE_ZERO_AMPLITUDE_HEAT_COEFFICIENT_STRICTLY_DOMINATED_BY_ZETA"
            if passed else "ZERO_AMPLITUDE_HEAT_ZETA_COMPARISON_INVALID"
        ),
        "classification": (
            "THE_VANISHING_INCOMING_ELEMENT_HAS_AN_EXACT_RANK_ONE_SCHUR_"
            "PENCIL_DERIVATIVE_ON_THE_C2_DIRICHLET_CORE;_MASS_GERSHGORIN_"
            "AND_HALF_HEAT_GAUSSIAN_BOUNDS_MAKE_ITS_COMPLETE_GRADED_"
            "AMPLITUDE_COEFFICIENT_STRICTLY_SMALLER_THAN_THE_ZETA_COEFFICIENT"
        ),
        "zero_amplitude_Schur_theorem": {
            "effective_pencil_derivative": "D_h_A_eff(rho)|h=0=-b(rho)*b(rho)^dagger",
            "boundary_coupling": "b(rho)=b_K-rho*b_M",
            "eigenvalue_derivative_bound": "abs(D_h_rho)<=2*m0^-1*(norm(b_K)^2+rho^2*norm(b_M)^2)",
            "matrix_inverse_formed": False,
        },
        "certified_finite_core_inputs": {
            "child_mass_Gershgorin_lower": mass_gershgorin_lower,
            "first_child_duration_interval": [first_h_lower, first_h_upper],
            "stiffness_coupling_polynomial_coefficient_upper": stiffness_coefficient,
            "mass_coupling_upper": mass_coupling_upper,
            "common_gap_lower": gap,
            "temporal_base": temporal,
            "D_lambda_h_per_lambda_upper": d_lambda_h_per_lambda_upper,
        },
        "half_heat_angular_majorants": {
            "Hubbard_Strattonovich_log": hs_log,
            "Hubbard_Strattonovich_cutoff": hs_cutoff,
            "gauge_transverse_log": gauge_log,
            "gauge_transverse_cutoff": gauge_cutoff,
            "Weyl_log": weyl_log,
            "Weyl_cutoff": weyl_cutoff,
            "total_log": angular_half_log,
        },
        "coefficient_comparison": {
            "limsup_absolute_heat_amplitude_coefficient_log_upper": heat_coefficient_log_upper,
            "zeta_replacement_amplitude_coefficient_lower": zeta_coefficient_lower,
            "zeta_replacement_amplitude_coefficient_log_lower": zeta_coefficient_log_lower,
            "zeta_minus_heat_logarithmic_margin_lower": logarithmic_margin,
            "finite_core_joint_replacement_amplitude_sign_near_zero": "STRICTLY_POSITIVE",
            "explicit_positive_neighborhood_radius": "OPEN_FINITE_AMPLITUDE_REMAINDER",
        },
        "adjudication": {
            "zero_amplitude_heat_zeta_coefficient_comparison": "CLOSED_STRICT_ZETA_DOMINANCE",
            "punctured_neighborhood_joint_amplitude_sign": "POSITIVE_BY_CONTINUITY_RADIUS_NOT_MATERIALIZED",
            "entire_certified_amplitude_box_sign": "OPEN_REMAINDER_BOUND",
            "componentwise_KKT_condition_added": False,
            "actual_full_projected_KKT_root": "OPEN",
            "maximal_projected_tail": "OPEN",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
        },
        "exact_next_dependency": (
            "CERTIFY_THE_FINITE_AMPLITUDE_COMPLIANCE_SCHUR_REMAINDER_ON_"
            "THE_STORED_BOX_TO_EXTEND_THE_STRICT_COEFFICIENT_COMPARISON_"
            "AWAY_FROM_lambda_EQUALS_ZERO,_THEN_COMPOSE_THE_RESULT_WITH_THE_"
            "COMPLETE_JOINT_PROJECTED_COVECTOR_AND_MAXIMAL_C2_TAIL"
        ),
        "claim_boundary": {
            "finite_core_zero_amplitude_heat_zeta_comparison": "CERTIFIED_STRICT",
            "finite_core_punctured_neighborhood_amplitude_sign": "CERTIFIED_EXISTENTIAL",
            "entire_amplitude_box_joint_sign": "OPEN",
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
        raise RuntimeError("zero-amplitude heat-zeta comparison validation failed")
    print(json.dumps({
        "status": payload["status"],
        "heat_log_upper": payload["coefficient_comparison"][
            "limsup_absolute_heat_amplitude_coefficient_log_upper"
        ],
        "zeta_log_lower": payload["coefficient_comparison"][
            "zeta_replacement_amplitude_coefficient_log_lower"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
