import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_closure_spectrum_selection import export_outputs  # noqa: E402


def test_closure_spectrum_selection_results_schema():
    export_outputs(ROOT)
    payload = json.loads((ROOT / "theory" / "closure_spectrum_selection_results.json").read_text())

    assert payload["status"] == "candidate_only"
    assert payload["branch"] == "bhsm-closure-spectrum-selection-rule-audit-v1"
    assert payload["official_predictions_changed"] is False
    assert payload["frozen_predictions_changed"] is False
    assert payload["standard_model_fully_derived"] is False
    assert payload["bhsm_replacement_claim_allowed"] is False
    assert payload["closure_spectrum_uniquely_derived"] is False
    assert payload["full_hessian_proof_complete"] is False
    assert payload["candidate_selected_low_energy_spectrum"] == [1, 2, 3]

    assert payload["audited_dimensions"] == {
        "1": "primitive reference/single closure",
        "2": "primitive orientation-pair closure",
        "3": "primitive cyclic three-channel closure",
        "4": "composite/reducible under current primitive set",
        "5": "higher prime unsupported by current low-energy minimality screens",
        "6": "composite/product-like under current primitive set",
        "7": "higher prime unsupported by current low-energy minimality screens",
        "8": "composite/product-like under current primitive set",
    }
    assert payload["bridges_preserved"] == {
        "closure_spectrum_to_finite_algebra": True,
        "finite_boundary_algebra_bridge": True,
        "projector_eigenvalue_bridge": True,
        "charge_hypercharge_bridge": True,
        "anomaly_closure_bridge": True,
    }
    assert "higher prime closures are unsupported, not impossible" in payload["negative_results"]
    assert "FULL_SM_DERIVATION_NOT_CLAIMED" in payload["verdict_labels"]
