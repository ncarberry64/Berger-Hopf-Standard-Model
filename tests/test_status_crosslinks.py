from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CROSSLINK_FILES = [
    "theory/full_bhsm_completion_v1_candidate.md",
    "theory/full_bhsm_master_equation_map.md",
    "theory/full_bhsm_claim_status_matrix.md",
    "theory/full_bhsm_open_proof_obligations.md",
    "theory/full_bhsm_empirical_gate_plan.md",
    "theory/full_bhsm_candidate_release_notes.md",
    "docs/current_bhsm_status.md",
    "README.md",
]


def test_status_crosslinks_are_present() -> None:
    for relative in CROSSLINK_FILES:
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "current_bhsm_status" in text or relative == "docs/current_bhsm_status.md"
        if relative.startswith("theory/"):
            assert "full_bhsm_completion_v1_candidate" in text or relative.endswith(
                "full_bhsm_completion_v1_candidate.md"
            )


def test_readme_links_to_status_and_synthesis_docs() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "theory/full_bhsm_completion_v1_candidate.md" in text
    assert "theory/full_bhsm_open_proof_obligations.md" in text
    assert "docs/frozen_predictions.md" in text
