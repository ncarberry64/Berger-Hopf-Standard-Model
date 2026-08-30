from __future__ import annotations

import numpy as np
import pytest

from bhsm.interface.aether_cancelled_arc_proper_time_pullback import (
    assemble_cancelled_arc_proper_time_coefficient_first_jet,
)
from bhsm.interface.aether_forward_history_weyl_first_jet import (
    integrate_cancelled_arc_history_weyl_first_jet,
    integrate_history_weyl_first_jet,
)


@pytest.mark.parametrize(
    ("channel", "unit_value", "chirality"),
    [("scalar", 3.0, 1), ("product_dirac", 1.5, -1)],
)
def test_history_weyl_first_jet_matches_centered_difference(
    channel: str, unit_value: float, chirality: int,
) -> None:
    times = np.linspace(0.0, 1.0, 9)
    base = 0.03 * np.sin(1.3 * times) - 0.01 * times
    directions = np.column_stack((
        0.2 + 0.04 * times,
        -0.1 * np.cos(0.7 * times),
        0.03 * times**2,
    ))
    duration = 0.8
    duration_first = np.asarray([0.07, -0.03, 0.02])
    result = integrate_history_weyl_first_jet(
        normalized_times=times,
        log_radius=base,
        log_radius_first_jet=directions,
        proper_duration=duration,
        proper_duration_first_jet=duration_first,
        channel=channel,  # type: ignore[arg-type]
        unit_channel_value=unit_value,
        spectral_parameter=-1.0,
        chirality=chirality,
        maximum_step=0.025,
        relative_tolerance=2.0e-12,
        absolute_tolerance=2.0e-14,
    )
    epsilon = 2.0e-6
    for index in range(3):
        varied = []
        for sign in (-1.0, 1.0):
            current = integrate_history_weyl_first_jet(
                normalized_times=times,
                log_radius=base + sign * epsilon * directions[:, index],
                log_radius_first_jet=np.zeros((times.size, 0)),
                proper_duration=duration + sign * epsilon * duration_first[index],
                proper_duration_first_jet=np.zeros(0),
                channel=channel,  # type: ignore[arg-type]
                unit_channel_value=unit_value,
                spectral_parameter=-1.0,
                chirality=chirality,
                maximum_step=0.025,
                relative_tolerance=2.0e-12,
                absolute_tolerance=2.0e-14,
            )["weyl"]
            varied.append(current)
        finite = (varied[1] - varied[0]) / (2.0 * epsilon)
        assert np.linalg.norm(finite - result["weyl_first_jet"][index]) < 2.0e-8
    assert result["parameter_count"] == 3
    assert result["weyl_Hermitian_residual"] < 2.0e-10
    assert result["propagation_representation"] == "TWO_SIDED_RICCATI_PLUS_LOG_TRANSFER_B"
    assert result["explicit_matrix_inverse_formed"] is False
    assert result["endpoint_condition_imposed"] is False


def test_history_input_shape_guard() -> None:
    with pytest.raises(ValueError):
        integrate_history_weyl_first_jet(
            normalized_times=np.asarray([0.0, 1.0]),
            log_radius=np.asarray([0.0, 0.0]),
            log_radius_first_jet=np.zeros((2, 2)),
            proper_duration=1.0,
            proper_duration_first_jet=np.zeros(3),
            channel="scalar",
            unit_channel_value=1.0,
            spectral_parameter=-1.0,
        )


def test_long_hyperbolic_scalar_interval_stays_in_riccati_chart() -> None:
    times = np.linspace(0.0, 1.0, 17)
    duration = 92.0
    result = integrate_history_weyl_first_jet(
        normalized_times=times,
        log_radius=np.zeros(times.size),
        log_radius_first_jet=np.zeros((times.size, 0)),
        proper_duration=duration,
        proper_duration_first_jet=np.zeros(0),
        channel="scalar",
        unit_channel_value=3.0,
        spectral_parameter=-1.0,
        maximum_step=0.01,
    )
    rate = 2.0
    expected = np.asarray(
        [
            [rate / np.tanh(rate * duration), -rate / np.sinh(rate * duration)],
            [-rate / np.sinh(rate * duration), rate / np.tanh(rate * duration)],
        ]
    )
    assert np.linalg.norm(result["weyl"] - expected, ord=2) < 2.0e-11
    assert result["transfer_b_chart_margin"] > 1.0e70
    assert result["weyl_Hermitian_residual"] == 0.0


def test_short_physical_interval_is_not_rejected_by_absolute_b_cutoff() -> None:
    times = np.linspace(0.0, 1.0, 9)
    duration = 1.5e-27
    radius_first = np.full((times.size, 1), 0.1)
    duration_first = np.asarray([0.2 * duration])
    result = integrate_history_weyl_first_jet(
        normalized_times=times,
        log_radius=np.zeros(times.size),
        log_radius_first_jet=radius_first,
        proper_duration=duration,
        proper_duration_first_jet=duration_first,
        channel="scalar",
        unit_channel_value=3.0,
        spectral_parameter=-1.0,
        maximum_step=0.02,
    )
    rate = 2.0
    expected = np.asarray(
        [
            [rate / np.tanh(rate * duration), -rate / np.sinh(rate * duration)],
            [-rate / np.sinh(rate * duration), rate / np.tanh(rate * duration)],
        ]
    )
    relative = np.linalg.norm(result["weyl"] - expected, ord=2) / np.linalg.norm(
        expected, ord=2,
    )
    assert relative < 2.0e-12
    assert result["transfer_b_chart_margin"] < 1.0e-14
    assert result["transfer_b_above_requested_absolute_tolerance"] is False
    assert result["absolute_chart_tolerance_used_for_rejection"] is False
    epsilon = 2.0e-6
    varied = [
        integrate_history_weyl_first_jet(
            normalized_times=times,
            log_radius=sign * epsilon * radius_first[:, 0],
            log_radius_first_jet=np.zeros((times.size, 0)),
            proper_duration=duration + sign * epsilon * duration_first[0],
            proper_duration_first_jet=np.zeros(0),
            channel="scalar",
            unit_channel_value=3.0,
            spectral_parameter=-1.0,
            maximum_step=0.02,
        )["weyl"]
        for sign in (-1.0, 1.0)
    ]
    finite = (varied[1] - varied[0]) / (2.0 * epsilon)
    first_relative = np.linalg.norm(
        finite - result["weyl_first_jet"][0], ord=2,
    ) / np.linalg.norm(finite, ord=2)
    assert first_relative < 2.0e-7


def test_cancelled_arc_composition_matches_explicit_pullback_then_weyl() -> None:
    rng = np.random.default_rng(7123002)
    arc = np.linspace(0.0, 1.0, 7)
    states = 0.01 * rng.normal(size=(arc.size, 98))
    state_first = 0.015 * rng.normal(size=(arc.size, 98, 2))
    weights = np.exp(0.03 * rng.normal(size=98))
    descriptor = 0.3 * (1.0 - arc)
    descriptor_first = 0.01 * rng.normal(size=(arc.size, 2))
    norm = 1.2 + 0.05 * arc
    norm_state = 0.02 * rng.normal(size=(arc.size, 98))
    norm_descriptor = 0.01 * rng.normal(size=arc.size)
    inputs = {
        "arc_nodes": arc,
        "states": states,
        "state_action_first_jet": state_first,
        "state_weights": weights,
        "signed_descriptor": descriptor,
        "signed_descriptor_first_jet": descriptor_first,
        "cancelled_field_action_norm": norm,
        "cancelled_norm_state_gradient_action": norm_state,
        "cancelled_norm_descriptor_derivative": norm_descriptor,
    }
    pullback = assemble_cancelled_arc_proper_time_coefficient_first_jet(**inputs)
    direct = integrate_history_weyl_first_jet(
        normalized_times=pullback["normalized_proper_times"],
        log_radius=pullback["log_radius"],
        log_radius_first_jet=pullback[
            "log_radius_normalized_proper_time_first_jet"
        ],
        proper_duration=pullback["proper_duration"],
        proper_duration_first_jet=pullback["proper_duration_first_jet"],
        channel="product_dirac",
        unit_channel_value=1.5,
        spectral_parameter=-1.0,
        chirality=1,
        maximum_step=0.02,
    )
    composed = integrate_cancelled_arc_history_weyl_first_jet(
        **inputs,
        channel="product_dirac",
        unit_channel_value=1.5,
        spectral_parameter=-1.0,
        chirality=1,
        maximum_step=0.02,
    )
    assert np.array_equal(composed["weyl"], direct["weyl"])
    assert np.array_equal(composed["weyl_first_jet"], direct["weyl_first_jet"])
    assert composed["cancelled_arc_composed_without_time_relabeling"] is True
    assert composed["proper_time_pullback"]["arc_parameter_not_identified_with_proper_time"] is True
