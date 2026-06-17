import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_raw_mode_berger_harmonic as rh  # noqa: E402


def test_raw_mode_to_feature_vector_bridge_is_symbolic():
    rh.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_raw_mode_to_feature_vector_bridge.md").read_text()

    assert rh.raw_mode_feature_bridge() in text
    assert "explicit feature values remain open" in text
    assert "RAW_MODE_TO_FEATURE_VECTOR_BRIDGE_DERIVED_CONDITIONAL" in text
