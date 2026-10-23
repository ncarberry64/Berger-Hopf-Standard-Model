"""Small-memory full-chain current and literal transpose-adjoint solves.

Every supplied Gauss/frame/corner row stays in its original block. Only
the diagonal array is consumed when explicitly requested. No full inverse,
Hermitian dual, boundary deletion, or native heat domain is introduced.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import lu_factor,lu_solve


def factor_literal_current_chain(diagonal,upper,lower,*,consume_diagonal=False):
    """Block LU of a complete independently directed chain.

    This stores LU diagonal blocks rather than LU, Schur AND inverse Schur
    copies. Numerical coordinate congruence belongs to the calling action
    application and must also be applied to its sources and residuals.
    """
    D=np.asarray(diagonal,complex);U=np.asarray(upper,complex);L=np.asarray(lower,complex)
    if (D.ndim!=3 or D.shape[1]!=D.shape[2]or not len(D)
            or U.shape!=(len(D)-1,D.shape[1],D.shape[1])or L.shape!=U.shape
            or any(not np.isfinite(a).all()for a in(D,U,L))):
        raise ValueError('complete independently directed finite action blocks required')
    if not consume_diagonal:D=D.copy()
    elif not D.flags.writeable:raise ValueError('explicitly consumed diagonal must be writable')
    pivots=np.empty(D.shape[:2],np.int32);minimum=[]
    for j in range(len(D)):
        S=D[j].copy()
        if j:S-=L[j-1]@lu_solve((D[j-1],pivots[j-1]),U[j-1])
        f,p=lu_factor(S)
        if np.any(np.diag(f)==0):raise np.linalg.LinAlgError('original chain has a singular Schur block')
        D[j]=f;pivots[j]=p;minimum.append(float(min(abs(np.diag(f)))))
    return dict(LU_diagonal=D,pivots=pivots,upper=U,lower=L,
        minimum_LU_pivots=np.array(minimum),all_original_rows_retained=True,
        physical_covariance_or_heat_domain_selected=False)


def solve_literal_current_chain(factor,rhs,*,transpose=False):
    """Apply the action or its analytic transpose to all supplied columns."""
    f=factor;D,U,L,P=(f[k]for k in('LU_diagonal','upper','lower','pivots'))
    b=np.asarray(rhs,complex)
    if b.ndim not in(2,3)or b.shape[:2]!=D.shape[:2]or not np.isfinite(b).all():
        raise ValueError('every original temporal source block must be supplied')
    y=np.empty_like(b);n=len(D)
    if not transpose:
        y[0]=b[0]
        for j in range(1,n):y[j]=b[j]-L[j-1]@lu_solve((D[j-1],P[j-1]),y[j-1])
        y[-1]=lu_solve((D[-1],P[-1]),y[-1])
        for j in range(n-2,-1,-1):y[j]=lu_solve((D[j],P[j]),y[j]-U[j]@y[j+1])
    else:
        y[0]=lu_solve((D[0],P[0]),b[0],trans=1)
        for j in range(1,n):y[j]=lu_solve((D[j],P[j]),b[j]-U[j-1].T@y[j-1],trans=1)
        for j in range(n-2,-1,-1):y[j]-=lu_solve((D[j],P[j]),L[j].T@y[j+1],trans=1)
    return y
