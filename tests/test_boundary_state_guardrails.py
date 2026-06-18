from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_boundary_state_docs_contain_required_guardrail_language() -> None:
    text = (
        ROOT / "theory" / "boundary_state_primitive_derivation_gate.md"
    ).read_text(encoding="utf-8")
    required = (
        "This gate does not fully derive the Standard Model. It proposes and tests "
        "a candidate boundary-state system whose outputs reproduce the previously "
        "audited integer primitive bridge. The remaining proof obligation is to "
        "derive the boundary state classes themselves from Berger-Hopf boundary "
        "action, admissible phase closure, automorphism structure, and topographic "
        "stability."
    )
    assert required in text
    assert "BOUNDARY_STATE_CLASSES_DERIVATION_REMAINS_OPEN" in text
    assert "FULL_SM_DERIVATION_NOT_CLAIMED" in text


def test_boundary_state_docs_do_not_make_forbidden_claims() -> None:
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            ROOT / "theory" / "boundary_state_primitive_derivation_gate.md",
            ROOT / "theory" / "boundary_state_primitive_registry.md",
            ROOT / "theory" / "boundary_state_to_sm_bridge.md",
            ROOT / "theory" / "boundary_state_primitive_derivation_results.json",
        ]
    )
    forbidden = [
        "therefore BHSM has derived the Standard Model",
        "therefore BHSM has replaced the Standard Model",
        "the full gauge group is now derived",
        "boundary state classes are fully derived",
    ]
    for phrase in forbidden:
        assert phrase not in text


def test_collective_curvature_not_moved_into_particle_sector_proof() -> None:
    text = (
        ROOT / "theory" / "boundary_state_primitive_derivation_gate.md"
    ).read_text(encoding="utf-8")
    assert "dark matter" not in text.lower()
    assert "collective curvature" not in text.lower()
