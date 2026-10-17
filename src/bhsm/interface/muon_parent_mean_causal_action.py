"""Actual instantaneous mean action for the joint causal descriptor.

The background is the pinned outgoing24 finite numerical germ.  This
assembly does not reidentify it as incoming C1 or invert a compact temporal
Newton Hessian.  Geometry, lapse/shift, all five gauge components and H
share one scalar action and one explicit value/rate coordinate system.
"""
from __future__ import annotations
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from scipy.interpolate import CubicSpline

from .muon_birth_candidate_geometry_action import ROOT
from .muon_moving_geometric_action import retained_state,moving_cap_action_jet
from .muon_parent_maxwell_corrected_retarded import load_corrected_iterate
from .muon_parent_gauge_geometry_correction import finite_common_iterate_at_time,compact_temporal_basis
from .muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
from .muon_parent_maxwell_full_weak import FIELD_ORDER,background_subtracted_maxwell_action_jet,full_maxwell_weak_geometric_jets,full_maxwell_gauge_hessian_matrix
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_material_higgs_gauge_action import material_intrinsic_higgs_gauge_action_jet
from .muon_parent_retarded_hypercharge import WALL,regular_radial_basis

VOLUME=2*np.pi**2
MAXWELL_TO_CAP=1/(8*VOLUME**2)
DEFAULT_FORCING='artifacts/muon_parent_maxwell_source_mean_forcing_20261010/run_2'


def mean_coordinate_lift(labels):
    """raw228=(geometry100,gauge60,gauge_rate60,H4,Hrate4)."""
    if len(labels)!=60:raise ValueError('all60 mean gauge coordinates required')
    P=np.zeros((228,216));P[:37,:37]=np.eye(37);P[37:74,90:127]=np.eye(37)
    P[74:98,180:204]=np.eye(24);P[98,37]=1.;P[99,127]=1.
    dynamic=[];algebraic=[]
    for i,label in enumerate(labels):
        if label['field']==FIELD_ORDER[0]:algebraic.append(i)
        else:dynamic.append(i)
    if len(dynamic)!=48 or len(algebraic)!=12:raise ValueError('complete all5 gauge decomposition required')
    for j,i in enumerate(dynamic):P[100+i,38+j]=1.;P[160+i,128+j]=1.
    for j,i in enumerate(algebraic):P[100+i,204+j]=1.
    P[220:224,86:90]=np.eye(4);P[224:228,176:180]=np.eye(4)
    return dict(lift=P,dynamic_gauge_indices=np.array(dynamic),At_indices=np.array(algebraic),
        x_count=90,v_count=90,y_count=36,
        x_order='q37,normal1,Ar/Ai48 in retained radial-major labels,Hreal4',
        y_order='m24,At12 in retained radial-major labels',
        H_order='ReH1,ReH2,ImH1,ImH2',raw_gauge_labels=labels)


@lru_cache(maxsize=2)
def mean_action_family(repository=ROOT,forcing_application=DEFAULT_FORCING):
    root=Path(repository);c,rep,receipt=load_corrected_iterate(root)
    forcing_dir=root/forcing_application;raw=(forcing_dir/'result.json').read_bytes();forcing=json.loads(raw)
    if forcing['retained_geometry_side']!='outgoing_C2_E1plus_branch24 local finite germ' or forcing['mean_second_response'] is not None:
        raise ValueError('this family must bind the evaluated outgoing-core cotangents, not a fabricated mean solution')
    if sha256((forcing_dir/'application.npz').read_bytes()).hexdigest()!=forcing['application_sha256']:raise ValueError('mean forcing archive hash mismatch')
    for name,digest in forcing['input_hashes'].items():
        if sha256((root/name).read_bytes()).hexdigest()!=digest:raise ValueError('mean forcing input/source changed')
    with np.load(forcing_dir/'application.npz') as a:arrays={k:a[k].copy() for k in a.files}
    coordinates=mean_coordinate_lift(rep['gauge_labels']);P=coordinates['lift'];n=len(arrays['times'])
    J=np.zeros((n,228,8,8));J[:,:100]=arrays['combined_geometry_100']
    J[:,100:160]=arrays['combined_mean_gauge_value'].reshape(n,60,8,8)
    J[:,160:220]=arrays['combined_mean_gauge_time'].reshape(n,60,8,8)
    J[:,220:224]=arrays['scalar_mean_H_value'];J[:,224:228]=arrays['scalar_mean_H_time']
    J=MAXWELL_TO_CAP*np.einsum('ij,tjAB->tiAB',P.T,J)
    return dict(root=root,coefficients=c,representation=rep,receipt=receipt,reference=retained_state(root),coordinates=coordinates,
        source=CubicSpline(arrays['times'],J),source_values=J,source_times=arrays['times'],
        source_receipt=forcing,source_receipt_sha256=sha256(raw).hexdigest(),source_application=forcing_application,
        length=rep['length'],nu_squared_action=receipt['action_parameters']['nu_squared_action'],surface_gamma=receipt['action_parameters']['surface_gamma'],
        scope='same evaluated outgoing24 backward local core; no physical incoming23 or E0 history identified')


def local_mean_action(time,family):
    """Assemble L, gradient and Hessian on x90,v90,y36 before any solve."""
    u=float(time);rep=family['representation'];c=family['coefficients']
    if not np.isfinite(u) or u<0 or u>family['length']:raise ValueError('time outside the evaluated finite core')
    t=u-family['length'];data=finite_common_iterate_at_time(t,c,rep,family['reference'])
    q,v,m,s,sr=(data[k] for k in ('q','qdot','m','normal','normal_rate'))
    cap=moving_cap_action_jet(12,q,v,m,points=rep['cap_points'],source_value=s,source_rate=sr)
    geo=geometric_connection_coefficient_jets(12,q,v,m,rep['rho'],source_value=s,source_rate=sr)
    gb,gr=rep['gauge_basis'],rep['gauge_radial_basis'];r=len(gb)
    tv=np.zeros((r,120,1,5,4));tt=tv.copy();tr=tv.copy();ta=np.zeros((r,120,1,3,5,4))
    tv[:,:60]=gb;tr[:,:60]=gr;tt[:,60:]=gb
    tests=dict(tests=tv,tests_tau=tt,tests_rho=tr,tests_angular=ta)
    fields=data['fields'];delta=background_subtracted_maxwell_action_jet(geo,rep['radial_quadrature'],np.ones(1),**fields)
    weak=full_maxwell_weak_geometric_jets(geo,rep['radial_quadrature'],np.ones(1),**fields,**tests)
    gauge=full_maxwell_gauge_hessian_matrix(geo,rep['radial_quadrature'],np.ones(1),**fields,**tests)
    gradient=np.zeros(228);hessian=np.zeros((228,228));value=cap['total'].value+MAXWELL_TO_CAP*delta['value']
    gradient[:100]=cap['total'].gradient+MAXWELL_TO_CAP*delta['gradient']
    hessian[:100,:100]=cap['total'].hessian+MAXWELL_TO_CAP*delta['hessian']
    gradient[100:220]+=MAXWELL_TO_CAP*weak['weak']['values']
    hessian[100:220,100:220]+=MAXWELL_TO_CAP*gauge['matrix']
    cross=MAXWELL_TO_CAP*weak['weak']['geometric_jacobian']
    hessian[100:220,:100]+=cross;hessian[:100,100:220]+=cross.T
    wall=finite_common_iterate_at_time(t,c,rep,family['reference'],rho=np.array([WALL]))
    metric=intrinsic_m4_weight_jet(12,q,v,m,source_value=s,source_rate=sr)
    b,bt=compact_temporal_basis(np.array([t]),rep['length']);sc=c[rep['scalar_start']:]
    H=b[0]*sc[:4]+sc[4:];Ht=bt[0]*sc[:4]
    wallbasis,_=regular_radial_basis(np.array([WALL]),rep['radial_order'])
    trace=np.zeros((1,5,4,60))
    for j,label in enumerate(rep['gauge_labels']):
        trace[0,FIELD_ORDER.index(label['field']),label['internal'],j]=wallbasis[0,label['radial']]
    scalar_value=np.zeros((1,4,8));scalar_value[0,:,:4]=np.eye(4)
    scalar_derivative=np.zeros((1,4,4,8));scalar_derivative[0,0,:,4:]=np.eye(4)
    scalar=material_intrinsic_higgs_gauge_action_jet(metric,scalar_coefficients=np.r_[H,Ht],scalar_value_map=scalar_value,
        scalar_derivative_map=scalar_derivative,gauge_coefficients=b[0]*c[62:122],gauge_trace_map=trace,
        angular_quadrature=np.ones(1),lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=family['nu_squared_action'])['action']
    S=np.zeros((168,228));S[:100,:100]=np.eye(100);S[100:108,220:228]=np.eye(8);S[108:168,100:160]=np.eye(60)
    value+=scalar.value/VOLUME**2;gradient+=S.T@scalar.gradient/VOLUME**2;hessian+=S.T@scalar.hessian@S/VOLUME**2
    if family['surface_gamma'] is not None:
        gamma=family['surface_gamma'];value+=gamma*cap['surface_per_gamma'].value
        gradient[:100]+=gamma*cap['surface_per_gamma'].gradient;hessian[:100,:100]+=gamma*cap['surface_per_gamma'].hessian
    P=family['coordinates']['lift'];G=P.T@gradient;Hessian=P.T@hessian@P
    J=family['source'](u)
    return dict(value=value,gradient=G,hessian=Hessian,Jx=J[:90],Jv=J[90:180],Jy=J[180:],
        Lxx=Hessian[:90,:90],Lxv=Hessian[:90,90:180],Lxy=Hessian[:90,180:],
        Lvx=Hessian[90:180,:90],Lvv=Hessian[90:180,90:180],Lvy=Hessian[90:180,180:],
        Lyx=Hessian[180:,:90],Lyv=Hessian[180:,90:180],Lyy=Hessian[180:,180:],
        constraint_base=G[180:],canonical_base=G[90:180],time=u,represented_coefficient_time=t,
        raw_gradient=gradient,raw_hessian=hessian,source_order='raw betaPhoton A,B symmetric mixed derivative',
        metric_chart='materialAt_ref once',conditional_nu_squared_action=family['nu_squared_action'],
        surface_gamma=family['surface_gamma'],surface_per_gamma_value=cap['surface_per_gamma'].value,
        surface_per_gamma_hessian=P[:100].T@cap['surface_per_gamma'].hessian@P[:100],
        all_constraints_and_Gauss_retained=True,compact_two_face_inverse_used=False,
        stationary_background=False,physical_two_arm_domain_selected=False)


def retained_mean_action_family(repository=ROOT,time_nodes=17):
    """Sample one scalar mean action with its prescribed trace restriction.

    All20 rejected wall value rows remain reaction outputs.  Their second
    trace is fixed zero because this numerical beta source is affine; no
    free-wall condition or physical gauge quotient is invented.
    """
    if type(time_nodes) is not int or time_nodes<3:raise ValueError('at least3 mean action sample nodes required')
    family=mean_action_family(repository);nodes=np.linspace(0,family['length'],time_nodes)
    labels=family['coordinates']['raw_gauge_labels'];dynamic=family['coordinates']['dynamic_gauge_indices'];at=family['coordinates']['At_indices']
    x=np.r_[np.arange(38),[38+j for j,i in enumerate(dynamic) if not labels[i]['wall_lift']],np.arange(86,90)]
    y=np.r_[np.arange(24),[24+j for j,i in enumerate(at) if not labels[i]['wall_lift']]]
    indices=np.r_[x,90+x,180+y];Q=np.eye(216)[:,indices]
    rejected_x=np.array([38+j for j,i in enumerate(dynamic) if labels[i]['wall_lift']])
    rejected_y=np.array([180+24+j for j,i in enumerate(at) if labels[i]['wall_lift']])
    samples=[local_mean_action(t,family) for t in nodes]
    H=np.array([s['hessian'] for s in samples]);J=np.array([np.concatenate((s['Jx'],s['Jv'],s['Jy'])) for s in samples])
    return dict(times=nodes,hessian_samples=np.einsum('ia,tij,jb->tab',Q,H,Q),
        source_samples=np.einsum('ia,tiAB->taAB',Q,J),full_hessian_samples=H,full_source_samples=J,
        full_gradient_samples=np.array([s['gradient'] for s in samples]),value_samples=np.array([s['value'] for s in samples]),
        surface_per_gamma_hessian_samples=np.array([s['surface_per_gamma_hessian'] for s in samples]),
        x_count=len(x),v_count=len(x),y_count=len(y),x_full_indices=x,y_full_indices=y,lift_to_full_mean=Q,
        H_real_indices=np.arange(len(x)-4,len(x)),rejected_wall_value_rows=np.r_[rejected_x,rejected_y],
        rejected_wall_canonical_rows=90+rejected_x,all20_wall_reaction_rows_retained=True,
        fixed_wall_trace='second derivative of the prescribed affine full-parent trace is zero; wall equations are reactions',
        source_record=dict(path=family['source_application'],receipt_sha256=family['source_receipt_sha256'],
            equation='J=D^3S; p=Lvx*x+Lvv*v+Lvy*y+Jv; pdot=Lxx*x+Lxv*v+Lxy*y+Jx; Lyx*x+Lyv*v+Lyy*y+Jy=0',
            pair_order='raw betaPhoton A,B=0..7; symmetric mixed derivative'),
        source_scope=family['source_receipt']['source_profile_scope'],background_scope=family['scope'],
        conditional_nu_squared_action=family['nu_squared_action'],surface_gamma=family['surface_gamma'],
        native_heat_or_Pauli_evaluated=False,physical_gauge_quotient_closed=False,physical_two_arm_domain_selected=False)
