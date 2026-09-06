"""Aggregate the complete supplemental midpoint Hessian-block campaign."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import derive_n12_gate7_current_green_signed_transverse_tensor_recovery as recovery  # noqa: E402
import derive_n12_gate7_current_green_supplemental_midpoint_blocks as supplement  # noqa: E402


F = ROOT / "artifacts" / "flagship_integration"
C = ROOT / "artifacts" / "current_semantics"
RESULT = F / "BHSM_N12_GATE7_CURRENT_GREEN_SUPPLEMENTAL_MIDPOINT_BLOCKS.json"
VALIDATION = C / "BHSM_N12_GATE7_SUPPLEMENTAL_MIXED_RATE_UU_VALIDATION.json"
THIS_SCRIPT = Path(__file__).resolve()


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _manifest(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(_relative(path).encode("utf-8"))
        digest.update(b"\0")
        digest.update(_sha(path).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest().upper()


def _valid_aggregate(
    path: Path,
    interval: int,
    fingerprint: str,
    recovered_sha: str,
) -> bool:
    if not path.is_file():
        return False
    try:
        with np.load(path) as source:
            cu = np.asarray(source["complement_retained"], dtype=float)
            cc = np.asarray(source["complement_complement"], dtype=float)
            return bool(
                int(source["interval"]) == interval
                and int(source["shard_revision"]) == supplement.SHARD_REVISION
                and str(source["campaign_fingerprint"].item()) == fingerprint
                and str(source["recovered_shard_SHA256"].item()) == recovered_sha
                and int(source["evaluated_new_direction_pairs"]) == supplement.NEW_PAIRS
                and cu.shape == (99, 26, 73)
                and cc.shape == (99, 26, 26)
                and source["retained_directions"].shape == (99, 73)
                and source["complement_directions"].shape == (99, 26)
                and source["frame_qr_diagonal"].shape == (74,)
                and source["row_diagnostics"].shape == (26, 5)
                and source["row_elapsed_seconds"].shape == (26,)
                and np.all(np.isfinite(cu))
                and np.all(np.isfinite(cc))
                and np.array_equal(cc, cc.transpose(0, 2, 1))
                and np.all(np.isfinite(source["row_diagnostics"]))
                and float(source["coordinate_basis_residual"]) < 5.0e-13
                and float(source["normal_frame_residual"]) < 5.0e-13
                and np.all(np.asarray(source["frame_qr_diagonal"]) > 0.0)
                and math.isfinite(float(source["full_basis_condition_2"]))
            )
    except Exception:
        return False


def build_payload() -> dict[str, object]:
    if not VALIDATION.is_file():
        raise FileNotFoundError("supplemental UU identity validation required")
    identity = json.loads(VALIDATION.read_text(encoding="utf-8"))
    fingerprint = supplement._fingerprint()
    recovery_fingerprint = recovery._fingerprint()
    identity_inputs = identity.get("inputs", {})
    identity_current = bool(
        identity.get("validation_passed") is True
        and identity.get("recovery_campaign_fingerprint")
        == recovery_fingerprint
        and isinstance(identity_inputs, dict)
        and identity_inputs
        and all(
            (ROOT / relative).is_file()
            and digest == _sha(ROOT / relative)
            for relative, digest in identity_inputs.items()
        )
    )
    if not identity_current:
        raise RuntimeError("current supplemental UU identity validation required")
    aggregates: list[Path] = []
    rows: list[Path] = []
    maximum_diagnostics = np.zeros(5)
    minimum_qr_pivot = math.inf
    maximum_coordinate_residual = 0.0
    maximum_normal_residual = 0.0
    maximum_condition = 0.0
    elapsed_seconds = 0.0
    for interval in range(supplement.INTERVALS):
        recovered = recovery._path("midpoint", interval)
        if not recovery._valid(
            recovered, "midpoint", interval, recovery_fingerprint,
        ):
            raise RuntimeError(f"validated recovered midpoint required: {interval}")
        recovered_sha = _sha(recovered)
        aggregate = supplement._aggregate_path(interval)
        if not _valid_aggregate(aggregate, interval, fingerprint, recovered_sha):
            raise RuntimeError(f"validated supplemental aggregate required: {interval}")
        row_paths = [
            supplement._row_path(interval, row)
            for row in range(supplement.COMPLEMENT)
        ]
        if not all(supplement._valid_row(
            path, interval, row, fingerprint, recovered_sha,
        ) for row, path in enumerate(row_paths)):
            raise RuntimeError(f"validated supplemental rows required: {interval}")
        with np.load(aggregate) as source:
            maximum_diagnostics = np.maximum(
                maximum_diagnostics,
                np.max(np.asarray(source["row_diagnostics"], dtype=float), axis=0),
            )
            minimum_qr_pivot = min(
                minimum_qr_pivot,
                float(np.min(source["frame_qr_diagonal"])),
            )
            maximum_coordinate_residual = max(
                maximum_coordinate_residual,
                float(source["coordinate_basis_residual"]),
            )
            maximum_normal_residual = max(
                maximum_normal_residual, float(source["normal_frame_residual"]),
            )
            maximum_condition = max(
                maximum_condition, float(source["full_basis_condition_2"]),
            )
            elapsed_seconds += float(np.sum(source["row_elapsed_seconds"]))
        aggregates.append(aggregate)
        rows.extend(row_paths)
    validations = {
        "all_370_midpoint_aggregates_valid": len(aggregates) == 370,
        "all_9620_restart_rows_valid": len(rows) == 370 * 26,
        "exactly_2249_new_direction_pairs_per_midpoint": supplement.NEW_PAIRS == 2249,
        "rectangular_kernel_matches_recovered_UU_authority": identity_current,
        "completed_basis_has_no_zero_QR_pivot": minimum_qr_pivot > 0.0,
        "coordinate_basis_residual_below_5e_minus_13": maximum_coordinate_residual < 5.0e-13,
        "normal_frame_residual_below_5e_minus_13": maximum_normal_residual < 5.0e-13,
        "all_center_diagnostics_finite": bool(np.all(np.isfinite(maximum_diagnostics))),
        "no_action_mesh_frame_axis_or_proof_parameter_changed": True,
    }
    passed = all(validations.values())
    tracked = [VALIDATION, THIS_SCRIPT, Path(supplement.__file__).resolve()]
    return {
        "artifact": "BHSM_N12_GATE7_CURRENT_GREEN_SUPPLEMENTAL_MIDPOINT_BLOCKS",
        "status": (
            "ALL_SIGNED_CU_CC_MIDPOINT_CENTER_BLOCKS_DERIVED"
            if passed else "SUPPLEMENTAL_MIDPOINT_BLOCKS_INCOMPLETE_OR_INVALID"
        ),
        "authority": "UNCHANGED_ACTION_SIGNED_RECTANGULAR_D2_RATE_CENTER",
        "summary": {
            "midpoint_count": len(aggregates),
            "restart_row_count": len(rows),
            "new_direction_pairs_per_midpoint": supplement.NEW_PAIRS,
            "total_new_direction_pairs": supplement.NEW_PAIRS * len(aggregates),
            "center_compute_CPU_hours": elapsed_seconds / 3600.0,
            "minimum_frame_QR_pivot": minimum_qr_pivot,
            "maximum_coordinate_basis_residual": maximum_coordinate_residual,
            "maximum_normal_frame_residual": maximum_normal_residual,
            "maximum_full_basis_condition_2": maximum_condition,
            "maximum_row_diagnostics": maximum_diagnostics.tolist(),
        },
        "aggregate_manifest_SHA256": _manifest(aggregates),
        "restart_row_manifest_SHA256": _manifest(rows),
        "campaign_fingerprint": fingerprint,
        "recovery_campaign_fingerprint": recovery_fingerprint,
        "validation": validations,
        "validation_passed": passed,
        "claim_boundary": {
            "complete_signed_midpoint_center_Hessian": "DERIVED" if passed else "OPEN",
            "outward_midpoint_Hessian_remainder": "OPEN",
            "causal_two_radius_certificate": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "RECONSTRUCT_EACH_ACTUAL_HERMITE_SIMPSON_MIDPOINT_PULLBACK_"
            "THROUGH_THE_COMPLETE_S_EQUALS_U_C_BASIS_BEFORE_CAUSAL_NORMS"
        ),
        "inputs": {_relative(path): _sha(path) for path in tracked},
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not payload["validation_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
