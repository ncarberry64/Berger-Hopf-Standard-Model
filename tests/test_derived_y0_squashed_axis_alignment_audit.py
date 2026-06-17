import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_y0_axis_identification as y0  # noqa: E402


def test_squashed_axis_alignment_is_structural_not_derived():
    assert y0.y0_squashed_axis_alignment_supported() == "STRUCTURALLY_MOTIVATED_NOT_DERIVED"
    y0.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_y0_squashed_axis_alignment_audit.md").read_text()
    assert "structurally motivated" in text
    assert "not promoted to identity-axis sampling" in text
