"""Stable common-cutoff kernels for the reached mixed Green insertions.

These are scalar proper-time integration identities. Their use does not
choose a field operator, statistics, native completion or physical cutoff.
"""
from __future__ import annotations
import math
import numpy as np
from flint import arb,ctx


def _real_points(value):
    data=np.asarray(value)
    if data.dtype.kind not in 'fiu':
        raise ValueError('real point-valued spectra and cutoff required; complex and interval operands are not accepted')
    return data.astype(float,copy=False)


def _data(eigenvalues,cutoff,terms):
    if len(eigenvalues) not in (2,3):raise ValueError('two or three reached Green factors required')
    arrays=np.broadcast_arrays(*[_real_points(a) for a in eigenvalues])
    cutoff_data=_real_points(cutoff)
    if cutoff_data.ndim:raise ValueError('one explicit scalar common cutoff required')
    c=float(cutoff_data)
    if any(a.size==0 or not np.isfinite(a).all() or np.any(a<=0) for a in arrays) or not np.isfinite(c) or c<0:
        raise ValueError('positive actual spectra and explicit nonnegative common cutoff required')
    if type(terms) is not int or not 2<=terms<=12:raise ValueError('resolved positive-series order required')
    m=np.maximum.reduce(arrays);rho=[(m-a)/m for a in arrays]
    if max(float(np.max(a)) for a in rho)>.125:
        raise ValueError('nearby positive spectra required; use direct simplex integration for wider ranges')
    z=c*m
    if np.max(z)>600:raise ValueError('use interval exponential arithmetic outside resolved binary range')
    # Complete homogeneous polynomials: generating function prod(1-rho_i*t)^-1.
    h=[np.ones_like(m)]+[np.zeros_like(m) for _ in range(terms-1)]
    for d in rho:
        for j in range(1,terms):h[j]=h[j]+d*h[j-1]
    return arrays,c,m,z,h


def _global_series_tail(arrays,cutoff,terms,*,boundary=False,precision_bits=192):
    """Outward exact-stored-spectrum truncation bound, independent of quadrature."""
    n=len(arrays);low=min(float(np.min(a)) for a in arrays);high=max(float(np.max(a)) for a in arrays)
    with ctx.workprec(precision_bits):
        p=arb(low);D=arb(high)-p;c=arb(cutoff)
        if D.is_zero() or c.is_zero() and boundary:return 0.
        if boundary:
            tail=c**(n-1)*(c*D)**terms/math.factorial(terms)/(math.factorial(n-1))*(-c*p).exp()
        else:
            z=c*p;poly=arb(1);power=arb(1)
            for j in range(1,n+terms):
                power*=z/j;poly+=power
            tail=math.comb(n+terms-1,n-1)*D**terms/p**(n+terms)*(-z).exp()*poly
        return float(np.nextafter(float(tail.upper()),math.inf)) if not tail.is_zero() else 0.


def common_total_cutoff_green_kernel(*eigenvalues,cutoff,terms=4):
    """Evaluate integral_{u_i>=0,sum u_i>=c} exp(-sum p_i*u_i) du.

    L2=-g_c[p,q], L3=g_c[p,q,r], g_c(p)=exp(-cp)/p.
    The positive expansion about m=max(p_i) avoids near-coincident
    divided-difference cancellation. All insertion orders use one total
    cutoff. The tail bound is rigorous exact-stored-spectrum SERIES
    truncation only; binary assembly/eigensolvers are outside that bound.
    """
    arrays,c,m,z,h=_data(eigenvalues,cutoff,terms);n=len(arrays)
    if c==0:
        return dict(value=1/np.prod(np.stack(arrays),axis=0),positive_series_truncation_upper=0.,
            common_total_cutoff=True,error_scope='exact zero-cutoff product identity; binary arithmetic and operand formation not enclosed')
    poly=np.ones_like(m);power=np.ones_like(m)
    for j in range(1,n):power*=z/j;poly+=power
    total=h[0]*poly
    for j in range(1,terms):
        power*=z/(n-1+j);poly+=power;total+=h[j]*poly
    value=np.exp(-z)*total/m**n
    return dict(value=value,positive_series_truncation_upper=_global_series_tail(arrays,c,terms),
        series_terms=terms,common_total_cutoff=True,
        error_scope='outward exact-stored-spectrum positive-series tail only; binary evaluation, eigensystem, field/vertex/domain and physical cutoff errors excluded')


def common_total_cutoff_boundary_kernel(*eigenvalues,cutoff,terms=4):
    """Evaluate -partial_c L_n: c^(n-1) int_simplex exp(-c sum s_i*p_i) ds.

    Its negative supplies the cutoff motion. No zero physical cutoff jet
    is assumed by this utility.
    """
    arrays,c,m,z,h=_data(eigenvalues,cutoff,terms);n=len(arrays)
    power=np.ones_like(m)/math.factorial(n-1);total=h[0]*power
    for j in range(1,terms):power*=z/(n-1+j);total+=h[j]*power
    return dict(value=c**(n-1)*np.exp(-z)*total,
        positive_series_truncation_upper=_global_series_tail(arrays,c,terms,boundary=True),
        sign_in_cutoff_derivative=-1,series_terms=terms,
        error_scope='outward exact-stored-spectrum exponential-series tail only; binary evaluation and physical cutoff selection/motion excluded')


def certified_three_green_point(p,q,r,cutoff,*,precision_bits=192):
    """Enclose one exact binary spectral triple by Hermite divided difference."""
    points=[_real_points(a) for a in (p,q,r,cutoff)]
    if any(a.ndim for a in points):raise ValueError('one real point per spectral argument and cutoff required')
    values=sorted([float(a) for a in points[:3]]);c=float(points[3])
    if not np.isfinite(values+[c]).all() or min(values)<=0 or c<0:raise ValueError('positive finite triple and nonnegative cutoff required')
    with ctx.workprec(precision_bits):
        x=[arb(v) for v in values];C=arb(c)
        g=lambda a:(-C*a).exp()/a
        gp=lambda a:-(-C*a).exp()*(C/a+1/a**2)
        if values[0]==values[2]:
            value=(-C*x[0]).exp()*(C**2/(2*x[0])+C/x[0]**2+1/x[0]**3)
        else:
            first=gp(x[0]) if values[0]==values[1] else (g(x[1])-g(x[0]))/(x[1]-x[0])
            second=gp(x[1]) if values[1]==values[2] else (g(x[2])-g(x[1]))/(x[2]-x[1])
            value=(second-first)/(x[2]-x[0])
        if not value.is_finite() or not value>0:raise ArithmeticError('positive exact spectral kernel not enclosed')
        return [float(np.nextafter(float(value.lower()),-math.inf)),
                float(np.nextafter(float(value.upper()),math.inf))]


def rigorous_frobenius_upper(matrix,*,precision_bits=192):
    """Bound the norm of exact stored binary floating coefficients outward.

    A maximum of real/imaginary components introduces no dot-product
    roundoff. N(max Re**2+max Im**2) bounds the squared Frobenius norm.
    This deliberately conservative bound encloses these stored arrays,
    not the unrounded action matrices or numerical eigenvectors.
    """
    a=np.asarray(matrix)
    if a.dtype.kind not in 'fc' or a.dtype.itemsize>(16 if a.dtype.kind=='c' else 8):
        raise ValueError('stored real/complex binary32/64 floating coefficients required')
    if not np.isfinite(a).all():raise ValueError('finite stored coefficients required')
    if a.size==0:return 0.
    r=float(np.max(np.abs(a.real)));i=float(np.max(np.abs(a.imag)))
    with ctx.workprec(precision_bits):
        value=(arb(int(a.size))*(arb(r)**2+arb(i)**2)).sqrt()
        return float(np.nextafter(float(value.upper()),math.inf)) if not value.is_zero() else 0.


def outward_positive_product_sum(terms,*,precision_bits=192):
    """Outward sum of products of nonnegative stored point bounds."""
    with ctx.workprec(precision_bits):
        value=arb(0)
        for factors in terms:
            product=arb(1)
            for factor in factors:
                point=_real_points(factor)
                if point.ndim or not np.isfinite(point) or point<0:
                    raise ValueError('finite nonnegative scalar point bounds required')
                product*=arb(float(point))
            value+=product
        return float(np.nextafter(float(value.upper()),math.inf)) if not value.is_zero() else 0.


def contraction_series_tail_upper(kernel_tail,left,middle,right,gram,*,precision_bits=192):
    """Bound one exact-stored L.(entrywise kernel tail*M).R contraction.

    Frobenius submultiplicativity gives tail*||L||F*||M||F*||R||F/Gram.
    Gram division and multiplication use Arb, including the last export.
    Assembly, eigensystem and binary contraction errors are separate.
    """
    t=_real_points(kernel_tail);g=_real_points(gram)
    if t.ndim or g.ndim or not np.isfinite([t,g]).all() or t<0 or g<=0:
        raise ValueError('finite nonnegative kernel tail and positive actual point Gram required')
    norms=[rigorous_frobenius_upper(a,precision_bits=precision_bits) for a in (left,middle,right)]
    with ctx.workprec(precision_bits):
        value=arb(float(t))/arb(float(g))
        for norm in norms:value*=arb(norm)
        return float(np.nextafter(float(value.upper()),math.inf)) if not value.is_zero() else 0.
