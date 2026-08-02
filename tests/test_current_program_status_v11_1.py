from __future__ import annotations

import json
from pathlib import Path

from bhsm.interface.completion.final_completion_gate_v11_1 import canonical_completion_gate_payload
from bhsm.interface.current_program_status import (
    CURRENT_VERSION,
    EXACT_NEXT_OBJECT,
    PRIMARY_VERDICT,
    public_repo_status,
    status_payload,
)
from bhsm.interface.master_action import CURRENT_MISSING_OBJECT, CURRENT_VERDICT
from bhsm.interface.neutrino_closure_status import PUBLIC_REPO_STATUS


ROOT = Path(__file__).resolve().parents[1]


def test_python_current_status_surfaces_share_one_source() -> None:
    assert CURRENT_VERSION == "v11.1"
    assert CURRENT_MISSING_OBJECT == EXACT_NEXT_OBJECT
    assert CURRENT_VERDICT == PRIMARY_VERDICT
    assert PUBLIC_REPO_STATUS == public_repo_status()
    assert status_payload()["primary_verdict"] == PRIMARY_VERDICT
    assert canonical_completion_gate_payload()["current_verdict"] == PRIMARY_VERDICT


def test_repository_current_status_surfaces_are_synchronized() -> None:
    for name in ("README.md", "STATUS.md", "CLAIMS.md", "ROADMAP.md", "FALSIFICATION.md"):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert "v11.1" in text.lower(), name
        assert PRIMARY_VERDICT in text, name
        assert EXACT_NEXT_OBJECT in text, name
    current = json.loads((ROOT / "docs" / "current_bhsm_status.json").read_text(encoding="utf-8"))
    assert current["current_version"] == CURRENT_VERSION
    assert current["primary_verdict"] == PRIMARY_VERDICT
    assert current["exact_next_object"] == EXACT_NEXT_OBJECT
