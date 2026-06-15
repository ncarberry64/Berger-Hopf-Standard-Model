from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FROZEN_MD_SHA256 = "A413C72F731A15B5AF0ED4DDDC3A58D428A60BA3367676FFCDA03FF546593439"
FROZEN_JSON_SHA256 = "A9735A4A17934B524C4DE317254AE40838078FBA99274C95C0DBAE11A43C6C17"


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
