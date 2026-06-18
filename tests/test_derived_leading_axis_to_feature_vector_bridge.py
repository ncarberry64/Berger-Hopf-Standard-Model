import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_leading_axis_m_weight as la  # noqa: E402


def test_feature_vector_bridge_is_candidate_only():
    la.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_leading_axis_to_feature_vector_bridge.md").read_text()
    assert "D^(k/2)_(q/2,q/2)" in text
    assert "after the `y0` axis sampling theorem is derived" in text
    assert "FEATURE_VECTOR_BRIDGE_CANDIDATE_ONLY" in text
