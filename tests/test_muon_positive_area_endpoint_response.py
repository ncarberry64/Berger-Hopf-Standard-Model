import numpy as np
import pytest
from bhsm.interface.muon_positive_area_endpoint_response import positive_parameter_checks


def test_positive_base_increments_use_same_action_member_not_zero_origin():
    base = .11; f = np.array([3., -2.]); r0 = np.array([.01, -.03])
    observed = []
    def rows(gamma):
        observed.append(gamma)
        return r0 + (gamma-base)*f
    checks = positive_parameter_checks(base,r0,f,rows,(1e-4,5e-5))
    np.testing.assert_allclose(observed,[.1101,.11005],atol=0,rtol=0)
    assert all(x['source_difference_norm'] < 2e-12 for x in checks)


def test_same_base_check_resolves_quadratic_contact_error_under_halving():
    base = .1; f = np.array([2., -1.]); c = np.array([4., 3.]); r0 = np.zeros(2)
    checks = positive_parameter_checks(base,r0,f,
        lambda g:(g-base)*f+(g-base)**2*c,(1e-4,5e-5))
    np.testing.assert_allclose(checks[0]['source_difference_norm'],
                               2*checks[1]['source_difference_norm'],rtol=3e-9)


@pytest.mark.parametrize('base,steps',[(0.,(1e-4,)),(.1,(0.,)),(.1,(-.2,))])
def test_check_preserves_positive_area_domain(base,steps):
    with pytest.raises(ValueError):
        positive_parameter_checks(base,np.zeros(1),np.zeros(1),lambda g:np.zeros(1),steps)
