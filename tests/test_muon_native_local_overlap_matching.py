import numpy as np
from bhsm.interface.muon_native_local_overlap_matching import (
    native_local_normal_matching,matched_local_square_application,
    coupled_radial_matching_contacts,radial_scalar_Pauli_covector_probe,VOLUME)
from bhsm.interface.muon_owned_native_product_connection import owned_native_product_node
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_inherited_normal_readout_frame import phase_normal_readout_frame


def test_actual_native_first_jet_and_current_restrict_to_matched_flat_symbol():
    phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
    t=phase['receipt']['span']/2
    node=owned_native_product_node(phase,t,family=1)
    args=phase_normal_readout_frame(phase,family=1,electric_charge=.30282,coordinate_time=t)['arguments']
    a=native_local_normal_matching(node,args['H'],args['wall_connection'],family=1,
        matched_mass_action=.0018192,electric_charge=args['electric_charge'])
    for k in('normal_body_residual','mass_matching_residual','neutral_mass_return',
              'full_EM_current_restriction_residual','charged_EM_current_residual',
              'neutral_EM_source','charged_radial_vertex_residual'):
        assert np.linalg.norm(a[k])<4e-15
    p=matched_local_square_application(a,proper_frequency=.013,spatial_momentum=[.002,-.005,.004])
    assert np.linalg.norm(p['square_matching_residual'])<1e-16
    # The actual connection/body does not conserve a fixed free charged
    # fiber. Local connection removal must not be promoted to global Ward.
    assert np.linalg.norm(a['charge_factor_body_commutator'])>.1
    assert np.linalg.norm(a['covariant_mass_spatial_first'])>1e-5
    assert np.linalg.norm(a['required_mass_matching_load'])>1e-4


def test_full_scalar_dual_normalization_and_coupled_matching_identity():
    N,R,Mh=1.13,.91,2.3;Z=R**3/VOLUME
    T=np.zeros((96,336));T[:80,:80]=np.eye(80);T[80:,320:]=np.eye(16)
    h=np.array([.7,-.2,.3,.9]);r=h/np.linalg.norm(h)/np.sqrt(2)
    M=np.eye(336)*.1;M[320:,320:]=np.eye(16)*2*Z/N
    K=-np.eye(336)*N*1.7;K[320:,320:]=-N*2*Z*(3/R**2+Mh**2)*np.eye(16)
    B=np.zeros((336,336));f=np.arange(96,112)
    p=coupled_radial_matching_contacts((M,B,K),T,f,h,lapse=N,radius=R,
        matched_scalar_mass_action=Mh,frequencies=[.4j,1.7j])
    np.testing.assert_allclose(p['actual_radial_restricted_kinetic'],Z*np.eye(4),rtol=3e-15,atol=0)
    np.testing.assert_allclose(p['static_linear_kinetic_matching_contacts'],0,atol=4e-16)
    for a in p['probe_applications']:
        np.testing.assert_allclose(a['canonical_radial_Green'],np.linalg.inv(a['reference_radial_inverse']),atol=2e-14)
    # Independently integrate the calibrated local reference in x; this
    # checks the log-endpoint measure, sign and matched internal mass.
    from scipy.integrate import quad
    m,Y=.105,.00061
    probe=radial_scalar_Pauli_covector_probe(p,matched_fermion_mass_action=m,fixed_Y=Y,
        quadrature_order=12,log_endpoint_edges=[0,4,8,12,16,24,32])
    expected=Y**2/(16*np.pi**2)*quad(lambda x:m*m*x*x*(2-x)/(m*m*x*x+(1-x)*(Mh*Mh+3/R**2)),0,1,
        epsabs=1e-14,epsrel=1e-13)[0]
    assert abs(probe['reached_radial_covector_value']-expected)<2e-21
    assert abs(probe['reached_minus_reference_covector'])<2e-23
    # Changing the coordinate lapse preserves the proper kinetic residue.
    N2=.73
    p2=coupled_radial_matching_contacts((M*N/N2,B,K*N2/N),T,f,h,lapse=N2,radius=R,
        matched_scalar_mass_action=Mh,frequencies=[.4j,1.7j])
    np.testing.assert_allclose(p2['actual_radial_restricted_kinetic'],Z*np.eye(4),rtol=3e-15,atol=0)
    # A literal gauge/H contact alters the reached propagator. All gauge
    # return placements and their nonquadratic contribution must survive.
    rng=np.random.default_rng(252);C=rng.normal(size=(80,16))*.013
    K[:80,320:]=C;K[320:,:80]=C.T
    B[:80,320:]=rng.normal(size=(80,16))*.003
    p=coupled_radial_matching_contacts((M,B,K),T,f,h,lapse=N,radius=R,
        matched_scalar_mass_action=Mh,frequencies=[.4j,1.7j])
    assert np.linalg.norm(p['static_linear_kinetic_matching_contacts'])>1e-3
    for a in p['probe_applications']:
        assert np.linalg.norm(a['radial_gauge_wall_Green'])>.01
        assert np.linalg.norm(a['surviving_nonquadratic_inverse'])>1e-6
        assert np.max(abs(a['original_reaction_resolved_residual']))<2e-14
        assert np.max(abs(a['inverse_matching_identity_residual']))<2e-16


def test_temporal_native_source_cannot_be_used_as_lorentz_current_without_conversion():
    phase=load_profile_preserving_phase('artifacts/muon_finite_normal_phase_20261011/incoming_run_1')
    node=owned_native_product_node(phase,0.,family=2)
    args=phase_normal_readout_frame(phase,family=2,electric_charge=.30282)['arguments']
    a=native_local_normal_matching(node,args['H'],args['wall_connection'],family=2,
        matched_mass_action=8.8e-6,electric_charge=args['electric_charge'])
    J=a['charged_injection']
    wrong=node['N']*J.conj().T@a['native_temporal_EM_source']@J
    assert np.linalg.norm(wrong-a['charged_EM_current'][0])>.8
    np.testing.assert_allclose(a['charged_EM_current'][0],args['electric_charge']*np.eye(4),atol=2e-16)
