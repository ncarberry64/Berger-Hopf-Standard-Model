from __future__ import annotations

import numpy as np
from scipy.optimize import brentq
from scipy.interpolate import CubicSpline

from bhsm.interface.aether_cancelled_arc_proper_time_pullback import (
    assemble_cancelled_arc_proper_time_coefficient_first_jet,
    cancelled_arc_proper_time_density_first_jet,
    pullback_cancelled_arc_history_to_proper_time,
)
from bhsm.interface.aether_forward_c2_geometry_incidence import (
    boundary_geometry_action_covectors,
)


def test_moving_duration_chain_rule_matches_centered_reparameterization() -> None:
    arc = np.linspace(0.0, 1.0, 33)
    x = 0.1 + arc**2
    x_first = np.column_stack((0.3 * arc, -0.2 + 0.05 * arc**2))
    density = 2.0 + arc + 0.1 * arc**2
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
            widths = np.diff(arc)
            cumulative = np.concatenate((
                np.zeros(1),
                np.cumsum(
                    0.5 * widths * (varied_density[:-1] + varied_density[1:])
                ),
            ))

            def primitive(value: float) -> float:
                if value <= arc[0]:
                    return 0.0
                if value >= arc[-1]:
                    return float(cumulative[-1])
                index = int(np.searchsorted(arc, value, side="right") - 1)
                local = value - arc[index]
                slope = (
                    varied_density[index + 1] - varied_density[index]
                ) / widths[index]
                return float(
                    cumulative[index]
                    + varied_density[index] * local
                    + 0.5 * slope * local * local
                )

            total = primitive(arc[-1])
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
                        lambda value: primitive(value) - target,
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
    assert abs(result["proper_duration"] - np.trapezoid(density, arc)) < 1.0e-13
    assert np.allclose(
        result["proper_duration_first_jet"],
        np.trapezoid(density_first, arc, axis=0),
    )
    assert result["density_interpolation"] == (
        "POSITIVE_PIECEWISE_LINEAR_WITH_EXACT_LINEAR_FIRST_JET"
    )
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


def test_geometry_and_norm_first_jets_are_composed_in_action_coordinates() -> None:
    rng = np.random.default_rng(7123001)
    arc = np.linspace(0.0, 1.0, 9)
    states = 0.015 * rng.normal(size=(arc.size, 98))
    weights = np.exp(0.05 * rng.normal(size=98))
    state_first = 0.02 * rng.normal(size=(arc.size, 98, 3))
    descriptor = 0.2 * (1.0 - arc)
    descriptor_first = 0.01 * rng.normal(size=(arc.size, 3))
    norm = 1.5 + 0.1 * arc
    norm_state_gradient = 0.03 * rng.normal(size=(arc.size, 98))
    norm_descriptor_derivative = 0.02 * rng.normal(size=arc.size)

    result = assemble_cancelled_arc_proper_time_coefficient_first_jet(
        arc_nodes=arc,
        states=states,
        state_action_first_jet=state_first,
        state_weights=weights,
        signed_descriptor=descriptor,
        signed_descriptor_first_jet=descriptor_first,
        cancelled_field_action_norm=norm,
        cancelled_norm_state_gradient_action=norm_state_gradient,
        cancelled_norm_descriptor_derivative=norm_descriptor_derivative,
    )

    epsilon = 1.0e-6
    for node in range(arc.size):
        geometry = boundary_geometry_action_covectors(
            state=states[node], weights=weights,
        )
        for direction in range(3):
            shifted = state_first[node, :, direction] / weights
            plus = boundary_geometry_action_covectors(
                state=states[node] + epsilon * shifted,
                weights=weights,
            )
            minus = boundary_geometry_action_covectors(
                state=states[node] - epsilon * shifted,
                weights=weights,
            )
            radius_finite = (plus["log_R4"] - minus["log_R4"]) / (2.0 * epsilon)
            lapse_finite = (plus["log_lapse"] - minus["log_lapse"]) / (2.0 * epsilon)
            assert abs(
                radius_finite
                - result["log_radius_arc_first_jet"][node, direction]
            ) < 2.0e-9
            assert abs(
                lapse_finite
                - result["log_boundary_lapse_arc_first_jet"][node, direction]
            ) < 2.0e-10
        assert np.isclose(
            result["log_boundary_lapse"][node], geometry["log_lapse"],
        )

    expected_norm_first = (
        np.einsum("ni,nij->nj", norm_state_gradient, state_first)
        + norm_descriptor_derivative[:, None] * descriptor_first
    )
    assert np.allclose(
        result["cancelled_field_action_norm_first_jet"], expected_norm_first,
    )
    terminal_expected = (
        np.exp(result["log_boundary_lapse"][-1])
        * descriptor_first[-1]
        / norm[-1]
    )
    assert np.allclose(result["proper_time_density_first_jet"][-1], terminal_expected)
    assert result["proper_duration"] > 0.0
