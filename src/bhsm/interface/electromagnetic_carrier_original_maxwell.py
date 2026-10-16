"""Angular seed and complete local Maxwell covectors on the owned coframe.

These helpers retain original five-component rows. They do not choose a
physical history, reference, boundary domain or gauge quotient.
"""
from __future__ import annotations

import itertools
import numpy as np

from .muon_intrinsic_scalar_discretization import (
    real_scalar_basis_labels, real_scalar_basis_transform, scalar_basis_values,
    scalar_angular_derivative_matrices, scalar_s3_discretization,
)
from .muon_baton_zoo_original_validation import independent_original_maxwell_weak
from .electromagnetic_carrier_mode_reduction import right_frame_s3_modes


def even_angular_space(*,haar_degree=None):
    """Complete scalar n=0,2, with exact degree-five rule or owned Haar rule.

    The small rule is exact for a homogeneous background's weak rows and
    their first field derivative. It is not a nonlinear truncation bound.
    """
    if haar_degree is None:
        q=np.array(list(itertools.product([-0.5,0.5],repeat=4))+list(np.eye(4))+list(-np.eye(4)))
        z1=q[:,0]+1j*q[:,1];z2=q[:,2]+1j*q[:,3]
        g=np.empty((24,2,2),complex)
        g[:,0,0]=z1;g[:,0,1]=z2;g[:,1,0]=-z2.conj();g[:,1,1]=z1.conj()
        transform=real_scalar_basis_transform(2)
        raw=scalar_basis_values(g,2)
        y=raw@transform
        ey=np.einsum('pm,amn,nh->pah',raw,scalar_angular_derivative_matrices(2),transform)
        if max(np.max(abs(y.imag)),np.max(abs(ey.imag)))>1e-13:
            raise ValueError('real scalar basis failed its reality identity')
        y,ey,weights=y.real,ey.real,np.full(24,1/24)
    else:
        a=scalar_s3_discretization(2,quadrature_polynomial_degree=haar_degree)
        x,alpha,beta=a['hopf_points'].T
        q=np.column_stack((np.sqrt(x)*np.cos(alpha),np.sqrt(x)*np.sin(alpha),
                           np.sqrt(1-x)*np.cos(beta),np.sqrt(1-x)*np.sin(beta)))
        y,ey,weights=a['real_basis_values'],a['real_basis_derivative_values'],a['haar_weights']
    labels=real_scalar_basis_labels(2)
    selected=[i for i,label in enumerate(labels) if label[0]%2==0]
    y,ey=y[:,selected],ey[:,:,selected]
    modes,dmodes,_=right_frame_s3_modes(q)
    coefficients=np.einsum('ph,p,pai->hai',y,weights,modes)
    defect=max(np.max(abs(np.einsum('ph,hai->pai',y,coefficients)-modes)),
               np.max(abs(np.einsum('pjh,hai->pjai',ey,coefficients)-dmodes)))
    return dict(quaternions=q,values=y,derivatives=ey,weights=weights,
                labels=[labels[i] for i in selected],modes=modes,mode_derivatives=dmodes,
                mode_coefficients=coefficients,reconstruction_defect=float(defect))


def original_maxwell_covectors(connection,time,radial,angular,densities,radial_weights,basis,basis_radial,space,*,normalization):
    """Evaluate every original value/rate row by exact local-jet factorization.

    Returns (radial profile,field,internal,harmonic) covectors. Literal local
    component and angular-jet probes use the independent original evaluator;
    canonical radial/time momenta supply their own respective derivative slots.
    No endpoint, matter current or Gauss replacement is inserted.
    """
    nr,nh=connection.shape[:2]
    identity=np.eye(20,dtype=complex).reshape(20,5,4)
    v=np.zeros((80,5,4),complex);v[:20]=identity
    ev=np.zeros((80,3,5,4),complex)
    for j in range(3):ev[20+20*j:40+20*j,j]=identity
    broadcast=lambda x:np.broadcast_to(x,(nr*nh,)+x.shape)
    zero=np.zeros_like(v)
    result=independent_original_maxwell_weak(
        connection=connection.reshape(-1,5,4),time_derivative=time.reshape(-1,5,4),
        radial_derivative=radial.reshape(-1,5,4),angular_derivative=angular.reshape(-1,3,5,4),
        tests=broadcast(v),tests_time=broadcast(zero),tests_radial=broadcast(zero),
        tests_angular=broadcast(ev),metric_densities=densities.reshape(-1,5),
        quadrature=(normalization*radial_weights[:,None]*space['weights'][None,:]).ravel())
    local=result['point_weak_rows'].reshape(nr,nh,80)
    value=local[:,:,:20].reshape(nr,nh,5,4)
    ea=local[:,:,20:].reshape(nr,nh,3,5,4)
    pt=result['temporal_momentum'].reshape(nr,nh,5,4)
    pr=result['radial_momentum'].reshape(nr,nh,5,4)
    w=normalization*radial_weights[:,None]*space['weights'][None,:]
    y,ey=space['values'],space['derivatives']
    rows=(np.einsum('rp,ra,ph,rpfc->afch',w,basis,y,value)
          +np.einsum('rp,ra,ph,rpfc->afch',w,basis_radial,y,pr)
          +np.einsum('rp,ra,pjh,rpjfc->afch',w,basis,ey,ea))
    momenta=np.einsum('rp,ra,ph,rpfc->afch',w,basis,y,pt)
    return dict(value_rows=rows,rate_rows=momenta,action=result['original_action_value'])


def electromagnetic_inclusion(mode_coefficients,charge,radial_count=4):
    """All independent EM mode/radial amplitudes in the complete coefficient space."""
    nh=len(mode_coefficients)
    s=np.zeros((radial_count,5,4,nh,4*radial_count))
    for j in range(radial_count):
        for a in range(4):
            s[j,2:,:,:,4*j+a]=np.einsum('hi,c->ich',mode_coefficients[:,a],charge)
    return s.reshape(-1,4*radial_count)


def geometric_dual_split(covector,gram20,inclusion):
    """Unreduced geometric L2 dual split; NOT a Maxwell kinetic inverse.

    gram20 couples (radial profile,field); internal and angular factors have
    unit Gram. At/Gauss remain present. The leading G in the covector
    projection is essential. Full Maxwell kinetic weight has an At kernel.
    """
    r=np.asarray(covector);s=np.asarray(inclusion)
    channel=r.shape[0]//len(gram20)
    def act(x):
        return np.einsum('ab,bc...->ac...',gram20,x.reshape(len(gram20),channel,*x.shape[1:])).reshape(x.shape)
    gs=act(s);mass=s.T@gs
    tangent=s.T@r
    parallel=gs@np.linalg.solve(mass,tangent)
    complement=r-parallel
    return dict(tangent_covector=tangent,complement_covector=complement,
                geometric_seed_gram=mass,
                complement_annihilation_defect=float(np.max(abs(s.T@complement))))
