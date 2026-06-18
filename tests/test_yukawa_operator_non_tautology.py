import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_operator as y  # noqa: E402


def test_yukawa_non_tautology_audit_contains_required_steps():
    y.export_outputs(ROOT)
    text = (ROOT / "theory" / "yukawa_operator_non_tautology_audit.md").read_text()
    for step in [
        "boundary field inventory",
        "scalar/conjugate scalar source",
        "hypercharge closure",
        "orientation contraction",
        "cyclic/reference contraction",
        "allowed operator classes",
        "forbidden operator classes",
        "neutral singlet mass operator",
        "comparison to known Yukawa classes",
    ]:
        assert step in text
    assert "does not use the known Standard Model Yukawa table as input" in text


def test_yukawa_docs_do_not_make_forbidden_downstream_claims():
    y.export_outputs(ROOT)
    texts = "\n".join(
        (ROOT / "theory" / name).read_text()
        for name in [
            "theorem_discharge_yukawa_operator_closure.md",
            "yukawa_operator_non_tautology_audit.md",
            "theorem_discharge_yukawa_operator_results.json",
        ]
    )
    forbidden = [
        "because the Standard Model has these Yukawa terms",
        "numerical Yukawa values are derived",
        "mass ratios are derived",
        "CKM/PMNS mixing is derived",
        "BHSM replaces the Standard Model",
    ]
    for phrase in forbidden:
        assert phrase not in texts
