import numpy as np
import pytest
from flint import ctx

from bhsm.interface.current_green_stored_tensor_error import bound_stored_tensor_error


def test_identity_maps_do_not_gain_a_dimension_factor():
    result = bound_stored_tensor_error(np.eye(4), np.eye(3), 2., 3.)
    assert 5. <= result['mapped_total_error_frobenius_upper'] < 5.000000000001


def test_scalar_error_uses_only_its_actual_output_column():
    result = bound_stored_tensor_error(np.array([[1000., 2.]]), np.array([[3., 4.]]), 0., 7.)
    assert 350. <= result['mapped_total_error_frobenius_upper'] < 350.000000001


def test_bound_contains_direct_tensor_pullback_errors():
    rng = np.random.default_rng(740)
    left = rng.normal(size=(3, 4)); right = rng.normal(size=(5, 6))
    error = rng.normal(size=(4, 5, 5))
    extra = rng.normal(size=(5, 5))
    e = np.nextafter(np.linalg.norm(error), np.inf)
    a = np.nextafter(np.linalg.norm(extra), np.inf)
    result = bound_stored_tensor_error(left, right, e, a, scalar_output=1)
    error[1] += extra
    mapped = np.einsum('co,oab,ai,bj->cij', left, error, right, right)
    assert np.linalg.norm(mapped) <= result['mapped_total_error_frobenius_upper']
    assert result['physical_Hessian_error_enclosed'] is False


def test_zero_error_and_precision_restoration():
    previous = ctx.prec
    result = bound_stored_tensor_error(np.ones((2, 3)), np.ones((4, 5)), 0.)
    assert result['mapped_total_error_frobenius_upper'] == 0.
    assert ctx.prec == previous


@pytest.mark.parametrize('error', [-1., np.nan, np.inf, [1.]])
def test_invalid_error_is_rejected(error):
    with pytest.raises(ValueError):
        bound_stored_tensor_error(np.eye(2), np.eye(2), error)
