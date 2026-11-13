import numpy as np
from scipy.linalg import expm
from bhsm.interface.muon_holomorphic_em_current import holomorphic_unit_em_moments,changing_unit_em_current


def test_realified_em_charge_and_both_source_jets_obey_literal_action():
    h=np.array([1.2+.03j,.4-.02j,.06+.01j,-.02+.004j])
    dh=np.array([[.2+.1j,.02],[-.1j,.13],[.08,.04j],[.1,-.05j]])
    a=holomorphic_unit_em_moments(h,dh,.8+.04j,np.array([.11+.02j,-.03j]))
    for n in ('charge_idempotence_rows','charge_idempotence_first_rows','charge_generator_rows',
        'charge_generator_first_rows','canonical_current_coframe_rows','canonical_current_coframe_first_rows',
        'fixed_Y_mass_charge_rows','fixed_Y_mass_charge_first_rows'):
        np.testing.assert_allclose(a[n],0,atol=8e-16)
    step=2e-5
    for k in range(2):
        b=holomorphic_unit_em_moments(h+step*dh[:,k],dh,.8+.04j+step*np.array([.11+.02j,-.03j])[k],np.array([.11+.02j,-.03j]))
        c=holomorphic_unit_em_moments(h-step*dh[:,k],dh,.8+.04j-step*np.array([.11+.02j,-.03j])[k],np.array([.11+.02j,-.03j]))
        np.testing.assert_allclose(a['literal_right_first'][k],(b['literal_right']-c['literal_right'])/(2*step),rtol=3e-8,atol=2e-11)
    assert np.linalg.norm(a['literal_left']-a['literal_right'].conj().T)>.01
    # The owned common phase has no neutral-line motion; a perpendicular
    # direction changes that line and is not frozen as an EM-axis fit.
    phase=np.r_[-h[2:],h[:2]][:,None]
    p=holomorphic_unit_em_moments(h,phase,1.,np.zeros(1))
    np.testing.assert_allclose(p['charge_first'],0,atol=1e-16)
    assert np.linalg.norm(a['charge_first'])>.1


def test_current_all_three_first_placements_match_whole_nonsymmetric_action():
    rng=np.random.default_rng(495);draw=lambda s:.07*(rng.normal(size=s)+1j*rng.normal(size=s))
    H=draw((2,18,18));dH=draw((2,2,18,18));N=np.array([1+.04j,.8-.02j]);dN=draw((2,2))
    hc=np.array([[1+.02j,.3,.07,-.02],[1+.01j,.4,.04,.03]])
    dh=draw((2,4,2));steps=np.array([.04+.01j,.03-.006j])
    stages=[dict(Hcan=H[j],Hcan_first=dH[j],induced_lapse=np.array(N[j]),induced_lapse_first=dN[j])for j in range(2)]
    a=changing_unit_em_current(steps,stages,hc,dh)
    def direct(s,k):
        P=np.eye(54,dtype=complex)
        for j in range(2):
            n=N[j]+s*dN[j,k];hh=H[j]+s*dH[j,k]
            m=holomorphic_unit_em_moments(hc[j]+s*dh[j,:,k],dh[j],n,dN[j])
            B=np.zeros((54,54),complex);B[:18,:18]=-1j*n*hh;B[:18,18:36]=1j*n*m['literal_right']
            B[36:,:18]=1j*n*m['literal_left'];P=expm(steps[j]*B)@P
        return P[36:,18:36]
    np.testing.assert_allclose(a['whole_current'],direct(0,0),atol=3e-18)
    np.testing.assert_allclose(a['whole_current'],a['independent_transpose_current'],atol=3e-18)
    np.testing.assert_allclose(a['whole_current_first'],a['independent_transpose_current_first'],atol=3e-18)
    np.testing.assert_allclose(a['first_placement_sum_rows'],0,atol=3e-18)
    h=2e-5
    for k in range(2):np.testing.assert_allclose(a['whole_current_first'][k],(direct(h,k)-direct(-h,k))/(2*h),rtol=3e-8,atol=2e-12)
    assert np.linalg.norm(a['left_current_motion_first'])>1e-4
    assert np.linalg.norm(a['right_current_motion_first'])>1e-4
    assert not a['physical_charge_F1_residue_soft_Pauli_or_external_pole_selected']
