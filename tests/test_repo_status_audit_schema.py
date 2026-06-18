from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {
    "clean",
    "updated",
    "stale_but_historical",
    "needs_user_review",
    "forbidden_overclaim_removed",
}


def test_repo_status_audit_schema() -> None:
    payload = json.loads(
        (ROOT / "docs" / "repo_status_audit_full_bhsm_v1.json").read_text(
            encoding="utf-8"
        )
    )
    assert payload["status"] == "repo_status_refresh_complete"
    assert payload["branch"] == "bhsm-repo-status-refresh-full-audit-v1"
    assert payload["official_predictions_changed"] is False
    assert payload["frozen_predictions_changed"] is False
    assert payload["release_published"] is False
    assert payload["zenodo_auth_material_handled"] is False
    assert payload["findings"]
    assert set(payload["allowed_classifications"]) == ALLOWED
    for finding in payload["findings"]:
        assert finding["classification"] in ALLOWED
        assert finding["area"]
        assert finding["finding"]
        assert finding["action"]


def test_repo_status_audit_verdict_labels() -> None:
    payload = json.loads(
        (ROOT / "docs" / "repo_status_audit_full_bhsm_v1.json").read_text(
            encoding="utf-8"
        )
    )
    labels = set(payload["verdict_labels"])
    assert "BHSM_REPO_STATUS_REFRESH_COMPLETE" in labels
    assert "GITHUB_README_REFRESHED" in labels
    assert "FULL_BHSM_STATUS_SYNCHRONIZED" in labels
    assert "NO_RELEASE_PUBLISHED" in labels
