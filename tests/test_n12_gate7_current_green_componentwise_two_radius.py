import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_CURRENT_GREEN_COMPONENTWISE_TWO_RADIUS_SCREEN.json"


def test_componentwise_screen_is_valid_and_fail_closed():
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["screen"]["positive_self_map_found"] is False
    assert payload["claim_boundary"]["CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED"] is False
    assert payload["claim_boundary"]["G7_ROOT_NONEXISTENCE_DERIVED"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_componentwise_screen_covers_all_intervals_and_keeps_open_remainders():
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    with np.load(ROOT / payload["data"]) as source:
        assert source["local_transverse_component_box"].shape == (370, 74)
        assert source["causal_transverse_transverse_upper"].shape == (371,)
        assert np.all(np.isfinite(source["local_transverse_component_box"]))
    assert payload["validation"]["normal_axis_remainder_explicitly_omitted_from_optimistic_screen"] is True
    assert payload["validation"]["outward_tube_remainder_explicitly_omitted_from_optimistic_screen"] is True
    assert "SIGNED_TRANSVERSE" in payload["representation_adjudication"]
