from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_required_finite_algebra_status_language_appears():
    text = (ROOT / "theory" / "finite_boundary_algebra_source_gate.md").read_text()
    required = (
        "This gate does not fully derive the Standard Model. It proposes a candidate finite "
        "Berger-Hopf boundary algebra whose central projections and orientation grading "
        "reproduce the previously audited projector eigenvalue system. The remaining proof "
        "obligation is to derive this finite algebra from Berger-Hopf boundary action, "
        "admissible phase closure, automorphism structure, and topographic stability."
    )
    assert required in text
    assert "It does not claim BHSM has replaced the Standard Model." in text
    assert "It does not claim the full gauge group is derived." in text


def test_finite_algebra_docs_do_not_overclaim():
    forbidden = [
        "full Standard Model derivation is complete",
        "BHSM replaces the Standard Model",
        "finite boundary algebra is fully derived from Berger-Hopf geometry",
        "full gauge-group derivation is complete",
    ]
    docs = [
        ROOT / "theory" / "finite_boundary_algebra_source_gate.md",
        ROOT / "theory" / "finite_boundary_algebra_blocks.md",
        ROOT / "theory" / "finite_boundary_algebra_charge_operators.md",
    ]
    for path in docs:
        text = path.read_text()
        for phrase in forbidden:
            assert phrase not in text
