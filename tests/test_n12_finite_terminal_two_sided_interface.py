import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts/flagship_integration"
SCRIPT = ROOT / "scripts/certify_n12_finite_terminal_two_sided_interface.py"
ARTIFACT = BASE / "BHSM_N12_FINITE_TERMINAL_TWO_SIDED_FORWARD_INTERFACE.json"
EVENT_LINE = BASE / "BHSM_N12_FINITE_TERMINAL_EVENT_EIGENLINE_SOLUTION_BALL.json"


def _module():
    spec = importlib.util.spec_from_file_location("two_sided_terminal", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_terminal_interface_has_incoming_and_outgoing_orientations():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["event_outgoing_orientation"]["root_c_psi_lower"] > 0.0
    assert payload["event_outgoing_orientation"]["root_b_psi_lower"] > 0.0
    assert payload["validation"][
        "terminal_root_and_child_incoming_orientation_certified"
    ] is True


def test_event_solution_line_is_validated_and_portable():
    payload = json.loads(EVENT_LINE.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["sector"] == "event"
    assert payload["bounds"]["eigenline_gap_lower"] > 0.0
    assert payload["bounds"]["eigenvector_graph_norm"] < 1.0e-9
    assert not Path(payload["checkpoint"]).is_absolute()
    assert not Path(payload["action_majorant"]).is_absolute()


def test_reset_projection_closes_local_positive_duration_family():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    crosscheck = payload["reset_projection_crosscheck"]
    assert crosscheck["full_reset_rank"] == 57
    assert crosscheck["event_block_rank"] == 32
    assert crosscheck["child_block_rank"] == 31
    assert crosscheck["child_projection_rank"] == 73
    assert crosscheck["incoming_soft_unit_projection_residual"] < 1.0e-12
    assert payload["claim_boundary"][
        "positive_duration_forward_child_history"
    ] == "CERTIFIED_LOCAL_EXISTENCE"
    assert payload["exact_local_theorem"][
        "physical_chronology"
    ] == "E0_TO_C1_TO_[T>0]_E1_TO_C2"
    assert payload["exact_local_theorem"][
        "same_event_recurrence_required"
    ] is False
    assert payload["claim_boundary"][
        "compact_finite_endpoint_operator"
    ] == "OPEN_CURRENT_OWNER"
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_two_sided_interface_artifact_is_reproducible():
    assert _module().build_payload() == json.loads(
        ARTIFACT.read_text(encoding="utf-8")
    )
