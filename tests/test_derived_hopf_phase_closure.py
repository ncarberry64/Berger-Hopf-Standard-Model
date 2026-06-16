import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_theorem_discharge_phase_orientation_cyclic import (  # noqa: E402
    hopf_phase_closure_condition,
    proof_discharge_ledger,
    DischargeStatus,
)


def test_hopf_phase_closure_accepts_positive_integers_only():
    assert hopf_phase_closure_condition(1)
    assert hopf_phase_closure_condition(3)
    assert not hopf_phase_closure_condition(0)
    assert not hopf_phase_closure_condition(-1)
    assert not hopf_phase_closure_condition(1.5)
    assert not hopf_phase_closure_condition("3")


def test_hopf_phase_discharge_status_and_documentation():
    assert proof_discharge_ledger()["PO-BH-2"].status == DischargeStatus.DERIVED_CONDITIONAL
    text = (ROOT / "theory" / "derived_hopf_phase_closure.md").read_text()
    assert "exp(i 2*pi d)=1" in text
    assert "d in Z_{>0}" in text
    assert "PO_BH_2_PHASE_CLOSURE_DERIVED_CONDITIONAL" in text

