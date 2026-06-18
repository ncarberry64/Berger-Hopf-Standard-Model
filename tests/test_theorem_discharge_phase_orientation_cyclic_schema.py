import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_theorem_discharge_phase_orientation_cyclic import export_outputs  # noqa: E402


def test_theorem_discharge_phase_orientation_cyclic_results_schema():
    export_outputs(ROOT)
    payload = json.loads(
        (ROOT / "theory" / "theorem_discharge_phase_orientation_cyclic_results.json").read_text()
    )

    assert payload["status"] == "theorem_discharge_candidate"
    assert payload["branch"] == "bhsm-theorem-discharge-phase-orientation-cyclic-v1"
    assert payload["official_predictions_changed"] is False
    assert payload["frozen_predictions_changed"] is False
    assert payload["standard_model_fully_derived"] is False
    assert payload["bhsm_replacement_claim_ready"] is False
    assert payload["closure_selection_layer_discharged_conditionally"] is True
    assert payload["primitive_low_energy_closure_spectrum"] == [1, 2, 3]
    assert set(payload["discharged_obligations"]) == {"PO-BH-2", "PO-BH-3", "PO-BH-4", "PO-BH-8"}
    assert payload["bridges_preserved"]["boundary_action_second_variation"] is True
    for label in [
        "THEOREM_DISCHARGE_PHASE_ORIENTATION_CYCLIC_COMPLETE",
        "PO_BH_2_PHASE_CLOSURE_DERIVED_CONDITIONAL",
        "PO_BH_3_ORIENTATION_INVOLUTION_DERIVED_CONDITIONAL",
        "PO_BH_4_MINIMAL_CYCLIC_CHANNEL_DERIVED_CONDITIONAL",
        "PO_BH_8_CLOSURE_SPECTRUM_123_DERIVED_CONDITIONAL",
        "BHSM_REPLACEMENT_CLAIM_NOT_READY",
    ]:
        assert label in payload["verdict_labels"]

