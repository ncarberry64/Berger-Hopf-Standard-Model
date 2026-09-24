"""Shared state Taylor models with an exact, arbitrary linear input leg.

Represents <c + A theta + e(theta), u>, with u in one product of unit
balls and e bounded by r in its dual support norm. The physical input ball
is never split into independent scalar boxes. Additional box groups can
retain shared implicit correction symbols until residual cancellation.
This arithmetic alone establishes no physical inclusion or Gate-7 result.
"""
from contextlib import contextmanager
from flint import arb, arb_mat, ctx

from bhsm.interface.shared_action_taylor import Taylor, scalar_taylor_action
from bhsm.interface.shared_parameter_residual import linear_support, validate_groups


def vector_norm(values):
    return sum((abs(v).upper() ** 2 for v in values), arb(0)).sqrt().upper()


def matrix_norm_bound(matrix):
    """Two rigorous upper bounds on the Euclidean induced matrix norm."""
    frobenius = vector_norm(matrix.entries())
    rows = max(sum((abs(matrix[i, j]).upper() for j in range(matrix.ncols())), arb(0)).upper()
               for i in range(matrix.nrows()))
    columns = max(sum((abs(matrix[i, j]).upper() for i in range(matrix.nrows())), arb(0)).upper()
                  for j in range(matrix.ncols()))
    return min(frobenius, (rows * columns).sqrt().upper())


class InputLinearTaylor:
    def __init__(self, domain, constant, coefficients, remainder=0, input_groups=None):
        if (ctx.prec != domain.precision or constant.nrows() != 1
                or coefficients.nrows() != domain.dimension
                or coefficients.ncols() != constant.ncols() or constant.ncols() < 1):
            raise ValueError('complete common state and input spaces required')
        remainder = arb(remainder)
        if (not remainder.is_finite() or not remainder >= 0
                or any(not v.is_finite() for v in constant.entries() + coefficients.entries())):
            raise ValueError('finite coefficients and nonnegative remainder required')
        self.domain, self.c, self.a, self.r = domain, constant, coefficients, remainder.upper()
        self.input_groups = tuple(input_groups or [(0, constant.ncols(), 'euclidean')])
        validate_groups(self.input_groups, constant.ncols())
        self._linear = None
        self._constant = None

    def _new(self, constant, coefficients, remainder):
        # Internal additions and products preserve the established finite
        # matrix shapes. Avoid walking a large coefficient matrix again.
        # Public construction still validates every supplied entry.
        if ctx.prec != self.domain.precision:
            raise ValueError('unchanged arithmetic precision required')
        remainder = remainder.upper()
        if not remainder.is_finite() or not remainder >= 0:
            raise ArithmeticError('finite nonnegative outward remainder required')
        result = object.__new__(InputLinearTaylor)
        result.domain, result.c, result.a, result.r = self.domain, constant, coefficients, remainder
        result.input_groups = self.input_groups
        result._linear = result._constant = None
        return result

    def constant_bound(self):
        if self._constant is None:
            self._constant = linear_support(self.c.entries(), self.input_groups)
        return self._constant

    def linear_bound(self):
        if self._linear is None:
            total = arb(0)
            for start, stop, kind in self.domain.groups:
                if kind == 'euclidean':
                    for begin, end, input_kind in self.input_groups:
                        if input_kind == 'euclidean':
                            total += matrix_norm_bound(arb_mat(stop-start, end-begin,
                                [self.a[i, j] for i in range(start, stop) for j in range(begin, end)]))
                        else:
                            total += sum((vector_norm([self.a[i, j] for i in range(start, stop)])
                                          for j in range(begin, end)), arb(0))
                else:
                    total += sum((linear_support([self.a[i, j] for j in range(self.c.ncols())], self.input_groups)
                                  for i in range(start, stop)), arb(0))
            self._linear = total.upper()
        return self._linear

    def support(self):
        return (self.constant_bound() + self.linear_bound() + self.r).upper()

    def __add__(self, other):
        if isinstance(other, (int, arb)) and other == 0:
            return self
        if (isinstance(other, Taylor) and other.domain is self.domain
                and other.c.is_zero() and other.r.is_zero()
                and all(v.is_zero() for v in other.a.entries())):
            return self
        if not isinstance(other, InputLinearTaylor):
            return NotImplemented
        if (other.domain is not self.domain or other.c.ncols() != self.c.ncols()
                or other.input_groups != self.input_groups):
            raise ValueError('same state parameters and same input leg required')
        return self._new(self.c + other.c, self.a + other.a, self.r + other.r)

    __radd__ = __add__

    def __neg__(self):
        return self._new(-self.c, -self.a, self.r)

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        if isinstance(other, InputLinearTaylor):
            raise ValueError('two input legs would violate exact input linearity')
        if isinstance(other, (int, float, str, arb)):
            scalar = arb(other)
            return self._new(self.c * scalar, self.a * scalar, self.r * abs(scalar).upper())
        if not isinstance(other, Taylor):
            return NotImplemented
        if other.domain is not self.domain:
            raise ValueError('same state parameter identity required')
        lb = other.linear_bound()
        if lb.is_zero() and other.r.is_zero():
            return self * other.c
        la = self.linear_bound()
        nc, nd = self.constant_bound(), abs(other.c).upper()
        remainder = la*lb + (nc+la)*other.r + (nd+lb)*self.r + self.r*other.r
        return self._new(self.c*other.c, self.a*other.c + other.a.transpose()*self.c, remainder)

    __rmul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, Taylor):
            return self * other.reciprocal()
        if isinstance(other, (int, float, str, arb)):
            return self * (1/arb(other))
        return NotImplemented

    def at_input(self, direction):
        """Restrict to a fixed input without assuming its length is one."""
        if direction.ncols() != 1 or direction.nrows() != self.c.ncols():
            raise ValueError('complete fixed input direction required')
        gauge = max(vector_norm([direction[i, 0] for i in range(start, stop)])
                    if kind == 'euclidean' else max(abs(direction[i, 0]).upper() for i in range(start, stop))
                    for start, stop, kind in self.input_groups)
        return Taylor(self.domain, (self.c*direction)[0, 0],
                      (self.a*direction).transpose(), self.r*gauge)


@contextmanager
def input_linear_taylor_action(module):
    """Retained action with shared state models and exactly one input leg."""
    with scalar_taylor_action(module):
        previous = module._a
        module._a = lambda v: v if isinstance(v, InputLinearTaylor) else previous(v)
        try:
            yield
        finally:
            module._a = previous
