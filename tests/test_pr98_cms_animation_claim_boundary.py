import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs/assets/pr98_cms_open_data_animation"


def test_pr98_animation_claim_boundary_is_explicit_and_safe():
    manifest = json.loads((ASSETS / "pr98_cms_sample_manifest.json").read_text(encoding="utf-8"))
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            ROOT / "README.md",
            ROOT / "docs/pr98_cms_open_data_animation.md",
            ASSETS / "README.md",
        )
    )
    assert manifest["claim_boundary"] == "Engine validation only; not empirical validation of BHSM Physics."
    assert manifest["detector_reconstruction_claimed"] is False
    assert manifest["cms_cern_endorsement_claimed"] is False
    assert manifest["frozen_predictions_modified"] is False
    assert manifest["official_prediction_logic_modified"] is False
    assert "not detector reconstruction" in text.lower()
    assert "not empirical validation of bhsm physics" in text.lower()
    assert "no cms/cern endorsement" in text.lower() or "not cms/cern endorsement" in text.lower()
    assert "atlas open data" not in text.lower()

