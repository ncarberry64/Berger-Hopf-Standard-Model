import json
from pathlib import Path

from bhsm.interface.boundary_collar_measure.common import REQUIRED_STATEMENTS


ROOT = Path(__file__).resolve().parents[1]


def test_artifacts_parse_and_preserve_required_schema():
    paths = sorted((ROOT / "artifacts").glob("BHSM_*_v4_1.json"))
    assert len(paths) >= 12
    required = {"status", "claim_boundary", "candidate_formula", "evidence_for", "evidence_against", "dependencies", "blocking_conditions", "promoted_from", "not_promoted_because", "empirical_inputs_used", "frozen_predictions_changed", "official_prediction_logic_changed"}
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert required <= payload.keys(), path
        assert payload["empirical_inputs_used"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False


def test_claims_publish_exact_guardrails():
    text = (ROOT / "CLAIMS.md").read_text(encoding="utf-8")
    for statement in REQUIRED_STATEMENTS:
        assert statement in text
