import numpy as np
import pytest

from bhsm.interface.aether_forward_e1_high_energy import (
    e1_high_energy_trace_norm_bound,
    factorized_heat_sandwich_trace_norm_bound,
    finite_matrix_e1_high_energy_witness,
)


def test_trace_norm_and_factorized_bounds() -> None:
    assert e1_high_energy_trace_norm_bound(6.0) == 6.0
    assert e1_high_energy_trace_norm_bound(6.0, 2.0) == 3.0
    assert factorized_heat_sandwich_trace_norm_bound(2.0, 3.0) == 12.0


def test_finite_matrix_tail_is_bounded_with_noncommuting_vertex() -> None:
    operator = np.array([[2.0, -1.0], [-1.0, 3.0]])
    source = np.array([[1.0, 0.75], [0.75, -2.0]])
    result = finite_matrix_e1_high_energy_witness(operator, source)
    assert result["actual_weighted_tail"] > 0.0
    assert result["heat_sandwiched_trace_norm"] > 0.0
    assert result["bound_residual"] >= -1.0e-14


@pytest.mark.parametrize("bad", [-1.0, np.inf, np.nan])
def test_trace_norm_inputs_fail_closed(bad: float) -> None:
    with pytest.raises(ValueError):
        e1_high_energy_trace_norm_bound(bad)
    with pytest.raises(ValueError):
        factorized_heat_sandwich_trace_norm_bound(bad, 1.0)
