from __future__ import annotations

import json
from pathlib import Path

from bhsm.interface.full_completion import build_full_completion_blocker_ledger


ROOT = Path(__file__).resolve().parents[1]


def test_ledger_covers_all_sixteen_completion_categories() -> None:
    blockers = build_full_completion_blocker_ledger()
    assert len(blockers) == 16
    assert {row.category_number for row in blockers} == set(range(1, 17))
    assert len({row.blocker_id for row in blockers}) == 16
    for row in blockers:
        assert row.sector
        assert row.current_status
        assert row.source_artifacts
        assert row.source_files
        assert row.why_it_blocks_full_completion
        assert row.what_would_close_it
        assert row.forbidden_shortcuts
        assert row.recommended_next_action
        assert all((ROOT / path).is_file() for path in (*row.source_artifacts, *row.source_files))


def test_ledger_artifact_parses_and_matches_runtime() -> None:
    payload = json.loads(
        (ROOT / "artifacts/BHSM_full_completion_blocker_ledger_v1_6.json").read_text(encoding="utf-8")
    )
    assert payload["blocker_count"] == 16
    assert payload["blockers"] == [row.to_dict() for row in build_full_completion_blocker_ledger()]
