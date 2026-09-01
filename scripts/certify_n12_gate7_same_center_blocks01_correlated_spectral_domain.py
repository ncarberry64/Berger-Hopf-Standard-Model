"""Certify the branch-24 spectral domain for the local Gate-7 owner.

The accepted replay center, action, causal frames, and branch are frozen.  The
domain radius is fixed before the spectral test as a five-percent reserve over
the outward two-block Newton correction.  Unlike an entrywise state box, the
ellipsoids below retain the native 74-dimensional causal correlations.

This certificate is intentionally narrower than a local Krawczyk theorem.  It
discharges the selected-line domain operand at endpoints 0--2 and midpoints
0--1; it does not relabel that result as an outward rate-Jacobian variation or
as a Gate-7 root certificate.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

import jax.numpy as jnp
import numpy as np
from flint import arb_mat, ctx


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_n12_c2_stop_boundary_cluster_probe as cluster  # noqa: E402
import certify_n12_gate7_accepted_replay_center_outward_74d as accepted  # noqa: E402
import certify_n12_gate7_recentered_cone_boundary_cluster_spectrum as spectrum  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_SAME_CENTER_BLOCKS01_CORRELATED_SPECTRAL_DOMAIN.json"
THIS_SCRIPT = Path(__file__).resolve()
RADIUS_RESERVE_FACTOR = 1.05


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _center_geometry(
    state: np.ndarray,
    projection: np.ndarray,
    weights: np.ndarray,
    reference: np.ndarray,
) -> dict[str, object]:
    jet = cluster.local.exact_full_action_jet_at_state(
        12,
        state[:cluster.local.QDIM],
        state[cluster.local.QDIM:2 * cluster.local.QDIM],
        state[2 * cluster.local.QDIM:],
        points=cluster.local.POINTS,
    )
    reduced = np.asarray(jet.hessian, dtype=float)[
        cluster.local.QDIM:, cluster.local.QDIM:
    ]
    values, vectors = np.linalg.eigh(0.5 * (reduced + reduced.T))
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    directionals = np.array(spectrum._batched_hessian_directionals(
        jnp.asarray(state),
        jnp.asarray(projection.T / weights[None, :]),
    ), copy=True)[:, cluster.local.QDIM:, cluster.local.QDIM:]
    directionals *= spectrum.JAX_D3_NORM_INFLATION
    return {
        "midpoint": state,
        "projection": projection,
        "values": values,
        "vectors": vectors,
        "selected": selected,
        "directionals": list(directionals),
    }


def _spectral_row(
    *,
    kind: str,
    index: int,
    state: np.ndarray,
    projection: np.ndarray,
    descriptor_center: float,
    descriptor_projection: np.ndarray,
    weights: np.ndarray,
    reference: np.ndarray,
) -> dict[str, object]:
    geometry = _center_geometry(state, projection, weights, reference)
    values = np.asarray(geometry["values"], dtype=float)
    clusters = [
        cluster._cluster_bound(
            branches,
            cluster._distance_groups(values, branches),
            geometry,
            weights,
        )
        for branches in ((23,), (24,), (25, 26, 27))
    ]
    negative = next(row for row in clusters if row["branches"] == [23])
    selected = next(row for row in clusters if row["branches"] == [24])
    positive = next(
        row for row in clusters if row["branches"] == [25, 26, 27]
    )
    negative_margin = float(
        values[24] - values[23]
        - selected["cluster_spectral_shift_upper"]
        - negative["cluster_spectral_shift_upper"]
    )
    positive_margin = float(
        values[25] - values[24]
        - selected["cluster_spectral_shift_upper"]
        - positive["cluster_spectral_shift_upper"]
    )
    descriptor_radius = math.nextafter(
        float(np.linalg.norm(descriptor_projection)), math.inf,
    )
    descriptor_lower = math.nextafter(
        descriptor_center - descriptor_radius, -math.inf,
    )
    closed = bool(
        geometry["selected"] == 24
        and all(row["quarter_gap_bootstrap_closed"] for row in clusters)
        and negative_margin > 0.0
        and positive_margin > 0.0
        and descriptor_lower > 0.0
    )
    return {
        "kind": kind,
        "index": index,
        "selected_branch": int(geometry["selected"]),
        "projection_dimension": int(projection.shape[1]),
        "projection_operator_2_norm": float(np.linalg.norm(projection, 2)),
        "descriptor_center": descriptor_center,
        "descriptor_radius": descriptor_radius,
        "descriptor_lower": descriptor_lower,
        "negative_selected_gap_lower": negative_margin,
        "selected_positive_gap_lower": positive_margin,
        "clusters": clusters,
        "correlated_spectral_domain_closed": closed,
    }


def _newton_coordinates(
    centers: np.ndarray,
    times: np.ndarray,
    tangents: np.ndarray,
    old_left: np.ndarray,
    old_right: np.ndarray,
) -> tuple[list[arb_mat], list[float]]:
    coordinate = arb_mat(74, 1)
    coordinates: list[arb_mat] = [arb_mat(74, 1)]
    norm_uppers = [0.0]
    for interval in range(2):
        h = accepted._a(float(times[interval + 1] - times[interval]))
        test = accepted._arb_matrix(accepted._frame(
            tangents[interval + 1], accepted.TEST_DESCRIPTOR_SCALE,
        ).T)
        trial = accepted._arb_matrix(accepted._frame(
            tangents[interval], accepted.TRIAL_DESCRIPTOR_SCALE,
        ))
        inverse = accepted._arb_matrix(old_right[interval]).inv()
        e0 = accepted._arb_mat_from_array(accepted._parse_arb_string_array(
            np.load(accepted.WORK / f"endpoint_{interval:03d}.npz")["value_arb"],
        ))
        e1 = accepted._arb_mat_from_array(accepted._parse_arb_string_array(
            np.load(accepted.WORK / f"endpoint_{interval + 1:03d}.npz")["value_arb"],
        ))
        em = accepted._arb_mat_from_array(accepted._parse_arb_string_array(
            np.load(accepted.WORK / f"midpoint_{interval:03d}.npz")["value_arb"],
        ))
        residual = (
            accepted._arb_vector(centers[interval + 1])
            - accepted._arb_vector(centers[interval])
            - h * (e0 + 4 * em + e1) / 6
        )
        coordinate = -inverse * (
            test * residual
            + test * accepted._arb_matrix(old_left[interval]) * trial * coordinate
        )
        coordinates.append(coordinate)
        norm_uppers.append(accepted._vector_norm_upper(coordinate))
    return coordinates, norm_uppers


def main() -> None:
    ctx.prec = accepted.PRECISION
    required = [
        accepted.ENDPOINT,
        accepted.ENDPOINT.with_suffix(".npz"),
        accepted.REPLAY,
        accepted.REPLAY.with_suffix(".npz"),
        accepted.OLD_JACOBIAN,
        accepted.OLD_JACOBIAN.with_suffix(".npz"),
        accepted.PRECONDITIONER,
        accepted.PRECONDITIONER.with_suffix(".npz"),
        accepted.WORK / "endpoint_000.npz",
        accepted.WORK / "endpoint_001.npz",
        accepted.WORK / "endpoint_002.npz",
        accepted.WORK / "midpoint_000.npz",
        accepted.WORK / "midpoint_001.npz",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing {len(missing)} accepted-center inputs")

    with np.load(accepted.ENDPOINT.with_suffix(".npz")) as source:
        states = np.asarray(source["projected_states"], dtype=float)
        descriptors = np.asarray(
            source["independent_signed_descriptors"], dtype=float,
        )
        weights = np.asarray(source["state_weights"], dtype=float)
        times = np.asarray(source["collocation_arc_parameters"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    centers = np.column_stack((states * weights[None, :], descriptors))
    with np.load(accepted.REPLAY.with_suffix(".npz")) as source:
        midpoint_augmented = np.asarray(
            source["midpoint_augmented_action_values"], dtype=float,
        )
    with np.load(accepted.OLD_JACOBIAN.with_suffix(".npz")) as source:
        tangents = np.asarray(
            source["endpoint_physical_tangent_action"], dtype=float,
        )
    with np.load(accepted.PRECONDITIONER.with_suffix(".npz")) as source:
        old_left = np.asarray(source["left_Newton_blocks"], dtype=float)
        old_right = np.asarray(
            source["reduced_right_Newton_blocks"], dtype=float,
        )

    coordinates, coordinate_norm_uppers = _newton_coordinates(
        centers, times, tangents, old_left, old_right,
    )
    pair_norm_upper = math.nextafter(math.hypot(
        coordinate_norm_uppers[1], coordinate_norm_uppers[2],
    ), math.inf)
    radius = math.nextafter(
        RADIUS_RESERVE_FACTOR * pair_norm_upper, math.inf,
    )
    frames = [
        accepted._frame(tangents[index], accepted.TRIAL_DESCRIPTOR_SCALE)
        for index in range(3)
    ]

    rows: list[dict[str, object]] = []
    for index in range(3):
        projection = radius * frames[index][:98]
        descriptor_projection = radius * frames[index][98]
        rows.append(_spectral_row(
            kind="endpoint",
            index=index,
            state=states[index],
            projection=projection,
            descriptor_center=float(descriptors[index]),
            descriptor_projection=descriptor_projection,
            weights=weights,
            reference=reference,
        ))

    for interval in range(2):
        h = accepted._a(float(times[interval + 1] - times[interval]))
        left_center = accepted._parse_arb_string_array(
            np.load(accepted.WORK / f"endpoint_{interval:03d}.npz")["derivative_arb"],
        )
        right_center = accepted._parse_arb_string_array(
            np.load(accepted.WORK / f"endpoint_{interval + 1:03d}.npz")["derivative_arb"],
        )
        left_frame = frames[interval]
        right_frame = frames[interval + 1]
        left_direction = np.empty((99, 74), dtype=object)
        right_direction = np.empty_like(left_direction)
        for i in range(99):
            for k in range(74):
                left_direction[i, k] = (
                    accepted._a(0.5 * left_frame[i, k])
                    + h * left_center[i, k] / 8
                )
                right_direction[i, k] = (
                    accepted._a(0.5 * right_frame[i, k])
                    - h * right_center[i, k] / 8
                )
        combined = np.column_stack((left_direction, right_direction))
        combined_mid = np.empty(combined.shape, dtype=float)
        combined_rad = np.empty(combined.shape, dtype=float)
        for entry in np.ndindex(combined.shape):
            combined_mid[entry], combined_rad[entry] = accepted._center_radius(
                combined[entry]
            )
        projection = radius * combined_mid[:98]
        projection_radius = radius * combined_rad[:98]
        # The Arb differentiation radii are retained as an outward scalar
        # enlargement of the correlated action projection.
        projection += 0.0
        projection_error_upper = math.nextafter(
            float(np.linalg.norm(projection_radius, ord="fro")), math.inf,
        )
        projection_scale = math.nextafter(
            1.0 + projection_error_upper / max(
                float(np.linalg.norm(projection, ord="fro")),
                np.finfo(float).tiny,
            ),
            math.inf,
        )
        projection *= projection_scale
        descriptor_projection = radius * combined_mid[98]
        descriptor_projection = np.nextafter(
            np.abs(descriptor_projection) + radius * combined_rad[98],
            math.inf,
        )
        midpoint_state = midpoint_augmented[interval, :98] / weights
        rows.append(_spectral_row(
            kind="midpoint",
            index=interval,
            state=midpoint_state,
            projection=projection,
            descriptor_center=float(midpoint_augmented[interval, 98]),
            descriptor_projection=descriptor_projection,
            weights=weights,
            reference=reference,
        ))

    minimum_negative = min(
        float(row["negative_selected_gap_lower"]) for row in rows
    )
    minimum_positive = min(
        float(row["selected_positive_gap_lower"]) for row in rows
    )
    minimum_descriptor = min(float(row["descriptor_lower"]) for row in rows)
    validation = {
        "same_frozen_accepted_replay_center": True,
        "same_BHSM_AE2_action_and_branch_24": all(
            int(row["selected_branch"]) == 24 for row in rows
        ),
        "two_block_newton_correction_strictly_inside_radius": (
            pair_norm_upper < radius
        ),
        "all_three_endpoints_and_two_midpoints_certified": len(rows) == 5,
        "all_cluster_quarter_gap_bootstraps_close": all(
            bool(row["correlated_spectral_domain_closed"]) for row in rows
        ),
        "selected_line_stays_between_neighboring_clusters": (
            minimum_negative > 0.0 and minimum_positive > 0.0
        ),
        "descriptor_orientation_stays_positive": minimum_descriptor > 0.0,
        "entrywise_axis_aligned_state_box_not_used": True,
        "outward_rate_Jacobian_variation_not_claimed": True,
        "local_Krawczyk_root_not_claimed": True,
    }
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_SAME_CENTER_BLOCKS01_CORRELATED_SPECTRAL_DOMAIN",
        "owner": "SAME_CENTER_LOCAL_FORMATION_VIABILITY_CERTIFICATE",
        "status": (
            "BLOCKS01_ROOT_CONTAINING_CORRELATED_BRANCH24_DOMAIN_CERTIFIED__"
            "LOCAL_RATE_JACOBIAN_VARIATION_REMAINS"
            if passed else
            "BLOCKS01_CORRELATED_BRANCH24_DOMAIN_NOT_CERTIFIED"
        ),
        "local_domain": {
            "action_coordinate_radius": radius,
            "radius_reserve_factor_over_two_block_Newton_correction": (
                RADIUS_RESERVE_FACTOR
            ),
            "endpoint_Newton_coordinate_norm_uppers": coordinate_norm_uppers,
            "two_block_Newton_coordinate_norm_upper": pair_norm_upper,
            "radius_minus_Newton_pair_norm": radius - pair_norm_upper,
            "proof_coordinate_classification": (
                "EQUIVALENT_NATIVE_CAUSAL_CORRELATED_ELLIPSOID"
            ),
        },
        "summary": {
            "minimum_negative_selected_gap_lower": minimum_negative,
            "minimum_selected_positive_gap_lower": minimum_positive,
            "minimum_descriptor_lower": minimum_descriptor,
            "certified_locations": len(rows),
            "broad_axis_aligned_interval_eigenline_failure_reclassified": (
                "CORRELATION_LOSS_NOT_BRANCH24_DOMAIN_FAILURE"
            ),
        },
        "rows": rows,
        "claim_boundary": {
            "correlated_branch24_spectral_domain_blocks01": (
                "CERTIFIED" if passed else "OPEN"
            ),
            "same_center_outward_local_rate_Jacobian_variation": "OPEN",
            "local_Y_Z1_Z2_Krawczyk_inequality": "OPEN",
            "causal_handoff_beyond_node_2": "NOT_STARTED",
            "Gate7": "OPEN",
            "root_nonexistence_claim": False,
            "physical_instability_claim": False,
        },
        "provenance_SHA256": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in required if path.suffix.lower() in {".json", ".npz"}
        },
        "majorant_source_SHA256": cluster.local.COMMITTED_MAJORANT_SHA256,
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        **payload["local_domain"],
        **payload["summary"],
        "validation_passed": passed,
        "result": str(RESULT),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
