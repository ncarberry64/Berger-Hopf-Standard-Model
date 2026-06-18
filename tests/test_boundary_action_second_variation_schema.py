import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_second_variation import export_outputs  # noqa: E402


def test_boundary_action_second_variation_results_schema():
    export_outputs(ROOT)
    payload = json.loads(
        (ROOT / "theory" / "boundary_action_second_variation_results.json").read_text()
    )

    assert payload["status"] == "candidate_only"
    assert payload["branch"] == "bhsm-boundary-action-second-variation-audit-v1"
    assert payload["official_predictions_changed"] is False
    assert payload["frozen_predictions_changed"] is False
    assert payload["standard_model_fully_derived"] is False
    assert payload["bhsm_replacement_claim_allowed"] is False
    assert payload["boundary_action_fully_derived"] is False
    assert payload["full_hessian_proof_complete"] is False
    assert payload["second_variation_audit_complete"] is True
    assert payload["second_variation_coefficients"]["H_phase_d"] == "2 d^2"
    assert payload["second_variation_coefficients"]["H_orientation"] == (
        "8 I + 2 lambda_trace J"
    )
    assert payload["second_variation_coefficients"]["H_cyclic_3"] == "18"
    assert payload["hessian_projector_bridge"] == {
        "P_ref": "reference-normalized",
        "P_orient": "orientation involution Hessian block",
        "P_cyclic": "cyclic-channel Hessian coefficient",
        "P_excess": "excess/gapped Hessian coefficient",
    }
    assert payload["diagnostic_selected_low_energy_dims"] == [1, 2, 3]
    assert payload["bridges_preserved"] == {
        "boundary_action_term_realization": True,
        "boundary_action_hessian_scaffold": True,
        "closure_spectrum_selection": True,
        "finite_boundary_algebra_bridge": True,
        "projector_eigenvalue_bridge": True,
        "charge_hypercharge_bridge": True,
        "anomaly_closure_bridge": True,
    }
    for label in [
        "BOUNDARY_ACTION_SECOND_VARIATION_AUDIT_COMPLETE",
        "ACTION_TERMS_TO_HESSIAN_PROJECTORS_DIAGNOSTIC",
        "BOUNDARY_ACTION_DERIVATION_REMAINS_OPEN",
        "FULL_HESSIAN_PROOF_REMAINS_OPEN",
        "FULL_SM_DERIVATION_NOT_CLAIMED",
    ]:
        assert label in payload["verdict_labels"]

