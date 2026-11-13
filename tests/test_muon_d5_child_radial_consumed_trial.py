import numpy as np
from bhsm.interface.muon_d5_child_radial_consumed_trial import (
    radial_trial_chart,old_field_initializer,extend_actual_data,
    compile_consumed_trial,solve_consumed_trial,solve_consumed_trial_source,evaluate_consumed_trial,
)
from bhsm.interface.muon_d5_child_characteristic_field import characteristic_bases
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace


def test_saved_values_and_time_jets_recover_the_completed_polynomial():
    t=np.linspace(0,.5,6);r=np.array([.2,.4,.6]);c=radial_trial_chart(t,r)
    tp=.5*np.array([.137,.419,.863]);rp=.2+.4*np.array([.083,.377,.911])
    V=lambda t,r:1+2*t-r+3*t**5*r**2+1j*t*r
    D=lambda t,r:2+15*t**4*r**2+1j*r
    v=V(tp[:,None],rp[None,:])[:,:,None,None];d=D(tp[:,None],rp[None,:])[:,:,None,None]
    recovered=old_field_initializer(v,d,tp,rp,c)
    expected=V(t[:,None],c['radii'][None,:])[:,:,None,None]
    np.testing.assert_allclose(recovered,expected,atol=8e-14)
    np.testing.assert_allclose(c['birth_degree2_extension'][c['shared_radial_indices']],np.eye(3),atol=3e-16)
    np.testing.assert_array_equal(c['higher_birth_free_lift'][c['shared_radial_indices']],np.zeros((3,14)))


def test_actual_nonzero_data_and_source_use_original_principal_on_r17():
    # An analytic control for the numerical method; not a physical state.
    t=np.linspace(0,.01,6);r=np.array([.2,.4,.6]);chart=radial_trial_chart(t,r)
    idx=np.array([6,7,22,23,38,39,54,55]);f=full_d5_localized_lepton_trace();g=f['gamma5D_particle']
    T=1j*np.kron(g[0],np.eye(16))[np.ix_(idx,idx)];R=1j*np.kron(g[4],np.eye(16))[np.ix_(idx,idx)];A=np.linalg.solve(T,R)
    rng=np.random.default_rng(916);a=rng.normal(size=(8,2))+1j*rng.normal(size=(8,2));b=a/3+.2
    V=lambda t,r:a+r*b-t*A@b
    Vt=lambda t,r:-A@b
    X=lambda t,r:-t*V(t,r)
    Xt=lambda t,r:-V(t,r)-t*Vt(t,r)
    z=np.zeros((8,384,2),complex);zx=np.zeros_like(z);rows=128+idx
    for j,rho in enumerate(r):z[j,rows]=V(0,rho);zx[j,rows]=X(0,rho)
    inner,outer=characteristic_bases('particle',1);(_,ii),(_,oi)=characteristic_bases('particle',1,idx)
    for j,time in enumerate(t[1:]):
        local=np.r_[ii,32+oi];z[j+3,128+local]=np.r_[inner[idx].conj().T@V(time,r[0]),outer[idx].conj().T@V(time,r[-1])][np.r_[ii,32+oi]]
        zx[j+3,128+local]=np.r_[inner[idx].conj().T@X(time,r[0]),outer[idx].conj().T@X(time,r[-1])][np.r_[ii,32+oi]]
    data,dx,_=extend_actual_data(z,zx,idx,'particle',1,chart)
    shape=(6,17,8,8);zero=np.zeros(shape,complex)
    c=dict(time=np.broadcast_to(T,shape),radial=np.broadcast_to(R,shape),body=zero)
    cx=dict(time=zero[None],radial=zero[None],body=np.broadcast_to(T,(1,*shape)))
    system=compile_consumed_trial(c,cx,chart,idx,'particle',1)
    tp=.01*np.array([.137,.419,.863]);rp=.2+.4*np.array([.083,.377,.911])
    sample=lambda fun:np.array([[fun(time,rho) for rho in rp] for time in tp])
    initial=old_field_initializer(sample(V),sample(Vt),tp,rp,chart)
    value,report=solve_consumed_trial(system,data,initial)
    initialx=old_field_initializer(sample(X),sample(Xt),tp,rp,chart)
    source,sreport=solve_consumed_trial_source(system,value,dx,0,initialx)
    field=evaluate_consumed_trial(system,value,source,tp,rp)
    np.testing.assert_allclose(field['value'],sample(V),atol=2e-12)
    np.testing.assert_allclose(field['source'],sample(X),atol=2e-12)
    assert report['full_family_solved'] is False and sreport['inverse_time_vertex_included']
