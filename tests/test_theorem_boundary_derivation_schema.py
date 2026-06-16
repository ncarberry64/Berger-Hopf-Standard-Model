import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_theorem_boundary_derivation import export_outputs  # noqa: E402


def test_theorem_boundary_derivation_status_schema():
    export_outputs(ROOT)
    payload = json.loads((ROOT / "theory" / "bhsm_boundary_derivation_status.json").read_text())

    assert payload["status"] == "theorem_scaffold_candidate"
    assert payload["branch"] == "bhsm-theorem-level-boundary-action-derivation-v1"
    assert payload["official_predictions_changed"] is False
    assert payload["frozen_predictions_changed"] is False
    assert payload["standard_model_fully_derived"] is False
    assert payload["bhsm_replacement_claim_allowed"] is False
    assert payload["boundary_action_fully_derived"] is False
    assert payload["full_hessian_proof_complete"] is False
    assert payload["closure_spectrum_theorem_complete"] is False
    assert payload["finite_algebra_theorem_complete"] is False
    assert payload["charge_anomaly_theorem_complete"] is False
    assert payload["axiom_count_minimum"] == 9
    assert payload["theorem_count_minimum"] == 8
    assert payload["proof_obligation_count_minimum"] == 12
    assert payload["open_proof_obligations"] == [f"PO-BH-{index}" for index in range(1, 13)]
    assert payload["bridges_preserved"]["boundary_action_second_variation"] is True
    assert payload["counts"]["axioms"] >= 9
    assert payload["counts"]["theorems"] >= 8
    assert payload["counts"]["proof_obligations"] >= 12
    for label in [
        "THEOREM_LEVEL_BOUNDARY_ACTION_DERIVATION_SCAFFOLD_COMPLETE",
        "BHSM_BOUNDARY_AXIOM_LEDGER_CREATED",
        "BHSM_BOUNDARY_THEOREM_STATEMENTS_CREATED",
        "BHSM_BOUNDARY_LEMMA_LEDGER_CREATED",
        "BHSM_BOUNDARY_PROOF_OBLIGATION_LEDGER_CREATED",
        "BHSM_BOUNDARY_NON_TAUTOLOGY_AUDIT_CREATED",
        "FULL_SM_DERIVATION_NOT_CLAIMED",
    ]:
        assert label in payload["verdict_labels"]

