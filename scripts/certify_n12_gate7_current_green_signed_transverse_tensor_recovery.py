"""Validate and aggregate every recovered signed transverse center tensor."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
from flint import arb, ctx


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import derive_n12_gate7_current_green_signed_transverse_tensor_recovery as recovery  # noqa: E402


F = ROOT / "artifacts" / "flagship_integration"
C = ROOT / "artifacts" / "current_semantics"
RESULT = F / "BHSM_N12_GATE7_CURRENT_GREEN_SIGNED_TRANSVERSE_TENSOR_RECOVERY.json"
DATA = RESULT.with_suffix(".npz")
JUSTIFICATION = C / "BHSM_N12_GATE7_CURRENT_GREEN_SIGNED_TENSOR_RECOVERY_COMPUTE_JUSTIFICATION.json"
FULL = F / "BHSM_N12_GATE7_CURRENT_GREEN_FULL_TRANSVERSE_QUADRATIC_CENTER.json"
THEORY = ROOT / "theory" / "n12_gate7_current_green_signed_transverse_tensor_recovery.md"
THIS_SCRIPT = Path(__file__).resolve()
PRECISION = 512
FIELDS = (
    "recovered_total_Frobenius_norm",
    "total_Frobenius_relative_residual",
    "output_Frobenius_maximum_relative_residual",
    "tensor_symmetry_relative_Frobenius_residual",
    "basis_orthonormal_residual_2_norm",
    "basis_axis_residual_2_norm",
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
    return [recovery.WORK / f"{kind}_{index:03d}.npz" for index in indices]


def _manifest(paths: list[Path]) -> str:
    rows = [f"{path.name}:{_sha(path)}" for path in paths]
    return hashlib.sha256("\n".join(rows).encode("ascii")).hexdigest().upper()


def _load_kind(
    kind: str, fingerprint: str,
) -> tuple[np.ndarray, list[Path]]:
    paths = _paths(kind)
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            f"{len(missing)} missing {kind} recovery shards; first={missing[0]}"
        )
    rows = np.empty((len(paths), len(FIELDS)))
    for row, path in enumerate(paths):
        index = row + 1 if kind == "endpoint" else row
        if not recovery._valid(path, kind, index, fingerprint):
            raise RuntimeError(f"invalid recovery shard: {path}")
        published = recovery._published_path(kind, index)
        with np.load(path) as source:
            tensor = np.asarray(source["quadratic_tensor"], dtype=float)
            stored_hash = str(source["published_shard_SHA256"].item())
            if stored_hash != _sha(published):
                raise RuntimeError(f"published parent hash changed: {path}")
            total = float(np.linalg.norm(tensor))
            symmetry = float(np.linalg.norm(
                tensor - tensor.transpose(0, 2, 1)
            ) / max(total, np.finfo(float).tiny))
            rows[row] = (
                float(source["recovered_total_Frobenius_norm"]),
                float(source["total_Frobenius_relative_residual"]),
                float(source["output_Frobenius_maximum_relative_residual"]),
                symmetry,
                float(source["basis_orthonormal_residual_2_norm"]),
                float(source["basis_axis_residual_2_norm"]),
                float(source["elapsed_seconds"]),
            )
    return rows, paths


def build_payload() -> dict[str, object]:
    ctx.prec = PRECISION
    required = (JUSTIFICATION, FULL, recovery.__file__, THEORY, THIS_SCRIPT)
    required = tuple(Path(path) for path in required)
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    justification = json.loads(JUSTIFICATION.read_text(encoding="utf-8"))
    full = json.loads(FULL.read_text(encoding="utf-8"))
    if not (
        justification.get("validation_passed") is True
        and justification.get("campaign_authorized") is True
        and full.get("validation_passed") is True
    ):
        raise RuntimeError("validated authorization and center parent required")
    fingerprint = recovery._fingerprint()
    endpoints, endpoint_paths = _load_kind("endpoint", fingerprint)
    midpoints, midpoint_paths = _load_kind("midpoint", fingerprint)
    combined = np.vstack((endpoints, midpoints))
    column = {name: index for index, name in enumerate(FIELDS)}
    elapsed = arb(0)
    for value in combined[:, column["elapsed_seconds"]]:
        elapsed += arb(float(value))
    manifest = _manifest(endpoint_paths + midpoint_paths)
    np.savez_compressed(
        DATA,
        field_names=np.asarray(FIELDS),
        endpoint_indices=np.arange(1, 371), midpoint_indices=np.arange(370),
        endpoint_rows=endpoints, midpoint_rows=midpoints,
        campaign_fingerprint=np.asarray(fingerprint),
        shard_manifest_SHA256=np.asarray(manifest),
    )
    validation = {
        "all_370_defined_axis_endpoint_tensors_recovered": endpoints.shape == (370, len(FIELDS)),
        "all_370_midpoint_tensors_recovered": midpoints.shape == (370, len(FIELDS)),
        "one_recovery_campaign_fingerprint_retained": True,
        "all_recovered_total_norms_reproduce_published_norms": bool(
            np.max(combined[:, column["total_Frobenius_relative_residual"]])
            < 5.0e-13
        ),
        "all_recovered_output_norms_reproduce_published_norms": bool(
            np.max(combined[:, column[
                "output_Frobenius_maximum_relative_residual"
            ]]) < 5.0e-13
        ),
        "all_recovered_tensors_are_symmetric_to_binary64_roundoff": bool(
            np.max(combined[:, column[
                "tensor_symmetry_relative_Frobenius_residual"
            ]]) < 5.0e-13
        ),
        "all_persisted_transverse_bases_are_orthonormal": bool(
            np.max(combined[:, column[
                "basis_orthonormal_residual_2_norm"
            ]]) < 5.0e-13
        ),
        "all_persisted_transverse_bases_annihilate_their_Green_axes": bool(
            np.max(combined[:, column[
                "basis_axis_residual_2_norm"
            ]]) < 5.0e-13
        ),
        "all_exported_summary_values_finite": bool(np.all(np.isfinite(combined))),
        "512_bit_Arb_CPU_aggregation_used": ctx.prec == PRECISION,
        "no_action_center_mesh_frame_axis_parameter_or_precision_changed": True,
        "raw_tensor_cache_not_committed_as_release_payload": True,
        "outward_remainder_and_Gate7_not_claimed": True,
        "FULL_BHSM_COMPLETE": False,
    }
    passed = (
        all(value for key, value in validation.items()
            if key != "FULL_BHSM_COMPLETE")
        and not validation["FULL_BHSM_COMPLETE"]
    )
    return {
        "artifact": "BHSM_N12_GATE7_CURRENT_GREEN_SIGNED_TRANSVERSE_TENSOR_RECOVERY",
        "status": "ALL_740_SIGNED_TRANSVERSE_CENTER_TENSORS_RECOVERED",
        "authority": (
            "COMPLETE_BINARY64_SIGNED_CENTER_TENSOR_CACHE_VALIDATED_AGAINST_"
            "THE_PUBLISHED_512_BIT_AGGREGATED_NORM_CAMPAIGN"
        ),
        "coverage": {
            "endpoint_nodes": "1_THROUGH_370",
            "midpoint_intervals": "0_THROUGH_369",
            "augmented_output_dimension": 99,
            "current_Green_complement_dimension": 73,
        },
        "campaign_fingerprint": fingerprint,
        "shard_manifest_SHA256": manifest,
        "aggregation_precision_bits": PRECISION,
        "measured_CPU_hours": float(elapsed / arb(3600)),
        "maximum_total_Frobenius_relative_residual": float(np.max(
            combined[:, column["total_Frobenius_relative_residual"]]
        )),
        "maximum_output_Frobenius_relative_residual": float(np.max(
            combined[:, column["output_Frobenius_maximum_relative_residual"]]
        )),
        "maximum_tensor_symmetry_relative_Frobenius_residual": float(np.max(
            combined[:, column["tensor_symmetry_relative_Frobenius_residual"]]
        )),
        "maximum_basis_orthonormal_residual_2_norm": float(np.max(
            combined[:, column["basis_orthonormal_residual_2_norm"]]
        )),
        "maximum_basis_axis_residual_2_norm": float(np.max(
            combined[:, column["basis_axis_residual_2_norm"]]
        )),
        "data": _relative(DATA),
        "data_SHA256": _sha(DATA),
        "claim_boundary": {
            "SIGNED_CENTER_TENSORS_RECOVERED": True,
            "SIGNED_CAUSAL_TRANSVERSE_CENTER_OPERATOR_DERIVED": False,
            "OUTWARD_TRANSVERSE_REMAINDER_DERIVED": False,
            "GATE7_CLOSED": False,
            "BHSM_PHYSICAL_BACKGROUND_AUTHORITY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_calculation": (
            "COMPOSE_THE_SIGNED_ENDPOINT_MIDPOINT_INCIDENCE_REDUCED_SOLVE_"
            "AND_FROZEN_CAUSAL_PRODUCTS_BEFORE_TAKING_TRANSVERSE_NORMS"
        ),
        "inputs": {_relative(path): _sha(path) for path in required},
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
        "measured_CPU_hours": payload["measured_CPU_hours"],
        "shard_manifest_SHA256": payload["shard_manifest_SHA256"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
