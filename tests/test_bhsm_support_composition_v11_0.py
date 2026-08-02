from __future__ import annotations

import math

import pytest

from bhsm.interface.envelopment.support_composition_v11_0 import (
    canonical_depth,
    composition_payload,
    haar_kinetic_function,
    support_character,
    support_from_depth,
)


def test_log_depth_is_additive_and_invertible():
    a, b = 0.3, 0.8
    assert canonical_depth(a * b) == pytest.approx(canonical_depth(a) + canonical_depth(b))
    assert support_from_depth(canonical_depth(a)) == pytest.approx(a)
    assert canonical_depth(1.0) == 0.0


def test_haar_metric_canonicalizes_and_characters_multiply():
    upsilon = 0.4
    derivative = -1.0 / upsilon
    assert haar_kinetic_function(upsilon) == pytest.approx(derivative**2)
    assert support_character(0.3 * 0.8, 2) == pytest.approx(
        support_character(0.3, 2) * support_character(0.8, 2)
    )
    assert composition_payload()["validation_passed"] is True


def test_support_domain_and_scale_are_guarded():
    for value in (0.0, -0.1, 1.1):
        with pytest.raises(ValueError):
            canonical_depth(value)
    with pytest.raises(ValueError):
        canonical_depth(0.5, lambda_D=0.0)
    assert math.isfinite(canonical_depth(1.0e-20))
