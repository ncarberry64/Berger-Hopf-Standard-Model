import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_projector_algebra import export_outputs  # noqa: E402


def test_boundary_projector_algebra_results_schema():
    export_outputs(ROOT)
    payload = json.loads((ROOT / "theory" / "boundary_projector_algebra_results.json").read_text())

    assert payload["status"] == "candidate_only"
    assert payload["branch"] == "bhsm-boundary-projector-algebra-gate-v1"
    assert payload["official_predictions_changed"] is False
    assert payload["frozen_predictions_changed"] is False
    assert payload["standard_model_fully_derived"] is False
    assert payload["bhsm_replacement_claim_allowed"] is False
    assert payload["projector_algebra_derived_from_geometry"] is False
    assert payload["primitive_derivation_complete"] is False

    assert payload["projector_eigenvalues"] == {
        "P_C": "C in {0,1}",
        "P_ell": "ell in {0,1}",
        "S_sigma": "sigma in {-1,+1}",
        "P_w": "w in {0,1}",
    }
    assert payload["candidate_constraints"] == {
        "P_C_plus_P_ell": "I",
        "C_plus_ell": 1,
        "channel_multiplicity": "1 + 2C",
    }
    assert payload["bridges_confirmed"] == {
        "boundary_state_bridge": True,
        "charge_hypercharge_bridge": True,
        "anomaly_closure_bridge": True,
    }

    expected_labels = {
        "BOUNDARY_PROJECTOR_ALGEBRA_GATE_COMPLETE",
        "C_ELL_SIGMA_W_AS_PROJECTOR_EIGENVALUES_CANDIDATE",
        "FERMION_CLOSURE_COMPLEMENTARITY_CANDIDATE",
        "CHANNEL_MULTIPLICITY_RULE_CANDIDATE",
        "PROJECTOR_TO_SM_CHARGE_BRIDGE_CONFIRMED_DIAGNOSTIC",
        "PROJECTOR_TO_ANOMALY_CLOSURE_CONFIRMED_DIAGNOSTIC",
        "PROJECTOR_ALGEBRA_DERIVATION_REMAINS_OPEN",
        "FULL_SM_DERIVATION_NOT_CLAIMED",
        "FROZEN_PREDICTIONS_UNCHANGED",
        "OFFICIAL_PREDICTIONS_UNCHANGED",
    }
    assert expected_labels.issubset(set(payload["verdict_labels"]))
