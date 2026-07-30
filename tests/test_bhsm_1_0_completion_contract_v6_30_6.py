from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface import bhsm_1_0_completion_contract as contract


def test_source_main_and_governance_only_version_are_pinned():
    assert contract.SOURCE_MAIN_SHA == (
        "e39f936b285d1917e29ed4803dc5e46e65e4bfc2"
    )
    assert contract.VERSION == "v6.30.6"
    assert contract.GUARDS["scientific_formula_changed"] is False


def test_exactly_three_cumulative_completion_tiers():
    tiers = contract.tier_definitions()
    assert [row["tier"] for row in tiers] == ["A", "B", "C"]
    assert all(row["cumulative"] is True for row in tiers)
    assert tiers[0]["possible_verdict"] == "BHSM_CORE_COMPLETE"
    assert tiers[2]["possible_verdict"] == "BHSM_1_0_RELEASE_COMPLETE"


def test_one_scale_allowance_has_all_seven_required_conditions():
    allowance = contract.tier_definitions()[1]["one_scale_allowance"]
    assert len(allowance) == 7
    assert all(allowance.values())
    assert allowance["no_dimensionless_fit"] is True


def test_all_six_release_gates_are_explicit_and_not_falsely_closed():
    gates = contract.gate_rows()
    assert [row["gate_id"] for row in gates] == [
        "G1",
        "G2",
        "G3",
        "G4",
        "G5",
        "G6",
    ]
    assert all(row["status"] != "CLOSED" for row in gates)
    assert contract.completion_payload()["BHSM_1_0_release_complete"] is False


def test_every_open_item_has_release_blocking_field():
    rows = contract.release_blockers() + contract.post_1_0_backlog()
    assert all("release_blocking" in row for row in rows)
    assert contract.validate_contract()[
        "every_open_item_has_release_blocking"
    ]


def test_every_release_blocker_has_rationale_and_headline_deliverable():
    for row in contract.release_blockers():
        assert row["release_blocking"] is True
        assert row["release_relevance_rationale"]
        assert row["affected_headline_deliverables"]
        assert row["gate"].startswith("G")


def test_every_nonblocking_item_has_post_1_0_category():
    for row in contract.post_1_0_backlog():
        assert row["release_blocking"] is False
        assert row["post_1_0_category"]
        assert row["status"] == "POST_BHSM_1_0_RESEARCH_BACKLOG"


def test_peer_review_and_institutional_acceptance_are_external():
    scope = contract.scope_payload()
    assert scope["peer_review_internal_blocker"] is False
    assert scope["institutional_acceptance_internal_blocker"] is False
    external = {
        row["post_1_0_category"]: row
        for row in contract.post_1_0_backlog()
    }["external_acceptance"]
    assert external["release_blocking"] is False


def test_arbitrary_higher_orders_are_not_blocking_without_dependency():
    scope = contract.scope_payload()
    assert scope["arbitrary_higher_order_internal_blocker"] is False
    categories = {
        row["post_1_0_category"]
        for row in contract.post_1_0_backlog()
    }
    assert "arbitrary_perturbative_orders" in categories
    assert "isolated_cancellation_higher_order" in categories


def test_exact_branch_restoration_is_completed_obstruction_not_release_gate():
    row = contract.exact_branch_scope_row()
    assert row["release_blocking"] is False
    assert row["status"] == "COMPLETED_SCIENTIFIC_OBSTRUCTION"
    assert row["inequality_holds"] is True
    assert (
        row["branch_cancellation_lambda5"]
        < row["quartic_minimum_threshold"]
    )


def test_scalar_quartic_is_next_highest_upstream_tractable_blocker():
    payload = contract.dag_payload()
    assert payload["highest_upstream_tractable_blocker"] == (
        "RB-02_SCALAR_QUARTIC_INVARIANT_SELECTION"
    )
    blockers = {
        row["blocker_id"]: row for row in contract.release_blockers()
    }
    assert blockers["RB-02"]["tractable_now"] is True
    assert "canonical quartic" in " ".join(
        blockers["RB-02"]["affected_headline_deliverables"]
    )


def test_historical_completion_ledgers_are_extended_not_replaced():
    rows = contract.dag_payload()["historical_ledgers_extended"]
    assert "docs/BHSM_HARD_CLOSURE_STATUS.json" in rows
    assert (
        "artifacts/BHSM_full_completion_blocker_ledger_v1_8.json" in rows
    )


def test_contract_has_no_new_physics_or_forbidden_claim():
    for key, value in contract.GUARDS.items():
        assert value is False, key


def test_frozen_hashes_match_integrity_audit_constants():
    audit_text = (
        ROOT / "tools" / "audit_frozen_prediction_integrity.py"
    ).read_text(encoding="utf-8")
    for digest in contract.FROZEN_HASHES.values():
        assert digest in audit_text


def test_exactly_three_deterministic_artifacts():
    assert len(contract.ARTIFACT_FILES) == 3
    assert set(contract.artifact_payloads()) == set(contract.ARTIFACT_FILES)
    first = contract.artifact_bytes()
    second = contract.artifact_bytes()
    assert first == second
    assert {
        name: hashlib.sha256(content).hexdigest()
        for name, content in first.items()
    } == {
        name: hashlib.sha256(content).hexdigest()
        for name, content in second.items()
    }


def test_artifact_schema_keeps_release_and_post_1_0_items_separate():
    payload = contract.completion_payload()
    assert payload["RB01"]["release_blocking"] is False
    assert payload["RB01"]["status"] == "CLOSED"
    assert payload["parameter_free_extension_blocker"] == "RB-02"
    assert payload["open_release_blockers"] == ["RB-15", "RB-16"]
    assert payload["next_highest_upstream_blocker"] == (
        "UNIVERSAL_RESPONSE_WITH_NO_FAMILY_RESOLUTION"
    )


def test_checked_in_artifacts_are_current_and_valid_json():
    for name, content in contract.artifact_bytes().items():
        path = ROOT / "artifacts" / name
        assert path.read_bytes() == content
        json.loads(content)


def test_materializer_is_idempotent():
    script = (
        ROOT
        / "scripts"
        / "materialize_bhsm_1_0_completion_contract_v6_30_6.py"
    )
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
    first = {
        name: (ROOT / "artifacts" / name).read_bytes()
        for name in contract.ARTIFACT_FILES.values()
    }
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
    second = {
        name: (ROOT / "artifacts" / name).read_bytes()
        for name in contract.ARTIFACT_FILES.values()
    }
    assert first == second == contract.artifact_bytes()
