import json
from pathlib import Path
from bhsm.interface.berger_hodge_component_map.common import REQUIRED_STATEMENTS

ROOT = Path(__file__).resolve().parents[1]

def test_artifact_guards_and_public_claim_boundaries():
    paths = sorted((ROOT / "artifacts").glob("BHSM_*_v4_4.json"))
    assert len(paths) >= 9
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["empirical_inputs_used"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False
        assert payload["orthonormal_formula"] != payload["raw_berger_formula"]
    text = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in ("STATUS.md", "CLAIMS.md"))
    for statement in REQUIRED_STATEMENTS:
        assert statement in text
