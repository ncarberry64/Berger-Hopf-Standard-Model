"""Fail-closed reconciliation for a physical BHSM release candidate.

The reconciler does not derive a missing prediction.  It checks that a
candidate already contains one Gate-7-closed background, one action and scale
provenance, complete promoted matrix rows, complete frozen benchmark coverage,
byte-exact artifact hashes, and a clean deterministic reproduction.  The
release row itself is excluded from the prerequisite matrix rows to avoid a
circular completion claim.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Iterable, Mapping

from bhsm.interface.universal_prediction_freeze import (
    FrozenPrediction,
    coverage_matrix,
)


RELEASE_ROW_ID = "PHYSICAL_RELEASE_RECONCILIATION"


@dataclass(frozen=True)
class PhysicalReleaseReconciliation:
    action_version: str
    background_id: str
    scale_map_id: str
    release_commit: str
    matrix_prerequisite_row_count: int
    promoted_matrix_prerequisite_row_count: int
    required_prediction_pair_count: int
    promoted_prediction_pair_count: int
    verified_artifact_count: int
    blockers: tuple[str, ...]
    frozen_prediction_commits: tuple[str, ...]

    @property
    def FULL_BHSM_COMPLETE(self) -> bool:
        return not self.blockers

    def require_complete(self) -> None:
        if self.blockers:
            raise RuntimeError(
                "BHSM physical release blocked by: " + ", ".join(self.blockers)
            )

    def metadata(self) -> dict:
        return {
            "action_version": self.action_version,
            "background_id": self.background_id,
            "scale_map_id": self.scale_map_id,
            "release_commit": self.release_commit,
            "matrix_prerequisite_row_count": self.matrix_prerequisite_row_count,
            "promoted_matrix_prerequisite_row_count": (
                self.promoted_matrix_prerequisite_row_count
            ),
            "required_prediction_pair_count": self.required_prediction_pair_count,
            "promoted_prediction_pair_count": self.promoted_prediction_pair_count,
            "verified_artifact_count": self.verified_artifact_count,
            "frozen_prediction_commits": list(self.frozen_prediction_commits),
            "blockers": list(self.blockers),
            "measured_data_used_to_select_prediction": False,
            "sector_specific_scale_retuning": False,
            "FULL_BHSM_COMPLETE": self.FULL_BHSM_COMPLETE,
        }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def reconcile_physical_release(
    physical_matrix: Mapping,
    predictions: Iterable[FrozenPrediction],
    required_prediction_pairs: Iterable[tuple[str, str]],
    artifact_manifest: Mapping[str, str],
    *,
    artifact_root: str | Path,
    action_version: str,
    background_id: str,
    scale_map_id: str,
    release_commit: str,
    gate7_closed: bool,
    clean_reproduction_passed: bool,
) -> PhysicalReleaseReconciliation:
    """Reconcile a candidate against every internal physical release gate."""

    prediction_rows = tuple(predictions)
    required_pairs = tuple(required_prediction_pairs)
    matrix_rows = tuple(physical_matrix.get("records", ()))
    prerequisite_rows = tuple(
        row for row in matrix_rows if row.get("id") != RELEASE_ROW_ID
    )
    promoted_rows = tuple(
        row for row in prerequisite_rows
        if row.get("implementation_status") == "IMPLEMENTED_PROMOTABLE"
        and row.get("prediction_classification") != "OPEN_INTERNAL_BLOCKER"
        and row.get("physical_prediction_materialized") is True
        and row.get("empirical_input_used") is False
    )
    coverage = coverage_matrix(required_pairs, prediction_rows)

    blockers: list[str] = []
    if not gate7_closed:
        blockers.append("Gate7_closed_background")
    if (
        physical_matrix.get("validation_passed") is not True
        or not prerequisite_rows
        or len({row.get("id") for row in matrix_rows}) != len(matrix_rows)
    ):
        blockers.append("validated_physical_completeness_matrix")
    if len(promoted_rows) != len(prerequisite_rows):
        blockers.append("all_required_matrix_rows_promoted")
    if (
        not prediction_rows
        or not all(prediction.physically_promoted for prediction in prediction_rows)
    ):
        blockers.append("physically_promoted_frozen_predictions")
    if (
        not action_version
        or physical_matrix.get("canonical_action_version") != action_version
        or any(prediction.action_version != action_version for prediction in prediction_rows)
    ):
        blockers.append("single_action_version")
    if (
        not background_id
        or any(prediction.background_id != background_id for prediction in prediction_rows)
    ):
        blockers.append("single_background")
    prediction_scale_ids = {
        prediction.scale_map_id
        for prediction in prediction_rows
        if prediction.scale_map_id is not None
    }
    if not scale_map_id or prediction_scale_ids != {scale_map_id}:
        blockers.append("single_scale_map")
    if not coverage["known_particle_coverage_complete"]:
        blockers.append("complete_benchmark_coverage")
    if not release_commit:
        blockers.append("release_commit")

    root = Path(artifact_root)
    verified_artifacts = 0
    if artifact_manifest:
        for relative, expected in artifact_manifest.items():
            path = root / relative
            if path.is_file() and _sha256(path) == str(expected).upper():
                verified_artifacts += 1
    if not artifact_manifest or verified_artifacts != len(artifact_manifest):
        blockers.append("artifact_hash_manifest")
    if not clean_reproduction_passed:
        blockers.append("clean_deterministic_release_reproduction")

    return PhysicalReleaseReconciliation(
        action_version=action_version,
        background_id=background_id,
        scale_map_id=scale_map_id,
        release_commit=release_commit,
        matrix_prerequisite_row_count=len(prerequisite_rows),
        promoted_matrix_prerequisite_row_count=len(promoted_rows),
        required_prediction_pair_count=coverage["required_pair_count"],
        promoted_prediction_pair_count=coverage["physically_promoted_pair_count"],
        verified_artifact_count=verified_artifacts,
        blockers=tuple(blockers),
        frozen_prediction_commits=tuple(sorted({
            prediction.frozen_git_commit for prediction in prediction_rows
        })),
    )


__all__ = [
    "PhysicalReleaseReconciliation",
    "RELEASE_ROW_ID",
    "reconcile_physical_release",
]
