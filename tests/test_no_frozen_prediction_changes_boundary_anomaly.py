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


def test_frozen_prediction_files_unchanged_for_boundary_anomaly_gate() -> None:
    for relative, expected in FROZEN_HASHES.items():
        assert _sha256(ROOT / relative) == expected


def test_boundary_anomaly_results_report_frozen_unchanged() -> None:
    text = (
        ROOT / "theory" / "boundary_integer_anomaly_closure_results.json"
    ).read_text(encoding="utf-8")
    assert '"frozen_predictions_changed": false' in text
    assert "FROZEN_PREDICTIONS_UNCHANGED" in text
