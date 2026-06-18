from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_theorem_boundary_docs_contain_required_guardrail_language():
    text = (ROOT / "theory" / "theorem_level_boundary_action_derivation.md").read_text()
    assert (
        "This document does not claim that the Standard Model is fully derived. It "
        "begins the theorem-level derivation program for BHSM by separating "
        "assumptions, candidate axioms, lemmas, theorem statements, and open proof "
        "obligations. The boundary action, full Hessian, closure spectrum, finite "
        "algebra, and charge/anomaly bridge remain candidate until their proof "
        "obligations are discharged."
    ) in text


def test_theorem_boundary_docs_do_not_overclaim():
    forbidden = [
        "full Standard Model derivation is complete",
        "BHSM replaces the Standard Model",
        "boundary action is derived",
        "boundary action is fully derived",
        "full Hessian proof is complete",
        "full gauge group is derived",
        "higher closures are impossible",
    ]
    docs = [
        ROOT / "theory" / "theorem_level_boundary_action_derivation.md",
        ROOT / "theory" / "bhsm_boundary_axioms.md",
        ROOT / "theory" / "bhsm_boundary_theorem_statements.md",
        ROOT / "theory" / "bhsm_boundary_lemma_ledger.md",
        ROOT / "theory" / "bhsm_boundary_proof_obligation_ledger.md",
        ROOT / "theory" / "bhsm_boundary_non_tautology_audit.md",
    ]
    for path in docs:
        text = path.read_text()
        for phrase in forbidden:
            assert phrase not in text

