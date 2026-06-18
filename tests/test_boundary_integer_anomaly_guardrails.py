from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_anomaly_gate_doc_contains_required_status_language() -> None:
    text = (
        ROOT / "theory" / "boundary_integer_anomaly_closure_gate.md"
    ).read_text(encoding="utf-8")
    required = (
        "This anomaly-closure gate tests whether the integer primitive charge/hypercharge "
        "bridge reproduces Standard Model one-generation anomaly cancellation. It does "
        "not derive the integer primitives from Berger-Hopf boundary geometry and does "
        "not prove that BHSM has derived or replaced the Standard Model."
    )
    assert required in text
    assert "BOUNDARY_INTEGER_ANOMALY_CLOSURE_GATE_CANDIDATE" in text
    assert "FULL_SM_DERIVATION_NOT_CLAIMED" in text


def test_anomaly_gate_doc_contains_explicit_anomaly_sums() -> None:
    text = (
        ROOT / "theory" / "boundary_integer_anomaly_closure_gate.md"
    ).read_text(encoding="utf-8")
    assert "2*(1/3) + (-4/3) + (2/3) = 0" in text
    assert "3*(1/3) + (-1) = 0" in text
    assert "6*(1/3)^3 + 3*(-4/3)^3 + 3*(2/3)^3 + 2*(-1)^3 + (2)^3 + 0^3 = 0" in text
    assert "6*(1/3) + 3*(-4/3) + 3*(2/3) + 2*(-1) + 2 + 0 = 0" in text
    assert "N_doublets = 3 quark doublets + 1 lepton doublet = 4" in text


def test_anomaly_gate_does_not_move_collective_curvature_into_particle_proof() -> None:
    text = (
        ROOT / "theory" / "boundary_integer_anomaly_closure_gate.md"
    ).read_text(encoding="utf-8")
    assert "Keep collective-curvature/dark-matter interpretation separate from this particle-sector proof." in text


def test_forbidden_overclaims_absent_from_anomaly_gate_docs() -> None:
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            ROOT / "theory" / "boundary_integer_anomaly_closure_gate.md",
            ROOT / "theory" / "boundary_integer_anomaly_closure_results.json",
        ]
    )
    forbidden = [
        "therefore BHSM has derived the Standard Model",
        "therefore BHSM has replaced the Standard Model",
        "the full gauge group is now derived",
        "anomaly cancellation has been derived from first-principles boundary geometry",
    ]
    for phrase in forbidden:
        assert phrase not in text
