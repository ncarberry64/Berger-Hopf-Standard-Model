import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "artifacts" / "n12_continuum_source_compatibility_checkpoint"
MANIFEST = CHECKPOINT / "BHSM_N12_CONTINUUM_SOURCE_COMPATIBILITY_MANIFEST.json"


def _load(name):
    return json.loads((CHECKPOINT / name).read_text(encoding="utf-8"))


def test_checkpoint_hashes_and_claim_boundary():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for item in manifest["files"]:
        path = ROOT / item["path"]
        payload = path.read_bytes()
        assert len(payload) == item["bytes"]
        assert hashlib.sha256(payload).hexdigest().upper() == item["SHA256"]
    assert manifest["scientific_status"]["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
    assert manifest["scientific_status"]["FULL_BHSM_COMPLETE"] is False
    assert manifest["new_equation_constraint_gate_scale_fit_prediction_or_event_definition"] is False


def test_eta_completed_ward_identity_reconstructs_exact_shift_rows():
    payload = _load("BHSM_N12_RADIAL_DIFFEO_NOETHER_COMPATIBILITY_AUDIT.json")
    assert payload["validation_passed"] is True
    assert payload["validation"][
        "eta_completed_exact_shift_rows_reconstructed_to_1e_minus_10"
    ] is True
    assert "ETA_CLOCK_CURRENT" in payload["classification"]
    assert payload["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False


def test_n48_results_remain_diagnostic_and_gauge_quotient_isolated():
    correction = _load("BHSM_N48_LINEAR_SOURCE_CORRECTION_NONLINEAR_AUDIT.json")
    projector = _load("BHSM_N48_ORDERED_EVENT_PROJECTOR_CLUSTER_AUDIT.json")
    assert correction["validation_passed"] is True
    assert correction["zero_padded_or_linear_state_promoted_as_root"] is False
    assert projector["validation_passed"] is True
    assert projector["validation"][
        "gauge_quotient_branch_isolated_on_both_states"
    ] is True
    assert projector["linear_candidate_promoted_as_root"] is False
    assert projector["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
