from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from audit_bhsm_status import audit as audit_status  # noqa: E402


def test_current_status_says_official_predictions_unchanged() -> None:
    status = json.loads((ROOT / "docs" / "current_bhsm_status.json").read_text())
    assert status["official_predictions_changed"] is False
    assert status["frozen_predictions_changed"] is False


def test_repo_refresh_does_not_touch_official_branch_names() -> None:
    changed_docs = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            ROOT / "README.md",
            ROOT / "docs" / "current_bhsm_status.md",
            ROOT / "docs" / "repo_status_audit_full_bhsm_v1.md",
        ]
    )
    assert "BHSM_BARE_V1" in changed_docs
    assert "BHSM_DRESSED_V1_CANDIDATE" in changed_docs
    assert "Official predictions changed | no" in changed_docs


def test_bhsm_status_audit_tool_passes() -> None:
    result = audit_status()
    assert result["passed"] is True
    assert result["checks"]["official_predictions_unchanged"] is True
