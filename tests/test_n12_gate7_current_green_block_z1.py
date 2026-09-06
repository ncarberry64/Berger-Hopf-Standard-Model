import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_CURRENT_GREEN_BLOCK_Z1.json"


def _load():
    return json.loads(RESULT.read_text(encoding="utf-8"))


def test_block_z1_certificate_is_valid_and_fail_closed():
    payload = _load()
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"][
        "CURRENT_GREEN_LONGITUDINAL_TRANSVERSE_BLOCK_Z1_DERIVED"
    ] is True
    assert payload["claim_boundary"][
        "CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED"
    ] is False
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_resolved_rows_have_expected_shape_and_parent_domination():
    payload = _load()
    with np.load(ROOT / payload["data"]) as source:
        rows = np.asarray(source["causal_block_Z1_upper_by_node"], dtype=float)
        maxima = np.asarray(source["causal_block_Z1_maximum_upper"], dtype=float)
        full = np.asarray(source["certified_full_Z1_row_upper"], dtype=float)
    assert rows.shape == (371, 4)
    assert np.array_equal(rows[0], np.zeros(4))
    assert np.all(np.isfinite(rows)) and np.all(rows >= 0.0)
    assert np.array_equal(np.max(rows, axis=0), maxima)
    assert np.all(maxima <= payload["certified_parent_full_Z1_upper"])
    assert np.array_equal(rows[:, 3], full)


def test_green_split_recovers_small_longitudinal_to_transverse_leakage():
    payload = _load()
    bounds = payload["maximum_block_Z1_upper"]
    assert bounds["L_FROM_L"] < 1.0e-3
    assert bounds["T_FROM_L"] < 1.0e-3
    assert bounds["L_FROM_T"] <= payload["certified_parent_full_Z1_upper"]
