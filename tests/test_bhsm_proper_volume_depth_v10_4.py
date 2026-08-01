from __future__ import annotations

import math

import pytest

from bhsm.interface.envelopment.proper_volume_depth_v10_4 import (
    DEPTH_VERDICT,
    linear_block_depth,
    proper_volume_payload,
    q_volume,
    volume_ratio,
)


def test_volume_ratio_and_conformal_normalization_are_exact():
    assert volume_ratio(math.exp(16), 1.0) == pytest.approx(math.exp(8))
    assert q_volume(math.exp(16), 1.0) == pytest.approx(-1.0)
    assert linear_block_depth(1.0, 1.0, 1.0) == pytest.approx(-7 / 8)
    with pytest.raises(ValueError):
        volume_ratio(0.0, 1.0)


def test_candidate_requires_common_pullback_and_excludes_degenerate_core():
    payload = proper_volume_payload()
    assert payload["validation_passed"] is True
    assert payload["block_reduction"]["q_V_reduced"] == "-7*rho/8"
    assert payload["covariance"]["local_gauge_invariant_without_relational_map"] is False
    assert payload["domain"][2]["inverse_metric_action_valid"] is False
    assert payload["physical_depth"] is None
    assert payload["verdict"] == DEPTH_VERDICT
