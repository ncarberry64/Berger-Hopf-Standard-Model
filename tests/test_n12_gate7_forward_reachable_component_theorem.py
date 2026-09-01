from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.audit_n12_gate7_forward_reachable_component_theorem import (
    build_payload,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_FORWARD_REACHABLE_COMPONENT_THEOREM_AUDIT.json"
)


def _record() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_forward_reachable_theorem_audit_regenerates() -> None:
    record = _record()
    assert json.dumps(record, sort_keys=True) == json.dumps(
        build_payload(), sort_keys=True
    )
    assert record["validation_passed"] is True
    assert record["Gate7_status_changed"] is False


def test_only_semigroup_and_transport_core_survives() -> None:
    clauses = _record()["clause_adjudication"]
    assert clauses["1_forward_invariance"]["adjudication"] == (
        "VALID_AFTER_REPLACING_COMPONENT_BY_REACHABLE_SET"
    )
    assert clauses["1_forward_invariance"][
        "global_connected_component_proved"
    ] is False
    assert clauses["5_component_restricted_transport"]["adjudication"] == (
        "VALID_ON_EACH_REGULAR_SIMPLE_EIGENLINE_INTERVAL"
    )
    assert clauses["5_component_restricted_transport"][
        "sign_or_absolute_bound_proved"
    ] is False


def test_reflection_disjointness_is_not_fabricated() -> None:
    clauses = _record()["clause_adjudication"]
    assert clauses["2_reflection_is_distinct_pairing"]["adjudication"] == (
        "PARTLY_VALID"
    )
    assert clauses["3_reflection_transition_requires_stop"]["adjudication"] == (
        "NOT_PROVED"
    )
    assert _record()["theorem_that_is_currently_proved"][
        "reflection_disjointness_included"
    ] is False


def test_infinite_regular_history_is_retained() -> None:
    clause = _record()["clause_adjudication"]["6_two_outcome_gate7_dichotomy"]
    assert clause["adjudication"] == (
        "INVALID_AS_STATED;_REPLACE_BY_THREE_OUTCOMES"
    )
    assert clause["retained_exhaustive_outcomes"][-1] == (
        "INFINITE_REGULAR_FORWARD_HISTORY_WITH_EVENT_NONZERO_FOR_ALL_FINITE_TIME"
    )
    assert clause["any_one_outcome_selected"] is False


def test_claim_boundary_and_chord_03_remain_closed() -> None:
    record = _record()
    assert record["two_chord_global_promotion_authorized"] is False
    assert record["chord_03_proof_value_established"] is False
    assert record["chord_03_authorized"] is False
    assert record["FULL_BHSM_COMPLETE"] is False


def test_forward_reachable_theorem_artifact_is_content_addressable() -> None:
    digest = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest().upper()
    assert digest == "CCBBF373BE3F596C5BBF5E6236288FA8ADB749692359628FCD0D635249ECBDBF"
