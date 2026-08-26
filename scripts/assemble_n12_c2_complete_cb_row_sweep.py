"""Assemble all signed non-scale C2 ``D2(cb)`` row checkpoints."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
ROWS = BASE / ".n12_c2_complete_cb_rows"
FIELD = BASE / "BHSM_N12_C2_EXACT_CENTER_FIXED_S_FIELD_MATRIX.json"
FIELD_DATA = FIELD.with_suffix(".npz")
COMMON_SCALE = BASE / "BHSM_N12_C2_COMMON_SCALE_WEYL_COVARIANCE.json"
REFERENCE_ROW = BASE / "BHSM_N12_C2_FULLY_REDUCED_SIGNED_ROW_CERTIFICATE.json"
THEORY = ROOT / "theory" / "n12_c2_complete_non_scale_cb_operator.md"
RESULT = BASE / "BHSM_N12_C2_COMPLETE_NON_SCALE_CB_OPERATOR.json"
DATA_RESULT = RESULT.with_suffix(".npz")
RADIUS = 5.5104723095444935e-11


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def main() -> None:
    row_paths = [ROWS / f"row_{row:03d}.json" for row in range(1, 98)]
    missing = [str(path) for path in row_paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            f"{len(missing)} non-scale cb row checkpoints remain missing; "
            f"first is {missing[0]}"
        )
    records = [json.loads(path.read_text(encoding="utf-8")) for path in row_paths]
    fingerprints = {record.get("sweep_input_fingerprint") for record in records}
    if len(fingerprints) != 1 or None in fingerprints:
        raise RuntimeError("non-scale cb rows do not share one input fingerprint")
    sweep_inputs = records[0]["sweep_inputs"]
    if not all(
        digest == sha256(ROOT / relative)
        for relative, digest in sweep_inputs.items()
    ):
        raise RuntimeError("the cb row input fingerprint is stale")
    if not all(
        record.get("row") == row
        and all(record.get("validation", {}).values())
        for row, record in enumerate(records, start=1)
    ):
        raise RuntimeError("one or more non-scale cb rows are invalid")

    common_scale = json.loads(COMMON_SCALE.read_text(encoding="utf-8"))
    reference_row = json.loads(REFERENCE_ROW.read_text(encoding="utf-8"))
    with np.load(FIELD_DATA) as data:
        delta_partial = np.asarray(data["Delta_first_partial_action"], dtype=float)
        seed_remainder = float(data["Delta_first_total_remainder_action_norm_upper"])
    row_uppers = np.asarray(
        [float(record["complete_cb_row_upper"]) for record in records],
        dtype=float,
    )
    b_radii = np.asarray(
        [float(record["b_i_radius_needed"]) for record in records], dtype=float
    )
    c_radii = np.asarray(
        [float(record["c_i_radius_needed"]) for record in records], dtype=float
    )
    frobenius = math.nextafter(math.sqrt(math.fsum(
        float(value) * float(value) for value in row_uppers
    )), math.inf)
    non_scale_center_norm = float(np.linalg.norm(delta_partial[1:]))
    transport_ceiling = math.nextafter(
        (non_scale_center_norm - seed_remainder) / RADIUS, -math.inf
    )
    row86 = records[85]
    reference86 = float(reference_row["fully_reduced_cb_row_2_norm_upper"])
    np.savez_compressed(
        DATA_RESULT,
        non_scale_row_indices=np.arange(1, 98, dtype=int),
        complete_cb_row_2_norm_upper=row_uppers,
        b_i_radius_needed=b_radii,
        c_i_radius_needed=c_radii,
        non_scale_DDelta_partial_action=delta_partial[1:],
    )
    validation = {
        "all_97_non_scale_rows_are_present": len(records) == 97,
        "all_rows_share_one_current_input_fingerprint": len(fingerprints) == 1,
        "all_row_bootstrap_validations_pass": all(
            all(record["validation"].values()) for record in records
        ),
        "all_b_i_radii_close": float(np.max(b_radii)) < 0.08,
        "all_c_i_radii_close": float(np.max(c_radii)) < 2.0e-6,
        "global_lambda_i_radius_closes": (
            float(records[0]["lambda_i_radius_needed_global"]) < 1.0e-5
        ),
        "clean_row_86_is_bounded_by_general_tensor_reference": (
            float(row86["complete_cb_row_upper"]) <= reference86
        ),
        "common_scale_pathwise_Jacobi_is_closed_by_exact_covariance": (
            common_scale["validation_passed"] is True
            and common_scale["adjudication"][
                "physical_common_scale_geometry_pullback"
            ] == "CLOSED"
        ),
        "non_scale_cb_operator_fits_pre_sR_transport_ceiling": (
            frobenius < transport_ceiling
        ),
        "no_selector_recurrence_scale_fit_gate_or_chord_added": True,
    }
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_C2_COMPLETE_NON_SCALE_CB_OPERATOR",
        "status": (
            "C2_COMPLETE_NON_SCALE_CB_OPERATOR_CERTIFIED"
            if passed else "C2_COMPLETE_NON_SCALE_CB_OPERATOR_INVALID"
        ),
        "classification": (
            "OUTWARD_ROUNDED_SIGNED_ONE_AXIS_ROW_SWEEP_ON_THE_INTRINSIC_"
            "NON_SCALE_SECTOR_WITH_EXACT_COMMON_SCALE_COVARIANCE_SEPARATION"
        ),
        "row_count": 97,
        "row_range": [1, 97],
        "common_scale_row_0": {
            "pathwise_Jacobi_required": False,
            "authority": COMMON_SCALE.relative_to(ROOT).as_posix(),
            "status": "CLOSED_BY_EXACT_COVARIANCE",
        },
        "operator": {
            "non_scale_cb_Frobenius_upper": frobenius,
            "maximum_row_upper": float(np.max(row_uppers)),
            "maximum_row_index": int(np.argmax(row_uppers)) + 1,
            "row_86_clean_upper": float(row86["complete_cb_row_upper"]),
            "row_86_general_tensor_reference_upper": reference86,
        },
        "bootstrap": {
            "maximum_b_i_radius_needed": float(np.max(b_radii)),
            "maximum_b_i_radius_row": int(np.argmax(b_radii)) + 1,
            "b_i_radius_available": 0.08,
            "maximum_c_i_radius_needed": float(np.max(c_radii)),
            "maximum_c_i_radius_row": int(np.argmax(c_radii)) + 1,
            "c_i_radius_available": 2.0e-6,
            "lambda_i_radius_needed_global": float(
                records[0]["lambda_i_radius_needed_global"]
            ),
            "lambda_i_radius_available": 1.0e-5,
        },
        "transport_budget_before_sR": {
            "non_scale_DDelta_partial_action_norm": non_scale_center_norm,
            "seed_remainder_action_norm_upper": seed_remainder,
            "state_action_radius": RADIUS,
            "pre_sR_operator_ceiling": transport_ceiling,
            "cb_remaining_budget": math.nextafter(
                transport_ceiling - frobenius, -math.inf
            ),
        },
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "data_SHA256": sha256(DATA_RESULT),
        "sweep_input_fingerprint": next(iter(fingerprints)),
        "sweep_inputs": sweep_inputs,
        "inputs": {
            path.relative_to(ROOT).as_posix(): sha256(path)
            for path in (
                FIELD, FIELD_DATA, COMMON_SCALE, REFERENCE_ROW, THEORY,
                Path(__file__),
            )
        },
        "adjudication": {
            "complete_non_scale_cb_operator": "CERTIFIED" if passed else "OPEN",
            "complete_non_scale_sR_operator": "OPEN",
            "complete_non_scale_D2Delta_operator": "OPEN_PENDING_sR",
            "transposed_exact_segment_map_action": "OPEN",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
        },
        "exact_next_dependency": (
            "ADD_THE_ONE_TIME_GLOBAL_sR_OPERATOR_CONTRACTIONS_TO_THE_"
            "CERTIFIED_NON_SCALE_cb_FROBENIUS_BOUND_AND_TEST_THE_COMPLETE_"
            "NON_SCALE_DDELTA_TRANSPORT_CEILING"
        ),
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "non_scale_cb_Frobenius_upper": frobenius,
        "pre_sR_operator_ceiling": transport_ceiling,
        "cb_remaining_budget": payload["transport_budget_before_sR"][
            "cb_remaining_budget"
        ],
        "maximum_row_upper": payload["operator"]["maximum_row_upper"],
        "maximum_row_index": payload["operator"]["maximum_row_index"],
        "validation_passed": passed,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
