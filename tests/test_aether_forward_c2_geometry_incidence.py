import numpy as np

from bhsm.interface.aether_forward_boundary_radius import (
    boundary_log_lapse,
    boundary_log_radius,
)
from bhsm.interface.aether_forward_c2_geometry_incidence import (
    boundary_geometry_action_covectors,
    proper_duration_density_and_action_covector,
)


def test_boundary_geometry_action_covectors_match_directional_differences() -> None:
    rng = np.random.default_rng(7122301)
    state = 0.03 * rng.normal(size=98)
    weights = np.exp(0.1 * rng.normal(size=98))
    direction = rng.normal(size=98)
    result = boundary_geometry_action_covectors(state=state, weights=weights)
    epsilon = 1.0e-6

    def values(a: float) -> tuple[float, float]:
        shifted = state + a * direction / weights
        return (
            boundary_log_radius(12, shifted[:37]),
            boundary_log_lapse(12, shifted[74:]),
        )

    plus = values(epsilon)
    minus = values(-epsilon)
    radius_fd = (plus[0] - minus[0]) / (2.0 * epsilon)
    lapse_fd = (plus[1] - minus[1]) / (2.0 * epsilon)
    assert abs(result["D_log_R4_action_dual"] @ direction - radius_fd) < 2.0e-10
    assert abs(result["D_log_lapse_action_dual"] @ direction - lapse_fd) < 2.0e-10


def test_duration_density_covector_includes_signed_Delta_term() -> None:
    rng = np.random.default_rng(7122302)
    state = 0.02 * rng.normal(size=98)
    weights = np.exp(0.05 * rng.normal(size=98))
    d_delta = rng.normal(size=98)
    direction = rng.normal(size=98)
    delta = 0.7
    descriptor = 0.04
    result = proper_duration_density_and_action_covector(
        state=state,
        weights=weights,
        signed_descriptor=descriptor,
        Delta=delta,
        D_Delta_action_dual=d_delta,
    )
    epsilon = 1.0e-6

    def density(a: float) -> float:
        shifted = state + a * direction / weights
        shifted_delta = delta + a * float(d_delta @ direction)
        return np.exp(boundary_log_lapse(12, shifted[74:])) * descriptor / shifted_delta

    finite = (density(epsilon) - density(-epsilon)) / (2.0 * epsilon)
    analytic = result["D_proper_duration_density_action_dual"] @ direction
    assert abs(analytic - finite) < 1.0e-9
