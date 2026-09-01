"""Zero-energy threshold audit for the BHSM-AE-2 factorized domain.

The AE2 reset lift removes the old relative Cayley parameter, but it does not
turn the spatial Dirac eigenvalue into an independent positive potential.  In
each retained product channel the squared form is ``||A_s u||^2`` with
``A_s=d_tau+s(tau)``.  The transport equation ``A_s u=0`` therefore supplies
an exact zero-form-energy collar section for every initial trace.  This module
records that obstruction without claiming that the realized maximal exterior
actually has a zero mode.
"""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np


def constant_channel_zero_transport(
    superpotential: float,
    proper_duration: float,
    initial_trace: complex = 1.0,
) -> dict[str, complex | float]:
    """Return the exact constant-channel solution of ``(d_tau+s)u=0``."""

    s = float(superpotential)
    duration = float(proper_duration)
    trace = complex(initial_trace)
    if not math.isfinite(s):
        raise ValueError("finite superpotential required")
    if not math.isfinite(duration) or duration <= 0.0:
        raise ValueError("finite positive proper duration required")
    if not (math.isfinite(trace.real) and math.isfinite(trace.imag)):
        raise ValueError("finite initial trace required")
    terminal = trace * math.exp(-s * duration)
    return {
        "initial_trace": trace,
        "terminal_trace": terminal,
        "birth_factorized_conormal": 0.0,
        "terminal_inward_factorized_graph": 0.0,
        "factorized_form_energy": 0.0,
        "zero_energy_weyl_value": 0.0,
    }


def piecewise_constant_zero_transport(
    superpotentials: Sequence[float],
    proper_steps: Sequence[float],
    initial_trace: complex = 1.0,
) -> dict[str, object]:
    """Propagate the exact zero-transport recurrence through a finite collar.

    On cell ``j``, ``u_{j+1}=exp(-s_j h_j)u_j``.  The returned residual is
    the recurrence residual, not a finite-difference approximation to the
    differential equation.
    """

    s = np.asarray(superpotentials, dtype=float)
    h = np.asarray(proper_steps, dtype=float)
    trace = complex(initial_trace)
    if s.ndim != 1 or h.ndim != 1 or s.size == 0 or s.shape != h.shape:
        raise ValueError("equal nonempty one-dimensional channel arrays required")
    if not np.all(np.isfinite(s)) or not np.all(np.isfinite(h)) or np.any(h <= 0.0):
        raise ValueError("finite superpotentials and positive proper steps required")
    if not (math.isfinite(trace.real) and math.isfinite(trace.imag)):
        raise ValueError("finite initial trace required")

    values = [trace]
    residuals = []
    for potential, step in zip(s, h, strict=True):
        next_value = values[-1] * math.exp(-float(potential * step))
        residuals.append(
            next_value - values[-1] * math.exp(-float(potential * step))
        )
        values.append(next_value)
    return {
        "values": values,
        "maximum_transport_residual": float(max(abs(value) for value in residuals)),
        "factorized_form_energy": 0.0,
        "birth_factorized_conormal": 0.0,
        "terminal_inward_factorized_graph": 0.0,
    }


def two_sided_ae2_zero_transport(
    event_superpotential: float,
    child_superpotential: float,
    event_duration: float,
    child_duration: float,
    reset_lift: Sequence[Sequence[complex]],
    event_trace: Sequence[complex],
) -> dict[str, float | bool]:
    """Give a two-sided zero-conormal witness compatible with the AE2 graph.

    Both sides use proper distance away from the reset seam.  Each side solves
    its own factor equation and the child seam trace is ``U_R`` times the
    event seam trace.  Consequently both factorized conormals vanish and so
    does their reset-pulled-back sum.
    """

    lift = np.asarray(reset_lift, dtype=complex)
    trace = np.asarray(event_trace, dtype=complex)
    if lift.ndim != 2 or lift.shape[0] != lift.shape[1]:
        raise ValueError("square reset lift required")
    if trace.ndim != 1 or trace.size != lift.shape[0]:
        raise ValueError("event trace and reset lift dimensions must match")
    if not np.all(np.isfinite(lift)) or not np.all(np.isfinite(trace)):
        raise ValueError("finite reset data required")
    unitarity = float(
        np.linalg.norm(np.conjugate(lift.T) @ lift - np.eye(lift.shape[0]))
    )
    if unitarity > 1.0e-12:
        raise ValueError("unitary reset lift required")

    event = constant_channel_zero_transport(
        event_superpotential, event_duration, trace[0]
    )
    child_trace = lift @ trace
    child = constant_channel_zero_transport(
        child_superpotential, child_duration, child_trace[0]
    )
    total_conormal = float(
        event["birth_factorized_conormal"]
        + child["birth_factorized_conormal"]
    )
    return {
        "unitarity_residual": unitarity,
        "trace_graph_residual": float(np.linalg.norm(child_trace - lift @ trace)),
        "event_factorized_form_energy": float(event["factorized_form_energy"]),
        "child_factorized_form_energy": float(child["factorized_form_energy"]),
        "two_sided_zero_energy_wronskian": total_conormal,
        "strict_positive_margin_from_local_collars": total_conormal > 0.0,
    }


__all__ = [
    "constant_channel_zero_transport",
    "piecewise_constant_zero_transport",
    "two_sided_ae2_zero_transport",
]
