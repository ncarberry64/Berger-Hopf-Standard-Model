from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_required_automorphism_closure_status_language_appears():
    text = (ROOT / "theory" / "boundary_automorphism_closure_origin_gate.md").read_text()
    required = (
        "This gate does not fully derive the Standard Model. It proposes a candidate "
        "automorphism-and-closure origin for the finite Berger-Hopf boundary algebra. "
        "The remaining proof obligation is to derive the admissible boundary closure "
        "classes, orientation grading, and interface activity directly from the "
        "Berger-Hopf boundary action and topographic stability operator."
    )
    assert required in text
    assert "It does not claim BHSM has replaced the Standard Model." in text
    assert "It does not claim the full gauge group is derived." in text
    assert "It does not claim SU(3), SU(2), or U(1) are fully derived." in text


def test_automorphism_closure_docs_do_not_overclaim():
    forbidden = [
        "full Standard Model derivation is complete",
        "BHSM replaces the Standard Model",
        "finite boundary algebra is fully derived",
        "full gauge-group derivation is complete",
        "SU(3), SU(2), and U(1) are fully derived",
    ]
    docs = [
        ROOT / "theory" / "boundary_automorphism_closure_origin_gate.md",
        ROOT / "theory" / "boundary_channel_automorphism_origin.md",
        ROOT / "theory" / "boundary_weak_interface_origin.md",
        ROOT / "theory" / "boundary_algebra_minimality_audit.md",
    ]
    for path in docs:
        text = path.read_text()
        for phrase in forbidden:
            assert phrase not in text
