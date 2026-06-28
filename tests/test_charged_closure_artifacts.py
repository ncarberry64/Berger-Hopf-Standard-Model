from __future__ import annotations

import json
from pathlib import Path

from bhsm.interface.charged_closure import ARTIFACT_PATHS, FULL_COMPLETION_V17_PATHS


ROOT = Path(__file__).resolve().parents[1]


def test_charged_and_completion_update_artifacts_parse() -> None:
    assert len(ARTIFACT_PATHS) == 9
    assert len(FULL_COMPLETION_V17_PATHS) == 2
    for path in (*ARTIFACT_PATHS.values(), *FULL_COMPLETION_V17_PATHS.values()):
        assert json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_completion_ledger_has_detailed_charged_statuses() -> None:
    payload = json.loads(
        (ROOT / FULL_COMPLETION_V17_PATHS["ledger"]).read_text(encoding="utf-8")
    )
    details = {
        row["blocker_id"]: row.get("v1_7_detail_status")
        for row in payload["blockers"]
    }
    assert details["FC-03"] == "CONDITIONAL_CHARGED_ACTION_STIFFNESS_CANDIDATE"
    assert details["FC-05"] == "CONDITIONAL_ETA_L_SOURCE_CANDIDATE"
    assert details["FC-06"] == "OPEN_MISSING_CKM_EXPONENT_DERIVATION"
