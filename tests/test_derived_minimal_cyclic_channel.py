import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_theorem_discharge_phase_orientation_cyclic import (  # noqa: E402
    DischargeStatus,
    cyclic_sector_is_new,
    minimal_non_involutive_cyclic_order,
    proof_discharge_ledger,
)


def test_minimal_non_involutive_cyclic_order():
    assert not cyclic_sector_is_new(1)
    assert not cyclic_sector_is_new(2)
    assert cyclic_sector_is_new(3)
    assert minimal_non_involutive_cyclic_order() == 3


def test_cyclic_discharge_status_and_documentation():
    assert proof_discharge_ledger()["PO-BH-4"].status == DischargeStatus.DERIVED_CONDITIONAL
    text = (ROOT / "theory" / "derived_minimal_cyclic_channel.md").read_text()
    assert "g^n = identity" in text
    assert "`n=1`: identity/reference" in text
    assert "`n=2`: involutive orientation" in text
    assert "n=3" in text

