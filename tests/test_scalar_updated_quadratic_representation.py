from fractions import Fraction

import numpy as np
import pytest
from flint import ctx

from bhsm.interface.symmetric_quadratic_center import certify_representation
from bhsm.interface.scalar_updated_quadratic_representation import certify_scalar_update


def test_reused_bound_contains_exact_rational_error_for_all_outputs():
    rng = np.random.default_rng(740)
    raw = rng.normal(size=(4, 5, 5))
    corrected = raw.copy()
    corrected[-1] += rng.normal(size=(5, 5))
    _, previous = certify_representation(raw)
    represented, report = certify_scalar_update(
        raw, corrected, previous['projection_rounding_Frobenius_upper'])
    squared = Fraction(0)
    for o, i, j in np.ndindex(corrected.shape):
        exact = (Fraction(float(corrected[o, i, j]))
                 + Fraction(float(corrected[o, j, i])))/2
        squared += (Fraction(float(represented[o, i, j]))-exact)**2
    assert Fraction(report['projection_rounding_Frobenius_upper'])**2 >= squared
    assert np.array_equal(represented, represented.transpose(0, 2, 1))
    assert report['raw_bound_requires_external_verification'] is True
    assert report['physical_Hessian_error_enclosed'] is False


def test_changed_field_output_is_rejected():
    raw = np.ones((3, 2, 2))
    corrected = raw.copy()
    corrected[0, 0, 1] += 1
    with pytest.raises(ValueError, match='scalar output'):
        certify_scalar_update(raw, corrected, 0.)


def test_cancelling_scalar_to_zero_has_exact_zero_error():
    raw = np.zeros((2, 2, 2))
    raw[-1, 0, 1] = .1
    result, record = certify_scalar_update(raw, np.zeros_like(raw), 1.)
    assert np.all(result == 0.)
    assert record['projection_rounding_Frobenius_upper'] == 0.
    assert record['projection_rounding_relative_to_maximum_entry_upper'] == 0.


def test_subnormal_updated_scalar_and_precision_restoration():
    previous = ctx.prec
    tiny = np.nextafter(0., 1.)
    raw = np.zeros((2, 2, 2))
    updated = raw.copy()
    updated[-1, 0, 1] = tiny
    _, report = certify_scalar_update(raw, updated, 0.)
    assert report['projection_rounding_Frobenius_upper'] >= tiny
    assert ctx.prec == previous


@pytest.mark.parametrize('bound', [-1., np.inf, np.nan, [1.]])
def test_invalid_raw_bound_is_rejected(bound):
    raw = np.ones((2, 2, 2))
    with pytest.raises(ValueError):
        certify_scalar_update(raw, raw, bound)
