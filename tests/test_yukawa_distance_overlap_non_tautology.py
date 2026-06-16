import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_distance_overlap as d  # noqa: E402


def test_distance_overlap_non_tautology_audit_contains_required_steps():
    d.export_outputs(ROOT)
    text = (ROOT / "theory" / "yukawa_distance_overlap_non_tautology_audit.md").read_text()
    for step in [
        "distance diagnostics",
        "exponential L1 candidate",
        "Gaussian D2 candidate",
        "power/dressing candidate",
        "boundary-action Hessian candidate",
        "selection-only scaffold",
    ]:
        assert step in text
    assert "does not use measured masses, known Yukawa textures, CKM values, or PMNS values as input" in text


def test_distance_overlap_docs_do_not_claim_numerical_values():
    d.export_outputs(ROOT)
    texts = "\n".join(
        (ROOT / "theory" / name).read_text()
        for name in [
            "theorem_discharge_yukawa_distance_overlap_law.md",
            "yukawa_distance_overlap_non_tautology_audit.md",
            "theorem_discharge_yukawa_distance_overlap_results.json",
        ]
    )
    forbidden = [
        "numerical overlap values are derived",
        "fermion mass ratios are derived",
        "CKM values are derived",
        "PMNS values are derived",
        "BHSM replaces the Standard Model",
    ]
    for phrase in forbidden:
        assert phrase not in texts
