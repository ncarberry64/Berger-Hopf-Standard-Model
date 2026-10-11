"""Reached Maxwell/Higgs weak action on the actual enriched primal fields.

The background retains its entire affine radial source image. The response
trial functions are the explicit inherited finite odd-sector functions;
their Galerkin solve is not a continuum or completed native-domain solve.
"""
from __future__ import annotations
import numpy as np

from .muon_reached_trace_action import moving_trace_time_forms,moving_trace_gauge_rows
from .muon_parent_maxwell_corrected_retarded import full_constant_angular_hessian,intrinsic_scalar_trace_hessian
from .muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
from .muon_parent_maxwell_full_weak import M
from .muon_parent_retarded_hypercharge import regular_radial_basis
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_parent_maxwell_full_retarded import constrained_gauss_schur


def enriched_coupled_reached_sample(raw_fields,representation,angular,trace,trace_rate,*,nu_squared_action):
    """Apply the literal full weak action with all80 independent background coefficients."""
    rep=representation;count=len(rep['gauge_labels']);hs=100+2*count
    raw=np.asarray(raw_fields)
    if count!=80 or not np.isrealobj(raw) or raw.shape!=(hs+8,) or not np.isfinite(raw).all():
        raise ValueError('complete finite real raw268 enriched background required')
    Q,Qt=(np.asarray(value) for value in (trace,trace_rate))
    if any(not np.isrealobj(value) or value.shape!=(400,8) or not np.isfinite(value).all() for value in (Q,Qt)):
        raise ValueError('complete same-background real400 reached trace and time derivative required')
    if np.any(Q[:160]) or np.any(Qt[:160]):raise ValueError('spatial source trace; allAt/Ar remain internal')
    if not np.isfinite(nu_squared_action) or nu_squared_action<0:raise ValueError('explicit nonnegative Higgs action parameter required')
    q,v,m=raw[:37],raw[37:74],raw[74:98];normal,normal_rate=raw[98:100]
    geo=geometric_connection_coefficient_jets(12,q,v,m,rep['rho'],source_value=normal,source_rate=normal_rate,clock='coordinate_time')
    A=np.einsum('rj...,j->r...',rep['gauge_basis'],raw[100:100+count])[:,0]
    At=np.einsum('rj...,j->r...',rep['gauge_basis'],raw[100+count:hs])[:,0]
    Ar=np.einsum('rj...,j->r...',rep['gauge_radial_basis'],raw[100:100+count])[:,0]
    local=[]
    for j,row in enumerate(geo['rows']):
        A[j,2:]+=M*(row['connection_lambda'].value-1)
        At[j,2:]+=M*row['lambda_tau'].value
        Ar[j,2:]+=M*row['lambda_rho'].value
        density=[row[k].value for k in ('electric','radial','angular','electric_radial','shift')]
        local.append(full_constant_angular_hessian(A[j],At[j],Ar[j],density))
    H,Hr=regular_radial_basis(rep['rho'],1)
    E=np.concatenate((np.eye(20)[None],angular['derivative_matrices']))
    products=np.array([[a.T@b for b in E] for a in E])
    maxwell=moving_trace_time_forms(np.array([a['tensor'] for a in local]),rep['radial_quadrature'],H,Hr,Q,Qt,products)
    idx=np.r_[np.arange(400),np.arange(480,488)];matrices=[]
    for old in maxwell:
        new=np.zeros((488,488));new[np.ix_(idx,idx)]=old;matrices.append(new)
    weights=intrinsic_m4_weight_jet(12,q,v,m,source_value=normal,source_rate=normal_rate)
    wall=np.einsum('fcj,j->fc',rep['wall_trace_map'],raw[100:100+count])
    wall[2:]+=M*(weights['mechanical_connection_lambda'].value-1)
    scalar=intrinsic_scalar_trace_hessian(raw[hs:hs+4],raw[hs+4:hs+8],wall,
        np.array([weights[k].value for k in ('wT','wS','wV')]),lambda_H=rep['scalar_matching']['lambda_H'],
        nu_squared_action=nu_squared_action,angular=angular)['matrix']
    value=np.zeros((560,488));velocity=np.zeros_like(value)
    value[:80,400:480]=np.eye(80);value[80:480,480:]=Q;velocity[480:,400:480]=np.eye(80)
    scalar_forms=(8*velocity.T@scalar@velocity,8*value.T@scalar@velocity,8*value.T@scalar@value)
    matrices=[a+b for a,b in zip(matrices,scalar_forms)]
    rows=moving_trace_gauge_rows(local,A,rep['radial_quadrature'],H,Hr,Q,Qt,E)
    expanded=np.zeros((4,80,488));expanded[:,:,:400]=rows[:,:,:400];expanded[:,:,480:]=rows[:,:,400:]
    reduced=constrained_gauss_schur(*matrices,80)
    return dict(raw_forms=tuple(matrices),reduced=reduced,scalar_forms=scalar_forms,
        gauge_weak_rows=expanded,source=Q,source_rate=Qt,raw_fields=raw,
        full_background_values=np.array([A,At,Ar]),scalar_Maxwell_relative_normalization=8.,
        all_moving_trace_contacts_retained=True,
        exact_affine_background_source_image_retained=True,
        response_radial_scope='inherited interior polynomial plus explicit independent wall source; finite Galerkin response',
        physical_free_wall_inverse=False,physical_Pauli_value=False)
