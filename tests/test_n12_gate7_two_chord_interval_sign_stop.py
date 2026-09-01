from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.audit_n12_gate7_two_chord_interval_sign_stop import build_payload


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_TWO_CHORD_INTERVAL_SIGN_STOP.json"
)


def _record() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_interval_sign_stop_regenerates() -> None:
    record = _record()
    assert json.dumps(record, sort_keys=True) == json.dumps(
        build_payload(), sort_keys=True
    )
    assert record["validation_passed"] is True


def test_positive_centers_are_not_promoted_to_interval_sign() -> None:
    frontier = _record()["signed_center_frontier"]
    assert frontier["positive_centers"] == 130
    assert frontier["minimum_u_rate"] > 0.0
    assert frontier["interval_sign_authority"] is False


def test_three_representations_share_one_owner() -> None:
    representations = _record()["three_representation_stop"]
    assert len(representations) == 3
    assert representations["A_full_coordinate_direct_interval"][
        "replay_diagnostic"
    ]["interval_Neumann_factor"] > 1.0
    assert "D5_KATO" in representations[
        "B_covariant_pole_free_hard_bundle"
    ]["failure_owner"]
    assert "D5_KATO" in representations[
        "C_implicit_adjoint_center_jets"
    ]["failure_owner"]


def test_no_go_scope_and_claim_boundary() -> None:
    record = _record()
    assert record["canonical_blocker"]["retained_action_incompatibility_proved"] is False
    assert record["Gate7_status_changed"] is False
    assert record["chord_03_authorized"] is False
    assert record["FULL_BHSM_COMPLETE"] is False


def test_interval_sign_stop_is_content_addressable() -> None:
    digest = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest().upper()
    assert digest == "E319C32F459FEC9C4F3F2AD595917D6FFEA18A3A014E9F15243CB6CEB28EB998"
