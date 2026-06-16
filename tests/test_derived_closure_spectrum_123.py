import inspect
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_phase_orientation_cyclic as discharge  # noqa: E402


def test_primitive_low_energy_closure_spectrum_is_derived_by_helpers():
    assert discharge.primitive_low_energy_closure_spectrum() == [1, 2, 3]
    source = inspect.getsource(discharge.primitive_low_energy_closure_spectrum)
    assert "minimal_orientation_dimension()" in source
    assert "minimal_non_involutive_cyclic_order()" in source
    assert "return [1, 2, 3]" not in source


def test_closure_spectrum_discharge_status_and_documentation():
    assert (
        discharge.proof_discharge_ledger()["PO-BH-8"].status
        == discharge.DischargeStatus.DERIVED_CONDITIONAL
    )
    text = (ROOT / "theory" / "derived_closure_spectrum_123.md").read_text()
    assert "D_primitive_low = {1,2,3}" in text
    assert "Higher `d` are not impossible" in text

