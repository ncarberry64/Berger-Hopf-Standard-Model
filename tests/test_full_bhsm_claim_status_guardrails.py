from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_full_bhsm_completion import (  # noqa: E402
    REQUIRED_CLAIM_IDS,
    claim_status_registry,
    validate_no_derived_overclaim,
)


FORBIDDEN_PHRASES = [
    "Full BHSM proven",
    "Standard Model has been fully derived",
    "Dark matter solved.",
    "Particle dark matter disproven.",
    "introduces a new official mass formula",
    "numerical closure achieved",
]


def test_required_claim_ids_are_present() -> None:
    ids = {row["claim_id"] for row in claim_status_registry()}
    assert set(REQUIRED_CLAIM_IDS) <= ids


def test_claim_matrix_contains_required_columns() -> None:
    text = (ROOT / "theory" / "full_bhsm_claim_status_matrix.md").read_text(
        encoding="utf-8"
    )
    for column in [
        "claim_id",
        "claim",
        "status",
        "supporting_audits",
        "test_status",
        "failure_modes",
        "allowed_language",
        "forbidden_language",
    ]:
        assert column in text


def test_forbidden_overclaim_phrases_absent_from_docs() -> None:
    paths = [
        ROOT / "theory" / "full_bhsm_completion_v1_candidate.md",
        ROOT / "theory" / "full_bhsm_master_equation_map.md",
        ROOT / "theory" / "full_bhsm_claim_status_matrix.md",
        ROOT / "theory" / "full_bhsm_open_proof_obligations.md",
        ROOT / "theory" / "full_bhsm_empirical_gate_plan.md",
        ROOT / "theory" / "full_bhsm_candidate_release_notes.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    for phrase in FORBIDDEN_PHRASES:
        assert phrase not in text


def test_overclaim_validator_rejects_only_strong_claims() -> None:
    assert validate_no_derived_overclaim("repo-audited candidate architecture") is True
    assert validate_no_derived_overclaim("Full BHSM proven") is False
    assert validate_no_derived_overclaim("dark matter solved") is False
