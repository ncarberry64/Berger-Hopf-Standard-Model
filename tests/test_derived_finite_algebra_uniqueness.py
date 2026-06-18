import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_finite_algebra_charge as discharge  # noqa: E402


def test_endomorphism_blocks_and_boundary_algebra_descriptor():
    assert discharge.endomorphism_block(1) == "C"
    assert discharge.endomorphism_block(2) == "M2(C)"
    assert discharge.endomorphism_block(3) == "M3(C)"
    with pytest.raises(ValueError):
        discharge.endomorphism_block(0)

    descriptor = discharge.finite_boundary_algebra_descriptor()
    assert descriptor["A_channel"] == "C_ref direct_sum M3(C)_cyc"
    assert descriptor["A_orientation"] == "M2(C)_active direct_sum C_+ direct_sum C_-"
    assert descriptor["A_boundary"] == "A_channel tensor A_orientation, up to repo convention/isomorphism"
    assert descriptor["primitive_closure_spectrum"] == [1, 2, 3]


def test_finite_algebra_discharge_status_and_documentation():
    discharge.export_outputs(ROOT)
    ledger = discharge.proof_discharge_ledger()
    assert ledger["PO-BH-9"].status == discharge.DischargeStatus.DERIVED_CONDITIONAL
    text = (ROOT / "theory" / "derived_finite_algebra_uniqueness.md").read_text(encoding="utf-8")
    assert "A_channel = C_ref direct_sum M3(C)_cyc" in text
    assert "A_orientation = M2(C)_active direct_sum C_+ direct_sum C_-" in text
    assert "PO_BH_9_FINITE_ALGEBRA_UNIQUENESS_DERIVED_CONDITIONAL" in text
