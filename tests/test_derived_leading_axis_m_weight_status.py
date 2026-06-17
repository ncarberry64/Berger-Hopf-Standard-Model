import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_leading_axis_m_weight as la  # noqa: E402


def test_leading_axis_m_weight_status_remains_open():
    assert la.leading_axis_m_assignment_derived() is False
    la.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_leading_axis_m_weight_status.md").read_text()
    assert "not promoted" in text
    assert "LEADING_AXIS_M_WEIGHT_ASSIGNMENT_REMAINS_OPEN" in text
