import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_finite_boundary_algebra import export_outputs  # noqa: E402


def test_finite_boundary_algebra_results_schema():
    export_outputs(ROOT)
    payload = json.loads((ROOT / "theory" / "finite_boundary_algebra_results.json").read_text())

    assert payload["status"] == "candidate_only"
    assert payload["branch"] == "bhsm-finite-boundary-algebra-source-gate-v1"
    assert payload["official_predictions_changed"] is False
    assert payload["frozen_predictions_changed"] is False
    assert payload["standard_model_fully_derived"] is False
    assert payload["bhsm_replacement_claim_allowed"] is False
    assert payload["finite_boundary_algebra_derived_from_geometry"] is False
    assert payload["projector_algebra_sourced_diagnostically"] is True

    assert payload["algebra"] == {
        "A_boundary_candidate": "A_channel tensor A_weak",
        "A_channel": "C_ell direct_sum M3(C)_C",
        "A_weak": "M2(C)_{w=1} direct_sum C_{sigma=+} direct_sum C_{sigma=-}",
    }
    assert payload["projector_sources"] == {
        "P_C": "central projection onto M3(C)_C",
        "P_ell": "central projection onto C_ell",
        "P_w": "central projection onto M2(C)_{w=1}",
        "S_sigma": "orientation grading",
    }
    assert payload["charge_operators"] == {
        "T3": "1/2 P_w S_sigma",
        "Y": "4/3 P_C - I + (I-P_w) S_sigma",
        "Q": "1/2(S_sigma - I) + 2/3 P_C",
    }
    assert payload["bridges_confirmed"] == {
        "projector_eigenvalue_bridge": True,
        "charge_hypercharge_bridge": True,
        "anomaly_closure_bridge": True,
    }

    expected_labels = {
        "FINITE_BOUNDARY_ALGEBRA_SOURCE_GATE_COMPLETE",
        "PROJECTORS_AS_FINITE_ALGEBRA_CENTRAL_PROJECTIONS_CANDIDATE",
        "ORIENTATION_GRADING_SOURCE_FOR_SIGMA_CANDIDATE",
        "CHANNEL_BLOCK_SOURCE_FOR_COLOR_TRIPLICITY_CANDIDATE",
        "WEAK_INTERFACE_BLOCK_SOURCE_FOR_W_CANDIDATE",
        "CHARGE_OPERATOR_SIMPLIFICATION_CONFIRMED_DIAGNOSTIC",
        "FINITE_ALGEBRA_DERIVATION_REMAINS_OPEN",
        "FULL_SM_DERIVATION_NOT_CLAIMED",
        "FROZEN_PREDICTIONS_UNCHANGED",
        "OFFICIAL_PREDICTIONS_UNCHANGED",
    }
    assert expected_labels.issubset(set(payload["verdict_labels"]))
