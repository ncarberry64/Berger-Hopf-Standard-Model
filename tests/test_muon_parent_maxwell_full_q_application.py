"""Exact angular identities / actual-reference applications, no chosen primal."""
import numpy as np
import pytest

from bhsm.interface.muon_matched_mechanical_source import angular_blocks, apply
from bhsm.interface.muon_moving_geometric_action import retained_state
from bhsm.interface.muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
from bhsm.interface.muon_parent_maxwell_full_weak import full_maxwell_hessian_pairing, full_maxwell_gauge_hessian_matrix
from bhsm.interface.muon_parent_maxwell_full_q_application import (
    ROOT,SOURCE,retained_full_q_angular_space,full_q_reference_operators,
    hessian_response_polynomials,apply_full_q_hessian,geometric_response_factors,
    full_q_offshell_ward,retained_full_q_application)
from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization


@pytest.fixture(scope='module')
def actual():
    a=retained_full_q_angular_space(); o=full_q_reference_operators(a)
    q,v,m=retained_state(ROOT)
    c=geometric_connection_coefficient_jets(12,q,v,m,np.array([.61]),clock='coordinate_time')
    return a,o,c,q,v,m


def values(a,coefficients):
    """CONTROL_ONLY local firstjets are derived from supplied angular coefficients."""
    c=np.asarray(coefficients).reshape(5,4,20)
    return np.einsum('pn,fcn->pfc',a['basis_values'],c), np.einsum('pin,fcn->pifc',a['basis_derivative_values'],c)


def test_actual_raw_source_and_saved_normalized_gram_are_distinguished(actual):
    a,*_=actual
    np.testing.assert_allclose(a['source_gram'],(16/3)*np.eye(8),atol=5e-15)
    np.testing.assert_allclose((3/16)*a['source_gram'],a['saved_normalized_source_gram'],atol=3e-15)
    assert np.linalg.norm(a['source_coefficients'].reshape(5,4,20,8)[:,:,4:])>0
    assert a['physical_source_profile_selected'] is False
    assert a['nonlinear_truncation_invariant'] is False


def test_owned_real_frame_curl_agrees_with_retained_complex_source(actual):
    a,o,c,*_=actual
    lam=c['rows'][0]['connection_lambda'].value
    scalar=scalar_s3_discretization(3); U=scalar['real_basis_coefficient_transform']
    old=np.zeros((8,3,4,30),complex)
    with np.load(ROOT/SOURCE) as z:
        for n in (1,3):
            ids=[i for i,l in enumerate(scalar['scalar_labels']) if l[0]==n]
            C,T,*_=angular_blocks(n)
            old[:,:,:,ids]=apply(C+(lam-1)*T,z[f'transformed_n{n}']).reshape(8,3,4,-1)
    odd=[i for i,l in enumerate(scalar['real_basis_labels']) if l[0] in (1,3)]
    old=np.einsum('ji,Afcj->Afci',U.conj(),old)[:,:,:,odd].real.reshape(8,240).T
    new=(o['curl0']+(lam-1)*o['curl1'])@a['source_coefficients'][160:]
    np.testing.assert_allclose(new,old,atol=2e-15)


def test_full_shell_closure_includes_scalar_gauss_and_spectator_columns(actual):
    a,o,*_=actual
    n=np.array([x[0] for x in a['harmonic_labels']]); n400=np.tile(n,20)
    P=hessian_response_polynomials(o,np.eye(400))
    # Every scalarfactor polynomial preservesn, independent of a metricpoint.
    for data in P:
        for block in data:
            for matrix in block:
                assert np.max(abs(matrix[np.ix_(n400==1,n400==3)]))==0
                assert np.max(abs(matrix[np.ix_(n400==3,n400==1)]))==0
    assert np.linalg.norm(P[:,:,:,:160])>0
    assert np.linalg.norm(o['magnetic_contact'])>0


@pytest.mark.parametrize('left_jet,right_jet',[(i,j) for i in range(3) for j in range(3)])
def test_nine_jet_blocks_against_literal_full_action_with_gauss_contacts(actual,left_jet,right_jet):
    a,o,c,*_=actual
    # RetainedQ0 is the right direction; left combines actualQ3 and
    # scalarAt/Ar n3 directions to expose contacts lost by QQ compression.
    Q=a['source_coefficients']
    left=.3*Q[:,3].copy(); left[19]=.8; left[80+14]=-.4
    right=Q[:,0]
    l=[np.zeros(400) for _ in range(3)]; z=[np.zeros(400) for _ in range(3)]
    l[left_jet]=left; z[right_jet]=right
    lv=[values(a,x)[0][None] for x in l]; zv=[values(a,x)[0][None] for x in z]
    le=values(a,l[0])[1][None]; ze=values(a,z[0])[1][None]
    zero=np.zeros_like(lv[0]); ea=np.zeros_like(le)
    literal=full_maxwell_hessian_pairing(c,np.ones(1),a['Haar_weights'],
        gauge=zero,gauge_tau=zero,gauge_rho=zero,gauge_angular=ea,
        left=lv[0],left_tau=lv[1],left_rho=lv[2],left_angular=le,
        right=zv[0],right_tau=zv[1],right_rho=zv[2],right_angular=ze,
        geometric_derivatives=False)
    response=apply_full_q_hessian(c['rows'][0],hessian_response_polynomials(o,right[:,None]))
    expected=left@response[left_jet,right_jet,:,0]
    assert literal['value']==pytest.approx(expected,rel=3e-12,abs=3e-10)


def test_mixed_scalar_and_spatial_matrix_against_literal_batch(actual):
    a,o,c,*_=actual
    Q=a['source_coefficients']
    V=np.column_stack((Q[:,:4],np.eye(400)[:,[2,14,80+2,80+14]]))
    jets=(V,.37*V,-.21*V)
    v=np.stack([values(a,x)[0] for x in V.T])[None]
    ea=np.stack([values(a,x)[1] for x in V.T])[None]
    zero=np.zeros((1,len(a['Haar_weights']),5,4)); ez=np.zeros((1,len(a['Haar_weights']),3,5,4))
    literal=full_maxwell_gauge_hessian_matrix(c,np.ones(1),a['Haar_weights'],
        gauge=zero,gauge_tau=zero,gauge_rho=zero,gauge_angular=ez,
        tests=v,tests_tau=.37*v,tests_rho=-.21*v,tests_angular=ea)
    R=apply_full_q_hessian(c['rows'][0],hessian_response_polynomials(o,V))
    expected=np.einsum('ica,ijcb,j->ab',np.array(jets),R,np.array([1.,.37,-.21]))
    np.testing.assert_allclose(literal['matrix'],expected,rtol=3e-12,atol=5e-10)
    assert np.linalg.norm(literal['curvature_contact_matrix'])>0


def test_all_sources_all_gauge_harmonics_offshell_ward_requires_euler_contact(actual):
    a,o,c,*_=actual
    W=full_q_offshell_ward(a,o,c['rows'][0])
    assert W['hessian'].shape==(8,80)
    assert np.max(abs(W['Euler_contact']))>1
    np.testing.assert_allclose(W['hessian'],-W['Euler_contact'],rtol=3e-12,atol=3e-10)
    assert W['Gauss_columns_included'] is True
    assert W['reference_stationarity_assumed'] is False


def test_geometry_normal_jet_of_whole_gauss_source_image_matches_owner_shifted_action(actual):
    a,o,c,q,v,m=actual
    P=hessian_response_polynomials(o,a['source_coefficients'])
    factors=geometric_response_factors(c['rows'][0])
    analytic=np.einsum('f,fijca->ijca',np.array([x.gradient[-2] for x in factors]),P)
    h=2e-6
    def shifted(s):
        cc=geometric_connection_coefficient_jets(12,q,v,m,np.array([.61]),source_value=s,clock='coordinate_time')
        return apply_full_q_hessian(cc['rows'][0],P)
    numeric=(shifted(h)-shifted(-h))/(2*h)
    np.testing.assert_allclose(analytic,numeric,rtol=3e-8,atol=2e-5)
    assert np.linalg.norm(analytic[:,:,:160])>0


def test_actual_source_image_requires_full400_not_eight_source_solve():
    r=retained_full_q_application(points=4)
    assert r['eight_source_closure_absolute']>1e3
    assert np.linalg.norm(r['Gauss_source_image'])>1e3
    assert r['full400_cross_shell_derivative_max']==0
    assert r['physical_radial_source_profile'] is None
    assert r['physical_retarded_solution'] is None
    assert r['physical_current_Pauli_form'] is None
    assert r['stationary_E1_claim'] is False


@pytest.mark.parametrize('bad',[np.zeros(400),np.zeros((399,1)),np.full((400,1),np.nan),np.ones((400,1))*1j])
def test_no_invalid_direction_projection(actual,bad):
    with pytest.raises(ValueError,match='finite real full400'):
        hessian_response_polynomials(actual[1],bad)
