import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_admissible_closure_spectrum import phase_closure_pass  # noqa: E402


def test_phase_closure_passes_only_diagnostic_dimensions():
    for d in [1, 2, 3]:
        assert phase_closure_pass(d) is True
    for d in [4, 5]:
        assert phase_closure_pass(d) is False


def test_phase_closure_rejects_invalid_dimensions():
    for d in [0, -1, 1.5, "3"]:
        with pytest.raises(ValueError):
            phase_closure_pass(d)  # type: ignore[arg-type]


def test_hopf_phase_filter_doc_guardrail():
    text = (ROOT / "theory" / "hopf_phase_closure_filter.md").read_text()
    assert "phase_closure_pass(d) = d in {1,2,3}" in text
    assert "This is not a final derivation." in text
    assert "derive it from the boundary action and global phase constraints" in text
