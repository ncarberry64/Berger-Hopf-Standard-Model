from __future__ import annotations

import math

import pytest

from bhsm.interface.geometry import (
    DEFAULT_INTERFACE_FORMULA,
    PLACEHOLDER_UNTIL_BHSM_THEOREM_SUPPLIED,
    HypersphericalGeometry,
)


def test_geometry_initializes_and_outputs_are_deterministic() -> None:
    geometry = HypersphericalGeometry((3.0, 4.0), (2.0,), anisotropy=1.5)
    assert geometry.mode_norm() == 5.0
    assert geometry.hopf_weight() == 2.0
    assert geometry.geometric_metric() == pytest.approx(34.0)
    assert geometry.geometric_tension() == pytest.approx(math.sqrt(34.0))


def test_geometry_round_trip_and_placeholder_labels() -> None:
    geometry = HypersphericalGeometry(
        (5.0, 2.0),
        (1.0,),
        radius=2.0,
        sector="lepton",
        mode_label="(5,2)",
        model_constants={"S": 0.1},
        metadata={"review": True},
    )
    payload = geometry.to_dict()
    restored = HypersphericalGeometry.from_dict(payload)
    assert restored.to_dict() == payload
    assert DEFAULT_INTERFACE_FORMULA in payload["formula_status"]
    assert PLACEHOLDER_UNTIL_BHSM_THEOREM_SUPPLIED in payload["formula_status"]


def test_custom_formulas_replace_defaults() -> None:
    geometry = HypersphericalGeometry(
        (1.0,),
        (1.0,),
        metric_fn=lambda _: 9.0,
        tension_fn=lambda _: 7.0,
    )
    assert geometry.geometric_metric() == 9.0
    assert geometry.geometric_tension() == 7.0
    assert geometry.to_dict()["formula_status"] == "USER_SUPPLIED_BHSM_THEOREM_MODE"


def test_invalid_geometry_is_rejected() -> None:
    with pytest.raises(ValueError, match="radius"):
        HypersphericalGeometry((1.0,), (1.0,), radius=0.0)
