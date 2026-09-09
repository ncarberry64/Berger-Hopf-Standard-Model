"""Outward stored-product covariance balls and fixed-axis projections."""
import numpy as np
from flint import arb,arb_mat,ctx
from bhsm.interface.current_green_midpoint_coordinate_error import (
    PRECISION,_float_upper,_real_binary64,
)
from bhsm.interface.stored_pullback_assembly_error import _gamma


def product_radius_about_stored(left,right,stored):
    """Enclose exact A B about an arbitrary supplied binary64 midpoint.

    A fresh signed and absolute product give componentwise dot-error bounds.
    The exact difference from the saved midpoint is added with Arb arithmetic.
    All operands are exact stored arrays, not physical evaluation enclosures.
    """
    a,b,m=[_real_binary64(v,name) for name,v in
           (('left',left),('right',right),('stored midpoint',stored))]
    if (any(v.ndim!=2 or min(v.shape)==0 for v in (a,b,m))
            or a.shape[1]!=b.shape[0] or m.shape!=(a.shape[0],b.shape[1])):
        raise ValueError('Compatible nonempty product operands required')
    observed=a@b
    positive=np.abs(a)@np.abs(b)
    if not (np.all(np.isfinite(observed)) and np.all(np.isfinite(positive))):
        raise RuntimeError('Product overflow; higher precision required')
    previous=ctx.prec
    ctx.prec=PRECISION
    try:
        operations=2*a.shape[1]
        gamma=_gamma(operations)
        if not gamma<1:
            raise ValueError('Product too large for rounding bound')
        underflow=operations*arb(2)**-1074/(1-operations*arb(2)**-53)
        radius=np.empty_like(m)
        for i in range(m.shape[0]):
            for j in range(m.shape[1]):
                rounding=(gamma*arb(float(positive[i,j]))+underflow)/(1-gamma)
                difference=abs(arb(float(observed[i,j]))-arb(float(m[i,j])))
                radius[i,j]=_float_upper(rounding+difference)
        return radius
    finally:
        ctx.prec=previous


def interval_matrix(midpoint,radius):
    """Materialize externally verified nonnegative componentwise radii."""
    m,r=[_real_binary64(v,'matrix ball') for v in (midpoint,radius)]
    if m.ndim!=2 or min(m.shape)==0 or r.shape!=m.shape or np.any(r<0):
        raise ValueError('Matching nonempty matrix and nonnegative radii required')
    return arb_mat([[arb(float(x),float(e)) for x,e in zip(row,errors)]
                    for row,errors in zip(m,r)])


def projected_covariance_upper(covariance,gram,pullback_axis,axis_squared):
    """Project G C G.T using Gram=G.T G and w=G.T e.

    The transverse map is exactly I-e e.T. Stored normalized axes need not
    have exact unit norm, so its squared norm is trace(G C G.T)+(||e||^2-2) l2,
    not trace-l2. Gram and w must describe the same externally verified G.
    """
    size=covariance.nrows()
    if (size==0 or covariance.ncols()!=size or gram.nrows()!=size or gram.ncols()!=size
            or pullback_axis.nrows()!=size or pullback_axis.ncols()!=1):
        raise ValueError('Compatible covariance projection operands required')
    longitudinal=(pullback_axis.transpose()*covariance*pullback_axis)[0,0]
    trace=sum(gram[i,j]*covariance[j,i] for i in range(size) for j in range(size))
    transverse=trace+(axis_squared-2)*longitudinal
    if not all(v.is_finite() and v.upper()>=0 for v in (longitudinal,transverse)):
        raise RuntimeError('Finite nonnegative covariance upper bounds required')
    return longitudinal.upper().sqrt().upper(),transverse.upper().sqrt().upper()
