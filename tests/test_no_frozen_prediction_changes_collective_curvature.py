from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FROZEN_HASHES = {
    "docs/frozen_predictions.md": "A413C72F731A15B5AF0ED4DDDC3A58D428A60BA3367676FFCDA03FF546593439",
    "docs/frozen_predictions.json": "A9735A4A17934B524C4DE317254AE40838078FBA99274C95C0DBAE11A43C6C17",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def test_frozen_prediction_files_are_unchanged() -> None:
    for relative, expected in FROZEN_HASHES.items():
        assert _sha256(ROOT / relative) == expected


def test_collective_curvature_sprint_does_not_modify_official_files() -> None:
    changed_files = {
        "theory/candidate_collective_curvature_threshold.py",
        "theory/collective_curvature_threshold_layer.md",
        "theory/collective_curvature_threshold_results.json",
        "theory/collective_curvature_dark_matter_interpretation.md",
        "theory/collective_curvature_mass_engine_bridge.md",
        "tests/test_collective_curvature_threshold_schema.py",
        "tests/test_collective_curvature_candidate_hygiene.py",
        "tests/test_collective_curvature_mass_bridge.py",
        "tests/test_collective_curvature_dark_matter_guardrails.py",
        "tests/test_no_frozen_prediction_changes_collective_curvature.py",
    }
    assert "docs/frozen_predictions.md" not in changed_files
    assert "docs/frozen_predictions.json" not in changed_files
    assert "BHSM_BARE_V1" not in changed_files
    assert "BHSM_DRESSED_V1_CANDIDATE" not in changed_files
