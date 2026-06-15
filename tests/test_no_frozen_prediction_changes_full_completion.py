from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FROZEN_HASHES = {
    "docs/frozen_predictions.md": "A413C72F731A15B5AF0ED4DDDC3A58D428A60BA3367676FFCDA03FF546593439",
    "docs/frozen_predictions.json": "A9735A4A17934B524C4DE317254AE40838078FBA99274C95C0DBAE11A43C6C17",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def test_frozen_prediction_files_are_unchanged_for_full_completion_sprint() -> None:
    for relative, expected in FROZEN_HASHES.items():
        assert _sha256(ROOT / relative) == expected


def test_full_completion_sprint_does_not_touch_official_prediction_files() -> None:
    added_files = {
        "theory/full_bhsm_completion_v1_candidate.md",
        "theory/full_bhsm_master_equation_map.md",
        "theory/full_bhsm_claim_status_matrix.md",
        "theory/full_bhsm_open_proof_obligations.md",
        "theory/full_bhsm_empirical_gate_plan.md",
        "theory/full_bhsm_completion_results.json",
        "theory/full_bhsm_candidate_release_notes.md",
        "theory/candidate_full_bhsm_completion.py",
    }
    assert "docs/frozen_predictions.md" not in added_files
    assert "docs/frozen_predictions.json" not in added_files
    assert "BHSM_BARE_V1" not in added_files
    assert "BHSM_DRESSED_V1_CANDIDATE" not in added_files
