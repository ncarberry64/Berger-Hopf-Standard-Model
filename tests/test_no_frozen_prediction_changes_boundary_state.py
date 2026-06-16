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


def test_frozen_prediction_files_unchanged_for_boundary_state_gate() -> None:
    for relative, expected in FROZEN_HASHES.items():
        assert _sha256(ROOT / relative) == expected


def test_boundary_state_results_report_frozen_unchanged() -> None:
    text = (
        ROOT / "theory" / "boundary_state_primitive_derivation_results.json"
    ).read_text(encoding="utf-8")
    assert '"frozen_predictions_changed": false' in text
    assert "FROZEN_PREDICTIONS_UNCHANGED" in text
