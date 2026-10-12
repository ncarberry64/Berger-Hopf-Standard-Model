"""Independent reflection, formal-domain and actual coefficient checks."""
import numpy as np
from scipy.sparse.linalg import splu
from bhsm.interface.muon_continued_action_reality import (
    _higgs_mass_realified,action_reality_coefficient,reflected_action_reality_coefficient,
    certify_local_coframe_disk,local_formal_reflected_square,_analytic_polynomial,
    formal_square_magnetic_application)
from bhsm.interface.muon_native_dirac_hamiltonian import fixed_y_higgs_hamiltonian


def test_realified_lr_conjugate_branch_is_holomorphic_not_pointwise_conjugated():
    x=np.array([.3,-.5,.2,.1]);r=np.array([.01,.02,-.04,.03]);z=.4+.3j
    real=_higgs_mass_realified(x)
    np.testing.assert_array_equal(real,fixed_y_higgs_hamiltonian((x[:2]+1j*x[2:])[None])[0])
    a=_higgs_mass_realified(x+z*r);b=_higgs_mass_realified(x+z.conjugate()*r)
    np.testing.assert_allclose(a,b.conj().T,atol=3e-18)
    assert np.linalg.norm(a-a.conj().T)>1e-5
    step=1e-4
    derivative=(_higgs_mass_realified(x+step*r)-_higgs_mass_realified(x-step*r))/(2*step)
    np.testing.assert_allclose((a-real)/z,derivative,atol=7e-15)


def test_formal_reflection_square_retains_principal_rotation_and_final_contact():
    w=np.array([.1,.12,.09]);H=np.zeros((3,2,2),complex)
    real=local_formal_reflected_square(w,H,H,rotation=1)
    imaginary=local_formal_reflected_square(w,H,H,rotation=1j)
    np.testing.assert_allclose(imaginary['K'].toarray(),-1j*real['K'].toarray(),atol=0)
    np.testing.assert_allclose(imaginary['variable_Gram'],1j*real['variable_Gram'],atol=0)
    Preal=np.linalg.solve(real['variable_Gram'],real['K'].toarray())
    Pimag=np.linalg.solve(imaginary['variable_Gram'],imaginary['K'].toarray())
    np.testing.assert_allclose(Pimag,-Preal,atol=0)
    assert imaginary['final_natural_contact_rows'].shape==(2,6)
    assert np.linalg.norm(imaginary['final_natural_contact_rows'].toarray())>1
    R=np.arange(12).reshape(6,2)
    u=splu(imaginary['K']).solve(imaginary['Abar'].T@imaginary['source_Gram']@R)
    direct=splu(imaginary['A']).solve(R)
    np.testing.assert_allclose(u,direct,atol=3e-16)
    assert np.linalg.norm(imaginary['K'].toarray()-imaginary['ordinary_imaginary_slice_positive_square'].toarray())>1


def test_complex_source_polynomial_preserves_the_owned_real_curve():
    from scipy.interpolate import CubicHermiteSpline
    t=np.array([0.,1.,2.]);f=t**3;fp=3*t*t
    p=CubicHermiteSpline(t,f,fp)
    z=.2+.3j
    np.testing.assert_allclose(_analytic_polynomial(p,.5,z),(.5+z)**3,atol=4e-16)
    assert abs(_analytic_polynomial(p,.5,z).imag)>.1


def test_actual_corrected_both_sides_coframe_and_reflection_match_original_owner():
    from scripts.evaluate_muon_continued_current_factor import retained_input
    from bhsm.interface.muon_profile_preserving_phase_sample import profile_preserving_lepton_sample
    for side in('incoming','outgoing'):
        p,_=retained_input(side,{})
        L=abs(float(p['receipt']['span']));t=(-.75 if side=='incoming'else .25)*L
        a=action_reality_coefficient(p,t)
        owned=profile_preserving_lepton_sample(p,t)['operator']
        np.testing.assert_allclose(a['W'],owned['W'],atol=5e-16)
        np.testing.assert_allclose(a['Omega'],owned['Omega_tau'],atol=5e-16)
        b=reflected_action_reality_coefficient(p,t,(1+1j)*L/64)
        assert b['Hcan_reflection_residual']<5e-15
        assert b['Omega_reflection_residual']<5e-15
        c=certify_local_coframe_disk(p,t,L/16)
        assert c['classification']=='CERTIFIED_EXACT_STORED_LOCAL_AFFINE_COFRAME_ANALYTIC_DISK'
        assert not c['physical_continuum_solution_or_global_contour_certified']


def test_complex_weight_square_contact_keeps_reflected_numerator_and_both_orders():
    from bhsm.interface.muon_continued_current_boundary_heat import rectangular_midpoint_matrix
    rng=np.random.default_rng(123);w=np.array([.1+.002j,.12-.001j,.11+.001j])
    H=rng.normal(size=(3,2,2))+1j*rng.normal(size=(3,2,2))
    Hs=H*.8;T=rng.normal(size=(3,3,3))+1j*rng.normal(size=(3,3,3));Ts=T*.9
    s=local_formal_reflected_square(w,H,Hs,rotation=np.exp(.3j))
    t=local_formal_reflected_square(w,T,Ts,rotation=np.exp(.3j))
    forward=rectangular_midpoint_matrix(rng.normal(size=(3,3,2))+1j*rng.normal(size=(3,3,2)))
    # The reverse reflected branch is deliberately independent here; the
    # algebra must cancel it without silently replacing it by forward†.
    bar_reverse=rectangular_midpoint_matrix(rng.normal(size=(3,2,3))+1j*rng.normal(size=(3,2,3)))
    R=rng.normal(size=(6,2));out=formal_square_magnetic_application(s,t,R,forward,bar_reverse)
    assert out['c0_inverse_contact_identity_max']<2e-15
    assert np.max(abs(out['original_right_rows']))<2e-14
    assert np.max(abs(out['original_form_rows']))<2e-14
    assert np.linalg.norm(out['delta_numerator'])>.1
