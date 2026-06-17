import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_harmonic_highest_weight as hw  # noqa: E402


def test_feature_vector_bridge_does_not_claim_explicit_eigenfunctions():
    assert hw.explicit_eigenfunctions_derived() is False
    hw.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_highest_weight_to_feature_vector_bridge.md").read_text()
    assert "D^ell_{m,q/2}" in text
    assert "after `m` and explicit harmonics are derived" in text
    assert "FEATURE_VECTOR_BRIDGE_CONDITIONAL" in text
