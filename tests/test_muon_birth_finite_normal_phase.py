import numpy as np
import pytest
from bhsm.interface.muon_birth_finite_normal_phase import area_length_coefficient,proper_clock_normal_density


def test_owned_area_length_derivatives_match_independent_power_law():
    c=.71;alpha=.0073;m=7;a=area_length_coefficient(c,alpha,m);h=1e-5
    value=lambda x:alpha/x**(m/2)
    assert a['value']==value(c)
    np.testing.assert_allclose(a['first'],(value(c+h)-value(c-h))/(2*h),rtol=2e-9)
    np.testing.assert_allclose(a['second'],(value(c+h)-2*value(c)+value(c-h))/h**2,rtol=3e-6)
    assert not a['alpha_EM_substituted']


def test_proper_clock_density_preserves_integrated_quadratic_action():
    It,Rt,l=2.3,7.1,.63;dt=.017;at=.4;a=.2
    r=proper_clock_normal_density(It,Rt,l)
    coordinate=dt*(It*at**2-Rt*a*a)/2
    proper=l*dt*(r['inertia']*(at/l)**2-r['stiffness']*a*a)/2
    assert proper==pytest.approx(coordinate,rel=2e-15,abs=1e-16)
    assert not r['integrated_endpoint_Schur_is_resistance']


@pytest.mark.parametrize('c,alpha,m',[(0.,1.,7),(1.,0.,7),(1.,1.,0),(1.,1.,7.)])
def test_area_law_rejects_invalid_domain(c,alpha,m):
    with pytest.raises(ValueError):area_length_coefficient(c,alpha,m)
