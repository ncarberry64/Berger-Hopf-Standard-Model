from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts/n16_coupled_momentum_response"


def test_n16_paired_hard_response_and_claim_boundary() -> None:
    audit = json.loads((
        ARTIFACT / "BHSM_N16_COUPLED_MOMENTUM_RESPONSE_AUDIT.json"
    ).read_text(encoding="utf-8"))
    hard = audit["paired_exact_hard_momentum_response"]

    assert audit["validation_passed"] is True
    assert hard["strict_exact_merit_reduction"] is True
    assert hard["exact_full_weak_norm_after"] < hard[
        "exact_full_weak_norm_before"
    ]
    assert hard["eta_after"]["admissible"] is True
    assert hard["soft_channel"]["classification"] == (
        "NORMAL_DIRECTION_CONTROLLED_BY_THE_EXISTING_POSITIVE_DURATION_"
        "GAUGE_FIXED_JACOBI_EVOLUTION"
    )
    assert hard["soft_channel"]["uniform_closed_range_failure_proved"] is False
    assert audit["N16_COMPLETE_PERSISTENT_CHILD_CERTIFIED"] is False
    assert audit["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
    assert audit["FULL_BHSM_COMPLETE"] is False


def test_n16_checkpoint_manifest_hashes() -> None:
    manifest = json.loads((
        ARTIFACT / "BHSM_N16_COUPLED_MOMENTUM_RESPONSE_CHECKPOINT_MANIFEST.json"
    ).read_text(encoding="utf-8"))

    for record in manifest["files"]:
        path = ROOT / record["path"]
        payload = path.read_bytes()
        assert len(payload) == record["bytes"]
        assert hashlib.sha256(payload).hexdigest() == record["sha256"]

    claims = manifest["claims"]
    assert claims["N16_COMPLETE_PERSISTENT_CHILD_CERTIFIED"] is False
    assert claims["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
    assert claims["FULL_BHSM_COMPLETE"] is False
