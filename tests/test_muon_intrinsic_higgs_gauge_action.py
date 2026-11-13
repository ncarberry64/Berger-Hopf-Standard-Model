import math
import numpy as np
import pytest

from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import Jet
from bhsm.interface.muon_intrinsic_higgs_gauge_action import (
    higgs_u2_real_representation,intrinsic_higgs_gauge_action_jet,
)


def weights(x=0.,y=0.):
    # A declared geometry control with two independent coordinates.
    x=Jet.affine(x,np.array([1.,0.]));y=Jet.affine(y,np.array([0.,1.]))
    return dict(wT=2*x.exp(),wS=3*y.exp(),wV=4*(x+y).exp(),
        mechanical_connection_lambda=.7+.1*x-.2*y,wall_rate=.03+x*y)


def data():
    rng=np.random.default_rng(465)
    V=np.broadcast_to(np.eye(4),(2,4,4)).copy()
    D=.2*rng.normal(size=(2,4,4,4))
    A=np.broadcast_to(np.eye(20).reshape(5,4,20),(2,5,4,20)).copy()
    return dict(scalar_coefficients=np.array([.1,.4,-.2,.3]),scalar_value_map=V,
        scalar_derivative_map=D,gauge_coefficients=.1*rng.normal(size=20),
        gauge_trace_map=A,angular_quadrature=np.array([.4,.6]),lambda_H=.13,nu_squared_action=.3)


def literal(w,d):
    # Direct COMPLEX doublet computation, independent of the producer's
    # real matrix representation and Jet action contractions.
    V,D,c,g,A=(d[k] for k in ('scalar_value_map','scalar_derivative_map',
        'scalar_coefficients','gauge_coefficients','gauge_trace_map'))
    h=V@c;dh=np.einsum('pmic,c->pmi',D,c)
    h=h[:,:2]+1j*h[:,2:];dh=dh[:,:,:2]+1j*dh[:,:,2:]
    a=np.einsum('pmac,c->pma',A,g)
    T=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]])/2
    generators=np.concatenate((-1j*T/np.sqrt(2),(-.5j*np.eye(2)/np.sqrt(10/3))[None]))
    temporal=a[:,0]+2*w['wall_rate'].value*a[:,1]
    spatial=a[:,2:].copy()
    for j in range(3):spatial[:,j,j]+=np.sqrt(8)*(w['mechanical_connection_lambda'].value-1)
    connection=np.concatenate((temporal[:,None],spatial),axis=1)
    dh=dh+np.einsum('pma,aij,pj->pmi',connection,generators,h)
    nu2=d['nu_squared_action']
    return 2*np.pi**2*np.sum(d['angular_quadrature']*(
        w['wT'].value*np.sum(abs(dh[:,0])**2,axis=-1)
        -w['wS'].value*np.sum(abs(dh[:,1:])**2,axis=(-1,-2))
        -w['wV'].value*d['lambda_H']*(np.sum(abs(h)**2,axis=-1)-nu2)**2))


def test_unit_trace_generators_match_owned_fundamental_and_bracket():
    r=higgs_u2_real_representation();G=r['complex_generators']
    np.testing.assert_allclose(G[0]@G[1]-G[1]@G[0],G[2]/np.sqrt(2),atol=1e-16)
    np.testing.assert_array_equal(G[3]@G[0]-G[0]@G[3],0)
    np.testing.assert_allclose(r['real_generators']+r['real_generators'].transpose(0,2,1),0,atol=0)
    assert r['hypercharge']=='1/2'


def test_same_action_matches_independent_complex_lagrangian_and_all_joint_first_derivatives():
    d=data();w=weights();out=intrinsic_higgs_gauge_action_jet(w,**d);S=out['action']
    assert S.value==pytest.approx(literal(w,d),rel=3e-15)
    rng=np.random.default_rng(466);v=rng.normal(size=len(S.gradient));step=2e-6
    def shifted(sign):
        e=dict(d);e['scalar_coefficients']=d['scalar_coefficients']+sign*step*v[2:6]
        e['gauge_coefficients']=d['gauge_coefficients']+sign*step*v[6:]
        return literal(weights(sign*step*v[0],sign*step*v[1]),e)
    assert (shifted(1)-shifted(-1))/(2*step)==pytest.approx(S.gradient@v,rel=3e-8,abs=2e-7)
    assert not out['stationarity_claim'] and not out['quantum_native_H_load_included']
    assert out['classical_body_source_provenance'].startswith('DERIVED_CLASSICAL_BODY_ZERO')


def test_mixed_geometry_scalar_gauge_hessian_is_real_linear_and_includes_moving_Ar_trace():
    d=data();S=intrinsic_higgs_gauge_action_jet(weights(),**d)['action']
    step=1e-5;direction=np.arange(len(S.gradient),dtype=float)/len(S.gradient)-.5
    def shifted(sign):
        e=dict(d);e['scalar_coefficients']=d['scalar_coefficients']+sign*step*direction[2:6]
        e['gauge_coefficients']=d['gauge_coefficients']+sign*step*direction[6:]
        return intrinsic_higgs_gauge_action_jet(weights(sign*step*direction[0],sign*step*direction[1]),**e)['action'].gradient
    np.testing.assert_allclose((shifted(1)-shifted(-1))/(2*step),S.hessian@direction,rtol=2e-7,atol=3e-7)
    np.testing.assert_allclose(S.hessian,S.hessian.T,atol=1e-13)
    assert np.linalg.norm(S.hessian[2:6,6:])>.1
    # Ar is not erased on a moving material wall: temporal connection
    # depends on Ar even with no ordinary temporal derivative map.
    assert np.linalg.norm(S.hessian[2:6,10:14])>.01


def test_joint_scale_coordinate_differentiates_actual_unit_conversion():
    d=data();del d['nu_squared_action'];d['nu_squared_GeV_squared']=.42*7**2;d['log_energy_unit_GeV']=math.log(7)
    out=intrinsic_higgs_gauge_action_jet(weights(),**d);S=out['action'];i=out['energy_unit_index']
    assert out['nu_squared_action_evaluated']==pytest.approx(.42,rel=2e-15)
    step=1e-5
    def shifted(sign):
        e=dict(d);e['log_energy_unit_GeV']+=sign*step
        return intrinsic_higgs_gauge_action_jet(weights(),**e)['action']
    assert (shifted(1).value-shifted(-1).value)/(2*step)==pytest.approx(S.gradient[i],rel=2e-8)
    np.testing.assert_allclose((shifted(1).gradient-shifted(-1).gradient)/(2*step),S.hessian[:,i],rtol=2e-8,atol=1e-8)


def test_shared_potential_parameter_polynomial_is_exact_for_same_action_and_all_cross_blocks():
    d=data();out=intrinsic_higgs_gauge_action_jet(weights(),**d)
    a,b,c=out['nu_squared_polynomial_coefficients']
    for nu2 in (0.,.1,.37,2.):
        e=dict(d,nu_squared_action=nu2)
        actual=intrinsic_higgs_gauge_action_jet(weights(),**e)['action']
        reconstructed=a+nu2*b+nu2**2*c
        assert actual.value==pytest.approx(reconstructed.value,rel=3e-15,abs=1e-14)
        np.testing.assert_allclose(actual.gradient,reconstructed.gradient,rtol=5e-14,atol=1e-13)
        np.testing.assert_allclose(actual.hessian,reconstructed.hessian,rtol=5e-14,atol=1e-13)


def test_off_shell_global_gauge_covariance_requires_second_action_cotangent():
    # One homogeneous doublet, all five independent gauge components,
    # and no ordinary derivatives. The full mechanical+independent
    # connection transforms; keeping its reference fixed requires the
    # corresponding inhomogeneous independent-field direction.
    d=data();d['scalar_value_map']=np.eye(4)[None];d['scalar_derivative_map']=np.zeros((1,4,4,4))
    d['gauge_trace_map']=np.eye(20).reshape(1,5,4,20);d['angular_quadrature']=np.ones(1)
    w=weights();rep=higgs_u2_real_representation();G=rep['real_generators']
    eta=np.array([.2,-.3,.1,.4]);E=np.einsum('a,aij->ij',eta,G)
    full=d['gauge_coefficients'].reshape(5,4).copy()
    for j in range(3):full[j+2,j]+=np.sqrt(8)*(w['mechanical_connection_lambda'].value-1)
    bracket=lambda a:np.r_[np.cross(a[:3],eta[:3])/np.sqrt(2),0.]
    v=np.zeros(26);z=np.zeros(26)
    v[2:6]=-E@d['scalar_coefficients'];z[2:6]=E@E@d['scalar_coefficients']
    v[6:]=np.array([bracket(a) for a in full]).ravel()
    z[6:]=np.array([bracket(bracket(a)) for a in full]).ravel()
    S=intrinsic_higgs_gauge_action_jet(w,**d)['action']
    assert abs(S.gradient@v)<2e-13
    assert abs(v@S.hessian@v+S.gradient@z)<3e-13
    assert abs(S.gradient@z)>.001


@pytest.mark.parametrize('bad',['complex','independent_derivative','double_volume','ambiguous_scale'])
def test_no_silent_real_projection_domain_or_unit_convention(bad):
    d=data()
    if bad=='complex':d['scalar_coefficients']=d['scalar_coefficients'].astype(complex)
    if bad=='independent_derivative':d['scalar_derivative_map']=np.zeros((2,4,4,3))
    if bad=='double_volume':d['angular_quadrature']*=2*np.pi**2
    if bad=='ambiguous_scale':d['nu_squared_GeV_squared']=.3
    with pytest.raises(ValueError):intrinsic_higgs_gauge_action_jet(weights(),**d)
