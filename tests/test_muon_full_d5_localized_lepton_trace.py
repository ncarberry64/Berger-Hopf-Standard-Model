"""Independent fullClifford, charge and literal source/trace controls."""
import numpy as np
from numpy.testing import assert_allclose
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace,lift_localized_analytic_source
from bhsm.interface.muon_full_d5_localized_lepton_trace import moving_d5_material_trace_frame
from bhsm.interface.muon_full_d5_localized_lepton_trace import normalized_d5_point_trace
from bhsm.interface.muon_full_d5_localized_lepton_trace import normalized_d5_dirac_bar_trace
from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation


def test_full_carrier_clifford_charge_intertwiner_and_complement():
    a=full_d5_localized_lepton_trace();G=a['gamma5D_self_dual128'];metric=np.diag([1,-1,-1,-1,-1])
    assert_allclose(G[:,None]@G[None]+G[None]@G[:,None],2*metric[:,:,None,None]*np.eye(128),atol=3e-15)
    assert_allclose(a['gamma5D_conjugate'][:4],a['gamma5D_particle'][:4],atol=2e-15)
    assert_allclose(a['gamma5D_conjugate'][4],-a['gamma5D_particle'][4],atol=2e-15)
    assert_allclose(a['localized_gauge_intertwiner'],lepton_unit_trace_gauge_representation()['generators'],atol=2e-16)
    assert_allclose(a['localized_canonical_angular_clifford'],lepton_current_hilbert_representation()['alpha'],atol=2e-15)
    W=a['localized_lepton18_trace_lift'];D=a['localized_lepton18_literal_dual'];pair=a['particle_antiparticle36_trace_lift'];Q=a['full_retained_complement']
    assert_allclose(D@W,np.eye(18),atol=0)
    assert_allclose(pair.conj().T@pair,np.eye(36),atol=2e-15)
    assert_allclose(Q@pair,0,atol=2e-15)
    assert_allclose(Q@Q,Q,atol=2e-15)
    assert int(round(np.trace(Q).real))==348
    # The full time Clifford sends localized fields into retained missing
    # opposite chirality, so18 cannot be promoted to a full5D Clifford.
    time=np.kron(np.eye(3),G[0]);assert np.linalg.norm(Q@time@W)>1
    gauge=a['unitTr16_gauge_all_families']
    assert_allclose(np.array([g@W-W@l for g,l in zip(gauge,a['localized_gauge_intertwiner'])]),0,atol=2e-16)


def test_independent_complex_source_dual_and_no_e_c_right_spin_graft():
    a=full_d5_localized_lepton_trace();rng=np.random.default_rng(566)
    M=rng.normal(size=(18,18))+1j*rng.normal(size=(18,18))
    u=rng.normal(size=18)+1j*rng.normal(size=18);left=rng.normal(size=18)+1j*rng.normal(size=18)
    W=a['localized_lepton18_trace_lift'];D=a['localized_lepton18_literal_dual'];V=lift_localized_analytic_source(M,full_representation=a)
    assert_allclose((left@D)@V@(W@u),left@M@u,rtol=2e-15,atol=2e-13)
    assert np.linalg.norm(V-lift_localized_analytic_source(M.conj(),full_representation=a))>10
    assert np.flatnonzero(W[:,12])[0]==64+2*16+14
    # A right-spin field in ordinary e_c still has Y=+1; it is not e_R.
    actual=a['localized_gauge_intertwiner'][3,12,12]
    wrong=a['unitTr16_gauge_particle'][3,14,14]
    assert abs(actual+wrong)<2e-16 and abs(actual-wrong)>.5
    C=a['charge_conjugation_all_families']
    assert_allclose(C@W.conj(),a['localized_antilepton18_trace_lift'],atol=0)


def test_actual_boost_principals_and_independent_analytic_dual_first():
    U=.23+.07j;dU=.04-.03j;a=moving_d5_material_trace_frame(U,dU)
    assert_allclose(a['adapted_time_Clifford_rows'],0,atol=2e-15)
    assert_allclose(a['adapted_normal_Clifford_rows'],0,atol=2e-15)
    assert_allclose(a['ambient_literal_trace_dual']@a['ambient_trace_lift'],np.eye(18),atol=2e-15)
    assert np.linalg.norm(a['ambient_literal_trace_dual']-a['ambient_trace_lift'].conj().T)>.1
    h=1e-5;p=moving_d5_material_trace_frame(U+h*dU,dU);m=moving_d5_material_trace_frame(U-h*dU,dU)
    for key in ('ambient_trace_lift','ambient_literal_trace_dual'):
        assert_allclose(a[key+'_first'],(p[key]-m[key])/(2*h),rtol=2e-8,atol=2e-11)
    real=moving_d5_material_trace_frame(.23,.04)
    assert_allclose(real['real_wall_Hilbert_current_isometry_rows'],0,atol=2e-15)


def test_normalized_pointtrace_seam_and_all_source_factors():
    ur=.8+.06j;ul=.9-.02j;dr=np.array([.04-.01j]);dl=np.array([-.03+.05j]);U=.2+.03j;dU=np.array([.02-.04j])
    a=normalized_d5_point_trace(ur,ul,dr,dl,U,dU)
    assert_allclose(a['right_normalized_trace_recovery_rows'],0,atol=2e-15)
    assert_allclose(a['literal_left_normalized_trace_recovery_rows'],0,atol=2e-15)
    h=1e-5;p=normalized_d5_point_trace(ur+h*dr[0],ul+h*dl[0],dr,dl,U+h*dU[0],dU)
    m=normalized_d5_point_trace(ur-h*dr[0],ul-h*dl[0],dr,dl,U-h*dU[0],dU)
    for key in ('normalized_right_Gamma0','normalized_literal_left_Gamma0','normalized_seam_scalar_chart_factor'):
        assert_allclose(a[key+'_first'][0],(p[key]-m[key])/(2*h),rtol=3e-8,atol=3e-11)
    rng=np.random.default_rng(157);psi=rng.normal(size=18)+1j*rng.normal(size=18)
    bar=rng.normal(size=18)+1j*rng.normal(size=18);YH=rng.normal(size=(18,18))+.3j*rng.normal(size=(18,18))
    source=a['normal_mode_right_point_lift']@psi;dual=bar@a['normal_mode_literal_left_point_lift']
    seam=a['normalized_literal_left_Gamma0']@YH@a['normalized_right_Gamma0']
    assert_allclose(dual@seam@source,bar@YH@psi,rtol=3e-15,atol=1e-12)


def test_dirac_bar_pointtrace_matches_real_current_and_complex_seam_source():
    real=normalized_d5_dirac_bar_trace(.8,.8,np.array([.03]),np.array([.03]),.21,np.array([.02]))
    ER=real['normal_mode_right_point_lift'];G0=real['Dirac_bar_to_canonical_factor']
    assert_allclose(real['normal_mode_Dirac_bar_left_point_lift'],ER.conj().T@G0,atol=2e-15)
    assert_allclose(real['Dirac_bar_trace_recovery_rows'],0,atol=2e-15)
    q=normalized_d5_dirac_bar_trace(.8+.03j,.9-.07j,np.array([.03-.02j]),
        np.array([-.02+.01j]),.21+.04j,np.array([.02-.01j]))
    rng=np.random.default_rng(727);draw=lambda s:rng.normal(size=s)+.2j*rng.normal(size=s)
    chi,left,M=draw(18),draw(18),draw((18,18))
    source=q['normal_mode_right_point_lift']@chi
    bar=left@q['normal_mode_Dirac_bar_left_point_lift']
    seam=q['normalized_Dirac_bar_left_Gamma0']@M@q['normalized_right_Gamma0']
    assert_allclose(bar@seam@source,left@M@chi,atol=8e-13,rtol=3e-15)
    assert np.linalg.norm(q['normal_mode_Dirac_bar_left_point_lift']-
        q['normal_mode_right_point_lift'].conj().T@G0)>.1
    h=1e-5
    def at(t):return normalized_d5_dirac_bar_trace(.8+.03j+t*(.03-.02j),
        .9-.07j+t*(-.02+.01j),np.array([.03-.02j]),np.array([-.02+.01j]),
        .21+.04j+t*(.02-.01j),np.array([.02-.01j]))
    plus,minus=at(h),at(-h)
    for key in ('normal_mode_Dirac_bar_left_point_lift','normalized_Dirac_bar_left_Gamma0'):
        assert_allclose(q[key+'_first'][0],(plus[key]-minus[key])/(2*h),rtol=3e-8,atol=4e-11)
