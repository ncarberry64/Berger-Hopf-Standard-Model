from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_required_boundary_action_hessian_status_language():
    text = (ROOT / "theory" / "boundary_action_hessian_scaffold_gate.md").read_text()
    assert (
        "This gate does not fully derive the Standard Model. It introduces a candidate "
        "Berger-Hopf boundary action and Hessian scaffold whose low-energy projector "
        "structure matches the previously audited closure-spectrum selection rule. The "
        "full proof still requires deriving this Hessian from the actual Berger-Hopf "
        "boundary action, admissible phase closure, and topographic stability operator."
    ) in text


def test_boundary_action_hessian_docs_do_not_overclaim():
    forbidden = [
        "full Standard Model derivation is complete",
        "BHSM replaces the Standard Model",
        "boundary action derivation is complete",
        "full Hessian proof has been completed",
        "closure spectrum has been uniquely derived",
    ]
    docs = [
        ROOT / "theory" / "boundary_action_hessian_scaffold_gate.md",
        ROOT / "theory" / "boundary_action_candidate_terms.md",
        ROOT / "theory" / "boundary_hessian_projector_decomposition.md",
        ROOT / "theory" / "boundary_hessian_closure_selection_bridge.md",
    ]
    for path in docs:
        text = path.read_text()
        for phrase in forbidden:
            assert phrase not in text
