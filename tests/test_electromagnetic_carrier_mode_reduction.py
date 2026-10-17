"""Independent controls; their guard is not the physical outgoing guard."""
import itertools

import numpy as np
import pytest
from scipy.linalg import expm

from bhsm.interface.electromagnetic_carrier_mode_reduction import (
    carrier_map_jet, exact_checks, nonlinear_action_pullback, numerical_checks,
    right_frame_s3_modes, round_mode_residual, s3_mode_generators,
)


def test_supplied_exact_groups():
    result=exact_checks()
    assert result['all_passed'] and result['group_count']==10


def test_supplied_numerical_groups():
    result=numerical_checks()
    assert result['all_passed'] and result['group_count']==3


def test_map_complete_jet_against_independent_differences():
    x=np.array([0.73,0.39]); b=1.6; r=0.81; h=1e-4
    f=lambda y: np.sqrt(b)*np.array([y[0]*np.cos(y[1]),y[0]*np.sin(y[1]),r*np.cos(y[1]),r*np.sin(y[1])])
    jet=carrier_map_jet(*x,b=b,r=r)
    eye=np.eye(2)
    fd=np.column_stack([(f(x+h*e)-f(x-h*e))/(2*h) for e in eye])
    assert np.max(np.abs(fd-jet['DR']))<4e-9
    for i in range(2):
        for j in range(2):
            second=(f(x+h*eye[i]+h*eye[j])-f(x+h*eye[i]-h*eye[j])-f(x-h*eye[i]+h*eye[j])+f(x-h*eye[i]-h*eye[j]))/(4*h*h)
            np.testing.assert_allclose(second,jet['D2R'][:,i,j],atol=2e-8,rtol=0)
    np.testing.assert_allclose(jet['tangent_projector']+jet['normal_projector'],np.eye(4),atol=4e-16)


def test_tangent_and_conservation_do_not_admit_full_equations():
    result=round_mode_residual(1,0,1/3,1/2,-3/4,-1/6,b=1,r=1,omega=1)
    np.testing.assert_allclose(result['tangent_covector'],0,atol=1e-16)
    assert np.dot(result['original'],result['original'])==pytest.approx(89/144)
    assert np.linalg.norm(result['normal'])>0.78
    for sign in [-1,1]:
        result=round_mode_residual(0.8,0.3,0,sign*1.7,0,0,b=1.2,r=0.9,omega=1.7)
        np.testing.assert_allclose(result['original'],0,atol=8e-16)


def test_full_second_map_cancels_false_phase_stiffness():
    jet=carrier_map_jet(0.7,0.2,b=1.3,r=0.8)
    omega=1.9
    result=nonlinear_action_pullback(omega**2*jet['Q'],omega**2*np.eye(4),jet['DR'],jet['D2R'])
    assert result['naive'][1,1]>4
    assert abs(result['hessian'][1,1])<2e-15
    assert result['hessian'][0,0]==pytest.approx(1.3*omega**2)
    # Analytic left duals also work for genuinely complex amplitudes.
    c=1+2j
    complex_result=nonlinear_action_pullback(c*omega**2*jet['Q'],c*omega**2*np.eye(4),jet['DR'],jet['D2R'])
    np.testing.assert_allclose(complex_result['hessian'],c*result['hessian'],atol=1e-14)


def test_owned_right_frame_orientation_gram_and_ordered_derivatives():
    q=np.array(list(itertools.product([-0.5,0.5],repeat=4))+list(np.eye(4))+list(-np.eye(4)))
    value,d1,d2=right_frame_s3_modes(q)
    owned=np.array([[0,0,-1],[0,-1,0]])
    np.testing.assert_allclose(value[:,:2],np.broadcast_to(owned,(24,2,3)),atol=0)
    np.testing.assert_allclose(d1[:,:,:2],0,atol=0)
    np.testing.assert_allclose(np.einsum('pai,pbi->ab',value,value)/24,np.eye(4),atol=1e-16)
    eps=np.zeros((3,3,3))
    for i,j,k in itertools.permutations(range(3)):
        eps[i,j,k]=((i-j)*(j-k)*(k-i))/2
    curl=2*value+np.einsum('ijk,pjak->pai',eps,d1)
    np.testing.assert_allclose(curl,value*np.array([2,2,-2,-2])[None,:,None],atol=1e-15)
    # Package Hopf orientation has the opposite signs, although curl² agrees.
    assert np.max(np.abs(curl-value*np.array([-2,-2,2,2])[None,:,None]))==4
    for k in range(3):
        for j in range(3):
            np.testing.assert_allclose(d2[:,k,j]-d2[:,j,k],-2*np.einsum('l,plai->pai',eps[k,j],d1),atol=0)
    np.testing.assert_allclose(-np.einsum('pjjai->pai',d2)[:,:, :],value*np.array([0,0,8,8])[None,:,None],atol=0)
    # Independent ambient flow, not the same polynomial differentiation.
    generic=np.concatenate((s3_mode_generators()[:2],np.array([[[0,0,0,-1],[0,0,-1,0],[0,1,0,0],[1,0,0,0]]])))
    l=-generic[[2,1,0]]
    h=2e-5
    for j in range(3):
        plus=right_frame_s3_modes(q@expm(h*l[j]).T)[0]
        minus=right_frame_s3_modes(q@expm(-h*l[j]).T)[0]
        np.testing.assert_allclose((plus-minus)/(2*h),d1[:,j],atol=8e-10,rtol=0)


def test_chart_rejects_nonunit_points():
    with pytest.raises(ValueError,match='unit sphere'):
        right_frame_s3_modes([[1,1,0,0]])


def test_owned_scalar_harmonic_derivatives_agree_with_frame_adapter():
    from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization
    a=scalar_s3_discretization(2,quadrature_polynomial_degree=8)
    x,alpha,beta=a['hopf_points'].T
    q=np.column_stack((np.sqrt(x)*np.cos(alpha),np.sqrt(x)*np.sin(alpha),
                       np.sqrt(1-x)*np.cos(beta),np.sqrt(1-x)*np.sin(beta)))
    values,first,_=right_frame_s3_modes(q)
    y,ey=a['real_basis_values'],a['real_basis_derivative_values']
    coefficient=np.einsum('ph,p,pai->hai',y,a['haar_weights'],values)
    np.testing.assert_allclose(np.einsum('ph,hai->pai',y,coefficient),values,atol=8e-15,rtol=0)
    np.testing.assert_allclose(np.einsum('pjh,hai->pjai',ey,coefficient),first,atol=2e-14,rtol=0)
