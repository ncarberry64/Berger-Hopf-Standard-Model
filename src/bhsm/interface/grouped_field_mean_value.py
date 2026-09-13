"""Integrate a uniform derivative over a complete affine product domain."""
import numpy as np
from flint import arb, arb_mat
from bhsm.interface.affine_eigenpair_contraction import _balls
from bhsm.interface.affine_hs_midpoint_domain import group_row_bounds


def enclose_field(anchor, derivative, directions, groups):
    """Caller certifies the same C1 family, anchor and full-domain derivative."""
    f, D, V = map(_balls, (anchor, derivative, directions))
    if (f.ndim != 1 or not f.size or D.ndim != 2 or D.shape[0] != f.size
            or V.ndim != 2 or V.shape[0] != D.shape[1] or not V.shape[1]):
        raise ValueError('complete field, physical derivative and affine directions required')
    directional = arb_mat(D.shape[0], D.shape[1], list(D.flat))*arb_mat(V.shape[0], V.shape[1], list(V.flat))
    directional = np.array(directional.entries(), dtype=object).reshape(f.size, V.shape[1])
    support = group_row_bounds(directional, groups)
    candidate = np.array([a+arb(0, b) for a, b in zip(f, support, strict=True)], dtype=object)
    return candidate, support, directional
