import json
from pathlib import Path

from bhsm.interface.aether_scale_child_ownership_audit_v16_78 import scale_ownership_audit


ROOT = Path(__file__).resolve().parents[1]

def test_scale_ownership_does_not_delete_a_physical_residual():
    audit=scale_ownership_audit()
    assert audit["configuration_ownership"]["reset_log_scale_is_KKT_unknown"] is False
    assert audit["measured_frontier"]["free_log_scale_nodes"]==audit["measured_frontier"]["log_scale_stationarity_rows"]
    assert audit["verdict"]["continue_current_metric_Gauss_Newton"] is True

def test_scale_child_ownership_audit_validates():
    path = ROOT / "artifacts" / "BHSM_aether_scale_child_ownership_audit_v16_78.json"
    retained = json.loads(path.read_text(encoding="utf-8"))
    audit = retained["scale_child_ownership_audit"]
    assert retained["validation_passed"] is True
    assert retained["FULL_BHSM_COMPLETE"] is False
    assert audit["derived_future_reconstruction_constraint"]["current_open_event_orbit_count"] == {
        "equations": 376,
        "square": True,
        "unknowns": 376,
    }
    assert audit["configuration_ownership"]["reset_log_scale_is_KKT_unknown"] is False
