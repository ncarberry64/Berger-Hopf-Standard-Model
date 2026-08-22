import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_FLUX_COMPACT_MODULUS.json"
)


def test_flux_compact_modulus_is_finite_and_action_owned():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["same_norm_coefficient_enclosed"] is True
    bounds = payload["bounds"]
    assert math.isfinite(bounds["C_flux_G_upper"])
    assert bounds["C_flux_G_upper"] > bounds["D2p_upper"] > 0.0
    assert (
        bounds["fixed_ball_flux_variation_upper"]
        == 2.0 * bounds["C_flux_G_upper"]
    )
    assert payload["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
