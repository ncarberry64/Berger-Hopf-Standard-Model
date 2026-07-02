import json
from pathlib import Path

from bhsm.interface.full_action_closure.common import REQUIRED_STATEMENTS


ROOT = Path(__file__).resolve().parents[1]


def test_json_artifacts_parse_and_preserve_guardrails():
    paths = sorted((ROOT / "artifacts").glob("BHSM_*_v4_0.json"))
    assert len(paths) >= 14
    required = {
        "status", "claim_boundary", "evidence_for", "evidence_against", "dependencies",
        "blocking_conditions", "promoted_from", "not_promoted_because", "empirical_inputs_used",
        "frozen_predictions_changed", "official_prediction_logic_changed",
    }
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert required <= payload.keys(), path
        assert payload["empirical_inputs_used"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False


def test_required_claim_boundaries_are_public():
    text = (ROOT / "CLAIMS.md").read_text(encoding="utf-8")
    for statement in REQUIRED_STATEMENTS:
        assert statement in text
