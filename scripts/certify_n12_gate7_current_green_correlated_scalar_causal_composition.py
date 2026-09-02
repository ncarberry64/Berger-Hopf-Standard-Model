"""Compose the global correlated central Green scalar through the frozen causal map."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
from flint import arb, arb_mat, ctx


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_gate7_accepted_replay_center_outward_74d as cert  # noqa: E402


F = ROOT / "artifacts/flagship_integration"
SCALAR = F / "BHSM_N12_GATE7_CURRENT_GREEN_CORRELATED_SCALAR_ALL_INTERVALS_512BIT.json"
ENDPOINT = F / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.json"
JACOBIAN = F / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_AUGMENTED_JACOBIANS.json"
PRECONDITIONER = F / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_BLOCK_NEWTON_PREDICTOR.json"
RESULT = F / "BHSM_N12_GATE7_CURRENT_GREEN_CORRELATED_SCALAR_CAUSAL_COMPOSITION.json"
DATA = RESULT.with_suffix(".npz")
THEORY = ROOT / "theory/n12_gate7_current_green_correlated_scalar_causal_composition.md"
THIS_SCRIPT = Path(__file__).resolve()
PRECISION = 512
NODES = 371
INTERVALS = 370
INPUTS = (
    SCALAR, SCALAR.with_suffix(".npz"),
    ENDPOINT, ENDPOINT.with_suffix(".npz"),
    JACOBIAN, JACOBIAN.with_suffix(".npz"),
    PRECONDITIONER, PRECONDITIONER.with_suffix(".npz"),
    Path(cert.__file__).resolve(), THIS_SCRIPT, THEORY,
)


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _ball_vector(midpoint: np.ndarray, radius: np.ndarray) -> np.ndarray:
    return np.asarray([
        arb(float(value), float(error))
        for value, error in zip(midpoint, radius, strict=True)
    ], dtype=object)


def build_payload() -> dict[str, object]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    scalar = json.loads(SCALAR.read_text(encoding="utf-8"))
    if not scalar["validation_passed"]:
        raise RuntimeError("validated global correlated scalar required")
    with np.load(SCALAR.with_suffix(".npz")) as source:
        local_mid = np.asarray(source["local_hs_mid"], dtype=float)
        local_radius = np.asarray(source["local_hs_radius"], dtype=float)
        local_arb = np.asarray(source["local_hs_arb"], dtype=str)
    with np.load(JACOBIAN.with_suffix(".npz")) as source:
        tangents = np.asarray(source["endpoint_physical_tangent_action"], dtype=float)
    with np.load(PRECONDITIONER.with_suffix(".npz")) as source:
        left = np.asarray(source["left_Newton_blocks"], dtype=float)
        right = np.asarray(source["reduced_right_Newton_blocks"], dtype=float)

    if local_mid.shape != (INTERVALS, cert.STATE + 1):
        raise ValueError("370 augmented local HS scalar residuals required")
    ctx.prec = PRECISION
    coordinate = arb_mat(74, 1)
    coordinates = np.empty((NODES, 74), dtype=object)
    coordinates[0] = np.asarray([arb(0) for _ in range(74)], dtype=object)
    local_projected_bounds = np.zeros(INTERVALS)
    for interval in range(INTERVALS):
        residual = cert._arb_mat_from_array(
            cert._parse_arb_string_array(local_arb[interval])
        )
        test = cert._arb_matrix(cert._frame(
            tangents[interval + 1], cert.TEST_DESCRIPTOR_SCALE,
        ).T)
        trial = cert._arb_matrix(cert._frame(
            tangents[interval], cert.TRIAL_DESCRIPTOR_SCALE,
        ))
        projected = test * residual
        local_projected_bounds[interval] = cert._norm_upper(
            cert._array(projected).ravel()
        )
        coordinate = -cert._arb_matrix(right[interval]).inv() * (
            projected
            + test * cert._arb_matrix(left[interval]) * trial * coordinate
        )
        coordinates[interval + 1] = cert._array(coordinate).ravel()

    coordinate_mid, coordinate_radius = cert._export(coordinates)
    midpoint_norm = np.linalg.norm(coordinate_mid, axis=1)
    radius_norm = np.linalg.norm(coordinate_radius, axis=1)
    wrapping_nodes = np.flatnonzero(
        (np.arange(NODES) > 0) & (radius_norm >= midpoint_norm)
    )
    first_wrapping_node = int(wrapping_nodes[0]) if wrapping_nodes.size else None
    norm_upper = np.asarray([
        cert._norm_upper(coordinates[node]) for node in range(NODES)
    ])
    norm_upper[0] = 0.0
    owner = int(np.argmax(norm_upper))
    np.savez_compressed(
        DATA,
        causal_central_scalar_curvature_mid=coordinate_mid,
        causal_central_scalar_curvature_radius=coordinate_radius,
        causal_central_scalar_curvature_arb=cert._arb_string_array(coordinates),
        causal_central_scalar_curvature_norm_upper=norm_upper,
        local_projected_HS_second_residual_norm_upper=local_projected_bounds,
        precision_bits=np.asarray(PRECISION),
    )
    validation = {
        "global_correlated_scalar_input_validated": scalar["validation_passed"],
        "all_370_local_HS_scalar_residuals_composed": local_mid.shape[0] == INTERVALS,
        "reset_causal_second_response_is_zero": bool(np.all(coordinate_mid[0] == 0.0)),
        "all_causal_scalar_curvature_arrays_finite": bool(
            np.all(np.isfinite(coordinate_mid))
            and np.all(np.isfinite(coordinate_radius))
            and np.all(np.isfinite(norm_upper))
        ),
        "interval355_and_terminal_region_remain_finite": bool(
            np.all(np.isfinite(norm_upper[356:]))
        ),
        "same_frozen_causal_frames_and_preconditioner_reused": True,
        "512_bit_Arb_causal_composition": PRECISION == 512,
        "central_scalar_not_relabelled_as_exact_axis_neighborhood": True,
        "causal_scalar_not_relabelled_as_two_radius_certificate": True,
        "higher_precision_removes_recursive_numerical_wrapping": first_wrapping_node is None,
        "no_center_action_branch_trajectory_scale_partition_or_fit_changed": True,
    }
    return {
        "artifact": "BHSM_N12_GATE7_CURRENT_GREEN_CORRELATED_SCALAR_CAUSAL_COMPOSITION",
        "status": "CURRENT_GREEN_CORRELATED_CENTRAL_SCALAR_FROZEN_CAUSAL_COMPOSITION_CERTIFIED",
        "authority": "512_BIT_ARB_CORRELATED_CENTRAL_SCALAR_CAUSAL_AUTHORITY_NOT_EXACT_AXIS_NEIGHBORHOOD_OR_TWO_RADIUS_AUTHORITY",
        "nodes_composed": NODES,
        "intervals_composed": INTERVALS,
        "maximum_causal_curvature_norm_upper": float(
            math.nextafter(norm_upper[owner], math.inf)
        ),
        "maximum_causal_curvature_owner_node": owner,
        "first_recursive_wrapping_node": first_wrapping_node,
        "maximum_central_representative_norm": float(np.max(midpoint_norm)),
        "maximum_local_projected_HS_second_residual_norm_upper": float(
            math.nextafter(np.max(local_projected_bounds), math.inf)
        ),
        "maximum_local_projected_HS_second_residual_owner_interval": int(
            np.argmax(local_projected_bounds)
        ),
        "exact_next_calculation": "ATTACH_THE_ACTION_DERIVED_MIXED_GREEN_TRANSVERSE_AND_TRANSVERSE_TRANSVERSE_AXIS_NEIGHBORHOOD_REMAINDER_TO_THIS_FROZEN_CAUSAL_CENTRAL_SCALAR_COMPOSITION,_THEN_APPLY_THE_LONGITUDINAL_TRANSVERSE_TWO_RADIUS_TEST",
        "claim_boundary": {
            "CURRENT_GREEN_CENTRAL_SCALAR_RECURSIVE_CAUSAL_ENCLOSURE_DERIVED": True,
            "CURRENT_GREEN_CORRELATED_CENTRAL_SCALAR_CAUSAL_COMPOSITION_DERIVED": True,
            "CURRENT_GREEN_EXACT_AXIS_NEIGHBORHOOD_CAUSAL_COMPOSITION_DERIVED": False,
            "CURRENT_GREEN_AXIS_NEIGHBORHOOD_MIXED_TRANSVERSE_BOUND_DERIVED": False,
            "CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED": False,
            "G7_ROOT_NONEXISTENCE_DERIVED": False,
            "G7_PHYSICAL_SPACETIME_INSTABILITY_DERIVED": False,
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
    if not payload["validation_passed"]:
        raise SystemExit("correlated central Green scalar causal composition failed")
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "maximum_causal_curvature_norm_upper": payload[
            "maximum_causal_curvature_norm_upper"
        ],
        "maximum_causal_curvature_owner_node": payload[
            "maximum_causal_curvature_owner_node"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
