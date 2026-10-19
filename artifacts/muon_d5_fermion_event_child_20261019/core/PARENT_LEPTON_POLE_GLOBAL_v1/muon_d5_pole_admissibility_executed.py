"""Original n0 D5 finite-Cauchy pole admissibility, not a new outer vacuum.

The pole is the genuine cap endpoint. A finite numerical start represents
its regular Frobenius branch only provisionally. No numerical strip face
is identified with the pole, and no regular amplitude or time face is set.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import qr

from .muon_d5_complement_bulk_response import _collocation_rule
from .muon_d5_temporal_bulk_refinement import _rectangular_collocation


def original_n0_pole_indicial(gamma, *, sheet_orientation, carrier_count=16):
    """Derive exponents+1/-2 from conical geometry AND the existing eta.

    C_rho rho/R->1; h4~3/(2 C_rho rho); m_eta~-1/(C_rho rho).
    The n0 right-frame angular spin term is -3i Gamma123/(2R).
    Hence rho Psi_rho=A0 Psi, A0=-I/2-3 eps Gamma4 Gamma123/2.
    Cauchy density~rho^3 excludes the -2 solution logarithmically.
    """
    G=np.asarray(gamma,complex);eps=int(sheet_orientation);nc=int(carrier_count)
    if G.shape!=(5,4,4) or eps not in (-1,1) or eps!=sheet_orientation or nc<1:
        raise ValueError('actual Lorentz Spin4, eta orientation and internal count required')
    K=eps*G[4]@G[1]@G[2]@G[3]
    I=np.eye(4);Pbad=(I+K)/2;Preg=(I-K)/2;A=-I/2-1.5*K
    if np.max(abs(K@K-I))>2e-13:
        raise ValueError('original pole Clifford involution required')
    tensor=lambda a:np.kron(a,np.eye(nc))
    return dict(indicial=tensor(A),regular_projector=tensor(Preg),
        singular_projector=tensor(Pbad),regular_exponent=np.array(1),
        singular_exponent=np.array(-2),Cauchy_density_power=np.array(3),
        indicial_source=np.zeros((4*nc,4*nc),complex))


def independent_projector_columns(projector):
    """Name a coordinate basis for the derived range, without state choice."""
    P=np.asarray(projector,complex)
    if P.ndim!=2 or P.shape[0]!=P.shape[1] or np.max(abs(P@P-P))>2e-12:
        raise ValueError('actual derived projector required')
    rank=int(round(np.trace(P).real))
    _,_,indices=qr(P,pivoting=True,mode='economic');indices=indices[:rank]
    V=P[:,indices]
    if rank and np.linalg.matrix_rank(V)!=rank:raise ArithmeticError('derived pole range lost rank')
    return V,indices


def frobenius_regular_seed(indicial,regular_projector,regular_generator,
        regular_generator_source,*,epsilon):
    """Use the first two Frobenius orders for Z=Psi/rho at rho=epsilon.

    (2I-A0) B1=G_regular(0) V has no resonance:2 differs from1 and-2.
    The supplied G_regular values are finite cutoff approximations of
    their limit, whose error is separately recorded by the consumer.
    """
    A,P,G,Gx=map(np.asarray,(indicial,regular_projector,regular_generator,regular_generator_source))
    if A.shape!=P.shape or G.shape!=A.shape or Gx.shape!=A.shape or not epsilon>0:
        raise ValueError('same full indicial/value/source charts and positive numerical start required')
    V,indices=independent_projector_columns(P)
    if np.max(abs(A@V-V))>2e-12:raise ValueError('the +1 regular branch is required')
    first=np.linalg.solve(2*np.eye(len(A))-A,G@V)
    firstx=np.linalg.solve(2*np.eye(len(A))-A,Gx@V)
    return dict(regular_seed=V+epsilon*first,regular_seed_source=epsilon*firstx,
        regular_leading_columns=V,regular_leading_column_indices=indices,
        first_frobenius_coefficient=first,first_frobenius_source_coefficient=firstx,
        original_first_recursion_rows=(2*np.eye(len(A))-A)@first-G@V,
        original_first_source_recursion_rows=(2*np.eye(len(A))-A)@firstx-Gx@V)


def propagate_regular_frame(radial_boundaries,generator_stages,source_generator_stages,
        seed,seed_source,*,order=3):
    """Execute original radial equations for Z=Psi/rho and its source.

    No amplitude, homogeneous coordinate, numerical annihilator, or
    physical outer value is assigned. Both firsts use the supplied Xi.
    """
    bounds=np.asarray(radial_boundaries,float);G,Gx=map(np.asarray,(generator_stages,source_generator_stages))
    V,Vx=map(lambda x:np.asarray(x,complex),(seed,seed_source))
    nodes,polys,integral,A=_collocation_rule(order)
    if bounds.ndim!=1 or len(bounds)<2 or np.any(np.diff(bounds)<=0) or bounds[0]<=0:
        raise ValueError('positive outward radial partition required')
    if G.shape!=Gx.shape or G.shape!=(len(bounds)-1,order,len(V),len(V)) or Vx.shape!=V.shape:
        raise ValueError('complete original regularized value/source stage operators required')
    initials=[];initialxs=[];slopes=[];slopesx=[];rows=[]
    for i,h in enumerate(np.diff(bounds)):
        initials.append(V.copy());initialxs.append(Vx.copy())
        S,Sx,row,rowx,iteration=_rectangular_collocation(G[i],Gx[i],V,Vx,h,A)
        V=V+h*np.einsum('q,qdk->dk',integral(1.),S)
        Vx=Vx+h*np.einsum('q,qdk->dk',integral(1.),Sx)
        slopes.append(S);slopesx.append(Sx);rows.append([row,rowx])
    return dict(radial_boundaries=bounds,regularized_initials=np.array(initials),
        regularized_source_initials=np.array(initialxs),regularized_slopes=np.array(slopes),
        regularized_source_slopes=np.array(slopesx),stage_rows=np.array(rows),
        regularized_final=V,regularized_source_final=Vx)


def regular_frame_at(application,rho,*,order=3):
    """Independent polynomial value/radial jets; never define derivative by GZ."""
    b=application['radial_boundaries'];r=float(rho)
    if not b[0]<=r<=b[-1]:raise ValueError('outside executed outward regular frame')
    k=min(max(np.searchsorted(b,r,side='right')-1,0),len(b)-2)
    h=b[k+1]-b[k];z=(r-b[k])/h
    _,polys,integral,_=_collocation_rule(order)
    p=np.array([a(z) for a in polys]);a=integral(z)
    out={}
    for prefix in ('','source_'):
        initial=application['regularized_'+prefix+'initials'][k]
        S=application['regularized_'+prefix+'slopes'][k]
        V=initial+h*np.einsum('q,qdk->dk',a,S)
        Vr=np.einsum('q,qdk->dk',p,S)
        out[prefix+'value']=r*V;out[prefix+'radial']=V+r*Vr
    return out


def pole_boundary_rows(regular_frame,regular_frame_source):
    """Derive explicit compatibility rows retaining every regular amplitude.

    A square row pivot of Y names regular coordinates. It does not set
    their values. B Psi=0 is equivalent to range(Psi) subset range(Y),
    and Bx retains the complete supplied source of this finite frame.
    """
    Y,Yx=map(np.asarray,(regular_frame,regular_frame_source));d,k=Y.shape
    if Yx.shape!=Y.shape or not 0<k<d:raise ValueError('nontrivial full regular frame/source required')
    _,_,rows=qr(Y.T,pivoting=True,mode='economic');p=rows[:k]
    free=np.setdiff1d(np.arange(d),p);A=Y[p]
    L=np.linalg.solve(A.T,Y[free].T).T
    Lx=np.linalg.solve(A.T,(Yx[free]-L@Yx[p]).T).T
    B=np.eye(d,dtype=complex)[free];B[:,p]=-L
    Bx=np.zeros_like(B);Bx[:,p]=-Lx
    return dict(boundary=B,boundary_source=Bx,regular_pivot_rows=p,
        dependent_rows=free,pivot_condition=np.array(np.linalg.cond(A)),
        original_regular_rows=B@Y,original_regular_source_rows=Bx@Y+B@Yx)
