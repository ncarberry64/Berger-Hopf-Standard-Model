from __future__ import annotations

import numpy as np
from scipy.optimize import brentq
from scipy.interpolate import CubicSpline, PchipInterpolator

from bhsm.interface.aether_cancelled_arc_proper_time_pullback import (
    cancelled_arc_proper_time_density_first_jet,
    pullback_cancelled_arc_history_to_proper_time,
)


def test_moving_duration_chain_rule_matches_centered_reparameterization() -> None:
    arc = np.linspace(0.0, 1.0, 33)
    x = 0.1 + arc**2
    x_first = np.column_stack((0.3 * arc, -0.2 + 0.05 * arc**2))
    density = 2.0 + arc
    density_first = np.column_stack((
        np.full(arc.size, 0.2),
        -0.1 * arc,
    ))
    result = pullback_cancelled_arc_history_to_proper_time(
        arc_nodes=arc,
        log_radius=x,
        log_radius_arc_first_jet=x_first,
        proper_time_density=density,
        proper_time_density_first_jet=density_first,
    )
    normalized = result["normalized_proper_times"]
    epsilon = 2.0e-6
    for direction in range(2):
        samples = []
        for sign in (-1.0, 1.0):
            varied_density = density + sign * epsilon * density_first[:, direction]
            density_spline = PchipInterpolator(arc, varied_density)
            primitive = density_spline.antiderivative()
            total = float(primitive(arc[-1]) - primitive(arc[0]))
            varied_x = CubicSpline(
                arc, x + sign * epsilon * x_first[:, direction],
            )
            values = []
            for unit in normalized:
                if unit == 0.0:
                    theta = arc[0]
                elif unit == 1.0:
                    theta = arc[-1]
                else:
                    target = unit * total
                    theta = brentq(
                        lambda value: float(
                            primitive(value) - primitive(arc[0]) - target
                        ),
                        arc[0],
                        arc[-1],
                    )
                values.append(float(varied_x(theta)))
            samples.append(np.asarray(values))
        finite = (samples[1] - samples[0]) / (2.0 * epsilon)
        assert np.max(np.abs(
            finite
            - result["log_radius_normalized_proper_time_first_jet"][:, direction]
        )) < 2.0e-8
    assert abs(result["proper_duration"] - 2.5) < 1.0e-13
    assert np.allclose(result["proper_duration_first_jet"], [0.2, -0.05])
    assert result["arc_parameter_not_identified_with_proper_time"] is True


def test_preterminal_density_must_be_positive() -> None:
    arc = np.asarray([0.0, 0.5, 1.0])
    try:
        pullback_cancelled_arc_history_to_proper_time(
            arc_nodes=arc,
            log_radius=np.zeros(3),
            log_radius_arc_first_jet=np.zeros((3, 1)),
            proper_time_density=np.asarray([1.0, 0.0, 0.0]),
            proper_time_density_first_jet=np.zeros((3, 1)),
        )
    except ValueError:
        pass
    else:
        raise AssertionError("zero preterminal proper-time density must fail")


def test_density_first_jet_is_regular_at_zero_descriptor() -> None:
    log_lapse = np.asarray([0.1, -0.2])
    descriptor = np.asarray([0.4, 0.0])
    norm = np.asarray([2.0, 3.0])
    lapse_first = np.asarray([[0.2, -0.1], [0.3, 0.4]])
    descriptor_first = np.asarray([[0.05, -0.02], [0.07, -0.03]])
    norm_first = np.asarray([[0.1, -0.2], [0.6, 0.8]])
    result = cancelled_arc_proper_time_density_first_jet(
        log_boundary_lapse=log_lapse,
        signed_descriptor=descriptor,
        cancelled_field_action_norm=norm,
        log_boundary_lapse_first_jet=lapse_first,
        signed_descriptor_first_jet=descriptor_first,
        cancelled_field_action_norm_first_jet=norm_first,
    )
    epsilon = 1.0e-6
    for direction in range(2):
        values = []
        for sign in (-1.0, 1.0):
            values.append(
                np.exp(log_lapse + sign * epsilon * lapse_first[:, direction])
                * (descriptor + sign * epsilon * descriptor_first[:, direction])
                / (norm + sign * epsilon * norm_first[:, direction])
            )
        finite = (values[1] - values[0]) / (2.0 * epsilon)
        assert np.max(np.abs(
            finite - result["proper_time_density_first_jet"][:, direction]
        )) < 5.0e-11
    expected_terminal = np.exp(log_lapse[-1]) * descriptor_first[-1] / norm[-1]
    assert np.allclose(result["proper_time_density_first_jet"][-1], expected_terminal)
