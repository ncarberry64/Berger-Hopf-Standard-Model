import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT / "artifacts" / "qxi_relative_energy_preparation"
    / "BHSM_N12_MATCHED_PARENT_QXI_OWNERSHIP.json"
)


def test_qxi_ownership_gate_is_precisely_fail_closed():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["CONTINUUM_EVENT_CHILD_CERTIFIED"] is True
    assert payload["Q_xi_evaluated"] is False
    assert payload["Delta_H_evaluated"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["required_matched_parent_map"][
        "defined_by_current_N12_state_or_action_API"
    ] is False
    assert payload["required_matched_parent_map"][
        "event_side_is_the_required_matched_parent"
    ] is False
    assert payload["required_boundary_improved_charge"][
        "complete_common_reference_Q_xi_assembler_available"
    ] is False
    assert payload["upstream_parent_composite_action_provenance"][
        "master_action_closed"
    ] is False
    assert payload["upstream_parent_composite_action_provenance"][
        "exact_missing_object"
    ] == "COVARIANT_BULK_BOUNDARY_REDUCTION_FUNCTOR"
    assert all(
        row["is_Q_xi"] is False and row["is_Delta_H"] is False
        for row in payload["available_local_diagnostic_only"]
    )
