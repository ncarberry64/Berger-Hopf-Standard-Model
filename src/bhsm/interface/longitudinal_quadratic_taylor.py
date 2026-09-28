"""Retain one common longitudinal square alongside all affine parameters.

Models c+a.theta+q*theta_0^2+[-r,r]. The remaining mixed products are
outwardly enclosed; no derivative or implicit-solution claim is supplied.
"""
from flint import arb, arb_mat
from bhsm.interface.shared_action_taylor import Taylor, TaylorDomain
from bhsm.interface.shared_parameter_residual import linear_support


class LongitudinalQuadraticDomain(TaylorDomain):
    def __init__(self, groups, dimension):
        super().__init__(groups, dimension)
        if tuple(groups[0]) != (0, 1, 'interval'):
            raise ValueError('first common parameter must be one longitudinal interval')

    def affine(self, constant, coefficients=None, remainder=0):
        a = [arb(0)]*self.dimension if coefficients is None else list(coefficients)
        result = LongitudinalQuadratic(self, arb(constant), arb_mat(1, self.dimension, a), arb(0), arb(remainder))
        if coefficients is None:
            result._linear = result._rest = arb(0)
        return result


class LongitudinalQuadratic(Taylor):
    def __init__(self, domain, constant, coefficients, quadratic, remainder):
        super().__init__(domain, constant, coefficients, remainder)
        quadratic = arb(quadratic)
        if not quadratic.is_finite():
            raise ValueError('finite common quadratic coefficient required')
        self.q = quadratic
        self._rest = None

    def remainder_linear_bound(self):
        if self._rest is not None:
            return self._rest
        a = self.a.entries()
        a[0] = arb(0)
        self._rest = linear_support(a, self.domain.groups)
        return self._rest

    def enclosure(self):
        return self.c+arb(0, (self.linear_bound()+abs(self.q).upper()+self.r).upper())

    def support(self):
        return (abs(self.c).upper()+self.linear_bound()+abs(self.q).upper()+self.r).upper()

    def _coerce(self, other):
        if isinstance(other, LongitudinalQuadratic):
            if other.domain is not self.domain:
                raise ValueError('same common quadratic parameter identity required')
            return other
        if isinstance(other, Taylor):
            raise ValueError('do not mix first-order and quadratic arithmetic implicitly')
        if isinstance(other, (int, float, str, arb)):
            return self.domain.affine(other)
        return NotImplemented

    def __add__(self, other):
        other = self._coerce(other)
        if other is NotImplemented:
            return NotImplemented
        return LongitudinalQuadratic(self.domain, self.c+other.c, self.a+other.a, self.q+other.q, self.r+other.r)

    __radd__ = __add__

    def __neg__(self):
        return LongitudinalQuadratic(self.domain, -self.c, -self.a, -self.q, self.r)

    def __sub__(self, other):
        other = self._coerce(other)
        return NotImplemented if other is NotImplemented else self+(-other)

    def __rsub__(self, other):
        return -self+other

    def __mul__(self, other):
        if isinstance(other, (int, float, str, arb)):
            k = arb(other)
            return LongitudinalQuadratic(self.domain, self.c*k, self.a*k, self.q*k, self.r*abs(k).upper())
        other = self._coerce(other)
        if other is NotImplemented:
            return NotImplemented
        la0, lb0 = abs(self.a[0, 0]).upper(), abs(other.a[0, 0]).upper()
        lar, lbr = self.remainder_linear_bound(), other.remainder_linear_bound()
        la, lb = la0+lar, lb0+lbr
        qa, qb = abs(self.q).upper(), abs(other.q).upper()
        r = (la0*lbr+lar*(lb0+lbr)+qa*lb+qb*la+qa*qb
             +(abs(self.c).upper()+la+qa)*other.r
             +(abs(other.c).upper()+lb+qb)*self.r+self.r*other.r)
        return LongitudinalQuadratic(self.domain, self.c*other.c,
            self.a*other.c+other.a*self.c,
            self.q*other.c+other.q*self.c+self.a[0, 0]*other.a[0, 0], r)

    __rmul__ = __mul__

    def _quadratic_unary(self, value, first, second, third_bound):
        la0, lar = abs(self.a[0, 0]).upper(), self.remainder_linear_bound()
        la = la0+lar
        extra = abs(self.q).upper()+self.r
        width = la+extra
        rest_square = 2*la0*lar+lar*lar+2*la*extra+extra*extra
        r = abs(first).upper()*self.r+abs(second).upper()*rest_square/2+third_bound*width**3/6
        return LongitudinalQuadratic(self.domain, value, self.a*first,
            first*self.q+second*self.a[0, 0]**2/2, r)

    def reciprocal(self):
        full = self.enclosure()
        if full.contains(0):
            raise ArithmeticError('quadratic reciprocal crosses zero')
        return self._quadratic_unary(1/self.c, -1/self.c**2, 2/self.c**3, (6/abs(full)**4).upper())

    def exp(self):
        value = self.c.exp()
        return self._quadratic_unary(value, value, value, self.enclosure().exp().upper())

    def log(self):
        full = self.enclosure()
        if not full>0:
            raise ArithmeticError('quadratic logarithm is not positive')
        return self._quadratic_unary(self.c.log(), 1/self.c, -1/self.c**2, (2/full**3).upper())

    def __truediv__(self, other):
        other = self._coerce(other)
        return NotImplemented if other is NotImplemented else self*other.reciprocal()

    def __rtruediv__(self, other):
        return self.reciprocal()*other

    def __pow__(self, power):
        if type(power) is not int:
            return NotImplemented
        if power < 0:
            return (self**(-power)).reciprocal()
        result, base = self.domain.affine(1), self
        while power:
            if power & 1:
                result = result*base
            power >>= 1
            if power:
                base = base*base
        return result
