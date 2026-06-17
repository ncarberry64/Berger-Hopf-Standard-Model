import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_y0_axis_identification as y0  # noqa: E402


def test_y0_group_identity_is_not_derived():
    assert y0.y0_group_identity_derived() is False
    y0.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_y0_identity_axis_audit.md").read_text()
    assert "No repo theorem identifies `y0` with the group identity" in text
    assert "Y0_AXIS_IDENTIFICATION_REMAINS_OPEN" in text
