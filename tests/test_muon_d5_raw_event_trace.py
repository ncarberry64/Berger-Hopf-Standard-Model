import numpy as np
from scipy.linalg import expm
from bhsm.interface.muon_d5_raw_event_trace import (
    sm_gauge_lift,raw_trace_transfer,raw_trace_transfer_first,
    point_to_half_density_transfer,original_wall_green_checks,
    colorless_trace_lift,colorless_middle_jet,required_raw_closed_trace,
)
from bhsm.interface.muon_full_d5_localized_lepton_trace import moving_d5_material_trace_frame


def test_full_gauge_lepton_phase_has_no_color_or_cube_root_ambiguity():
    # Nontrivial group factors test the representation, not a physical state.
    K=expm(np.array([[.21j,.13],[-.13,-.21j]]))
    C=expm(1j*np.diag([.17,-.29,.12]));w=np.exp(.19j)
    g=sm_gauge_lift(K,w,C)
    from bhsm.interface.muon_d5_child_higgs_seam_source_application import operator_consumed_lepton_lift
    L,powers=operator_consumed_lepton_lift();a=L.T@np.kron(np.eye(3),g)@L
    gp=sm_gauge_lift(K,w*np.exp(2j*np.pi/3),expm(1j*np.diag([.31,-.11,-.20])))
    b=L.T@np.kron(np.eye(3),gp)@L
    np.testing.assert_allclose(a,b,atol=2e-15)
    np.testing.assert_allclose(g.conj().T@g,np.eye(128),atol=4e-16)


def test_raw_transfer_first_contains_both_frame_contacts():
    rng=np.random.default_rng(64);D=lambda:rng.normal(size=(384,384))*1e-3
    p=np.eye(384)+D();c=np.eye(384)+D();k=np.eye(384)+D();px,cx,kx=D(),D(),D()
    v,x=raw_trace_transfer_first(p,c,k,px,cx,kx,spin_sign=-1)
    # Real analytic matrices permit a complex-step check without subtracting
    # two near-unit diagonal384 entries (which loses finite-difference digits).
    e=1e-20
    fd=raw_trace_transfer(p+1j*e*px,c+1j*e*cx,k+1j*e*kx,spin_sign=-1).imag/e
    np.testing.assert_allclose(x,fd,atol=128*np.finfo(float).eps*np.max(abs(x)),rtol=8e-14)


def test_original_green_current_uses_clock_density_and_not_mode_profile():
    p=moving_d5_material_trace_frame(.12,0)['spin_boost128']
    c=moving_d5_material_trace_frame(-.23,0)['spin_boost128']
    p,c=(np.kron(np.eye(3),a) for a in (p,c))
    g=np.kron(np.eye(3),sm_gauge_lift(np.eye(2),np.exp(.11j),np.eye(3)))
    r=original_wall_green_checks(p,c,g,1.4,.8,1.1,1.1,.8/1.4)
    for key in ('normal_Clifford_rows','time_Clifford_rows','Dirac_bar_rows','original_wall_green_rows'):
        np.testing.assert_allclose(r[key],0,atol=32*np.finfo(float).eps)
    assert not r['normal_mode_factor_in_raw_transfer']
    assert not r['full_E1_cap_incidence_derived']
    bad=original_wall_green_checks(p,c,g,1.4,.8,1.1,1.1,1.)
    assert np.max(abs(bad['original_wall_green_rows']))>.5


def test_half_density_factor_is_a_determined_coordinate_change():
    M=np.array([[1.,2.],[3.,4.]])
    np.testing.assert_array_equal(point_to_half_density_transfer(M,2,8),2*M)


def test_both_charge_and_neutral_colorless96_is_closed_under_original_clifford_gauge():
    from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
    from bhsm.interface.muon_d5_spatial_bundle_application import known_spin_gauge_factor
    from scipy.spatial.transform import Rotation
    f=full_d5_localized_lepton_trace();C,powers=colorless_trace_lift()
    assert C.shape==(384,96)
    outside=np.eye(384)-C@C.T
    for g in f['gamma5D_self_dual128']:
        np.testing.assert_array_equal(outside@np.kron(np.eye(3),g)@C,0)
    for g in f['unitTr16_gauge_all_families']:
        np.testing.assert_array_equal(outside@g@C,0)
    m=known_spin_gauge_factor(Rotation.from_rotvec([.2,-.1,.3]).as_matrix(),
        Rotation.from_rotvec([-.1,.3,.12]).as_matrix())
    _,K,Kx=colorless_middle_jet(m['known_middle128'],m['known_middle_free_rotation_first128'],np.exp(.2j))
    np.testing.assert_allclose(K.conj().T@K,np.eye(96),atol=6e-16)
    rng=np.random.default_rng(5);q=rng.normal(size=(384,3));qx=rng.normal(size=q.shape)
    r=required_raw_closed_trace(q,qx,np.eye(384),np.zeros((384,384)),C,K,Kx,spin_sign=1)
    np.testing.assert_allclose(r['original_wall_trace_rows'],0,atol=1e-15)
    np.testing.assert_allclose(r['original_wall_trace_source_rows'],0,atol=1e-15)
