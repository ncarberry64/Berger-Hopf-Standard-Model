"""Action derivatives and actual off-shell Ward pairing, without qdd inversion."""
import numpy as np
import pytest

from bhsm.interface.muon_birth_candidate_geometry_action import ROOT
from bhsm.interface.muon_parent_retarded_hypercharge import SOURCE, WALL
from bhsm.interface.muon_parent_maxwell_background_euler import (
    retained_connection_first_jet, background_weak_application,
    angular_ward_probe, off_shell_gauge_ward_application,
    evaluate_retained_background, _bracket,
)
from bhsm.interface.muon_matched_mechanical_source import epsilon


def test_actual_connection_rates_are_not_frozen_and_match_owned_profile_derivatives():
    rho=np.linspace(.15,WALL-.15,17);eps=1e-6
    data=retained_connection_first_jet(rho)
    plus=retained_connection_first_jet(rho+eps)['connection_lambda']
    minus=retained_connection_first_jet(rho-eps)['connection_lambda']
    np.testing.assert_allclose(data['lambda_rho'],(plus-minus)/(2*eps),atol=2e-9,rtol=1e-8)
    assert np.max(abs(data['lambda_tau'])) > .01
    assert not data['second_time_derivative_assigned']


def test_background_weak_row_is_the_nonlinear_action_derivative_with_all_shift_terms():
    rho=np.linspace(.1,WALL-.1,21);data=retained_connection_first_jet(rho)
    w=np.full(len(rho),.03);h=np.sin(2*rho);hr=2*np.cos(2*rho);ht=.2*np.cos(rho)
    applied=background_weak_application(data,w,h,hr,ht)
    e,r,d,b,l,lt,lr=(data[k] for k in ('electric','radial','angular','shift',
        'connection_lambda','lambda_tau','lambda_rho'))
    def action(s):
        v,vt,vr=l+s*h,lt+s*ht,lr+s*hr
        return np.sum(w*(12*e*(vt-b*vr)**2-12*r*vr**2-48*d*v*v*(v-1)**2))
    eps=2e-6
    assert applied['weak_Euler'][0] == pytest.approx((action(eps)-action(-eps))/(2*eps),rel=2e-9)
    np.testing.assert_allclose(applied['temporal_momentum_density'],24*e*(lt-b*lr))
    np.testing.assert_allclose(applied['radial_momentum_density'],-24*(e*b*(lt-b*lr)+r*lr))
    np.testing.assert_allclose(applied['background_generator_Gram'],8*np.eye(3))
    np.testing.assert_allclose(applied['mechanical_component_normalized_weak_Euler'],applied['weak_Euler']/8)
    assert 'final plus, initial minus' in applied['temporal_contact']
    assert 'wall plus, pole minus' in applied['radial_contact']
    assert not applied['contacts_already_appended_to_derivative_form']


def test_internal_bracket_normalization_matches_actual_saved_rank16_basis():
    with np.load(ROOT/SOURCE,allow_pickle=False) as z:
        H=np.array(z['unit_trace_carrier_basis'])
    np.testing.assert_allclose(H[0]@H[1]-H[1]@H[0],H[2]/np.sqrt(2),atol=1e-15)
    np.testing.assert_allclose(H[3]@H[0]-H[0]@H[3],0,atol=1e-15)
    a=np.array([.2,-.4,.8,.7]);b=np.array([.3,.9,-.1,-.2])
    A=np.einsum('i,ijk->jk',a,H);B=np.einsum('i,ijk->jk',b,H)
    np.testing.assert_allclose(A@B-B@A,np.einsum('i,ijk->jk',_bracket(a,b),H),atol=1e-15)


def test_actual_off_shell_euler_term_and_curvature_contact_are_nonzero_and_cancel_ward():
    result=evaluate_retained_background()
    ward=result['Ward']
    assert np.linalg.norm(ward['background_Euler_commutator']) > 1e4
    assert np.linalg.norm(ward['curvature_Hessian_contact']) > 1e3
    assert np.max(abs(ward['Ward_pairing'])) < 1e-9
    assert ward['Ward_relative_density_defect'] < 2e-14
    np.testing.assert_allclose(ward['hessian_on_gauge_tangent'],
        -ward['background_Euler_commutator'],atol=1e-9)
    assert result['weak']['strong_point_Euler_at_singular_birth'] is None
    assert not result['primal_acceleration_evaluated']
    assert not result['native_Pauli_evaluated']


def test_full_gauge_tangent_hessian_matches_independent_mixed_action_difference():
    rho=np.array([.42,.81,1.22]);data=retained_connection_first_jet(rho)
    weights=np.array([.2,.3,.4]);probe=angular_ward_probe()
    with np.load(ROOT/SOURCE,allow_pickle=False) as z:
        coeff=np.array(z['original_n1'][1:2])
    value=probe['evaluate'](coeff).transpose(0,3,1,2)
    Evalue=np.array([probe['evaluate'](probe['derivative'](coeff,i)).transpose(0,3,1,2)
                     for i in range(3)]).transpose(1,2,0,3,4)
    a=np.broadcast_to(.4*value[None],(3,1,8,3,4));at=.3*a;ar=-.2*a
    Ea=np.broadcast_to(.4*Evalue[None],(3,1,8,3,3,4))
    result=off_shell_gauge_ward_application(data,weights,a,at,ar,Ea,probe)
    internal=np.column_stack((np.eye(3),np.zeros(3)))
    expand=lambda x:x[:,None,None,None,None]
    A=np.sqrt(8)*expand(data['connection_lambda']-1)*internal
    At=np.sqrt(8)*expand(data['lambda_tau'])*internal
    Ar=np.sqrt(8)*expand(data['lambda_rho'])*internal
    EA=np.zeros((3,1,8,3,3,4),complex)
    eta=probe['eta'][None,None,:,None,:];etaE=probe['eta_angular'][None,None]
    z=etaE+_bracket(A,eta);zt=_bracket(At,eta);zr=_bracket(Ar,eta)
    Ez=probe['eta_second'][None,None]+_bracket(A[...,None,:,:],etaE[..., :,None,:])
    eps=epsilon()
    def action(s,t):
        X=A+s*a+t*z;Xt=At+s*at+t*zt;Xr=Ar+s*ar+t*zr;EX=EA+s*Ea+t*Ez
        B=2*X.copy()
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    B[...,i,:] += eps[i,j,k]*(EX[...,j,k,:]+.5*_bracket(X[...,j,:],X[...,k,:]))
        square=lambda x:np.sum(abs(x)**2,axis=(-1,-2))
        v=.5*(data['electric'][:,None,None]*square(Xt-expand(data['shift'])*Xr)
              -data['radial'][:,None,None]*square(Xr)-data['angular'][:,None,None]*square(B))
        return np.einsum('r,p,rAp->A',weights,probe['Haar_weights'],v)[0]
    step=2e-4
    mixed=(action(step,step)-action(step,-step)-action(-step,step)+action(-step,-step))/(4*step*step)
    assert result['hessian_on_gauge_tangent'][0] == pytest.approx(mixed,rel=1e-7,abs=3e-3)
    assert np.max(abs(result['Ward_pairing'])) < 2e-9
