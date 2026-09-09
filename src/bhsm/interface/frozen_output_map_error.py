"""Enclose frozen Hermite--Simpson output-map construction and its cross terms."""
import numpy as np
from flint import arb, arb_mat, ctx
from bhsm.interface.current_green_midpoint_coordinate_error import (
    PRECISION, _float_upper, _real_binary64,
)
from bhsm.interface.resolved_midpoint_coordinate_error import _exact_matrix, _operator_norm_upper


def bound_output_map_errors(right, test, ambient, step, approximate_maps):
    """Compare stored left/right/midpoint maps to their exact frozen formulas.

    B=-R^-1 T, J=B A; the maps are h B/6 +/- h^2 J/12 and 2 h B/3.
    Every supplied binary64 operand is exact. Physical input evaluation and
    midpoint kinematic-map construction remain separate obligations.
    """
    r,t,a,p = [_real_binary64(value,name) for name,value in (
        ('right',right),('test',test),('ambient',ambient),('output maps',approximate_maps))]
    h = _real_binary64(step,'step')
    if (r.ndim != 2 or min(r.shape) == 0 or r.shape[0] != r.shape[1]
            or t.ndim != 2 or t.shape[0] != r.shape[0] or t.shape[1] == 0
            or a.shape != (t.shape[1],t.shape[1]) or p.shape != (3,*t.shape)
            or h.shape != () or float(h) <= 0):
        raise ValueError('Compatible output maps and positive step required')
    previous = ctx.prec
    ctx.prec = PRECISION
    try:
        rm = _exact_matrix(r)
        inverse = rm.inv()
        residual = arb_mat(np.eye(r.shape[0],dtype=int).tolist()) - rm*inverse
        upper = max(sum(abs(residual[i,j]) for j in range(r.shape[0])).upper()
                    for i in range(r.shape[0]))
        if not (upper.is_finite() and upper < 1):
            raise RuntimeError('Frozen output-map inverse could not be certified')
        b = -inverse*_exact_matrix(t)
        incidence = b*_exact_matrix(a)
        exact_h = arb(float(h))
        targets = [b*(exact_h/6)+incidence*(exact_h**2/12),
                   b*(exact_h/6)-incidence*(exact_h**2/12), b*(2*exact_h/3)]
        rows = []
        for target,stored in zip(targets,p):
            error = target-_exact_matrix(stored)
            if not all(error[i,j].is_finite() for i in range(t.shape[0]) for j in range(t.shape[1])):
                raise RuntimeError('Nonfinite output-map error enclosure')
            frob = sum(abs(error[i,j]).upper()**2 for i in range(t.shape[0])
                       for j in range(t.shape[1])).sqrt().upper()
            scalar = sum(abs(error[i,t.shape[1]-1]).upper()**2 for i in range(t.shape[0])).sqrt().upper()
            rows.append(dict(operator_error_upper=_float_upper(_operator_norm_upper(error,frob)),
                             frobenius_error_upper=_float_upper(frob),
                             scalar_column_error_upper=_float_upper(scalar)))
        return dict(scope='FROZEN_OUTPUT_MAP_CONSTRUCTION_FROM_EXACT_STORED_OPERANDS_ONLY',
                    arithmetic_precision_bits=PRECISION,
                    inverse_residual_infinity_upper=_float_upper(upper),
                    maps=dict(zip(('left','right','midpoint'),rows)),
                    physical_operand_errors_enclosed=False)
    finally:
        ctx.prec = previous


def bound_output_error_pullback(output_error, scalar_column_error,
                                retained_norm, complement_norm, tensor_norms,
                                projection_error, addition_error):
    """Apply output error to the entire coordinate/storage-corrected tensor.

    Retained/complement norms must bound exact coordinates, including solve
    error. UU storage errors are a full projection error plus a scalar-only
    addition error. The result is Frobenius error before the pair-input factor.
    The caller must verify all supplied scalar bounds.
    """
    values = [_real_binary64(v,'nonnegative bound') for v in
              (output_error,scalar_column_error,retained_norm,complement_norm,
               projection_error,addition_error)]
    q = _real_binary64(tensor_norms,'tensor norm bounds')
    if (any(v.shape != () or float(v)<0 for v in values) or q.shape != (3,) or np.any(q<0)):
        raise ValueError('Nonnegative scalar bounds and three tensor norms required')
    previous = ctx.prec
    ctx.prec = PRECISION
    try:
        e,es,u,c,projection,addition = [arb(float(v)) for v in values]
        uu,cu,cc = [arb(float(v)) for v in q]
        return _float_upper(u*u*(e*(uu+projection)+es*addition)
                            +e*(2*u*c*cu+c*c*cc))
    finally:
        ctx.prec = previous
