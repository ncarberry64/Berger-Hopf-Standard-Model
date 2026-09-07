import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_CURRENT_GREEN_TRANSVERSE_QUADRATIC_SEED.json"


def test_current_transverse_quadratic_seed_is_finite_and_fail_closed():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"]
    assert len(payload["rows"]) == 8
    assert {row["node"] for row in payload["rows"]} == {1, 355, 356, 370}
    assert all(
        np.isfinite(row["quadratic_rate_curvature_norm_upper"])
        for row in payload["rows"]
    )
    boundary = payload["claim_boundary"]
    assert boundary[
        "CURRENT_GREEN_TRANSVERSE_TRANSVERSE_DECISIVE_DIRECTION_SEED_DERIVED"
    ]
    assert not boundary[
        "CURRENT_GREEN_TRANSVERSE_TRANSVERSE_FULL_OPERATOR_BOUND_DERIVED"
    ]
    assert not boundary["CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED"]


def test_current_transverse_quadratic_seed_data_is_complete():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    with np.load(ROOT / payload["data"]) as source:
        assert source["transverse_coordinate_directions"].shape == (4, 2, 74)
        assert source["transverse_quadratic_mid"].shape == (4, 2, 99)
        assert source["transverse_quadratic_radius"].shape == (4, 2, 99)
        assert np.all(np.isfinite(source["transverse_quadratic_mid"]))
        assert np.all(source["transverse_quadratic_radius"] >= 0.0)
        assert int(source["precision_bits"]) == 512
