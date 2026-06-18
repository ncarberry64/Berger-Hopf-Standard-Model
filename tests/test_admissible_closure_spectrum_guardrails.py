from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_required_closure_spectrum_status_language_appears():
    text = (ROOT / "theory" / "admissible_boundary_closure_spectrum_gate.md").read_text()
    required = (
        "This gate does not fully derive the Standard Model. It proposes a candidate "
        "admissible boundary-closure spectrum whose minimal dimensions reproduce the "
        "finite boundary algebra used in the previous projector and charge-bridge gates. "
        "The remaining proof obligation is to derive the closure spectrum uniquely from "
        "the Berger-Hopf boundary action, admissible phase closure, and the full "
        "topographic stability/Hessian problem."
    )
    assert required in text
    assert "It does not claim BHSM has replaced the Standard Model." in text
    assert "It does not claim the full gauge group is derived." in text
    assert "It does not claim the admissible closure spectrum is uniquely derived" in text


def test_closure_spectrum_docs_do_not_overclaim():
    forbidden = [
        "full Standard Model derivation is complete",
        "BHSM replaces the Standard Model",
        "we prove the admissible closure spectrum",
        "admissible closure spectrum has been uniquely derived",
        "full Hessian proof is complete",
        "finite boundary algebra is fully derived",
    ]
    docs = [
        ROOT / "theory" / "admissible_boundary_closure_spectrum_gate.md",
        ROOT / "theory" / "hopf_phase_closure_filter.md",
        ROOT / "theory" / "topographic_stability_closure_filter.md",
        ROOT / "theory" / "closure_spectrum_to_finite_algebra_bridge.md",
    ]
    for path in docs:
        text = path.read_text()
        for phrase in forbidden:
            assert phrase not in text
