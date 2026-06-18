import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_overlap_kernel as k  # noqa: E402


def test_yukawa_overlap_kernel_non_tautology_audit_contains_required_steps():
    k.export_outputs(ROOT)
    text = (ROOT / "theory" / "yukawa_overlap_kernel_non_tautology_audit.md").read_text()
    for step in [
        "operator closure inheritance",
        "generation mode ledgers",
        "mode-alignment principle",
        "diagonal leading texture",
        "off-diagonal conditional status",
        "mode-distance scaffold",
        "mass hierarchy bridge",
        "mixing source bridge",
        "comparison to known texture/mixing frameworks",
    ]:
        assert step in text
    assert "does not use measured masses, known texture patterns, CKM values, or PMNS values as input" in text


def test_yukawa_overlap_kernel_docs_do_not_claim_numerical_closure():
    k.export_outputs(ROOT)
    texts = "\n".join(
        (ROOT / "theory" / name).read_text()
        for name in [
            "theorem_discharge_yukawa_overlap_kernel_selection.md",
            "yukawa_overlap_kernel_non_tautology_audit.md",
            "theorem_discharge_yukawa_overlap_kernel_results.json",
        ]
    )
    forbidden = [
        "because the SM has approximately diagonal Yukawas",
        "known texture patterns as input",
        "numerical overlap values are derived",
        "fermion mass ratios are derived",
        "CKM values are derived in this branch",
        "PMNS values are derived in this branch",
        "BHSM replaces the Standard Model",
    ]
    for phrase in forbidden:
        assert phrase not in texts
