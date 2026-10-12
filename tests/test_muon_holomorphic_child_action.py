import numpy as np
from bhsm.interface.muon_holomorphic_normal_geometry import anchored_holomorphic_chart
from bhsm.interface.muon_exact_material_response import anchored_join_coefficients


def test_anchored_holomorphic_chart_keeps_owned_third_implicit_derivative():
    old=anchored_join_coefficients(.004,points=48);new=anchored_holomorphic_chart(.004,points=48)
    np.testing.assert_allclose(new['coefficients'],old['coefficients'],atol=2e-15)
    np.testing.assert_allclose(new['derivatives'],old['derivatives'],atol=4e-13,rtol=3e-13)
    a=anchored_holomorphic_chart(.004+2e-5j,points=48)
    b=anchored_holomorphic_chart(.004-2e-5j,points=48)
    np.testing.assert_allclose(a['coefficients'],b['coefficients'].conj(),atol=2e-15)
    assert np.max(abs(a['implicit_Taylor_residual'][:,1:]))<8e-13
    h=1e-5
    plus=anchored_holomorphic_chart(.004+2e-5j+h,points=48)
    minus=anchored_holomorphic_chart(.004+2e-5j-h,points=48)
    np.testing.assert_allclose((plus['derivatives'][:,1]-minus['derivatives'][:,1])/(2*h),a['derivatives'][:,2],rtol=2e-7,atol=3e-6)
