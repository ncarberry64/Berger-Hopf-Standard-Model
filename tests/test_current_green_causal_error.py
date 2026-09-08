from fractions import Fraction

import numpy as np
import pytest
from flint import ctx

from bhsm.interface.current_green_causal_error import transport_local_errors


@pytest.mark.parametrize('block', [1, 2, 3, 10])
def test_scalar_transport_encloses_exact_rational_oracle(block):
    maps = np.array([2., -.25, 4., .125, -8.])
    errors = np.array([.125, .25, .5, .125, .25])
    actual = transport_local_errors(maps[:, None, None], errors, block)
    radius = Fraction(0)
    for i, (p, e) in enumerate(zip(maps, errors)):
        radius = abs(Fraction(float(p))) * radius + Fraction(float(e))
        assert Fraction(actual['node_error_norm_upper'][i+1]) >= radius
        assert actual['node_error_norm_upper'][i+1] < float(radius)*1.000000000001


def test_signed_products_retain_cancellation_across_two_maps():
    # A norm-per-step recurrence amplifies by roughly a million; the
    # exact signed product at the final node is the identity.
    maps = np.array([np.eye(2), [[1., 1000.], [0., 1.]],
                     [[1., -1000.], [0., 1.]]])
    for block in (1, 3):
        result = transport_local_errors(maps, [1., 0., 0.], block)
        assert 1. <= result['node_error_norm_upper'][-1] < 1.000000000001


@pytest.mark.parametrize('block', [1, 2, 4, 10])
def test_noncommuting_vector_recurrence_is_enclosed(block):
    rng = np.random.default_rng(740)
    maps = rng.integers(-3, 4, size=(7, 3, 3)).astype(float)/4
    sources = rng.integers(-4, 5, size=(7, 3)).astype(float)/8
    errors = np.nextafter(np.linalg.norm(sources, axis=1), np.inf)
    result = transport_local_errors(maps, errors, block)
    value = np.zeros(3)
    for i, (p, source) in enumerate(zip(maps, sources)):
        value = p @ value + source
        assert np.linalg.norm(value) <= result['node_error_norm_upper'][i+1]


def test_fixed_reset_and_source_injection_index():
    result = transport_local_errors(np.array([[[1e100]], [[3.]]]), [2., 0.])
    assert result['node_error_norm_upper'][0] == 0.
    assert 2. <= result['node_error_norm_upper'][1] < 2.000000000001
    assert 6. <= result['node_error_norm_upper'][2] < 6.000000000001


def test_zero_errors_and_subnormal_source_preserve_precision():
    previous = ctx.prec
    maps = np.ones((2, 1, 1))
    assert transport_local_errors(maps, [0., 0.])['maximum_node_error_norm_upper'] == 0.
    tiny = np.nextafter(0., 1.)
    result = transport_local_errors(maps, [tiny, tiny])
    assert result['node_error_norm_upper'][-1] >= 2*tiny
    assert ctx.prec == previous
    assert result['physical_Hessian_error_enclosed'] is False
    assert result['FULL_BHSM_COMPLETE'] is False


@pytest.mark.parametrize('bounds', [[-1.], [np.inf], [np.nan], [1., 2.]])
def test_invalid_bounds_are_rejected(bounds):
    with pytest.raises(ValueError):
        transport_local_errors(np.ones((1, 1, 1)), bounds)


@pytest.mark.parametrize('block', [0, -1, 1.5, True])
def test_invalid_block_size_is_rejected(block):
    with pytest.raises(ValueError):
        transport_local_errors(np.ones((1, 1, 1)), [1.], block)
