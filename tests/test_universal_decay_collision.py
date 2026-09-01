import math

import numpy as np

from bhsm.interface.universal_decay_collision import (
    combine_decay_channels,
    integrate_two_to_two_cross_section,
    kallen,
    multi_body_decay_width,
    three_body_decay_width,
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


def test_massless_constant_three_body_decay_matches_exact_phase_space() -> None:
    parent_mass = 2.0
    amplitude_squared = 3.0
    result = three_body_decay_width(
        parent_mass,
        (0.0, 0.0, 0.0),
        lambda _s12, _cosine: amplitude_squared,
        invariant_quadrature_order=24,
        angular_quadrature_order=12,
    )
    expected = amplitude_squared * parent_mass / (512.0 * math.pi**3)
    assert result.open_channel is True
    assert result.s12_lower == 0.0
    assert result.s12_upper == parent_mass**2
    assert np.isclose(result.width, expected, rtol=2.0e-14)


def test_three_body_decay_integrates_helicity_angle_and_joins_ledger() -> None:
    three_body = three_body_decay_width(
        1.0,
        (0.0, 0.0, 0.0),
        lambda _s12, cosine: 2.0 * (1.0 + cosine**2),
        invariant_quadrature_order=24,
        angular_quadrature_order=16,
    )
    expected = 1.0 / (192.0 * math.pi**3)
    assert np.isclose(three_body.width, expected, rtol=2.0e-14)
    two_body = two_body_decay_width(1.0, 0.0, 0.0, 1.0)
    ledger = combine_decay_channels((
        ("two-body", two_body),
        ("three-body", three_body),
    ))
    assert np.isclose(
        ledger.total_width,
        two_body.width + three_body.width,
    )


def test_three_body_threshold_and_invalid_amplitude_fail_closed() -> None:
    closed = three_body_decay_width(
        1.0,
        (0.4, 0.4, 0.4),
        lambda _s12, _cosine: 1.0,
    )
    assert closed.open_channel is False
    assert closed.width == 0.0
    with np.testing.assert_raises_regex(ValueError, "finite and nonnegative"):
        three_body_decay_width(
            2.0,
            (0.0, 0.0, 0.0),
            lambda _s12, _cosine: -1.0,
        )


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


def test_recursive_massless_four_body_phase_space_matches_exact_volume() -> None:
    parent_mass = 2.0
    amplitude_squared = 3.0
    result = multi_body_decay_width(
        parent_mass,
        (0.0, 0.0, 0.0, 0.0),
        lambda _momenta: amplitude_squared,
        invariant_quadrature_order=8,
        angular_quadrature_order=2,
        azimuthal_quadrature_order=2,
    )
    expected = amplitude_squared * parent_mass**3 / (49152.0 * math.pi**5)
    assert result.open_channel is True
    assert result.daughter_count == 4
    assert result.amplitude_evaluations > 0
    assert np.isclose(result.width, expected, rtol=3.0e-14)


def test_recursive_phase_space_reconstructs_on_shell_conserved_momenta() -> None:
    daughter_masses = (0.2, 0.3, 0.4, 0.5)
    parent = np.asarray((2.0, 0.0, 0.0, 0.0))
    maximum_residual = 0.0

    def amplitude(momenta: tuple[np.ndarray, ...]) -> float:
        nonlocal maximum_residual
        total = np.sum(momenta, axis=0)
        residuals = [np.max(np.abs(total - parent))]
        residuals.extend(
            abs(momentum[0] ** 2 - momentum[1:] @ momentum[1:] - mass**2)
            for momentum, mass in zip(momenta, daughter_masses)
        )
        maximum_residual = max(maximum_residual, *residuals)
        return 1.0 + 0.1 * abs(float(momenta[0][1]))

    result = multi_body_decay_width(
        parent[0],
        daughter_masses,
        amplitude,
        invariant_quadrature_order=3,
        angular_quadrature_order=2,
        azimuthal_quadrature_order=3,
    )
    assert result.open_channel is True
    assert result.width > 0.0
    assert maximum_residual < 2.0e-14


def test_recursive_multi_body_threshold_and_amplitude_validation() -> None:
    closed = multi_body_decay_width(
        1.0,
        (0.3, 0.3, 0.3, 0.3),
        lambda _momenta: 1.0,
    )
    assert closed.open_channel is False
    assert closed.width == 0.0
    with np.testing.assert_raises_regex(ValueError, "finite and nonnegative"):
        multi_body_decay_width(
            2.0,
            (0.0, 0.0),
            lambda _momenta: -1.0,
            angular_quadrature_order=2,
            azimuthal_quadrature_order=2,
        )
