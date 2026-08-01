from __future__ import annotations

import math

import pytest

from bhsm.interface.envelopment.spacetime_support_order_parameter_v10_4 import (
    logarithmic_depth_coordinate,
    order_parameter_payload,
    validate_support,
)


def test_support_range_background_and_monotone_coordinate():
    assert validate_support(1.0) == 1.0
    assert validate_support(0.0, regular_domain=False) == 0.0
    assert logarithmic_depth_coordinate(1.0) == 0.0
    assert logarithmic_depth_coordinate(0.5) == pytest.approx(math.log(2.0))
    with pytest.raises(ValueError):
        validate_support(0.0)


def test_order_parameter_does_not_replace_metric_determinant_or_seam():
    payload = order_parameter_payload()
    assert payload["validation_passed"] is True
    assert payload["proper_volume_deficit_as_q_D"] == "INVALIDATED"
    assert payload["regular_action_domain"] == "0<upsilon<=1 with det(G)!=0"
    assert payload["canonical_q_D"] is None
    assert payload["core_value_domain"].startswith("Sigma_core")
