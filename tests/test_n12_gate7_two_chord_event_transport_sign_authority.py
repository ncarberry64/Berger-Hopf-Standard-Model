from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.audit_n12_gate7_two_chord_event_transport_sign_authority import (
    build_payload,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_TWO_CHORD_EVENT_TRANSPORT_SIGN_AUTHORITY.json"
)


def _record() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_sign_authority_audit_regenerates() -> None:
    record = _record()
    assert json.dumps(record, sort_keys=True) == json.dumps(
        build_payload(), sort_keys=True
    )
    assert record["validation_passed"] is True


def test_all_certified_subspans_are_accounted() -> None:
    audit = _record()["sign_authority_audit"]
    assert audit["certified_core"]["certified_chords"] == 2
    assert audit["certified_core"]["certified_subspans"] == 128
    assert audit["chord_01"]["subspans"] == 64
    assert audit["chord_02"]["subspans"] == 64


def test_state_shadowing_is_not_promoted_to_sign_authority() -> None:
    audit = _record()["sign_authority_audit"]
    assert audit["chord_01"]["F_u_interval_sign_certified"] is False
    assert audit["chord_02"]["F_u_interval_sign_certified"] is False
    assert "u_dot_lower" in audit["chord_01"]["missing_signed_interval_fields"]
    assert "u_dot_upper" in audit["chord_02"]["missing_signed_interval_fields"]
    assert audit["global_monotone_decrease_proved"] is False


def test_next_calculation_reuses_only_existing_chords() -> None:
    calculation = _record()["bounded_next_calculation"]
    assert calculation["new_chord_required"] is False
    assert calculation["trajectory_campaign_required"] is False
    assert "EXISTING_128_CERTIFIED_SUBSPANS" in calculation["target"]


def test_claim_boundaries_remain_closed() -> None:
    record = _record()
    assert record["obstruction_class"] == (
        "MISSING_PROOF_ENCLOSURE_NOT_RETAINED_ACTION_INCOMPATIBILITY"
    )
    assert record["Gate7_status_changed"] is False
    assert record["chord_03_authorized"] is False
    assert record["FULL_BHSM_COMPLETE"] is False


def test_sign_authority_artifact_is_content_addressable() -> None:
    digest = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest().upper()
    assert digest == "BB94C21B3E9DCFD392B14945E54EB3585590BC3678FD43475DDABCBB672474B0"
