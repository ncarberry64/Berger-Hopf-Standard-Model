"""Formal anchor derivatives retaining one complete linear input space.

These jets carry NO neighborhood bounds. They are used only to propose
residual covectors; a separate outward residual evaluation is required.
"""
from contextlib import contextmanager
from flint import arb, arb_mat
from bhsm.interface.coupled_action_output_adjoint import FirstJet
from bhsm.interface.shared_action_taylor import scalar_taylor_action


class InputLinearJet:
    def __init__(self, constant, derivative):
        if constant.nrows() != 1 or constant.ncols() != derivative.ncols():
            raise ValueError('complete linear input coefficient rows required')
        self.c, self.a = constant, derivative

    def __add__(self, other):
        if isinstance(other, (int, arb)) and other == 0:
            return self
        if isinstance(other, FirstJet) and other.c.is_zero() and all(v.is_zero() for v in other.a.entries()):
            return self
        if not isinstance(other, InputLinearJet):
            return NotImplemented
        return InputLinearJet(self.c+other.c, self.a+other.a)

    __radd__ = __add__

    def __neg__(self):
        return InputLinearJet(-self.c, -self.a)

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        if isinstance(other, InputLinearJet):
            raise ValueError('formal expression must remain linear in the input')
        if isinstance(other, FirstJet):
            return InputLinearJet(self.c*other.c,
                                  self.a*other.c+other.a.transpose()*self.c)
        if isinstance(other, (int, float, str, arb)):
            return InputLinearJet(self.c*arb(other), self.a*arb(other))
        return NotImplemented

    __rmul__ = __mul__

    def __truediv__(self, other):
        return self * (other.reciprocal() if isinstance(other, FirstJet) else 1/arb(other))


class ScalarJet(FirstJet):
    """FirstJet arithmetic with explicit dispatch to the linear input module."""
    @staticmethod
    def wrap(value):
        return ScalarJet(value.c, value.a) if isinstance(value, FirstJet) else value

    def __add__(self, other):
        if isinstance(other, InputLinearJet):
            return other+self
        return self.wrap(super().__add__(other))

    __radd__ = __add__

    def __neg__(self):
        return self.wrap(super().__neg__())

    def __mul__(self, other):
        if isinstance(other, InputLinearJet):
            return other*self
        return self.wrap(super().__mul__(other))

    __rmul__ = __mul__

    def reciprocal(self):
        return self.wrap(super().reciprocal())

    def __rtruediv__(self, other):
        return self.reciprocal()*other

    def exp(self):
        value = self.c.exp()
        return ScalarJet(value, self.a*value)

    def log(self):
        if not self.c > 0:
            raise ArithmeticError('positive anchor required')
        return ScalarJet(self.c.log(), self.a/self.c)

    def __pow__(self, power):
        if type(power) is not int:
            return NotImplemented
        if power == 0:
            return ScalarJet(arb(1), arb_mat(1, self.a.ncols()))
        return ScalarJet(self.c**power, self.a*(power*self.c**(power-1)))


@contextmanager
def input_linear_anchor_action(module):
    """Use the unchanged scalar action with formal U jets and one input leg."""
    with scalar_taylor_action(module):
        previous_a, previous_mixed = module._a, module.Mixed

        class Mixed(previous_mixed):
            def reciprocal(self):
                value = self.d[0]
                if not isinstance(value, ScalarJet):
                    return super().reciprocal()
                outer, factorial = [arb(0)], 1
                for order in range(1, self.directions+1):
                    factorial *= order
                    outer.append((-1)**order*factorial/value**(order+1))
                return self._unary(value.reciprocal(), outer)

            def positive_power(self, power):
                value = self.d[0]
                if not isinstance(value, ScalarJet):
                    return super().positive_power(power)
                p, coefficient, outer = arb(power), arb(1), [arb(0)]
                for order in range(1, self.directions+1):
                    coefficient *= p-(order-1)
                    outer.append(coefficient*((p-order)*value.log()).exp())
                return self._unary((p*value.log()).exp(), outer)

        # The scalar adapter's closure creates its original Mixed subclass.
        # Replace that factory too so anchor unary methods dispatch here.
        previous_variables = module._local_variables
        def variables(values, directions, legs):
            if legs is None:
                if directions:
                    raise ValueError('explicit legs required')
                return [Mixed.constant(v, 0) for v in values]
            return [Mixed.affine(v, [leg[i] for leg in legs]) for i, v in enumerate(values)]

        module._a = lambda v: v if isinstance(v, (ScalarJet, InputLinearJet)) else previous_a(v)
        module.Mixed, module._local_variables = Mixed, variables
        try:
            yield
        finally:
            module._a, module.Mixed, module._local_variables = previous_a, previous_mixed, previous_variables
