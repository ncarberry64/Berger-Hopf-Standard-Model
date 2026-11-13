"""Finite-mass neutral daughter energies share the full parent spin rate."""
import numpy as np
import pytest

from bhsm.interface.muon_daughter_neutrino_channel import (
    neutrino_parent_analyzer,neutrino_parent_analyzer_first,neutrino_phase_prefactor,
)
from bhsm.interface.muon_daughter_spin_channel import (
    va_tensor,va_neutrino_analyzer,local_decay_spectrum,
)
from evaluate_muon_daughter_source_20261016 import neutral_spectrum


@pytest.mark.parametrize('species',['nu_mu','anti_nu_e'])
@pytest.mark.parametrize('m',[0.,.14,.4])
def test_neutral_energy_spin_analyzers_match_independent_finite_mass_VA(species,m):
    E=.18;n=np.array([.6,0.,.8]);C=va_tensor()
    d=neutrino_parent_analyzer(C,M=1.,m=m,E=E,direction=n,species=species)
    # analytic reference is per dy dOmega/(4pi), normalized by Gamma0.
    observed=neutrino_phase_prefactor(M=1.,m=m,E=E)*d/2*(1536*np.pi**3)
    expected=va_neutrino_analyzer(2*E,n,mass_squared_ratio=m*m,species=species)
    np.testing.assert_allclose(observed,expected,atol=2e-13,rtol=0)


def test_all_daughter_total_spin_rates_and_energy_balance_for_full_complex_tensor():
    rng=np.random.default_rng(701);C=(rng.normal(size=(2,4,4,2))+1j*rng.normal(size=(2,4,4,2)))/9
    m=.13;e=local_decay_spectrum(C,M=1.,m=m,energy_order=48)
    neutrals=neutral_spectrum(C,m=m,order=96)
    moment=np.einsum('p,p,pij->ij',e['energy_measure_weights'],e['energy_nodes'],e['parent_density_per_energy'])
    for d in neutrals.values():
        np.testing.assert_allclose(d['integrated_parent_analyzer'],e['integrated_parent_analyzer'],atol=2e-13,rtol=0)
        moment+=d['integrated_energy_analyzer']
    np.testing.assert_allclose(moment,e['integrated_parent_analyzer'],atol=2e-13,rtol=0)


def test_neutral_tensor_direction_is_the_full_quadratic_polarization_identity():
    C=va_tensor(.7+.2j);dC=np.zeros_like(C);dC[1,3,1,0]=.12j
    kw=dict(M=1.,m=.2,E=.29,direction=np.array([0.,.6,.8]),species='anti_nu_e')
    literal=(neutrino_parent_analyzer(C+dC,**kw)-neutrino_parent_analyzer(C-dC,**kw))/2
    np.testing.assert_allclose(neutrino_parent_analyzer_first(C,dC,**kw),literal,atol=2e-13,rtol=0)
