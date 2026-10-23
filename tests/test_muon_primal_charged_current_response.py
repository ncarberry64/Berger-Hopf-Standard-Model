"""Exact current algebra and actual-source checks; no primal Newton rerun."""
import numpy as np
import pytest
from fractions import Fraction
import sympy as sp
from bhsm.interface.muon_primal_charged_current_response import (
    charged_current_matrices,charged_current_action_source,central_gauge_profile_coefficients,
    source_midpoint_rows,exact_stored_bordered_pairing,
)
from bhsm.interface.muon_parent_gauge_geometry_correction import ROOT,correction_representation
from bhsm.interface.muon_primal_intrinsic_lepton_operator import primal_intrinsic_lepton_operator
from bhsm.interface.muon_parent_retarded_hypercharge import WALL,regular_radial_basis
from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation


def test_whole_charged_current_basis_and_raising_normalization():
    X=charged_current_matrices()
    np.testing.assert_allclose(np.einsum('aij,bji->ab',X,X),np.eye(8),atol=7e-16,rtol=0)
    np.testing.assert_array_equal(X,X.conj().transpose(0,2,1))
    np.testing.assert_array_equal(X[:,12:],0)
    expected=np.zeros((18,18),complex)
    expected[2:4,8:10]=np.eye(2)/np.sqrt(2)
    np.testing.assert_allclose((X[0]+1j*X[4])/np.sqrt(2),expected,atol=2e-16,rtol=0)
    generators=lepton_unit_trace_gauge_representation()['generators']
    # Same-doublet hypercharges imply neutrality of all8 bilinears. The
    # charged source is not made compatible by deleting Gauss rows.
    np.testing.assert_array_equal(generators[3]@X-X@generators[3],0)


def test_analytic_central_profiles_are_in_same_At_and_Ar_spaces():
    p=central_gauge_profile_coefficients();rho=np.array([.16,.48,.91,1.22]);h=1e-6
    B,_=regular_radial_basis(rho,2);Bp,_=regular_radial_basis(rho+h,2);Bm,_=regular_radial_basis(rho-h,2)
    numerical=(Bp@p['theta_coefficients']-Bm@p['theta_coefficients'])/(2*h)
    np.testing.assert_allclose(B@p['radial_derivative_coefficients'],numerical,atol=3e-10,rtol=1e-9)
    assert p['profile_reconstruction_absolute_error']<2e-12


def test_midpoint_source_signs_are_from_action_variation():
    b=np.arange(216*2,dtype=float).reshape(216,2);h=-.125;r=source_midpoint_rows(b,h)
    np.testing.assert_array_equal(r[:90],0)
    np.testing.assert_array_equal(r[90:180],.125*b[:90])
    np.testing.assert_array_equal(r[180:270],b[90:180])
    np.testing.assert_array_equal(r[270:],b[180:])
    with pytest.raises(ValueError):source_midpoint_rows(b,0)


def test_exact_stored_nonsymmetric_system_adjoint_and_export_errors_CONTROL_ONLY():
    K=np.array([[2.,1.,0.],[0.,3.,1.],[1.,0.,2.]])
    f=np.array([[1.,2.],[3.,-1.],[2.,4.]]);L=np.array([[1.,2.,3.],[0.,-1.,2.]])
    result=exact_stored_bordered_pairing(K,f,L)
    target=sp.Matrix(L.astype(int))*(sp.Matrix(K.astype(int)).inv()*sp.Matrix(f.astype(int)))
    assert result['source_adjoint_intervals_overlap']
    for i in range(2):
        for j in range(2):
            rational=Fraction(int(sp.numer(target[i,j])),int(sp.denom(target[i,j])))
            assert Fraction.from_float(result['paired_current_lower'][i,j])<=rational
            assert Fraction.from_float(result['paired_current_upper'][i,j])>=rational
    assert result['exact_stored_bordered_residual_upper']<1e-50
    assert result['exact_stored_source_adjoint_difference_upper']<1e-50
    assert not result['physical_action_or_current_source_formation_error_enclosed']
    assert np.all(result['response_export_error_upper']>=0)
    with pytest.raises(ValueError):exact_stored_bordered_pairing(K,f,L,precision_bits=64)


@pytest.fixture(scope='module')
def actual():
    with np.load(ROOT/'artifacts/muon_parent_gauge_geometry_correction_20261010/full_midpoint_outgoing_run_1/application.npz',allow_pickle=False) as a:
        raw=a['updated_midpoint_raw'].copy()
    rep=correction_representation(radial_points=48,cap_points=48,radial_order=2,include_wall_lift=True,include_scalar_mean=True)
    return raw,rep,charged_current_action_source(raw,rep)


@pytest.mark.parametrize('index',[0,74,98,100,122,142])
def test_actual_charged_source_is_derivative_of_literal_coordinate_time_action(actual,index):
    raw,rep,a=actual;step=2e-6;plus=raw.copy();minus=raw.copy();plus[index]+=step;minus[index]-=step
    p=primal_intrinsic_lepton_operator(plus,rep);m=primal_intrinsic_lepton_operator(minus,rep)
    delta=(-p['N']*p['H_can']+m['N']*m['H_can'])/(2*step)
    expected=np.einsum('aij,ji->a',a['current_matrices'],delta).real
    np.testing.assert_allclose(a['raw_source'][index],expected,atol=2e-9,rtol=5e-6)


def test_family_identity_and_no_lsz_or_zero_weak_formula_promotion(actual):
    raw,rep,a=actual;b=charged_current_action_source(raw,rep,family=2)
    np.testing.assert_array_equal(a['raw_source'],b['raw_source'])
    np.testing.assert_array_equal(a['raw_source'][160:220],0)
    np.testing.assert_array_equal(a['raw_source'][220:228],0)
    assert np.linalg.norm(a['raw_source'])>0
    assert not a['constant_angular_Haar_volume_reapplied']
    assert not a['physical_external_state_selected']
