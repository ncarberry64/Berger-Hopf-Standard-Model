"""Attach the retained exact-curvature recursion to the final exact carrier."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import derive_n12_gate7_exact_center_causal_vector_certificate as retained  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
BOOTSTRAP = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_SIGNED_CAUSAL_VECTOR_BOOTSTRAP.json"
BOOTSTRAP_DATA = BOOTSTRAP.with_suffix(".npz")
MIXED = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_MIXED_FIELD_CURVATURE.json"
RESULT = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_CAUSAL_VECTOR_CERTIFICATE.json"
DATA = RESULT.with_suffix(".npz")

retained.BOOTSTRAP = BOOTSTRAP
retained.BOOTSTRAP_DATA = BOOTSTRAP_DATA
retained.MIXED = MIXED
retained.RESULT = RESULT
retained.DATA = DATA


def main() -> None:
    payload = retained.build_payload()
    bootstrap = json.loads(BOOTSTRAP.read_text(encoding="utf-8"))
    mixed_record = json.loads(MIXED.read_text(encoding="utf-8"))
    transverse_record = json.loads(retained.TRANSVERSE.read_text(encoding="utf-8"))
    with np.load(BOOTSTRAP_DATA) as source:
        vector = np.asarray(source["signed_center_vector"], dtype=float)
        green = np.asarray(source["causal_green_norm"], dtype=float)
        correction = np.asarray(source["correction_time_transverse_norm"], dtype=float)
        carrier = np.asarray(source["exact_carrier_source_radius"], dtype=float)
    vector_norm = np.linalg.norm(vector, axis=1)
    mixed_norm = np.asarray([
        row["mixed_field_curvature_Frobenius_norm"] for row in mixed_record["rows"]
    ])
    transverse = np.asarray([
        row["physical_time_transverse_D2f_Frobenius_norm"]
        for row in transverse_record["rows"]
    ])
    error = np.zeros(48)
    quadratic = np.zeros(48)
    mixed_error = np.zeros(48)
    for endpoint in range(1, 48):
        earlier = slice(0, endpoint)
        mixed_error[endpoint] = np.sum(
            green[endpoint, earlier] * mixed_norm[earlier]
            * correction[earlier] * error[earlier]
        )
        quadratic[endpoint] = np.sum(
            green[endpoint, earlier] * 0.5 * transverse[earlier]
            * (vector_norm[earlier] + error[earlier]) ** 2
        )
        error[endpoint] = carrier[endpoint] + mixed_error[endpoint] + quadratic[endpoint]
    total = vector_norm + error
    halo = float(bootstrap["summary"]["reference_reconnaissance_nonlinear_halo"])
    np.savez_compressed(
        DATA,
        signed_center_vector=vector,
        signed_center_vector_2_norm=vector_norm,
        exact_carrier_source_radius=carrier,
        exact_transverse_quadratic_error_radius=quadratic,
        exact_mixed_error_radius=mixed_error,
        exact_total_center_radius=total,
    )
    payload["artifact"] = "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_CAUSAL_VECTOR_CERTIFICATE"
    payload["status"] = (
        "FINAL_EXACT_AFFINE_ACTION_CENTER_CAUSAL_VECTOR_RADIUS_DERIVED"
        if float(np.max(total)) < halo else
        "FINAL_EXACT_AFFINE_CAUSAL_VECTOR_RADIUS_REQUIRES_SHARPENING"
    )
    payload["summary"].update({
        "maximum_exact_carrier_source_radius": float(np.max(carrier)),
        "maximum_exact_transverse_quadratic_error_radius": float(np.max(quadratic)),
        "maximum_exact_mixed_error_radius": float(np.max(mixed_error)),
        "maximum_exact_total_center_radius": float(np.max(total)),
        "exact_total_radius_owner_node": int(np.argmax(total)),
        "reference_halo_to_exact_center_radius_ratio": float(halo / np.max(total)),
        "terminal_exact_total_center_radius": float(total[-1]),
    })
    payload["validation"].update({
        "exact_affine_carrier_source_radius_seeded_in_causal_recursion": True,
        "outward_exact_affine_Green_norm_consumed": True,
        "final_exact_center_radius_fits_reference_halo": float(np.max(total)) < halo,
    })
    payload["validation_passed"] = all(payload["validation"].values())
    payload["claim_boundary"].update({
        "outward_exact_affine_Green_suffix_products": "CERTIFIED",
        "outward_signed_nonlinear_source_remainder": "OPEN",
        "outward_D5_curvature_remainder": "OPEN",
    })
    payload["exact_next_dependency"] = (
        "ATTACH_ONLY_THE_RETAINED_D5_CURVATURE_AND_SIGNED_NONLINEAR_"
        "SOURCE_REMAINDERS_TO_THE_DERIVED_EXACT_CENTER_CAUSAL_RADIUS"
    )
    payload["data_SHA256"] = retained._sha256(DATA)
    payload["inputs"][retained._relative(Path(__file__).resolve())] = retained._sha256(
        Path(__file__).resolve()
    )
    retained_script = Path(retained.__file__).resolve()
    payload["inputs"][retained._relative(retained_script)] = retained._sha256(
        retained_script
    )
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": payload["validation_passed"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
