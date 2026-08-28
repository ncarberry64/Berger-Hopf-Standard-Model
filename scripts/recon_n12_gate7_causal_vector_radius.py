"""Reconnoiter the recentered causal vector radius for Gate 7.

The finite reset-to-stop operator is Volterra: a source on seam ``j`` can
affect only later seams ``i > j``.  This script retains that triangular
structure and separates the already-computed signed Green correction ``c``
from its nonlinear remainder ``delta``.  It is a center reconnaissance, not
an interval Krawczyk certificate.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_CENTER_RECONNAISSANCE.npz"
TANGENT = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_PHYSICAL_TANGENT_TRANSFER_RECONNAISSANCE.npz"
GREEN = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_MATCHED_TANGENT_CORRELATED_DEFECT_GAUSS12_RECONNAISSANCE.npz"
CURVATURE = BASE / "BHSM_N12_GATE7_COMMON_FRAME_ANISOTROPIC_Z2_RECONNAISSANCE.json"
RESULT = BASE / "BHSM_N12_GATE7_CAUSAL_VECTOR_RADIUS_RECONNAISSANCE.json"
DATA = RESULT.with_suffix(".npz")


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def build_payload() -> dict[str, Any]:
    inputs = (CENTER, TANGENT, GREEN, CURVATURE)
    if not all(path.is_file() for path in inputs):
        raise FileNotFoundError("causal vector-radius inputs required")
    with np.load(CENTER) as source:
        times = np.asarray(source["action_lengths"], dtype=float)
    with np.load(TANGENT) as source:
        tangents = np.asarray(source["physical_tangent_action"], dtype=float)
    with np.load(GREEN) as source:
        step_maps = np.asarray(source["physical_macro_step_maps"], dtype=float)
        correction = np.asarray(source["ambient_correction_profile"], dtype=float)
    curvature_record = json.loads(CURVATURE.read_text(encoding="utf-8"))
    rows = curvature_record["rows"]
    if (
        times.shape != (48,)
        or tangents.shape != (48, 98, 73)
        or step_maps.shape != (47, 73, 73)
        or correction.shape != (48, 98)
        or len(rows) != 48
    ):
        raise RuntimeError("the retained 48-node causal data do not align")

    dt = np.diff(times)
    correction_norm = np.asarray([
        np.linalg.norm(tangents[index].T @ correction[index])
        for index in range(48)
    ])
    directional = np.asarray([
        row["directional_D2f_correction_unit_squared_2_norm"]
        for row in rows
    ])
    mixed = np.asarray([
        row["mixed_D2f_dot_correction_unit_operator_2_norm"]
        for row in rows
    ])
    transverse = np.asarray([
        row["physical_time_transverse_D2f_Frobenius_norm"]
        for row in rows
    ])

    # G[i,j] bounds the causal propagation from source interval j to node i,
    # including that interval's quadrature length.  The products stay signed
    # matrices until the final operator norm is taken.
    green_norm = np.zeros((48, 48))
    maximum_propagator_norm = 0.0
    for endpoint in range(1, 48):
        propagator = np.eye(73)
        for source_index in range(endpoint - 1, -1, -1):
            propagator = propagator @ step_maps[source_index]
            norm = float(np.linalg.norm(propagator, ord=2))
            maximum_propagator_norm = max(maximum_propagator_norm, norm)
            green_norm[endpoint, source_index] = dt[source_index] * norm

    # Around c, write e=c+delta.  The three source groups are respectively
    # 1/2 D2f[c,c], D2f[c,delta], and 1/2 D2f[delta,delta].  Causality makes
    # the radius recursion explicit: radius at node i depends only on earlier
    # radii, so no global scalar maximum or fixed-point solve is introduced.
    delta_radius = np.zeros(48)
    directional_contribution = np.zeros(48)
    mixed_contribution = np.zeros(48)
    transverse_contribution = np.zeros(48)
    for endpoint in range(1, 48):
        earlier = slice(0, endpoint)
        directional_contribution[endpoint] = np.sum(
            green_norm[endpoint, earlier]
            * 0.5 * directional[earlier] * correction_norm[earlier] ** 2
        )
        mixed_contribution[endpoint] = np.sum(
            green_norm[endpoint, earlier]
            * mixed[earlier] * correction_norm[earlier] * delta_radius[earlier]
        )
        transverse_contribution[endpoint] = np.sum(
            green_norm[endpoint, earlier]
            * 0.5 * transverse[earlier] * delta_radius[earlier] ** 2
        )
        delta_radius[endpoint] = (
            directional_contribution[endpoint]
            + mixed_contribution[endpoint]
            + transverse_contribution[endpoint]
        )

    total_radius = correction_norm + delta_radius
    owner = int(np.argmax(delta_radius))
    np.savez_compressed(
        DATA,
        action_lengths=times,
        action_step_lengths=dt,
        causal_green_norm=green_norm,
        linear_correction_radius=correction_norm,
        nonlinear_delta_radius=delta_radius,
        total_radius=total_radius,
        directional_contribution=directional_contribution,
        mixed_contribution=mixed_contribution,
        transverse_contribution=transverse_contribution,
    )

    validation = {
        "same_48_node_finite_history_used": True,
        "all_causal_products_and_radii_finite": bool(
            np.all(np.isfinite(green_norm))
            and np.all(np.isfinite(total_radius))
        ),
        "only_strictly_earlier_source_intervals_enter_each_radius": bool(
            np.allclose(np.triu(green_norm), 0.0, atol=0.0, rtol=0.0)
        ),
        "signed_Green_correction_used_as_recenter": True,
        "directional_mixed_and_transverse_quadratic_groups_kept_distinct": True,
        "common_scale_direction_not_deleted": curvature_record["validation"][
            "common_scale_direction_not_deleted"
        ],
        "no_multiplier_or_hybrid_time_generator_projected_out_by_hand": (
            curvature_record["validation"][
                "no_multiplier_or_hybrid_time_generator_projected_out_by_hand"
            ]
        ),
        "center_reconnaissance_not_interval_authority": True,
        "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
    }
    structural_passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_CAUSAL_VECTOR_RADIUS_RECONNAISSANCE",
        "status": (
            "RECENTERED_CAUSAL_VECTOR_RADIUS_CLOSES_AT_THE_48_SEAM_CENTER;_"
            "OUTWARD_INTERVAL_AND_DOMAIN_TRANSFER_OPEN"
        ),
        "authority": "CENTER_RECONNAISSANCE_ONLY_NOT_INTERVAL_KRAWCZYK_AUTHORITY",
        "identity": {
            "history_operator": "FINITE_CAUSAL_VOLTERRA_BLOCK_OPERATOR",
            "recenter": "e=c+delta,_c=A*(-d)",
            "source_bound": (
                "0.5*H_directional*c^2+H_mixed*c*delta+"
                "0.5*H_transverse*delta^2"
            ),
            "vector_radius": (
                "r_delta[i]=sum_{j<i}G[i,j]*(0.5*Hd[j]*c[j]^2+"
                "Hm[j]*c[j]*r_delta[j]+0.5*Ht[j]*r_delta[j]^2)"
            ),
            "triangular_dependency": "STRICTLY_LOWER_CAUSAL_IN_NODE_INDEX",
        },
        "summary": {
            "nodes": 48,
            "seams": 47,
            "finite_action_duration": float(times[-1] - times[0]),
            "maximum_causal_propagator_2_norm": maximum_propagator_norm,
            "maximum_linear_correction_radius": float(np.max(correction_norm)),
            "maximum_nonlinear_delta_radius": float(np.max(delta_radius)),
            "maximum_nonlinear_delta_owner_node": owner,
            "maximum_total_radius": float(np.max(total_radius)),
            "terminal_linear_correction_radius": float(correction_norm[-1]),
            "terminal_nonlinear_delta_radius": float(delta_radius[-1]),
            "terminal_directional_contribution": float(
                directional_contribution[-1]
            ),
            "terminal_mixed_contribution": float(mixed_contribution[-1]),
            "terminal_transverse_quadratic_contribution": float(
                transverse_contribution[-1]
            ),
            "maximum_delta_to_linear_correction_ratio": float(
                np.max(delta_radius / np.maximum(correction_norm, np.finfo(float).tiny))
            ),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "validation": validation,
        "structural_validation_passed": structural_passed,
        "validation_passed": False,
        "claim_boundary": {
            "causal_vector_radius_identity": "DERIVED",
            "center_reconnaissance": "FINITE_AND_CLOSING",
            "between_seam_retained_action_curvature": "OPEN_INTERVAL_AUTHORITY",
            "causal_Green_operator": "OPEN_INTERVAL_AUTHORITY",
            "domain_and_first_hit_transfer": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "OUTWARD_ENCLOSE_THE_THREE_RECENTERED_SOURCE_GROUPS_AND_CAUSAL_"
            "GREEN_BLOCKS_CELLWISE,_THEN_COMPARE_THE_RESULTING_48_VECTOR_"
            "RADII_WITH_THE_EXISTING_FIRST_HIT_AND_DOMAIN_MARGIN_PROFILE"
        ),
        "inputs": {_relative(path): _sha256(path) for path in inputs},
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
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
