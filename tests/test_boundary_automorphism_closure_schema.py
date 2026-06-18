import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_automorphism_closure import export_outputs  # noqa: E402


def test_boundary_automorphism_closure_results_schema():
    export_outputs(ROOT)
    payload = json.loads((ROOT / "theory" / "boundary_automorphism_closure_results.json").read_text())

    assert payload["status"] == "candidate_only"
    assert payload["branch"] == "bhsm-boundary-automorphism-closure-origin-gate-v1"
    assert payload["official_predictions_changed"] is False
    assert payload["frozen_predictions_changed"] is False
    assert payload["standard_model_fully_derived"] is False
    assert payload["bhsm_replacement_claim_allowed"] is False
    assert payload["finite_boundary_algebra_fully_derived"] is False
    assert payload["automorphism_closure_origin_documented"] is True
    assert payload["channel_origin"] == {
        "single_channel": "End(C) = C_ell",
        "three_channel": "End(C^3) = M3(C)_C",
    }
    assert payload["weak_origin"] == {
        "active_interface": "End(C^2) = M2(C)_{w=1}",
        "inactive_orientations": "End(C_+) direct_sum End(C_-) = C_{sigma=+} direct_sum C_{sigma=-}",
    }
    assert payload["minimality_audit"] == {
        "diagnostic_requirements_met": True,
        "unique_first_principles_derivation": False,
    }
    assert payload["bridges_preserved"] == {
        "projector_eigenvalue_bridge": True,
        "charge_hypercharge_bridge": True,
        "anomaly_closure_bridge": True,
    }

    expected = {
        "BOUNDARY_AUTOMORPHISM_CLOSURE_ORIGIN_GATE_COMPLETE",
        "CHANNEL_ALGEBRA_FROM_ENDOMORPHISM_BLOCKS_CANDIDATE",
        "WEAK_INTERFACE_ALGEBRA_FROM_ACTIVE_AND_INACTIVE_ORIENTATION_BLOCKS_CANDIDATE",
        "CENTRAL_PROJECTORS_FROM_DIRECT_SUM_ALGEBRA_CANDIDATE",
        "ORIENTATION_GRADING_FROM_Z2_BOUNDARY_INVOLUTION_CANDIDATE",
        "FINITE_BOUNDARY_ALGEBRA_MINIMALITY_DIAGNOSTIC",
        "FINITE_ALGEBRA_DERIVATION_REMAINS_OPEN",
        "FULL_SM_DERIVATION_NOT_CLAIMED",
        "FROZEN_PREDICTIONS_UNCHANGED",
        "OFFICIAL_PREDICTIONS_UNCHANGED",
    }
    assert expected.issubset(set(payload["verdict_labels"]))
