import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_action_hessian import export_outputs  # noqa: E402


def test_boundary_action_hessian_results_schema():
    export_outputs(ROOT)
    payload = json.loads((ROOT / "theory" / "boundary_action_hessian_scaffold_results.json").read_text())

    assert payload["status"] == "candidate_only"
    assert payload["branch"] == "bhsm-boundary-action-hessian-scaffold-v1"
    assert payload["official_predictions_changed"] is False
    assert payload["frozen_predictions_changed"] is False
    assert payload["standard_model_fully_derived"] is False
    assert payload["bhsm_replacement_claim_allowed"] is False
    assert payload["full_hessian_proof_complete"] is False
    assert payload["boundary_action_derived"] is False
    assert payload["candidate_action_terms"] == [
        "S_phase",
        "S_orientation",
        "S_cyclic_channel",
        "S_topographic",
        "S_excess",
    ]
    assert payload["hessian_projectors"] == {
        "P_ref": "d=1 reference/single closure",
        "P_orient": "d=2 orientation-pair closure",
        "P_cyclic": "d=3 cyclic three-channel closure",
        "P_excess": "d>=4 higher/composite closures",
    }
    assert payload["bridges_preserved"] == {
        "closure_spectrum_selection": True,
        "finite_boundary_algebra_bridge": True,
        "projector_eigenvalue_bridge": True,
        "charge_hypercharge_bridge": True,
        "anomaly_closure_bridge": True,
    }
    assert "BOUNDARY_ACTION_HESSIAN_SCAFFOLD_GATE_COMPLETE" in payload["verdict_labels"]
    assert "FULL_HESSIAN_PROOF_REMAINS_OPEN" in payload["verdict_labels"]
