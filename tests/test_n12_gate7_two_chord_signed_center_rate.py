from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_TWO_CHORD_SIGNED_CENTER_RATE_PROFILE.json"
)


def _record() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_all_centers_and_selected_branch_are_preserved() -> None:
    record = _record()
    assert record["validation_passed"] is True
    assert sum(item["nodes"] for item in record["summary"].values()) == 130
    assert all(
        item["selected_indices"] == [23]
        for item in record["summary"].values()
    )


def test_node_profile_is_not_interval_authority() -> None:
    record = _record()
    assert record["claim_boundary"]["signed_center_rate"] == "EVALUATED"
    assert record["claim_boundary"]["128_subspan_interval_sign"] == "OPEN"
    assert record["claim_boundary"]["continuum_tube_sign_transfer"] == "OPEN"
    assert record["Gate7_status_changed"] is False
    assert record["chord_03_authorized"] is False


def test_profile_is_content_addressable() -> None:
    digest = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest().upper()
    assert digest == "3B0C40CA88E3B37818C315696ACA5FB39BA7877D9763EB164DC1729609A43992"
