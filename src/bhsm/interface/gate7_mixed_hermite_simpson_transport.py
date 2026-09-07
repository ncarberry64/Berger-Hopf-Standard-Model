"""Exact algebra for the Gate-7 mixed Hermite--Simpson transport.

This module contains no action evaluation and promotes no Gate-7 claim.  It
only records the bilinear chain rule which the current-C2 retained-action
endpoint and midpoint evaluations must satisfy.
"""

from __future__ import annotations

from typing import NamedTuple

import numpy as np


class MixedMidpointKinematics(NamedTuple):
    central_direction: np.ndarray
    transverse_directions: np.ndarray
    mixed_second_incidence: np.ndarray


def _array(value: np.ndarray) -> np.ndarray:
    return np.asarray(value)


def mixed_midpoint_kinematics(
    step: object,
    left_central_direction: np.ndarray,
    right_central_direction: np.ndarray,
    left_central_first: np.ndarray,
    right_central_first: np.ndarray,
    left_transverse_directions: np.ndarray,
    right_transverse_directions: np.ndarray,
    left_transverse_first: np.ndarray,
    right_transverse_first: np.ndarray,
    left_mixed_second: np.ndarray,
    right_mixed_second: np.ndarray,
) -> MixedMidpointKinematics:
    """Apply the exact mixed derivative of the HS midpoint formula."""
    lc = _array(left_central_direction)
    rc = _array(right_central_direction)
    lcf = _array(left_central_first)
    rcf = _array(right_central_first)
    lt = _array(left_transverse_directions)
    rt = _array(right_transverse_directions)
    ltf = _array(left_transverse_first)
    rtf = _array(right_transverse_first)
    lm = _array(left_mixed_second)
    rm = _array(right_mixed_second)
    if not (lc.shape == rc.shape == lcf.shape == rcf.shape):
        raise ValueError("central endpoint arrays must have one common shape")
    if lc.ndim != 1:
        raise ValueError("central endpoint arrays must be ambient vectors")
    if not (lt.shape == rt.shape == ltf.shape == rtf.shape == lm.shape == rm.shape):
        raise ValueError("transverse and mixed endpoint arrays must share shape")
    if lt.ndim != 2 or lt.shape[0] != lc.size:
        raise ValueError("transverse arrays must be ambient-by-coordinate matrices")
    central = (lc + rc) / 2 + step * (lcf - rcf) / 8
    transverse = (lt + rt) / 2 + step * (ltf - rtf) / 8
    incidence = step * (lm - rm) / 8
    return MixedMidpointKinematics(central, transverse, incidence)


def local_hs_mixed_residual(
    step: object,
    left_mixed_second: np.ndarray,
    midpoint_intrinsic_mixed: np.ndarray,
    midpoint_incidence_first: np.ndarray,
    right_mixed_second: np.ndarray,
) -> np.ndarray:
    """Return the mixed second derivative of the local HS residual."""
    left = _array(left_mixed_second)
    intrinsic = _array(midpoint_intrinsic_mixed)
    incidence = _array(midpoint_incidence_first)
    right = _array(right_mixed_second)
    if not (left.shape == intrinsic.shape == incidence.shape == right.shape):
        raise ValueError("all local mixed residual terms must share shape")
    return -step * (left + 4 * (intrinsic + incidence) + right) / 6


def causal_mixed_rhs(
    test_frame: np.ndarray,
    left_newton_block: np.ndarray,
    trial_frame: np.ndarray,
    previous_causal_mixed: np.ndarray,
    local_hs_mixed: np.ndarray,
) -> np.ndarray:
    """Assemble the frozen causal right-hand side before verified solution.

    The caller must apply the already-certified reduced-right Newton solve and
    the overall minus sign.  Keeping that solve outside this algebra helper
    prevents an ordinary floating-point inverse from masquerading as outward
    authority.
    """
    test = _array(test_frame)
    left = _array(left_newton_block)
    trial = _array(trial_frame)
    previous = _array(previous_causal_mixed)
    local = _array(local_hs_mixed)
    if test.ndim != 2 or left.ndim != 2 or trial.ndim != 2:
        raise ValueError("test, Newton, and trial maps must be matrices")
    if previous.ndim != 2 or local.ndim != 2:
        raise ValueError("mixed operators must be matrices")
    if left.shape[0] != left.shape[1]:
        raise ValueError("the left Newton block must be square")
    if test.shape[1] != left.shape[0] or left.shape[1] != trial.shape[0]:
        raise ValueError("test, Newton, and trial ambient dimensions disagree")
    if trial.shape[1] != previous.shape[0]:
        raise ValueError("the prior causal coordinate dimension is incompatible")
    if test.shape[1] != local.shape[0]:
        raise ValueError("the local residual has the wrong ambient dimension")
    if previous.shape[1] != local.shape[1]:
        raise ValueError("mixed operators must use one common source coordinate")
    return test @ local + test @ left @ trial @ previous
