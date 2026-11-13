import warnings
import numpy as np
from scipy.integrate import IntegrationWarning
from bhsm.interface.muon_calibrated_local_pauli import (
    one_loop_pauli_spacelike,signed_soft_transfer_application,
    local_spin_pole_application,universal_two_loop_coefficient,
    lepton_vacuum_polarization_pauli,calibrated_local_qed_two_loop,
    fixed_yukawa_higgs_pauli,
)


def test_actual_on_shell_pole_and_descriptor():
    for spin in (-1,1):
        a=local_spin_pole_application(.105658, .03,spin=spin)
        assert a['pole_residual']<2e-16
        assert a['LSZ_descriptor_residual']<3e-15
        assert abs(a['energy_GeV']-a['analytic_energy_GeV'])<3e-16
        assert a['action_selected'] is False
        assert a['full_spin_degeneracy']==2


def test_signed_transfer_and_direction_agreement_with_rigorous_soft_bias():
    alpha=1/137.036
    for u in np.eye(3):
        for t in (-.01,-.001,.001,.01):
            a=signed_soft_transfer_application(alpha=alpha,mass_GeV=.105658,t=t,direction=u)
            assert a['absolute_limit_difference']<=a['soft_bias_bound']+3e-17
            assert a['Dirac_annihilation_residual']==0
            assert a['Pauli_unit_pairing_residual']<2e-15
            assert a['form_factor_projection_residual']<8e-16
            assert a['physical_native_promotion'] is False


def test_pauli_integral_zero_and_monotonic_transfer():
    a=one_loop_pauli_spacelike(alpha=.0073,Q_squared_over_m_squared=0)
    b=one_loop_pauli_spacelike(alpha=.0073,Q_squared_over_m_squared=1)
    assert a['F2']==.0073/(2*np.pi)
    assert b['F2']<a['F2']


def test_finite_spacelike_pauli_integral_matches_closed_on_shell_result():
    # Eq.(33)-(34), PhysRevD108.096036, with rho=-k²/m² and x=su,
    # y=s(1-u).  The resulting u integral has this elementary exact form.
    alpha=.0073
    for rho in (1e-6,1.,1e6):
        a=one_loop_pauli_spacelike(alpha=alpha,Q_squared_over_m_squared=rho)
        closed=alpha/(2*np.pi)*4*np.arcsinh(np.sqrt(rho)/2)/np.sqrt(rho*(rho+4))
        assert abs(a['F2']-closed)<max(a['quadrature_error_estimate'],2e-18)


def test_universal_exact_coefficient():
    assert abs(universal_two_loop_coefficient()+.328478965579193)<3e-15


def test_vp_integral_recovers_known_same_mass_and_decoupling():
    a=lepton_vacuum_polarization_pauli(1.)
    assert abs(a['coefficient']-(119/36-np.pi**2/3))<3e-14
    small=lepton_vacuum_polarization_pauli(.001)
    assert abs(small['coefficient']/(.001**2/45)-1)<3e-5


def test_vp_source_derivative_is_actual_integral_derivative():
    r=206.76838;eps=1e-4
    a=lepton_vacuum_polarization_pauli(r)
    fd=(lepton_vacuum_polarization_pauli(r*np.exp(eps))['coefficient']-
        lepton_vacuum_polarization_pauli(r*np.exp(-eps))['coefficient'])/(2*eps)
    assert abs(fd-a['derivative_log_mass_ratio'])<2e-10


def test_vp_requested_mass_ratios_refine_without_nested_roundoff_warnings():
    # Independent 60- and 90-digit quadrature of the exact VP antiderivative,
    # using 180 beta-series terms near k=0, agreed on these decimal inputs.
    references=(
        (206.76838,1.09425846096206569879542957752416292756,
         .32216792455357417070836605624555980370),
        (.05946,.00007806657564042048940120803188548589,
         .00015530916935875603890739887988835428),
    )
    with warnings.catch_warnings():
        warnings.simplefilter('error',IntegrationWarning)
        for ratio,coefficient,derivative in references:
            ordinary=lepton_vacuum_polarization_pauli(ratio)
            refined=lepton_vacuum_polarization_pauli(ratio,eps=2e-13)
            for key,error_key,reference in (
                ('coefficient','quadrature_error_estimate',coefficient),
                ('derivative_log_mass_ratio','derivative_error_estimate',derivative),
            ):
                assert abs(refined[key]-reference)<2e-15
                assert abs(ordinary[key]-refined[key])<ordinary[error_key]+refined[error_key]
            assert refined['rigorous_quadrature_enclosure'] is False
            assert 'roundoff is not enclosed' in refined['error_scope']
            assert refined['integrated_series_truncation_bound']<2e-23
            assert refined['integrated_derivative_series_truncation_bound']<2e-21


def test_accounting_keeps_missing_native_and_higher_orders_open():
    a=calibrated_local_qed_two_loop(alpha=1/137.036,
        muon_electron_ratio=206.76838,muon_tau_ratio=.05946)
    assert abs(a['a_mu_local_QED_through_two_loops']-sum(a['contributions'].values()))<1e-18
    assert a['full_a_mu'] is None and a['native_remainder'] is None
    assert a['perturbative_truncation_bound'] is None
    assert a['measured_anomaly_used'] is False


def test_fixed_yukawa_scalar_loop_retains_pole_coupling_distinction():
    a=fixed_yukawa_higgs_pauli(muon_mass_GeV=.10565842526040435,higgs_mass_GeV=125.11)
    assert a['independent_Y_mu_fitted'] is False
    assert a['radial_scalar_coupling']!=.10565842526040435/246.21979929677656
    assert 2e-14<a['a_mu_local_radial_Higgs_one_loop']<2.3e-14
    assert a['asymptotic_difference']<2e-19


def test_scalar_loop_input_gradient_agrees_with_mass_motion():
    m,mh=.10565842526040435,125.11;eps=1e-4
    a=fixed_yukawa_higgs_pauli(muon_mass_GeV=m,higgs_mass_GeV=mh)
    f=lambda mm,hh:fixed_yukawa_higgs_pauli(muon_mass_GeV=mm,higgs_mass_GeV=hh)['a_mu_local_radial_Higgs_one_loop']
    dm=(f(m*np.exp(eps),mh)-f(m*np.exp(-eps),mh))/(2*eps)
    dh=(f(m,mh*np.exp(eps))-f(m,mh*np.exp(-eps)))/(2*eps)
    np.testing.assert_allclose(dm,a['derivative_log_muon_mass'],rtol=2e-8,atol=1e-22)
    np.testing.assert_allclose(dh,a['derivative_log_higgs_mass'],rtol=2e-8,atol=1e-22)
