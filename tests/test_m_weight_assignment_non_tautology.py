from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_m_weight_non_tautology_audit_contains_guardrails():
    text = (ROOT / "theory" / "m_weight_assignment_non_tautology_audit.md").read_text()

    assert "admissibility" in text
    assert "m sources" in text
    assert "candidate assignments" in text
    assert "No `m` assignment is selected to fit masses, mixing values, or admissibility alone" in text


def test_m_weight_forbidden_overclaims_absent():
    text = "\n".join(
        path.read_text()
        for path in [
            ROOT / "theory" / "theorem_discharge_m_weight_assignment.md",
            ROOT / "theory" / "m_weight_assignment_non_tautology_audit.md",
            ROOT / "theory" / "theorem_discharge_m_weight_assignment_results.json",
        ]
    ).lower()

    for phrase in [
        "m-weight assignment derived",
        "selected harmonic convention derived",
        "explicit eigenfunction values derived",
        "rank-three yukawa theorem derived",
        "numerical yukawa values derived",
        "bhsm replaces the standard model",
    ]:
        assert phrase not in text
