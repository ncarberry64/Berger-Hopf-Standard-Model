import numpy as np
from bhsm.interface.muon_holomorphic_n1_magnetic_action import (
    original_signed_stage,holomorphic_local_B_trace,magnetic_angular_trace,
    complete_gauge_wall_constraints,original_named_wall_lift,known_wall_source_weak_response,
    original_field_permutation,
)
from bhsm.interface.muon_holomorphic_current_source import holomorphic_current_stage
from bhsm.interface.muon_parent_maxwell_full_weak import M


def fixture():
    rng=np.random.default_rng(202610123);draw=lambda shape:.003*(rng.normal(size=shape)+.2j*rng.normal(size=shape))
    x=draw((268,));x[260:264]=[1.1+.03j,.4-.02j,.07+.01j,.03-.01j]
    dx=.03*(rng.normal(size=(268,2))+1j*rng.normal(size=(268,2)))
    p=x.copy();p[2]+=.001j;refs=np.array([x.copy(),x.copy()]);refs[1,5]+=.0002
    names=('A_tau','A_rho','A_1','A_2','A_3');unit=np.eye(20).reshape(20,5,4)
    phi=np.array([[.3,.7,.2,.4],[.4,.5,.6,.7],[.5,.3,.8,.9]])
    pr=phi*.3;wv=np.array([.2,-.1,.4,1.])
    rep=dict(rho=np.array([.1,.4,1.]),radial_quadrature=np.array([.2,.3,.4]),
        gauge_basis=np.array([np.concatenate([v*unit for v in r])for r in phi])[:,:,None],
        gauge_radial_basis=np.array([np.concatenate([v*unit for v in r])for r in pr])[:,:,None],
        wall_trace_map=np.concatenate([v*np.eye(20)for v in wv],axis=1).reshape(5,4,80),
        gauge_labels=[dict(field=names[f],internal=c,wall_lift=r==3)for r in range(4)for f in range(5)for c in range(4)])
    return x,dx,p,.6*dx,refs,np.stack((.2*dx,-.1j*dx)),rep


def test_actual_stage_profile_and_density_direction_before_wall_projection():
    x,dx,p,dp,refs,dr,rep=fixture()
    b=original_signed_stage(x,dx,p,dp,refs,dr,rep,side='child',lambda_H=.129,nu_squared_action=4.)
    row=b['row'];s=b['stage'];gb=rep['gauge_basis'][:,:,0]
    expected=np.einsum('rjfc,j->rfc',gb,x[100:180]);expected[:,2:]+=M*(s['total_profile'][:3,0,None,None]-1)
    np.testing.assert_allclose(row['A'],expected,atol=0)
    h=2e-5
    plus=original_signed_stage(x+h*dx[:,0],dx,p+h*dp[:,0],dp,refs+h*dr[:,:,0],dr,rep,side='child',lambda_H=.129,nu_squared_action=4.)
    minus=original_signed_stage(x-h*dx[:,0],dx,p-h*dp[:,0],dp,refs-h*dr[:,:,0],dr,rep,side='child',lambda_H=.129,nu_squared_action=4.)
    for key in ('A','At','Ar','densities','wall_A','weights'):
        np.testing.assert_allclose(b['row_first'][key][0],(plus['row'][key]-minus['row'][key])/(2*h),rtol=2e-7,atol=2e-6)
    assert np.linalg.norm(b['row_first']['A'])>1e-4
    assert b['mechanical_profile_count']==1


def test_B_charge_radius_time_and_source_motion_keep_analytic_branches():
    x,dx,p,dp,refs,dr,rep=fixture()
    stage=lambda a,d:holomorphic_current_stage(a,d,p,dp,refs,dr,rep,side='child')
    a=holomorphic_local_B_trace(x,dx,stage(x,dx),electric_charge=.3028)
    step=2e-5
    for k in range(2):
        plus=holomorphic_local_B_trace(x+step*dx[:,k],dx,stage(x+step*dx[:,k],dx),electric_charge=.3028)
        minus=holomorphic_local_B_trace(x-step*dx[:,k],dx,stage(x-step*dx[:,k],dx),electric_charge=.3028)
        for key in ('Q','Q_coordinate_time'):
            np.testing.assert_allclose(a[key+'_first'][k],(plus[key]-minus[key])/(2*step),rtol=5e-8,atol=3e-10)
    imaginary=holomorphic_local_B_trace(x,1j*dx,stage(x,1j*dx),electric_charge=.3028)
    np.testing.assert_allclose(imaginary['Q_first'],1j*a['Q_first'],atol=2e-16)
    np.testing.assert_array_equal(a['Q'][:2],0)
    np.testing.assert_array_equal(a['Q_coordinate_time'][:2],0)
    assert np.linalg.norm(a['Q'])>.01


def test_named_full_wall_lift_and_only_proved_central_Ar_duplicate():
    x,dx,p,dp,refs,dr,rep=fixture()
    b=original_signed_stage(x,dx,p,dp,refs,dr,rep,side='parent',lambda_H=.129,nu_squared_action=4.)
    a=complete_gauge_wall_constraints(b['lifts'],4);L=original_named_wall_lift(rep,b['value_permutation'])
    np.testing.assert_allclose(b['lifts']['W']@L,np.eye(20),atol=0)
    assert a['constraint'].shape==(92,336)
    assert a['duplicate_wall_index']==7
    changed={**b['lifts'],'W':b['lifts']['W'].copy()};changed['W'][7,80]+=.01
    import pytest
    with pytest.raises(ValueError,match='redundancy'):complete_gauge_wall_constraints(changed,4)


def test_known_lift_Qdot_and_both_time_placements_reach_full_original_rows():
    x,dx,p,dp,refs,dr,rep=fixture()
    b=original_signed_stage(x,dx,p,dp,refs,dr,rep,side='parent',lambda_H=.129,nu_squared_action=4.)
    nh=4;n=336;W=np.kron(np.r_[b['lifts']['W'],b['lifts']['hv']],np.eye(4));F=np.kron(b['lifts']['frame_rows'],np.eye(4))
    rng=np.random.default_rng(177);z=.01*(rng.normal(size=(n,n))+1j*rng.normal(size=(n,n)))
    K=np.diag(np.linspace(1,2,n)).astype(complex)+z+z.T
    B=.02*(rng.normal(size=(n,n))+1j*rng.normal(size=(n,n)))
    mass=np.eye(n,dtype=complex);mass[:64]=0;mass[:,:64]=0
    form=dict(K=K,M=mass,B_forward=B,B_reverse=B.T,wall_value_map=W,frame_rows=F)
    first={key:np.zeros((2,n,n),complex)for key in ('K','M','B_forward','B_reverse')}
    source=holomorphic_local_B_trace(x,dx,b['stage'],electric_charge=.3028)
    a=known_wall_source_weak_response([form,form],[first,first],np.array([.02,.02]),[source,source],rep,b['value_permutation'])
    np.testing.assert_allclose(a['original_rows'],0,atol=3e-13)
    np.testing.assert_allclose(a['original_first_rows'],0,atol=4e-13)
    np.testing.assert_allclose(a['prescribed_full_gauge_unknown_wall_rows'],0,atol=1e-13)
    np.testing.assert_array_equal(a['C2_ramp_initial_value_and_rate'],0)
    for q in a['point_sources']:
        np.testing.assert_allclose(q['original_full_wall_rows'],0,atol=2e-13)
        np.testing.assert_allclose(q['original_full_wall_rate_rows'],0,atol=4e-12)
    # Unbordered field/Gauss equations carry the retained wall reaction.
    np.testing.assert_allclose(a['unbordered_field_rows']+a['field_wall_and_frame_reaction'],
        a['original_rows'].reshape(2,428,3)[:,:336],atol=2e-16)
    assert np.linalg.norm(a['wall_reactions'])>1e-3
    assert np.linalg.norm(a['unbordered_Gauss_rows'])>1e-6
    no_rate={**source,'Q_coordinate_time':np.zeros_like(source['Q_coordinate_time']),
        'Q_coordinate_time_first':np.zeros_like(source['Q_coordinate_time_first'])}
    c=known_wall_source_weak_response([form,form],[first,first],np.array([.02,.02]),[no_rate,no_rate],rep,b['value_permutation'])
    assert np.linalg.norm(a['source_rhs']-c['source_rhs'])>1e-8
