from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.audit_n12_gate7_component_separator import build_payload


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_COMPONENT_SEPARATOR_AUDIT.json"
)


def _record() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_component_separator_audit_regenerates() -> None:
    record = _record()
    assert json.dumps(record, sort_keys=True) == json.dumps(
        build_payload(), sort_keys=True
    )
    assert record["validation_passed"] is True
    assert record["separator_kill_test"]["separator_found"] is False
    assert len(record["separator_kill_test"]["candidates"]) == 5


def test_reflection_candidates_fail_for_the_stated_reasons() -> None:
    candidates = _record()["separator_kill_test"]["candidates"]
    assert candidates[0]["decision"] == "REJECT_REFLECTION_EVEN"
    assert candidates[0]["zero_is_existing_stop"] is True
    assert candidates[1]["fixed_event_child_shape"] == [31, 98]
    assert candidates[2]["decision"] == (
        "REJECT_NO_ACTION_OWNED_LINE_ORIENTATION"
    )
    assert candidates[3]["reflection_odd"] is True
    assert candidates[3]["continuous_scalar"] is False
    assert candidates[4]["reset_fiber_dimension"] == 67


def test_three_representation_stop_and_claim_boundary() -> None:
    record = _record()
    representations = record["three_representation_adjudication"]
    assert representations["A_constraint_topology"]["separator_found"] is False
    assert representations["B_differential_transport"][
        "integrated_barrier_found"
    ] is False
    assert representations["C_action_Noether_form"][
        "conserved_or_monotone_separator_found"
    ] is False
    assert record["canonical_no_go_scope"]["retained_action_incompatibility"] is False
    assert record["Gate7_status_changed"] is False
    assert record["chord_03_authorized"] is False
    assert record["FULL_BHSM_COMPLETE"] is False


def test_global_s2_owner_is_localized() -> None:
    owner = _record()["global_S2_owner_localization"]
    assert owner["first_specific_uncontrolled_nonlinear_owner"] == (
        "D(Y)^(-1)*b(Y)"
    )
    assert owner["maximal_flow_already_treats_inverse_divergence_as_stop"] is True
    assert owner["coercive_S2_bound_available"] is False


def test_component_separator_artifact_is_content_addressable() -> None:
    digest = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest().upper()
    assert digest == "E40F4E334D9FC39CCA62EF45B0FA2F8F056F11F3C35BBD2D457889D2B390F0D1"
