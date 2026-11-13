"""Literal magnetic cubic and energy contacts at the true attached E1.

The inherited canonical first state is re-evaluated by the endpoint
Legendre/Gauss owner.  This does not reuse midpoint-held velocities or
claim that the finite first-response history solves a global birth BVP.
"""
from __future__ import annotations
import numpy as np

from .muon_current_source_motion_cubic import (
    _real, current_face_source_jets, maxwell_cross_hessian, higgs_cross_hessian,
)
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP, VOLUME
from .muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
from .muon_parent_maxwell_full_weak import M
from .muon_birth_trace_enriched_action import generic_coordinate_lift
from .muon_magnetic_source_mean_load import magnetic_source_complete_mean_load
from .muon_magnetic_true_birth_fields import true_magnetic_birth_fields


def fixed_first_pair_action(fields, representation, angular, *, nu_squared_action):
    """D2L[u_A,u_B] and the two literal first-velocity momentum contacts.

    The rate tests contain the actual physical future field rates,
    including Qdot at the wall.  Using coefficient energy from the
    moving-source K matrix would omit this wall momentum contribution.
    """
    rep=representation;raw=_real(fields['raw_fields'],'true E1 raw268',(268,))
    u,ut,ur=(_real(fields[k],'true first field') for k in
             ('first_gauge','first_gauge_rate','first_gauge_radial'))
    h,ht,aw=(_real(fields[k],'true scalar/wall field') for k in
             ('first_H','first_H_rate','first_wall_gauge'))
    E=angular['derivative_matrices'];count=len(h)
    if u.shape!=(len(rep['rho']),count,5,4,20) or ut.shape!=u.shape or ur.shape!=u.shape:
        raise ValueError('complete true-E1 future gauge value/rate/radial fields required')
    A=np.einsum('rj...,j->r...',rep['gauge_basis'],raw[100:180])[:,0]
    At=np.einsum('rj...,j->r...',rep['gauge_basis'],raw[180:260])[:,0]
    Ar=np.einsum('rj...,j->r...',rep['gauge_radial_basis'],raw[100:180])[:,0]
    geo=geometric_connection_coefficient_jets(12,raw[:37],raw[37:74],raw[74:98],
        rep['rho'],source_value=raw[98],source_rate=raw[99])
    quadratic=np.zeros((count,count));velocity_cross=np.zeros_like(quadratic)
    for j,row in enumerate(geo['rows']):
        A[j,2:]+=M*(row['connection_lambda'].value-1)
        At[j,2:]+=M*row['lambda_tau'].value
        Ar[j,2:]+=M*row['lambda_rho'].value
        density=np.array([row[k].value for k in
            ('electric','radial','angular','electric_radial','shift')])
        kwargs=(A[j],At[j],Ar[j],u[j],ut[j],ur[j])
        quadratic+=rep['radial_quadrature'][j]*maxwell_cross_hessian(
            *kwargs,u[j],ut[j],ur[j],E,density)
        zero=np.zeros_like(u[j])
        cross=maxwell_cross_hessian(*kwargs,zero,ut[j],zero,E,density)
        velocity_cross+=rep['radial_quadrature'][j]*(cross+cross.T)
    w=current_face_source_jets(raw[:100])['intrinsic_weights']
    wall=np.einsum('fcj,j->fc',rep['wall_trace_map'],raw[100:180])
    wall[2:]+=M*(w['mechanical_connection_lambda'].value-1)
    weights=np.array([w[k].value for k in ('wT','wS','wV')])
    scalar_args=dict(lambda_H=rep['scalar_matching']['lambda_H'],
                     nu_squared_action=nu_squared_action)
    scalar=higgs_cross_hessian(raw[260:264],raw[264:],wall,h,ht,aw,h,ht,aw,
                              E,weights,**scalar_args)
    zero_h=np.zeros_like(h);zero_a=np.zeros_like(aw)
    cross=higgs_cross_hessian(raw[260:264],raw[264:],wall,h,ht,aw,
                             zero_h,ht,zero_a,E,weights,**scalar_args)
    return dict(fixed_first_pair_action=MAXWELL_TO_CAP*quadratic+scalar/VOLUME**2,
        fixed_first_velocity_momentum_contact=MAXWELL_TO_CAP*velocity_cross+
            (cross+cross.T)/VOLUME**2)


def canonical_energy_mixed_contact(background_velocity, fixed_master_load,
        action_pair, first_velocity_momentum_contact):
    """Literal E_AB for E=v L_v-L on a fixed linear first-field chart."""
    v=_real(background_velocity,'same-action background velocities')
    j=_real(fixed_master_load,'fixed-action cubic master load')
    a=_real(action_pair,'fixed-action first pair')
    p=_real(first_velocity_momentum_contact,'both first-velocity contacts')
    if v.ndim!=1 or j.shape!=(2*len(v)+40,)+a.shape or a.ndim!=2 or a.shape!=p.shape:
        raise ValueError('complete x/v/y master load and both source orders required')
    return np.einsum('i,iAB->AB',v,j[len(v):2*len(v)])+p-a


def true_birth_mean_contact_application(inputs, *, repository, angular):
    """Apply D3L and explicit source motion to the recovered true E1 fields."""
    birth=true_magnetic_birth_fields(inputs,repository=repository)
    fields=birth['fields'];rep=birth['representation'];source=birth['source']
    applied=magnetic_source_complete_mean_load(fields['raw_fields'],rep,angular,
        source,1.,0.,**{key:fields[key] for key in
        ('first_gauge','first_gauge_rate','first_gauge_radial','first_wall_gauge','first_H','first_H_rate')},
        nu_squared_action=birth['action_parameters']['nu_squared_action'])
    P=generic_coordinate_lift(rep['gauge_labels'])['lift']
    master=np.einsum('rc,rAB->cAB',P,applied['raw_mean_cotangent'])
    fixed_master=np.einsum('rc,rAB->cAB',P,applied['fixed_field_raw_mean_cotangent'])
    motion_master=master-fixed_master
    # P contains the exact coordinate identification.  Its velocity
    # columns select qdot, normal_rate, dynamic gauge rates and Hdot.
    base_v=P[:,106:212].T@fields['raw_fields']
    pairs=fixed_first_pair_action(fields,rep,angular,
        nu_squared_action=birth['action_parameters']['nu_squared_action'])
    fixed_energy=canonical_energy_mixed_contact(base_v,fixed_master,
        pairs['fixed_first_pair_action'],pairs['fixed_first_velocity_momentum_contact'])
    return dict(birth=birth,application=applied,**pairs,
        mean_master_cotangent=master,fixed_master_cotangent=fixed_master,
        source_motion_master_cotangent=motion_master,
        canonical_velocity_contact=master[106:212],
        fixed_canonical_velocity_contact=fixed_master[106:212],
        source_motion_canonical_velocity_contact=motion_master[106:212],
        algebraic_contact=master[212:],fixed_algebraic_contact=fixed_master[212:],
        source_motion_algebraic_contact=motion_master[212:],
        fixed_action_energy_contact=fixed_energy,
        source_motion_velocity_work=np.einsum('i,iAB->AB',base_v,motion_master[106:212]),
        fixed_multiplier_constraint_contact=applied['fixed_field_raw_mean_cotangent'][74:98],
        source_motion_multiplier_constraint_contact=applied['source_motion_cotangent'][74:98],
        fixed_action_energy_equation='E_AB=v_base*(D3L)_v,AB+D2L[u_A,V_B]+D2L[u_B,V_A]-D2L[u_A,u_B]',
        source_motion_energy_scope='separate velocity-work pullback; not promoted to nonlinear angular H-selected source family',
        true_E1_endpoint_coefficients_used=True,source_cell_midpoint_velocities_substituted=False,
        global_mean_reset_or_Pauli_completed=False)
