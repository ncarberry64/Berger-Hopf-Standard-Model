from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_required_candidate_only_status_language_appears():
    text = (ROOT / "theory" / "boundary_projector_algebra_gate.md").read_text()
    required = (
        "This gate does not fully derive the Standard Model. It replaces named "
        "boundary-state classes with a candidate boundary-projector algebra whose "
        "joint eigenvalues reproduce the previously audited \\(C,\\ell,\\sigma,w\\) "
        "primitive bridge. The remaining proof obligation is to derive the projector "
        "algebra itself from Berger-Hopf boundary action, automorphism structure, "
        "admissible phase closure, and topographic stability."
    )
    assert required in text
    assert "It does not claim BHSM has replaced the Standard Model." in text
    assert "It does not claim the full gauge group is derived." in text


def test_forbidden_overclaim_phrases_absent_from_projector_docs():
    forbidden = [
        "full Standard Model derivation is complete",
        "projector algebra is derived from geometry",
        "BHSM replaces the Standard Model",
        "BHSM replacement is claimed",
        "full gauge-group derivation is complete",
    ]
    for path in [
        ROOT / "theory" / "boundary_projector_algebra_gate.md",
        ROOT / "theory" / "boundary_projector_to_state_bridge.md",
        ROOT / "theory" / "boundary_projector_closure_constraints.md",
    ]:
        text = path.read_text()
        for phrase in forbidden:
            assert phrase not in text
