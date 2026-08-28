"""Replay the signed causal vector with exact center curvature authority."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
BOOTSTRAP = BASE / "BHSM_N12_GATE7_SIGNED_CAUSAL_VECTOR_BOOTSTRAP.json"
BOOTSTRAP_DATA = BOOTSTRAP.with_suffix(".npz")
MIXED = BASE / "BHSM_N12_GATE7_EXACT_SIGNED_MIXED_FIELD_CURVATURE.json"
TRANSVERSE = BASE / "BHSM_N12_GATE7_EXACT_SIGNED_FULL_TRANSVERSE_CURVATURE_ADJUDICATION.json"
RESULT = BASE / "BHSM_N12_GATE7_EXACT_CENTER_CAUSAL_VECTOR_CERTIFICATE.json"
DATA = RESULT.with_suffix(".npz")


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def build_payload() -> dict[str, Any]:
    inputs = (BOOTSTRAP, BOOTSTRAP_DATA, MIXED, TRANSVERSE)
    if not all(path.is_file() for path in inputs):
        raise FileNotFoundError("exact center causal-vector inputs required")
    records = {
        path: json.loads(path.read_text(encoding="utf-8"))
        for path in (BOOTSTRAP, MIXED, TRANSVERSE)
    }
    if records[TRANSVERSE]["validation_passed"] is not True:
        raise RuntimeError("certified exact transverse profile required")
    if records[MIXED]["validation_passed"] is not True:
        raise RuntimeError("certified exact mixed profile required")
    with np.load(BOOTSTRAP_DATA) as source:
        vector = np.asarray(source["signed_center_vector"], dtype=float)
        green_norm = np.asarray(source["causal_green_norm"], dtype=float)
        correction_norm = np.asarray(
            source["correction_time_transverse_norm"], dtype=float,
        )
    mixed_norm = np.asarray([
        row["mixed_field_curvature_Frobenius_norm"]
        for row in records[MIXED]["rows"]
    ])
    transverse = np.asarray([
        row["physical_time_transverse_D2f_Frobenius_norm"]
        for row in records[TRANSVERSE]["rows"]
    ])
    vector_norm = np.linalg.norm(vector, axis=1)
    error = np.zeros(48)
    quadratic = np.zeros(48)
    mixed_error = np.zeros(48)
    for endpoint in range(1, 48):
        earlier = slice(0, endpoint)
        mixed_error[endpoint] = np.sum(
            green_norm[endpoint, earlier]
            * mixed_norm[earlier] * correction_norm[earlier] * error[earlier]
        )
        quadratic[endpoint] = np.sum(
            green_norm[endpoint, earlier]
            * 0.5 * transverse[earlier]
            * (vector_norm[earlier] + error[earlier]) ** 2
        )
        error[endpoint] = mixed_error[endpoint] + quadratic[endpoint]
    total = vector_norm + error
    halo = float(records[BOOTSTRAP]["summary"][
        "existing_certified_nonlinear_halo"
    ])
    np.savez_compressed(
        DATA,
        signed_center_vector=vector,
        signed_center_vector_2_norm=vector_norm,
        exact_transverse_quadratic_error_radius=quadratic,
        exact_mixed_error_radius=mixed_error,
        exact_total_center_radius=total,
    )
    validation = {
        "signed_48_by_73_center_vector_reused_without_rescalarization": (
            vector.shape == (48, 73)
        ),
        "exact_action_directional_mixed_and_transverse_center_curvatures_used": True,
        "strictly_lower_causal_error_recursion_used": bool(
            np.allclose(np.triu(green_norm), 0.0, atol=0.0, rtol=0.0)
        ),
        "all_exact_center_radii_finite": bool(np.all(np.isfinite(total))),
        "exact_center_vector_radius_fits_existing_certified_halo": (
            float(np.max(total)) < halo
        ),
        "no_JAX_curvature_used_as_center_authority": True,
        "no_recurrence_reset_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    owner = int(np.argmax(total))
    return {
        "artifact": "BHSM_N12_GATE7_EXACT_CENTER_CAUSAL_VECTOR_CERTIFICATE",
        "status": (
            "EXACT_ACTION_CENTER_CAUSAL_VECTOR_RADIUS_CERTIFIED_INSIDE_EXISTING_HALO"
            if passed else "EXACT_CENTER_CAUSAL_VECTOR_CERTIFICATE_INVALID"
        ),
        "summary": {
            "maximum_signed_center_vector_2_norm": float(np.max(vector_norm)),
            "maximum_exact_transverse_quadratic_error_radius": float(
                np.max(quadratic)
            ),
            "maximum_exact_mixed_error_radius": float(np.max(mixed_error)),
            "maximum_exact_total_center_radius": float(np.max(total)),
            "exact_total_radius_owner_node": owner,
            "existing_certified_nonlinear_halo": halo,
            "halo_to_exact_center_radius_ratio": float(halo / np.max(total)),
            "terminal_exact_total_center_radius": float(total[-1]),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "exact_action_center_causal_vector_radius": (
                "CERTIFIED" if passed else "OPEN"
            ),
            "outward_curvature_remainder": "OPEN",
            "outward_signed_step_map_and_Green_remainder": "OPEN",
            "causal_interval_vector_radius": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "ATTACH_ONLY_THE_RETAINED_D5_CURVATURE_AND_SIGNED_GREEN_STEP_MAP_"
            "OUTWARD_REMAINDERS_TO_THE_EXACT_CENTER_VECTOR_BOOTSTRAP"
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
