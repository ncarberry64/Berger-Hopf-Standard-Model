"""Common fixed-Y current jets on one joined chronological inverse.

The retained common canonical birth frame is explicit. These are source
applications on that domain, not a choice of quantum state or native heat.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import lu_factor, lu_solve


def block_current_coefficients(diagonal, lower, Y_diagonal, Y_lower, rhs, *, order=4):
    """Apply the block first-order action without a dense temporal inverse."""
    d, l, b, c, r = (np.asarray(a, complex) for a in (diagonal, lower, Y_diagonal, Y_lower, rhs))
    if d.ndim != 3 or any(a.shape != d.shape for a in (l, b, c)) or r.ndim != 4 or r.shape[1:3] != d.shape[:2]:
        raise ValueError('same block action and literal coefficient source required')
    if not all(np.isfinite(a).all() for a in (d, l, b, c, r)) or len(r)-1 > order:
        raise ValueError('finite coefficients and complete retained order required')
    factors = [lu_factor(a) for a in d]
    u = np.zeros((order+1, *r.shape[1:]), complex)
    residuals = np.zeros_like(u)
    for k in range(order+1):
        for j in range(len(d)):
            source = r[k, j].copy() if k < len(r) else np.zeros_like(r[0, j])
            if j:
                source -= l[j]@u[k, j-1]
            if k:
                source -= b[j]@u[k-1, j]
                if j:
                    source -= c[j]@u[k-1, j-1]
            u[k, j] = lu_solve(factors[j], source)
            residuals[k, j] = d[j]@u[k, j]-source
    return dict(coefficients=u, original_recurrence_residuals=residuals)


def rectangular_block_source_jet(source, diagonal, lower, Y_diagonal, Y_lower,
        delta_diagonal, delta_lower, *, order=4):
    """Differentiate the action with source and target Y motion retained."""
    u, dd, dl = (np.asarray(a, complex) for a in (source, delta_diagonal, delta_lower))
    right = np.zeros((order+1, len(diagonal), diagonal.shape[1], u.shape[-1]), complex)
    for k in range(order+1):
        for q in range(min(k+1, len(dd))):
            right[k] -= dd[q]@u[k-q]
            right[k, 1:] -= dl[q, 1:]@u[k-q, :-1]
    return block_current_coefficients(diagonal, lower, Y_diagonal, Y_lower, right, order=order)


def midpoint_current_coefficients(left, weights, response, *, birth_index, birth_transport):
    """Pull back the child preceding trace in the current as in the action."""
    u = np.asarray(response, complex)
    before = np.concatenate((np.zeros_like(u[:, :1]), u[:, :-1]), axis=1)
    before[:, birth_index] = np.asarray(birth_transport)@before[:, birth_index]
    midpoint = (u+before)/2
    return np.einsum('t,tij,ktjm->kim', weights, left, midpoint)
