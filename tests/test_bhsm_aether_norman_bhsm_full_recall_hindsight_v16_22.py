from bhsm.interface.aether_norman_bhsm_full_recall_hindsight_v16_22 import (
    SOURCE_LEDGER,
    completion_payload,
    deterministic_json,
    hindsight_classification,
)


def test_recall_has_complete_unique_source_provenance():
    assert len(SOURCE_LEDGER) == 8
    assert len({row["source"] for row in SOURCE_LEDGER}) == 8
    assert len({row["sha256"] for row in SOURCE_LEDGER}) == 8
    assert all(len(row["sha256"]) == 64 for row in SOURCE_LEDGER)


def test_hindsight_does_not_import_external_normalizations():
    result = hindsight_classification()
    assert any("B_BETA_Q1_Q2_RH_ETA0_ZT" in row for row in result["INVALIDATED"])
    assert any("ONE_COMMON_PARENT_CHILD_PROCESS" in row for row in result["VALIDATED"])
    assert any("376_VARIABLE_N3_KKT" in row for row in result["ACTIVE"])


def test_completion_payload_is_fail_closed_and_deterministic():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["USB_OR_REMOTE_SYNC_AUTHORIZED"] is False
    assert deterministic_json(payload) == deterministic_json(completion_payload())
