import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_CURRENT_GREEN_MIXED_TRANSVERSE_SEED.json"


def test_current_green_mixed_transverse_seed_is_finite_and_fail_closed():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"]
    assert [row["node"] for row in payload["rows"]] == [1, 355, 356, 370]
    assert all(
        np.isfinite(row["mixed_interval_Frobenius_upper"])
        for row in payload["rows"]
    )
    boundary = payload["claim_boundary"]
    assert boundary["CURRENT_GREEN_MIXED_TRANSVERSE_DECISIVE_NODE_SEED_DERIVED"]
    assert not boundary["CURRENT_GREEN_MIXED_TRANSVERSE_ALL_NODES_DERIVED"]
    assert not boundary["CURRENT_GREEN_AXIS_NEIGHBORHOOD_MIXED_TRANSVERSE_BOUND_DERIVED"]
    assert not boundary["CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED"]


def test_current_green_mixed_seed_data_has_complete_projected_maps():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    with np.load(ROOT / payload["data"]) as source:
        assert np.array_equal(source["seed_nodes"], np.asarray([1, 355, 356, 370]))
        assert source["mixed_green_transverse_mid"].shape == (4, 99, 74)
        assert source["mixed_green_transverse_radius"].shape == (4, 99, 74)
        assert np.all(np.isfinite(source["mixed_green_transverse_mid"]))
        assert np.all(np.isfinite(source["mixed_green_transverse_radius"]))
        assert np.all(source["mixed_green_transverse_radius"] >= 0.0)
        assert source["central_green_axis_coordinate"].shape == (4, 74)
        assert source["transverse_projector_coordinate"].shape == (4, 74, 74)
        assert int(source["precision_bits"]) == 512
