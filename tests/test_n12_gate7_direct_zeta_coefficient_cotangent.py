import json

import numpy as np

from bhsm.interface.forward_finite_endpoint_heat_force import (
    piecewise_linear_zeta_coefficient_cotangent,
)
from scripts.derive_n12_gate7_direct_zeta_coefficient_cotangent import (
    DATA_RESULT,
    RESULT,
    build_payload,
)


def test_piecewise_linear_zeta_cotangent_matches_finite_differences() -> None:
    x = np.asarray([-0.3, 0.2, 0.20000001, 0.8], dtype=float)
    h = np.asarray([0.7, 0.2, 1.1], dtype=float)
    result = piecewise_linear_zeta_coefficient_cotangent(x, h)
    step = 2.0e-7

    def value(x_arg: np.ndarray, h_arg: np.ndarray) -> float:
        return float(
            piecewise_linear_zeta_coefficient_cotangent(x_arg, h_arg)[
                "Gamma_SM_zeta"
            ]
        )

    finite_x = np.zeros_like(x)
    for index in range(x.size):
        delta = np.zeros_like(x)
        delta[index] = step
        finite_x[index] = (value(x + delta, h) - value(x - delta, h)) / (2.0 * step)
    finite_h = np.zeros_like(h)
    for index in range(h.size):
        delta = np.zeros_like(h)
        delta[index] = step
        finite_h[index] = (value(x, h + delta) - value(x, h - delta)) / (2.0 * step)

    np.testing.assert_allclose(
        result["D_log_R4_Gamma_SM_zeta"], finite_x, rtol=2.0e-8, atol=2.0e-9
    )
    np.testing.assert_allclose(
        result["D_proper_duration_Gamma_SM_zeta"],
        finite_h,
        rtol=2.0e-9,
        atol=2.0e-9,
    )


def test_equal_radius_series_and_common_scale_identity() -> None:
    x = np.full(4, -0.125, dtype=float)
    h = np.asarray([0.25, 0.5, 0.75], dtype=float)
    coefficient = 59.0 / 30.0
    scale = np.exp(-x[0])
    result = piecewise_linear_zeta_coefficient_cotangent(x, h)
    expected_x = coefficient * scale * np.asarray(
        [0.5 * h[0], 0.5 * (h[0] + h[1]), 0.5 * (h[1] + h[2]), 0.5 * h[2]]
    )
    expected_h = np.full(3, -coefficient * scale)
    np.testing.assert_allclose(result["D_log_R4_Gamma_SM_zeta"], expected_x)
    np.testing.assert_allclose(result["D_proper_duration_Gamma_SM_zeta"], expected_h)
    assert abs(result["common_scale_zeta_force_residual"]) < 1.0e-14


def test_direct_zeta_family_artifact_replays_without_promoting_force() -> None:
    payload, arrays = build_payload()
    stored = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"][
        "direct_zeta_finite_core_coefficient_cotangent"
    ] == "CERTIFIED"
    assert payload["claim_boundary"]["full_heat_minus_zeta_signed_reverse_value"] == "OPEN"
    assert payload["C2_family_enclosure"]["all_node_components_strictly_positive"] is True
    assert payload["C2_family_enclosure"]["all_duration_components_strictly_negative"] is True
    assert stored["status"] == payload["status"]
    with np.load(DATA_RESULT) as data:
        assert set(data.files) == set(arrays)
        for name, expected in arrays.items():
            np.testing.assert_array_equal(data[name], expected)
