"""Outward arithmetic for exact stored native source/adjoint contractions.

These intervals enclose the supplied finite operator expression.  They
exclude operator/target formation, temporal and continuum approximation,
physical matching, overlap and the soft Pauli limit.
"""
from __future__ import annotations
import numpy as np
from flint import arb,arb_mat,ctx


def certify_native_adjoint_contractions(matrix,forcing,readout,*,precision_bits=192):
    """Solve only the consumed adjoints and check one independent forward.

    With A z=F and A^T p=L^T, all Lz contractions equal p^T F.
    Conversion uses the exact stored binary64 entries, without replacing
    A by its rounded numerical preconditioner.  The interval LU solve
    must certify the square operator invertible.
    """
    if any(x is None for x in (matrix,forcing,readout)):
        raise ValueError('explicit real finite stored operator, load and readout required')
    A0=np.asarray(matrix);F0=np.asarray(forcing);L0=np.asarray(readout)
    if not all(np.isrealobj(x) and np.isfinite(x).all() for x in (A0,F0,L0)):
        raise ValueError('explicit real finite stored operator, load and readout required')
    if A0.ndim!=2 or A0.shape[0]!=A0.shape[1] or F0.ndim!=2 or F0.shape[0]!=len(A0) or L0.ndim!=2 or L0.shape[1]!=len(A0) or F0.shape[1]==0 or L0.shape[0]==0:
        raise ValueError('complete square system with nonempty consumed columns required')
    if type(precision_bits) is not int or precision_bits<128:raise ValueError('Arb precision>=128 required')
    previous=ctx.prec
    try:
        ctx.prec=precision_bits
        A=arb_mat(np.asarray(A0,float).tolist());F=arb_mat(np.asarray(F0,float).tolist());L=arb_mat(np.asarray(L0,float).tolist())
        p=A.transpose().solve(L.transpose())
        if not all(p[i,j].is_finite() for i in range(p.nrows()) for j in range(p.ncols())):
            raise ArithmeticError('stored adjoint inverse was not certified')
        contracted=p.transpose()*F
        forward=A.solve(arb_mat([[F[i,0]] for i in range(F.nrows())]))
        checked=L*forward
        if not all(checked[i,0].overlaps(contracted[i,0]) for i in range(checked.nrows())):
            raise ArithmeticError('independent forward and adjoint intervals disagree')
        upper=lambda x:float(np.nextafter(float(x.upper()),np.inf)) if not x.is_zero() else 0.
        lower=lambda x:float(np.nextafter(float(x.lower()),-np.inf)) if not x.is_zero() else 0.
        mid=np.array([[float(p[i,j].mid()) for j in range(p.ncols())] for i in range(p.nrows())])
        error=np.array([[upper(abs(p[i,j]-arb(float(mid[i,j])))) for j in range(p.ncols())] for i in range(p.nrows())])
        residual=A.transpose()*p-L.transpose()
        return dict(contraction_lower=np.array([[lower(contracted[i,j]) for j in range(contracted.ncols())] for i in range(contracted.nrows())]),
            contraction_upper=np.array([[upper(contracted[i,j]) for j in range(contracted.ncols())] for i in range(contracted.nrows())]),
            adjoint_export=mid,adjoint_export_error_upper=error,
            exact_stored_adjoint_residual_upper=max(upper(abs(residual[i,j])) for i in range(residual.nrows()) for j in range(residual.ncols())),
            independent_first_column_forward_adjoint_difference_upper=max(upper(abs(checked[i,0]-contracted[i,0])) for i in range(checked.nrows())),
            stored_operator_certified_invertible=True,all_consumed_pairings_enclosed=True,
            independent_first_column_intervals_overlap=True,
            physical_source_target_formation_or_Pauli_error_enclosed=False,
            precision_bits=precision_bits)
    finally:ctx.prec=previous
