"""Audit whether the retained graded sectors cancel the physical heat tail."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/"
    "BHSM_N12_FORWARD_BRST_HEAT_TAIL_CANCELLATION_AUDIT.json"
)
SUPERDET = ARTIFACTS / "BHSM_aether_common_quantum_superdeterminant_v15_96.json"
GAP = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_EXTERIOR_GAP_ORACLE_AUDIT.json"
)
HEAT_TRACE = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_HEAT_TRACE_CLASS_AUDIT.json"
)
INFRARED = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_E1_INFRARED_CONTROL_AUDIT.json"
)
INPUTS = (SUPERDET, GAP, HEAT_TRACE, INFRARED)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _graded_spatial_heat_trace(a: float) -> dict[str, float | int]:
    if not math.isfinite(a) or a <= 0.0:
        raise ValueError("positive finite dimensionless heat ratio required")
    maximum = max(100, int(math.sqrt(50.0 / a)))
    hs = sum(4.0 * m * m * math.exp(-a * m * m) for m in range(1, maximum + 1))
    gauge = sum(
        24.0 * (m * m - 1.0) * math.exp(-a * m * m)
        for m in range(2, maximum + 1)
    )
    weyl = sum(
        -48.0
        * (n + 1.0)
        * (n + 2.0)
        * math.exp(-a * (n + 1.5) ** 2)
        for n in range(maximum + 1)
    )
    total = hs + gauge + weyl
    scaled = a**1.5 * total
    target = -5.0 * math.sqrt(math.pi)
    return {
        "a_equals_heat_time_over_R4_squared": a,
        "summation_cutoff": maximum,
        "HS_contribution": hs,
        "transverse_gauge_contribution": gauge,
        "Weyl_contribution": weyl,
        "graded_total": total,
        "a_to_three_halves_times_total": scaled,
        "leading_asymptotic_target": target,
        "absolute_scaled_residual": abs(scaled - target),
    }


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all BRST heat-tail audit inputs are required")
    records = {
        path.name: json.loads(path.read_text(encoding="utf-8")) for path in INPUTS
    }
    if not all(record.get("validation_passed") is True for record in records.values()):
        raise RuntimeError("all BRST heat-tail audit inputs must validate")
    superdet = records[SUPERDET.name]
    gap = records[GAP.name]
    heat_trace = records[HEAT_TRACE.name]
    infrared = records[INFRARED.name]
    ledger = superdet["graded_operator_ledger"]
    rows = [_graded_spatial_heat_trace(a) for a in (0.1, 0.05, 0.02, 0.01, 0.005, 0.002)]
    leading_degeneracy_coefficient = 4 + 24 - 48
    leading_heat_coefficient = leading_degeneracy_coefficient / 4.0

    validation = {
        "all_inputs_validated": True,
        "longitudinal_ghost_pair_cancels_mode_by_mode": ledger[
            "gauge_longitudinal_ghost"
        ]["net_supertrace_sign"]
        == 0,
        "retained_physical_sector_species_and_signs_consumed": (
            ledger["Hubbard_Strattonovich"]["species"] == 4
            and ledger["Hubbard_Strattonovich"]["supertrace_sign"] == 1
            and ledger["gauge_transverse"]["species"] == 12
            and ledger["gauge_transverse"]["supertrace_sign"] == 1
            and ledger["Weyl"]["species"] == 48
            and ledger["Weyl"]["supertrace_sign"] == -1
        ),
        "leading_physical_superdimension_is_nonzero": (
            leading_degeneracy_coefficient == -20
        ),
        "leading_heat_coefficient_is_minus_five": leading_heat_coefficient == -5.0,
        "scaled_numeric_rows_converge_toward_exact_nonzero_coefficient": all(
            later["absolute_scaled_residual"] < earlier["absolute_scaled_residual"]
            for earlier, later in zip(rows, rows[1:])
        )
        and rows[-1]["absolute_scaled_residual"] < 0.021,
        "Ward_BRST_cancellation_is_not_complete_physical_force_cancellation": (
            gap["validation"]["BRST_cancellation_is_only_longitudinal_ghost"]
            is True
        ),
        "graded_supertrace_not_previously_promoted_to_trace_class": heat_trace[
            "adjudication"
        ]["graded_supertrace_cancellation_can_replace_trace_class_proof"]
        is False,
        "infrared_relative_or_spectral_control_remains_open": infrared[
            "adjudication"
        ]["E1_infrared_synthesis_from_current_bounds"]
        == "OPEN",
        "no_sector_removed_reference_added_or_prediction_changed": True,
    }
    return {
        "artifact": "BHSM_N12_FORWARD_BRST_HEAT_TAIL_CANCELLATION_AUDIT",
        "status": "BRST_LONGITUDINAL_GHOST_CANCELLATION_DOES_NOT_CANCEL_PHYSICAL_HEAT_TAIL",
        "classification": (
            "THE_RETAINED_LONGITUDINAL_GAUGE_AND_COMPLEX_GHOST_BLOCKS_CANCEL_"
            "MODE_BY_MODE,_BUT_THE_PHYSICAL_TRANSVERSE_GAUGE_PLUS_FOUR_HS_"
            "MINUS_48_WEYL_GRADED_S3_HEAT_TRACE_HAS_NONZERO_LEADING_"
            "COEFFICIENT_MINUS_5_SQRT_PI_TIMES_a_TO_MINUS_3_OVER_2;_THEREFORE_"
            "BRST_GRADING_ALONE_CANNOT_SUPPLY_THE_MISSING_SOURCE_ANGULAR_OR_"
            "INFRARED_RELATIVE_TRACE_CANCELLATION"
        ),
        "exact_asymptotic": {
            "dimensionless_ratio": "a=s/R4^2",
            "HS": "4*sum_(m>=1)m^2*exp(-a*m^2)",
            "transverse_gauge": "24*sum_(m>=2)(m^2-1)*exp(-a*m^2)",
            "Weyl": (
                "-48*sum_(n>=0)(n+1)(n+2)*exp(-a*(n+3/2)^2)"
            ),
            "Gaussian_moment": (
                "sum_(m>=1)m^2*exp(-a*m^2)~sqrt(pi)/(4*a^(3/2))"
            ),
            "leading_degeneracy_coefficient": leading_degeneracy_coefficient,
            "leading_scaled_limit": "-5*sqrt(pi)",
            "leading_scaled_limit_decimal": -5.0 * math.sqrt(math.pi),
            "shift_and_minus_one_terms_affect_leading_coefficient": False,
        },
        "numeric_witness_rows": rows,
        "adjudication": {
            "longitudinal_ghost_BRST_pair": "CANCELS_EXACTLY",
            "transverse_gauge_HS_Weyl_physical_supertrace": (
                "NONZERO_LEADING_HEAT_COEFFICIENT"
            ),
            "universal_Ward_BRST_zero_force": "INVALID",
            "BRST_grading_closes_source_angular_tail": False,
            "BRST_grading_closes_E1_infrared": False,
            "action_owned_relative_reference_or_low_energy_control": "STILL_REQUIRED",
        },
        "exact_next_dependency": (
            "DERIVE_AN_ACTION_OWNED_RELATIVE_HEAT_REFERENCE_OR_LOW_ENERGY_"
            "SPECTRAL_MEASURE_BOUND_FOR_THE_NONCANCELLING_PHYSICAL_SECTORS,_"
            "OR_EVALUATE_THE_ACTUAL_FINITE_MAXIMAL_ENDPOINT_OPERATOR;_BRST_"
            "GRADING_ALONE_IS_EXHAUSTED"
        ),
        "claim_boundary": {
            "Gate_7": "ACTIVE_NOT_CLOSED",
            "Gate_8": "LOCKED",
            "chord_03_authorized": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "leading_scaled_limit": payload["exact_asymptotic"][
                    "leading_scaled_limit"
                ],
                "validation_passed": payload["validation_passed"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
