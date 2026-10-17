"""Independent constant connection and coordinate-chain D5 controls."""
import numpy as np
from scipy.linalg import expm
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from bhsm.interface.muon_sigma_collar_d5_weak_action import collar_spin_gauge_transport,original_collar_coordinate_action


def test_spin_gauge_line_and_literal_inverse_match_one_full_exponential():
    full=full_d5_localized_lepton_trace();s=.17;w=.3-.11j
    coeff=np.array([.2+.07j,-.05+.03j,.09j,.04-.02j]);G=full['unitTr16_gauge_particle']
    A=np.einsum('a,aij->ij',coeff,G);B=np.einsum('a,aij->ij',coeff,G.conj())
    T,L,Tb,Lb=expm(-s*A),expm(s*A),expm(-s*B),expm(s*B)
    z=collar_spin_gauge_transport(s*w,w,T,L,Tb,Lb,-A@T,L@A,-B@Tb,Lb@B,full=full,sheet_orientation=-1)
    for branch,gauge,sl in(('particle',A,slice(0,64)),('conjugate',B,slice(64,128))):
        gamma=full['gamma5D_'+branch];O=-.5*gamma[0]@gamma[4]*w
        generator=np.kron(O,np.eye(16))+np.kron(np.eye(4),gauge)
        expected=expm(-s*generator)
        assert np.max(abs(z['spin_gauge_transport128'][sl,sl]-expected))<2e-15
        h=1e-6;fd=(expm(-(s+h)*generator)-expm(-(s-h)*generator))/(2*h)
        assert np.max(abs(z['spin_gauge_transport_first128'][sl,sl]-fd))<1e-9
    assert np.max(abs(z['analytic_inverse_rows']))<2e-15
    assert np.max(abs(z['analytic_inverse_first_rows']))<2e-15


def test_original_coordinate_derivatives_recover_independent_complex_trial_chain():
    full=full_d5_localized_lepton_trace();g=full['gamma5D_particle'];T=full['unitTr16_gauge_particle']
    rng=np.random.default_rng(723);V=rng.normal(size=(64,64))+1j*rng.normal(size=(64,64));Vt=.1*V+.03*V.T;Vr=-.2*V+.04j*V.T
    left=rng.normal(size=(64,64))+.1j*rng.normal(size=(64,64));Xi=np.array([.9+.04j,.07-.02j]);F=np.array([-.2+.03j,-1.1+.05j])
    Vq=Xi[0]*Vt+Xi[1]*Vr;Vs=F[0]*Vt+F[1]*Vr
    c=dict(lapse=1.2+.03j,radial_coframe=.8-.07j,radius=.9+.08j,coordinate_shift=.14-.02j,
        geometric_time_contact=0j,geometric_radial_contact=0j,gauge_connection_material=np.zeros((5,4),complex))
    E=.03+.01j;clock=.7+.02j
    z=original_collar_coordinate_action(c,gamma=g,generators=T,right_value=V,right_normal_first=Vs,right_transverse_first=Vq,
        literal_left_value=left,normal_coordinate_velocity=F,leaf_transverse=Xi,eta_mass_outward=0,
        normal_timelike_outward=.2,normal_radial_outward=np.sqrt(1.04),sheet_orientation=-1,surface_proper_clock=clock,energy=E)
    assert np.max(abs(z['actual_trial_coordinate_time']-Vt))<2e-15
    assert np.max(abs(z['actual_trial_coordinate_radial']-Vr))<2e-15
    G=np.array([np.kron(a,np.eye(16))for a in g]);spin=np.kron(-1.5j*g[1]@g[2]@g[3],np.eye(16))
    expected=(spin/c['radius']+G[0]*E*clock/c['lapse'])@V+1j*G[0]@(Vt-c['coordinate_shift']*Vr)/c['lapse']-1j*G[4]@Vr/c['radial_coframe']
    assert np.max(abs(z['original_D5_on_trial']-expected))<3e-15
    assert np.max(abs(z['literal_weak_integrand']-left@expected))<1e-13
