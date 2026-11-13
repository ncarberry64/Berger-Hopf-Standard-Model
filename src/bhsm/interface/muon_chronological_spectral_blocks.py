"""Spectral action solves on the complete chronological block chain.

Independent complex upper/lower blocks, endpoint contacts and the original
mass pencil remain intact.  Small block Schur applications replace a full
chronological inverse.  The backend selects no physical contour or cutoff.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import lu_factor,lu_solve


def _blocks(diagonal,upper,lower):
    D=[np.asarray(x,complex)for x in diagonal]
    U=[np.asarray(x,complex)for x in upper];L=[np.asarray(x,complex)for x in lower]
    if not D or len(U)!=len(D)-1 or len(L)!=len(U):
        raise ValueError('complete ordered chronological blocks required')
    for j,A in enumerate(D):
        if A.ndim!=2 or len(A)!=A.shape[1]or not len(A)or not np.isfinite(A).all():
            raise ValueError('finite complete diagonal action blocks required')
        if j<len(U)and(U[j].shape!=(len(A),len(D[j+1]))or L[j].shape!=(len(D[j+1]),len(A))
                or not np.isfinite(U[j]).all()or not np.isfinite(L[j]).all()):
            raise ValueError('independent correctly oriented neighboring blocks required')
    return D,U,L


def chronological_spectral_factor(diagonal,upper,lower,*,balance=True):
    """Factor a supplied K-zM chain, retaining every temporal block.

    Positive scalar congruences are numerical equilibration only; they do
    not replace the complex action density or select a positive domain.
    """
    D,U,L=_blocks(diagonal,upper,lower)
    scales=np.array([1/np.sqrt(max(np.max(abs(A)),np.finfo(float).tiny))
        if balance else 1. for A in D])
    Ds=[t*t*A for t,A in zip(scales,D)]
    Us=[scales[i]*A*scales[i+1]for i,A in enumerate(U)]
    Ls=[scales[i+1]*A*scales[i]for i,A in enumerate(L)]
    inverse=[];factors=[];schur=[]
    phase=1.+0j;logabs=0.
    for i,A in enumerate(Ds):
        S=A.copy()if i==0 else A-Ls[i-1]@inverse[i-1]@Us[i-1]
        f=lu_factor(S)
        if np.any(np.diag(f[0])==0):raise np.linalg.LinAlgError('singular chronological Schur block at supplied spectral point')
        inv=lu_solve(f,np.eye(len(S),dtype=complex))
        sign,labs=np.linalg.slogdet(S);phase*=sign;logabs+=labs
        inverse.append(inv);factors.append(f);schur.append(S)
    logabs-=sum(2*len(A)*np.log(t)for A,t in zip(D,scales))
    return dict(diagonal=D,upper=U,lower=L,balanced_upper=Us,balanced_lower=Ls,
        inverse_Schur_blocks=inverse,Schur_blocks=schur,LU=factors,scales=scales,
        determinant_phase=phase,log_absolute_determinant=float(logabs),
        determinant_phase_is_not_relative_eta_completion=True,
        temporal_blocks_retained=len(D),physical_domain_or_spectral_point_selected=False)


def chronological_selected_inverse(factor):
    """Return all diagonal/nearest blocks required by local action traces."""
    f=factor;I=f['inverse_Schur_blocks'];U=f['balanced_upper'];L=f['balanced_lower']
    n=len(I);D=[None]*n;up=[None]*(n-1);low=[None]*(n-1);D[-1]=I[-1].copy()
    for j in range(n-2,-1,-1):
        up[j]=-I[j]@U[j]@D[j+1]
        low[j]=-D[j+1]@L[j]@I[j]
        D[j]=I[j]-up[j]@L[j]@I[j]
    t=f['scales']
    return dict(diagonal=[t[j]**2*A for j,A in enumerate(D)],
        upper=[t[j]*t[j+1]*A for j,A in enumerate(up)],
        lower=[t[j+1]*t[j]*A for j,A in enumerate(low)],
        independent_reverse_blocks_retained=True,full_chronological_inverse_constructed=False)


def chronological_source_solve(factor,rhs):
    """Apply the full chain to source columns without a full inverse."""
    f=factor;n=len(f['diagonal']);b=[np.asarray(x,complex)for x in rhs]
    if len(b)!=n or any(x.ndim not in(1,2)or len(x)!=len(f['diagonal'][j])
            or not np.isfinite(x).all()for j,x in enumerate(b)):
        raise ValueError('all chronological source blocks with one common column shape required')
    if any(x.shape[1:]!=b[0].shape[1:]for x in b):raise ValueError('source column shapes differ')
    y=[];t=f['scales'];LU=f['LU'];U=f['balanced_upper'];L=f['balanced_lower']
    for j,x in enumerate(b):
        y.append(t[j]*x if j==0 else t[j]*x-L[j-1]@lu_solve(LU[j-1],y[j-1]))
    out=[None]*n;out[-1]=lu_solve(LU[-1],y[-1])
    for j in range(n-2,-1,-1):out[j]=lu_solve(LU[j],y[j]-U[j]@out[j+1])
    return [t[j]*x for j,x in enumerate(out)]


def chronological_action_trace(selected,diagonal,upper,lower):
    """Tr((K-zM)^-1 delta(K-zM)), retaining both off-diagonal orders."""
    D,U,L=_blocks(diagonal,upper,lower)
    if len(D)!=len(selected['diagonal']):raise ValueError('same complete action chain required')
    value=sum(np.einsum('ij,ji->',A,B)for A,B in zip(selected['diagonal'],D))
    value+=sum(np.einsum('ij,ji->',A,B)for A,B in zip(selected['lower'],U))
    value+=sum(np.einsum('ij,ji->',A,B)for A,B in zip(selected['upper'],L))
    return complex(value)


def chronological_source_residual(factor,solution,rhs):
    """Export original rows; small residuals do not certify a physical domain."""
    D,U,L=(factor[k]for k in('diagonal','upper','lower'));x=solution;b=rhs
    return [D[j]@x[j]-b[j]+(L[j-1]@x[j-1]if j else 0)
        +(U[j]@x[j+1]if j<len(U)else 0)for j in range(len(D))]


def homogeneous_scalar_degree_reduction(degree):
    """Exact owned PW spectator reduction; no covariance/carrier is chosen.

    Existing scalar E_a=2iJ_a acts on m, with k a spectator. Homogeneous
    spin/field coefficients preserve that tensor identity. Only the n0
    mean source is reduced here; a nonconstant source needs its full Gaunt
    transitions before any trace or source application is reduced.
    """
    from .muon_intrinsic_scalar_discretization import (
        _spin_matrices,real_scalar_basis_transform,scalar_angular_derivative_matrices,
        scalar_section_labels,real_scalar_basis_labels)
    if type(degree)is not int or degree<0:raise ValueError('complete integer PW degree required')
    n=degree;labels=scalar_section_labels(n);real_labels=real_scalar_basis_labels(n)
    ci=np.array([j for j,l in enumerate(labels)if l[0]==n])
    ri=np.array([j for j,l in enumerate(real_labels)if l[0]==n])
    U=real_scalar_basis_transform(n)[np.ix_(ci,ri)]
    E=2j*_spin_matrices(n)
    full=scalar_angular_derivative_matrices(n)[:,ci][:,:,ci]
    expected=np.array([np.kron(e,np.eye(n+1))for e in E])
    if not np.array_equal(full,expected):raise ArithmeticError('owned spectator decomposition changed')
    return dict(angular_derivatives=E,trace_multiplicity=n+1,
        real_to_complex_coefficient_map=U,full_complex_angular_derivatives=full,
        full_real_angular_derivatives=(U.conj().T@full@U).real,
        active_weight_labels=np.arange(n,-n-1,-2),spectator_weight_labels=np.arange(n,-n-1,-2),
        homogeneous_and_complete_degree_scope=True,
        nonconstant_source_reduced_without_Gaunt=False,physical_state_selected=False)
