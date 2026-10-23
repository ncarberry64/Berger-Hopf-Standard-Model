"""Independent action identities and soft-kernel checks for the measured sector."""
import math
from pathlib import Path
import numpy as np
import pytest
from scipy.integrate import quad

from bhsm.interface.muon_calibrated_current_response import (
    transverse_current_response,finite_transfer_pauli_kernel,magnetic_moment_accounting,
    paired_two_current_pauli,
)
from bhsm.interface.muon_calibrated_local_pauli import one_loop_pauli_spacelike


def test_primal_adjoint_identity_with_current_and_state_motion():
    # Finite identity check; the production driver independently inserts the
    # actual measured spectrum. This polynomial is CONTROL_ONLY.
    Q=.13;d=lambda x:.04*x+.01*x*x
    row=transverse_current_response(Q,(d(Q),.04+.02*Q,.02),
        J=1+.3j,L=.2-.7j,J_dot=.8-.1j,L_dot=-.3+.2j)
    assert row['primal_residual']<1e-15
    assert row['full_adjoint_residual']<1e-15
    assert row['return_identity_residual']<1e-14
    assert row['derivative_identity_residual']<1e-14
    assert abs(row['first_insertion_dimensionless_return']-np.conj(.2-.7j)*(1+.3j)*d(Q))<1e-17


@pytest.mark.parametrize('rho',[0.,1e-8,.001,.4,2.])
def test_massless_kernel_reduces_to_independent_qed_vertex(rho):
    alpha=.0072973525627871355
    calculated=alpha/math.pi*finite_transfer_pauli_kernel(0.,.105,rho)
    independent=one_loop_pauli_spacelike(alpha=alpha,Q_squared_over_m_squared=rho)['F2']
    assert abs(calculated-independent)<2e-17


@pytest.mark.parametrize('s',[.08,1.,100.])
def test_massive_kernel_with_independent_double_parameter_integral(s):
    m=.1056584;rho=.013
    actual=finite_transfer_pauli_kernel(s,m,rho,order=192)
    def outer(x):
        return quad(lambda u:x*x*(1-x)/(x*x+(1-x)*s/m**2+rho*x*x*u*(1-u)),
            0,1,epsabs=1e-14,epsrel=1e-12)[0]
    independent=quad(outer,0,1,epsabs=1e-14,epsrel=1e-12)[0]
    assert abs(actual-independent)<2e-14
    at_zero=finite_transfer_pauli_kernel(s,m,0.,order=192)
    assert 0<=at_zero-actual<=rho/6*at_zero


def test_signed_magnetic_units_and_g_relation():
    plus=magnetic_moment_accounting(a_mu=.001,mass_GeV=.105,charge_sign=1)
    minus=magnetic_moment_accounting(a_mu=.001,mass_GeV=.105,charge_sign=-1)
    assert plus['g_mu']==2.002
    assert plus['magnetic_moment_Sz_plus_hbar_over_2_J_per_T']==-minus['magnetic_moment_Sz_plus_hbar_over_2_J_per_T']
    assert 4.5e-26<plus['muon_magneton_J_per_T']<4.6e-26


def test_nonphysical_resummed_domain_rejected():
    with pytest.raises(ValueError):transverse_current_response(.1,(1.,0.,0.))


def test_measured_spectrum_pair_retains_shared_covariance():
    from bhsm.interface.muon_calibrated_hvp_spectral import load_alphaqed26_spectrum
    source=Path(__file__).resolve().parents[1]/'artifacts/muon_calibrated_hvp_spectral_20261010/input'
    p=paired_two_current_pauli(load_alphaqed26_spectrum(source),alpha=.0072973525627871355,
        muon_mass_GeV=.10565842526040435,electron_mass_GeV=.000510998950905377)
    assert 1.7e-12<p['electron']['value']<2e-12
    assert p['muon_minus_electron']==p['muon']['value']-p['electron']['value']
    assert p['difference_source_standard_uncertainty']<p['muon']['spectral_error']
    assert p['difference_source_standard_uncertainty']>p['muon']['spectral_error']*.999
    assert not p['completed_native_pair']
