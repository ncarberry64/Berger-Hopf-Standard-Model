from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import quad

from bhsm.interface.muon_calibrated_hvp_spectral import (
    delta_alpha_had_spacelike,
    delta_alpha_had_spacelike_jet,
    integrate_spectral_kernel,
    leading_hvp_pauli,
    load_alphaqed26_spectrum,
    pauli_kernel,
)

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'artifacts/muon_calibrated_hvp_spectral_20261010/input'
ALPHA=1/137.035999206
MUON=.10565842526040435

@pytest.fixture(scope='module')
def spectrum():
    return load_alphaqed26_spectrum(INPUT)

def test_primary_input_identity_and_resonance_error_units(spectrum):
    # This load verifies every committed input against the primary receipt.
    omega=spectrum['blocks']['OMEGA']
    phi=spectrum['blocks']['PHI']
    assert omega['sys'][np.argmax(omega['y'])]==pytest.approx(.40662)
    assert phi['sys'][np.argmax(phi['y'])]==pytest.approx(1.01337)
    assert set(spectrum['undressing'])=={4,5,6,10,11,12,13,14,15}
    assert spectrum['blocks']['PQCD_2']['x'][-1]==1e6

@pytest.mark.parametrize('energy',[.27914036,.5,1.,10.,100.])
def test_analytic_kernel_agrees_with_independent_parameter_quadrature(energy):
    ratio=energy**2/MUON**2
    expected,error=quad(lambda x:x*x*(1-x)/(x*x+(1-x)*ratio),0,1,
                        epsabs=1e-20,epsrel=3e-12)
    actual=float(pauli_kernel(energy**2,MUON))
    assert actual>0
    assert actual==pytest.approx(expected,rel=2e-12,abs=1e-16)
    assert error<2e-14

def test_measured_contraction_refines_and_retains_partial_scope(spectrum):
    a=leading_hvp_pauli(spectrum,ALPHA,MUON,order=8)
    b=leading_hvp_pauli(spectrum,ALPHA,MUON,order=32)
    assert abs(a['value']-b['value'])<5e-22
    assert b['value']==pytest.approx(6.969377657120127e-8,rel=2e-12)
    assert 3e-10<b['spectral_error']<5e-10
    assert not b['complete_native_remainder']
    assert b['tail_not_included']
    assert b['undressing_error_estimate']>0

def test_spacelike_jet_is_same_subtracted_spectral_operator(spectrum):
    assert delta_alpha_had_spacelike(spectrum,0,ALPHA)['value']==0
    q=.1;step=1e-4
    jet=delta_alpha_had_spacelike_jet(spectrum,q,ALPHA)
    f=lambda z:delta_alpha_had_spacelike(spectrum,z,ALPHA)['value']
    first=(f(q+step)-f(q-step))/(2*step)
    second=(f(q+step)-2*f(q)+f(q-step))/step**2
    assert jet['first']['value']==pytest.approx(first,rel=2e-7)
    assert jet['second']['value']==pytest.approx(second,rel=5e-7)
    assert jet['first']['value']>0>jet['second']['value']
    assert len(jet['first']['statistical_error_vector'])==len(jet['value']['statistical_error_vector'])

def test_shared_uncertainty_rows_are_linear_not_independently_resampled(spectrum):
    q=.1;f=ALPHA/(3*np.pi)
    jet=delta_alpha_had_spacelike_jet(spectrum,q,ALPHA)
    combined=integrate_spectral_kernel(spectrum,
        lambda s:f*q/(s*(s+q))+.2*f/(s+q)**2)
    for key in ['statistical_error_vector','systematic_error_vector']:
        expected=np.asarray(jet['value'][key])+.2*np.asarray(jet['first'][key])
        np.testing.assert_allclose(combined[key],expected,rtol=5e-14,atol=1e-20)
    assert combined['value']==pytest.approx(jet['value']['value']+.2*jet['first']['value'],rel=5e-14)

@pytest.mark.parametrize('q,a',[(-1.,ALPHA),(np.nan,ALPHA),(.1,np.inf),(.1,0.)])
def test_invalid_physical_scalar_inputs_are_rejected(spectrum,q,a):
    with pytest.raises(ValueError):delta_alpha_had_spacelike(spectrum,q,a)

def test_nonfinite_kernel_cannot_become_physical_contraction(spectrum):
    with pytest.raises(ValueError,match='nonfinite'):
        integrate_spectral_kernel(spectrum,lambda s:np.full_like(s,np.nan))
