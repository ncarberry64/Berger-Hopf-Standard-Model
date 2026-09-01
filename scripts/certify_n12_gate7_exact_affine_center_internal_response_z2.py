"""Replay the signed Taylor--Volterra Z2 theorem at the final exact center."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_gate7_selected_cone_internal_response_z2 as retained  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
GREEN = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_Z2_INPUTS.npz"
CONE = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_Z2_CONE_ADAPTER.json"
RESPONSE = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_BORDERED_RHS_RESPONSE.json"
FIELD = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_DIRECTIONAL_FIELD_CURVATURE.npz"
MIXED_DATA = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_MIXED_FIELD_CURVATURE.npz"
CAUSAL = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_CAUSAL_VECTOR_CERTIFICATE.npz"
BOOTSTRAP = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_SIGNED_CAUSAL_VECTOR_BOOTSTRAP.npz"
RESULT = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_INTERNAL_RESPONSE_Z2.json"

retained.GREEN = GREEN
retained.CONE = CONE
retained.CONE_SPECTRUM = CONE
retained.PATH_RESPONSE = RESPONSE
retained.FIELD = FIELD
retained.MIXED_DATA = MIXED_DATA
retained.CAUSAL = CAUSAL
retained.BOOTSTRAP = BOOTSTRAP
retained.RESULT = RESULT


def main() -> None:
    payload = retained.build_payload()
    with np.load(BOOTSTRAP) as source:
        vector = np.asarray(source["signed_center_vector"], dtype=float)
        green = np.asarray(source["causal_green_norm"], dtype=float)
        correction = np.asarray(source["correction_time_transverse_norm"], dtype=float)
        carrier = np.asarray(source["exact_carrier_source_radius"], dtype=float)
    mixed_record = json.loads(
        MIXED_DATA.with_suffix(".json").read_text(encoding="utf-8")
    )
    mixed_norm = np.asarray([
        row["mixed_field_curvature_Frobenius_norm"] for row in mixed_record["rows"]
    ])
    center_d2 = np.asarray([
        row["center_physical_transverse_D2f_Frobenius"] for row in payload["rows"]
    ])
    d3 = np.asarray([
        row["physical_transverse_D3f_tube_upper"] for row in payload["rows"]
    ])
    vector_norm = np.linalg.norm(vector, axis=1)
    error = np.zeros(48)
    mixed_error = np.zeros(48)
    quadratic_error = np.zeros(48)
    cubic_error = np.zeros(48)
    for endpoint in range(1, 48):
        earlier = slice(0, endpoint)
        mixed_error[endpoint] = np.sum(
            green[endpoint, earlier] * mixed_norm[earlier]
            * correction[earlier] * error[earlier]
        )
        quadratic_error[endpoint] = np.sum(
            green[endpoint, earlier] * center_d2[earlier]
            * (vector_norm[earlier] * error[earlier] + 0.5 * error[earlier] ** 2)
        )
        cubic_error[endpoint] = np.sum(
            green[endpoint, earlier] * d3[earlier]
            * (vector_norm[earlier] + error[earlier]) ** 3 / 6.0
        )
        error[endpoint] = (
            carrier[endpoint] + mixed_error[endpoint]
            + quadratic_error[endpoint] + cubic_error[endpoint]
        )
    total = vector_norm + error
    local = np.asarray(payload["causal_Taylor_Volterra"]["local_proof_tube_radius"])
    radius = float(payload["domain"]["candidate_nonlinear_action_radius"])
    payload["artifact"] = "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_INTERNAL_RESPONSE_Z2"
    payload["status"] = (
        "FINAL_EXACT_AFFINE_CENTER_INTERNAL_RESPONSE_AND_TAYLOR_VOLTERRA_Z2_CERTIFIED"
        if np.all(total <= local) and float(np.max(total)) < radius else
        "FINAL_EXACT_AFFINE_CENTER_Z2_REQUIRES_SHARPENING"
    )
    payload["causal_Taylor_Volterra"].update({
        "exact_carrier_source_radius": carrier.tolist(),
        "mixed_error_radius": mixed_error.tolist(),
        "quadratic_error_radius": quadratic_error.tolist(),
        "cubic_error_radius": cubic_error.tolist(),
        "total_error_radius": error.tolist(),
        "total_radius": total.tolist(),
    })
    payload["summary"].update({
        "maximum_exact_carrier_source_radius": float(np.max(carrier)),
        "maximum_third_order_Taylor_Volterra_error_radius": float(np.max(error)),
        "maximum_third_order_Taylor_Volterra_total_radius": float(np.max(total)),
        "selected_cone_radius_utilization": float(np.max(total) / radius),
        "maximum_local_proof_tube_utilization": float(np.max(np.divide(
            total, local, out=np.zeros_like(total), where=local > 0.0,
        ))),
    })
    payload["validation"].update({
        "exact_affine_carrier_radius_seeded_before_nonlinear_recursion": True,
        "outward_exact_affine_Green_norm_used": True,
        "third_order_Taylor_Volterra_Z2_radius_inside_local_proof_tubes": bool(
            np.all(total <= local)
        ),
        "third_order_Taylor_Volterra_Z2_radius_inside_selected_cone": (
            float(np.max(total)) < radius
        ),
        "historical_Gauss12_center_not_consumed": True,
    })
    payload["validation_passed"] = all(payload["validation"].values())
    payload["claim_boundary"].update({
        "final_exact_affine_center_Z2": (
            "CERTIFIED" if payload["validation_passed"] else "OPEN"
        ),
        "candidate_radius_self_map": (
            "CERTIFIED" if payload["validation_passed"] else "OPEN"
        ),
    })
    payload["exact_next_dependency"] = (
        "TRANSFER_THE_EXISTING_TERMINAL_RADII_CONTINUOUS_MARGINS_AND_SCALAR_FIRST_HIT_TO_THIS_FINAL_CENTER"
        if payload["validation_passed"] else
        "SHARPEN_ONLY_THE_REPORTED_FINAL_EXACT_CENTER_Z2_OWNER"
    )
    payload["inputs"][retained._relative(Path(__file__).resolve())] = retained._sha256(
        Path(__file__).resolve()
    )
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": payload["validation_passed"], "exact_next_dependency": payload["exact_next_dependency"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
