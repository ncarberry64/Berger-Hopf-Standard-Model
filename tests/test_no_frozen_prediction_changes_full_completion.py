from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FROZEN_HASHES = {
    "docs/frozen_predictions.md": "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4",
    "docs/frozen_predictions.json": "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7",
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
