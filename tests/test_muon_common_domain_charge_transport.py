import numpy as np
from scipy.linalg import expm
from bhsm.interface.muon_common_domain_charge_transport import (
    holomorphic_charge_first, source_clock_higgs_first, transported_charge_application)
from bhsm.interface.muon_source_directed_em_normal_current import holomorphic_charge_projection
from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from bhsm.interface.muon_piecewise_euclidean_action import FAMILY_INDICES


def generators():
    i=FAMILY_INDICES[1]
    return lepton_unit_trace_gauge_representation()['generators'][:,i][:,:,i]


def test_charge_quotient_first_uses_the_same_nonreal_direction_and_keeps_the_neutral_kernel():
    h=np.array([.8+.07j,.12-.04j,.08+.02j,.03-.05j])
    dh=np.array([.2+.3j,-.1+.07j,.06-.05j,.2-.04j]);G=generators()
    a=holomorphic_charge_first(h,dh,G);eps=2e-6
    def independent(x):
        s=holomorphic_charge_projection(x)['unit_Tr16_charge_coefficients']
        return 1j*np.einsum('c,cij->ij',s,G)
    np.testing.assert_allclose(a['charge'],independent(h),atol=3e-16)
    np.testing.assert_allclose(a['charge_first'],(independent(h+eps*dh)-independent(h-eps*dh))/(2*eps),rtol=2e-9,atol=2e-10)
    Q,Q1=a['charge'],a['charge_first']
    np.testing.assert_allclose(Q@Q+Q,0,atol=6e-16)
    np.testing.assert_allclose(Q@Q1+Q1@Q+Q1,0,atol=5e-16)


def test_connector_clock_and_noncommuting_source_map_do_not_silently_satisfy_the_full_action():
    G=generators();h=np.array([.9+.03j,.1,.08j,.04]);dh=np.array([.1j,.03,.02+.02j,.04])
    a=holomorphic_charge_first(h,dh,G)
    rng=np.random.default_rng(305);A=.03*(rng.normal(size=(6,6))+1j*rng.normal(size=(6,6)))
    H=A+np.diag(np.arange(6))*.02;F=expm(-.2*A);L=np.linalg.solve(F.T,np.eye(6))
    b=transported_charge_application(a['charge'],a['charge_first'],H,A,F,L)
    eps=2e-6
    def curve(s):
        Q=holomorphic_charge_first(h+s*dh,np.zeros(4),G)['charge'];Fs=expm(-s*A)@F
        return np.linalg.solve(Fs,Q@Fs)
    np.testing.assert_allclose(b['represented_source_chart_charge_first'],(curve(eps)-curve(-eps))/(2*eps),rtol=3e-9,atol=3e-10)
    np.testing.assert_allclose(b['analytic_dual_pairing_residual'],0,atol=3e-16)
    assert np.linalg.norm(b['actual_source_chart_weak_action_residual'])>.05
    assert np.linalg.norm(b['action_minus_represented_charge_first'])>.001
    # On a constant-coordinate connector only the inherited profile stops.
    w=1+.2j;N=1.1-.07j;nodal=np.array([.1j,.2,.03-.04j,.05]);base=np.array([.3,.4j,.1,.2])
    fieldrate=1j*N/w*nodal
    np.testing.assert_allclose(source_clock_higgs_first(base+fieldrate,fieldrate,0,w,N),nodal/w,atol=6e-17)
    slope=.03-.02j
    np.testing.assert_allclose(source_clock_higgs_first(base+fieldrate,fieldrate,slope,w,N),(slope*base+nodal)/w,atol=6e-17)
