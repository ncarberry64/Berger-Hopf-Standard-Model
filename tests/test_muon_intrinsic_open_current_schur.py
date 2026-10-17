from pathlib import Path
import numpy as np
import pytest

from bhsm.interface.muon_intrinsic_open_current_schur import (
    external_current_schur_application,source_image_external_current_application,
)


def test_neutral_rhs_and_schur_return_match_complete_nonnormal_solve():
    A=np.array([[1+1j,2,0],[0,3-2j,1],[1j,0,2]],complex)
    P=7*np.eye(3)+A.conj().T@A
    J=np.eye(3)[:,:2];K=np.eye(3)[:,2:]
    r=external_current_schur_application(A,P,J,K)
    np.testing.assert_allclose(r['charged_source_response'],np.linalg.solve(P,A.conj().T@J),rtol=2e-15,atol=2e-16)
    assert np.linalg.norm(r['neutral_right_hand_side'])>0
    assert np.linalg.norm(r['complete_response_difference_from_isolated'])>.01
    assert np.linalg.norm(r['Schur_full_solve_difference'])<3e-16


def test_actual_same_background_open_image_retains_all_neutral_placements():
    root=Path(__file__).resolve().parents[1]
    p=root/'artifacts/muon_magnetic_mixed_green_20261011/run_3'
    with np.load(p/'incoming_family_1_fermion_operators.npz') as f:
        data={k.removeprefix('incoming_family_1_'):f[k] for k in f.files}
    with np.load(p/'scalar_sources.npz') as f:H=f['incoming_raw_fields'][-8:-4];H=H[:2]+1j*H[2:]
    with np.load(root/'artifacts/muon_intrinsic_scalar_temporal_image_20261011/run_1/application.npz') as f:
        forward=f['incoming_family_1_forward_total'];reverse=f['incoming_family_1_reverse_total']
    r=source_image_external_current_application(data,forward,reverse,H,family=1)
    assert r['external_n0']['positive_form_minimum_eigenvalue']>1e10
    for k in ('external_n0','external_n1'):
        assert np.linalg.norm(r[k]['Schur_full_solve_difference'])/np.linalg.norm(r[k]['charged_source_response'])<2e-15
        assert np.linalg.norm(r[k]['neutral_factor_source_leakage'])>0
    assert np.linalg.norm(r['forward_charged_neutral_placements']['neutral_image_charged_source'])>0
    assert np.linalg.norm(r['forward_placement_sum_difference'])/np.linalg.norm(r['forward_charged_current_insertion'])<2e-15
    assert r['physical_a_mu'] is None


def test_open_current_insertion_is_exact_green_derivative():
    A=np.array([[2+1j,1],[0,3]],complex);P=11*np.eye(2)+A.conj().T@A
    J=np.eye(2)[:,:1];K=np.eye(2)[:,1:]
    G=external_current_schur_application(A,P,J,K)['Green']
    Z=np.array([[.3,.2j],[.1,-.2]],complex)
    h=1e-5
    # The factor Green G need not be Hermitian; both ordered inverse placements matter.
    numerical=(np.linalg.inv(np.linalg.inv(G)+h*Z)-np.linalg.inv(np.linalg.inv(G)-h*Z))/(2*h)
    np.testing.assert_allclose(numerical,-G@Z@G,rtol=3e-9,atol=3e-12)


def test_current_maps_and_numeric_inputs_fail_closed():
    with pytest.raises(ValueError,match='required'):
        external_current_schur_application(None,np.eye(2),np.eye(2)[:,:1],np.eye(2)[:,1:])
    with pytest.raises(ValueError,match='orthonormal'):
        external_current_schur_application(np.eye(2),np.eye(2),2*np.eye(2)[:,:1],np.eye(2)[:,1:])
    with pytest.raises(ValueError,match='positive'):
        external_current_schur_application(np.eye(2),-np.eye(2),np.eye(2)[:,:1],np.eye(2)[:,1:])
