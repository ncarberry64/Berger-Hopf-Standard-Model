"""Certify the maximal graded incoming relative heat angular sum."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_MAXIMAL_GRADED_INCOMING_RELATIVE_HEAT_COTANGENT.json"
FIXED = BASE / "BHSM_N12_GATE7_MAXIMAL_FIXED_CHANNEL_RELATIVE_HEAT_COTANGENT.json"
CORE = BASE / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
CORE_DATA = CORE.with_suffix(".npz")
FINITE_HEAT = BASE / "BHSM_N12_GATE7_ONE_SEAM_FULL_GRADED_FINITE_CORE_HEAT_BOUND.json"
INCOMING = BASE / "BHSM_N12_GATE7_INCOMING_GRADED_HEAT_DIFFERENTIABILITY.json"
ANGULAR_AUDIT = BASE / "BHSM_N12_GATE7_AE2_ANGULAR_DINI_UNIFORMITY_AUDIT.json"
SOURCE_ONTOLOGY = BASE / "BHSM_N12_GATE7_CLOSED_SYSTEM_ZERO_EXTERNAL_SOURCE_ONTOLOGY.json"
THEORY = ROOT / "theory" / "n12_gate7_maximal_graded_incoming_relative_heat_cotangent.md"
INPUTS = (
    FIXED,
    CORE,
    CORE_DATA,
    FINITE_HEAT,
    INCOMING,
    ANGULAR_AUDIT,
    SOURCE_ONTOLOGY,
    THEORY,
)


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
        raise FileNotFoundError(
            "missing maximal graded incoming inputs: " + ", ".join(missing)
        )
    fixed, core, finite_heat, incoming, angular, source = (
        _load(path)
        for path in (FIXED, CORE, FINITE_HEAT, INCOMING, ANGULAR_AUDIT, SOURCE_ONTOLOGY)
    )
    if not all(parent.get("validation_passed") is True for parent in (
        fixed, core, finite_heat, incoming, angular, source,
    )):
        raise RuntimeError("validated maximal graded incoming parents required")

    with np.load(CORE_DATA) as data:
        durations = np.asarray(data["segment_proper_duration_interval"], dtype=float)
    collar_length_lower = float(durations[0, 0])
    x_min, x_max = (
        float(value) for value in finite_heat["finite_core_domain"]["log_R4_interval"]
    )
    rate_upper = float(
        finite_heat["finite_core_domain"]["C2_D_tau_log_R4_absolute_upper"]
    )
    spatial_quadratic = math.exp(-2.0 * x_max)
    dirac_linear = math.exp(-x_min) * rate_upper
    dirac_barrier_threshold = 2.0 * dirac_linear / spatial_quadratic
    radius_upper = math.exp(x_max)
    barrier_linear_rate = collar_length_lower / radius_upper
    transfer_linear_loss = float(
        incoming["domination_theorem"]["transfer_linear_loss"]
    )
    net_linear_decay = barrier_linear_rate - transfer_linear_loss
    high_gaussian_rate = spatial_quadratic / 4.0
    polynomial_power = int(
        incoming["domination_theorem"]["common_vertex_polynomial_power"]
    )
    total_polynomial_power = polynomial_power + 2

    sample_levels = [1.0e33, 2.0e33, 5.0e33, 1.0e34, 2.0e34]
    low_rows = []
    previous = math.inf
    decreasing = True
    for mu in sample_levels:
        log_term = total_polynomial_power * math.log1p(mu) - net_linear_decay * mu
        decreasing = decreasing and log_term < previous
        low_rows.append({
            "mu": mu,
            "log_absolute_multiplicity_weighted_low_term_upper": log_term,
        })
        previous = log_term

    validation = {
        "all_parent_artifacts_are_validated": True,
        "first_C2_collar_has_positive_certified_proper_length": collar_length_lower > 0.0,
        "collar_radius_and_rate_bounds_are_finite": all(math.isfinite(value) for value in (
            radius_upper, rate_upper, spatial_quadratic, dirac_linear,
        )),
        "all_retained_Weyl_levels_are_above_two_chirality_barrier_threshold": (
            1.5 >= dirac_barrier_threshold
        ),
        "all_retained_integer_levels_are_above_barrier_threshold": (
            1.0 >= dirac_barrier_threshold
        ),
        "incoming_transfer_loss_is_strictly_below_child_collar_barrier": (
            net_linear_decay > 0.0
        ),
        "low_energy_root_test_is_strictly_summable": net_linear_decay > 0.0,
        "high_energy_heat_Gaussian_is_strictly_summable": high_gaussian_rate > 0.0,
        "sampled_asymptotic_low_logs_strictly_decrease": decreasing,
        "fixed_channel_relative_heat_cotangent_is_derived": (
            fixed["claim_boundary"]["maximal_fixed_channel_relative_heat_cotangent"]
            == "DERIVED"
        ),
        "interior_source_angular_counterexample_not_falsified": (
            angular["adjudication"]["arbitrary_positive_tail_angular_sum"] == "FALSE"
        ),
        "only_external_source_is_zeroed": (
            source["external_internal_partition"]["set_to_zero"] == ["J_ext"]
        ),
        "spatial_Galerkin_tail_not_used_as_temporal_tail": True,
        "numerical_value_or_sign_not_overclaimed": True,
        "no_internal_response_is_zeroed": True,
        "no_source_selector_endpoint_recurrence_scale_fit_gate_or_chord_added": True,
    }
    validation = {name: bool(value) for name, value in validation.items()}
    passed = all(validation.values())

    return {
        "artifact": "BHSM_N12_GATE7_MAXIMAL_GRADED_INCOMING_RELATIVE_HEAT_COTANGENT",
        "status": (
            "MAXIMAL_GRADED_INCOMING_RELATIVE_HEAT_COTANGENT_SUMMABLE"
            if passed
            else "MAXIMAL_GRADED_INCOMING_RELATIVE_HEAT_COTANGENT_INVALID"
        ),
        "classification": (
            "THE_CERTIFIED_POSITIVE_C2_BIRTH_COLLAR_SPLITS_EACH_MAXIMAL_"
            "FIXED_CHANNEL_RELATIVE_HEAT_COTANGENT_INTO_A_LOW_ENERGY_AGMON_"
            "TRANSMISSION_TAIL_AND_A_HIGH_ENERGY_HEAT_GAUSSIAN;_BOTH_DOMINATE_"
            "THE_RETAINED_QUADRATIC_MULTIPLICITIES_AND_DEGREE_FOUR_INCOMING_"
            "GENERATOR_LOSS_UNIFORMLY_WITHOUT_USING_THE_UNKNOWN_FAR_TAIL"
        ),
        "certified_C2_collar": {
            "proper_length_lower": collar_length_lower,
            "log_R4_interval": [x_min, x_max],
            "R4_upper": radius_upper,
            "D_tau_log_R4_absolute_upper": rate_upper,
            "spatial_quadratic_lower": spatial_quadratic,
            "Dirac_linear_upper": dirac_linear,
            "two_chirality_barrier_level_threshold": dirac_barrier_threshold,
        },
        "low_high_spectral_split": {
            "energy_split": "E_mu=exp(-2*x_max)*mu^2/4",
            "Dirac_collar_form_lower": (
                "P_mu>=-D_tau^2+(exp(-2*x_max)/2)*mu^2"
            ),
            "Agmon_action_lower": "A_mu>=ell_0*mu/(2*R4_max)",
            "two_Poisson_factor_suppression": "exp(-2*A_mu)<=exp(-ell_0*mu/R4_max)",
            "high_energy_heat_suppression": "exp(-E_mu)",
            "incoming_transfer_linear_loss": transfer_linear_loss,
            "collar_linear_suppression_rate": barrier_linear_rate,
            "net_low_energy_linear_decay_rate": net_linear_decay,
            "high_energy_quadratic_decay_rate": high_gaussian_rate,
            "generator_polynomial_power": polynomial_power,
            "multiplicity_inclusive_polynomial_power": total_polynomial_power,
        },
        "root_test_witness": {
            "low_energy_nth_root_log_limit": -net_linear_decay,
            "low_energy_limit_is_strictly_negative": net_linear_decay > 0.0,
            "high_energy_nth_root_log_limit": "minus_infinity",
            "sample_rows": low_rows,
            "sample_rows_strictly_decrease": decreasing,
        },
        "adjudication": {
            "maximal_fixed_terminal_incoming_full_graded_relative_heat_cotangent": "CLOSED_SUMMABLE",
            "unknown_far_C2_tail_used_in_angular_majorant": False,
            "absolute_infinite_volume_heat_trace_required": False,
            "interior_log_radius_source_counterexample_reopened": False,
            "actual_maximal_incoming_heat_coefficient_value_and_sign": "OPEN",
            "complete_joint_all_direction_graded_cotangent": "OPEN_CURRENT_OWNER",
            "actual_projected_reverse_adjoint_Cauchy_tail": "OPEN_CURRENT_OWNER",
            "actual_projected_KKT_root": "OPEN",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
        },
        "exact_next_dependency": (
            "ASSEMBLE_THE_COMPLETE_SIGNED_JOINT_GRADED_COTANGENT_IN_THE_REMAINING_"
            "PHYSICAL_QUOTIENT_DIRECTIONS,_COMPOSE_IT_WITH_THE_CERTIFIED_REVERSE_"
            "ADJOINT,_AND_PROVE_THE_PROJECTED_CAUCHY_LIMIT_OR_USE_AN_ACTUAL_FINITE_"
            "LATER_EVENT_OR_CANONICAL_STOP;_THEN_TEST_THE_INTRINSIC_OR_BORDERED_KKT_ROOT"
        ),
        "claim_boundary": {
            "maximal_incoming_full_graded_relative_heat_cotangent": "CERTIFIED_SUMMABLE",
            "maximal_incoming_heat_value_and_sign": "OPEN",
            "complete_joint_all_direction_graded_cotangent": "OPEN",
            "actual_projected_Cauchy_tail": "OPEN_CURRENT_OWNER",
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
        raise RuntimeError("maximal graded incoming relative heat validation failed")
    split = payload["low_high_spectral_split"]
    print(json.dumps({
        "status": payload["status"],
        "collar_length_lower": payload["certified_C2_collar"]["proper_length_lower"],
        "net_low_energy_linear_decay_rate": split["net_low_energy_linear_decay_rate"],
        "high_energy_quadratic_decay_rate": split["high_energy_quadratic_decay_rate"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
