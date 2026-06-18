import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_admissible_closure_spectrum import topographic_stability_pass  # noqa: E402


def test_topographic_stability_passes_only_diagnostic_dimensions():
    for d in [1, 2, 3]:
        assert topographic_stability_pass(d) is True
    for d in [4, 5]:
        assert topographic_stability_pass(d) is False


def test_topographic_stability_rejects_invalid_dimensions():
    for d in [0, -2, 2.5, "2"]:
        with pytest.raises(ValueError):
            topographic_stability_pass(d)  # type: ignore[arg-type]


def test_topographic_filter_doc_guardrail():
    text = (ROOT / "theory" / "topographic_stability_closure_filter.md").read_text()
    assert "L_T = nabla^2 - B*nabla^4" in text
    assert "topographic_stability_pass(d) = d in {1,2,3}" in text
    assert "cannot be claimed closed here" in text
