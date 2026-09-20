"""Cancel base-state/input products using shared implicit residual models.

For G(theta)=0 on the retained solution graph and a freely chosen constant
matrix B, f(theta,u) equals f(theta,u)-G(theta)^T B u. The residual Taylor
remainders are retained as individual input-linear terms until the physical
input map or a specified direction is substituted. This is a value bound.
"""
from flint import arb, arb_mat
from bhsm.interface.input_linear_taylor import InputLinearTaylor, vector_norm
from bhsm.interface.joint_output_support import box_image_norm


class BaseResidualBlock:
    def __init__(self, residuals, state_indices):
        self.residuals = tuple(residuals)
        self.indices = tuple(state_indices)
        if not self.residuals or len(self.indices) != len(self.residuals):
            raise ValueError('one full base-state block and its equations required')
        self.domain = self.residuals[0].domain
        if (len(set(self.indices)) != len(self.indices)
                or any(not 0 <= i < self.domain.dimension for i in self.indices)
                or any(g.domain is not self.domain for g in self.residuals)):
            raise ValueError('distinct base coordinates on one common domain required')
        size = len(self.residuals)
        jacobian = arb_mat(size, size,
            [g.a[0, i] for g in self.residuals for i in self.indices])
        # This inverse only proposes free point covectors. Its rounding and
        # the full interval Jacobian remain in the corrected coefficients.
        self.point_inverse_transpose = jacobian.transpose().mid().inv().mid()
        self.constants = arb_mat(size, 1, [g.c for g in self.residuals])
        self.coefficients = arb_mat(size, self.domain.dimension,
            [v for g in self.residuals for v in g.a.entries()])

    def cancel(self, value):
        if value.domain is not self.domain:
            raise ValueError('the original common state domain must be retained')
        target = arb_mat(len(self.indices), value.c.ncols(),
            [value.a[i, j] for i in self.indices for j in range(value.c.ncols())])
        beta = (self.point_inverse_transpose * target).mid()
        c = value.c - self.constants.transpose() * beta
        a = value.a - self.coefficients.transpose() * beta
        polynomial = InputLinearTaylor(value.domain, c, a, value.r, value.input_groups)
        weighted = arb_mat(beta.nrows(), beta.ncols(),
            [beta[i, j] * self.residuals[i].r for i in range(beta.nrows())
             for j in range(beta.ncols())])
        # The returned polynomial deliberately excludes the added residual
        # tail. A caller must add weighted_tail_* before reporting a bound.
        return polynomial, weighted


def weighted_tail_at_input(weighted, direction):
    if direction.nrows() != weighted.ncols() or direction.ncols() != 1:
        raise ValueError('complete common input direction required')
    return sum((abs(v).upper() for v in (weighted * direction).entries()), arb(0)).upper()


def weighted_tail_on_physical_input(weighted, maps, physical_dimension=74):
    if not 0 < physical_dimension <= weighted.ncols():
        raise ValueError('positive physical input dimension required')
    physical = arb_mat(weighted.nrows(), physical_dimension,
        [weighted[i, j] for i in range(weighted.nrows()) for j in range(physical_dimension)])
    used = set()
    for offset, mapping in maps:
        slots = list(range(offset, offset + mapping.nrows()))
        if (not slots or mapping.ncols() != physical_dimension
                or offset < physical_dimension or slots[-1] >= weighted.ncols()
                or used.intersection(slots)
                or any(not v.is_finite() for v in mapping.entries())):
            raise ValueError('finite disjoint complete common-input maps required')
        used.update(slots)
        physical += arb_mat(weighted.nrows(), len(slots),
            [weighted[i, j] for i in range(weighted.nrows()) for j in slots]) * mapping
    if used != set(range(physical_dimension, weighted.ncols())):
        raise ValueError('every auxiliary input coordinate must be mapped')
    separated = sum((vector_norm([physical[i, j] for j in range(physical_dimension)])
                     for i in range(physical.nrows())), arb(0)).upper()
    return min(separated, box_image_norm(physical.transpose()))
