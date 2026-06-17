from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_raw_mode_berger_harmonic_non_tautology_audit_guardrails():
    text = (ROOT / "theory" / "raw_mode_berger_harmonic_non_tautology_audit.md").read_text()

    assert "raw mode map" in text
    assert "candidate harmonic form" in text
    assert "m assignment" in text
    assert "does not import measured masses, known Yukawa matrices, CKM values, or PMNS values" in text


def test_raw_mode_berger_harmonic_forbidden_overclaims_absent():
    text = "\n".join(
        path.read_text()
        for path in [
            ROOT / "theory" / "theorem_discharge_raw_mode_berger_harmonic_map.md",
            ROOT / "theory" / "raw_mode_berger_harmonic_non_tautology_audit.md",
            ROOT / "theory" / "theorem_discharge_raw_mode_berger_harmonic_results.json",
        ]
    ).lower()

    for phrase in [
        "m-weight assignment derived",
        "explicit eigenfunction values derived",
        "rank-three yukawa theorem derived",
        "numerical yukawa values derived",
        "bhsm replaces the standard model",
        "standard model fully derived",
    ]:
        assert phrase not in text
