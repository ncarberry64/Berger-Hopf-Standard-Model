import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT / "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_CURRENT_GREEN_DIRECTIONAL_ENDPOINT_CURVATURE.json"
)


def test_all_post_reset_endpoint_green_curvatures_are_certified_fail_closed():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"]
    assert payload["post_reset_nodes_certified"] == 370
    assert payload["claim_boundary"][
        "CURRENT_CENTER_ALL_POST_RESET_ENDPOINT_GREEN_DIRECTIONAL_CURVATURE_DERIVED"
    ]
    assert not payload["claim_boundary"][
        "CURRENT_CENTER_GREEN_MIDPOINT_DIRECTIONAL_CURVATURE_DERIVED"
    ]
    assert not payload["claim_boundary"][
        "CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED"
    ]
    terminal = payload["terminal_endpoint_stiffening"]
    assert terminal["terminal_node"] == 370
    assert terminal["terminal_norm_lower"] > 1.39e11
    assert terminal["terminal_to_node1_upper_growth_factor"] > 5.0e12
    assert terminal["final_31_endpoint_upper_bounds_strictly_increase"]


def test_endpoint_data_preserves_each_complete_augmented_curvature_vector():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    with np.load(ROOT / payload["data"]) as data:
        midpoint = data["green_directional_endpoint_curvature_mid"]
        radius = data["green_directional_endpoint_curvature_radius"]
        lower = data["green_directional_endpoint_norm_lower"]
        upper = data["green_directional_endpoint_norm_upper"]
        mask = data["post_reset_node_mask"]
        assert midpoint.shape == (371, 99)
        assert radius.shape == midpoint.shape
        assert lower.shape == upper.shape == (371,)
        assert mask.shape == (371,)
        assert not bool(mask[0]) and bool(np.all(mask[1:]))
        assert np.all(midpoint[0] == 0.0) and np.all(radius[0] == 0.0)
        assert np.all(lower[1:] <= upper[1:])


def test_node1_reproduces_the_existing_authoritative_seed():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    seed = json.loads((
        ROOT / "artifacts/flagship_integration/"
        "BHSM_N12_GATE7_CURRENT_GREEN_DIRECTIONAL_CURVATURE_SEED.json"
    ).read_text(encoding="utf-8"))
    bounds = payload["endpoint_green_directional_curvature_norm"]
    assert bounds["node1_seed_lower"] == seed[
        "green_directional_rate_curvature"
    ]["total"]["lower"]
    assert bounds["node1_seed_upper"] == seed[
        "green_directional_rate_curvature"
    ]["total"]["upper"]
