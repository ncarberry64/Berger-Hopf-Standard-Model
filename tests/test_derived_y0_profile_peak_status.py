import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_y0_axis_identification as y0  # noqa: E402


def test_y0_profile_peak_is_supported_but_limited():
    assert y0.y0_profile_peak_supported() is True
    y0.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_y0_profile_peak_status.md").read_text()
    assert "Y0_PROFILE_PEAK_SUPPORTED" in text
    assert "universal scalar/topographic profile" in text
