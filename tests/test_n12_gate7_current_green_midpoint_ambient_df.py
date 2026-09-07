import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_CURRENT_GREEN_MIDPOINT_AMBIENT_DF.json"


def test_midpoint_ambient_df_is_complete_and_fail_closed():
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["CURRENT_GREEN_MIDPOINT_AMBIENT_DF_DERIVED"] is True
    assert payload["claim_boundary"]["CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_midpoint_ambient_df_data_contract():
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    with np.load(ROOT / payload["data"]) as source:
        assert source["ambient_DF_mid"].shape == (370, 99, 99)
        assert source["ambient_DF_radius"].shape == (370, 99, 99)
        assert np.all(source["ambient_DF_radius"] >= 0.0)
        assert np.all(source["selected_direction_sigma_min"] > 0.0)
        assert np.all(np.isfinite(source["ambient_DF_Frobenius_upper"]))
