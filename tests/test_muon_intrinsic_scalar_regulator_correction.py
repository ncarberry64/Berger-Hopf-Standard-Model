"""Independent kernel, source derivative and literal action-reduction checks."""
from fractions import Fraction
import numpy as np
import pytest
from scipy.linalg import expm
from bhsm.interface.muon_common_cutoff_green_kernel import common_total_cutoff_green_kernel
from bhsm.interface.muon_intrinsic_scalar_regulator_correction import (
    scalar_reduced_kernel,two_green_regulator_correction,
    scalar_regulator_source_application,intrinsic_scalar_gaussian_embedding_contract,
)
from bhsm.interface.muon_magnetic_mixed_green import mixed_green_spectral_derivative
from test_muon_magnetic_mixed_green import control


def test_positive_missing_proper_time_region_and_coincident_limit():
    p=np.array([1000.,1001.,999.]);q=1000.;c=.001
    correction=two_green_regulator_correction(p,q,c)
    full=common_total_cutoff_green_kernel(p,q,cutoff=c,terms=8)
    np.testing.assert_allclose(scalar_reduced_kernel(p,q,c)+correction,
        full['value'],rtol=8*np.finfo(float).eps,atol=0)
    assert np.all(correction>0)
    assert correction[0]==c*np.exp(-c*q)/q
    np.testing.assert_array_equal(two_green_regulator_correction(p,q,0),np.zeros(3))
    for bad in (None,-1,1j):
        with pytest.raises(ValueError):two_green_regulator_correction(p,q,bad)


def test_correction_reconstructs_both_open_placements_and_every_contact():
    d,s=control();c=.001
    r=scalar_regulator_source_application(d,s,c,series_terms=8)
    original=mixed_green_spectral_derivative(d,s,c,series_terms=8)
    for place in ('forward','reverse'):
        for name,value in original[place].items():
            actual=r['scalar_first_reduction'][place][name]+r['finite_cutoff_correction'][place][name]
            np.testing.assert_allclose(actual,value,rtol=2e-14,atol=1e-22)
    assert np.linalg.norm(r['finite_cutoff_correction']['forward']['total'])>0
    assert not r['scalar_Schur_graph_promoted_to_Gamma']


def reduced_original_expression(d,s,source,epsilon,c):
    # CONTROL_ONLY: direct finite nonnormal Gaussian Schur expression.
    A=np.zeros((5,5),complex);A[:2,:2]=d['A_odd'];A[2:,2:]=d['A_even']
    A[2:,:2]=epsilon*d['Xi_even_odd'][source]
    A[:2,2:]=epsilon*d['Xi_reverse_dagger_even_odd'][source].conj().T
    GF=np.linalg.solve(1000*np.eye(5)+A.conj().T@A,A.conj().T)
    H=np.zeros((5,5));H[:2,:2]=s['positive_H_odd'];H[2:,2:]=s['positive_H_even']
    H[2:,:2]=epsilon*s['delta_positive_H_even_odd'][source];H[:2,2:]=H[2:,:2].T
    GH=np.linalg.solve(H,expm(-c*H))/s['action_Gram_scalar']
    B=np.zeros((5,5,3),complex);B[:2,:2,:1]=d['mixed_vertex_n0_odd']
    B[:2,2:,1:]=d['mixed_vertex_n1_Hodd'];B[2:,:2,1:]=d['mixed_vertex_n1_Heven']
    return np.einsum('aiu,ij,bjv,ab->uv',B.conj(),GF,B,GH)


def test_scalar_first_source_derivative_matches_original_action_expression():
    d,s=control();c=.001;h=2e-5
    r=scalar_regulator_source_application(d,s,c,series_terms=8)['scalar_first_reduction']
    for a in range(3):
        derivative=(reduced_original_expression(d,s,a,h,c)-reduced_original_expression(d,s,a,-h,c))/(2*h)
        np.testing.assert_allclose(r['forward']['total'][a],derivative[1:,:1],rtol=2e-8,atol=1e-17)
        np.testing.assert_allclose(r['reverse']['total'][a],derivative[:1,1:],rtol=2e-8,atol=1e-17)


def test_exact_temporal_product_complement_and_signed_gaussian_completion():
    import sympy as sp
    # A triangular tent has integral b^k=L/(k+1). This is an exact
    # complement calculation, not a proposed physical temporal state.
    norm=Fraction(1,5)-Fraction(1,4)**2/Fraction(1,3)
    assert norm==Fraction(1,80) and norm/Fraction(1,5)==Fraction(1,16)
    a,v,h,eta,bar_eta,psi,bar_psi=sp.symbols('a v h eta bar_eta psi bar_psi')
    original=bar_eta*a*eta+bar_eta*v*psi*h+bar_psi*v*eta*h
    completed=(bar_eta+bar_psi*v*h/a)*a*(eta+v*psi*h/a)-bar_psi*v**2*h**2*psi/a
    assert sp.expand(original-completed)==0
    contract=intrinsic_scalar_gaussian_embedding_contract()
    assert contract['gaussian_open_exchange_statistics_coefficient']==-1
    assert not contract['finite_cutoff_Schur_equivalence']
