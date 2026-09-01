import json

import numpy as np

from scripts.derive_n12_gate7_c2_finite_core_zeta_reset_cotangent_enclosure import (
    DATA_RESULT,
    RESULT,
    build_payload,
)


def test_c2_finite_core_zeta_reset_cotangent_ball_is_certified() -> None:
    payload, arrays = build_payload()
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"][
        "C2_finite_core_zeta_reset_cotangent_norm_ball"
    ] == "CERTIFIED"
    enclosure = payload["enclosure"]
    assert 0.0 < enclosure["node_radius_contribution_upper"]
    assert 0.0 < enclosure["moving_duration_contribution_upper"]
    assert enclosure["total_C2_zeta_reset_cotangent_radius_upper"] > (
        enclosure["moving_duration_contribution_upper"]
    )
    assert enclosure["duration_fraction"] > 0.999999999
    assert arrays["C2_zeta_reset_cotangent_ball_center"].shape == (98,)
    assert payload["theorem"]["transition_matrix_constructed_or_inverted"] is False


def test_zeta_reset_ball_does_not_promote_a_signed_force_or_heat_contraction() -> None:
    payload, _ = build_payload()
    assert payload["claim_boundary"]["signed_C2_zeta_reset_cotangent_value"] == "OPEN"
    assert payload["claim_boundary"]["full_finite_core_heat_minus_zeta_force"] == "OPEN"
    assert payload["matching_audit"]["full_graded_heat_non_scale_contraction"].startswith(
        "OPEN"
    )
    assert payload["matching_audit"]["incoming_formation_zeta_pullback"].startswith(
        "OPEN"
    )


def test_zeta_reset_ball_artifact_and_arrays_replay() -> None:
    payload, arrays = build_payload()
    stored = json.loads(RESULT.read_text(encoding="utf-8"))
    assert stored["status"] == payload["status"]
    with np.load(DATA_RESULT) as data:
        assert set(data.files) == set(arrays)
        for name, expected in arrays.items():
            np.testing.assert_array_equal(data[name], expected)
