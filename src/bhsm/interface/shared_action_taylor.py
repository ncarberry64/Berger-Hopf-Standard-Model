"""First-order common-parameter Taylor enclosures of the retained action.

The polynomial part is never converted into coordinate intervals. Only the
explicit nonlinear remainder is hulled. This is an action evaluator, not an
implicit-solution inclusion or a Gate-7 certificate.
"""
from contextlib import contextmanager
from flint import arb, arb_mat, ctx
from bhsm.interface.shared_parameter_residual import linear_support, validate_groups


class TaylorDomain:
    def __init__(self, groups, dimension):
        validate_groups(groups, dimension)
        self.groups = tuple(groups)
        self.dimension = dimension
        self.precision = ctx.prec

    def affine(self, constant, coefficients=None, remainder=0):
        is_constant = coefficients is None
        coefficients = ([arb(0)] * self.dimension if coefficients is None
                        else list(coefficients))
        result = Taylor(self, arb(constant), arb_mat(1, self.dimension, coefficients), arb(remainder))
        if is_constant:
            result._linear = arb(0)
        return result


class Taylor:
    """f(theta) in c + a theta + [-r,r], on one specified product domain."""
    def __init__(self, domain, constant, coefficients, remainder):
        if (ctx.prec != domain.precision or coefficients.nrows() != 1
                or coefficients.ncols() != domain.dimension):
            raise ValueError('same precision and complete parameter domain required')
        if (not constant.is_finite() or not remainder.is_finite() or not remainder >= 0
                or any(not x.is_finite() for x in coefficients.entries())):
            raise ValueError('finite coefficients and nonnegative remainder required')
        self.domain, self.c, self.a, self.r = domain, constant, coefficients, remainder.upper()
        self._linear = None

    def linear_bound(self):
        if self._linear is None:
            self._linear = linear_support(self.a.entries(), self.domain.groups)
        return self._linear

    def enclosure(self):
        return self.c + arb(0, (self.linear_bound() + self.r).upper())

    def support(self):
        return (abs(self.c).upper() + self.linear_bound() + self.r).upper()

    def _coerce(self, other):
        if isinstance(other, Taylor):
            if other.domain is not self.domain:
                raise ValueError('shared parameter identity required')
            return other
        if isinstance(other, (int, float, str, arb)):
            return self.domain.affine(other)
        return NotImplemented

    def __add__(self, other):
        if isinstance(other, (int, float, str, arb)):
            return Taylor(self.domain, self.c+arb(other), self.a, self.r)
        other = self._coerce(other)
        if other is NotImplemented:
            return NotImplemented
        return Taylor(self.domain, self.c + other.c, self.a + other.a, self.r + other.r)

    __radd__ = __add__

    def __neg__(self):
        return Taylor(self.domain, -self.c, -self.a, self.r)

    def __sub__(self, other):
        other = self._coerce(other)
        return NotImplemented if other is NotImplemented else self + (-other)

    def __rsub__(self, other):
        return (-self) + other

    def __mul__(self, other):
        if isinstance(other, (int, float, str, arb)):
            other = arb(other)
            return Taylor(self.domain, self.c*other, self.a*other, self.r*abs(other).upper())
        other = self._coerce(other)
        if other is NotImplemented:
            return NotImplemented
        la, lb = self.linear_bound(), other.linear_bound()
        remainder = (la * lb + (abs(self.c).upper() + la) * other.r
                     + (abs(other.c).upper() + lb) * self.r + self.r * other.r)
        return Taylor(self.domain, self.c * other.c,
                      self.a * other.c + other.a * self.c, remainder)

    __rmul__ = __mul__

    def _unary(self, value, first, second_bound):
        width = (self.linear_bound() + self.r).upper()
        remainder = abs(first).upper() * self.r + second_bound * width * width / 2
        return Taylor(self.domain, value, self.a * first, remainder)

    def reciprocal(self):
        full = self.enclosure()
        if full.contains(0):
            raise ArithmeticError('Taylor reciprocal crosses zero')
        return self._unary(1 / self.c, -1 / self.c**2,
                           (2 / abs(full)**3).upper())

    def exp(self):
        return self._unary(self.c.exp(), self.c.exp(), self.enclosure().exp().upper())

    def log(self):
        full = self.enclosure()
        if not full > 0:
            raise ArithmeticError('Taylor logarithm is not positive')
        return self._unary(self.c.log(), 1 / self.c, (1 / full**2).upper())

    def __truediv__(self, other):
        other = self._coerce(other)
        return NotImplemented if other is NotImplemented else self * other.reciprocal()

    def __rtruediv__(self, other):
        return self.reciprocal() * other

    def __pow__(self, power):
        if type(power) is not int:
            return NotImplemented
        if power < 0:
            return (self ** (-power)).reciprocal()
        result, base = self.domain.affine(1), self
        while power:
            if power & 1:
                result = result * base
            power >>= 1
            if power:
                base = base * base
        return result


@contextmanager
def scalar_taylor_action(module):
    """Adapt the unchanged parent action's scalar mixed algebra, then restore.

    The caller binds the parent's source hash. No array-valued contraction is
    allowed here. The original quadrature, maps, action and boundary are used.
    """
    original_a, original_mixed, original_variables = module._a, module.Mixed, module._local_variables

    class ScalarMixed(original_mixed):
        def reciprocal(self):
            value = self.d[0]
            if not isinstance(value, Taylor):
                return super().reciprocal()
            outer = [arb(0)]
            factorial = 1
            for order in range(1, self.directions + 1):
                factorial *= order
                outer.append((-1)**order * factorial / value**(order + 1))
            return self._unary(value.reciprocal(), outer)

        def positive_power(self, power):
            value = self.d[0]
            if not isinstance(value, Taylor):
                return super().positive_power(power)
            p = arb(power)
            outer, coefficient = [arb(0)], arb(1)
            for order in range(1, self.directions + 1):
                coefficient *= p - (order - 1)
                outer.append(coefficient * ((p - order) * value.log()).exp())
            return self._unary((p * value.log()).exp(), outer)

    def variables(values, directions, legs):
        if legs is None:
            if directions:
                raise ValueError('explicit scalar action legs required')
            return [ScalarMixed.constant(value, 0) for value in values]
        selected = []
        for i, value in enumerate(values):
            items = []
            for leg in legs:
                entry = leg[i]
                if hasattr(entry, 'shape'):
                    if entry.shape != ():
                        raise ValueError('only scalar contracted action outputs supported')
                    entry = entry.item()
                items.append(entry)
            selected.append(ScalarMixed.affine(value, items))
        return selected

    module._a = lambda value: value if isinstance(value, Taylor) else original_a(value)
    module.Mixed, module._local_variables = ScalarMixed, variables
    try:
        yield
    finally:
        module._a, module.Mixed, module._local_variables = original_a, original_mixed, original_variables
