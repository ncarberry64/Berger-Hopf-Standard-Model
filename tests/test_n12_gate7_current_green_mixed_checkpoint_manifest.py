from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_CURRENT_GREEN_MIXED_TRANSVERSE_CHECKPOINT_MANIFEST.json"


def test_checkpoint_manifest_is_valid_and_fail_closed() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert len(payload["shards"]) == 80
    assert payload["claim_boundary"][
        "PRE_DIRECTIVE_SHARDS_RECOMPUTATION_REQUIRED"
    ] is False
    assert payload["claim_boundary"]["ALL_POST_RESET_ENDPOINTS_MATERIALIZED"] is False


def test_checkpoint_manifest_covers_contiguous_nodes_and_hashes() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert [row["node"] for row in payload["shards"]] == list(range(1, 81))
    assert all(len(row["SHA256"]) == 64 for row in payload["shards"])
    assert len(payload["mixed_axis_map_source_SHA256"]) == 64


def test_local_checkpoint_shards_match_manifest_when_available() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    paths = [ROOT / row["path"] for row in payload["shards"]]
    if not all(path.is_file() for path in paths):
        return
    for row, path in zip(payload["shards"], paths, strict=True):
        assert hashlib.sha256(path.read_bytes()).hexdigest().upper() == row["SHA256"]
