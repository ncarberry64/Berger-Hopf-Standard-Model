from __future__ import annotations

import math

import numpy as np
import pytest

from bhsm.interface.c2_finite_connection_residual import (
    assemble_c2_finite_connection_residual,
    fixed_event_child_reset_rows,
)


def test_fixed_event_child_reset_partition() -> None:
    rows = np.arange(57, dtype=float)
    child = fixed_event_child_reset_rows(rows)
    assert child.shape == (31,)
    assert np.array_equal(child, rows[26:])


def test_exact_linear_event_connection_has_zero_residual() -> None:
    # General mathematical witness for the assembly algebra.  All callbacks
    # occupy BHSM slots in production; this two-state model is not BHSM data.
    initial = np.asarray([0.0, 1.0])
    nodes = np.asarray([
        [0.0, 1.0],
        [0.5, 1.0],
        [1.0, 1.0],
    ])
    result = assemble_c2_finite_connection_residual(
        child_initial_state=initial,
        path_nodes=nodes,
        log_duration=0.0,
        reset_rows=lambda state: np.asarray([state[0]]),
        vector_field=lambda state: np.asarray([1.0, 0.0]),
        endpoint_function=lambda state: state[0] - 1.0,
        margin_functions={
            "positive_lapse": lambda state: state[1],
            "selected_line_gap": lambda state: 2.0 - state[0],
        },
        endpoint_kind="RETAINED_EVENT",
    )
    assert math.isclose(result.duration, 1.0)
    assert result.path_admissible is True
    assert np.linalg.norm(result.vector) == 0.0
    assert result.minimum_margins["positive_lapse"] == 1.0


def test_domain_margin_is_an_inequality_not_a_residual_penalty() -> None:
    nodes = np.asarray([[0.0], [1.0]])
    result = assemble_c2_finite_connection_residual(
        child_initial_state=np.asarray([0.0]),
        path_nodes=nodes,
        log_duration=0.0,
        reset_rows=lambda state: np.asarray([state[0]]),
        vector_field=lambda state: np.asarray([1.0]),
        endpoint_function=lambda state: state[0] - 1.0,
        margin_functions={"domain": lambda state: 0.5 - state[0]},
        endpoint_kind="CANONICAL_STOP",
    )
    assert np.linalg.norm(result.vector) == 0.0
    assert result.path_admissible is False
    assert result.minimum_margins["domain"] == -0.5


def test_rejects_unowned_endpoint_type_and_nonpositive_duration_overflow() -> None:
    kwargs = dict(
        child_initial_state=np.asarray([0.0]),
        path_nodes=np.asarray([[0.0], [1.0]]),
        reset_rows=lambda state: np.asarray([state[0]]),
        vector_field=lambda state: np.asarray([1.0]),
        endpoint_function=lambda state: state[0] - 1.0,
        margin_functions={"domain": lambda state: 1.0},
    )
    with pytest.raises(ValueError, match="endpoint kind"):
        assemble_c2_finite_connection_residual(
            **kwargs, log_duration=0.0, endpoint_kind="VALIDATION_CUTOFF"
        )
    with pytest.raises((OverflowError, ValueError)):
        assemble_c2_finite_connection_residual(
            **kwargs, log_duration=1000.0, endpoint_kind="RETAINED_EVENT"
        )
