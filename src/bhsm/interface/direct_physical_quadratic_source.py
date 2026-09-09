"""Contract complete ambient rate Hessians into fixed-frame HS sources."""
from flint import arb_mat, ctx
from bhsm.interface.direct_physical_hs_jacobian import _matrix, physical_hs_blocks
from bhsm.interface.direct_physical_hs_second_variation import (
    physical_hs_second_residual, frozen_newton_quadratic_source,
)


class UpperHessian:
    """A complete symmetric input tensor, supplied as output-by-upper-row blocks.

    Symmetry is the caller's local C2 Hessian assumption. No missing row is
    filled with zero; each row i must contain every input column i..n-1.
    This object validates arithmetic and layout, not physical provenance.
    """

    def __init__(self, rows):
        rows = [_matrix(row) for row in rows]
        n = len(rows)
        if not n or any(row.nrows() != n or row.ncols() != n-i for i,row in enumerate(rows)):
            raise ValueError('complete square-output upper Hessian rows required')
        self.dimension = n
        self.components = tuple(arb_mat(n, n, [
            rows[min(i,j)][output,abs(j-i)] for i in range(n) for j in range(n)
        ]) for output in range(n))

    def cartesian(self, left, right):
        """Return H[left[:,a],right[:,b]], columns ordered a*q+b."""
        left, right = _matrix(left), _matrix(right)
        if left.nrows() != self.dimension or right.nrows() != self.dimension:
            raise ValueError('ambient Hessian directions have wrong dimension')
        values = [(left.transpose()*component*right).entries() for component in self.components]
        result = arb_mat(self.dimension, left.ncols()*right.ncols(), [v for row in values for v in row])
        if not all(v.is_finite() for v in result.entries()):
            raise ArithmeticError('nonfinite Hessian contraction')
        return result


def physical_quadratic_source(hessians, derivatives, step, u0, u1, v0, v1,
                              test, frozen_right, *, precision=512):
    """Enclose -R^-1 T D2r[(u0,u1),(v0,v1)]/2 for Cartesian families.

    Inputs are ordered endpoint, actual HS midpoint, next endpoint. Endpoint
    direction matrices already include the frozen trial frame. Both time
    endpoints of each family have the same column count. Missing endpoints
    are never inferred: a fixed initial endpoint must be explicitly zero.
    """
    if type(precision) is not int or precision < 64:
        raise ValueError('at least 64 bits of arithmetic precision required')
    previous = ctx.prec; ctx.prec = precision
    try:
        if len(hessians) != 3 or len(derivatives) != 3 or not all(isinstance(h,UpperHessian) for h in hessians):
            raise ValueError('three complete physical Hessians and derivatives required')
        u0,u1,v0,v1 = map(_matrix,(u0,u1,v0,v1))
        n = hessians[0].dimension
        if (any(h.dimension != n for h in hessians)
                or any(m.nrows() != n for m in (u0,u1,v0,v1))
                or u0.ncols() != u1.ncols() or v0.ncols() != v1.ncols()):
            raise ValueError('compatible paired endpoint direction families required')
        blocks = physical_hs_blocks(*derivatives,step,precision=precision)
        if blocks['midpoint_left'].nrows() != n:
            raise ValueError('Hessian and derivative dimensions differ')
        um = blocks['midpoint_left']*u0 + blocks['midpoint_right']*u1
        vm = blocks['midpoint_left']*v0 + blocks['midpoint_right']*v1
        contractions = [h.cartesian(u,v) for h,u,v in zip(hessians,(u0,um,u1),(v0,vm,v1))]
        residual = physical_hs_second_residual(*contractions,derivatives[1],step,precision=precision)
        return frozen_newton_quadratic_source(residual['residual_second'],test,frozen_right,precision=precision)
    finally:
        ctx.prec = previous
