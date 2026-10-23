import numpy as np
import pytest
from bhsm.interface.muon_birth_area_coupled_endpoint import area_continuation_initializer


def test_area_initializer_is_only_a_shared_parameter_tangent_step():
    x=np.arange(536,dtype=float).reshape(2,268)/1000;d=np.sin(x)
    moved=area_continuation_initializer(x,d,1e-4)
    np.testing.assert_array_equal(moved,x+1e-4*d)
    np.testing.assert_array_equal(x,np.arange(536,dtype=float).reshape(2,268)/1000)


@pytest.mark.parametrize('gamma',[0.,-1.,np.nan,np.inf])
def test_no_zero_or_unphysical_parameter_is_assigned_as_positive_family(gamma):
    with pytest.raises(ValueError):area_continuation_initializer(np.zeros((2,268)),np.ones((2,268)),gamma)


def test_complex_primal_or_incomplete_area_image_is_not_discarded():
    with pytest.raises(ValueError):area_continuation_initializer(np.ones((2,268),complex),np.ones((2,268)),1.)
    with pytest.raises(ValueError):area_continuation_initializer(np.ones((2,268)),np.ones((2,100)),1.)
