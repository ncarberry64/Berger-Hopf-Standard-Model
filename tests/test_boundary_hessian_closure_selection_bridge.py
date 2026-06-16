import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_action_hessian import closure_selection_summary  # noqa: E402


def test_closure_selection_summary_preserves_previous_spectrum():
    summary = closure_selection_summary()
    assert summary["selected_low_energy_spectrum"] == [1, 2, 3]
    assert summary["stability_hierarchy_passes"] is True
    assert summary["boundary_action_derived"] is False
    assert summary["full_hessian_proof_complete"] is False
    assert summary["projectors"]["P_excess"]["finite_algebra_block"] == "higher/composite"


def test_closure_selection_bridge_doc():
    text = (ROOT / "theory" / "boundary_hessian_closure_selection_bridge.md").read_text()
    assert "P_ref     -> d=1 -> End(C^1)=C" in text
    assert "P_orient  -> d=2 -> End(C^2)=M2(C)" in text
    assert "P_cyclic  -> d=3 -> End(C^3)=M3(C)" in text
    assert "P_excess  -> d>=4 -> higher/composite/unsupported low-energy closures" in text
    assert "does not uniquely derive it" in text
