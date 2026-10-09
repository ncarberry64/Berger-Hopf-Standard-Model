import math

import pytest

from bhsm.interface.muon_calibrated_decay_matching import calibrated_muon_decay_one_loop


ALPHA = 1/137.035999206
RATIO = 206.76838
REFERENCE = .99561554934729


def test_selected_input_massless_inclusive_coefficient_and_reference_scope():
    result = calibrated_muon_decay_one_loop(
        alpha_0=ALPHA, muon_electron_ratio=RATIO, reference_decay_factor=REFERENCE)
    assert abs(result['tree_phase_space']-.9998129493472899)<2e-16
    assert -4210e-6<result['delta_q1_massless_alpha_0']<-4200e-6
    comparison = result['reference_comparison']
    assert 29e-6<comparison['massless_alpha_0_delta_q1_minus_rounded_MuLan']<31e-6
    assert comparison['reference_decay_factor']==REFERENCE
    assert comparison['comparison_is_rounding_only'] is False
    assert 'alpha_e(m_mu)' in comparison['reference_one_loop_scope']
    assert result['complete_decay_factor'] is None
    assert result['finite_electron_mass_one_loop_remainder'] is None
    assert result['native_lifetime_correction'] is None
    assert result['complete_GF_matching'] is False
    assert result['input_configuration_changed'] is False


def test_muon_decay_additive_rate_normalization_and_massless_limit():
    result = calibrated_muon_decay_one_loop(alpha_0=ALPHA, muon_electron_ratio=RATIO)
    assert result['partial_decay_factor_tree_plus_massless_one_loop']==(
        result['tree_phase_space']+result['delta_q1_massless_alpha_0'])
    # Multiplying the massless one-loop factor by F inserts an unspecified
    # finite-mass O(alpha) term and differs from the published additive ledger.
    product = result['tree_phase_space']*(1+result['delta_q1_massless_alpha_0'])
    assert abs(product-result['partial_decay_factor_tree_plus_massless_one_loop'])>7e-7
    limit = calibrated_muon_decay_one_loop(alpha_0=ALPHA, muon_electron_ratio=1e10)
    assert limit['tree_phase_space']==1
    assert abs(limit['delta_q1_massless_alpha_0']-ALPHA/(2*math.pi)*(25/4-math.pi**2))<1e-18


def test_selected_charge_and_mass_ratio_sensitivity_by_independent_perturbation():
    result = calibrated_muon_decay_one_loop(alpha_0=ALPHA, muon_electron_ratio=RATIO)
    step = 1e-4
    plus = calibrated_muon_decay_one_loop(alpha_0=ALPHA, muon_electron_ratio=RATIO*math.exp(step))
    minus = calibrated_muon_decay_one_loop(alpha_0=ALPHA, muon_electron_ratio=RATIO*math.exp(-step))
    derivative = (plus['partial_decay_factor_tree_plus_massless_one_loop']-
                  minus['partial_decay_factor_tree_plus_massless_one_loop'])/(2*step)
    assert abs(derivative-result['derivative_log_muon_electron_ratio'])<4e-12
    plus = calibrated_muon_decay_one_loop(alpha_0=ALPHA+1e-6, muon_electron_ratio=RATIO)
    minus = calibrated_muon_decay_one_loop(alpha_0=ALPHA-1e-6, muon_electron_ratio=RATIO)
    derivative = (plus['partial_decay_factor_tree_plus_massless_one_loop']-
                  minus['partial_decay_factor_tree_plus_massless_one_loop'])/2e-6
    assert abs(derivative-result['derivative_alpha_0'])<5e-11


@pytest.mark.parametrize('value',[None,True,0,-1,math.inf,math.nan])
def test_rejects_missing_or_nonphysical_charge(value):
    with pytest.raises(ValueError):
        calibrated_muon_decay_one_loop(alpha_0=value, muon_electron_ratio=RATIO)


@pytest.mark.parametrize('value',[None,True,0,.5,1,math.inf,math.nan])
def test_rejects_missing_or_nondecaying_mass_ratio(value):
    with pytest.raises(ValueError):
        calibrated_muon_decay_one_loop(alpha_0=ALPHA, muon_electron_ratio=value)
