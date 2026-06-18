from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FROZEN_MD_SHA256 = "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4"
FROZEN_JSON_SHA256 = "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def test_frozen_prediction_files_are_unchanged_by_minimal_branch_threshold() -> None:
    assert _sha(ROOT / "docs" / "frozen_predictions.md") == FROZEN_MD_SHA256
    assert _sha(ROOT / "docs" / "frozen_predictions.json") == FROZEN_JSON_SHA256


def test_official_dressed_candidate_rule_remains_unchanged() -> None:
    payload = json.loads((ROOT / "docs" / "frozen_predictions.json").read_text())
    assert payload["branches"]["bare"] == "BHSM_BARE_V1"
    assert payload["branches"]["dressed_candidate"] == "BHSM_DRESSED_V1_CANDIDATE"
    assert payload["dressing_rule"] == {
        "affects_only": "c/t",
        "factor": 0.5,
        "status": "CANDIDATE",
    }
    assert payload["outputs"]["c/t"]["changed"] is True
    assert payload["outputs"]["u/t"]["changed"] is False
    assert payload["outputs"]["sin_theta_13"]["changed"] is False


def test_reconstruction_json_declares_no_official_or_frozen_mutation() -> None:
    payload = json.loads(
        (ROOT / "theory" / "minimal_branch_threshold_reconstruction_results.json").read_text()
    )
    assert payload["official_predictions_changed"] is False
    assert payload["frozen_predictions_changed"] is False
    assert "no frozen predictions changed" in payload["notes"]
    assert "no official predictions changed" in payload["notes"]
