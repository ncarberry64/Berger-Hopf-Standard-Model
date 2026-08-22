import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_ORDERED_EVENT_COMPACT_MODULUS.json"
)


def test_ordered_event_compact_modulus_is_same_norm_and_fail_closed():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["same_norm_coefficient_enclosed"] is True
    bounds = payload["bounds"]
    assert bounds["C_event_G_upper"] > bounds["C_ED_G_upper"] > 0.0
    assert (
        bounds["fixed_ball_event_projector_variation_upper"]
        == 2.0 * bounds["C_event_G_upper"]
    )
    assert payload["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
