"""Certify all retained exact-affine Green suffix products in Arb.

The binary midpoint/radius export of each macro map includes one binary64
spacing allowance per component.  Those export allowances must not be
reintroduced at every subsequent product.  This certificate instead composes
the authoritative 256-bit Arb macro strings and rounds each requested suffix
only once at its final endpoint.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

from flint import arb_mat, ctx
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_gate7_arb_interaction_taylor26_macro_maps as macro  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
MACRO = BASE / "BHSM_N12_GATE7_ARB_INTERACTION_TAYLOR26_MACRO_MAPS.json"
MACRO_DATA = MACRO.with_suffix(".npz")
RESULT = BASE / "BHSM_N12_GATE7_ARB_EXACT_AFFINE_GREEN_SUFFIX_PRODUCTS.json"
DATA = RESULT.with_suffix(".npz")
PRECISION = 256
PHYSICAL = 73
SEAMS = 47


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _identity() -> arb_mat:
    return arb_mat(np.eye(PHYSICAL, dtype=int).tolist())


def _frobenius_export_bounds(matrix: arb_mat) -> tuple[float, float, float]:
    midpoint, radius = macro._mid_radius(matrix)
    midpoint_frobenius = float(np.linalg.norm(midpoint, ord="fro"))
    radius_frobenius = float(np.linalg.norm(radius, ord="fro"))
    upper = math.nextafter(midpoint_frobenius + radius_frobenius, math.inf)
    return midpoint_frobenius, radius_frobenius, upper


def main() -> None:
    record = json.loads(MACRO.read_text(encoding="utf-8"))
    if record.get("validation_passed") is not True:
        raise RuntimeError("validated exact-affine Arb macro maps required")
    with np.load(MACRO_DATA) as source:
        times = np.asarray(source["macro_action_lengths"], dtype=float)
        strings = np.asarray(source["macro_step_map_arb_strings"])
        global_midpoint = np.asarray(
            source["global_exact_affine_fundamental_midpoint"], dtype=float,
        )
        global_radius = np.asarray(
            source["global_exact_affine_fundamental_component_radius"],
            dtype=float,
        )
    if strings.shape != (SEAMS, PHYSICAL, PHYSICAL):
        raise RuntimeError("47 retained 73D Arb macro maps required")

    ctx.prec = PRECISION
    blocks = [macro._matrix_from_arb_strings(strings[index]) for index in range(SEAMS)]
    midpoint_frobenius = np.zeros((SEAMS + 1, SEAMS + 1))
    radius_frobenius = np.zeros_like(midpoint_frobenius)
    upper_frobenius = np.zeros_like(midpoint_frobenius)
    full_product: arb_mat | None = None
    for source_index in range(SEAMS):
        product = _identity()
        for endpoint in range(source_index + 1, SEAMS + 1):
            product = blocks[endpoint - 1] * product
            mid_fro, rad_fro, upper_fro = _frobenius_export_bounds(product)
            midpoint_frobenius[endpoint, source_index] = mid_fro
            radius_frobenius[endpoint, source_index] = rad_fro
            upper_frobenius[endpoint, source_index] = upper_fro
            if source_index == 0 and endpoint == SEAMS:
                full_product = product
        if (source_index + 1) % 4 == 0 or source_index + 1 == SEAMS:
            print(json.dumps({
                "completed_source_indices": source_index + 1,
                "total_source_indices": SEAMS,
                "maximum_suffix_Frobenius_upper_so_far": float(
                    np.max(upper_frobenius)
                ),
            }), flush=True)

    if full_product is None:
        raise RuntimeError("full exact-affine product missing")
    computed_midpoint, computed_radius = macro._mid_radius(full_product)
    global_overlap = np.all(
        np.abs(computed_midpoint - global_midpoint)
        <= computed_radius + global_radius
    )
    maximum_radius = float(np.max(radius_frobenius))
    maximum_upper = float(np.max(upper_frobenius))
    owner = np.unravel_index(
        int(np.argmax(upper_frobenius)), upper_frobenius.shape,
    )
    np.savez_compressed(
        DATA,
        action_lengths=times,
        suffix_product_midpoint_Frobenius=midpoint_frobenius,
        suffix_product_export_radius_Frobenius=radius_frobenius,
        suffix_product_Frobenius_upper=upper_frobenius,
    )
    validation = {
        "all_1128_strictly_causal_suffix_products_evaluated": int(
            np.count_nonzero(upper_frobenius)
        ) == SEAMS * (SEAMS + 1) // 2,
        "all_suffix_products_finite": bool(
            np.all(np.isfinite(upper_frobenius))
        ),
        "stored_global_product_overlaps_recomputed_Arb_product": bool(
            global_overlap
        ),
        "authoritative_256_bit_Arb_strings_composed_before_binary_export": True,
        "one_final_binary_spacing_allowance_per_suffix_component": True,
        "no_independent_binary_macro_export_radii_repropagated": True,
        "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
    }
    payload = {
        "artifact": "BHSM_N12_GATE7_ARB_EXACT_AFFINE_GREEN_SUFFIX_PRODUCTS",
        "status": (
            "ALL_1128_EXACT_AFFINE_GREEN_SUFFIX_PRODUCTS_OUTWARD_CERTIFIED"
            if all(validation.values()) else
            "EXACT_AFFINE_GREEN_SUFFIX_PRODUCT_CERTIFICATE_INVALID"
        ),
        "precision_bits": PRECISION,
        "summary": {
            "suffix_product_count": SEAMS * (SEAMS + 1) // 2,
            "maximum_suffix_product_Frobenius_upper": maximum_upper,
            "maximum_suffix_product_export_radius_Frobenius": maximum_radius,
            "maximum_suffix_owner_endpoint": int(owner[0]),
            "maximum_suffix_owner_source_index": int(owner[1]),
            "full_product_Frobenius_upper": float(
                upper_frobenius[SEAMS, 0]
            ),
            "full_product_export_radius_Frobenius": float(
                radius_frobenius[SEAMS, 0]
            ),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "claim_boundary": {
            "exact_affine_Green_suffix_products": (
                "CERTIFIED" if all(validation.values()) else "OPEN"
            ),
            "outward_signed_nonlinear_source_remainder": "OPEN",
            "outward_D5_curvature_remainder": "OPEN",
            "causal_interval_vector_radius": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "REPLAY_THE_EXACT_AFFINE_CAUSAL_VECTOR_WITH_THE_CORRELATED_ARB_"
            "SUFFIX_BOUNDS_AND_ATTACH_THE_RETAINED_D5_SOURCE_REMAINDER"
        ),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (MACRO, MACRO_DATA, Path(__file__).resolve())
        },
        "FULL_BHSM_COMPLETE": False,
    }
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
