import numpy as np
import pytest
from bhsm.interface.muon_changing_current_energy_moments import (
    external_energy_weights,two_current_energy_application,proper_clock_at_nodes)


def test_owned_contour_uses_analytic_dual_and_both_energy_signs():
    t=np.array([-.4,.2,.9]);E=.3
    w=external_energy_weights(t,E,variable='continued_Lorentz_energy')
    np.testing.assert_allclose(w['left'],np.exp(E*t),rtol=0,atol=0)
    np.testing.assert_allclose(w['right'],np.exp(-E*t),rtol=0,atol=0)
    np.testing.assert_allclose(w['left_first'],t*np.exp(E*t),rtol=0,atol=0)
    np.testing.assert_allclose(w['right_first'],-t*np.exp(-E*t),rtol=0,atol=0)
    assert np.linalg.norm(w['left']-w['right'].conj())>0
    f=external_energy_weights(t,E,variable='proper_clock_frequency')
    np.testing.assert_allclose(f['left_first'],1j*t*f['left'],rtol=0,atol=0)
    with pytest.raises(ValueError):external_energy_weights(t,E,variable='unbound')


def test_energy_derivative_matches_literal_two_time_kernel_not_one_leg():
    # A finite actual two-time Gaussian graph with independent left/right
    # vertices. Its denominator is known exactly at c=0.
    t=np.array([-.4,.2,.9]);ln=np.array([1+2j,2-.3j,-.7+.4j]);rn=np.array([-.2+1j,.8-2j,1.3+.6j])
    E=.3;w=external_energy_weights(t,E,variable='continued_Lorentz_energy')
    m=lambda a:np.sum(a).reshape(1,1,1)
    r=two_current_energy_application(m(w['left']*ln),m(w['right']*rn),
        m(w['left_first']*ln),m(w['right_first']*rn),[2.],[3.],cutoff=0.)
    exact=-sum((t[i]-t[j])*np.exp(E*(t[i]-t[j]))*ln[i]*rn[j]/6 for i in range(3)for j in range(3))
    np.testing.assert_allclose(r['energy_first'][0,0],exact,rtol=2e-15,atol=1e-15)
    assert abs(r['left_energy_contact'][0,0]-exact)>0.1


def test_clock_origin_cancels_in_value_and_two_sided_energy_jet():
    t=np.array([.1,.4,.8]);l=np.array([1+1j,2.,3-.7j]);r=np.array([-.4,.8+1j,1.2])
    def value(clock):
        w=external_energy_weights(clock,.2,variable='proper_clock_frequency')
        a=lambda z:np.sum(z).reshape(1,1,1)
        return two_current_energy_application(a(w['left']*l),a(w['right']*r),
            a(w['left_first']*l),a(w['right_first']*r),[2.],[3.],cutoff=.1)
    a,b=value(t),value(t+4)
    np.testing.assert_allclose(a['value'],b['value'],rtol=2e-15,atol=2e-15)
    np.testing.assert_allclose(a['energy_first'],b['energy_first'],rtol=3e-14,atol=2e-15)
    assert np.linalg.norm(a['left_energy_contact']-b['left_energy_contact'])>.1


def test_proper_clock_uses_reached_lapse_and_rejects_wrong_orientation():
    u=np.array([0.,.1,.6,1.])
    r=proper_clock_at_nodes(u,lambda s:1+2*s+s*s,order=16)
    np.testing.assert_allclose(r['proper_times'],u+u*u+u**3/3,rtol=3e-16,atol=1e-16)
    assert not r['clock_enclosure_claimed']
    with pytest.raises(ValueError):proper_clock_at_nodes(u,lambda s:-1.)
