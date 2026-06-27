from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_docs_contain_exact_claim_warnings_and_readme_section():
    docs = "\n".join((ROOT / "docs" / name).read_text(encoding="utf-8") for name in (
        "cp_o_int_sprint_b.md", "cp_o_int_attachment_theorem_attempt.md",
        "cp_o_int_stage_evaluation.md", "cp_o_int_proof_gates.md", "cp_o_int_claim_policy.md",
    ))
    for warning in (
        "CP holonomy or CKM/PMNS phase attachment alone is not a standalone CP O_int interaction theorem.",
        "A standalone CP O_int theorem requires field, Lorentz, gauge, coupling, and action/operator definitions.",
        "Reference values, including PDG values, are comparison inputs only and are never theorem inputs.",
        "A conditional author axiom is not an action-level closure.",
        "Runtime-disabled software gates remain disabled until live external validation passes.",
    ):
        assert warning in docs
    assert "## CP O_int standalone interaction attachment attempt" in (ROOT / "README.md").read_text(encoding="utf-8")
