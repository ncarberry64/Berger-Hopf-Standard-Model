import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_theorem_discharge_phase_orientation_cyclic import replacement_claim_ready  # noqa: E402


def test_theorem_discharge_docs_contain_mission_and_downstream_guardrails():
    text = (ROOT / "theory" / "theorem_discharge_phase_orientation_cyclic.md").read_text()
    assert "The purpose of this branch is not to preserve not-proven labels indefinitely." in text
    assert "attempt to discharge the proof obligations" in text
    assert "Status labels may be promoted only when the derivation is explicit" in text
    assert "Replacement readiness remains false" in text
    assert replacement_claim_ready() is False


def test_theorem_discharge_docs_do_not_overclaim():
    forbidden = [
        "full Standard Model derivation is complete",
        "BHSM replaces the Standard Model",
        "replacement claim is ready",
        "full color gauge group is proven",
        "full weak gauge group is proven",
        "higher closures are impossible",
    ]
    docs = [
        ROOT / "theory" / "theorem_discharge_phase_orientation_cyclic.md",
        ROOT / "theory" / "derived_hopf_phase_closure.md",
        ROOT / "theory" / "derived_orientation_involution.md",
        ROOT / "theory" / "derived_minimal_cyclic_channel.md",
        ROOT / "theory" / "derived_closure_spectrum_123.md",
    ]
    for path in docs:
        text = path.read_text()
        for phrase in forbidden:
            assert phrase not in text

