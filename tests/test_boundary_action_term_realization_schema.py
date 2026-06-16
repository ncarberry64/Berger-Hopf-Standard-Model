import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_action_terms import export_outputs  # noqa: E402


def test_boundary_action_term_realization_results_schema():
    export_outputs(ROOT)
    payload = json.loads(
        (ROOT / "theory" / "boundary_action_term_realization_results.json").read_text()
    )

    assert payload["status"] == "candidate_only"
    assert payload["branch"] == "bhsm-boundary-action-term-realization-audit-v1"
    assert payload["official_predictions_changed"] is False
    assert payload["frozen_predictions_changed"] is False
    assert payload["standard_model_fully_derived"] is False
    assert payload["bhsm_replacement_claim_allowed"] is False
    assert payload["boundary_action_fully_derived"] is False
    assert payload["full_hessian_proof_complete"] is False
    assert payload["candidate_functionals"] == {
        "S_phase": "|exp(i d theta)-1|^2",
        "S_orientation": "||R^2-I||^2 + lambda_trace |Tr(R)|^2",
        "S_cyclic_channel": "cyclic closure U_3^3=I with minimal cyclic channel diagnostic",
        "S_topographic": "L_T = nabla^2 - B nabla^4 branch scaffold",
        "S_excess": "gamma max(d-3,0)^2",
    }
    assert payload["diagnostic_selected_low_energy_dims"] == [1, 2, 3]
    assert payload["bridges_preserved"] == {
        "boundary_action_hessian_scaffold": True,
        "closure_spectrum_selection": True,
        "finite_boundary_algebra_bridge": True,
        "projector_eigenvalue_bridge": True,
        "charge_hypercharge_bridge": True,
        "anomaly_closure_bridge": True,
    }
    for label in [
        "BOUNDARY_ACTION_TERM_REALIZATION_AUDIT_COMPLETE",
        "ACTION_TERMS_SUPPORT_CLOSURE_SCAFFOLD_DIAGNOSTIC",
        "BOUNDARY_ACTION_DERIVATION_REMAINS_OPEN",
        "FULL_HESSIAN_PROOF_REMAINS_OPEN",
        "FULL_SM_DERIVATION_NOT_CLAIMED",
    ]:
        assert label in payload["verdict_labels"]

