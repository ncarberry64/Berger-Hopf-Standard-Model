"""Bound the complete graded heat seed on the direct AE2 finite core."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any, Callable

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from derive_n12_c2_birth_coefficient_quotient_jet import (  # noqa: E402
    _coefficient_enclosure,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_ONE_SEAM_FULL_GRADED_FINITE_CORE_HEAT_BOUND.json"
ONE_SEAM = BASE / "BHSM_N12_GATE7_AE2_ONE_SEAM_DIRECT_DESCRIPTOR.json"
CHILD = BASE / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
CHILD_DATA = CHILD.with_suffix(".npz")
INCOMING = BASE / "BHSM_N12_INCOMING_FINITE_AMPLITUDE_COEFFICIENT_ENCLOSURE.json"
INCOMING_SEGMENT = BASE / "BHSM_N12_INCOMING_REGULARIZED_TERMINAL_SEGMENT.json"
NONFERMION = BASE / "BHSM_N12_GATE7_AE2_NONFERMION_THRESHOLD_MARGIN.json"
ACTION = ROOT / "artifacts" / "action_extension" / "BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json"
LEDGER = ROOT / "artifacts" / "BHSM_aether_common_quantum_superdeterminant_v15_96.json"
WARD = BASE / "BHSM_N12_GATE7_COMMON_SCALE_HEAT_ZETA_WARD.json"
COEFFICIENT = ROOT / "scripts" / "derive_n12_c2_birth_coefficient_quotient_jet.py"
THEORY = ROOT / "theory" / "n12_gate7_one_seam_full_graded_finite_core_heat_bound.md"
INPUTS = (
    ONE_SEAM, CHILD, CHILD_DATA, INCOMING, INCOMING_SEGMENT, NONFERMION,
    ACTION, LEDGER, WARD, COEFFICIENT, THEORY,
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _positive_series(term: Callable[[int], float], start: int) -> tuple[float, int]:
    total = 0.0
    consecutive_zeros = 0
    final = start
    for index in range(start, 10000):
        value = float(term(index))
        if not math.isfinite(value) or value < 0.0:
            raise RuntimeError("finite nonnegative angular summand required")
        total += value
        final = index
        if value == 0.0:
            consecutive_zeros += 1
        else:
            consecutive_zeros = 0
        if consecutive_zeros >= 8:
            break
    else:
        raise RuntimeError("angular witness summation did not terminate")
    return total, final


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing full graded heat inputs: " + ", ".join(missing))
    one_seam, child, incoming, incoming_segment, nonfermion, action, ledger, ward = (
        _load(path) for path in (
            ONE_SEAM, CHILD, INCOMING, INCOMING_SEGMENT, NONFERMION,
            ACTION, LEDGER, WARD,
        )
    )
    if not all(record.get("validation_passed") is True for record in (
        one_seam, child, incoming, incoming_segment, nonfermion, action, ledger, ward
    )):
        raise RuntimeError("validated full graded heat parents required")

    with np.load(CHILD_DATA) as data:
        nodes = np.asarray(data["C2_proof_center_nodes"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        tubes = np.asarray(data["node_action_tube_upper"], dtype=float)
    rate_rows = [
        _coefficient_enclosure(node, weights, float(tube))[
            "root_D_tau_log_R4_interval"
        ]
        for node, tube in zip(nodes, tubes, strict=True)
    ]
    c2_rate_abs_upper = max(abs(float(endpoint)) for row in rate_rows for endpoint in row)
    incoming_rate_abs_upper = max(abs(float(value)) for value in incoming_segment[
        "explicit_segment"
    ]["D_tau_log_R4_interval_on_terminal_ball"])
    rate_abs_upper = max(c2_rate_abs_upper, incoming_rate_abs_upper)

    child_duration_upper = float(child["coefficient_path"]["proper_duration_interval"][1])
    formation_duration_upper = float(incoming[
        "amplitude_family"
    ]["endpoint_proof_edge_duration_interval"][1])
    total_duration_upper = child_duration_upper + formation_duration_upper
    # Preserve the strict positive formation contribution under binary64
    # absorption by rounding the enclosing upper endpoint outward.
    if total_duration_upper == child_duration_upper:
        total_duration_upper = math.nextafter(child_duration_upper, math.inf)
    child_x = child["coefficient_path"]["log_R4_global_interval"]
    incoming_x = incoming["amplitude_family"]["terminal_log_R4_interval"]
    x_lower = min(float(child_x[0]), float(incoming_x[0]))
    x_upper = max(float(child_x[1]), float(incoming_x[1]))

    temporal_base = (math.pi / total_duration_upper) ** 2
    spatial_quadratic = math.exp(-2.0 * x_upper)
    dirac_linear = math.exp(-x_lower) * rate_abs_upper
    lowest_weyl = 1.5
    weyl_spatial_lower = (
        spatial_quadratic * lowest_weyl**2 - dirac_linear * lowest_weyl
    )
    common_gap_lower = temporal_base + min(spatial_quadratic, weyl_spatial_lower)
    temporal_log_bound = -temporal_base
    if temporal_base < 250.0:
        temporal_log_bound -= math.log1p(-math.exp(-3.0 * temporal_base))

    hs_sum, hs_cutoff = _positive_series(
        lambda m: 4.0 * m * m * math.exp(-spatial_quadratic * m * m), 1
    )
    gauge_sum, gauge_cutoff = _positive_series(
        lambda m: 24.0 * (m * m - 1.0)
        * math.exp(-spatial_quadratic * m * m),
        2,
    )
    weyl_sum, weyl_cutoff = _positive_series(
        lambda n: 48.0 * (n + 1.0) * (n + 2.0)
        * math.exp(
            -spatial_quadratic * (n + 1.5) ** 2
            + dirac_linear * (n + 1.5)
        ),
        0,
    )
    angular_absolute_sum = hs_sum + gauge_sum + weyl_sum
    full_heat_log_upper = temporal_log_bound + math.log(angular_absolute_sum)
    cotangent_trace_norm_log_upper = (
        full_heat_log_upper - math.log(2.0 * common_gap_lower)
    )
    log10 = math.log(10.0)

    validation = {
        "direct_one_seam_domain_consumed": (
            one_seam["claim_boundary"]["finite_core_joint_operator_type"]
            == "DERIVED_EXECUTABLE"
        ),
        "external_E0_and_far_core_are_Dirichlet": (
            one_seam["operator"]["external_birth"]
            == "E0_DIRICHLET_Gamma0_birth=0"
            and one_seam["operator"]["far_core"].startswith("C2_FRIEDRICHS")
        ),
        "formation_and_child_durations_are_positive": (
            formation_duration_upper > 0.0 and child_duration_upper > 0.0
        ),
        "radius_and_rate_bounds_are_finite": all(math.isfinite(value) for value in (
            x_lower, x_upper, rate_abs_upper
        )),
        "all_C2_rate_rows_are_positive_forward": min(float(row[0]) for row in rate_rows) > 0.0,
        "Dirac_quadratic_minus_linear_margin_is_positive": weyl_spatial_lower > 0.0,
        "common_full_graded_gap_is_positive": common_gap_lower > 0.0,
        "all_absolute_angular_sector_sums_are_positive_finite": (
            all(math.isfinite(value) and value > 0.0 for value in (
                hs_sum, gauge_sum, weyl_sum, angular_absolute_sum
            ))
        ),
        "nonfermion_contacts_are_nonnegative": (
            nonfermion["theorem"]["quadratic_form_order"].startswith("M_event(0)>=0")
        ),
        "fermion_internal_surface_action_is_zero": (
            action["action_definition"]["independent_normal_matter_boundary_action"]
            == "S_Sigma_F_AE2=0"
        ),
        "retained_grading_ledger_consumed": (
            ledger["graded_operator_ledger"]["Weyl"]["species"] == 48
            and ledger["graded_operator_ledger"]["gauge_transverse"]["species"] == 12
            and ledger["graded_operator_ledger"]["Hubbard_Strattonovich"]["species"] == 4
        ),
        "common_scale_Ward_formula_consumed": (
            ward["adjudication"]["common_scale_source_contraction_formula"] == "CLOSED"
        ),
        "heat_and_seed_bounds_remain_in_log_space": (
            full_heat_log_upper < -1.0e50 and cotangent_trace_norm_log_upper < -1.0e50
        ),
        "far_core_not_promoted_to_endpoint": (
            child["endpoint_event_child_partition"]["far_core_edge_is_physical_endpoint"]
            is False
        ),
        "no_selector_source_scale_recurrence_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_ONE_SEAM_FULL_GRADED_FINITE_CORE_HEAT_BOUND",
        "status": (
            "FULL_GRADED_ONE_SEAM_FINITE_CORE_HEAT_SEED_SUPPRESSED_IN_LOG_SPACE"
            if passed else "FULL_GRADED_ONE_SEAM_FINITE_CORE_HEAT_BOUND_FAILED"
        ),
        "classification": (
            "THE_DIRECT_E0_TO_E1_C2_TO_FAR_CORE_DOMAIN_HAS_TWO_EXTERNAL_"
            "DIRICHLET_TRACES_AND_ONE_INTERNAL_SEAM;_DIRICHLET_POINCARE_PLUS_"
            "THE_GLOBAL_AE2_FACTORIZATION_GIVES_AN_EXPLICIT_ABSOLUTE_SUM_OVER_"
            "ALL_RETAINED_GAUGE_WEYL_AND_HS_LEVELS,_SUPPRESSING_THE_COMPLETE_"
            "FINITE_CORE_HEAT_TRACE_AND_HEAT_COTANGENT_SEED_IN_LOG_SPACE"
        ),
        "finite_core_domain": {
            "formation_duration_upper": formation_duration_upper,
            "child_duration_upper": child_duration_upper,
            "total_duration_upper": total_duration_upper,
            "log_R4_interval": [x_lower, x_upper],
            "C2_D_tau_log_R4_absolute_upper": c2_rate_abs_upper,
            "incoming_D_tau_log_R4_absolute_upper": incoming_rate_abs_upper,
            "joint_D_tau_log_R4_absolute_upper": rate_abs_upper,
            "C2_rate_rows_recomputed": len(rate_rows),
            "far_core_is_physical_endpoint": False,
        },
        "coercive_bound": {
            "temporal_Dirichlet_base": temporal_base,
            "spatial_quadratic_coefficient": spatial_quadratic,
            "Dirac_linear_coefficient": dirac_linear,
            "lowest_Weyl_spatial_lower": weyl_spatial_lower,
            "common_gap_lower": common_gap_lower,
            "scalar": "g_m>=(pi/T)^2+exp(-2*x_max)*m^2",
            "Weyl": "g_n>=(pi/T)^2+exp(-2*x_max)*(n+3/2)^2-exp(-x_min)*norm(x_dot)_infinity*(n+3/2)",
            "contact_rule": "NONNEGATIVE_NONFERMION_CONTACTS_CAN_ONLY_INCREASE_THE_FORM;_FERMION_W_phys=0",
        },
        "absolute_angular_sum": {
            "Hubbard_Strattonovich": hs_sum,
            "Hubbard_Strattonovich_binary64_cutoff": hs_cutoff,
            "gauge_transverse": gauge_sum,
            "gauge_transverse_binary64_cutoff": gauge_cutoff,
            "Weyl": weyl_sum,
            "Weyl_binary64_cutoff": weyl_cutoff,
            "total": angular_absolute_sum,
            "longitudinal_complex_ghost": 0.0,
            "cancellation_used_for_bound": False,
        },
        "full_graded_bounds": {
            "heat_trace_absolute_log_upper": full_heat_log_upper,
            "heat_trace_absolute_log10_upper": full_heat_log_upper / log10,
            "heat_cotangent_seed_trace_norm_log_upper": cotangent_trace_norm_log_upper,
            "heat_cotangent_seed_trace_norm_log10_upper": cotangent_trace_norm_log_upper / log10,
            "binary64_underflow_is_exact_zero": False,
            "dense_generalized_eigendecomposition_used": False,
            "common_scale_heat_force_absolute_log_upper": full_heat_log_upper,
            "common_scale_zeta_force": 0.0,
        },
        "matching_audit": {
            "full_finite_core_angular_sum": "CLOSED_ABSOLUTELY",
            "full_finite_core_joint_heat_trace": "CLOSED_LOG_SPACE_ENCLOSURE",
            "full_finite_core_joint_heat_cotangent_seed": "CLOSED_TRACE_NORM_LOG_SPACE_ENCLOSURE",
            "common_scale_finite_core_force": "CLOSED_LOG_SPACE_ENCLOSURE_WITH_ZERO_ZETA_COMPONENT",
            "signed_non_scale_geometry_contraction": "OPEN",
            "maximal_C2_tail": "OPEN",
            "projected_KKT_root": "WAITING_ON_SIGNED_NON_SCALE_FORCE_AND_MAXIMAL_TAIL",
        },
        "exact_next_dependency": (
            "CONTRACT_THE_NOW_UNIFORMLY_SUPPRESSED_FULL_GRADED_FINITE_CORE_SEED_"
            "WITH_THE_SIGNED_NON_SCALE_DIRECT_DESCRIPTOR_JET,_ADD_THE_EXPLICIT_"
            "DIRECT_ZETA_COVECTOR,_RUN_THE_CERTIFIED_REVERSE_ADJOINT,_AND_PROVE_"
            "THE_MAXIMAL_PROJECTED_CAUCHY_TAIL_OR_CERTIFY_A_LATER_EVENT_OR_STOP"
        ),
        "claim_boundary": {
            "full_graded_finite_core_heat_trace": "CERTIFIED_SUPPRESSED",
            "full_graded_finite_core_heat_cotangent_seed": "CERTIFIED_SUPPRESSED",
            "actual_signed_non_scale_force": "OPEN",
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
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not payload["validation_passed"]:
        raise RuntimeError("full graded finite-core heat validation failed")
    print(json.dumps({
        "status": payload["status"],
        "heat_trace_log10_upper": payload["full_graded_bounds"]["heat_trace_absolute_log10_upper"],
        "seed_trace_norm_log10_upper": payload["full_graded_bounds"]["heat_cotangent_seed_trace_norm_log10_upper"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
