from __future__ import annotations

import json
from pathlib import Path

from bhsm.interface.common_16 import ARTIFACT_PATHS


ROOT = Path(__file__).resolve().parents[1]


def test_v18_ledger_exposes_selected_blockers() -> None:
    ledger = json.loads((ROOT / ARTIFACT_PATHS["ledger"]).read_text(encoding="utf-8"))
    assert ledger["full_completion_claimed"] is False
    details = {row["blocker_id"]: row.get("v1_8_detail_status") for row in ledger["blockers"]}
    assert details["FC-03"] == "OPEN_MISSING_RHO_CH_ACTION_DERIVATION"
    assert details["FC-06"] == "OPEN_MISSING_CKM_EXPONENT_DERIVATION"
    assert details["FC-11"] == "OPEN_MISSING_CROSS_SCALE_TRANSPORT_THEOREM"
