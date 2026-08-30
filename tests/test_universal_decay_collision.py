import math

from bhsm.interface.universal_decay_collision import (
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
