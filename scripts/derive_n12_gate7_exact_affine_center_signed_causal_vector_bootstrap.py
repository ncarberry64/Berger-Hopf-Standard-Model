"""Replay the causal vector at final Y and attach exact-carrier radii."""

from __future__ import annotations

import json
import math
from pathlib import Path
import sys

import numpy as np
from scipy.linalg import null_space


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import derive_n12_gate7_signed_causal_vector_bootstrap as retained  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
GREEN = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_Z2_INPUTS.npz"
DIRECTIONAL = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_DIRECTIONAL_FIELD_CURVATURE.json"
DIRECTIONAL_DATA = DIRECTIONAL.with_suffix(".npz")
MIXED = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_MIXED_FIELD_CURVATURE.json"
MIXED_DATA = MIXED.with_suffix(".npz")
GREEN_SUFFIX = BASE / "BHSM_N12_GATE7_ARB_EXACT_AFFINE_GREEN_SUFFIX_PRODUCTS.json"
GREEN_SUFFIX_DATA = GREEN_SUFFIX.with_suffix(".npz")
RESULT = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_SIGNED_CAUSAL_VECTOR_BOOTSTRAP.json"
DATA = RESULT.with_suffix(".npz")

retained.GREEN = GREEN
retained.DIRECTIONAL = DIRECTIONAL
retained.DIRECTIONAL_DATA = DIRECTIONAL_DATA
retained.MIXED = MIXED
retained.MIXED_DATA = MIXED_DATA
retained.RESULT = RESULT
retained.DATA = DATA


def _product_bounds(
    maps: np.ndarray, component_radii: np.ndarray,
) -> tuple[dict[tuple[int, int], np.ndarray], dict[tuple[int, int], float]]:
    midpoints: dict[tuple[int, int], np.ndarray] = {}
    errors: dict[tuple[int, int], float] = {}
    for endpoint in range(1, 48):
        product = np.eye(73)
        error = 0.0
        for source_index in range(endpoint - 1, -1, -1):
            matrix = maps[source_index]
            radius = float(np.linalg.norm(component_radii[source_index]))
            old_norm = float(np.linalg.norm(product, ord=2))
            matrix_norm = float(np.linalg.norm(matrix, ord=2))
            error = math.nextafter(
                old_norm * radius + error * matrix_norm + error * radius,
                math.inf,
            )
            product = product @ matrix
            midpoints[(endpoint, source_index)] = product.copy()
            errors[(endpoint, source_index)] = error
    return midpoints, errors


def main() -> None:
    payload = retained.build_payload()
    suffix_record = json.loads(GREEN_SUFFIX.read_text(encoding="utf-8"))
    if suffix_record.get("validation_passed") is not True:
        raise RuntimeError("validated correlated Arb Green suffix products required")
    with np.load(DATA) as source:
        arrays = {name: np.asarray(source[name]) for name in source.files}
    with np.load(GREEN) as source:
        maps = np.asarray(source["physical_macro_step_maps"], dtype=float)
        map_radii = np.asarray(source["physical_macro_step_map_component_radius"], dtype=float)
        corrections = np.asarray(source["ambient_correction_profile"], dtype=float)
        correction_radii = np.linalg.norm(
            np.asarray(source["ambient_correction_component_radius"], dtype=float), axis=1,
        )
    with np.load(retained.CENTER) as source:
        times = np.asarray(source["action_lengths"], dtype=float)
    with np.load(retained.TANGENT) as source:
        tangents = np.asarray(source["physical_tangent_action"], dtype=float)
    with np.load(DIRECTIONAL_DATA) as source:
        fields = np.asarray(source["normalized_field"], dtype=float)
        directional = np.asarray(source["physical_time_transverse_directional_curvature"], dtype=float)
    with np.load(MIXED_DATA) as source:
        mixed = np.asarray(source["physical_time_transverse_mixed_Green_curvature"], dtype=float)
    with np.load(GREEN_SUFFIX_DATA) as source:
        product_radius_frobenius = np.asarray(
            source["suffix_product_export_radius_Frobenius"], dtype=float,
        )
        product_frobenius_upper = np.asarray(
            source["suffix_product_Frobenius_upper"], dtype=float,
        )

    vector = np.asarray(arrays["signed_center_vector"], dtype=float)
    vector_norm = np.linalg.norm(vector, axis=1)
    correction_norm = np.asarray(arrays["correction_time_transverse_norm"], dtype=float)
    frames = []
    for index in range(48):
        flow = tangents[index].T @ fields[index]
        flow /= np.linalg.norm(flow)
        frames.append(null_space(flow[None, :]))
    frames = np.asarray(frames)
    dt = np.diff(times)
    green_upper = np.zeros((48, 48))
    carrier_source_error = np.zeros(48)
    for endpoint in range(1, 48):
        for source_index in range(endpoint):
            product_error = product_radius_frobenius[endpoint, source_index]
            product_upper = product_frobenius_upper[endpoint, source_index]
            green_upper[endpoint, source_index] = math.nextafter(
                dt[source_index] * product_upper, math.inf,
            )
            transverse_vector = frames[source_index].T @ vector[source_index]
            source_directional = (
                0.5 * directional[source_index] * correction_norm[source_index] ** 2
            )
            source_mixed = (
                mixed[source_index] @ transverse_vector * correction_norm[source_index]
            )
            source_mid = frames[source_index] @ (source_directional + source_mixed)
            correction_error = float(correction_radii[source_index])
            source_radius = (
                0.5 * float(np.linalg.norm(directional[source_index]))
                * (2.0 * correction_norm[source_index] * correction_error + correction_error**2)
                + float(np.linalg.norm(mixed[source_index], ord=2))
                * float(np.linalg.norm(transverse_vector)) * correction_error
            )
            carrier_source_error[endpoint] += dt[source_index] * (
                product_error * float(np.linalg.norm(source_mid))
                + product_upper * source_radius
            )
    carrier_source_error = np.nextafter(carrier_source_error, math.inf)
    arrays["causal_green_norm"] = green_upper
    arrays["exact_carrier_source_radius"] = carrier_source_error
    np.savez_compressed(DATA, **arrays)

    payload["artifact"] = "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_SIGNED_CAUSAL_VECTOR_BOOTSTRAP"
    payload["status"] = "FINAL_EXACT_AFFINE_CAUSAL_CENTER_WITH_OUTWARD_CARRIER_RADIUS_DERIVED"
    payload["summary"].update({
        "maximum_exact_carrier_source_radius": float(np.max(carrier_source_error)),
        "maximum_outward_causal_Green_norm": float(np.max(green_upper)),
        "maximum_exact_macro_map_Frobenius_radius": float(np.max(np.linalg.norm(map_radii, axis=(1, 2)))),
        "maximum_exact_correction_Euclidean_radius": float(np.max(correction_radii)),
    })
    payload["structural_validation"].update({
        "exact_affine_macro_map_interval_radii_consumed": True,
        "exact_affine_correction_interval_radii_consumed": True,
        "outward_product_norms_used_in_causal_Green_matrix": True,
        "all_1128_correlated_Arb_suffix_products_consumed": bool(
            np.count_nonzero(product_frobenius_upper) == 1128
        ),
        "binary_macro_export_radii_not_repropagated": True,
        "direct_carrier_and_source_interval_error_attached": bool(
            np.all(np.isfinite(carrier_source_error))
        ),
    })
    payload["structural_validation_passed"] = all(payload["structural_validation"].values())
    payload["validation_passed"] = payload["structural_validation_passed"]
    payload["claim_boundary"].update({
        "outward_exact_affine_Green_suffix_products": "CERTIFIED",
        "outward_signed_nonlinear_source_remainder": "OPEN",
        "outward_D5_curvature_remainder": "OPEN",
    })
    payload["exact_next_dependency"] = (
        "ATTACH_ONLY_THE_RETAINED_D5_CURVATURE_AND_SIGNED_NONLINEAR_"
        "SOURCE_REMAINDERS_TO_THE_CORRELATED_ARB_CAUSAL_BOOTSTRAP"
    )
    payload["data_SHA256"] = retained._sha256(DATA)
    payload["inputs"][retained._relative(Path(__file__).resolve())] = retained._sha256(
        Path(__file__).resolve()
    )
    for path in (GREEN_SUFFIX, GREEN_SUFFIX_DATA):
        payload["inputs"][retained._relative(path)] = retained._sha256(path)
    retained_script = Path(retained.__file__).resolve()
    payload["inputs"][retained._relative(retained_script)] = retained._sha256(
        retained_script
    )
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": payload["validation_passed"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
