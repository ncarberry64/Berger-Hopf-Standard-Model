import numpy as np
from bhsm.interface.muon_continued_action_dual import (
    analytic_midpoint_action, analytic_action_current, directed_action_contact,
    analytic_magnetic_current, principal_heat_contour_condition)


def test_original_green_identity_with_changing_complex_body_and_both_faces():
    rng=np.random.default_rng(144)
    H=rng.normal(size=(5,3,3))+1j*rng.normal(size=(5,3,3))
    a=analytic_midpoint_action(np.array([.12,.08,.15,.11,.13]),H)
    right=rng.normal(size=18)+1j*rng.normal(size=18)
    left=rng.normal(size=18)+1j*rng.normal(size=18)
    lhs=(a['midpoint_full']@left).T@a['contour_source_Gram']@(a['A_full']@right)
    lhs-=(a['left_Euler_full']@left).T@a['contour_source_Gram']@(a['midpoint_full']@right)
    expected=left[-3:].T@right[-3:]-left[:3].T@right[:3]
    np.testing.assert_allclose(lhs,expected,atol=7e-15)
    assert a['Green_identity_max']<3e-16
    assert a['doubled_skew_max']==0
    assert a['lorentz_contour_action_identity_max']==0


def test_signed_contour_action_and_independent_left_dual_current():
    rng=np.random.default_rng(63);w=np.linspace(.04,.07,6)
    H=rng.normal(size=(6,2,2))+1j*rng.normal(size=(6,2,2))
    a=analytic_midpoint_action(w,H)
    R=rng.normal(size=(6,2,2))+1j*rng.normal(size=(6,2,2))
    L=rng.normal(size=(6,2,2))+1j*rng.normal(size=(6,2,2))
    c=analytic_action_current(a,R,L)
    A=a['A_right_initial_zero'].toarray();u=np.linalg.solve(A,R.reshape(12,2))
    nodal=np.concatenate([np.zeros((1,2,2)),u.reshape(6,2,2)])
    coordinate=np.einsum('j,jab,jbc->ac',w,L,(nodal[:-1]+nodal[1:])/2)
    np.testing.assert_allclose(c['contour_current'],1j*coordinate,atol=1e-15)
    np.testing.assert_allclose(c['transpose_pairing'],c['contour_current'],atol=1e-15)
    np.testing.assert_allclose(a['lorentz_action'].toarray(),1j*a['action'].toarray(),atol=0)
    assert c['inverse_action_identity_max']<1e-15
    assert c['action_Hermitian_dual_mismatch_norm']>.1
    assert np.max(abs(c['original_right_Euler_rows']))<5e-15
    # A complex left map is linear, not conjugate-linear.
    d=analytic_action_current(a,R,(1+2j)*L)
    np.testing.assert_allclose(d['contour_current'],(1+2j)*c['contour_current'],atol=1e-15)


def test_rectangular_doubled_action_contact_equals_original_inverse_derivative():
    rng=np.random.default_rng(72);w=np.linspace(.08,.12,4)
    H0=rng.normal(size=(4,2,2));H1=rng.normal(size=(4,3,3))
    V=rng.normal(size=(4,3,2))+1j*rng.normal(size=(4,3,2))
    a=analytic_midpoint_action(w,H0);b=analytic_midpoint_action(w,H1)
    R=rng.normal(size=(4,2,2));L=rng.normal(size=(4,2,3))+1j*rng.normal(size=(4,2,3))
    c=analytic_action_current(a,R,np.zeros((4,2,2)))
    contact=directed_action_contact(a,b,V)
    mag=analytic_magnetic_current(a,b,c,L,contact)
    A=a['A_right_initial_zero'].toarray();B=b['A_right_initial_zero'].toarray()
    DV=contact['delta_right_operator'].toarray()
    joint=np.block([[A,np.zeros((8,12))],[.001*DV,B]])
    direct=np.linalg.solve(joint,np.concatenate([R.reshape(8,2),np.zeros((12,2))]))[8:]/.001
    np.testing.assert_allclose(mag['response'],direct,atol=2e-16)
    np.testing.assert_array_equal(contact['delta_left_Euler_action'].toarray(),contact['delta_action'].toarray().T)
    doubled=contact['delta_doubled_Grassmann_action'].toarray()
    np.testing.assert_array_equal(doubled+doubled.T,0)
    assert mag['current_pairing_max']<1e-16
    assert mag['inverse_operator_contact_identity_max']<1e-16
    assert np.max(abs(mag['original_right_Euler_rows']))<5e-16


def test_principal_condition_is_not_a_contour_or_full_adjoint_theorem():
    real=principal_heat_contour_condition(1,2e-11)
    imaginary=principal_heat_contour_condition(1j,2e-11)
    assert real['necessary_positive_high_frequency_decay']
    assert not imaginary['necessary_positive_high_frequency_decay']
    assert imaginary['principal_cutoff_phase']==-2e-11
    assert not real['full_sectorial_or_relative_contour_theorem']
