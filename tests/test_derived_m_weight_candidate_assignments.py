import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_m_weight_assignment as mw  # noqa: E402


def test_m_weight_candidate_assignments_are_not_promoted():
    mw.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_m_weight_candidate_assignments.md").read_text()
    assignments = {row["assignment"]: row["status"] for row in mw.candidate_m_assignments()}

    assert assignments["m=sigma/2"] == "STRUCTURALLY_MOTIVATED_NOT_DERIVED"
    assert assignments["m=T3"] == "STRUCTURALLY_MOTIVATED_NOT_DERIVED"
    assert assignments["m=generation-index dependent label"] == "FAILED_GUARDRAIL"
    assert mw.m_weight_assignment_derived() is False
    assert "m=sigma/2" in text
    assert "m=generation-index dependent label" in text
