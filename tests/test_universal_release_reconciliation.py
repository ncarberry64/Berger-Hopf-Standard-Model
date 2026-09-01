from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from bhsm.interface.universal_prediction_freeze import FrozenPrediction
from bhsm.interface.universal_release_reconciliation import (
    reconcile_physical_release,
)
from bhsm.interface.universal_spectral_forecast import CertifiedInterval


ROOT = Path(__file__).resolve().parents[1]


def _prediction(mode: str, observable: str, *, background: str = "background"):
    return FrozenPrediction(
        prediction_id=f"prediction:{mode}:{observable}",
        mode_id=mode,
        observable_id=observable,
        classification="DERIVED_INTERVAL_PREDICTION",
        interval=CertifiedInterval(1.0, 1.1),
        categorical_value=None,
        action_version="TEST-ACTION",
        background_id=background,
        scale_map_id="TEST-SCALE",
        frozen_git_commit="freeze-commit",
        provenance=("same-action synthetic unit-test fixture",),
        gate7_closed=True,
        engine_promotion_passed=True,
    )


def _complete_matrix() -> dict:
    rows = []
    for identifier in ("GATE7_PHYSICAL_BACKGROUND", "BENCHMARK_OBSERVABLE_SUITE"):
        rows.append({
            "id": identifier,
            "implementation_status": "IMPLEMENTED_PROMOTABLE",
            "prediction_classification": "DERIVED_INTERVAL_PREDICTION",
            "physical_prediction_materialized": True,
            "empirical_input_used": False,
        })
    rows.append({
        "id": "PHYSICAL_RELEASE_RECONCILIATION",
        "implementation_status": "IMPLEMENTED_GATED",
        "prediction_classification": "OPEN_INTERNAL_BLOCKER",
        "physical_prediction_materialized": False,
        "empirical_input_used": False,
    })
    return {
        "canonical_action_version": "TEST-ACTION",
        "validation_passed": True,
        "records": rows,
    }


def test_synthetic_complete_candidate_closes_only_all_gates(tmp_path: Path) -> None:
    artifact = tmp_path / "prediction.json"
    artifact.write_text('{"prediction":"frozen"}\n', encoding="utf-8")
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    predictions = (
        _prediction("muon", "magnetic_moment"),
        _prediction("mode-X", "decay_width"),
    )
    result = reconcile_physical_release(
        _complete_matrix(),
        predictions,
        (("muon", "magnetic_moment"), ("mode-X", "decay_width")),
        {"prediction.json": digest},
        artifact_root=tmp_path,
        action_version="TEST-ACTION",
        background_id="background",
        scale_map_id="TEST-SCALE",
        release_commit="release-commit",
        gate7_closed=True,
        clean_reproduction_passed=True,
    )
    assert result.FULL_BHSM_COMPLETE is True
    assert result.blockers == ()
    assert result.verified_artifact_count == 1
    result.require_complete()


def test_current_bhsm_matrix_fails_closed_without_predictions() -> None:
    matrix_path = ROOT / "artifacts/BHSM_PHYSICAL_COMPLETENESS_MATRIX.json"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    result = reconcile_physical_release(
        matrix,
        (),
        (("muon", "magnetic_moment"),),
        {"artifacts/BHSM_PHYSICAL_COMPLETENESS_MATRIX.json": hashlib.sha256(
            matrix_path.read_bytes()
        ).hexdigest()},
        artifact_root=ROOT,
        action_version="BHSM-AE-2.0.0",
        background_id="CURRENT-GATE7-BACKGROUND",
        scale_map_id="BHSM-UNIVERSAL-GF-SCALE",
        release_commit="CURRENT-CANDIDATE",
        gate7_closed=False,
        clean_reproduction_passed=False,
    )
    assert result.FULL_BHSM_COMPLETE is False
    assert "Gate7_closed_background" in result.blockers
    assert "all_required_matrix_rows_promoted" in result.blockers
    assert "physically_promoted_frozen_predictions" in result.blockers
    assert "complete_benchmark_coverage" in result.blockers
    assert "clean_deterministic_release_reproduction" in result.blockers
    with pytest.raises(RuntimeError, match="Gate7_closed_background"):
        result.require_complete()


def test_mixed_background_or_bad_hash_cannot_reconcile(tmp_path: Path) -> None:
    artifact = tmp_path / "result.json"
    artifact.write_text("{}\n", encoding="utf-8")
    predictions = (
        _prediction("first", "mass"),
        _prediction("second", "mass", background="different-background"),
    )
    result = reconcile_physical_release(
        _complete_matrix(),
        predictions,
        (("first", "mass"), ("second", "mass")),
        {"result.json": "00" * 32},
        artifact_root=tmp_path,
        action_version="TEST-ACTION",
        background_id="background",
        scale_map_id="TEST-SCALE",
        release_commit="release-commit",
        gate7_closed=True,
        clean_reproduction_passed=True,
    )
    assert "single_background" in result.blockers
    assert "artifact_hash_manifest" in result.blockers
    assert result.FULL_BHSM_COMPLETE is False
