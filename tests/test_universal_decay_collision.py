import math

import numpy as np

from bhsm.interface.universal_decay_collision import (
    combine_decay_channels,
    integrate_two_to_two_cross_section,
    kallen,
    two_body_decay_width,
    two_to_two_differential_cross_section,
)


def test_kallen_and_massless_two_body_decay() -> None:
    assert kallen(4.0, 1.0, 1.0) == 0.0
    result = two_body_decay_width(2.0, 0.0, 0.0, 3.0)
    assert result.open_channel is True
    assert result.momentum == 1.0
    assert math.isclose(result.width, 3.0 / (32.0 * math.pi))


def test_closed_decay_channel_has_zero_width() -> None:
    result = two_body_decay_width(1.0, 0.6, 0.6, 10.0)
    assert result.open_channel is False
    assert result.width == 0.0


def test_massless_two_to_two_cross_section() -> None:
    result = two_to_two_differential_cross_section(
        100.0, (0.0, 0.0), (0.0, 0.0), 5.0,
    )
    assert result.open_channel is True
    assert result.incoming_momentum == 5.0
    assert result.outgoing_momentum == 5.0
    assert math.isclose(
        result.differential_cross_section_domega,
        5.0 / (64.0 * math.pi**2 * 100.0),
    )


def test_decay_ledger_produces_branching_fractions_and_inverse_width() -> None:
    first = two_body_decay_width(5.0, 1.0, 1.0, 2.0)
    second = two_body_decay_width(5.0, 1.0, 1.0, 6.0)
    result = combine_decay_channels((("first", first), ("second", second)))
    assert np.isclose(result.branching_fractions["first"], 0.25)
    assert np.isclose(result.branching_fractions["second"], 0.75)
    assert np.isclose(result.inverse_width_lifetime, 1.0 / result.total_width)


def test_total_cross_section_integrates_azimuth_symmetric_angular_amplitude() -> None:
    s = 100.0
    amplitude = lambda cosine: 3.0 * (1.0 + cosine**2)
    result = integrate_two_to_two_cross_section(
        s,
        (0.0, 0.0),
        (0.0, 0.0),
        amplitude,
        quadrature_order=12,
    )
    expected = 3.0 * (2.0 + 2.0 / 3.0) * 2.0 * np.pi / (64.0 * np.pi**2 * s)
    assert result.open_channel is True
    assert np.isclose(result.total_cross_section, expected, rtol=2.0e-14)
