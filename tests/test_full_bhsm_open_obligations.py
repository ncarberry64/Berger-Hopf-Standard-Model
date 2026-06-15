from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_full_bhsm_completion import OPEN_OBLIGATIONS, open_obligation_registry  # noqa: E402


def test_all_required_open_obligations_are_registered() -> None:
    registered = [row["obligation"] for row in open_obligation_registry()]
    assert registered == OPEN_OBLIGATIONS
    assert len(registered) == 14


def test_open_obligation_document_contains_required_items() -> None:
    text = (ROOT / "theory" / "full_bhsm_open_proof_obligations.md").read_text(
        encoding="utf-8"
    )
    for obligation in OPEN_OBLIGATIONS:
        assert obligation in text
    assert "open_proof_obligation" in text


def test_completion_results_keep_open_obligations_visible() -> None:
    text = (ROOT / "theory" / "full_bhsm_completion_results.json").read_text(
        encoding="utf-8"
    )
    assert "Derive collective curvature fixed-point mass law." in text
    assert "Empirically test collective-curvature dark-matter interpretation." in text
    assert "Harmonize quark reference schemes." in text
