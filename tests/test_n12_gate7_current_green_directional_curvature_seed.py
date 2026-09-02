import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_CURRENT_GREEN_DIRECTIONAL_CURVATURE_SEED.json"
)


def test_current_green_directional_seed_is_outward_and_fail_closed():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"]
    bounds = payload["green_directional_rate_curvature"]["total"]
    assert 0.0 < bounds["lower"] < bounds["upper"] < 0.03
    comparison = payload["comparison_to_existing_transverse_obstruction"]
    assert comparison["transverse_to_green_lower_factor"] > 5.0e6
    assert payload["claim_boundary"][
        "CURRENT_CENTER_NODE1_GREEN_DIRECTIONAL_RATE_CURVATURE_DERIVED"
    ]
    assert not payload["claim_boundary"][
        "CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED"
    ]


def test_seed_data_persists_the_complete_augmented_curvature_vector():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    with np.load(ROOT / payload["data"]) as data:
        assert data["green_directional_rate_curvature_mid"].shape == (99,)
        assert data["green_directional_rate_curvature_radius"].shape == (99,)
        assert int(data["node"]) == 1
        assert int(data["precision_bits"]) == 384
