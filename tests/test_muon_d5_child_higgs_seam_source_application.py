import numpy as np

from bhsm.interface.muon_d5_child_higgs_seam_source_application import (
    operator_consumed_lepton_lift,lepton_middle_jet,child_seam_factors,apply_ordered_event_seam,
)
from bhsm.interface.muon_formed_event_domain_application import endpoint_seam_numerator
from bhsm.interface.muon_d5_spatial_bundle_application import known_spin_gauge_factor


def test_phase_is_integer_lepton_representation_and_source_is_analytic():
    a=known_spin_gauge_factor(np.eye(3),np.eye(3));u=np.exp(.37j)
    K,Kx=lepton_middle_jet(a['known_middle128'],a['known_middle_free_rotation_first128'],u)
    C,powers=operator_consumed_lepton_lift()
    np.testing.assert_array_equal(C.T@C,np.eye(36))
    np.testing.assert_allclose(K,np.diag(u**powers),atol=0,rtol=0)
    np.testing.assert_allclose(Kx[6],K@np.diag(1j*powers),atol=0,rtol=0)
    # An analytic i coefficient is multiplied linearly; it is not conjugated.
    np.testing.assert_allclose(1j*Kx[6],-K@np.diag(powers),atol=0,rtol=0)


def test_event_density_normal_maps_cannot_be_absorbed_or_commuted():
    rng=np.random.default_rng(917);L=rng.normal(size=(18,36));q=rng.normal(size=(36,2))
    Dc=np.eye(36);Dc[0,1]=.4;Dp=np.eye(36);Dp[1,2]=-.3
    K=np.eye(36);K[1,0]=.2
    actual=apply_ordered_event_seam(L,Dc,K,Dp,q)
    np.testing.assert_allclose(actual,L@Dc@K@Dp@q,rtol=0,atol=0)
    assert np.linalg.norm(actual-L@K@q)>.01
    assert np.linalg.norm(actual-L@K@Dc@Dp@q)>.001


def test_original_seam_source_has_one_gamma0_and_same_canonical_sign():
    from test_muon_formed_event_domain_application import data
    x,_=data('outgoing','lo');x[260:264]=[.13,.71,-.09,.07]
    e=endpoint_seam_numerator(x,np.zeros(268))
    cache=dict(outgoing_plus_spin_boost128=e['frames']['plus']['spin_boost128'],
        outgoing_Bhat=e['Bhat'][0],outgoing_raw268=x)
    f=child_seam_factors(cache,e['surface_density'])
    d=np.array([.031,-.019,.011,-.017]);M=np.einsum('c,cij->ij',d,f['vertices'])
    T=f['density']*M@f['B'];dN=f['jump_factor']@T;dS=f['action_factor']@T
    np.testing.assert_allclose(f['J']@dN+f['Gamma0']@dS,0,atol=3e-16)
    # The selected operator annihilates OTHER SM species by its actual rows,
    # rather than assigning their states zero.
    C,_=operator_consumed_lepton_lift()
    np.testing.assert_allclose(f['B']@(np.eye(384)-C@C.T),0,atol=0,rtol=0)
