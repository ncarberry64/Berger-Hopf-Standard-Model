"""Finite reference/operator mathematics; no physical reference is selected.

Projector and Gram first jets are conditional finite-domain tools. The CAR
interval is unrestricted; charge/family/Hadamard restrictions use their owners.
It is not a bosonic covariance condition or a physical muon error bound.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import solve_sylvester


def _hermitian_matrix(value,name):
    a=np.asarray(value,dtype=complex)
    if a.ndim!=2 or not a.shape[0] or a.shape[0]!=a.shape[1] or not np.all(np.isfinite(a)):
        raise ValueError(f'{name} must be a finite square matrix')
    if not np.allclose(a,a.conj().T,rtol=0,atol=1e-13*max(1,float(np.linalg.norm(a,ord=2)))):
        raise ValueError(f'{name} must be Hermitian')
    return a


def positive_projector_jet(h,dh,*,gap_tolerance=1e-10):
    """Positive spectral projector and divided-difference first derivative."""
    h=_hermitian_matrix(h,'h'); dh=_hermitian_matrix(dh,'dh')
    if dh.shape!=h.shape: raise ValueError('shape mismatch')
    if not np.isfinite(gap_tolerance) or gap_tolerance<0: raise ValueError('invalid gap tolerance')
    w,u=np.linalg.eigh(h)
    gap=float(np.min(np.abs(w)))
    if gap<=gap_tolerance: raise ValueError('positive/negative spectral gap is not admitted')
    p=(w>0).astype(float)
    dd=np.zeros((len(w),len(w)))
    opposite=p[:,None]!=p[None,:]
    np.divide(p[:,None]-p[None,:],w[:,None]-w[None,:],out=dd,where=opposite)
    return u@np.diag(p)@u.conj().T,u@(dd*(u.conj().T@dh@u))@u.conj().T,gap


def gram_sqrt_jet(g,dg):
    """Positive Hermitian Gram root and its Sylvester first jet."""
    g=_hermitian_matrix(g,'g'); dg=_hermitian_matrix(dg,'dg')
    if g.shape!=dg.shape: raise ValueError('shape mismatch')
    w,u=np.linalg.eigh(g)
    if np.min(w)<=0: raise ValueError('Gram must be strictly positive')
    root=(u*np.sqrt(w))@u.conj().T
    return root,solve_sylvester(root,root,dg)


def unrestricted_affine_car_range(m,j):
    """Sharp finite CAR interval and witnesses, retaining tiny eigenvalues.

    C+J C* J^dagger=I, 0<=C<=I. Source optimizer's absolute eigenvalue
    threshold is deliberately removed; see the recorded source erratum.
    """
    m=_hermitian_matrix(m,'m'); j=np.asarray(j,dtype=complex)
    eye=np.eye(len(m))
    if j.shape!=m.shape or not np.all(np.isfinite(j)) or not np.allclose(j@j.conj().T,eye,atol=1e-13,rtol=0) or not np.allclose(j@j.conj(),eye,atol=1e-13,rtol=0):
        raise ValueError('j must represent an antiunitary involution')
    k=(m-j@m.conj()@j.conj().T)/2
    w,u=np.linalg.eigh(k)
    sign=(u*np.sign(w))@u.conj().T
    center=float(np.trace(m).real/2)
    radius=float(np.sum(np.abs(w))/2)
    low=(eye-sign)/2; high=(eye+sign)/2
    car_defect=max(float(np.linalg.norm(c+j@c.conj()@j.conj().T-eye,ord=2)) for c in (low,high))
    endpoint_defect=max(abs(float(np.trace(m@low).real)-(center-radius)),
                        abs(float(np.trace(m@high).real)-(center+radius)))
    # Taking sign at a roundoff-sized EVEN nullspace can amplify an imperfect
    # antiunitary into an order-one CAR violation. Reject it explicitly rather
    # than silently deleting a small, genuinely odd eigenvalue.
    if car_defect>1e-12:
        raise ValueError('CAR endpoint witnesses unresolved at numerical nullspace')
    return {'lower':center-radius,'upper':center+radius,'center':center,
            'radius':radius,'C_minus':low,'C_plus':high,'odd_kernel':k,
            'witness_CAR_residual':car_defect,'endpoint_residual':endpoint_defect,
            'scope':'UNRESTRICTED_FINITE_CAR_NOT_CCR_OR_CHARGED_FAMILY'}
