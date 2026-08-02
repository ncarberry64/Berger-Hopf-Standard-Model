from __future__ import annotations

import json
from pathlib import Path

from bhsm.interface.completion.final_completion_gate_v11_1 import (
    CURRENT_VERSION,
    EXACT_NEXT_OBJECT,
    PRIMARY_VERDICT,
    canonical_completion_gate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_historical_v11_1_gate_keeps_its_merged_identity() -> None:
    assert CURRENT_VERSION == "v11.1"
    assert canonical_completion_gate_payload()["current_verdict"] == PRIMARY_VERDICT


def test_repository_preserves_v11_1_historical_chronology() -> None:
    for name in ("README.md", "STATUS.md", "CLAIMS.md", "ROADMAP.md", "FALSIFICATION.md"):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert "v11.1" in text.lower(), name
    assert PRIMARY_VERDICT in (ROOT / "STATUS.md").read_text(encoding="utf-8")
    assert EXACT_NEXT_OBJECT in (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
