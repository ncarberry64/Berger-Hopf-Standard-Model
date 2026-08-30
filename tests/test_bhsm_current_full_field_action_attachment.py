from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_bhsm_current_full_field_action_attachment.py"
ARTIFACT = ROOT / "artifacts/BHSM_CURRENT_FULL_FIELD_ACTION_ATTACHMENT_AUDIT.json"


def _module():
    spec = importlib.util.spec_from_file_location("full_field_attachment_audit", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_current_local_action_scope_is_geometry_only() -> None:
    payload = _module().build_payload()
    state = payload["current_retained_action_state"]
    assert state == {
        "geometry_coordinates": 37,
        "geometry_velocities": 37,
        "constraint_multipliers": 24,
        "total_state_dimension": 98,
        "retained_order": 12,
        "gauge_and_ghost_fields": 0,
        "fermion_fields": 0,
        "HS_or_scalar_fields": 0,
    }
    assert payload["decision"].endswith("INSTANTIATE_UNIVERSAL_SM_S2_S3_S4")


def test_domain_ownership_is_not_relabelled_as_full_field_action() -> None:
    payload = _module().build_payload()
    ae2 = payload["ae2_domain_result"]
    assert ae2["global_fermion_reset_domain_owned"] is True
    assert ae2["new_continuous_coefficient"] is None
    assert ae2["new_physical_scale"] is None
    assert ae2["new_propagating_field"] is None
    assert ae2["field_action_attachment_completed"] is False
    assert payload["scientific_boundary"]["root_nonexistence_claimed"] is False


def test_brst_and_retained_components_are_credited_without_promotion() -> None:
    payload = _module().build_payload()
    infrastructure = payload["implemented_complementary_infrastructure"]
    assert infrastructure["explicit_BRST_physical_nullspace_quotient"] is True
    assert infrastructure["explicit_Faddeev_Popov_regularity_check"] is True
    assert infrastructure["physical_action_inputs_supplied_by_BRST_module"] is False
    retained = payload["retained_component_evidence"]
    assert retained["global_SM_bundle_and_representations_fixed"] is True
    assert retained["historical_centers_promoted"] is False
    assert retained["complete_current_full_field_action_materialized"] is False


def test_fail_closed_certificate_names_minimum_missing_attachment() -> None:
    payload = _module().build_payload()
    required_blocks = {
        "gauge_and_ghost_fields",
        "fermion_fields",
        "HS_or_scalar_fields",
        "geometry_gauge_cross_derivatives",
        "geometry_fermion_cross_derivatives",
        "geometry_HS_cross_derivatives",
        "gauge_fermion_HS_cross_derivatives",
    }
    assert required_blocks == set(payload["missing_physical_field_blocks"])
    minimum = set(payload["minimum_promotion_inputs"])
    assert "same_action_value_and_derivatives_orders_1_through_4" in minimum
    assert "history_and_seam_action_assembly" in minimum
    assert "current_action_owned_local_momentum_symbol" in minimum
    assert payload["scientific_boundary"]["physical_prediction_promotion"] == "BLOCKED"
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["validation_passed"] is True


def test_materialized_artifact_matches_builder_and_hashes() -> None:
    module = _module()
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert stored == module.build_payload()
    for relative, digest in stored["source_sha256"].items():
        assert module._sha256(ROOT / relative) == digest
