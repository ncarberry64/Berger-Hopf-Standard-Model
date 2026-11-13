"""Checks of the new same-spectrum NLO projections, without anomaly inputs."""
from pathlib import Path
import json
import math

import numpy as np
import pytest
from scipy.integrate import quad

from bhsm.interface.muon_calibrated_hvp_spectral import load_alphaqed26_spectrum
from bhsm.interface.muon_calibrated_hvp_higher import (
    next_to_leading_hvp_pauli, nlo_photonic_kernel_log_endpoint,
    one_loop_lepton_delta_alpha,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def inputs():
    config = json.loads((ROOT/'artifacts/muon_calibrated_pauli_20261009/inputs.json').read_text())
    spectrum = load_alphaqed26_spectrum(ROOT/'artifacts/muon_calibrated_hvp_spectral_20261010/input')
    return (spectrum, 1/config['primary_measurements']['alpha_inverse_0']['value'],
            config['selected_consumer_values']['m_mu_GeV']['value'],
            config['selected_consumer_values']['m_e_GeV']['value'],
            config['primary_measurements']['tau_mass']['value'])


@pytest.mark.parametrize('k',[0.,1e-7,.9,1.,1e5,1e12])
def test_lepton_vp_against_independent_parameter_integral(k):
    a=.0073
    actual=one_loop_lepton_delta_alpha(k,1.,a)
    independent=2*a/math.pi*quad(lambda y:y*(1-y)*math.log1p(k*y*(1-y)),0,1,
                              epsabs=2e-13,epsrel=2e-13)[0]
    assert actual == pytest.approx(independent,rel=4e-12,abs=1e-18)


def test_exact_kernel_high_precision_endpoint():
    actual=nlo_photonic_kernel_log_endpoint(32)
    assert actual == nlo_photonic_kernel_log_endpoint(32,decimal_precision=110)
    assert actual == pytest.approx(-23/18,abs=3e-13)
    with pytest.raises(ValueError,match='precision'):
        nlo_photonic_kernel_log_endpoint(32,decimal_precision=40)


def test_each_nlo_class_has_alpha_cubed_normalization(inputs):
    original=next_to_leading_hvp_pauli(*inputs,order=8,spectral_order=8)
    changed=list(inputs);changed[1]*=1.03
    scaled=next_to_leading_hvp_pauli(*changed,order=8,spectral_order=8)
    for name in original['classes']:
        assert scaled['classes'][name]['value'] == pytest.approx(original['classes'][name]['value']*1.03**3,rel=3e-14)
    # The shared vector sum, rather than independent class variances, is used.
    shared=np.sum([row['statistical_error_vector'] for row in original['classes'].values()],axis=0)
    assert original['NLO_HVP']['statistical_error'] == pytest.approx(np.linalg.norm(shared),rel=1e-15)
    assert original['complete_native_remainder'] is False
    assert original['overlap']['muon_VP'].startswith('in 4a')


def test_outer_and_endpoint_refinement(inputs):
    coarse=next_to_leading_hvp_pauli(*inputs,order=16,spectral_order=8,endpoint_v=32)
    fine=next_to_leading_hvp_pauli(*inputs,order=32,spectral_order=12,endpoint_v=40)
    assert abs(coarse['NLO_HVP']['value']-fine['NLO_HVP']['value']) < 1e-18
    assert fine['classes']['4a_photonic_and_muon_VP']['value'] < 0
    assert fine['classes']['4b_electron_tau_VP']['value'] > 0
    assert fine['classes']['4c_double_hadronic_VP']['value'] > 0
    assert fine['numerical_endpoint_remainder_enclosure'] is None


@pytest.mark.parametrize('value',[0.,-1.,math.nan,math.inf])
def test_reject_invalid_physical_normalization(inputs,value):
    args=list(inputs);args[1]=value
    with pytest.raises(ValueError):
        next_to_leading_hvp_pauli(*args,order=8)
