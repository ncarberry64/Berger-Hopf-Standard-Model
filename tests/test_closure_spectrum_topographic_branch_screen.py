import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_closure_spectrum_selection import topographic_branch_screen_status  # noqa: E402


def test_topographic_branch_screen_mapping():
    assert topographic_branch_screen_status(1) == "reference"
    assert topographic_branch_screen_status(2) == "stable_nonzero_orientation_candidate"
    assert topographic_branch_screen_status(3) == "stable_nonzero_channel_candidate"
    for d in [4, 5, 6, 7, 8]:
        assert topographic_branch_screen_status(d) == "higher_or_composite_unsupported"


def test_topographic_branch_screen_doc_guardrail():
    text = (ROOT / "theory" / "closure_spectrum_topographic_branch_screen.md").read_text()
    assert "L_T = nabla^2 - B nabla^4" in text
    assert "zero/reference closure + two stable nonzero branches" in text
    assert "not a full Hessian proof" in text
