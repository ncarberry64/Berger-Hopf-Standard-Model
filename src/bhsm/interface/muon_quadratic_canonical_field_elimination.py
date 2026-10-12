"""Exact action-polynomial elimination of canonical field/Gauss rows.

At fixed x and geometry v38/m24 the Maxwell and intrinsic Higgs action
is quadratic in dynamic gauge velocities, Hdot and algebraic At.  Every
one of these84 original rows remains in the named86 saddle and in the
returned full146 residual.  Only that algebraic solve is eliminated from
the nonlinear geometry equations; no spectral direction is removed.
"""
from __future__ import annotations
import numpy as np


def original_field_geometry_indices(n=106,m=40):
    if (n,m)!=(106,40):raise ValueError('literal enriched x106/v106/y40 ordering required')
    field=np.r_[np.arange(38,n),np.arange(n+24,n+m)]
    geometry=np.r_[np.arange(38),np.arange(n,n+24)]
    return field,geometry


def _balanced_solve(K,rhs):
    row=1/np.maximum(np.max(abs(K),axis=1),np.finfo(float).tiny)
    col=1/np.maximum(np.max(abs(row[:,None]*K),axis=0),np.finfo(float).tiny)
    solution=col[:,None]*np.linalg.solve(row[:,None]*K*col[None,:],row[:,None]*rhs)if rhs.ndim==2 else col*np.linalg.solve(row[:,None]*K*col[None,:],row*rhs)
    return solution,row,col


def eliminate_quadratic_canonical_fields(eta,p0,evaluate,frame,*,field_indices=None,
        geometry_indices=None,frame_reference=None,quadratic_tolerance=2e-9):
    """Solve the original field+Gauss saddle, then form its exact Schur jet."""
    eta=np.asarray(eta,complex).copy();p0=np.asarray(p0,complex);n=len(p0);m=len(eta)-2*n
    if field_indices is None:field_indices,geometry_indices=original_field_geometry_indices(n,m)
    f=np.asarray(field_indices,int);g=np.asarray(geometry_indices,int)
    if not np.array_equal(np.sort(np.r_[f,g]),np.arange(n+m))or len(np.unique(np.r_[f,g]))!=n+m:
        raise ValueError('partition every original constitutive row exactly once')
    C=np.asarray(frame['named_frame_covectors'],complex);Z=np.asarray(frame['literal_generators'],complex)
    reference=eta[n:].copy()if frame_reference is None else np.asarray(frame_reference,complex)
    if C.shape!=(2,n+m)or Z.shape!=(n+m,2)or reference.shape!=(n+m,)or np.any(C[:,g]):
        raise ValueError('same named temporal frame must act only on retained field coordinates')
    first=evaluate(eta);G=np.asarray(first['gradient'],complex);H=np.asarray(first['hessian'],complex)
    r=np.r_[G[n:2*n]-p0,G[2*n:]];D=H[n:,n:];Cf=C[:,f]
    K=np.block([[D[np.ix_(f,f)],Cf.T],[Cf,np.zeros((2,2),complex)]])
    rhs=-np.r_[r[f],C@(eta[n:]-reference)]
    delta,row,col=_balanced_solve(K,rhs)
    eta[n+f]+=delta[:-2];rho=delta[-2:]
    second=evaluate(eta);G=np.asarray(second['gradient'],complex);H=np.asarray(second['hessian'],complex)
    residual=np.r_[G[n:2*n]-p0,G[2*n:]];D2=H[n:,n:]
    hessian_defect=D2[np.ix_(f,f)]-D[np.ix_(f,f)]
    affine_defect=residual[f]-r[f]-D[np.ix_(f,f)]@delta[:-2]
    relative_hessian=float(np.max(abs(hessian_defect))/max(1.,np.max(abs(D[np.ix_(f,f)]))))
    relative_affine=float(np.max(abs(affine_defect))/max(1.,np.max(abs(r[f])),np.max(abs(D[np.ix_(f,f)]@delta[:-2]))))
    if max(relative_hessian,relative_affine)>quadratic_tolerance:
        raise ArithmeticError('same fixed-geometry original field action is not the declared quadratic polynomial')
    # Exact implicit derivative in the original analytic-transpose chart.
    K2=np.block([[D2[np.ix_(f,f)],Cf.T],[Cf,np.zeros((2,2),complex)]])
    field_geometry_rhs=np.vstack((D2[np.ix_(f,g)],np.zeros((2,len(g)),complex)))
    lift,_,_=_balanced_solve(K2,-field_geometry_rhs)
    Schur=D2[np.ix_(g,g)]+D2[np.ix_(g,f)]@lift[:-2]
    framed_field=np.r_[residual[f]+Cf.T@rho,C@(eta[n:]-reference)]
    return dict(coefficients=eta,canonical_momentum_target=p0,action=second,
        field_indices=f,geometry_indices=g,field_frame_saddle=K2,field_frame_solution=delta,
        field_frame_reactions=rho,field_correction=delta[:-2],
        original_field_rows=residual[f],framed_field_rows=framed_field,
        original_constitutive_rows=residual,reduced_geometry_rows=residual[g],
        reduced_geometry_Jacobian=Schur,implicit_field_geometry_lift=lift[:-2],
        implicit_frame_reaction_geometry_lift=lift[-2:],
        original_frame_reference=reference,literal_generators=Z,named_frame_covectors=C,
        literal_gauge_source_compatibility=Z.T@residual,literal_generator_image=D2@Z,
        fixed_geometry_position_defect=np.zeros(n,complex),
        fixed_geometry_velocity_multiplier_defect=np.zeros(len(g),complex),
        field_hessian_quadratic_identity_defect=hessian_defect,
        field_gradient_affine_identity_defect=affine_defect,
        field_hessian_quadratic_identity_relative_max=relative_hessian,
        field_gradient_affine_identity_relative_max=relative_affine,
        implicit_original_field_geometry_rows=K2@lift+field_geometry_rhs,
        all_original_constitutive_rows_retained=True,numerical_spectral_quotient_used=False)
