import numpy as np
import pytest
from bhsm.interface.muon_paired_local_vp_pauli import certified_vp_coefficient,paired_local_vp_pauli,signed_soft_overlap_enclosure
from bhsm.interface.muon_calibrated_local_pauli import lepton_vacuum_polarization_pauli


@pytest.fixture(scope='module')
def physical():
    return paired_local_vp_pauli(alpha_inverse_decimal='137.035999206',mass_ratio_decimal='206.76838',
        precision_bits=160,collar_bits=32,quadrature_bits=55)


def test_independent_continuum_and_mass_derivative(physical):
    reference=lepton_vacuum_polarization_pauli(206.76838,eps=1e-12)
    actual=physical['electron_integral']
    for key,ref,error in [('coefficient_interval',reference['coefficient'],reference['quadrature_error_estimate']),
        ('derivative_log_mass_ratio_interval',reference['derivative_log_mass_ratio'],reference['derivative_error_estimate'])]:
        lo,hi=actual[key]
        assert lo-error<=ref<=hi+error
    assert physical['paired_muon_minus_electron_interval'][1]<0
    assert physical['frozen_own_VP_already_in_A1']
    assert not physical['native_boundary_form_overlap_subtracted']


def test_signed_soft_normalization_and_limit(physical):
    minus=signed_soft_overlap_enclosure(physical,-.01)
    plus=signed_soft_overlap_enclosure(physical,.01)
    closer=signed_soft_overlap_enclosure(physical,.003)
    assert minus['normalized_signed_derivative_interval']==plus['normalized_signed_derivative_interval']
    assert closer['paired_soft_bias_upper']<plus['paired_soft_bias_upper']
    a,b=physical['paired_muon_minus_electron_interval']
    assert plus['normalized_signed_derivative_interval'][0]<=a<=b<=plus['normalized_signed_derivative_interval'][1]
    assert not plus['finite_transfer_point_evaluated']


def test_invalid_physical_inputs_rejected(physical):
    with pytest.raises(ValueError):certified_vp_coefficient('0')
    with pytest.raises(ValueError):signed_soft_overlap_enclosure(physical,0)
    assert np.isfinite(physical['paired_center'])
