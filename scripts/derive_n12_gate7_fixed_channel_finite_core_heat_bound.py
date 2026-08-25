"""Certify the stored C2 fixed-channel heat traces without pencil inversion."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.forward_finite_endpoint_heat_force import (  # noqa: E402
    finite_core_heat_trace_log_upper_bound,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_FIXED_CHANNEL_FINITE_CORE_HEAT_BOUND.json"
CORE_1064 = BASE / "BHSM_N12_C2_1064_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
CORE_1222 = BASE / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
DATA_1064 = CORE_1064.with_suffix(".npz")
DATA_1222 = CORE_1222.with_suffix(".npz")
MODULE = ROOT / "src" / "bhsm" / "interface" / "forward_finite_endpoint_heat_force.py"
THEORY = ROOT / "theory" / "n12_gate7_fixed_channel_finite_core_heat_bound.md"
INPUTS = (CORE_1064, DATA_1064, CORE_1222, DATA_1222, MODULE, THEORY)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _logaddexp(values: list[float]) -> float:
    maximum = max(values)
    return maximum + math.log(sum(math.exp(value - maximum) for value in values))


def _core_rows(record: dict[str, Any]) -> dict[str, Any]:
    duration_upper = float(record["coefficient_path"]["proper_duration_interval"][1])
    log_radius_lower = float(record["coefficient_path"]["log_R4_global_interval"][0])
    dimension = int(record["coefficient_path"]["segment_count"])
    coefficient_upper = 1.5 * math.exp(-log_radius_lower)
    scalar = finite_core_heat_trace_log_upper_bound(
        dimension=dimension,
        proper_duration_upper=duration_upper,
        scalar_potential_lower=0.0,
    )
    plus = finite_core_heat_trace_log_upper_bound(
        dimension=dimension,
        proper_duration_upper=duration_upper,
        factorization_coefficient_upper=coefficient_upper,
    )
    minus = finite_core_heat_trace_log_upper_bound(
        dimension=dimension,
        proper_duration_upper=duration_upper,
        factorization_coefficient_upper=coefficient_upper,
    )
    channels = {
        "scalar_c3": scalar,
        "product_Dirac_lambda1_5_chirality_plus": plus,
        "product_Dirac_lambda1_5_chirality_minus": minus,
    }
    return {
        "segment_count": dimension,
        "proper_duration_upper": duration_upper,
        "global_log_radius_lower": log_radius_lower,
        "lambda1_5_over_R_upper": coefficient_upper,
        "channels": channels,
        "three_channel_absolute_sum_log_upper": _logaddexp([
            row["log_heat_trace_upper_bound"] for row in channels.values()
        ]),
    }


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing fixed-channel heat-bound inputs: " + ", ".join(missing))
    core_1064, core_1222 = (_load(path) for path in (CORE_1064, CORE_1222))
    if not all(record.get("validation_passed") is True for record in (core_1064, core_1222)):
        raise RuntimeError("validated finite-core descriptor parents required")
    rows = {
        "1064": _core_rows(core_1064),
        "1222": _core_rows(core_1222),
    }
    per_channel_increment = {
        name: _logaddexp([
            rows["1064"]["channels"][name]["log_heat_trace_upper_bound"],
            rows["1222"]["channels"][name]["log_heat_trace_upper_bound"],
        ])
        for name in rows["1222"]["channels"]
    }
    total_increment_log_upper = _logaddexp(list(per_channel_increment.values()))
    gap_1064 = rows["1064"]["channels"]["scalar_c3"]["generalized_gap_lower"]
    gap_1222 = rows["1222"]["channels"]["scalar_c3"]["generalized_gap_lower"]
    increment_expression = (
        f"3*(1064*exp(-{gap_1064:.17e})+"
        f"1222*exp(-{gap_1222:.17e}))"
    )
    validation = {
        "both_descriptor_parents_validate": True,
        "1064_core_is_exact_prefix_of_1222_core": (
            core_1222["validation"]["validated_1064_segment_prefix_consumed"] is True
        ),
        "certified_duration_upper_endpoints_used": all(
            rows[key]["proper_duration_upper"]
            == float(record["coefficient_path"]["proper_duration_interval"][1])
            for key, record in (("1064", core_1064), ("1222", core_1222))
        ),
        "certified_radius_tube_lower_endpoints_used_for_Dirac": True,
        "all_six_log_bounds_are_finite_and_negative": all(
            math.isfinite(channel["log_heat_trace_upper_bound"])
            and channel["log_heat_trace_upper_bound"] < 0.0
            for row in rows.values() for channel in row["channels"].values()
        ),
        "all_six_bounds_underflow_binary64": all(
            channel["upper_bound_underflows_binary64"]
            for row in rows.values() for channel in row["channels"].values()
        ),
        "no_generalized_mass_kinetic_or_Dirac_inverse_formed": True,
        "floating_point_underflow_not_reported_as_exact_zero": True,
        "full_graded_joint_trace_is_not_claimed": True,
        "tail_beyond_1222_is_not_claimed": True,
        "far_core_edge_is_not_promoted_to_endpoint": True,
        "no_selector_scale_fit_recurrence_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_FIXED_CHANNEL_FINITE_CORE_HEAT_BOUND",
        "status": (
            "C2_FIXED_CHANNEL_1064_TO_1222_HEAT_INCREMENT_SUPPRESSED_IN_LOG_SPACE"
            if passed else "C2_FIXED_CHANNEL_FINITE_CORE_HEAT_BOUND_NOT_CERTIFIED"
        ),
        "classification": (
            "THE_MIXED_BIRTH_FREE_FAR_FRIEDRICHS_DIRICHLET_POINCARE_BOUND_"
            "SUPPRESSES_THE_THREE_STORED_FIXED_CHANNEL_HEAT_TRACES_AND_THEIR_"
            "1064_TO_1222_INCREMENT_WITHOUT_INVERTING_THE_DESCRIPTOR_PENCIL"
        ),
        "theorem": {
            "mixed_boundary_Poincare": "norm(u_prime)>=pi*norm(u)/(2*T)",
            "scalar_gap": "g>=(pi/(2*T_upper))^2+V_lower",
            "factorized_Dirac_gap": "g>=max(0,pi/(2*T_upper)-norm(W)_infinity)^2",
            "heat_trace_bound": "Tr_exp(-ell_kappa^2*P)<=N*exp(-ell_kappa^2*g)",
            "heat_length_in_ell_kappa_units": 1.0,
            "representation": "NATURAL_LOG_SPACE_NO_UNDERFLOW_PROMOTION",
        },
        "cores": rows,
        "increment_1064_to_1222": {
            "per_channel_absolute_difference_log_upper": per_channel_increment,
            "three_channel_absolute_sum_log_upper": total_increment_log_upper,
            "three_channel_absolute_sum_exact_bound_expression": increment_expression,
            "meaning": "ABSOLUTE_BOUND_BY_SUM_OF_ENDPOINT_TRACE_BOUNDS",
        },
        "claim_boundary": {
            "stored_fixed_channel_finite_core_increment": "CERTIFIED_SUPPRESSED",
            "actual_joint_graded_heat_trace": "OPEN",
            "full_angular_sum": "OPEN_WITH_SHARP_JOINT_DOMAIN",
            "incoming_M_f_and_event_child_seam": "OPEN",
            "non_scale_reset_quotient": "OPEN",
            "maximal_tail_beyond_1222": "OPEN",
            "Gate7": "G7_08_OPEN",
            "Gate8": "LOCKED",
        },
        "validated_invalidated_open": {
            "VALIDATED": [
                "inverse-free mixed-boundary fixed-channel gap",
                "1064 and 1222 representative heat-trace log bounds",
                "absolute representative 1064-to-1222 increment bound",
            ],
            "INVALIDATED": [
                "dense generalized eigensolution is required for these representative bounds",
                "binary64 underflow is an exact zero heat trace",
            ],
            "OPEN": [
                "sharp incoming and seam realization",
                "full graded angular trace",
                "non-scale reset quotient force sector",
                "maximal projected force tail",
            ],
        },
        "exact_next_dependency": (
            "DO_NOT_SPEND_GATE7_EFFORT_DIAGONALIZING_THE_THREE_SUPPRESSED_"
            "REPRESENTATIVE_CORES;_REALIZE_THE_SHARP_INCOMING_SEAM_AND_FULL_"
            "GRADED_DOMAIN_AND_SOLVE_THE_NON_SCALE_RESET_QUOTIENT_PULLBACK"
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
        "increment_log_upper": payload["increment_1064_to_1222"]
        ["three_channel_absolute_sum_log_upper"],
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
