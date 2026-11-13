import numpy as np
from bhsm.interface.muon_holomorphic_n1_magnetic_cauchy import (
    causal_prescribed_magnetic_prefix,magnetic_trace_time_germ,
)
from bhsm.interface.muon_holomorphic_n1_magnetic_action import original_signed_stage,holomorphic_local_B_trace
from test_muon_holomorphic_n1_magnetic_action import fixture


def test_actual_source_zero_Cauchy_keeps_Gauss_reaction_and_the_same_trace_rate():
    x,dx,p,dp,refs,dr,rep=fixture()
    # Original prescribed-wall trial domain, distinct from arbitrary wall maps.
    rep['wall_trace_map'][:]=0;rep['wall_trace_map'].reshape(20,80)[:,60:]=np.eye(20)
    b=original_signed_stage(x,dx,p,dp,refs,dr,rep,side='parent',lambda_H=.129,nu_squared_action=4.)
    n=336;W=np.kron(np.r_[b['lifts']['W'],b['lifts']['hv']],np.eye(4));F=np.kron(b['lifts']['frame_rows'],np.eye(4))
    rng=np.random.default_rng(1278);K=.02*(rng.normal(size=(n,n))+1j*rng.normal(size=(n,n)));K=K+K.T+np.eye(n)
    BF=.01*(rng.normal(size=(n,n))+1j*rng.normal(size=(n,n)));BF[:,:64]=0
    M=np.eye(n,dtype=complex);M[:64]=0;M[:,:64]=0
    f=dict(K=K,M=M,B_forward=BF,B_reverse=BF.T,wall_value_map=W,frame_rows=F)
    s=holomorphic_local_B_trace(x,dx,b['stage'],electric_charge=.3028)
    h=np.array([.002,.002]);a=causal_prescribed_magnetic_prefix([f,f],h,[s,s],rep,b['value_permutation'])
    np.testing.assert_array_equal(a['initial_reduced_canonical_state'],0)
    zero=magnetic_trace_time_germ(0,[s,s],sum(h))
    for q in zero:np.testing.assert_array_equal(q,0)
    assert np.linalg.norm(a['final_reduced_canonical_state'])>.001
    for point in a['point_sources']:
        np.testing.assert_allclose(point['original_At_interior_Gauss_rows'],0,atol=3e-12)
        np.testing.assert_allclose(point['original_full_wall_rows'],0,atol=1e-15)
        np.testing.assert_allclose(point['original_full_wall_rate_rows'],0,atol=2e-13)
        np.testing.assert_allclose(point['original_reconstructed_rows'],0,atol=5e-11)
    # Differentiate the actual continuous Hermite/ramp source, not nodal secants.
    t=.61;step=1e-5;Q,Qt,Qtt=magnetic_trace_time_germ(t,[s,s],sum(h))
    plus=magnetic_trace_time_germ(t+step,[s,s],sum(h));minus=magnetic_trace_time_germ(t-step,[s,s],sum(h))
    np.testing.assert_allclose(Qt,(plus[0]-minus[0])/(2*step*sum(h)),rtol=2e-8,atol=1e-9)
    np.testing.assert_allclose(Qtt,(plus[1]-minus[1])/(2*step*sum(h)),rtol=3e-8,atol=1e-7)


def test_same_causal_operator_and_both_source_placements_first_are_independent():
    x,dx,p,dp,refs,dr,rep=fixture()
    rep['wall_trace_map'][:]=0;rep['wall_trace_map'].reshape(20,80)[:,60:]=np.eye(20)
    b=original_signed_stage(x,dx,p,dp,refs,dr,rep,side='parent',lambda_H=.129,nu_squared_action=4.)
    n=336;rng=np.random.default_rng(1901)
    K=np.diag(np.linspace(.8,1.2,n)).astype(complex)
    BF=.01*(rng.normal(size=(n,n))+1j*rng.normal(size=(n,n)));BF[:,:64]=0
    M=np.eye(n,dtype=complex);M[:64]=0;M[:,:64]=0
    f=dict(K=K,M=M,B_forward=BF,B_reverse=BF.T)
    df={name:.005*(rng.normal(size=(2,n,n))+1j*rng.normal(size=(2,n,n)))for name in f}
    df['M'][:,:64]=0;df['M'][:,:,:64]=0;df['B_forward'][:,:,:64]=0;df['B_reverse'][:,:64]=0
    s=holomorphic_local_B_trace(x,dx,b['stage'],electric_charge=.3028);h=np.array([.002,.002])
    a=causal_prescribed_magnetic_prefix([f,f],h,[s,s],rep,b['value_permutation'],forms_first=[df,df])
    step=2e-5;values=[]
    for t in (step,-step):
        ff={key:v+t*df[key][0]for key,v in f.items()}
        ss=dict(s,Q=s['Q']+t*s['Q_first'][0],Q_coordinate_time=s['Q_coordinate_time']+t*s['Q_coordinate_time_first'][0])
        values.append(causal_prescribed_magnetic_prefix([ff,ff],h,[ss,ss],rep,b['value_permutation']))
    actual=a['final_reduced_canonical_state_first'][0]
    expected=(values[0]['final_reduced_canonical_state']-values[1]['final_reduced_canonical_state'])/(2*step)
    np.testing.assert_allclose(actual,expected,rtol=2e-5,atol=2e-8)
    assert np.linalg.norm(actual)>.001
    np.testing.assert_array_equal(a['initial_reduced_canonical_state_first'],0)
    for point in a['point_sources']:
        np.testing.assert_allclose(point['original_first_At_Gauss_rows'],0,atol=1e-10)
