from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "artifacts" / "n12_direct_checkpoint"
MANIFEST = CHECKPOINT / "BHSM_N12_SCIENTIFIC_CHECKPOINT_MANIFEST.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_direct_n12_checkpoint_claim_boundary_and_hashes() -> None:
    manifest = _load(MANIFEST)
    status = manifest["scientific_status"]

    assert status["DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED"] is True
    assert status["exact_F12_norm"] < 3.0e-14
    assert status["certified_action_coordinate_root_ball_radius"] == 1.0e-11
    assert status["corrected_ordered_event_branch"] == "N6_INDEX_12_TO_N12_INDEX_24"
    assert status["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
    assert status["FULL_BHSM_COMPLETE"] is False

    assert len(manifest["promoted_files"]) == 26
    for record in manifest["promoted_files"]:
        path = ROOT / record["durable_repository_path"]
        assert path.is_file()
        assert path.stat().st_size == record["bytes"]
        # Use the on-disk bytes.  The repository-wide pytest fixture
        # intentionally canonicalizes JSON line endings for legacy artifact
        # comparisons, while this manifest is a byte-level provenance record.
        with path.open("rb") as handle:
            digest = hashlib.sha256(handle.read()).hexdigest().upper()
        assert digest == record["SHA256"]


def test_direct_n12_finite_symbol_evidence_is_not_continuum_promotion() -> None:
    manifest = _load(MANIFEST)
    status = manifest["scientific_status"]

    assert status["N12_event_child_Calderon_symbol_gap"] > 0.029
    assert status["minimum_zero_padded_probe_symbol_gap_N12_to_N48"] > 0.009
    assert "zero-padded diagnostic probes, not roots" in manifest["claim_boundary"]
    assert "N12_TO_INFINITY" in manifest["exact_next_dependency"]
