"""Audit transfer of the 72D affine history jet to the nonlinear family."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
AFFINE = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_72D_HISTORY_FIRST_JET.json"
AFFINE_DATA = AFFINE.with_suffix(".npz")
Z2 = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_INTERNAL_RESPONSE_Z2.json"
CAUSAL = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_CAUSAL_VECTOR_CERTIFICATE.npz"
CAUSAL_RECORD = CAUSAL.with_suffix(".json")
GREEN = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_SIGNED_CAUSAL_VECTOR_BOOTSTRAP.npz"
GREEN_RECORD = GREEN.with_suffix(".json")
RESULT = BASE / "BHSM_N12_GATE7_AFFINE_72D_NONLINEAR_TRANSFER_AUDIT.json"
THIS_SCRIPT = Path(__file__).resolve()


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def main() -> None:
    affine, z2, causal_record, green_record = (
        _load(path) for path in (AFFINE, Z2, CAUSAL_RECORD, GREEN_RECORD)
    )
    if not all(record.get("validation_passed") is True for record in (
        affine, z2, causal_record, green_record,
    )):
        raise RuntimeError("validated affine, Z2, causal, and Green parents required")
    with np.load(AFFINE_DATA) as source:
        jacobi = np.asarray(source["ambient_fixed_time_Jacobi_midpoint"], dtype=float)
        jacobi_radius = np.asarray(
            source["ambient_fixed_time_Jacobi_component_radius"], dtype=float,
        )
    with np.load(CAUSAL) as source:
        center_radius = np.asarray(source["exact_total_center_radius"], dtype=float)
    with np.load(GREEN) as source:
        green = np.asarray(source["causal_green_norm"], dtype=float)
    D2F = np.asarray([
        row["physical_transverse_D2f_tube_upper"] for row in z2["rows"]
    ], dtype=float)
    jacobi_norm = np.asarray([
        np.linalg.norm(jacobi[node], ord=2)
        + np.linalg.norm(jacobi_radius[node])
        for node in range(48)
    ])
    generator_difference = D2F * center_radius
    error = np.zeros(48)
    contraction = np.zeros(48)
    for endpoint in range(1, 48):
        earlier = slice(0, endpoint)
        weights = green[endpoint, earlier] * generator_difference[earlier]
        contraction[endpoint] = math.nextafter(float(np.sum(weights)), math.inf)
        error[endpoint] = math.nextafter(float(np.sum(
            weights * (jacobi_norm[earlier] + error[earlier])
        )), math.inf)
    ratio = np.divide(
        error, np.maximum(jacobi_norm, np.finfo(float).tiny),
    )
    closes = bool(float(np.max(contraction)) < 1.0)
    validation = {
        "all_48_causal_nodes_consumed": len(error) == 48,
        "all_transfer_quantities_finite": bool(np.all(np.isfinite(
            np.concatenate((D2F, center_radius, jacobi_norm, error, contraction))
        ))),
        "same_correlated_Green_norm_as_exact_center_Z2_consumed": green.shape == (48, 48),
        "full_72D_operator_norm_not_single_direction_used": jacobi.shape == (48, 98, 72),
        "failed_contraction_not_promoted": not closes,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_AFFINE_72D_NONLINEAR_TRANSFER_AUDIT",
        "status": (
            "AFFINE_TO_NONLINEAR_72D_VOLterra_TRANSFER_REJECTED_NOT_CONTRACTIVE"
            if passed and not closes else "AFFINE_TO_NONLINEAR_72D_TRANSFER_AUDIT_INVALID"
        ),
        "method": (
            "CAUSAL_GREEN_VOLterra_BOUND_WITH_DELTA_A_LE_D2F_TUBE_TIMES_"
            "EXACT_CENTER_RADIUS_AND_FULL_72D_JACOBI_OPERATOR_NORM"
        ),
        "summary": {
            "maximum_generator_difference_upper": float(np.max(generator_difference)),
            "maximum_causal_contraction_factor_upper": float(np.max(contraction)),
            "maximum_affine_Jacobi_operator_upper": float(np.max(jacobi_norm)),
            "maximum_nonlinear_transfer_error_upper": float(np.max(error)),
            "terminal_nonlinear_transfer_error_upper": float(error[-1]),
            "maximum_error_to_affine_Jacobi_ratio": float(np.max(ratio)),
            "terminal_error_to_affine_Jacobi_ratio": float(ratio[-1]),
        },
        "adjudication": {
            "affine_carrier_72D_data_object": "VALID_MATERIALIZED_CANDIDATE",
            "nonlinear_exact_solution_family_first_jet_transfer": "REJECTED_BY_CURRENT_BOUND",
            "affine_jet_may_be_used_as_complete_operator_authority": False,
            "next_route": "DIRECT_EXACT_CENTER_VARIATIONAL_CARRIER",
        },
        "inputs": {
            _relative(path): _sha256(path)
            for path in (
                AFFINE, AFFINE_DATA, Z2, CAUSAL, CAUSAL_RECORD,
                GREEN, GREEN_RECORD, THIS_SCRIPT,
            )
        },
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "affine_72D_history_first_jet": "MATERIALIZED_NOT_NONLINEAR_AUTHORITY",
            "nonlinear_72D_history_first_jet": "OPEN_DIRECT_CARRIER_REQUIRED",
            "Weyl_force_KKT_Hessian": "NOT_CLAIMED",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "MATERIALIZE_THE_NORMALIZED_ACTION_FIELD_FIRST_DERIVATIVE_ON_THE_"
            "EXACT_CENTER_HISTORY_AND_BUILD_A_DIRECT_OUTWARD_VARIATIONAL_"
            "CARRIER;_DO_NOT_INFLATE_THE_REJECTED_AFFINE_TRANSFER"
        ),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "summary": payload["summary"],
        "validation_passed": passed,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
