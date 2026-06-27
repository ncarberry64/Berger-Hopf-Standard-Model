from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_sprint_c_docs_have_exact_warnings_and_readme_section():
    docs = "\n".join((ROOT / "docs" / name).read_text(encoding="utf-8") for name in (
        "cp_o_int_sprint_c.md", "cp_o_int_field_action_candidate.md",
        "cp_o_int_field_representation_gate.md", "cp_o_int_lorentz_gate.md",
        "cp_o_int_gauge_admissibility_gate.md", "cp_o_int_coupling_normalization_gate.md",
        "cp_o_int_action_source_gate.md", "cp_o_int_production_eligibility.md",
        "cp_o_int_sprint_c_claim_policy.md",
    ))
    for warning in (
        "CP holonomy or CKM/PMNS phase attachment alone is not a standalone CP O_int interaction theorem.",
        "A standalone CP O_int theorem requires field, Lorentz, gauge, coupling, and action/operator definitions.",
        "A symbolic field/action candidate is not action-level closure.",
        "A conditional author axiom is not production-ready.",
        "Runtime-disabled software gates remain disabled until live external validation passes.",
    ):
        assert warning in docs
    assert "## CP O_int field/action construction attempt" in (ROOT / "README.md").read_text(encoding="utf-8")
