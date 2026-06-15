from __future__ import annotations

import hashlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from audit_frozen_prediction_integrity import audit as audit_frozen  # noqa: E402

FROZEN_HASHES = {
    "docs/frozen_predictions.md": "A413C72F731A15B5AF0ED4DDDC3A58D428A60BA3367676FFCDA03FF546593439",
    "docs/frozen_predictions.json": "A9735A4A17934B524C4DE317254AE40838078FBA99274C95C0DBAE11A43C6C17",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def test_frozen_prediction_hashes_are_unchanged() -> None:
    for relative, expected in FROZEN_HASHES.items():
        assert _sha256(ROOT / relative) == expected


def test_frozen_prediction_audit_tool_passes() -> None:
    result = audit_frozen()
    assert result["passed"] is True
    assert result["frozen_predictions_changed"] is False
