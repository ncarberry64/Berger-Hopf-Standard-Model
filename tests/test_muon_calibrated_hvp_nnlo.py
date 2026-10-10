from pathlib import Path
import json
import math

import numpy as np
import pytest

from bhsm.interface.muon_calibrated_hvp_spectral import load_alphaqed26_spectrum
from bhsm.interface.muon_calibrated_hvp_nnlo import (
    COEFFICIENT_PATH,retained_nnlo_coefficients,next_to_next_to_leading_hvp_pauli,
)
import bhsm.interface.muon_calibrated_hvp_nnlo as nnlo

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def inputs():
    config=json.loads((ROOT/'artifacts/muon_calibrated_pauli_20261009/inputs.json').read_text())
    return (load_alphaqed26_spectrum(ROOT/'artifacts/muon_calibrated_hvp_spectral_20261010/input'),
            1/config['primary_measurements']['alpha_inverse_0']['value'],
            config['selected_consumer_values']['m_mu_GeV']['value'],
            config['selected_consumer_values']['m_e_GeV']['value'])


def test_primary_exact_coefficient_values_and_identity_guard(tmp_path):
    coefficients=retained_nnlo_coefficients(.005)
    assert coefficients['6a']['j'][1] == -3793/864
    assert coefficients['6a']['g'][0] == pytest.approx(1301/144-19*math.pi**2/9,rel=1e-15)
    assert coefficients['6bll']['j'][1] == pytest.approx(4/27-9*.005**2/2,rel=1e-15)
    altered=tmp_path/'changed.json';altered.write_bytes(COEFFICIENT_PATH.read_bytes()+b' ')
    with pytest.raises(ValueError,match='identity'):
        retained_nnlo_coefficients(.005,path=altered)


def test_all_eight_classes_scale_as_alpha_fourth_power_and_share_covariance(inputs):
    original=next_to_next_to_leading_hvp_pauli(*inputs,order=12,spectral_order=8,double_order=8)
    args=list(inputs);args[1]*=1.02
    changed=next_to_next_to_leading_hvp_pauli(*args,order=12,spectral_order=8,double_order=8)
    assert len(original['classes']) == 8
    for name,row in original['classes'].items():
        assert changed['classes'][name]['value'] == pytest.approx(row['value']*1.02**4,rel=2e-12)
    shared=np.sum([row['systematic_error_vector'] for row in original['classes'].values()],axis=0)
    assert original['NNLO_HVP']['systematic_error'] == pytest.approx(np.linalg.norm(shared),rel=1e-15)
    assert original['kernel_approximation_error_estimate'] > 0
    assert original['omitted_tau_NNLO_error_estimate'] > 0
    assert original['complete_native_remainder'] is False


def test_endpoint_and_triangular_double_integral_refinement(inputs):
    coarse=next_to_next_to_leading_hvp_pauli(*inputs,order=24,spectral_order=8,double_order=12,endpoint_v=32)
    fine=next_to_next_to_leading_hvp_pauli(*inputs,order=32,spectral_order=12,double_order=24,endpoint_v=40)
    assert abs(fine['NNLO_HVP']['value']-coarse['NNLO_HVP']['value']) < 2e-15
    assert abs(fine['classes']['6c2']['value']-coarse['classes']['6c2']['value']) < 2e-15
    assert fine['NNLO_HVP']['value'] > 0


def test_different_line_measure_and_two_source_variations(monkeypatch):
    # An independent constant test function checks the triangular Jacobian
    # and both variations. It is not supplied as a physical correlator.
    h=.004;st=.0002;sy=.0003;a=.0073
    monkeypatch.setattr(nnlo,'delta_alpha_had_spacelike',lambda *args,**kwargs:
        dict(value=h,statistical_error_vector=[st],systematic_error_vector=[sy],undressing_error_estimate=0.))
    row=nnlo._different_line_double_hvp(None,a,.1,order=32,spectral_order=8)
    A=1855-188*math.pi**2;B=988*math.pi**2-9765;C=24*(435-44*math.pi**2)
    moment=(a/math.pi)**2/(2*(32*math.pi**2-315))*(A/2+B/3+C/4)
    assert row['value'] == pytest.approx(moment*h*h,rel=2e-12)
    assert row['statistical_error_vector'][0] == pytest.approx(moment*2*h*st,rel=2e-12)


@pytest.mark.parametrize('ratio',[None,0.,-1.,math.nan,math.inf])
def test_no_invalid_mass_ratio(ratio):
    with pytest.raises(ValueError):
        retained_nnlo_coefficients(ratio)
