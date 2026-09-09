"""Bound a fixed binary64 pullback evaluation, including gradual underflow."""
import numpy as np
from flint import arb, ctx
from bhsm.interface.current_green_midpoint_coordinate_error import (
    PRECISION, _float_upper, _real_binary64,
)
from bhsm.interface.resolved_midpoint_coordinate_error import _exact_matrix, _operator_norm_upper


def _gamma(count):
    product = arb(int(count))*arb(2)**-53
    if not product < 1:
        raise ValueError('Operation count exceeds the rounding model')
    return product/(1-product)


def _norm(values):
    """Scaled sum-of-squares with an outward scalar error enclosure.

    IEEE binary64 round-to-nearest with gradual underflow is assumed. There
    are at most 2n rounded operations in the positive square/sum reduction.
    Scaling avoids overflow; the absolute underflow terms are retained.
    """
    maximum = float(np.max(np.abs(values)))
    if maximum == 0:
        return arb(0)
    n = values.size
    scaled = values/maximum
    squared_sum = float(np.sum(scaled*scaled))
    if not np.isfinite(squared_sum):
        raise RuntimeError('Nonfinite scaled reduction')
    unit, eta = arb(2)**-53, arb(2)**-1074
    gamma = _gamma(2*n)
    if not gamma < 1:
        raise ValueError('Reduction too large for this error bound')
    stored_norm = ((arb(squared_sum)+2*n*eta)/(1-gamma)).sqrt()
    # Recover the exact scaled inputs from their rounded divisions.
    return (arb(maximum)*(stored_norm+arb(n).sqrt()*eta)/(1-unit)).upper()


def fast_frobenius_upper(values):
    values = _real_binary64(values,'norm input')
    if values.size == 0:
        raise ValueError('Nonempty norm input required')
    previous = ctx.prec
    ctx.prec = PRECISION
    try:
        return _float_upper(_norm(values))
    finally:
        ctx.prec = previous


def _operator(matrix):
    # The smaller Gram matrix has the same nonzero singular values.
    value = matrix.T if matrix.shape[0] > matrix.shape[1] else matrix
    return _operator_norm_upper(_exact_matrix(value),_norm(value))


def _dot_error(inner, positive_product):
    operations = 2*inner
    eta, unit = arb(2)**-1074, arb(2)**-53
    gamma = _gamma(operations)
    if not gamma < 1 or not np.all(np.isfinite(positive_product)):
        raise RuntimeError('Absolute-product error enclosure failed')
    underflow = arb(positive_product.size).sqrt()*operations*eta/(1-operations*unit)
    # The auxiliary positive product is itself rounded. Solve its error
    # inequality before using it to bound rounding in the signed product.
    return ((gamma*_norm(positive_product)+underflow)/(1-gamma)).upper()


def difference_frobenius_upper(left,right):
    a,b = [_real_binary64(x,'difference operand') for x in (left,right)]
    if a.shape != b.shape or a.size == 0:
        raise ValueError('Matching nonempty difference operands required')
    difference = a-b
    if not np.all(np.isfinite(difference)):
        raise RuntimeError('Difference overflow; higher precision required')
    previous = ctx.prec
    ctx.prec = PRECISION
    try:
        if np.array_equal(a,b):
            return 0.0
        return _float_upper((_norm(difference)+arb(a.size).sqrt()*arb(2)**-1074)/(1-arb(2)**-53))
    finally:
        ctx.prec = previous


def addition_rounding_frobenius_upper(left,right):
    a,b = [_real_binary64(x,'addition operand') for x in (left,right)]
    if a.shape != b.shape or a.size == 0:
        raise ValueError('Matching nonempty addition operands required')
    if not np.all(np.isfinite(a+b)):
        raise RuntimeError('Addition overflow; higher precision required')
    previous = ctx.prec
    ctx.prec = PRECISION
    try:
        return _float_upper(arb(2)**-53*(_norm(a)+_norm(b))+arb(a.size).sqrt()*arb(2)**-1074)
    finally:
        ctx.prec = previous


def assemble_pullback_with_error(output,tensor,left_input,right_input=None,symmetrize=False):
    """Return a fixed three-matmul evaluation and its exact-operand error.

    Target: L [X.T Q Y], independently for each tensor output. The bound uses
    separately enclosed absolute matrix products for new dot rounding and
    signed operator norms for propagating previous-stage error. Applying the
    output map first preserves its tensor-channel scale separation.
    Optional symmetrization
    is part of the target, with its own arithmetic error.
    """
    l,q,x,y = [_real_binary64(value,name) for name,value in (
        ('output',output),('tensor',tensor),('left input',left_input),
        ('right input',left_input if right_input is None else right_input))]
    if (l.ndim != 2 or min(l.shape) == 0 or q.ndim != 3 or min(q.shape) == 0
            or x.ndim != 2 or min(x.shape) == 0 or y.ndim != 2 or min(y.shape) == 0
            or q.shape != (l.shape[1],x.shape[0],y.shape[0])
            or (symmetrize and x.shape[1] != y.shape[1])):
        raise ValueError('Compatible nonempty pullback operands required')
    previous = ctx.prec
    ctx.prec = PRECISION
    try:
        first = (l@q.reshape(q.shape[0],-1)).reshape(l.shape[0],q.shape[1],q.shape[2])
        second = np.matmul(x.T,first)
        formed = np.matmul(second,y)
        if not all(np.all(np.isfinite(v)) for v in (first,second,formed)):
            raise RuntimeError('Pullback arithmetic overflow; higher precision required')
        e1 = _dot_error(l.shape[1],np.abs(l)@np.abs(q).reshape(q.shape[0],-1))
        e2 = _dot_error(x.shape[0],np.matmul(np.abs(x.T),np.abs(first)))
        e3 = _dot_error(y.shape[0],np.matmul(np.abs(second),np.abs(y)))
        error = _operator(y)*(_operator(x)*e1+e2)+e3
        if symmetrize:
            transposed = formed.transpose(0,2,1)
            summed = formed+transposed
            result = .5*summed
            if not np.all(np.isfinite(summed)):
                raise RuntimeError('Symmetrization overflow; higher precision required')
            addition = arb(2)**-53*(2*_norm(formed))+arb(formed.size).sqrt()*arb(2)**-1074
            scaling = arb(2)**-53*.5*_norm(summed)+arb(formed.size).sqrt()*arb(2)**-1074
            error += .5*addition+scaling
        else:
            result = formed
        return result,dict(
            scope='FIXED_BINARY64_PULLBACK_ASSEMBLY_FROM_EXACT_STORED_OPERANDS_ONLY',
            arithmetic_precision_bits=PRECISION,rounding_model='IEEE_BINARY64_NEAREST_GRADUAL_UNDERFLOW',
            target_symmetrized=bool(symmetrize),
            assembly_error_frobenius_upper=_float_upper(error),
            local_dot_error_bounds=[_float_upper(v) for v in (e1,e2,e3)],
            physical_operand_errors_enclosed=False,physical_Hessian_error_enclosed=False,
            coordinate_solve_error_enclosed=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    finally:
        ctx.prec = previous
