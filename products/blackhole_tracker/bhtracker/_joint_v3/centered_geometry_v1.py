"""Same five-parameter PSPL geometry, evaluated without a large-JD round trip.

Input epochs remain the supplied finite JD values. The physical t0 is represented
by the pair (numerical_time_origin, t0_offset_days), never by their rounded sum
inside the forward calculation. This is a numerical evaluation revision, not a
new optical potential, covariance, likelihood family or physical analysis domain.
"""
import math
import numpy as np


def centered_geometry(times, *, numerical_time_origin, t0_offset_days, tE_days,
                      u0_heliocentric, angle_source_minus_lens_rad, pi_E, earth):
    scalar = (numerical_time_origin, t0_offset_days, tE_days, u0_heliocentric,
              angle_source_minus_lens_rad, pi_E)
    if any(isinstance(x, (bool, np.bool_)) or not isinstance(x, (int, float, np.integer, np.floating)) for x in scalar):
        raise ValueError('Finite real physical scalars required')
    if not np.isfinite(scalar).all() or tE_days <= 0 or pi_E < 0:
        raise ValueError('Finite scalars, positive timescale and nonnegative parallax required')
    raw_t, raw_e = np.asarray(times), np.asarray(earth)
    if raw_t.dtype.kind not in 'iuf' or raw_e.dtype.kind not in 'iuf':
        raise ValueError('Real epoch/Earth vectors required')
    t, e = np.asarray(raw_t, float), np.asarray(raw_e, float)
    if t.ndim != 1 or e.shape != (len(t), 2) or not len(t) or not np.isfinite(t).all() or not np.isfinite(e).all():
        raise ValueError('Matched finite nonempty epoch/Earth vectors required')
    n = np.array([math.cos(angle_source_minus_lens_rad), math.sin(angle_source_minus_lens_rad)])
    b = np.array([-n[1], n[0]])
    h = ((t - numerical_time_origin) - t0_offset_days) / tE_days
    q = u0_heliocentric * b + h[:, None] * n + pi_E * e
    dq = np.empty((len(t), 2, 5))
    dq[:, :, 0] = -n / tE_days
    dq[:, :, 1] = -h[:, None] * n
    dq[:, :, 2] = b
    dq[:, :, 3] = -u0_heliocentric * n + h[:, None] * b
    dq[:, :, 4] = e
    q2 = np.sum(q * q, axis=1)
    if not np.isfinite(q2).all() or np.any(q2 <= 1e-16):
        raise ValueError('Unresolved critical alignment in the unchanged declared numerical domain')
    amplitude = (q2 + 2) / np.sqrt(q2 * (q2 + 4))
    da = np.einsum('ni,nij->nj', -8 * q / (q2 * (q2 + 4))[:, None] ** 1.5, dq)
    unit = q / (q2 + 2)[:, None]
    jac = np.eye(2)[None, :, :] / (q2 + 2)[:, None, None] - 2 * q[:, :, None] * q[:, None, :] / (q2 + 2)[:, None, None] ** 2
    du = np.einsum('nik,nkj->nij', jac, dq)
    if not all(np.isfinite(x).all() for x in (amplitude, da, unit, du)):
        raise FloatingPointError('Unrepresentable geometry/derivatives; no floor substituted')
    return amplitude, da, unit, du
