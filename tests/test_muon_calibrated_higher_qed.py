"""Exact references and numerical local contractions; no native promotion."""
import math
import numpy as np
import pytest
from scipy.integrate import quad
from bhsm.interface.muon_calibrated_higher_qed import (
    ELECTRON_RATIO_REFERENCE,TAU_RATIO_REFERENCE,_vp,
    calibrated_higher_qed,mixed_three_loop_vp,universal_three_loop_coefficient,
    leading_electroweak_pauli,higgs_photon_barr_zee_kernel,
    fixed_yukawa_lepton_barr_zee_photon,higgs_z_barr_zee_kernel,
    fixed_yukawa_lepton_barr_zee_z,
)


def test_three_loop_exact_universal_reference():
    assert universal_three_loop_coefficient()==pytest.approx(1.181241456587200,abs=2e-15)


@pytest.mark.parametrize('k',[.001,.99,1.,1.01,100.,1e6])
def test_subtracted_bubble_against_independent_parameter_integral(k):
    actual=2*quad(lambda y:y*(1-y)*math.log1p(k*y*(1-y)),0,1,epsabs=1e-13,epsrel=1e-13,limit=250)[0]
    assert _vp(k)==pytest.approx(actual,rel=2e-12,abs=1e-13)


def test_mixed_two_bubbles_factor_and_exchange_symmetry():
    # CONTROL_ONLY ratios: independent nested integral tests the permutation2.
    def bubble(r,x):
        return 2*quad(lambda y:y*(1-y)*math.log1p(r*r*x*x*y*(1-y)/(1-x)),0,1)[0]
    expected=2*quad(lambda x:(1-x)*bubble(.3,x)*bubble(.7,x),0,1,epsabs=1e-12)[0]
    result=mixed_three_loop_vp(.3,.7)
    assert result['coefficient']==pytest.approx(expected,rel=1e-8,abs=1e-12)
    assert mixed_three_loop_vp(.7,.3)['coefficient']==pytest.approx(result['coefficient'],rel=2e-12)


def test_reference_c3_includes_actual_mixed_integral_once():
    result=calibrated_higher_qed(alpha=1/137.035999206,
        muon_electron_ratio=ELECTRON_RATIO_REFERENCE,muon_tau_ratio=TAU_RATIO_REFERENCE)
    assert result['coefficients']['C3']==pytest.approx(24.05050996,abs=1e-8)
    assert result['C3_masspoint_updates']['electron']==0
    assert result['C3_masspoint_updates']['tau']==0
    assert result['coefficients']['C5']==pytest.approx(750.1524,abs=1e-10)


def test_selected_mass_derivative_and_alpha_power_counting():
    args=dict(alpha=1/137.035999206,muon_electron_ratio=206.76838,muon_tau_ratio=.10565842526040435/1.77709)
    out=calibrated_higher_qed(**args)
    eps=2e-6
    for key,derivative in [('muon_electron_ratio','derivative_log_muon_electron_ratio'),
                           ('muon_tau_ratio','derivative_log_muon_tau_ratio')]:
        lo=args|{key:args[key]*math.exp(-eps)};hi=args|{key:args[key]*math.exp(eps)}
        finite=(calibrated_higher_qed(**hi)['increment']-calibrated_higher_qed(**lo)['increment'])/(2*eps)
        assert finite==pytest.approx(out[derivative],rel=2e-7,abs=2e-17)
    doubled=calibrated_higher_qed(**(args|{'alpha':2*args['alpha']}))
    for n in (3,4,5):
        key=f'local_leptonic_QED_{n}_loop'
        assert doubled['contributions'][key]==pytest.approx(2**n*out['contributions'][key],rel=2e-15)
    assert not out['old_two_loop_subtotal_included']
    assert not out['complete_observable'] and not out['action_selected']
    assert out['native_remainder'] is None
    assert out['errors']['all_orders_remainder_enclosure'] is None


@pytest.mark.parametrize('updates',[{'alpha':0},{'alpha':float('nan')},{'muon_electron_ratio':1},
    {'muon_tau_ratio':.5}])
def test_invalid_or_outside_reference_masspoint_rejected(updates):
    args=dict(alpha=.0073,muon_electron_ratio=206.76838,muon_tau_ratio=.059456)
    with pytest.raises(ValueError):calibrated_higher_qed(**(args|updates))


def test_leading_weak_normalization_and_masses_have_correct_derivatives():
    args=dict(fermi_constant_GeV_inverse_squared=1.1663787e-5,muon_mass_GeV=.1056583715,
        w_mass_GeV=80.363,z_mass_GeV=91.1876)
    out=leading_electroweak_pauli(**args)
    assert out['a_mu_leading_EW']==pytest.approx(194.80e-11,abs=.01e-11)
    for key,label in [('w_mass_GeV','w_mass'),('z_mass_GeV','z_mass')]:
        h=1e-4
        derivative=(leading_electroweak_pauli(**(args|{key:args[key]+h}))['a_mu_leading_EW']
            -leading_electroweak_pauli(**(args|{key:args[key]-h}))['a_mu_leading_EW'])/(2*h)
        assert derivative==pytest.approx(out['derivatives'][label],rel=1e-7,abs=1e-21)
    assert not out['radial_Higgs_one_loop_included'] and not out['full_EW_evaluated']


def test_scalar_barr_zee_kernel_removable_root_and_heavy_limit_sign():
    assert higgs_photon_barr_zee_kernel(.25)['value']<0
    assert higgs_photon_barr_zee_kernel(.2499999)['value']==pytest.approx(
        higgs_photon_barr_zee_kernel(.2500001)['value'],rel=2e-6)
    x=100.
    # Independent leading heavy-mass integral: denominator x-u -> x.
    asymptotic=quad(lambda w:(1-2*w*(1-w))*math.log(w*(1-w)/x),0,1)[0]
    assert higgs_photon_barr_zee_kernel(x)['value']==pytest.approx(asymptotic,rel=.003)


def test_literal_fixed_y_lepton_barr_zee_is_not_whole_weak_total():
    out=fixed_yukawa_lepton_barr_zee_photon(alpha=.0072973525627871355,
        muon_mass_GeV=.10565842526040435,higgs_mass_GeV=125.11,
        lepton_masses_GeV=[1.77709,.10565842526040435,.000510998950905377])
    assert len(out['contributions'])==3
    assert all(row['a_mu']<0 for row in out['contributions'])
    assert out['a_mu_Hgamma_charged_leptons']==pytest.approx(
        math.fsum(row['a_mu'] for row in out['contributions']),rel=1e-15)
    assert not out['quark_Hgamma_included'] and not out['HZ_included']
    assert not out['whole_EW_evaluated']


def test_hz_kernel_equal_mass_and_photon_limit():
    x=.3
    equal=higgs_z_barr_zee_kernel(x,x)['value']
    nearby=higgs_z_barr_zee_kernel(x,x*(1+1e-5))['value']
    assert equal<0 and nearby==pytest.approx(equal,rel=2e-5)
    assert higgs_z_barr_zee_kernel(x,1e8)['value']==pytest.approx(
        higgs_photon_barr_zee_kernel(x)['value'],rel=1e-6)


def test_literal_fixed_y_hz_lepton_terms_suppressed_but_not_zero_filled():
    out=fixed_yukawa_lepton_barr_zee_z(alpha=.0072973525627871355,
        muon_mass_GeV=.10565842526040435,higgs_mass_GeV=125.11,
        lepton_masses_GeV=[1.77709,.10565842526040435,.000510998950905377],
        w_mass_GeV=80.3602,z_mass_GeV=91.1876)
    assert -1e-15<out['a_mu_HZ_charged_leptons']<0
    assert not out['quark_HZ_included'] and not out['whole_EW_evaluated']
