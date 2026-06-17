from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_legacy_geometric_overlap_non_tautology_audit_contains_guarded_rows():
    text = (ROOT / "theory" / "legacy_geometric_overlap_non_tautology_audit.md").read_text()

    assert "legacy integral source" in text
    assert "BHSM notation bridge" in text
    assert "rank guardrail" in text
    assert "numerical values" in text
    assert "does not use measured masses or known Yukawa matrices as inputs" in text


def test_legacy_geometric_overlap_forbidden_overclaims_absent():
    text = "\n".join(
        path.read_text()
        for path in [
            ROOT / "theory" / "theorem_discharge_legacy_geometric_overlap_bridge.md",
            ROOT / "theory" / "legacy_geometric_overlap_non_tautology_audit.md",
            ROOT / "theory" / "theorem_discharge_legacy_geometric_overlap_results.json",
        ]
    ).lower()

    for phrase in [
        "ckm values are derived",
        "pmns values are derived",
        "bhsm replaces the standard model",
        "standard model fully derived",
        "rank-three yukawa matrix theorem complete",
    ]:
        assert phrase not in text
