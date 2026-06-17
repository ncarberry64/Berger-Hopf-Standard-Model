from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_qj_eigenfunction_map_non_tautology_audit_contains_route_split():
    text = (ROOT / "theory" / "qj_eigenfunction_map_non_tautology_audit.md").read_text()

    assert "mode ledger" in text
    assert "symbolic eigenfunction map" in text
    assert "local features" in text
    assert "diagonal route" in text
    assert "full rank-three route" in text
    assert "does not use measured masses, known Yukawa matrices, CKM values, or PMNS values" in text


def test_qj_eigenfunction_map_forbidden_overclaims_absent():
    text = "\n".join(
        path.read_text()
        for path in [
            ROOT / "theory" / "theorem_discharge_qj_eigenfunction_map.md",
            ROOT / "theory" / "qj_eigenfunction_map_non_tautology_audit.md",
            ROOT / "theory" / "theorem_discharge_qj_eigenfunction_map_results.json",
        ]
    ).lower()

    for phrase in [
        "measured masses are used",
        "ckm values are derived",
        "pmns values are derived",
        "rank-three yukawa theorem is proven",
        "explicit qj-to-eigenfunction map derived",
        "bhsm replaces the standard model",
        "standard model fully derived",
    ]:
        assert phrase not in text
