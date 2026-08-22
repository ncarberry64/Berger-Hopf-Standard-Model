import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "artifacts" / "n12_dynamic_calderon_checkpoint"
MANIFEST = CHECKPOINT / "BHSM_N12_DYNAMIC_CALDERON_CHECKPOINT_MANIFEST.json"


def _load(name):
    return json.loads((CHECKPOINT / name).read_text(encoding="utf-8"))


def test_checkpoint_hashes_and_fail_closed_claim_boundary():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for item in manifest["files"]:
        path = ROOT / item["path"]
        payload = path.read_bytes()
        assert len(payload) == item["bytes"]
        assert hashlib.sha256(payload).hexdigest().upper() == item["SHA256"]
    status = manifest["scientific_status"]
    assert status["N64_state_promoted_as_complete_child"] is False
    assert status["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
    assert status["FULL_BHSM_COMPLETE"] is False
    assert manifest[
        "new_equation_constraint_gate_scale_fit_prediction_or_event_definition"
    ] is False


def test_static_projector_shortcut_is_invalidated():
    payload = _load(
        "BHSM_N12_N48_ORDERED_EVENT_FESHBACH_EQUIVALENCE_AUDIT.json"
    )
    assert payload["validation_passed"] is True
    assert "PRINCIPAL_SUBMATRIX_IS_NOT_AN_EQUIVALENT" in payload[
        "classification"
    ]
    n12 = payload["evaluations"]["192"]["12"]["embedded"]
    n48 = payload["evaluations"]["192"]["48"]["embedded"]
    assert n12["principal_submatrix_diagnostic"][
        "is_exact_feshbach_reduction"
    ] is False
    assert n48["shifted_w_shift_block_smallest_singular_value"] < 1.0e-8


def test_source_corrected_dynamic_calderon_probes_remain_transverse():
    n48 = _load("BHSM_N48_SOURCE_CORRECTED_CALDERON_SYMBOL_AUDIT.json")
    n64 = _load("BHSM_N64_SOURCE_CORRECTED_CALDERON_SYMBOL_AUDIT.json")
    assert n48["validation_passed"] is True
    assert n64["validation_passed"] is True
    assert n48["evaluations"]["192"]["linear_candidate"][
        "seven_by_seven_symbol_gap"
    ] > 0.009
    assert n64["evaluations"]["96"]["linear_candidate"][
        "seven_by_seven_symbol_gap"
    ] > 0.003
    assert n64["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False


def test_n64_tail_probe_is_action_cauchy_not_strong_graph_closed():
    payload = _load("BHSM_N64_FULL_QVM_CONSTRAINT_TAIL_DIAGNOSTIC.json")
    assert payload["validation_passed"] is True
    assert max(payload["orders"]) == 64
    assert "N12_TO_N64" in payload["classification"]
    event = payload["exact_source_correction_cauchy_diagnostic"]["event"][0]
    child = payload["exact_source_correction_cauchy_diagnostic"]["child"][0]
    assert event["exact_common_mode_injected_action_distance"] < 0.002
    assert child["exact_common_mode_injected_action_distance"] < 0.002
    assert event["S2_H2q_H1v_H2m_injected_distance"] > 0.25
    assert child["S2_H2q_H1v_H2m_injected_distance"] > 0.15
    assert payload["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
