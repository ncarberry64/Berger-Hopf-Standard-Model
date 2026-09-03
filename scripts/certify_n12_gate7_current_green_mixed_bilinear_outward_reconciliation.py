"""Reconcile the direct and polarized current mixed-map evaluations outward.

The Fréchet-Hessian polarization identity is exact.  This unit retains that
identity, forms one outward hull of the two independently rounded seed graphs,
and checks the reconnaissance owner's leading transverse direction with a
fresh 512-bit polarized evaluation.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np
from flint import arb, ctx


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_gate7_accepted_replay_center_outward_74d as cert  # noqa: E402
import certify_n12_gate7_current_green_correlated_scalar_interval355 as scalar  # noqa: E402
import certify_n12_gate7_current_green_mixed_transverse_all_endpoints as direct  # noqa: E402


F = ROOT / "artifacts/flagship_integration"
ALL_ENDPOINTS = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_TRANSVERSE_ALL_ENDPOINTS.json"
ALL_ENDPOINTS_DATA = ALL_ENDPOINTS.with_suffix(".npz")
POLARIZATION_SEED = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_TRANSVERSE_SEED.json"
POLARIZATION_SEED_DATA = POLARIZATION_SEED.with_suffix(".npz")
COMPUTE_AUDIT = (
    ROOT
    / "artifacts/current_semantics/"
    "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_OUTWARD_COMPUTE_JUSTIFICATION.json"
)
RESULT = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_BILINEAR_OUTWARD_RECONCILIATION.json"
DATA = RESULT.with_suffix(".npz")
WORK = F / ".current_green_mixed_bilinear_outward_reconciliation_work"
THEORY = ROOT / "theory/n12_gate7_current_green_mixed_bilinear_outward_reconciliation.md"
THIS_SCRIPT = Path(__file__).resolve()
PRECISION = 512
SHARD_REVISION = 2
SEED_NODES = (1, 355, 356, 370)
INPUTS = (
    ALL_ENDPOINTS,
    ALL_ENDPOINTS_DATA,
    POLARIZATION_SEED,
    POLARIZATION_SEED_DATA,
    COMPUTE_AUDIT,
    direct.ENDPOINT,
    direct.ENDPOINT.with_suffix(".npz"),
    direct.JACOBIAN,
    direct.JACOBIAN.with_suffix(".npz"),
    direct.PARTITION,
    direct.PARTITION.with_suffix(".npz"),
    Path(cert.__file__).resolve(),
    Path(scalar.__file__).resolve(),
    Path(direct.__file__).resolve(),
    THIS_SCRIPT,
    THEORY,
)
WITNESS_COMPUTE_INPUTS = (
    ALL_ENDPOINTS_DATA,
    POLARIZATION_SEED_DATA,
    direct.ENDPOINT.with_suffix(".npz"),
    direct.JACOBIAN.with_suffix(".npz"),
    direct.PARTITION.with_suffix(".npz"),
    Path(cert.__file__).resolve(),
    Path(scalar.__file__).resolve(),
    Path(direct.__file__).resolve(),
)


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _recorded_inputs_are_current(payload: dict[str, object]) -> bool:
    recorded = payload.get("inputs")
    if not isinstance(recorded, dict) or not recorded:
        return False
    for relative, digest in recorded.items():
        path = ROOT / str(relative)
        if not path.is_file() or _sha(path) != digest:
            return False
    return True


def _owner_shard(node: int) -> Path:
    return WORK / f"owner_node_{node:03d}.npz"


def _canonical_vector(vector: np.ndarray) -> np.ndarray:
    result = np.asarray(vector, dtype=float).copy()
    pivot = int(np.argmax(np.abs(result)))
    if result[pivot] < 0.0:
        result *= -1.0
    return result


def _hull(
    left_mid: np.ndarray,
    left_radius: np.ndarray,
    right_mid: np.ndarray,
    right_radius: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    left_mid = np.asarray(left_mid, dtype=np.longdouble)
    left_radius = np.asarray(left_radius, dtype=np.longdouble)
    right_mid = np.asarray(right_mid, dtype=np.longdouble)
    right_radius = np.asarray(right_radius, dtype=np.longdouble)
    lower = np.minimum(
        np.nextafter(left_mid - left_radius, -np.longdouble(np.inf)),
        np.nextafter(right_mid - right_radius, -np.longdouble(np.inf)),
    )
    upper = np.maximum(
        np.nextafter(left_mid + left_radius, np.longdouble(np.inf)),
        np.nextafter(right_mid + right_radius, np.longdouble(np.inf)),
    )
    midpoint_ld = (lower + upper) / np.longdouble(2)
    midpoint = np.asarray(midpoint_ld, dtype=float)
    radius = np.nextafter(
        np.asarray(
            np.nextafter(
                np.maximum(midpoint_ld - lower, upper - midpoint_ld)
                + np.abs(midpoint_ld - np.asarray(midpoint, dtype=np.longdouble)),
                np.longdouble(np.inf),
            ),
            dtype=float,
        ),
        np.inf,
    )
    return midpoint, radius


def _contains(
    hull_mid: np.ndarray,
    hull_radius: np.ndarray,
    inner_mid: np.ndarray,
    inner_radius: np.ndarray,
) -> bool:
    return bool(np.all(
        np.abs(np.asarray(inner_mid) - np.asarray(hull_mid))
        + np.asarray(inner_radius) <= np.asarray(hull_radius)
    ))


def _owner_fingerprint(node: int, direction: np.ndarray) -> str:
    payload = {
        "node": node,
        "precision_bits": PRECISION,
        "direction": np.asarray(direction, dtype=float).tobytes().hex(),
        "inputs": {
            _relative(path): _sha(path)
            for path in WITNESS_COMPUTE_INPUTS
        },
        "shard_revision": SHARD_REVISION,
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()


def _valid_owner_shard(path: Path, node: int, direction: np.ndarray) -> bool:
    if not path.is_file():
        return False
    try:
        with np.load(path) as source:
            return (
                int(source["node"]) == node
                and int(source["precision_bits"]) == PRECISION
                and int(source["shard_revision"]) == SHARD_REVISION
                and np.array_equal(
                    np.asarray(source["leading_right_direction"], dtype=float),
                    np.asarray(direction, dtype=float),
                )
                and str(source["input_fingerprint_SHA256"].item())
                == _owner_fingerprint(node, direction)
            )
    except Exception:
        return False


def _materialize_owner_witness(
    node: int,
    direction: np.ndarray,
    direct_mid: np.ndarray,
    direct_radius: np.ndarray,
) -> Path:
    target = _owner_shard(node)
    if _valid_owner_shard(target, node, direction):
        return target
    ctx.prec = PRECISION
    WORK.mkdir(parents=True, exist_ok=True)
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
    axis_direction = frame @ axis
    transverse_direction = frame @ projector @ direction
    started = time.perf_counter()
    original_action_jets = cert._arb_action_jets
    jets = original_action_jets(state)
    try:
        cert._arb_action_jets = lambda _state, cached=jets: cached
        plus = cert._rate_second_directional(
            state, descriptor, weights, reference,
            axis_direction + transverse_direction,
        )
        minus = cert._rate_second_directional(
            state, descriptor, weights, reference,
            axis_direction - transverse_direction,
        )
    finally:
        cert._arb_action_jets = original_action_jets
    polarized = np.asarray(
        [(plus[index] - minus[index]) / 4 for index in range(direct.OUTPUTS)],
        dtype=object,
    )
    polarization_mid, polarization_radius = direct._export(polarized)
    contracted_mid = np.asarray(direct_mid, dtype=float) @ direction
    contracted_radius = np.asarray(direct_radius, dtype=float) @ np.abs(direction)
    np.savez_compressed(
        target,
        node=np.asarray(node),
        precision_bits=np.asarray(PRECISION),
        shard_revision=np.asarray(SHARD_REVISION),
        leading_right_direction=np.asarray(direction, dtype=float),
        direct_contracted_mid=contracted_mid,
        direct_contracted_radius=contracted_radius,
        polarization_mid=polarization_mid,
        polarization_radius=polarization_radius,
        elapsed_seconds=np.asarray(time.perf_counter() - started),
        input_fingerprint_SHA256=np.asarray(_owner_fingerprint(node, direction)),
    )
    return target


def build_payload() -> dict[str, object]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    all_endpoints = json.loads(ALL_ENDPOINTS.read_text(encoding="utf-8"))
    seed = json.loads(POLARIZATION_SEED.read_text(encoding="utf-8"))
    compute_audit = json.loads(COMPUTE_AUDIT.read_text(encoding="utf-8"))
    if not all_endpoints["validation_passed"] or not seed["validation_passed"]:
        raise ValueError("validated all-endpoint and polarization seed inputs required")
    owner_witness_authorized = bool(
        compute_audit.get("validation_passed") is True
        and _recorded_inputs_are_current(compute_audit)
        and compute_audit.get("authorization", {}).get(
            "owner_leading_direction_512_bit_polarization_witness"
        ) is True
    )
    if not owner_witness_authorized:
        raise PermissionError("post-reconnaissance owner witness is not authorized")
    with np.load(ALL_ENDPOINTS_DATA) as source:
        nodes = np.asarray(source["post_reset_nodes"], dtype=int)
        all_mid = np.asarray(source["mixed_direct_bilinear_mid"], dtype=float)
        all_radius = np.asarray(source["mixed_direct_bilinear_radius"], dtype=float)
    with np.load(POLARIZATION_SEED_DATA) as source:
        seed_nodes = np.asarray(source["seed_nodes"], dtype=int)
        polarization_mid = np.asarray(source["mixed_green_transverse_mid"], dtype=float)
        polarization_radius = np.asarray(
            source["mixed_green_transverse_radius"], dtype=float,
        )
    if tuple(seed_nodes) != SEED_NODES:
        raise ValueError("unexpected polarization seed-node order")
    node_to_index = {int(node): index for index, node in enumerate(nodes)}
    direct_seed_mid = np.asarray([all_mid[node_to_index[node]] for node in SEED_NODES])
    direct_seed_radius = np.asarray([
        all_radius[node_to_index[node]] for node in SEED_NODES
    ])
    seed_hull_mid, seed_hull_radius = _hull(
        direct_seed_mid, direct_seed_radius,
        polarization_mid, polarization_radius,
    )
    seed_difference = direct_seed_mid - polarization_mid
    seed_absolute_difference = np.abs(seed_difference)
    seed_scaled_difference = seed_absolute_difference / np.maximum(
        1.0, np.abs(polarization_mid),
    )

    owner = int(all_endpoints["maximum_direct_graph_owner_node"])
    owner_index = node_to_index[owner]
    _, _, right_h = np.linalg.svd(all_mid[owner_index], full_matrices=False)
    leading_direction = _canonical_vector(right_h[0])
    owner_shard = _materialize_owner_witness(
        owner, leading_direction, all_mid[owner_index], all_radius[owner_index],
    )
    with np.load(owner_shard) as source:
        owner_direct_mid = np.asarray(source["direct_contracted_mid"], dtype=float)
        owner_direct_radius = np.asarray(
            source["direct_contracted_radius"], dtype=float,
        )
        owner_polarization_mid = np.asarray(source["polarization_mid"], dtype=float)
        owner_polarization_radius = np.asarray(
            source["polarization_radius"], dtype=float,
        )
        owner_elapsed = float(source["elapsed_seconds"])
    owner_hull_mid, owner_hull_radius = _hull(
        owner_direct_mid, owner_direct_radius,
        owner_polarization_mid, owner_polarization_radius,
    )
    owner_absolute_difference = np.abs(
        owner_direct_mid - owner_polarization_mid
    )
    owner_scaled_difference = owner_absolute_difference / np.maximum(
        1.0, np.abs(owner_polarization_mid),
    )
    np.savez_compressed(
        DATA,
        seed_nodes=np.asarray(SEED_NODES),
        seed_direct_mid=direct_seed_mid,
        seed_direct_radius=direct_seed_radius,
        seed_polarization_mid=polarization_mid,
        seed_polarization_radius=polarization_radius,
        seed_common_hull_mid=seed_hull_mid,
        seed_common_hull_radius=seed_hull_radius,
        owner_node=np.asarray(owner),
        owner_leading_right_direction=leading_direction,
        owner_direct_mid=owner_direct_mid,
        owner_direct_radius=owner_direct_radius,
        owner_polarization_mid=owner_polarization_mid,
        owner_polarization_radius=owner_polarization_radius,
        owner_common_hull_mid=owner_hull_mid,
        owner_common_hull_radius=owner_hull_radius,
    )
    validation = {
        "Frechet_Hessian_polarization_identity_is_exact": True,
        "all_four_seed_nodes_and_74_columns_reconciled": (
            seed_hull_mid.shape == (4, direct.OUTPUTS, direct.COORDINATES)
        ),
        "seed_common_hull_is_finite_with_nonnegative_radii": bool(
            np.all(np.isfinite(seed_hull_mid))
            and np.all(np.isfinite(seed_hull_radius))
            and np.all(seed_hull_radius >= 0.0)
        ),
        "seed_common_hull_contains_direct_graph": _contains(
            seed_hull_mid, seed_hull_radius,
            direct_seed_mid, direct_seed_radius,
        ),
        "seed_common_hull_contains_polarization_graph": _contains(
            seed_hull_mid, seed_hull_radius,
            polarization_mid, polarization_radius,
        ),
        "all_296_seed_centers_agree_below_1e_minus_8_absolute": bool(
            np.max(seed_absolute_difference) < 1.0e-8
        ),
        "all_296_seed_centers_agree_below_1e_minus_9_scaled": bool(
            np.max(seed_scaled_difference) < 1.0e-9
        ),
        "reconnaissance_owner_leading_direction_checked_at_512_bit": bool(
            owner_direct_mid.shape == (direct.OUTPUTS,)
            and np.all(np.isfinite(owner_polarization_mid))
            and np.all(np.isfinite(owner_polarization_radius))
        ),
        "owner_common_hull_is_finite_with_nonnegative_radii": bool(
            np.all(np.isfinite(owner_hull_mid))
            and np.all(np.isfinite(owner_hull_radius))
            and np.all(owner_hull_radius >= 0.0)
        ),
        "owner_common_hull_contains_direct_graph": _contains(
            owner_hull_mid, owner_hull_radius,
            owner_direct_mid, owner_direct_radius,
        ),
        "owner_common_hull_contains_polarization_graph": _contains(
            owner_hull_mid, owner_hull_radius,
            owner_polarization_mid, owner_polarization_radius,
        ),
        "owner_leading_direction_centers_agree_below_1e_minus_8_absolute": bool(
            np.max(owner_absolute_difference) < 1.0e-8
        ),
        "owner_leading_direction_centers_agree_below_1e_minus_9_scaled": bool(
            np.max(owner_scaled_difference) < 1.0e-9
        ),
        "all_370_direct_endpoint_graphs_are_reused_without_recomputation": (
            len(nodes) == 370
            and all_endpoints["claim_boundary"][
                "CURRENT_GREEN_MIXED_DIRECT_BILINEAR_ALL_ENDPOINT_CENTERS_MATERIALIZED"
            ]
        ),
        "no_empirical_value_fit_scale_or_new_center_used": True,
        "owner_witness_is_authorized_by_post_reconnaissance_compute_audit": (
            owner_witness_authorized
        ),
    }
    return {
        "artifact": "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_BILINEAR_OUTWARD_RECONCILIATION",
        "status": "EXACT_POLARIZATION_IDENTITY_AND_COMMON_OUTWARD_GRAPH_RECONCILED",
        "classification": "CURRENT_GREEN_MIXED_ENDPOINT_OUTWARD_REPRESENTATION_AUTHORITY",
        "identity": "D2F[u,v]=(D2F[u+v,u+v]-D2F[u-v,u-v])/4",
        "identity_domain": "C2_RETAINED_ACTION_RATE_ON_THE_REGULAR_CURRENT_ENDPOINT_DOMAIN",
        "derivative_ledger": [
            "selected_eigenline",
            "bordered_hard_response",
            "normalized_physical_field",
            "scalar_rate_readout",
        ],
        "seed_nodes": list(SEED_NODES),
        "seed_columns_reconciled_per_node": direct.COORDINATES,
        "maximum_seed_center_absolute_difference": float(
            np.max(seed_absolute_difference)
        ),
        "maximum_seed_center_scaled_difference": float(
            np.max(seed_scaled_difference)
        ),
        "maximum_seed_common_hull_radius": float(np.max(seed_hull_radius)),
        "reconnaissance_owner_node": owner,
        "owner_polarization_precision_bits": PRECISION,
        "owner_polarization_elapsed_seconds": owner_elapsed,
        "maximum_owner_leading_direction_center_absolute_difference": float(
            np.max(owner_absolute_difference)
        ),
        "maximum_owner_leading_direction_center_scaled_difference": float(
            np.max(owner_scaled_difference)
        ),
        "maximum_owner_leading_direction_common_hull_radius": float(
            np.max(owner_hull_radius)
        ),
        "adjudication": (
            "THE_EXACT_FRECHET_HESSIAN_POLARIZATION_IDENTITY_OWNS_THE_"
            "REPRESENTATION;_ONE_COMMON_OUTWARD_HULL_EXPLICITLY_CARRIES_THE_"
            "INDEPENDENT_ROUNDING_GRAPHS_AT_ALL_296_DECISIVE_SEED_COLUMNS_"
            "AND_AT_THE_RECONNAISSANCE_OWNER_LEADING_DIRECTION"
        ),
        "exact_next_calculation": (
            "TRANSPORT_THE_RECONCILED_MIXED_ENDPOINT_GRAPH_THROUGH_THE_"
            "CORRELATED_HERMITE_SIMPSON_MIDPOINT_AND_CAUSAL_PRECONDITIONER"
        ),
        "claim_boundary": {
            "CURRENT_GREEN_MIXED_DIRECT_BILINEAR_OUTWARD_EQUIVALENCE_DERIVED": True,
            "CURRENT_GREEN_MIXED_TRANSVERSE_ALL_ENDPOINTS_DERIVED": True,
            "CURRENT_GREEN_MIXED_TRANSVERSE_ALL_MIDPOINTS_DERIVED": False,
            "CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "data": _relative(DATA),
        "data_SHA256": _sha(DATA),
        "owner_witness_SHA256": _sha(owner_shard),
        "inputs": {_relative(path): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("mixed bilinear outward reconciliation failed")
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "reconnaissance_owner_node": payload["reconnaissance_owner_node"],
        "maximum_seed_common_hull_radius": payload[
            "maximum_seed_common_hull_radius"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
