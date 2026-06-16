import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_theorem_discharge_phase_orientation_cyclic import (  # noqa: E402
    DischargeStatus,
    minimal_orientation_dimension,
    orientation_involution_eigenvalues,
    proof_discharge_ledger,
)


def test_orientation_involution_eigenvalues_and_dimension():
    assert orientation_involution_eigenvalues() == (1, -1)
    assert minimal_orientation_dimension() == 2


def test_orientation_discharge_status_and_documentation():
    assert proof_discharge_ledger()["PO-BH-3"].status == DischargeStatus.DERIVED_CONDITIONAL
    text = (ROOT / "theory" / "derived_orientation_involution.md").read_text()
    assert "Iota^2 = identity" in text
    assert "lambda = +/-1" in text
    assert "d=2" in text

