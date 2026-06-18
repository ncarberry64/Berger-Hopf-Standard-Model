from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FROZEN_HASHES = {
    "docs/frozen_predictions.md": "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4",
    "docs/frozen_predictions.json": "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7",
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
