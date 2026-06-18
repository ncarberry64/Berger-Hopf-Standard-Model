from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_m_weight_open_problem_forbids_fitting_or_admissibility_only_selection():
    text = (ROOT / "theory" / "derived_m_weight_open_problem.md").read_text()

    assert "without measured masses" in text
    assert "CKM values" in text
    assert "PMNS values" in text
    assert "admissibility-only selection" in text
    assert "M_WEIGHT_ASSIGNMENT_REMAINS_OPEN" in text
