import json
from pathlib import Path
from bhsm.interface.gallery import build_prediction_gallery
from bhsm.interface.speculative import build_speculative_report, default_speculative_registry
ROOT=Path(__file__).resolve().parents[1]
def test_speculative_template_disabled_by_default():
    registry=default_speculative_registry(); candidate=registry.candidates["template_speculative_mode"]
    assert candidate.enabled_by_default is False and registry.enabled()==[]
    assert build_speculative_report().included==[]
    assert all(e.category!="speculative_candidate" for e in build_prediction_gallery().entries)
    assert any(e.category=="speculative_candidate" for e in build_prediction_gallery(True).entries)
def test_speculative_artifact_is_nonofficial():
    data=json.loads((ROOT/"artifacts/BHSM_speculative_candidate_registry_v0_2.json").read_text())
    assert data["enabled_by_default_count"]==0 and data["official_predictions_changed"] is False
