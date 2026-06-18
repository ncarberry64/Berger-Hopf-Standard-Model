import inspect
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_closure_spectrum_selection import (  # noqa: E402
    classify_dimension,
    cyclic_channel_rule_pass,
    orientation_rule_pass,
    reference_rule_pass,
    selected_low_energy_spectrum,
)


def test_named_rules_select_reference_orientation_and_cyclic_channel():
    assert reference_rule_pass(1)
    assert not reference_rule_pass(2)
    assert orientation_rule_pass(2)
    assert not orientation_rule_pass(3)
    assert cyclic_channel_rule_pass(3)
    assert not cyclic_channel_rule_pass(2)


def test_classification_for_primitive_dimensions():
    assert classify_dimension(1).primitive_status == "primitive reference/single closure"
    assert classify_dimension(2).primitive_status == "primitive orientation-pair closure"
    assert classify_dimension(3).primitive_status == "primitive cyclic three-channel closure"
    assert selected_low_energy_spectrum(8) == [1, 2, 3]


def test_selection_uses_classification_not_raw_membership_return():
    source = inspect.getsource(selected_low_energy_spectrum)
    assert "classify_dimension" not in source  # it delegates through audit_dimensions
    assert "audit_dimensions" in source
    assert "d in {1, 2, 3}" not in source
    assert "d in PRIMITIVE_SELECTED_DIMS" not in source


def test_invalid_dimensions_raise():
    for d in [0, -1, 1.2, "3"]:
        with pytest.raises(ValueError):
            classify_dimension(d)  # type: ignore[arg-type]
