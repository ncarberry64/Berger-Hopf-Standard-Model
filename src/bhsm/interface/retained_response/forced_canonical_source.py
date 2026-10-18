"""Forced Gauss elimination and moving-lift canonical evolution.

Source convention: BHSM muon_parent_maxwell_full_retarded.py,
L=1/2 qdot^T M qdot+q^T B qdot+1/2 q^T K q+f^T q+h^T qdot+c.
Algebraic temporal coordinates have no time momentum. No gauge pseudo-inverse
or new boundary condition is chosen. All arrays/derivatives are explicit.
The functions below are analytic-bilinear: T, not Hermitian conjugation.
They are not a physical BHSM background, quantum propagator or muon result.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.linalg import solve

@dataclass(frozen=True)
class Form:
    M: np.ndarray
    B: np.ndarray
    K: np.ndarray
    f: np.ndarray
    h: np.ndarray
    c: complex = 0.

    def __post_init__(self):
        for name in ('M','B','K','f','h'):
            a=np.asarray(getattr(self,name))
            if a.dtype.kind not in 'fci' or not np.isfinite(a).all():
                raise ValueError(name+' must contain finite explicit numeric operands')
            object.__setattr__(self,name,a)
        n=self.f.size
        if self.f.shape!=(n,) or self.h.shape!=(n,) or any(getattr(self,k).shape!=(n,n) for k in ('M','B','K')):
            raise ValueError('form shapes are inconsistent')
        if not np.isfinite(self.c):raise ValueError('finite scalar constant required')
        # Numeric tolerance checks representation symmetry, not physical admission.
        for name in ('M','K'):
            a=getattr(self,name)
            if np.max(abs(a-a.T))>2e-12*max(1.,np.max(abs(a))):
                raise ValueError(name+' is not symmetric in the stated analytic pairing')

    def action(self,q,qd):
        return .5*qd@self.M@qd+q@self.B@qd+.5*q@self.K@q+self.f@q+self.h@qd+self.c

    def momentum(self,q,qd):return self.M@qd+self.B.T@q+self.h
    def position_gradient(self,q,qd):return self.B@qd+self.K@q+self.f


def forced_gauss_schur(full:Form, gauss_count:int):
    """Eliminate the original algebraic rows, including their additive load.

    A=Kyy, C=Kyz, D=Byz; y=-solve(A,C z+D zdot+f_y).
    A can be indefinite but must be invertible on an established constraint
    chart. An unresolved kernel is an error, not silently projected out.
    Returns the affine reconstruction and its unchanged original coefficients.
    """
    ny=gauss_count;n=full.f.size
    if type(ny)is not int or not 0<ny<n:raise ValueError('explicit proper Gauss split required')
    if np.any(full.M[:ny]) or np.any(full.M[:,:ny]) or np.any(full.B[:,:ny]) or np.any(full.h[:ny]):
        raise ValueError('temporal coordinates must be algebraic in this chart')
    A=full.K[:ny,:ny];C=full.K[:ny,ny:];D=full.B[:ny,ny:];j=full.f[:ny]
    X=solve(A,np.column_stack((C,D,j)),assume_a='gen')
    nz=n-ny;Y=X[:,:nz];Z=X[:,nz:2*nz];a=X[:,-1]
    reduced=Form(full.M[ny:,ny:]-D.T@Z,
        full.B[ny:,ny:]-C.T@Z,full.K[ny:,ny:]-C.T@Y,
        full.f[ny:]-C.T@a,full.h[ny:]-D.T@a,
        full.c-.5*j@a)
    return dict(form=reduced,At_value_map=-Y,At_velocity_map=-Z,
        At_source_value=-a,Gauss_matrix=A,Gauss_value_row=C,
        Gauss_velocity_row=D,Gauss_source=j,
        eliminated_source_constant=-.5*j@a,
        gauss_solve_residual=float(np.max(abs(A@X-np.column_stack((C,D,j))))))


def moving_lift_pullback(form:Form,*,E,E_dot,w,w_dot):
    """Exact scalar action under z=E(t)x+w(t), retaining all source terms.

    E spans allowed zero-trace variations; w has the prescribed trace.
    Their physical domain/trace origin is a caller obligation. No fixed
    'physical exterior' is inferred from an arbitrary lift.
    """
    E,Ed,w,wd=map(np.asarray,(E,E_dot,w,w_dot));n=form.f.size
    if E.ndim!=2 or E.shape[0]!=n or Ed.shape!=E.shape or w.shape!=(n,) or wd.shape!=(n,):
        raise ValueError('compatible moving inclusion and lift jets required')
    if any(not a.size or not np.isfinite(a).all() for a in (E,Ed,w,wd)):
        raise ValueError('explicit finite lift data required')
    M,B,K,f,h=form.M,form.B,form.K,form.f,form.h
    pw=M@wd+B.T@w+h
    return Form(E.T@M@E,
        Ed.T@M@E+E.T@B@E,
        Ed.T@M@Ed+E.T@B@Ed+Ed.T@B.T@E+E.T@K@E,
        E.T@(K@w+B@wd+f)+Ed.T@pw,
        E.T@pw,form.action(w,wd))


def canonical_rhs(form:Form,state):
    """Hamilton equations; source momentum shift is not replaced by a force."""
    a=np.asarray(state);n=form.f.size
    if a.shape!=(2*n,):raise ValueError('state is (x,p) in the supplied form')
    x,p=a[:n],a[n:]
    xd=solve(form.M,p-form.B.T@x-form.h,assume_a='gen')
    pd=form.B@xd+form.K@x+form.f
    return np.r_[xd,pd]


def canonical_tangent(form:Form,first:Form,state,state_first):
    """Total first sensitivity for explicit same-chart form/source jets.

    This is an analytic derivative identity. Missing physical background,
    current, event or boundary jets must not be substituted by zeros.
    """
    n=form.f.size;x,p=np.split(np.asarray(state),2);xs,ps=np.split(np.asarray(state_first),2)
    if x.shape!=(n,) or xs.shape!=(n,):raise ValueError('state/source dimensions differ')
    rhs=canonical_rhs(form,state);xd=rhs[:n]
    xds=solve(form.M,ps-first.B.T@x-form.B.T@xs-first.h-first.M@xd,assume_a='gen')
    pds=first.B@xd+form.B@xds+first.K@x+form.K@xs+first.f
    return np.r_[xds,pds]


def forced_gauss_schur_first(full:Form,first:Form,gauss_count:int):
    """Analytic first derivative of all Schur coefficients and source shifts."""
    result=forced_gauss_schur(full,gauss_count);n=gauss_count
    if first.f.shape!=full.f.shape:raise ValueError('same full coefficient chart required')
    if np.any(first.M[:n]) or np.any(first.M[:,:n]) or np.any(first.B[:,:n]) or np.any(first.h[:n]):
        raise ValueError('derivative must preserve the declared algebraic chart')
    A,C,D,j=(full.K[:n,:n],full.K[:n,n:],full.B[:n,n:],full.f[:n])
    As,Cs,Ds,js=(first.K[:n,:n],first.K[:n,n:],first.B[:n,n:],first.f[:n])
    Y,Z,a=-result['At_value_map'],-result['At_velocity_map'],-result['At_source_value']
    Ys=solve(A,Cs-As@Y,assume_a='gen');Zs=solve(A,Ds-As@Z,assume_a='gen');aa=solve(A,js-As@a,assume_a='gen')
    fs=Form(first.M[n:,n:]-Ds.T@Z-D.T@Zs,
        first.B[n:,n:]-Cs.T@Z-C.T@Zs,
        first.K[n:,n:]-Cs.T@Y-C.T@Ys,
        first.f[n:]-Cs.T@a-C.T@aa,
        first.h[n:]-Ds.T@a-D.T@aa,
        first.c-.5*(js@a+j@aa))
    return dict(base=result,first=fs,At_value_map_first=-Ys,
        At_velocity_map_first=-Zs,At_source_value_first=-aa)
