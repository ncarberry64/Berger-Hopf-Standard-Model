"""Intersect a known implicit-error box with a rigorous residual majorant.

If the actual error satisfies |eta| <= f + K |eta| with f,K nonnegative,
every finite intersection step below preserves the original solution graph.
Contraction is not required and no existence or uniqueness claim is made.
"""
from flint import arb, arb_mat


def intersect_majorant(initial, forcing, coupling, iterations=32):
    size = len(initial)
    if (not size or len(forcing) != size or coupling.nrows() != size
            or coupling.ncols() != size or iterations < 0
            or any(not v.is_finite() or not v >= 0
                   for v in [*initial, *forcing, *coupling.entries()])):
        raise ValueError('finite nonnegative complete error majorant required')
    bounds = [v.upper() for v in initial]
    for _ in range(iterations):
        candidate = arb_mat(size, 1, forcing) + coupling * arb_mat(size, 1, bounds)
        bounds = [min(old, new.upper()) for old, new in zip(bounds, candidate.entries(), strict=True)]
    return bounds
