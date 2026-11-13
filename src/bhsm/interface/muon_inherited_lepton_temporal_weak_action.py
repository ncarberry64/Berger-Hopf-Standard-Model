"""Proper-clock weak lepton action on the solved inherited child cell.

The represented trajectory uses linear x and midpoint v/y, the SAME
convention as the canonical discrete action.  Its parent/reference first
germs remain the explicitly scoped computational lifts.  Integrating
A^dagger A retains the variable spatial factor's time contact by parts;
subtracting W_tau again would count that contact twice.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import eigh

from .muon_birth_trace_enriched_action import generic_coordinate_lift
from .muon_inherited_intrinsic_lepton_operator import inherited_intrinsic_lepton_operator


def smooth_temporal_trial(time, length):
    """Dirichlet H1 trials b=4t(L-t)/L² and b², including derivatives."""
    t,L=float(time),float(length)
    if not np.isfinite([t,L]).all() or L<=0 or t<0 or t>L:
        raise ValueError('same finite represented cell required')
    b=4*t*(L-t)/(L*L); d=4*(L-2*t)/(L*L)
    return np.array([b,b*b]),np.array([d,2*b*d])


def inherited_cell_raw_at_time(stage_raw, stage_time, time, representation):
    """Exact interpolation convention of x-linear, full-stage v/y."""
    raw=np.asarray(stage_raw,float);c=generic_coordinate_lift(representation['gauge_labels'])
    P=c['lift'];n=c['x_count']
    if raw.shape!=(len(P),) or not np.isfinite(raw).all():
        raise ValueError('complete independent child raw required')
    eta=P.T@raw
    if np.linalg.norm(P@eta-raw)>1e-12:
        raise ValueError('raw lies outside the owned phase coordinate lift')
    eta[:n]+=(float(time)-float(stage_time))*eta[n:2*n]
    return P@eta


def inherited_temporal_weak_application(stage_raw, stage_time, initial_pair,
        reference_pair, representation, *, length, quadrature_order):
    """Execute the changing all-family18 weak factor, Gram and spectrum.

    This is a represented positive product component.  No physical
    exterior, Feynman prescription, formation length or LSZ is selected.
    The full18 constant angular space is invariant for this homogeneous
    wall component.  This does not sum the native angular trace.
    """
    L=float(length)
    if not np.isfinite(L) or L<=0 or not 0<float(stage_time)<L:
        raise ValueError('positive same solved cell and its interior stage required')
    if type(quadrature_order)is not int or quadrature_order<4:
        raise ValueError('explicit resolved Gauss order required')
    K=np.zeros((36,36),complex);G=K.copy();held=K.copy();cross=K.copy()
    gx,gw=np.polynomial.legendre.leggauss(quadrature_order);snapshots=[]
    midpoint=inherited_intrinsic_lepton_operator(stage_raw,stage_time,initial_pair,
                                                reference_pair,representation)
    for time,weight in zip((gx+1)*L/2,gw*L/2):
        raw=inherited_cell_raw_at_time(stage_raw,stage_time,time,representation)
        op=inherited_intrinsic_lepton_operator(raw,time,initial_pair,reference_pair,representation)
        b,d=smooth_temporal_trial(time,L);I=np.eye(18)
        V=np.concatenate([z*I for z in b],axis=1)
        Dt=np.concatenate([z*I for z in d],axis=1)
        A=Dt/op['N']+(op['W']+op['Omega_tau'])@V
        Ah=Dt/midpoint['N']+(midpoint['W']+midpoint['Omega_tau'])@V
        K+=weight*op['N']*(A.conj().T@A)
        G+=weight*op['N']*(V.conj().T@V)
        held+=weight*midpoint['N']*(Ah.conj().T@Ah)
        cross+=weight*op['N']*((Dt/op['N']).conj().T@((op['W']+op['Omega_tau'])@V)
            +(((op['W']+op['Omega_tau'])@V).conj().T@(Dt/op['N'])))
        snapshots.append((time,op['N'],op['R4'],np.linalg.norm(op['W'])))
    K=(K+K.conj().T)/2;G=(G+G.conj().T)/2
    p,U=eigh(K,G)
    if p[0]<=0:raise ArithmeticError('actual proper-clock weak factor is not positive')
    return dict(weak_form=K,proper_time_Gram=G,midpoint_coefficient_weak_form=held,
        temporal_cross_form=cross,eigenvalues=p,Gram_orthonormal_eigenvectors=U,
        quadrature_samples=np.array(snapshots),
        generalized_eigen_residual=float(np.linalg.norm(K@U-(G@U)*p)/max(np.linalg.norm(K@U),1.)),
        Gram_orthonormality_defect=float(np.linalg.norm(U.conj().T@G@U-np.eye(36))),
        variable_minus_midpoint_weak_form_norm=float(np.linalg.norm(K-held)),
        material_inherited_connection_count=1,
        proper_time_Gram_included=True,
        separately_subtracted_spatial_time_contact=False,
        coefficient_interpolation='owned phase convention: x linear; v/y midpoint; parent/reference first germs affine',
        action='integral N dt ((partial_t/N+Omega_tau+W)u)^dagger ((partial_t/N+Omega_tau+W)u)',
        angular_scope='complete all-family18 constant angular component, not the whole angular trace',
        temporal_complement_or_physical_exterior_domain_enclosed=False,
        native_relative_completion_or_LSZ_or_Pauli_completed=False)
