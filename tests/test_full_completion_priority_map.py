from __future__ import annotations

import json
from pathlib import Path

from bhsm.interface.full_completion import build_full_completion_priority_map, select_highest_leverage_target


ROOT = Path(__file__).resolve().parents[1]


def test_priority_map_uses_explicit_predeclared_scoring() -> None:
    rows = build_full_completion_priority_map()
    assert len(rows) >= 5
    assert rows[0] == select_highest_leverage_target()
    assert rows[0].target_id == "boundary_measure_collar_transport"
    assert rows[0].total_score == 24
    for row in rows:
        expected = (
            row.necessity
            + row.artifact_locality
            + row.no_empirical_path
            + row.cross_sector_leverage
            + row.feasibility_now
            - row.external_runtime_penalty
        )
        assert row.total_score == expected
        assert 0 <= row.external_runtime_penalty <= 5


def test_priority_artifact_records_no_residual_selection() -> None:
    priority = json.loads(
        (ROOT / "artifacts/BHSM_full_completion_priority_map_v1_6.json").read_text(encoding="utf-8")
    )
    selected = json.loads(
        (ROOT / "artifacts/BHSM_full_completion_selected_target_v1_6.json").read_text(encoding="utf-8")
    )
    assert priority["selected_target"] == "boundary_measure_collar_transport"
    assert selected["selected_by_explicit_scoring"] is True
    assert selected["observed_residuals_used"] is False
