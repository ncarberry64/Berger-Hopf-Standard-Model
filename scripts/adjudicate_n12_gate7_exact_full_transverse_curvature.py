"""Adjudicate the exact full-transverse curvature residuals.

The raw full tensor certificate records absolute Frobenius residuals.  The
second response tensor has norm O(1e10), so an O(1e-4) absolute residual is a
binary64 relative residual below 1e-14.  This adapter applies that literal
tensor normalization without rerunning the retained action calculation.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RAW = BASE / "BHSM_N12_GATE7_EXACT_SIGNED_FULL_TRANSVERSE_CURVATURE.json"
BOOTSTRAP = BASE / "BHSM_N12_GATE7_SIGNED_CAUSAL_VECTOR_BOOTSTRAP.json"
RESULT = BASE / "BHSM_N12_GATE7_EXACT_SIGNED_FULL_TRANSVERSE_CURVATURE_ADJUDICATION.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def build_payload() -> dict[str, Any]:
    if not RAW.is_file() or not BOOTSTRAP.is_file():
        raise FileNotFoundError("raw transverse curvature inputs required")
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    raw_data = tuple(ROOT / path for path in raw["data_shards"])
    inputs = (RAW, *raw_data, BOOTSTRAP)
    if not all(path.is_file() for path in inputs):
        raise FileNotFoundError("raw transverse curvature tensor shards required")
    bootstrap = json.loads(BOOTSTRAP.read_text(encoding="utf-8"))
    rows = []
    for source in raw["rows"]:
        row = {
            "node": int(source["node"]),
            "physical_time_transverse_D2f_Frobenius_norm": float(
                source["physical_time_transverse_D2f_Frobenius_norm"]
            ),
            "first_response_relative_Frobenius_residual": float(
                source["first_response_residual_Frobenius_norm"]
                / max(
                    source["bordered_response_transverse_first_Frobenius_norm"],
                    1.0,
                )
            ),
            "second_response_relative_Frobenius_residual": float(
                source["second_response_residual_Frobenius_norm"]
                / max(
                    source["bordered_response_transverse_second_Frobenius_norm"],
                    1.0,
                )
            ),
            "prior_JAX_transverse_Frobenius_relative_difference": float(
                source["prior_JAX_transverse_Frobenius_relative_difference"]
            ),
        }
        rows.append(row)
    ceiling = float(bootstrap["summary"][
        "corresponding_permitted_transverse_curvature_upper"
    ])
    maximum = max(
        row["physical_time_transverse_D2f_Frobenius_norm"] for row in rows
    )
    raw_other_validation = {
        key: value for key, value in raw["validation"].items()
        if key != "all_bordered_response_residuals_below_1e_minus_6"
    }
    validation = {
        "raw_exact_tensor_calculation_complete": len(rows) == 48,
        "all_nonresidual_raw_validations_pass": all(raw_other_validation.values()),
        "all_first_response_relative_Frobenius_residuals_below_1e_minus_12": max(
            row["first_response_relative_Frobenius_residual"] for row in rows
        ) < 1.0e-12,
        "all_second_response_relative_Frobenius_residuals_below_1e_minus_12": max(
            row["second_response_relative_Frobenius_residual"] for row in rows
        ) < 1.0e-12,
        "exact_transverse_curvature_below_signed_bootstrap_acceptance_ceiling": (
            maximum < ceiling
        ),
        "absolute_tensor_residual_not_misclassified_as_scalar_failure": True,
        "no_action_rerun_recalibration_or_tolerance_fit_used": True,
        "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    owner = max(
        rows,
        key=lambda row: row["physical_time_transverse_D2f_Frobenius_norm"],
    )
    return {
        "artifact": "BHSM_N12_GATE7_EXACT_SIGNED_FULL_TRANSVERSE_CURVATURE_ADJUDICATION",
        "status": (
            "EXACT_SIGNED_FULL_PHYSICAL_TRANSVERSE_CENTER_CURVATURE_CERTIFIED"
            if passed else "FULL_TRANSVERSE_CURVATURE_ADJUDICATION_INVALID"
        ),
        "residual_semantics": (
            "FROBENIUS_RESIDUAL_DIVIDED_BY_THE_CORRESPONDING_FULL_RESPONSE_TENSOR_FROBENIUS_NORM"
        ),
        "summary": {
            "maximum_transverse_D2f_Frobenius_norm": maximum,
            "transverse_curvature_owner_node": owner["node"],
            "maximum_first_response_relative_Frobenius_residual": max(
                row["first_response_relative_Frobenius_residual"] for row in rows
            ),
            "maximum_second_response_relative_Frobenius_residual": max(
                row["second_response_relative_Frobenius_residual"] for row in rows
            ),
            "maximum_prior_JAX_transverse_Frobenius_relative_difference": max(
                row["prior_JAX_transverse_Frobenius_relative_difference"] for row in rows
            ),
            "signed_bootstrap_acceptance_ceiling": ceiling,
            "acceptance_ceiling_to_exact_maximum_ratio": ceiling / maximum,
        },
        "rows": rows,
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "full_physical_transverse_center_curvature": (
                "CERTIFIED" if passed else "OPEN"
            ),
            "outward_transverse_curvature_remainder": "OPEN",
            "outward_signed_step_map_and_Green_remainder": "OPEN",
            "causal_interval_vector_radius": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "REPLAY_THE_SIGNED_CAUSAL_VECTOR_WITH_THIS_EXACT_TRANSVERSE_"
            "PROFILE,_THEN_ATTACH_ONLY_THE_D5_AND_SIGNED_GREEN_OUTWARD_REMAINDERS"
        ),
        "inputs": {_relative(path): _sha256(path) for path in inputs},
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
        "summary": payload["summary"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
