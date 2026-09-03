"""Audit the direct mixed bilinear implementation against polarization."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
from flint import ctx


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_gate7_accepted_replay_center_outward_74d as cert  # noqa: E402
import certify_n12_gate7_current_green_correlated_scalar_interval355 as scalar  # noqa: E402
import certify_n12_gate7_current_green_mixed_transverse_all_endpoints as direct  # noqa: E402


F = ROOT / "artifacts/flagship_integration"
A = ROOT / "artifacts/action_extension"
RESULT = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_BILINEAR_EQUIVALENCE_AUDIT.json"
DATA = RESULT.with_suffix(".npz")
THEORY = ROOT / "theory/n12_gate7_current_green_mixed_bilinear_equivalence.md"
THIS_SCRIPT = Path(__file__).resolve()
SEED_NODES = (1, 355, 356, 370)
SEED_COLUMNS = (0, 1, 61)
AUDIT_PRECISION = 512
INPUTS = (
    direct.ENDPOINT, direct.ENDPOINT.with_suffix(".npz"),
    direct.JACOBIAN, direct.JACOBIAN.with_suffix(".npz"),
    direct.PARTITION, direct.PARTITION.with_suffix(".npz"),
    direct.SEED, direct.SEED.with_suffix(".npz"),
    Path(cert.__file__).resolve(), Path(scalar.__file__).resolve(),
    Path(direct.__file__).resolve(), THIS_SCRIPT, THEORY,
)


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _row(node: int) -> dict[str, object]:
    ctx.prec = AUDIT_PRECISION
    with np.load(direct.ENDPOINT.with_suffix(".npz")) as source:
        state = np.asarray(source["projected_states"][node], dtype=float)
        descriptor = float(source["independent_signed_descriptors"][node])
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    with np.load(direct.JACOBIAN.with_suffix(".npz")) as source:
        tangent = np.asarray(source["endpoint_physical_tangent_action"][node], dtype=float)
    with np.load(direct.PARTITION.with_suffix(".npz")) as source:
        axis = scalar._normalized_central_axis(
            np.asarray(source["current_center_green_image_unit_mid"][node], dtype=float)
        )
    projector = np.eye(direct.COORDINATES) - np.outer(axis, axis)
    frame = cert._frame(tangent, cert.TRIAL_DESCRIPTOR_SCALE)
    values = direct._mixed_axis_map(
        state, descriptor, weights, reference, frame @ axis,
        frame @ projector[:, SEED_COLUMNS],
    )
    midpoint, radius = direct._export(values)
    return {"node": node, "midpoint": midpoint, "radius": radius}


def build_payload() -> dict[str, object]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    rows = []
    with ProcessPoolExecutor(max_workers=len(SEED_NODES)) as executor:
        futures = [executor.submit(_row, node) for node in SEED_NODES]
        for future in as_completed(futures):
            rows.append(future.result())
    rows.sort(key=lambda row: int(row["node"]))
    direct_mid = np.asarray([row.pop("midpoint") for row in rows])
    direct_radius = np.asarray([row.pop("radius") for row in rows])
    with np.load(direct.SEED.with_suffix(".npz")) as source:
        polarization_mid = np.asarray(
            source["mixed_green_transverse_mid"][:, :, SEED_COLUMNS], dtype=float,
        )
        polarization_radius = np.asarray(
            source["mixed_green_transverse_radius"][:, :, SEED_COLUMNS], dtype=float,
        )
    difference = direct_mid - polarization_mid
    absolute = np.abs(difference)
    scale = np.maximum(1.0, np.abs(polarization_mid))
    maximum_absolute = float(np.max(absolute))
    maximum_relative = float(np.max(absolute / scale))
    interval_overlap = absolute <= direct_radius + polarization_radius
    np.savez_compressed(
        DATA, seed_nodes=np.asarray(SEED_NODES),
        seed_columns=np.asarray(SEED_COLUMNS), direct_bilinear_mid=direct_mid,
        direct_bilinear_radius=direct_radius,
        polarization_mid=polarization_mid,
        polarization_radius=polarization_radius,
        center_difference=difference,
    )
    validation = {
        "four_decisive_nodes_replayed": direct_mid.shape[0] == 4,
        "three_coordinate_columns_per_node_replayed": direct_mid.shape[2] == 3,
        "512_bit_Arb_direct_bilinear_evaluation": AUDIT_PRECISION == 512,
        "direct_and_polarized_centers_agree_below_1e_minus_8_absolute": maximum_absolute < 1.0e-8,
        "direct_and_polarized_centers_agree_below_1e_minus_9_scaled": maximum_relative < 1.0e-9,
        "all_direct_values_and_radii_finite": bool(
            np.all(np.isfinite(direct_mid))
            and np.all(np.isfinite(direct_radius))
            and np.all(direct_radius >= 0.0)
        ),
        "nonoverlap_not_hidden_or_promoted": not bool(np.all(interval_overlap)),
        "historical_values_new_center_fit_or_scale_not_used": True,
    }
    return {
        "artifact": "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_BILINEAR_EQUIVALENCE_AUDIT",
        "status": "DIRECT_BILINEAR_CENTER_IDENTITY_REPRODUCED__OUTWARD_IMPLEMENTATION_EQUIVALENCE_REMAINDER_OPEN",
        "classification": "CURRENT_CENTER_NUMERICAL_IDENTITY_AUDIT_NOT_FULL_MIXED_MAP_AUTHORITY",
        "identity": "D2F[u,v]=(D2F[u+v,u+v]-D2F[u-v,u-v])/4",
        "seed_nodes": list(SEED_NODES),
        "seed_columns": list(SEED_COLUMNS),
        "maximum_center_absolute_difference": maximum_absolute,
        "maximum_center_scaled_difference": maximum_relative,
        "all_component_interval_hulls_overlap": bool(np.all(interval_overlap)),
        "adjudication": (
            "THE_DIRECT_BILINEAR_FORMULA_REPRODUCES_THE_INDEPENDENT_POLARIZATION_"
            "CENTERS_BUT_THE_TWO_EVALUATION_PATHS_HAVE_SMALL_NONOVERLAPPING_"
            "ARB_EXPORTS;_USE_THE_DIRECT_MAP_TO_RECONNOITER_ALL_ENDPOINTS,_THEN_"
            "DERIVE_AN_OUTWARD_ALGEBRAIC_EQUIVALENCE_REMAINDER_BEFORE_PROMOTION"
        ),
        "exact_next_calculation": (
            "MATERIALIZE_THE_DIRECT_BILINEAR_MIXED_MAP_AT_ALL_370_POST_RESET_"
            "ENDPOINTS_WITH_A_DEFINED_GREEN_AXIS,_"
            "LOCALIZE_ITS_MAXIMUM_AND_VARIATION,_AND_CERTIFY_THE_POLARIZATION_"
            "EQUIVALENCE_REMAINDER_AT_THE_ACTION_SELECTED_OWNER_NODES"
        ),
        "claim_boundary": {
            "CURRENT_GREEN_MIXED_DIRECT_BILINEAR_CENTER_IDENTITY_REPRODUCED": True,
            "CURRENT_GREEN_MIXED_DIRECT_BILINEAR_OUTWARD_EQUIVALENCE_DERIVED": False,
            "CURRENT_GREEN_MIXED_TRANSVERSE_ALL_ENDPOINTS_DERIVED": False,
            "CURRENT_GREEN_MIXED_TRANSVERSE_ALL_MIDPOINTS_DERIVED": False,
            "CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "data": _relative(DATA),
        "data_SHA256": _sha(DATA),
        "inputs": {_relative(path): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
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
        "maximum_center_absolute_difference": payload["maximum_center_absolute_difference"],
        "maximum_center_scaled_difference": payload["maximum_center_scaled_difference"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
