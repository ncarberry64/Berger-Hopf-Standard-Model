import numpy as np
from bhsm.interface.muon_owned_static_charged_current import owned_chiral_charge_injection,owned_static_charged_current
from bhsm.interface.muon_static_coupled_charged_current import static_coupled_charged_current
from bhsm.interface.muon_native_dirac_hamiltonian import fixed_y_higgs_hamiltonian


def test_charge_spin_and_mass_maps_come_from_owned_weak_times_spin_carrier():
    H=np.array([.2+.1j,.7-.15j]);a=owned_chiral_charge_injection(H,family=1)
    J,N,fi=a['charged_chiral'],a['neutral_left'],a['family_indices']
    h=H/np.linalg.norm(H)
    expected=np.vstack((np.c_[h[0]*np.eye(2),np.zeros((2,2))],np.c_[h[1]*np.eye(2),np.zeros((2,2))],np.c_[np.zeros((2,2)),np.eye(2)]))
    np.testing.assert_allclose(J,expected,atol=3e-16)
    np.testing.assert_allclose(a['charge_alignment_residual'],0,atol=3e-16)
    np.testing.assert_allclose(a['neutral_charge_residual'],0,atol=3e-16)
    np.testing.assert_allclose(J.conj().T@N,0,atol=3e-16)
    M=fixed_y_higgs_hamiltonian(H[None])[0][np.ix_(fi,fi)]
    B=J.conj().T@M@J;mass=(B[0,2]+B[1,3])/2
    np.testing.assert_allclose(B,mass*np.block([[np.zeros((2,2)),np.eye(2)],[np.eye(2),np.zeros((2,2))]]),atol=3e-19)


def test_axis_source_interchanges_no_weak_and_spin_indices_or_field_inverse():
    H=np.array([0.,1.]);old=static_coupled_charged_current(np.eye(24),H,radius=.9,lapse=.7,family=1)
    a=owned_static_charged_current(np.eye(24),H,radius=.9,lapse=.7)
    # An independent charged-state axis test fails for the preserved old
    # injection even though its Gram and literal tensor identity pass.
    assert np.linalg.norm(old['charged_injection']-a['right_charge_injection'])>1
    np.testing.assert_allclose(a['right_charge_injection'][2:4,:2],np.eye(2),atol=3e-16)
    np.testing.assert_allclose(a['right_charge_injection'][:2],0,atol=3e-16)
    assert np.max(abs(a['exact_sector_sum_difference']))<3e-16
    assert a['angular_current_integral']==1
