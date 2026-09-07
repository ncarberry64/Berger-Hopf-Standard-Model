import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_CURRENT_GREEN_HERMITE_SIMPSON_MIDPOINT_CURVATURE.json"
HIGH_PRECISION_ARTIFACT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_CURRENT_GREEN_HERMITE_SIMPSON_MIDPOINT_CURVATURE_512BIT.json"


def test_midpoint_componentwise_direction_ball_route_fails_closed_at_355():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"]
    obstruction = payload["componentwise_direction_ball_obstruction"]
    assert obstruction["finite_intrinsic_prefix_intervals"] == 355
    assert obstruction["first_nonfinite_intrinsic_interval"] == 355
    assert obstruction["nonfinite_intrinsic_intervals"] == list(range(355, 370))
    assert obstruction["midpoint_direction_and_second_incidence_remain_finite"]
    boundary = payload["claim_boundary"]
    assert boundary["CURRENT_CENTER_COMPONENTWISE_GREEN_DIRECTION_BALL_MIDPOINT_ROUTE_OBSTRUCTED"]
    assert not boundary["CURRENT_CENTER_GREEN_MIDPOINT_INTRINSIC_CURVATURE_GLOBAL_FINITE_ENCLOSURE_DERIVED"]
    assert not boundary["CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED"]


def test_midpoint_artifact_preserves_finite_prefix_and_failed_suffix():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    with np.load(ROOT / payload["data"]) as data:
        intrinsic = data["intrinsic_curvature_norm_upper"]
        incidence = data["incidence_curvature_norm_upper"]
        assert intrinsic.shape == incidence.shape == (370,)
        assert np.all(np.isfinite(intrinsic[:355]))
        assert np.all(~np.isfinite(intrinsic[355:]))
        assert np.all(np.isfinite(incidence))
        assert int(data["precision_bits"]) == 384


def test_512_bit_exact_axis_component_box_repeats_the_dependency_obstruction():
    payload = json.loads(HIGH_PRECISION_ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"]
    assert payload["componentwise_direction_ball_obstruction"][
        "nonfinite_intrinsic_intervals"
    ] == list(range(355, 370))
    boundary = payload["claim_boundary"]
    assert not boundary[
        "CURRENT_GREEN_EXACT_AXIS_NEIGHBORHOOD_LOCAL_HS_CURVATURE_DERIVED"
    ]
    assert not boundary[
        "CURRENT_GREEN_AXIS_NEIGHBORHOOD_MIXED_TRANSVERSE_BOUND_DERIVED"
    ]
    assert not boundary["CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED"]
    with np.load(ROOT / payload["data"]) as data:
        assert int(data["precision_bits"]) == 512
        assert data["local_hs_arb"].shape == (370, 99)
        assert np.all(np.isfinite(data["local_hs_residual_second_norm_upper"][:355]))
        assert np.all(~np.isfinite(data["local_hs_residual_second_norm_upper"][355:]))
