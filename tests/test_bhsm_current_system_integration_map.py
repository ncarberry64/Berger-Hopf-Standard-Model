from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/materialize_bhsm_current_system_integration_map.py"


def _payload():
    spec = importlib.util.spec_from_file_location("bhsm_system_map", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.build_payload()


def test_canonical_system_and_required_subsystems() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    assert payload["validation"]["causal_Z2_nonlinear_halo_is_certified"] is True
    assert payload["validation"][
        "quarter_green_corrected_carrier_is_certified"
    ] is True
    assert payload["validation"][
        "signed_Y_binary_source_noise_is_superseded_by_decimal_repair"
    ] is True
    assert payload["validation"][
        "decimal_Gauss8_PROP16_center_is_frozen_without_source_double_counting"
    ] is True
    assert payload["validation"][
        "causal_proxy_margin_budget_has_strict_exact_rational_headroom"
    ] is True
    assert payload["validation"][
        "affine_Magnus4_recenter_removes_midpoint_leading_defect_numerically"
    ] is True
    assert payload["validation"][
        "aligned_Magnus4_discrete_blocks_and_exponential_roundoff_are_outward_certified"
    ] is True
    assert payload["validation"][
        "global_finite_correlated_Magnus4_affine_composition_is_outward_certified"
    ] is True
    assert payload["validation"][
        "affine_Omega5_identity_is_established_without_binary64_tail_promotion"
    ] is True
    assert payload["validation"][
        "finite_exact_Omega5_augmented_global_composition_is_outward_certified"
    ] is True
    assert payload["validation"][
        "finite_exact_Omega7_augmented_global_composition_is_outward_certified"
    ] is True
    assert payload["validation"][
        "interaction_frame_analytic_infinite_tail_is_certified_without_exact_propagator_promotion"
    ] is True
    assert payload["validation"][
        "correlated_exact_affine_Taylor26_homogeneous_carrier_is_certified"
    ] is True
    assert payload["validation"][
        "correlated_exact_affine_Taylor26_signed_source_is_certified"
    ] is True
    assert payload["validation"][
        "exact_affine_signed_Y_center_transfer_is_certified_and_old_Gauss12_cone_is_rejected"
    ] is True
    assert payload["validation"][
        "physical_completeness_matrix_is_required_and_open"
    ] is True
    assert payload["validation"][
        "binary64_compact_reserve_artifact_is_superseded_by_directed_replay"
    ] is True
    assert payload["validation"][
        "one_transverse_center_witness_suffices_for_open_stop_stratum"
    ] is True
    assert payload["canonical_action_version"] == "BHSM-AE-2.0.0"
    identifiers = {row["id"] for row in payload["subsystems"]}
    assert {
        "STRATIFIED_PARENT_CORE", "SCALE_OBSERVABLE_TRANSPORT",
        "GENERATION_FAMILY_PROJECTORS", "ETA_AETHER_ACTION",
        "AE2_NORMAL_MATTER_TRANSMISSION", "N12_EVENT_RESET_CHILD",
        "C2_DOP853_RESPONSE", "GATE7_HEAT_ZETA_CHAIN", "CKM_SECTOR",
        "NEUTRINO_PMNS_SECTOR", "FROZEN_PREDICTION_SYSTEM",
        "RELEASE_DEFINITION_OF_DONE",
    } <= identifiers
    required = {
        "canonical_action_version", "configuration_space", "variational_domain",
        "input_artifacts", "output_artifacts", "mathematical_status",
        "owning_theorem_version", "downstream_consumers",
        "historical_supersessions", "current_blockers",
    }
    assert all(required <= row.keys() for row in payload["subsystems"])


def test_blocker_and_interface_priority_reconciliation() -> None:
    payload = _payload()
    blockers = payload["blocker_reconciliation"]
    assert sum(row["classification"] == "CURRENT_BLOCKER" for row in blockers) == 1
    old_domain = next(row for row in blockers if row["id"] == "V6_7_NORMAL_MATTER_DOMAIN_NO_GO")
    assert old_domain["classification"] == "SUPERSEDED_BY_LATER_DOMAIN"
    assert payload["current_irreducible_object"] == (
        "G7_CORRELATED_QUARTER_STEP_CENTER_STOP_WITNESS"
    )
    assert payload["current_irreducible_objects"] == [
        "G7_CORRELATED_QUARTER_STEP_CENTER_STOP_WITNESS",
    ]
    assert payload["integration_order"] == [
        "A_EXISTING_COMPOSITION", "C_IMPLEMENTATION", "B_THEOREM", "D_NEW_THEORY_CHOICE"
    ]
    assert all(
        gap["status"] == "NONE_CURRENTLY_IDENTIFIED"
        for gap in payload["interface_gaps"] if gap["class"] == "D"
    )
    assert payload["claim_boundary"]["FULL_BHSM_COMPLETE"] is False
    response_gap = next(
        row for row in payload["interface_gaps"]
        if row["id"] == "RESPONSE_TO_CORRELATED_Y_Z1_Z2"
    )
    assert response_gap["status"] == (
        "EXACT_AFFINE_TAYLOR26_CARRIER_AND_RETAINED_GAUSS8_SIGNED_Y_CERTIFIED;_"
        "FINAL_CENTER_Z2_AND_RECENTERED_CONE_REBUILD_OPEN"
    )
