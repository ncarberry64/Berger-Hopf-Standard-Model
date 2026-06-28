from __future__ import annotations

import json
from pathlib import Path

from bhsm.interface.common_16 import ARTIFACT_PATHS


ROOT = Path(__file__).resolve().parents[1]


def test_all_v18_artifacts_parse() -> None:
    assert len(ARTIFACT_PATHS) == 12
    for relative in ARTIFACT_PATHS.values():
        assert json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_target_selection_uses_predeclared_score() -> None:
    payload = json.loads((ROOT / ARTIFACT_PATHS["selection"]).read_text(encoding="utf-8"))
    assert payload["selected_target"] == "common_16_ckm_transport"
    assert payload["candidate_targets"][0]["total_score"] == 24
    assert payload["scores"]["common_16_ckm_transport"] == 24
    assert payload["empirical_inputs_used"] is False
