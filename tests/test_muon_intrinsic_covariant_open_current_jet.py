from pathlib import Path
import numpy as np
import pytest
from scipy.linalg import expm

from bhsm.interface.muon_intrinsic_covariant_open_current_jet import (
    round_spatial_spin_connection,normal_coordinate_first_momentum_lift,
    covariant_bilocal_first_jet,reached_first_momentum_source_image,
    normal_frame_magnetic_principal_symbol_application,
)
from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation


def test_round_spin_lift_reproduces_retained_contraction_and_torsion_free_orientation():
    R=1.25;r=round_spatial_spin_connection(R)
    assert np.max(abs(r['owned_contracted_spin_difference']))<2e-15
    O=r['connection'];alpha=lepton_current_hilbert_representation()['alpha']
    np.testing.assert_allclose(O+O.conj().transpose(0,2,1),0,atol=0)
    # The spin lift rotates the right coframe with the inherited bracket.
    np.testing.assert_allclose(O[0]@alpha[1]-alpha[1]@O[0],-alpha[2]/R,atol=2e-15)


def test_three_normal_coordinate_momentum_columns_are_exact_local_first_jets():
    r=normal_coordinate_first_momentum_lift(.9)
    np.testing.assert_allclose(r['value_at_identity'],0,atol=0)
    np.testing.assert_allclose(r['physical_gradient_at_identity'],np.eye(3),rtol=0,atol=7e-16)
    assert r['incoming_C6_first_momentum_lift'].shape==(24,18)


def test_wilson_relative_and_center_jets_match_direct_endpoint_transport():
    rng=np.random.default_rng(27)
    F=rng.normal(size=(3,24,6))+1j*rng.normal(size=(3,24,6))
    B=rng.normal(size=(3,6,24))+1j*rng.normal(size=(3,6,24))
    O=rng.normal(size=(3,6,6))+1j*rng.normal(size=(3,6,6))
    O=(O-O.conj().transpose(0,2,1))/2
    n=normal_coordinate_first_momentum_lift(1.1)
    y=n['n1_value_at_identity'];d=n['n1_unit_coframe_derivative_at_identity']/1.1
    r=covariant_bilocal_first_jet(F,B,y,d,O)
    K=r['point_kernel'];dx=r['coordinate_left_derivative'];dy=r['coordinate_right_derivative']
    h=1e-6
    for i in range(3):
        # U(X,x), U(y,X), with x=X+r/2 and y=X-r/2.
        local=lambda e:expm(e*O[i]/2)@(K+e*(dx[:,i]-dy[:,i])/2)@expm(e*O[i]/2)
        np.testing.assert_allclose((local(h)-local(-h))/(2*h),r['Wilson_relative_first_jet'][:,i],rtol=3e-10,atol=3e-10)
        center=lambda e:expm(e*O[i])@(K+e*(dx[:,i]+dy[:,i]))@expm(-e*O[i])
        np.testing.assert_allclose((center(h)-center(-h))/(2*h),r['Wilson_center_first_jet'][:,i],rtol=3e-10,atol=3e-10)


def test_actual_magnetic_momentum_columns_have_nonzero_new_n2_source_image():
    root=Path(__file__).resolve().parents[1]
    p=root/'artifacts/muon_magnetic_mixed_green_20261011/run_3'
    import json
    md=json.loads((p/'result.json').read_text());row=next(x for x in md['records'] if x['side']=='incoming')
    with np.load(p/'scalar_sources.npz') as f:
        G=f['incoming_gaunt_even_odd_source']
    with np.load(p/'incoming_family_1_fermion_operators.npz') as f:
        Xi=f['incoming_family_1_Xi_even_odd']
    # Gaunt n0 times source1 gives the actual n1 insertion coefficients;
    # extract them from the already evaluated complete family direction.
    X=Xi[:,:6,:24].reshape(3,6,4,6).transpose(0,2,1,3)
    r=reached_first_momentum_source_image(X,G,row['even_harmonic_labels'],1.)
    assert r['complete_n0_n2_source_image'].shape==(3,60,18)
    assert np.linalg.norm(r['source_image_n2'])>0
    assert not r['existing_reverse_n0_rows_sufficient_for_complete_first_momentum_jet']


def test_numeric_guard_does_not_discard_imaginary_or_missing_connection():
    F=np.zeros((3,24,6));B=np.zeros((3,6,24));y=np.zeros(4);dy=np.zeros((3,4))
    with pytest.raises(ValueError,match='required'):
        covariant_bilocal_first_jet(F,B,y,dy,None)
    with pytest.raises(ValueError,match='real'):
        covariant_bilocal_first_jet(F,B,y+1j,dy,np.zeros((3,6,6)))
    with pytest.raises(ValueError,match='anti-Hermitian'):
        covariant_bilocal_first_jet(F,B,y,dy,np.ones((3,6,6)))


def test_normal_frame_minimal_magnetic_symbol_has_signed_unit_dirac_coefficient():
    from bhsm.interface.muon_magnetic_open_lepton_vertex import charged_dirac_injection
    from bhsm.interface.muon_intrinsic_higgs_weak_action import retained_higgs_spin_charge_representation
    H=np.array([.2j,1.1]);e=.3;family=1
    J=charged_dirac_injection(H,family=family)['charged']
    gamma=retained_higgs_spin_charge_representation()['gamma_Dirac']
    alpha=np.array([gamma[0]@g for g in gamma[1:]])
    epsilon=np.zeros((3,3,3))
    epsilon[0,1,2]=epsilon[1,2,0]=epsilon[2,0,1]=1
    epsilon[0,2,1]=epsilon[2,1,0]=epsilon[1,0,2]=-1
    dV=np.zeros((3,3,18,18),complex)
    for A in range(3):
        for j in range(3):
            small=(e/2)*sum(alpha[i]*epsilon[i,A,j] for i in range(3))
            dV[A,j]=J@small@J.conj().T
    r=normal_frame_magnetic_principal_symbol_application(np.zeros((3,18,18)),dV,
        round_spatial_spin_connection(1.)['connection'],H,family=family,electric_charge=e)
    np.testing.assert_allclose(r['relative_to_minimal_Dirac_spin_coefficient'],np.eye(3),rtol=0,atol=2e-15)
    assert not r['native_loop_or_LSZ_amputation_completed']
