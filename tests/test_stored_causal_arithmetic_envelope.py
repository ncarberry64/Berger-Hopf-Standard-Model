from fractions import Fraction as F
import numpy as np
import pytest
from flint import ctx
from bhsm.interface.stored_causal_arithmetic_envelope import (
    fixed_axis_projection_norms,combine_stored_causal_errors,
)


def test_combination_encloses_exact_nonunit_axis_and_map_source_cross_terms():
    result=combine_stored_causal_errors([5.,2.],[.125,.5],.0625,[1.125,1.])
    state=F(9,8)*5+2
    error=(F(1,16)*state+F(1,8)+F(1,2))/(1-F(1,16))
    assert F(result['frozen_map_response_error_coefficient_upper'])>=error
    assert F(result['frozen_map_transverse_quadratic_coefficients_upper'][0])>=5+F(9,8)*error
    assert F(result['frozen_map_transverse_quadratic_coefficients_upper'][1])>=2+error
    assert result['frozen_map_response_error_coefficient_upper']<float(error)*1.000000000001


def test_exact_stored_axis_norms_do_not_assume_normalization():
    l,t=fixed_axis_projection_norms([[0.,0.],[1.5,0.]])
    assert 1.5<=l<1.500000001
    assert 1.25<=t<1.250000001
    l,t=fixed_axis_projection_norms([[0.],[.5]])
    assert .5<=l<.500000001
    assert .75<=t<.750000001


def test_empty_source_error_and_zero_response_remain_zero():
    previous=ctx.prec
    result=combine_stored_causal_errors([0.,0.],[],0.,[1.,1.])
    assert result['frozen_map_transverse_quadratic_coefficients_upper']==[0.,0.]
    assert result['FULL_BHSM_COMPLETE'] is False
    assert ctx.prec==previous


@pytest.mark.parametrize('gain',[-1.,1.,np.inf,np.nan])
def test_invalid_map_gain_rejected(gain):
    with pytest.raises(ValueError):combine_stored_causal_errors([1.,1.],[0.],gain,[1.,1.])
