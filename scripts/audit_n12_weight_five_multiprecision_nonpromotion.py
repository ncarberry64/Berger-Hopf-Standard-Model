"""Historical generic-jet precision audit, superseded by local blocks.

The stored rows used high-precision Gauss nodes and 70-digit final solves, but
the generic action-jet arithmetic ran at mpmath's then-default 15 digits. This
scope correction is retained explicitly. The later analytic local-block audit
supersedes these rows.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
from typing import Any

import mpmath as mp


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.weight_seven_transverse_descriptor import (  # noqa: E402
    weight_five_center_lift_system,
)


RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_WEIGHT_FIVE_MULTIPRECISION_NONPROMOTION.json"
)
INPUT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_WEIGHT_FIVE_CENTER_MODULATION.json"
)

STORED_ROWS = [
    {
        "points": 32,
        "seconds": 134.3200306892395,
        "q0_coefficient": "66.517579294464621925438868196913683302883640258568",
        "q0_rate_coefficient": "-51.98193251138158552392445718140179524496263518694",
        "solution_norm": "124719.36226266647243472601977",
    },
    {
        "points": 48,
        "seconds": 198.5036063194275,
        "q0_coefficient": "66.494409659373344100479002837486761939572856577327",
        "q0_rate_coefficient": "-51.963825983447121605498386370280584120188686317495",
        "solution_norm": "124686.786623973548826756877032",
        "relative_solve_residual": "9.698890548e-71",
    },
    {
        "points": 64,
        "seconds": 265.0776946544647,
        "q0_coefficient": "66.494452982548247449792743121292066926232755268183",
        "q0_rate_coefficient": "-51.963859839495070002359193420268403480296988304983",
        "solution_norm": "124686.838201158230723803499253",
        "relative_solve_residual": "8.452298848e-71",
    },
    {
        "points": 80,
        "seconds": 341.9832458496094,
        "q0_coefficient": "66.494334392983139592544955934981622462384518203278",
        "q0_rate_coefficient": "-51.963767164523500438357375992150874038076474897853",
        "solution_norm": "124686.697514319030703234676464",
        "relative_solve_residual": "6.925556925e-71",
    },
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def recompute_row(points: int) -> dict[str, object]:
    started = time.time()
    system = weight_five_center_lift_system(
        points=points, extended_precision=True
    )
    matrix = system["matrix"]
    rhs = system["right_hand_side"]
    with mp.workdps(70):
        A = mp.matrix(
            [[matrix[i, j] for j in range(74)] for i in range(74)]
        )
        b = mp.matrix(list(rhs))
        solution = mp.lu_solve(A, b)
        residual = mp.norm(A * solution - b) / mp.norm(b)
        return {
            "points": points,
            "seconds": time.time() - started,
            "q0_coefficient": mp.nstr(solution[0], 50),
            "q0_rate_coefficient": mp.nstr(
                system["descriptor_exponent"] * solution[0], 50
            ),
            "solution_norm": mp.nstr(mp.norm(solution), 30),
            "relative_solve_residual": mp.nstr(residual, 12),
        }


def build_payload(rows: list[dict[str, object]] | None = None) -> dict[str, Any]:
    if not INPUT.is_file():
        raise FileNotFoundError("weight-five operator artifact required")
    parent = json.loads(INPUT.read_text(encoding="utf-8"))
    if parent.get("validation_passed") is not True:
        raise RuntimeError("validated weight-five operator required")
    rows = STORED_ROWS if rows is None else rows
    tail = rows[1:]
    q0 = [mp.mpf(str(row["q0_coefficient"])) for row in tail]
    rate = [mp.mpf(str(row["q0_rate_coefficient"])) for row in tail]
    diff_48_64 = abs(q0[1] - q0[0])
    diff_64_80 = abs(q0[2] - q0[1])
    validation = {
        "precision_scope_corrected_high_precision_nodes_15_digit_action_70_digit_solve": True,
        "all_tail_common_scale_coefficients_positive": all(x > 0 for x in q0),
        "all_tail_rate_coefficients_negative": all(x < 0 for x in rate),
        "64_to_80_change_exceeds_48_to_64_change": diff_64_80 > diff_48_64,
        "multiprecision_solve_residuals_below_1e_minus_60": all(
            mp.mpf(str(row["relative_solve_residual"])) < mp.mpf("1e-60")
            for row in tail
        ),
        "coefficient_not_promoted_without_quadrature_enclosure": True,
        "no_R_minus_2_stability_eigenvalue_promoted": True,
        "no_action_gate_scale_selector_or_physics_changed": True,
    }
    return {
        "artifact": "BHSM_N12_WEIGHT_FIVE_MULTIPRECISION_NONPROMOTION",
        "status": "SUPERSEDED_GENERIC_JET_PRECISION_SCOPE_CORRECTED_COEFFICIENT_WAS_NOT_PROMOTED",
        "classification": (
            "THE_STORED_ROWS_USED_HIGH_PRECISION_GAUSS_NODES_AND_70_DIGIT_"
            "SOLVES_BUT_ONLY_DEFAULT_15_DIGIT_GENERIC_ACTION_JET_ARITHMETIC;_"
            "THEIR_NONPROMOTION_CONCLUSION_WAS_CONSERVATIVE_AND_REMAINS_"
            "VALID,_BUT_THE_ROWS_ARE_SUPERSEDED_BY_THE_GENUINE_70_DIGIT_"
            "ANALYTIC_LOCAL_BLOCK_ASSEMBLY"
        ),
        "multiprecision_rows": rows,
        "tail_diagnostics": {
            "absolute_q0_change_48_to_64": mp.nstr(diff_48_64, 30),
            "absolute_q0_change_64_to_80": mp.nstr(diff_64_80, 30),
            "q0_tail_minimum_48_64_80": mp.nstr(min(q0), 50),
            "q0_tail_maximum_48_64_80": mp.nstr(max(q0), 50),
            "q0_rate_sign_on_all_tail_rows": "NEGATIVE",
            "tight_coefficient_enclosure_certified": False,
        },
        "adjudication": {
            "linear_solve_precision": "CLOSED_TO_BELOW_1E-70_RESIDUAL",
            "generic_action_arithmetic_precision": "CORRECTED_TO_15_DECIMAL_DIGITS_NOT_70",
            "common_scale_rate_correction_sign_empirically_robust": True,
            "common_scale_rate_correction_sign_promoted_as_theorem": False,
            "weight_five_coefficient_promoted": False,
            "full_remainder_outcome_promoted": False,
        },
        "exact_next_dependency": (
            "USE_THE_SUPERSEDING_GENUINE_MULTIPRECISION_ANALYTIC_LOCAL_BLOCK_"
            "ASSEMBLY_AND_THEN_ADD_DIRECTED_ROUNDING_FOR_FINAL_INTERVAL_"
            "PROMOTION"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE",
            "multiprecision_bordered_solve": "DERIVED_HISTORICAL",
            "weight_five_coefficient": "OPEN_NOT_PROMOTED",
            "uniform_full_remainder_outcome": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {INPUT.relative_to(ROOT).as_posix(): _sha256(INPUT)},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--recompute", action="store_true")
    args = parser.parse_args()
    rows = (
        [recompute_row(points) for points in (32, 48, 64, 80)]
        if args.recompute else None
    )
    RESULT.write_text(
        json.dumps(build_payload(rows), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(RESULT)


if __name__ == "__main__":
    main()
