import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_CORRECTED_FORWARD_HISTORY_AND_PARTICLE_CLASS_GATES.json"
)


def test_corrected_forward_history_and_particle_class_gates() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    assert record["validation_passed"] is True
    assert record["gate5"]["status"] == "CLOSED"
    assert record["gate6"]["status"] == "CLOSED"
    assert record["reclassification"]["mandatory_terminal_reset_reachability"] == "RETIRED"
    assert record["reclassification"]["mandatory_unique_action_selected_Cauchy_state"] == "RETIRED"
    assert record["claim_boundary"]["gauge_scale_flavor_neutrino"] == "OPEN"
    assert record["FLAGSHIP_READY"] is False
    assert record["FULL_BHSM_COMPLETE"] is False
