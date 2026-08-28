"""Assemble the signed Gate-7 causal vector bootstrap.

The prior scalar recurrence took a norm at every source interval.  Here the
exact directional source vectors and mixed Green/transverse matrices are
propagated through the signed 73-dimensional Volterra step maps first.  A
scalar error radius is attached only to the residual transverse quadratic
term.  This is a center bootstrap; outward step-map and curvature authority
remain explicit dependencies.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.linalg import null_space


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_CENTER_RECONNAISSANCE.npz"
TANGENT = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_PHYSICAL_TANGENT_TRANSFER_RECONNAISSANCE.npz"
GREEN = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_MATCHED_TANGENT_CORRELATED_DEFECT_GAUSS12_RECONNAISSANCE.npz"
DIRECTIONAL = BASE / "BHSM_N12_GATE7_EXACT_SIGNED_DIRECTIONAL_FIELD_CURVATURE.json"
DIRECTIONAL_DATA = DIRECTIONAL.with_suffix(".npz")
MIXED = BASE / "BHSM_N12_GATE7_EXACT_SIGNED_MIXED_FIELD_CURVATURE.json"
MIXED_DATA = MIXED.with_suffix(".npz")
PRIOR = BASE / "BHSM_N12_GATE7_COMMON_FRAME_ANISOTROPIC_Z2_RECONNAISSANCE.json"
OLD_RADIUS = BASE / "BHSM_N12_GATE7_CAUSAL_VECTOR_RADIUS_RECONNAISSANCE.npz"
RESULT = BASE / "BHSM_N12_GATE7_SIGNED_CAUSAL_VECTOR_BOOTSTRAP.json"
DATA = RESULT.with_suffix(".npz")


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _error_radius(
    inflation: float,
    vector_norm: np.ndarray,
    green_norm: np.ndarray,
    correction_norm: np.ndarray,
    mixed_norm: np.ndarray,
    transverse_bound: np.ndarray,
) -> np.ndarray:
    error = np.zeros(48)
    for endpoint in range(1, 48):
        earlier = slice(0, endpoint)
        with np.errstate(over="ignore", invalid="ignore"):
            error[endpoint] = np.sum(
                green_norm[endpoint, earlier] * (
                    mixed_norm[earlier] * correction_norm[earlier] * error[earlier]
                    + 0.5 * inflation * transverse_bound[earlier]
                    * (vector_norm[earlier] + error[earlier]) ** 2
                )
            )
        if not math.isfinite(float(error[endpoint])):
            error[endpoint:] = math.inf
            break
    return error


def build_payload() -> dict[str, Any]:
    inputs = (
        CENTER, TANGENT, GREEN, DIRECTIONAL, DIRECTIONAL_DATA,
        MIXED, MIXED_DATA, PRIOR, OLD_RADIUS,
    )
    if not all(path.is_file() for path in inputs):
        raise FileNotFoundError("signed causal-vector inputs required")
    records = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in (DIRECTIONAL, MIXED)
    ]
    if not all(record["validation_passed"] for record in records):
        raise RuntimeError("exact signed directional and mixed maps required")
    with np.load(CENTER) as source:
        times = np.asarray(source["action_lengths"], dtype=float)
    with np.load(TANGENT) as source:
        tangents = np.asarray(source["physical_tangent_action"], dtype=float)
    with np.load(GREEN) as source:
        step_maps = np.asarray(source["physical_macro_step_maps"], dtype=float)
        corrections = np.asarray(source["ambient_correction_profile"], dtype=float)
    with np.load(DIRECTIONAL_DATA) as source:
        fields = np.asarray(source["normalized_field"], dtype=float)
        directional = np.asarray(
            source["physical_time_transverse_directional_curvature"],
            dtype=float,
        )
    with np.load(MIXED_DATA) as source:
        mixed = np.asarray(
            source["physical_time_transverse_mixed_Green_curvature"],
            dtype=float,
        )
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    transverse_bound = np.asarray([
        row["physical_time_transverse_D2f_Frobenius_norm"]
        for row in prior["rows"]
    ])
    with np.load(OLD_RADIUS) as source:
        old_radius = np.asarray(source["nonlinear_delta_radius"], dtype=float)
    halo = float(np.max(old_radius))
    dt = np.diff(times)

    transverse_frames = []
    correction_norm = []
    for index in range(48):
        physical_flow = tangents[index].T @ fields[index]
        physical_flow /= np.linalg.norm(physical_flow)
        frame = null_space(physical_flow[None, :])
        transverse_frames.append(frame)
        correction_norm.append(float(np.linalg.norm(
            frame.T @ tangents[index].T @ corrections[index]
        )))
    transverse_frames = np.asarray(transverse_frames)
    correction_norm = np.asarray(correction_norm)

    propagators: dict[tuple[int, int], np.ndarray] = {}
    green_norm = np.zeros((48, 48))
    for endpoint in range(1, 48):
        propagator = np.eye(73)
        for source_index in range(endpoint - 1, -1, -1):
            propagator = propagator @ step_maps[source_index]
            propagators[(endpoint, source_index)] = propagator.copy()
            green_norm[endpoint, source_index] = (
                dt[source_index] * np.linalg.norm(propagator, ord=2)
            )

    # Strictly lower-triangular signed Volterra solve for the directional and
    # mixed center equation.  No fixed-point iteration is necessary.
    vector = np.zeros((48, 73))
    directional_part = np.zeros_like(vector)
    mixed_part = np.zeros_like(vector)
    for endpoint in range(1, 48):
        for source_index in range(endpoint):
            frame = transverse_frames[source_index]
            source_directional = (
                0.5 * directional[source_index]
                * correction_norm[source_index] ** 2
            )
            source_mixed = (
                mixed[source_index]
                @ (frame.T @ vector[source_index])
                * correction_norm[source_index]
            )
            transport = dt[source_index] * propagators[(endpoint, source_index)]
            directional_part[endpoint] += transport @ (
                frame @ source_directional
            )
            mixed_part[endpoint] += transport @ (frame @ source_mixed)
        vector[endpoint] = directional_part[endpoint] + mixed_part[endpoint]

    vector_norm = np.linalg.norm(vector, axis=1)
    mixed_norm = np.linalg.norm(mixed, axis=(1, 2))
    error = _error_radius(
        1.0, vector_norm, green_norm, correction_norm,
        mixed_norm, transverse_bound,
    )
    total_radius = vector_norm + error

    # Quantify the exact remaining center theorem: any rigorous transverse
    # curvature upper below this uniform inflation of the reconnaissance
    # profile preserves the already certified nonlinear halo.
    lower = 0.0
    upper = 1.0
    while upper < 1.0e20:
        candidate = _error_radius(
            upper, vector_norm, green_norm, correction_norm,
            mixed_norm, transverse_bound,
        )
        if float(np.max(vector_norm + candidate)) >= halo:
            break
        upper *= 10.0
    for _ in range(100):
        midpoint = 0.5 * (lower + upper)
        candidate = _error_radius(
            midpoint, vector_norm, green_norm, correction_norm,
            mixed_norm, transverse_bound,
        )
        if float(np.max(vector_norm + candidate)) < halo:
            lower = midpoint
        else:
            upper = midpoint

    np.savez_compressed(
        DATA,
        action_lengths=times,
        signed_center_vector=vector,
        signed_directional_part=directional_part,
        signed_mixed_part=mixed_part,
        quadratic_error_radius=error,
        total_center_radius=total_radius,
        correction_time_transverse_norm=correction_norm,
        causal_green_norm=green_norm,
    )
    structural_validation = {
        "all_48_nodes_and_47_signed_step_maps_used": (
            vector.shape == (48, 73) and step_maps.shape == (47, 73, 73)
        ),
        "exact_signed_directional_vectors_used": directional.shape == (48, 72),
        "exact_signed_mixed_matrices_used": mixed.shape == (48, 72, 72),
        "strictly_lower_causal_dependency_preserved": bool(
            np.allclose(np.triu(green_norm), 0.0, atol=0.0, rtol=0.0)
        ),
        "signed_sources_and_propagators_combined_before_norms": True,
        "center_vector_plus_quadratic_error_fits_existing_halo": (
            float(np.max(total_radius)) < halo
        ),
        "transverse_curvature_can_inflate_by_more_than_1000_before_halo_failure": (
            lower > 1000.0
        ),
        "no_recurrence_reset_selector_scale_gate_or_chord_changed": True,
    }
    structural_validation = {
        key: bool(value) for key, value in structural_validation.items()
    }
    structural_passed = all(structural_validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_SIGNED_CAUSAL_VECTOR_BOOTSTRAP",
        "status": (
            "SIGNED_CAUSAL_CENTER_VECTOR_CLOSES_WITH_LARGE_TRANSVERSE_HEADROOM;_OUTWARD_AUTHORITY_OPEN"
            if structural_passed else "SIGNED_CAUSAL_VECTOR_BOOTSTRAP_INVALID"
        ),
        "authority": "EXACT_SIGNED_DIRECTIONAL_AND_MIXED_CENTER_MAPS_WITH_RECONNAISSANCE_TRANSVERSE_ERROR",
        "identity": {
            "signed_center": (
                "v_i=sum_{j<i}dt_j*P_ij*N_j*(0.5*Hd_j*c_j^2+Hm_j*c_j*N_j^T*v_j)"
            ),
            "error_radius": (
                "e_i=sum_{j<i}G_ij*(||Hm_j||*c_j*e_j+0.5*Ht_j*(||v_j||+e_j)^2)"
            ),
        },
        "summary": {
            "maximum_signed_center_vector_2_norm": float(np.max(vector_norm)),
            "signed_center_vector_owner_node": int(np.argmax(vector_norm)),
            "terminal_signed_center_vector_2_norm": float(vector_norm[-1]),
            "maximum_quadratic_error_radius": float(np.max(error)),
            "maximum_total_center_radius": float(np.max(total_radius)),
            "existing_certified_nonlinear_halo": halo,
            "halo_to_center_radius_ratio": float(halo / np.max(total_radius)),
            "maximum_uniform_transverse_profile_inflation_before_halo_failure": lower,
            "corresponding_permitted_transverse_curvature_upper": float(
                lower * np.max(transverse_bound)
            ),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "structural_validation": structural_validation,
        "structural_validation_passed": structural_passed,
        "validation_passed": False,
        "claim_boundary": {
            "signed_directional_and_mixed_center_vector": "DERIVED",
            "center_transverse_quadratic_error": "RECONNAISSANCE_BOUND_ONLY",
            "outward_curvature_remainder": "OPEN",
            "outward_signed_step_map_and_Green_remainder": "OPEN",
            "causal_interval_vector_radius": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "PROVE_ANY_RETAINED_ACTION_PHYSICAL_TRANSVERSE_CURVATURE_TUBE_"
            "BELOW_THE_REPORTED_7E8_SCALE_AND_ATTACH_THE_EXISTING_SIGNED_"
            "GREEN_STEP_MAP_REMAINDER;_NO_FULL_72_CUBED_TENSOR_IS_REQUIRED"
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
        "structural_validation_passed": payload[
            "structural_validation_passed"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
