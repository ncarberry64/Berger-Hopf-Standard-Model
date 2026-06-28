from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_aggregate_stack_record_is_review_ready_without_release_side_effects() -> None:
    payload = json.loads(
        (ROOT / "artifacts/BHSM_v1_5_status_stabilization_report.json").read_text(encoding="utf-8")
    )
    assert payload["stack_merged"] is True
    assert payload["merge_path"] == "aggregate_integration_branch_from_main"
    assert payload["public_base_branch"] == "main"
    assert payload["internet_required"] is False
    assert payload["external_hep_tools_required"] is False
    assert payload["official_prediction_logic_changed"] is False


def test_integration_files_have_no_unresolved_merge_markers() -> None:
    for path in (
        "README.md",
        "STATUS.md",
        "CLAIMS.md",
        "ROADMAP.md",
        "ARTIFACT_INDEX.md",
        "CLI_REFERENCE.md",
    ):
        text = (ROOT / path).read_text(encoding="utf-8")
        assert "<<<<<<<" not in text
        assert ">>>>>>>" not in text
