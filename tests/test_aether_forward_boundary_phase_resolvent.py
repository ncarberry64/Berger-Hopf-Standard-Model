import math

import pytest

from bhsm.interface.aether_forward_boundary_phase_resolvent import (
    cayley_phase,
    compact_indicator_neumann_to_robin_difference,
    compact_indicator_resolvent_difference,
    half_line_reflection_coefficient,
    hs_weyl_spatial_supertrace_enclosure,
    phase_distance,
    robin_neumann_relative_heat_trace,
)


def test_cayley_phases_are_unitary_and_separated() -> None:
    assert cayley_phase(0.0) == 1.0 + 0.0j
    assert cayley_phase(1.0) == -1.0j
    assert abs(cayley_phase(2.0)) == pytest.approx(1.0)
    assert phase_distance(0.0, 1.0) == pytest.approx(math.sqrt(2.0))


def test_compact_source_resolvent_difference_exact() -> None:
    expected = -(1.0 - math.exp(-1.0)) ** 2 / 2.0
    direct = compact_indicator_resolvent_difference(1.0, 1.0, 0.0, 1.0)
    closed = compact_indicator_neumann_to_robin_difference(1.0, 1.0, 1.0)
    assert half_line_reflection_coefficient(1.0, 0.0) == 1.0
    assert half_line_reflection_coefficient(1.0, 1.0) == 0.0
    assert direct == pytest.approx(expected)
    assert closed == pytest.approx(expected)


def test_graded_relative_heat_factors_are_strictly_nonzero() -> None:
    temporal = robin_neumann_relative_heat_trace(1.0, 1.0)
    spatial = hs_weyl_spatial_supertrace_enclosure(1.0, cutoff=20)
    assert temporal == pytest.approx(-0.2862082119220965)
    assert spatial["graded_upper"] < -8.9
    assert spatial["absolute_tail_upper"] < 1.0e-150
    assert temporal * spatial["graded_upper"] > 2.5


@pytest.mark.parametrize(
    "arguments",
    [(-1.0, 1.0, 0.0, 1.0), (1.0, 0.0, 0.0, 1.0)],
)
def test_invalid_resolvent_inputs_rejected(arguments: tuple[float, ...]) -> None:
    with pytest.raises(ValueError):
        compact_indicator_resolvent_difference(*arguments)
