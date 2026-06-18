from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FROZEN_MD_SHA256 = "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4"
FROZEN_JSON_SHA256 = "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def test_frozen_prediction_files_are_unchanged_by_bare_yukawa_gate() -> None:
    assert _sha(ROOT / "docs" / "frozen_predictions.md") == FROZEN_MD_SHA256
    assert _sha(ROOT / "docs" / "frozen_predictions.json") == FROZEN_JSON_SHA256


def test_official_branch_and_dressed_candidate_rule_are_unchanged() -> None:
    payload = json.loads((ROOT / "docs" / "frozen_predictions.json").read_text(encoding="utf-8"))
    assert payload["branches"]["bare"] == "BHSM_BARE_V1"
    assert payload["branches"]["dressed_candidate"] == "BHSM_DRESSED_V1_CANDIDATE"
    assert payload["dressing_rule"]["affects_only"] == "c/t"
    assert payload["dressing_rule"]["factor"] == 0.5
    assert payload["dressing_rule"]["status"] == "CANDIDATE"
    assert payload["outputs"]["c/t"]["changed"] is True
    assert payload["outputs"]["u/t"]["changed"] is False
    assert payload["outputs"]["s/b"]["changed"] is False
    assert payload["outputs"]["d/b"]["changed"] is False
    assert payload["outputs"]["sin_theta_13"]["changed"] is False


def test_numerical_gate_json_does_not_claim_official_mutation() -> None:
    path = ROOT / "theory" / "bare_yukawa_numerical_closure_results.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["official_predictions_changed"] is False
    assert payload["frozen_predictions_changed"] is False
    assert "no frozen predictions changed" in payload["notes"]
    assert "the official dressed candidate rule remains unchanged" in payload["notes"]
