import numpy as np
import pytest

from bhsm.interface.muon_calibrated_matching import (
    calibrated_tree_matching, chiral_pole_denominator_application,
    higgs_scalar_action_unit_conversion, local_calibrated_higgs_radial_newton,
)


# Selected primary-input central arithmetic, not a stationary BHSM state.
VALUES = np.array([1.16637729304358539e-5, 125.11, 1.77709,
                   .105658425260404350, .000510998950905377070])


def application(x=VALUES, covariance=None):
    return calibrated_tree_matching(
        fermi_constant_GeV_inverse_squared=x[0], higgs_mass_GeV=x[1],
        pole_masses_GeV=x[2:], input_covariance=covariance)


def test_tree_matching_obeys_literal_scalar_and_fixed_family_normalization():
    a = application()
    v, nu2, lam = a['v_GeV'], a['nu_squared_GeV_squared'], a['lambda_H']
    assert v*v == pytest.approx(1/(np.sqrt(2)*VALUES[0]))
    assert 2*nu2 == pytest.approx(v*v)
    assert 2*lam*v*v == pytest.approx(VALUES[1]**2)
    y = np.array([r['fixed_yukawa'] for r in a['family_rows']])
    tree = np.array([r['tree_mass_GeV'] for r in a['family_rows']])
    assert np.allclose(tree, v*y/np.sqrt(2), rtol=1e-15)
    assert [r['family'] for r in a['family_rows']] == ['tau', 'muon', 'electron']
    assert a['family_rows'][0]['required_relative_pole_shift'] > .01
    assert -.0003 < a['family_rows'][1]['required_relative_pole_shift'] < -.0002
    assert a['family_rows'][2]['required_relative_pole_shift'] < -.022


def test_common_scale_cannot_repair_fixed_mass_ratios():
    a = application()
    x = VALUES.copy()
    x[0] *= 4  # Computational comparison of the common scale only.
    b = application(x)
    assert a['ratio_rows'] == b['ratio_rows']
    assert a['ratio_rows'][1]['fixed_yukawa_ratio'] == pytest.approx(202.0729113420439)
    assert a['ratio_rows'][1]['measured_pole_ratio'] == pytest.approx(206.76838)
    assert a['ratio_rows'][1]['relative_ratio_discrepancy'] > .023
    assert len({r['v_required_with_unmodified_tree_kinetics_GeV']
                for r in a['family_rows']}) == 3
    assert not a['common_scale_matches_all_supplied_central_mass_ratios']
    x = VALUES.copy()
    x[2:] = [r['tree_mass_GeV'] for r in a['family_rows']]
    assert application(x)['common_scale_matches_all_supplied_central_mass_ratios']


def test_analytic_uncertainty_jacobian_against_independent_input_perturbations():
    a = application()
    jac = np.array(a['input_jacobian'])
    for j in range(len(VALUES)):
        step = VALUES[j]*2e-5
        plus, minus = VALUES.copy(), VALUES.copy()
        plus[j] += step
        minus[j] -= step
        fd = (np.array(application(plus)['output_values'])-
              np.array(application(minus)['output_values']))/(2*step)
        assert np.allclose(fd, jac[:, j], rtol=2e-8, atol=1e-9)


def test_lifetime_mass_correlation_is_not_independent_twice():
    # Fixed-lifetime leading dependence G_F proportional to m_mu^-5/2.
    # Its fluctuation is therefore correlated with the pole mass input.
    direction = np.zeros(5)
    sigma_mu = VALUES[3]*8e-7
    direction[0] = -2.5*VALUES[0]/VALUES[3]*sigma_mu
    direction[3] = sigma_mu
    covariance = np.outer(direction, direction)
    a = application(covariance=covariance)
    factors = np.array([r['required_pole_factor'] for r in a['family_rows']])
    sigma = np.array(a['output_standard_uncertainties'])
    assert sigma[10] == pytest.approx(.25*factors[1]*sigma_mu/VALUES[3], rel=2e-14)
    assert np.allclose(np.array(a['output_covariance']),
                       np.array(a['input_jacobian'])@covariance@np.array(a['input_jacobian']).T)


def test_mass_matching_does_not_determine_pole_slope_or_lsz_residue():
    mass = VALUES[3]
    common = dict(pole_mass_GeV=mass, A_left=1., A_right=1.,
                  B_left_GeV=mass, B_right_GeV=mass)
    a = chiral_pole_denominator_application(**common)
    b = chiral_pole_denominator_application(**common,
        dA_left_dp_squared=3., dA_right_dp_squared=2.,
        dB_left_dp_squared=.1, dB_right_dp_squared=.2)
    assert a['scalar_denominator_GeV_squared'] == 0
    assert b['scalar_denominator_GeV_squared'] == 0
    assert a['derivative_with_respect_to_p_squared'] is None
    expected = 1+mass**2*5-.3*mass
    assert b['derivative_with_respect_to_p_squared'] == pytest.approx(expected)
    assert not b['physical_lsz_residue_evaluated']


def test_pole_denominator_derivative_keeps_masslike_and_both_kinetic_contacts():
    mass, al, ar, bl, br = .2, 1.2, .9, .18, .24
    da, db, dc, dd = .7, -.2, .3, -.1
    a = chiral_pole_denominator_application(pole_mass_GeV=mass,
        A_left=al,A_right=ar,B_left_GeV=bl,B_right_GeV=br,
        dA_left_dp_squared=da,dA_right_dp_squared=db,
        dB_left_dp_squared=dc,dB_right_dp_squared=dd)
    s = mass*mass
    def denominator(t):
        return t*(al+da*(t-s))*(ar+db*(t-s))-(bl+dc*(t-s))*(br+dd*(t-s))
    eps = 1e-5
    fd = (denominator(s+eps)-denominator(s-eps))/(2*eps)
    assert a['derivative_with_respect_to_p_squared'] == pytest.approx(fd, rel=1e-9)
    assert a['scalar_denominator_GeV_squared'] == pytest.approx(denominator(s))


def test_canonical_action_dimension_conversion_does_not_choose_native_length():
    nu2, unit = application()['nu_squared_GeV_squared'], 1000.
    a = higgs_scalar_action_unit_conversion(nu_squared_GeV_squared=nu2,
                                          energy_unit_GeV=unit)
    assert a['nu_squared_chart']*unit**2 == pytest.approx(nu2)
    # R_phys=R_chart/E, D_t H_phys=E^2 D_t H_chart gives p_phys=p_chart/E.
    r, dh = 1.3, .7
    assert (r/unit)**3*(dh*unit**2) == pytest.approx(r**3*dh/unit)
    assert a['lambda_H_unchanged']
    assert not a['native_cutoff_assigned']


def test_no_covariance_does_not_claim_zero_or_complete_prediction_uncertainty():
    a = application()
    assert a['output_standard_uncertainties'] is None
    for key in ('full_prediction_uncertainty_established','independent_yukawas_introduced',
                'required_corrections_fitted','mass_input_assigns_residue',
                'action_selected','Gate7_closed','stationary_base_solved',
                'native_cutoff_assigned','muon_anomaly_calibration_used',
                'full_native_pauli_evaluated'):
        assert not a[key]


def test_rejects_wrong_units_shapes_and_non_covariances():
    with pytest.raises(ValueError):
        application(np.array([-VALUES[0], *VALUES[1:]]))
    with pytest.raises(ValueError):
        application(covariance=np.eye(4))
    c = np.eye(5); c[2, 3] = .3
    with pytest.raises(ValueError):
        application(covariance=c)
    c = np.eye(5); c[1, 1] = -1
    with pytest.raises(ValueError):
        application(covariance=c)
    with pytest.raises(ValueError):
        chiral_pole_denominator_application(pole_mass_GeV=1,A_left=1,A_right=1,
            B_left_GeV=1,B_right_GeV=1,dA_left_dp_squared=1)


def test_local_tree_radial_newton_executes_residual_corrections_and_canonical_mass():
    a = local_calibrated_higgs_radial_newton(
        fermi_constant_GeV_inverse_squared=VALUES[0], higgs_mass_GeV=VALUES[1])
    tree = application()
    assert a['converged']
    assert len(a['history']) >= 3
    assert a['initial_weak_residual_GeV_cubed'] != 0
    assert a['history'][0]['accepted_correction_GeV'] != 0
    assert abs(a['final_weak_residual_GeV_cubed']) < abs(a['initial_weak_residual_GeV_cubed'])*1e-10
    for row in a['history']:
        assert abs(row['updated_residual_GeV_cubed']) < abs(row['initial_residual_GeV_cubed'])
        assert row['radial_h_after_GeV']-row['radial_h_before_GeV'] == pytest.approx(
            row['accepted_correction_GeV'], abs=2e-14)
    assert a['local_radial_h_GeV'] == pytest.approx(tree['v_GeV'], rel=1e-13)
    assert a['local_neutral_amplitude_GeV']**2 == pytest.approx(tree['nu_squared_GeV_squared'], rel=1e-13)
    assert a['potential_radial_curvature_GeV_squared'] == pytest.approx(VALUES[1]**2, rel=1e-12)
    assert a['final_weak_radial_jacobian_GeV_squared'] == pytest.approx(-VALUES[1]**2, rel=1e-12)
    # This is a local matched vacuum calculation; no E1 Cauchy data are selected.
    assert a['classification'] == 'CALIBRATED_TREE_LOCAL_BROKEN_VACUUM_ONLY'
    for key in ('current_E1_stationary_base_solved','physical_retarded_boundary_conditions_selected',
                'quantum_effects_deleted','mechanical_formation_section_selected',
                'native_cutoff_assigned','full_native_pauli_evaluated'):
        assert not a[key]


def test_local_radial_curvature_agrees_with_independent_potential_second_difference():
    a = local_calibrated_higgs_radial_newton(
        fermi_constant_GeV_inverse_squared=VALUES[0], higgs_mass_GeV=VALUES[1],
        initial_fraction=1.2)
    h, lam, nu2 = a['local_radial_h_GeV'], a['lambda_H'], a['nu_squared_GeV_squared']
    def potential(t):
        return lam*(t*t/2-nu2)**2
    eps = .01
    curvature = (potential(h+eps)+potential(h-eps)-2*potential(h))/eps**2
    assert curvature == pytest.approx(a['potential_radial_curvature_GeV_squared'], rel=2e-9)
    with pytest.raises(ValueError):
        local_calibrated_higgs_radial_newton(fermi_constant_GeV_inverse_squared=VALUES[0],
            higgs_mass_GeV=VALUES[1],initial_fraction=.2)
