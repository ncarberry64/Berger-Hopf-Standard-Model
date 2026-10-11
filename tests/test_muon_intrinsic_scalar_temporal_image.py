"""Exact source closure, weak kinetic images and independent Green checks."""
from fractions import Fraction
import numpy as np
import pytest
from scipy.linalg import block_diag
from bhsm.interface.muon_intrinsic_scalar_temporal_image import (
    temporal_yukawa_source_image,temporal_image_green_kernel,temporal_image_source_application,
)
from test_muon_magnetic_mixed_green import control


def test_exact_temporal_source_image_and_kinetic_pairing():
    import sympy as sp
    x=sp.symbols('x',real=True);b=2*x
    # Each branch of the tent contributes the same reflection-even integral.
    integral=lambda f:2*sp.integrate(f,(x,0,sp.Rational(1,2)))
    phi=[b,b*b];M=sp.Matrix(2,2,lambda i,j:integral(phi[i]*phi[j]))
    D=sp.Matrix(2,2,lambda i,j:integral(sp.diff(phi[i],x)*sp.diff(phi[j],x)))
    T=sp.Matrix([integral(b*b*p) for p in phi])
    assert M.inv()*T==sp.Matrix([0,1])
    assert 3*(T.T*M.inv()*T)[0]==sp.Rational(3,5)
    assert (sp.Rational(3,5)-sp.Rational(9,16))/sp.Rational(3,5)==sp.Rational(1,16)
    r=temporal_yukawa_source_image()
    np.testing.assert_allclose(r['Gram'],np.array(M,float),rtol=0,atol=0)
    np.testing.assert_allclose(r['derivative_Gram'],np.array(D,float),rtol=0,atol=0)
    U=r['temporal_eigenvectors']
    np.testing.assert_allclose(U.T@r['Gram']@U,np.eye(2),rtol=0,atol=2e-14)
    np.testing.assert_allclose(sum(r['normalized_vertex_coefficients']**2),.6,rtol=2e-14)
    assert not r['differential_image_orthogonality_is_full_domain_closure']
    assert not r['source_norm_fraction_is_Pauli_error']


def test_wide_common_cutoff_kernels_and_positive_close_pair_remainder():
    import mpmath as mp
    with mp.workdps(70):
        p,q,c=mp.mpf(100),mp.mpf(11),mp.mpf('.003')
        g=lambda z:mp.exp(-c*z)/z
        two=-(g(q)-g(p))/(q-p)
        r=temporal_image_green_kernel(100.,11.,cutoff=.003)
        np.testing.assert_allclose(r['value'],float(two),rtol=3e-15)
        p1=mp.mpf('100.4')
        exact=((g(q)-g(p1))/(q-p1)-(g(p1)-g(p))/(p1-p))/(q-p)
        r=temporal_image_green_kernel(100.,100.4,11.,cutoff=.003)
        assert abs(mp.mpf(float(r['value']))-exact)<r['kernel_approximation_upper']
        assert r['kernel_approximation_upper']>0
        assert 'outward' in r['method']


def original_enlarged_expression(d,s,source,epsilon,*,length,lapse):
    # CONTROL_ONLY original ten-dimensional nonnormal factor form, with
    # exact source image in two temporal branches and the original scalar
    # starting trial; no physical packet is inferred from this control.
    t=temporal_yukawa_source_image();blocks=[];Bs=[]
    for k,v in zip(t['temporal_eigenvalues'],t['normalized_vertex_coefficients']):
        A=np.zeros((5,5),complex);A[:2,:2]=d['A_odd'];A[2:,2:]=d['A_even']
        A[2:,:2]=epsilon*d['Xi_even_odd'][source]
        A[:2,2:]=epsilon*d['Xi_reverse_dagger_even_odd'][source].conj().T
        P=(1000+(k-12)/(lapse*length)**2)*np.eye(5)+A.conj().T@A
        blocks.append(np.linalg.solve(P,A.conj().T))
        B=np.zeros((5,5,3),complex)
        B[:2,:2,:1]=d['mixed_vertex_n0_odd'];B[:2,2:,1:]=d['mixed_vertex_n1_Hodd'];B[2:,:2,1:]=d['mixed_vertex_n1_Heven']
        Bs.append(B*v/.75)
    GF=block_diag(*blocks);B=np.concatenate(Bs,axis=1)
    H=np.zeros((5,5));H[:2,:2]=s['positive_H_odd'];H[2:,2:]=s['positive_H_even']
    H[2:,:2]=epsilon*s['delta_positive_H_even_odd'][source];H[:2,2:]=H[2:,:2].T
    GH=np.linalg.inv(H)/s['action_Gram_scalar']
    return np.einsum('aiu,ij,bjv,ab->uv',B.conj(),GF,B,GH)


def test_source_derivative_matches_original_enlarged_action_green():
    d,s=control();r=temporal_image_source_application(d,s,length=1.,lapse=1.,cutoff=0)
    h=2e-5
    for source in range(3):
        p=original_enlarged_expression(d,s,source,h,length=1.,lapse=1.)
        m=original_enlarged_expression(d,s,source,-h,length=1.,lapse=1.)
        exact=(p-m)/(2*h)
        np.testing.assert_allclose(r['forward']['total'][source],exact[1:,:1],rtol=3e-8,atol=2e-17)
        np.testing.assert_allclose(r['reverse']['total'][source],exact[:1,1:],rtol=3e-8,atol=2e-17)
    assert r['internal_fermion_source_image_b_squared_exact']
    assert not r['original_scalar_trial_enlarged']
    assert not r['source_first_order_differential_complement_removed']


def test_nonzero_cutoff_keeps_each_contact_and_all_temporal_branches():
    d,s=control();r=temporal_image_source_application(d,s,length=1.,lapse=1.,cutoff=.001)
    assert len(r['branches'])==2
    for place in ('forward','reverse'):
        assert np.linalg.norm(r[place]['fermion_numerator_contact'])>0
        assert np.linalg.norm(r[place]['scalar_propagator_insertion'])>0
        np.testing.assert_allclose(r[place]['total'],sum(b[place]['total'] for b in r['branches']),rtol=0,atol=0)
    assert not r['complete_adopted_P_strat_derived']


def test_missing_negative_complex_inputs_cannot_select_or_default():
    d,s=control()
    for bad in (None,-1,1j):
        with pytest.raises(ValueError):temporal_image_source_application(d,s,length=1.,lapse=1.,cutoff=bad)
        with pytest.raises(ValueError):temporal_image_source_application(d,s,length=bad,lapse=1.,cutoff=0)
    with pytest.raises(ValueError):temporal_image_green_kernel(1.,3.,8.,cutoff=.1)
