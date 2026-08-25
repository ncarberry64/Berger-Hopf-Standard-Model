"""Inverse-free residual assembly for a finite C2 event/stop connection.

This module supplies only the general residual algebra.  The reset rows,
Euler--Dirac vector field, endpoint graph, and domain margins must be supplied
by BHSM callables; the assembler never selects or synthesizes them.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable, Mapping

import numpy as np


Array = np.ndarray
VectorField = Callable[[Array], Array]
ScalarField = Callable[[Array], float]
ResetRows = Callable[[Array], Array]


@dataclass(frozen=True)
class C2ConnectionResidual:
    """Block residual and inequality audit for one endpoint stratum."""

    duration: float
    reset: Array
    birth_seam: Array
    flow: Array
    endpoint: Array
    minimum_margins: Mapping[str, float]
    endpoint_kind: str
    path_admissible: bool

    @property
    def vector(self) -> Array:
        """Return equality blocks in their action-native order."""

        return np.concatenate((
            self.reset.reshape(-1),
            self.birth_seam.reshape(-1),
            self.flow.reshape(-1),
            self.endpoint.reshape(-1),
        ))


def fixed_event_child_reset_rows(full_reset_rows: Array) -> Array:
    """Extract the 31 child/interface rows after fixing the certified event.

    The retained 57-row joint reset is ordered as 25 event constraints, one
    ordered-event row, four trace rows, 25 child constraints, and two momentum
    rows.  Holding the certified event fixed removes the first 26 rows; the
    remaining 31 rows define the local child reset fiber.
    """

    rows = np.asarray(full_reset_rows, dtype=float)
    if rows.shape != (57,) or not np.all(np.isfinite(rows)):
        raise ValueError("finite 57-row full reset residual required")
    return rows[26:].copy()


def _evaluate_vector_field(function: VectorField, state: Array) -> Array:
    value = np.asarray(function(state), dtype=float)
    if value.shape != state.shape or not np.all(np.isfinite(value)):
        raise ValueError("vector field must return one finite state vector")
    return value


def assemble_c2_finite_connection_residual(
    *,
    child_initial_state: Array,
    path_nodes: Array,
    log_duration: float,
    reset_rows: ResetRows,
    vector_field: VectorField,
    endpoint_function: ScalarField,
    margin_functions: Mapping[str, ScalarField],
    endpoint_kind: str,
) -> C2ConnectionResidual:
    """Assemble a trapezoidal C2-to-event/stop connection residual.

    ``log_duration`` parameterizes ``T=exp(log_duration)>0``.  The path uses
    normalized time ``s in [0,1]`` and the equality blocks are

    ``C_reset(Y0)=0``, ``Y_path(0)-Y0=0``,
    ``Y_{i+1}-Y_i-(T*ds/2)(V_i+V_{i+1})=0``, and
    ``e(Y_path(1))=0``.

    Domain margins are inequalities, not equations.  They are evaluated at
    every node and reported without adding a fitted cutoff or penalty.
    """

    initial = np.asarray(child_initial_state, dtype=float)
    nodes = np.asarray(path_nodes, dtype=float)
    if initial.ndim != 1 or initial.size == 0 or not np.all(np.isfinite(initial)):
        raise ValueError("finite nonempty child initial state required")
    if (
        nodes.ndim != 2
        or nodes.shape[0] < 2
        or nodes.shape[1] != initial.size
        or not np.all(np.isfinite(nodes))
    ):
        raise ValueError("at least two finite path nodes of the child dimension required")
    theta = float(log_duration)
    if not math.isfinite(theta):
        raise ValueError("finite log-duration required")
    duration = math.exp(theta)
    if not math.isfinite(duration) or duration <= 0.0:
        raise ValueError("finite positive duration required")
    kind = str(endpoint_kind)
    if kind not in {"RETAINED_EVENT", "CANONICAL_STOP"}:
        raise ValueError("endpoint kind must be retained event or canonical stop")
    if not margin_functions:
        raise ValueError("at least one action-domain margin required")

    reset = np.asarray(reset_rows(initial), dtype=float)
    if reset.ndim != 1 or not np.all(np.isfinite(reset)):
        raise ValueError("reset callback must return one finite row vector")
    birth_seam = nodes[0] - initial
    fields = np.asarray([
        _evaluate_vector_field(vector_field, node) for node in nodes
    ])
    step = 1.0 / (nodes.shape[0] - 1)
    flow = (
        nodes[1:]
        - nodes[:-1]
        - 0.5 * duration * step * (fields[:-1] + fields[1:])
    )
    endpoint_value = float(endpoint_function(nodes[-1]))
    if not math.isfinite(endpoint_value):
        raise ValueError("finite endpoint graph value required")

    minimum_margins: dict[str, float] = {}
    for name, function in margin_functions.items():
        values = [float(function(node)) for node in nodes]
        if not values or not all(math.isfinite(value) for value in values):
            raise ValueError(f"finite values required for margin {name}")
        minimum_margins[str(name)] = min(values)
    path_admissible = all(value > 0.0 for value in minimum_margins.values())

    return C2ConnectionResidual(
        duration=duration,
        reset=reset,
        birth_seam=birth_seam,
        flow=flow,
        endpoint=np.asarray([endpoint_value]),
        minimum_margins=minimum_margins,
        endpoint_kind=kind,
        path_admissible=path_admissible,
    )


__all__ = [
    "C2ConnectionResidual",
    "assemble_c2_finite_connection_residual",
    "fixed_event_child_reset_rows",
]
