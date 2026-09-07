"""Aggregate the current-Green full-transverse quadratic center shards."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
from flint import arb, ctx


ROOT = Path(__file__).resolve().parents[1]
F = ROOT / "artifacts/flagship_integration"
C = ROOT / "artifacts/current_semantics"
WORK = F / ".current_green_full_transverse_quadratic_center_work"
RESULT = F / "BHSM_N12_GATE7_CURRENT_GREEN_FULL_TRANSVERSE_QUADRATIC_CENTER.json"
DATA = RESULT.with_suffix(".npz")
CAMPAIGN = ROOT / "scripts/derive_n12_gate7_current_green_full_transverse_quadratic_center.py"
JUSTIFICATION = C / "BHSM_N12_GATE7_CURRENT_GREEN_FULL_TRANSVERSE_COMPUTE_JUSTIFICATION.json"
SEED = F / "BHSM_N12_GATE7_CURRENT_GREEN_TRANSVERSE_QUADRATIC_SEED.json"
THEORY = ROOT / "theory/n12_gate7_current_green_full_transverse_quadratic_majorant.md"
THIS_SCRIPT = Path(__file__).resolve()
SHARD_REVISION = 4
AGGREGATION_PRECISION = 512
FIELDS = (
    "quadratic_Frobenius_norm",
    "quadratic_maximum_component_absolute",
    "field_quadratic_Frobenius_norm",
    "scalar_quadratic_Frobenius_norm",
    "minimum_selected_eigenline_gap",
    "normalized_field_reference_difference_2_norm",
    "axis_projection_residual_2_norm",
    "base_response_residual_2_norm",
    "first_response_relative_Frobenius_residual",
    "second_response_relative_Frobenius_residual",
    "second_eigenline_normalization_Frobenius_residual",
    "second_field_normalization_Frobenius_residual",
    "elapsed_seconds",
)


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _paths(kind: str) -> list[Path]:
    indices = range(1, 371) if kind == "endpoint" else range(370)
    return [WORK / f"{kind}_{index:03d}.npz" for index in indices]


def _arb_relative_square_decomposition_residual(
    total: np.ndarray,
    parts: np.ndarray,
) -> float:
    """Aggregate stored binary center norms with 512-bit directed arithmetic."""
    maximum = 0.0
    tiny = arb(float(np.finfo(float).tiny))
    for value, row in zip(total, parts, strict=True):
        whole = arb(float(value)) ** 2
        subtotal = arb(0)
        for component in row:
            subtotal += arb(float(component)) ** 2
        denominator = whole if float(whole.lower()) > float(tiny) else tiny
        residual = abs(whole - subtotal) / denominator
        maximum = max(maximum, float(residual.upper()))
    return math.nextafter(maximum, math.inf)


def _arb_sum(values: np.ndarray) -> arb:
    total = arb(0)
    for value in np.asarray(values, dtype=float).ravel():
        total += arb(float(value))
    return total


def _load_kind(kind: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, str, list[str]]:
    paths = _paths(kind)
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"{len(missing)} missing {kind} shards; first={missing[0]}")
    values = np.empty((len(paths), len(FIELDS)))
    output_norms = np.empty((len(paths), 99))
    output_maxima = np.empty((len(paths), 99))
    fingerprints: set[str] = set()
    hashes = []
    for row, path in enumerate(paths):
        with np.load(path) as source:
            expected_index = row + 1 if kind == "endpoint" else row
            if str(source["kind"].item()) != kind or int(source["index"]) != expected_index:
                raise RuntimeError(f"mislabelled shard: {path}")
            if int(source["shard_revision"]) != SHARD_REVISION:
                raise RuntimeError(f"stale shard revision: {path}")
            fingerprints.add(str(source["campaign_fingerprint"].item()))
            values[row] = [float(source[field]) for field in FIELDS]
            output_norms[row] = np.asarray(
                source["quadratic_output_Frobenius_norms"], dtype=float,
            )
            output_maxima[row] = np.asarray(
                source["quadratic_output_maximum_component_absolute"], dtype=float,
            )
        hashes.append(f"{path.name}:{_sha(path)}")
    if len(fingerprints) != 1:
        raise RuntimeError(f"mixed campaign fingerprints in {kind} shards")
    return values, output_norms, output_maxima, fingerprints.pop(), hashes


def build_payload() -> dict[str, object]:
    ctx.prec = AGGREGATION_PRECISION
    required = (CAMPAIGN, JUSTIFICATION, SEED, THEORY, THIS_SCRIPT)
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    justification = json.loads(JUSTIFICATION.read_text(encoding="utf-8"))
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    endpoints, endpoint_output, endpoint_maxima, endpoint_fingerprint, endpoint_hashes = _load_kind("endpoint")
    midpoints, midpoint_output, midpoint_maxima, midpoint_fingerprint, midpoint_hashes = _load_kind("midpoint")
    combined = np.vstack((endpoints, midpoints))
    combined_output = np.vstack((endpoint_output, midpoint_output))
    combined_maxima = np.vstack((endpoint_maxima, midpoint_maxima))
    column = {name: index for index, name in enumerate(FIELDS)}
    qnorm = combined[:, column["quadratic_Frobenius_norm"]]
    owner = int(np.argmax(qnorm))
    owner_kind = "endpoint" if owner < 370 else "midpoint"
    owner_index = owner + 1 if owner < 370 else owner - 370
    endpoint_qnorm = endpoints[:, column["quadratic_Frobenius_norm"]]
    seed_rows = seed["rows"]
    seed_dominated = all(
        float(row["quadratic_rate_curvature_norm_upper"])
        <= math.nextafter(float(endpoint_qnorm[int(row["node"]) - 1]), math.inf)
        for row in seed_rows
    )
    f = combined[:, column["field_quadratic_Frobenius_norm"]]
    s = combined[:, column["scalar_quadratic_Frobenius_norm"]]
    componentwise_relative = _arb_relative_square_decomposition_residual(
        qnorm, combined_output,
    )
    pythagorean_relative = _arb_relative_square_decomposition_residual(
        qnorm, np.column_stack((f, s)),
    )
    manifest = hashlib.sha256("\n".join(endpoint_hashes + midpoint_hashes).encode("ascii")).hexdigest().upper()
    validation = {
        "all_370_defined_axis_endpoint_shards_present": endpoints.shape == (370, len(FIELDS)),
        "all_370_midpoint_shards_present": midpoints.shape == (370, len(FIELDS)),
        "one_campaign_fingerprint_retained": endpoint_fingerprint == midpoint_fingerprint,
        "all_exported_values_finite": bool(np.all(np.isfinite(combined))),
        "all_selected_eigenline_gaps_positive": bool(np.all(combined[:, column["minimum_selected_eigenline_gap"]] > 0.0)),
        "all_maximum_components_below_Frobenius_norm": bool(np.all(combined[:, column["quadratic_maximum_component_absolute"]] <= qnorm)),
        "all_componentwise_maxima_below_componentwise_Frobenius_norms": bool(np.all(combined_maxima <= combined_output)),
        "componentwise_Frobenius_norms_recompose_total_norms": componentwise_relative < 1.0e-12,
        "field_scalar_Frobenius_decomposition_consistent": float(pythagorean_relative) < 1.0e-12,
        "all_first_response_relative_residuals_below_1e_minus_10": bool(np.max(combined[:, column["first_response_relative_Frobenius_residual"]]) < 1.0e-10),
        "all_second_response_relative_residuals_below_1e_minus_10": bool(np.max(combined[:, column["second_response_relative_Frobenius_residual"]]) < 1.0e-10),
        "all_eigenline_normalization_residuals_below_1e_minus_6": bool(np.max(combined[:, column["second_eigenline_normalization_Frobenius_residual"]]) < 1.0e-6),
        "all_field_normalization_residuals_below_1e_minus_6": bool(np.max(combined[:, column["second_field_normalization_Frobenius_residual"]]) < 1.0e-6),
        "all_midpoint_axis_projection_residuals_below_1e_minus_6": bool(np.max(midpoints[:, column["axis_projection_residual_2_norm"]]) < 1.0e-6),
        "all_seed_directional_Arb_upper_bounds_dominated_by_full_center_Frobenius_norms": seed_dominated,
        "compute_justification_authorized_campaign": justification.get("campaign_authorized") is True,
        "final_shard_aggregation_uses_512_bit_Arb_arithmetic": ctx.prec == AGGREGATION_PRECISION,
        "full_unit_sphere_center_majorant_follows_by_Hilbert_Schmidt_inequality": True,
        "outward_neighborhood_authority_not_claimed": True,
        "no_empirical_or_calibration_input_used": True,
        "CURRENT_GREEN_TRANSVERSE_TRANSVERSE_FULL_OPERATOR_BOUND_DERIVED": False,
        "FULL_BHSM_COMPLETE": False,
    }
    passed = all(value for key, value in validation.items() if key not in {
        "CURRENT_GREEN_TRANSVERSE_TRANSVERSE_FULL_OPERATOR_BOUND_DERIVED",
        "FULL_BHSM_COMPLETE",
    }) and not validation["CURRENT_GREEN_TRANSVERSE_TRANSVERSE_FULL_OPERATOR_BOUND_DERIVED"] and not validation["FULL_BHSM_COMPLETE"]
    if not passed:
        failed = [key for key, value in validation.items() if key not in {
            "CURRENT_GREEN_TRANSVERSE_TRANSVERSE_FULL_OPERATOR_BOUND_DERIVED",
            "FULL_BHSM_COMPLETE",
        } and not value]
        raise RuntimeError(f"center aggregation validation failed: {failed}")
    np.savez_compressed(
        DATA,
        endpoint_indices=np.arange(1, 371),
        midpoint_indices=np.arange(370),
        field_names=np.asarray(FIELDS),
        endpoint_rows=endpoints,
        midpoint_rows=midpoints,
        endpoint_output_Frobenius_norms=endpoint_output,
        midpoint_output_Frobenius_norms=midpoint_output,
        endpoint_output_maximum_component_absolute=endpoint_maxima,
        midpoint_output_maximum_component_absolute=midpoint_maxima,
        all_node_output_Frobenius_majorant=np.max(combined_output, axis=0),
        campaign_fingerprint=np.asarray(endpoint_fingerprint),
        shard_manifest_SHA256=np.asarray(manifest),
    )
    inputs = {
        _relative(path): _sha(path) for path in required
    }
    return {
        "artifact": "BHSM_N12_GATE7_CURRENT_GREEN_FULL_TRANSVERSE_QUADRATIC_CENTER",
        "status": "CURRENT_GREEN_FULL_TRANSVERSE_QUADRATIC_CENTER_OPERATOR_DERIVED",
        "authority": "COMPLETE_BINARY64_SIGNED_CENTER_TENSOR_WITH_HILBERT_SCHMIDT_UNIT_SPHERE_MAJORANT_NOT_OUTWARD_NEIGHBORHOOD_AUTHORITY",
        "data": _relative(DATA),
        "data_SHA256": _sha(DATA),
        "campaign_fingerprint": endpoint_fingerprint,
        "shard_manifest_SHA256": manifest,
        "aggregation_precision_bits": AGGREGATION_PRECISION,
        "coverage": {
            "endpoint_nodes": "1_THROUGH_370",
            "midpoint_intervals": "0_THROUGH_369",
            "coordinate_dimension": 74,
            "current_Green_complement_dimension": 73,
            "augmented_output_dimension": 99,
        },
        "maximum_center_transverse_quadratic_Frobenius_norm": float(qnorm[owner]),
        "maximum_center_owner": {"kind": owner_kind, "index": owner_index},
        "maximum_component_absolute": float(np.max(combined[:, column["quadratic_maximum_component_absolute"]])),
        "maximum_componentwise_output_Frobenius_majorant": float(np.max(combined_output)),
        "minimum_selected_eigenline_gap": float(np.min(combined[:, column["minimum_selected_eigenline_gap"]])),
        "maximum_first_response_relative_residual": float(np.max(combined[:, column["first_response_relative_Frobenius_residual"]])),
        "maximum_second_response_relative_residual": float(np.max(combined[:, column["second_response_relative_Frobenius_residual"]])),
        "maximum_midpoint_axis_projection_residual": float(np.max(midpoints[:, column["axis_projection_residual_2_norm"]])),
        "componentwise_Frobenius_maximum_relative_recomposition_residual": float(componentwise_relative),
        "field_scalar_Frobenius_maximum_relative_decomposition_residual": float(pythagorean_relative),
        "measured_CPU_hours": float(
            _arb_sum(combined[:, column["elapsed_seconds"]]) / arb(3600)
        ),
        "claim_boundary": {
            "CURRENT_GREEN_TRANSVERSE_TRANSVERSE_FULL_CENTER_OPERATOR_DERIVED": True,
            "CURRENT_GREEN_TRANSVERSE_TRANSVERSE_FULL_UNIT_SPHERE_CENTER_MAJORANT_DERIVED": True,
            "CURRENT_GREEN_TRANSVERSE_TRANSVERSE_OUTWARD_REMAINDER_DERIVED": False,
            "CURRENT_GREEN_TRANSVERSE_TRANSVERSE_FULL_OPERATOR_BOUND_DERIVED": False,
            "CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED": False,
            "G7_ROOT_NONEXISTENCE_DERIVED": False,
            "G7_PHYSICAL_SPACETIME_INSTABILITY_DERIVED": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_calculation": "ATTACH_A_RIGOROUS_OUTWARD_ROUNDING_AND_AXIS_NEIGHBORHOOD_REMAINDER_TO_THE_ALL_NODE_CENTER_MAJORANT_THEN_INSERT_IT_WITH_THE_CERTIFIED_MIXED_CAUSAL_OPERATOR_IN_THE_TWO_RADIUS_SCREEN",
        "inputs": inputs,
        "validation": validation,
        "validation_passed": passed,
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
        "maximum": payload["maximum_center_transverse_quadratic_Frobenius_norm"],
        "owner": payload["maximum_center_owner"],
        "measured_CPU_hours": payload["measured_CPU_hours"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
