import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_admissible_closure_spectrum import export_outputs  # noqa: E402


def test_admissible_closure_spectrum_results_schema():
    export_outputs(ROOT)
    payload = json.loads(
        (ROOT / "theory" / "admissible_boundary_closure_spectrum_results.json").read_text()
    )

    assert payload["status"] == "candidate_only"
    assert payload["branch"] == "bhsm-admissible-boundary-closure-spectrum-gate-v1"
    assert payload["official_predictions_changed"] is False
    assert payload["frozen_predictions_changed"] is False
    assert payload["standard_model_fully_derived"] is False
    assert payload["bhsm_replacement_claim_allowed"] is False
    assert payload["closure_spectrum_uniquely_derived"] is False
    assert payload["full_hessian_proof_complete"] is False
    assert payload["admissible_diagnostic_dimensions"] == [1, 2, 3]
    assert payload["filters"] == {
        "hopf_phase_closure": "candidate diagnostic",
        "topographic_stability": "candidate diagnostic",
    }
    assert payload["endomorphism_blocks"] == {
        "End(C^1)": "C",
        "End(C^2)": "M2(C)",
        "End(C^3)": "M3(C)",
    }
    assert payload["bridges_preserved"] == {
        "finite_boundary_algebra_bridge": True,
        "projector_eigenvalue_bridge": True,
        "charge_hypercharge_bridge": True,
        "anomaly_closure_bridge": True,
    }

    expected = {
        "ADMISSIBLE_BOUNDARY_CLOSURE_SPECTRUM_GATE_COMPLETE",
        "HOPF_PHASE_CLOSURE_FILTER_CANDIDATE",
        "TOPOGRAPHIC_STABILITY_CLOSURE_FILTER_CANDIDATE",
        "MINIMAL_CLOSURE_SPECTRUM_123_DIAGNOSTIC",
        "CLOSURE_SPECTRUM_TO_FINITE_ALGEBRA_BRIDGE_CONFIRMED_DIAGNOSTIC",
        "UNIQUE_FIRST_PRINCIPLES_CLOSURE_DERIVATION_REMAINS_OPEN",
        "FULL_HESSIAN_PROOF_REMAINS_OPEN",
        "FULL_SM_DERIVATION_NOT_CLAIMED",
        "FROZEN_PREDICTIONS_UNCHANGED",
        "OFFICIAL_PREDICTIONS_UNCHANGED",
    }
    assert expected.issubset(set(payload["verdict_labels"]))
