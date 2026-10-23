"""Independent canonical sign, crossing and readout checks; no physical controls."""
import numpy as np
import pytest
from bhsm.interface.muon_parent_mean_causal_descriptor import (
    _descriptor_from_samples, mean_phase_coefficients,mean_implicit_descriptor_step,
    implicit_mean_source_target_application,
)


def _action(crossing=False):
    t=np.linspace(0,1,5);H=np.zeros((5,3,3));J=np.zeros((5,3,8,8))
    H[:,0,0]=1 if crossing else .3;H[:,1,1]=t-.5 if crossing else 2
    H[:,2,2]=-1
    if not crossing:H[:,0,1]=H[:,1,0]=.2;H[:,1,2]=H[:,2,1]=.5;H[:,0,2]=H[:,2,0]=.1
    for k,u in enumerate(t):
        J[k,0]=u*np.eye(8);J[k,1]=u*u*np.eye(8);J[k,2]=(.4+u)*np.eye(8)
    return _descriptor_from_samples(dict(times=t,hessian_samples=H,source_samples=J,x_count=1,v_count=1,y_count=1))


def test_canonical_source_and_algebraic_rows_are_retained():
    d=_action();t=.3;a=mean_phase_coefficients(t,d);H=d['hessian'](t);J=d['source'](t).reshape(3,64)
    z=np.vstack((np.linspace(0,1,64),np.linspace(1,2,64)))
    w=a['U']@z+a['f'];rate=a['F']@z+a['b']
    np.testing.assert_allclose(H[1:,1:]@w,z[1:]*np.array([[1],[0]])-H[1:,:1]@z[:1]-J[1:])
    np.testing.assert_allclose(rate[0],w[0])
    np.testing.assert_allclose(rate[1],(H[:1,:1]@z[:1]+H[:1,1:]@w+J[:1])[0])
    assert np.linalg.norm(a['f'][1])>0  # actual algebraic Jy affects the canonical dynamics


def test_full_midpoint_step_remains_a_descriptor_at_legendre_crossing():
    d=_action(crossing=True);step=mean_implicit_descriptor_step(d,.4,.6)
    assert d['hessian'](.5)[1,1]==0
    assert np.linalg.matrix_rank(step['K'])==4
    assert step['instantaneous_saddle_inverse_used'] is False


def test_exact_discrete_adjoint_includes_velocity_algebraic_direct_readouts():
    d=_action();times=np.array([.17,.42,.83]);loads=np.zeros((3,3,2))
    loads[:,:,0]=[[1,.2,.4],[.3,-.7,.2],[-.2,.1,.8]]
    loads[:,:,1]=[[.1,1,-.3],[.8,.5,.2],[1,-.1,-.3]]
    a=implicit_mean_source_target_application(d,time_steps=32,target_times=times,target_loads=loads)
    np.testing.assert_allclose(a['forward_target'],a['adjoint_target'],rtol=2e-13,atol=2e-13)
    assert a['maximum_primal_step_backward_error']<1e-14
    assert a['maximum_adjoint_step_backward_error']<1e-14
    assert a['continuous_causal_regularity_established'] is False


def test_complex_or_nonfinite_source_is_not_projected_to_real():
    d=_action();samples=dict(d['samples']);samples['source_samples']=samples['source_samples'].astype(complex)
    with pytest.raises(ValueError,match='explicit real'):_descriptor_from_samples(samples)
    samples=dict(d['samples']);samples['source_samples']=samples['source_samples'].copy();samples['source_samples'][0,0,0,0]=np.nan
    with pytest.raises(ValueError,match='finite'):_descriptor_from_samples(samples)


def test_arb_encloses_exact_stored_discrete_forward_and_adjoint():
    d=_action();times=np.array([.2,.8]);loads=np.ones((2,3,1))
    a=implicit_mean_source_target_application(d,time_steps=4,target_times=times,target_loads=loads,precision_bits=128)
    assert a['exact_stored_forward_adjoint_intervals_overlap']
    assert a['forward_adjoint_entrywise_difference_upper']<1e-30
    assert a['exact_stored_target_entry_radius_upper']<1e-30
    assert 'continuum errors excluded' in a['arithmetic_scope']
