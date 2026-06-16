from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_boundary_second_variation_docs_contain_required_guardrail_language():
    text = (ROOT / "theory" / "boundary_action_second_variation_audit.md").read_text()
    assert (
        "This audit does not fully derive the Standard Model. It computes candidate "
        "second-variation behavior of the finite boundary action surrogates and shows "
        "that their local quadratic structure supports the previously introduced "
        "Hessian projector scaffold. The full Berger-Hopf boundary action and full "
        "topographic Hessian remain unproved."
    ) in text
    assert (
        "The audit supports a candidate route from realized boundary action terms to "
        "the Hessian projector scaffold. It does not prove that the actual Berger-Hopf "
        "boundary action uniquely produces these projectors."
    ) in text


def test_boundary_second_variation_docs_do_not_overclaim():
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
        ROOT / "theory" / "boundary_action_second_variation_audit.md",
        ROOT / "theory" / "phase_closure_second_variation.md",
        ROOT / "theory" / "orientation_involution_second_variation.md",
        ROOT / "theory" / "cyclic_channel_second_variation.md",
        ROOT / "theory" / "topographic_excess_hessian_bridge.md",
    ]
    for path in docs:
        text = path.read_text()
        for phrase in forbidden:
            assert phrase not in text

