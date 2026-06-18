import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_action_hessian import boundary_action_terms  # noqa: E402


def test_boundary_action_terms_exact_catalog():
    assert boundary_action_terms() == {
        "S_phase": "Hopf phase closure / global boundary consistency",
        "S_orientation": "Z2 upper/lower boundary orientation pair",
        "S_cyclic_channel": "minimal cyclic three-channel closure",
        "S_topographic": "fourth-order topographic branch stability",
        "S_excess": "gap penalty for higher/composite closures",
    }


def test_action_terms_doc_contains_guardrail():
    text = (ROOT / "theory" / "boundary_action_candidate_terms.md").read_text()
    for term in ["S_phase", "S_orientation", "S_cyclic_channel", "S_topographic", "S_excess"]:
        assert term in text
    assert "not yet derived from first principles" in text
