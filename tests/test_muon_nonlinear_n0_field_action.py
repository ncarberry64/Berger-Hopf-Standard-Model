import numpy as np
from bhsm.interface.muon_nonlinear_n0_field_action import (
    analytic_constant_maxwell_jet,analytic_intrinsic_n0_jet,nonlinear_source_directed_newton,
)
from bhsm.interface.muon_local_wick_action import local_field_chart,local_analytic_action_jet
from bhsm.interface.muon_parent_maxwell_corrected_retarded import full_constant_angular_hessian


def data_and_images(count):
    shapes=local_field_chart()['shapes']
    return {k:np.zeros(s,complex)for k,s in shapes.items()},{k:np.zeros((count,)+s,complex)for k,s in shapes.items()}


def test_complex_quartic_maxwell_contacts_equal_independent_literal_action_jets():
    rng=np.random.default_rng(963);r=lambda s:rng.normal(size=s)+.2j*rng.normal(size=s)
    A,At,Ar=[r((5,4))for _ in range(3)];c=np.array([2,3,4,5,.13])+.02j
    data,im=data_and_images(60)
    data.update(A=A,A_time=At,A_radial=Ar,densities=c)
    for k,key in enumerate(('A','A_time','A_radial')):im[key][20*k:20*k+20]=np.eye(20).reshape(20,5,4)
    ref=local_analytic_action_jet(data,im,lambda_H=.2,nu_squared_action=4,signature='lorentz')['maxwell']
    got=analytic_constant_maxwell_jet(A,At,Ar,c)
    for a,b in(('value','value'),('gradient','first'),('hessian','second')):
        np.testing.assert_allclose(got[a],ref[b],rtol=4e-14,atol=2e-13)
    # Complex analytic transpose is consequential: a Hermitian replacement
    # would disagree on this retained real-coefficient continuation.
    assert np.linalg.norm(got['hessian'].imag)>1


def test_n0_real_hessian_restricts_original_full_owned_angular_tensor():
    rng=np.random.default_rng(47);A,At,Ar=[.1*rng.normal(size=(5,4))for _ in range(3)];c=[2,3,4,5,.17]
    ref=full_constant_angular_hessian(A,At,Ar,c)['tensor'][:,:,0,0].transpose(0,2,1,3).reshape(60,60)
    got=analytic_constant_maxwell_jet(A,At,Ar,c)
    np.testing.assert_allclose(got['hessian'],ref,rtol=3e-14,atol=5e-14)


def test_intrinsic_nonlinear_realified_gradient_and_hessian_match_independent_action():
    rng=np.random.default_rng(812);r=lambda s:rng.normal(size=s)+.05j*rng.normal(size=s)
    A,h,hd,w=r((5,4)),r((4,)),r((4,)),np.array([2,3,4])+.03j
    data,im=data_and_images(28);data.update(A=A,H=h,H_derivative=np.r_[hd[None],np.zeros((3,4))],weights=w)
    im['H'][:4]=np.eye(4);im['A'][4:24]=np.eye(20).reshape(20,5,4);im['H_derivative'][24:,0]=np.eye(4)
    ref=local_analytic_action_jet(data,im,lambda_H=.19,nu_squared_action=4,signature='lorentz')['higgs']
    got=analytic_intrinsic_n0_jet(A,h,hd,w,lambda_H=.19,nu_squared_action=4)
    V=2*np.pi**2
    np.testing.assert_allclose(got['value'],ref['value']/V,rtol=3e-14,atol=3e-14)
    np.testing.assert_allclose(got['gradient'],ref['first']/V,rtol=3e-14,atol=3e-14)
    np.testing.assert_allclose(got['hessian'],ref['second']/V,rtol=3e-14,atol=3e-14)


def test_nonlinear_source_is_reassembled_and_frame_reaction_not_deleted():
    calls=[]
    def classical(x):
        return dict(value=(x@x)/2+np.sum(x**4)/4,gradient=x+x**3,hessian=np.eye(2)+np.diag(3*x*x))
    def native(x):
        calls.append(x.copy());return np.array([.2*np.exp(x[0]),.3+2*x[1]])
    a=nonlinear_source_directed_newton(classical,native,np.zeros(2),np.array([[0.,1.]]),
        native_hessian=lambda x:np.diag([.2*np.exp(x[0]),2]),tolerance=1e-11)
    assert a['status']=='REPRESENTED_NONLINEAR_FIELD_TOLERANCE'
    assert abs(a['coefficients'][1])<1e-15
    assert abs(a['frame_reaction'][0]+.3)<1e-12
    assert np.linalg.norm(a['residual'])<1e-11
    assert any(abs(x[0])>.1 for x in calls)
    # A frozen source would solve another equation, even on this simple
    # represented chart; the actual callback must see each candidate.
    x=a['coefficients'][0]
    assert abs(x+x**3+.2)>.01
