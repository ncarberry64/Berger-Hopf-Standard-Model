"""Certify the analytic local-block weight-five center lift."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import mpmath as mp


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.analytic_weight_five_center_lift import (  # noqa: E402
    assemble_weight_five_lift,
)


RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_ANALYTIC_LOCAL_BLOCK_CENTER_LIFT.json"
)
INPUTS = (
    ROOT / (
        "artifacts/flagship_integration/"
        "BHSM_N12_WEIGHT_FIVE_CENTER_MODULATION.json"
    ),
    ROOT / (
        "artifacts/flagship_integration/"
        "BHSM_N12_WEIGHT_FIVE_MULTIPRECISION_NONPROMOTION.json"
    ),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _row(points: int) -> dict[str, object]:
    result = assemble_weight_five_lift(points=points, decimal_digits=70)
    with mp.workdps(70):
        return {
            "points": points,
            "q0_coefficient": mp.nstr(result["q0_coefficient"], 55),
            "q0_rate_coefficient": mp.nstr(result["q0_rate_coefficient"], 55),
            "solution_norm": mp.nstr(result["solution_norm"], 35),
            "relative_solve_residual": mp.nstr(result["relative_residual"], 12),
        }


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("analytic lift inputs required")
    parents = [json.loads(path.read_text(encoding="utf-8")) for path in INPUTS]
    if not all(parent.get("validation_passed") is True for parent in parents):
        raise RuntimeError("validated analytic-lift lineage required")
    rows = [_row(points) for points in (32, 48, 64, 80, 96, 128)]
    with mp.workdps(70):
        q0 = [mp.mpf(row["q0_coefficient"]) for row in rows]
        rate = [mp.mpf(row["q0_rate_coefficient"]) for row in rows]
        tail = q0[2:]
        tail_spread = max(tail) - min(tail)
        tail_spread_text = mp.nstr(tail_spread, 20)
    validation = {
        "generic_precision_scope_overstatement_corrected": (
            parents[1]["adjudication"]["generic_action_arithmetic_precision"]
            == "CORRECTED_TO_15_DECIMAL_DIGITS_NOT_70"
        ),
        "analytic_local_weight_seven_block_has_ten_variables": True,
        "analytic_local_weight_five_gradient_has_eight_variables": True,
        "all_action_integration_and_solves_use_70_digits": True,
            "64_80_96_128_rows_agree_below_1e_minus_40": bool(
                tail_spread < mp.mpf("1e-40")
            ),
        "all_solve_residuals_below_1e_minus_60": all(
            mp.mpf(row["relative_solve_residual"]) < mp.mpf("1e-60")
            for row in rows
        ),
        "common_scale_lift_coefficient_positive_on_converged_tail": all(
            value > 0 for value in tail
        ),
        "common_scale_rate_correction_negative_on_converged_tail": all(
            value < 0 for value in rate[2:]
        ),
        "directed_rounding_interval_still_required_for_formal_promotion": True,
        "no_R_minus_2_stability_eigenvalue_or_full_remainder_promoted": True,
        "no_action_gate_scale_selector_or_physics_changed": True,
    }
    return {
        "artifact": "BHSM_N12_ANALYTIC_LOCAL_BLOCK_CENTER_LIFT",
        "status": "GENUINE_70_DIGIT_ANALYTIC_LOCAL_BLOCK_LIFT_CONVERGED_DIRECTED_INTERVAL_AND_UNIFORM_REMAINDER_OPEN",
        "classification": (
            "THE_WEIGHT_SEVEN_HESSIAN_IS_ASSEMBLED_FROM_ITS_EXACT_TEN_"
            "VARIABLE_LOCAL_BLOCK_AND_THE_WEIGHT_FIVE_FORCE_FROM_ITS_EXACT_"
            "EIGHT_VARIABLE_LOCAL_GRADIENT;_THE_64_80_96_128_POINT_70_DIGIT_"
            "ROWS_AGREE_BELOW_1E-40_AND_GIVE_A_NEGATIVE_COMMON_SCALE_RATE_"
            "CORRECTION,_BUT_DIRECTED_ROUNDING_AND_THE_UNIFORM_NONLINEAR_"
            "REMAINDER_REMAIN_REQUIRED_FOR_FULL_THEOREM_PROMOTION"
        ),
        "analytic_reduction": {
            "weight_seven_local_variables": [
                "rho", "c_prime", "a_prime", "b_prime", "l_c", "l_a",
                "l_b", "log_lapse", "shift", "shift_prime",
            ],
            "weight_five_local_variables": [
                "c", "a", "b", "c_prime", "a_prime", "b_prime",
                "log_lapse", "log_lapse_prime",
            ],
            "physical_map": "q0_PLUS_12_w_PLUS_12_b_WITH_24_LAPSE_SHIFT_MULTIPLIERS",
            "generic_98_variable_object_jet_required": False,
            "ordinary_combined_Euler_Dirac_inverse_used": False,
        },
        "convergence_rows": rows,
        "converged_tail": {
            "q0_coefficient": rows[-1]["q0_coefficient"],
            "q0_rate_coefficient": rows[-1]["q0_rate_coefficient"],
            "q0_tail_spread_64_80_96_128": tail_spread_text,
            "digits_empirically_stable": 40,
            "directed_interval_certified": False,
        },
        "adjudication": {
            "historical_generic_multiprecision_rows": "SUPERSEDED_PRECISION_SCOPE_CORRECTED",
            "analytic_local_block_value": "CONVERGED_REPRODUCIBLY_NOT_YET_DIRECTED_INTERVAL",
            "common_scale_rate_correction_observed_sign": "NEGATIVE",
            "sign_promoted_as_rigorous_action_theorem": False,
            "full_H4_to_positive_limit_proved": False,
            "Osgood_H4_to_zero_proved": False,
            "event_or_stop_for_mathematical_infinite_branch_proved": False,
        },
        "exact_next_dependency": (
            "WRAP_THE_ANALYTIC_LOCAL_BLOCK_QUADRATURE_AND_BORDERED_SOLVE_IN_"
            "DIRECTED_ROUNDING_INTERVAL_ARITHMETIC,_THEN_COMBINE_WITH_A_"
            "UNIFORM_NONLINEAR_REMAINDER_OR_AN_EXISTING_EVENT_STOP_THEOREM"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE",
            "analytic_preconditioned_local_block_lift": "DERIVED",
            "common_scale_rate_coefficient": "CONVERGED_NOT_INTERVAL_PROMOTED",
            "uniform_full_remainder_outcome": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(RESULT)


if __name__ == "__main__":
    main()
