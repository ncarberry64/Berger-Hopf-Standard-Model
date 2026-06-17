import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_raw_mode_berger_harmonic as rh  # noqa: E402


def test_j_fiber_weight_audit_is_structural_not_derived():
    rh.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_j_fiber_weight_audit.md").read_text()

    assert rh.j_fiber_weight_status() == "STRUCTURALLY_MOTIVATED_NOT_DERIVED"
    assert "structurally compatible" in text
    assert "does not yet derive" in text
    assert "J_AS_HOPF_FIBER_WEIGHT_STRUCTURALLY_MOTIVATED_NOT_DERIVED" in text
