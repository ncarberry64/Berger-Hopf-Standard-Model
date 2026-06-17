from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_finite_width_overlap_rank_non_tautology_audit_contains_guarded_rows():
    text = (ROOT / "theory" / "finite_width_overlap_rank_non_tautology_audit.md").read_text()

    assert "sharp-peak term" in text
    assert "moment expansion" in text
    assert "rank condition" in text
    assert "width guardrail" in text
    assert "does not use measured masses, known Yukawa matrices, CKM values, or PMNS values" in text


def test_finite_width_overlap_rank_forbidden_overclaims_absent():
    text = "\n".join(
        path.read_text()
        for path in [
            ROOT / "theory" / "theorem_discharge_finite_width_overlap_rank.md",
            ROOT / "theory" / "finite_width_overlap_rank_non_tautology_audit.md",
            ROOT / "theory" / "theorem_discharge_finite_width_overlap_rank_results.json",
        ]
    ).lower()

    for phrase in [
        "measured masses are used",
        "ckm values are derived",
        "pmns values are derived",
        "rank-three yukawa structure is proven",
        "bhsm replaces the standard model",
        "standard model fully derived",
    ]:
        assert phrase not in text
