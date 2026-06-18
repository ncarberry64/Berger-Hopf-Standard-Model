import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_overlap as yo  # noqa: E402


def test_yukawa_overlap_non_tautology_audit_contains_required_steps():
    yo.export_outputs(ROOT)
    text = (ROOT / "theory" / "yukawa_overlap_non_tautology_audit.md").read_text()
    for step in [
        "allowed operator classes",
        "generation mode ledgers",
        "overlap functional",
        "matrix scaffold",
        "mass matrix relation",
        "mixing scaffold",
        "neutral sector mass scaffold",
        "comparison to known fermion mass/mixing framework",
    ]:
        assert step in text
    assert "does not use measured masses, known Yukawa matrices, CKM values, or PMNS values as input" in text


def test_yukawa_overlap_docs_do_not_claim_numerical_closure():
    yo.export_outputs(ROOT)
    texts = "\n".join(
        (ROOT / "theory" / name).read_text()
        for name in [
            "theorem_discharge_yukawa_overlap_texture_source.md",
            "yukawa_overlap_non_tautology_audit.md",
            "theorem_discharge_yukawa_overlap_results.json",
        ]
    )
    forbidden = [
        "because the SM has these masses",
        "known Yukawa matrices as assumptions",
        "numerical Yukawa values are derived",
        "fermion mass ratios are derived",
        "CKM values are derived",
        "PMNS values are derived",
        "BHSM replaces the Standard Model",
    ]
    for phrase in forbidden:
        assert phrase not in texts
