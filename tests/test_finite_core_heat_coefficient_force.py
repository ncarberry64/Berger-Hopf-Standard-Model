"""Check the effective-action derivative, including the moving mass form."""
import numpy as np
import pytest
import math

from bhsm.interface.finite_core_heat_coefficient_force import finite_core_heat_coefficient_cotangent


@pytest.mark.parametrize("channel,value,chirality", [("scalar", 4.0, 1), ("product_Dirac", 1.5, 1), ("product_Dirac", 1.5, -1)])
def test_combined_coefficient_direction(channel, value, chirality):
    x = np.asarray([0.0, 0.03, -0.04, 0.01, 0.02])
    h = np.asarray([0.17, 0.21, 0.18, 0.23])
    dx = np.asarray([0.2, -0.1, 0.05, 0.3, -0.15])
    dh = np.asarray([0.07, -0.04, 0.03, -0.02])
    def evaluate(radius, duration):
        return finite_core_heat_coefficient_cotangent(log_radii=radius, proper_durations=duration,
            channel=channel, unit_channel_value=value, chirality=chirality, heat_length=0.1)
    base = evaluate(x, h)
    analytic = base["D_log_R4_Gamma_heat"] @ dx + base["D_proper_duration_Gamma_heat"] @ dh
    epsilon = 2e-5
    finite = (evaluate(x + epsilon * dx, h + epsilon * dh)["Gamma_heat"]
              - evaluate(x - epsilon * dx, h - epsilon * dh)["Gamma_heat"]) / (2 * epsilon)
    assert finite == pytest.approx(analytic, rel=2e-8, abs=2e-9)
    assert base["numerical_residuals"]["scaled_common_scale_Ward_relative"] < 1e-12


def test_small_heat_force_keeps_scaled_cotangent():
    result = finite_core_heat_coefficient_cotangent(log_radii=np.zeros(5),
        proper_durations=np.full(4, 1e-5), channel="product_Dirac", unit_channel_value=1.5)
    assert result["binary64_cotangent_underflow"]
    assert result["log_absolute_Gamma_heat"] < -1e8
    assert np.linalg.norm(result["scaled_D_proper_duration_Gamma_heat"]) > 0
    assert np.all(np.isfinite(result["scaled_D_log_R4_Gamma_heat"]))


def test_force_can_be_representable_when_common_seed_underflows():
    duration = math.sqrt(3.0 / 740.0)
    result = finite_core_heat_coefficient_cotangent(log_radii=np.zeros(2),
        proper_durations=np.asarray([duration]), channel="scalar", unit_channel_value=0.0)
    assert result["cotangent_common_factor_underflows_binary64"]
    expected = -math.exp(-740.0 - math.log(duration))
    assert result["D_proper_duration_Gamma_heat"][0] == pytest.approx(expected, rel=0.01, abs=0)
    assert not result["binary64_cotangent_underflow"]
