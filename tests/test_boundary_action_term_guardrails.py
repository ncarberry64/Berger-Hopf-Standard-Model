from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_boundary_action_term_docs_contain_required_guardrail_language():
    text = (ROOT / "theory" / "boundary_action_term_realization_audit.md").read_text()
    assert (
        "This audit does not fully derive the Standard Model. It gives candidate "
        "mathematical realizations of the boundary action terms used in the Hessian "
        "scaffold. These functionals support the previously audited closure-spectrum "
        "route diagnostically, but the full Berger-Hopf boundary action and Hessian "
        "remain unproved."
    ) in text
    assert "higher `d` values are not declared impossible" in text


def test_boundary_action_term_docs_do_not_overclaim():
    forbidden = [
        "full Standard Model derivation is complete",
        "BHSM replaces the Standard Model",
        "boundary action is fully derived",
        "boundary action derivation is complete",
        "full Hessian proof is complete",
        "full gauge group is derived",
        "higher closures are impossible",
    ]
    docs = [
        ROOT / "theory" / "boundary_action_term_realization_audit.md",
        ROOT / "theory" / "boundary_phase_closure_functional.md",
        ROOT / "theory" / "boundary_orientation_involution_functional.md",
        ROOT / "theory" / "boundary_cyclic_channel_functional.md",
        ROOT / "theory" / "boundary_topographic_excess_functional.md",
    ]
    for path in docs:
        text = path.read_text()
        for phrase in forbidden:
            assert phrase not in text

