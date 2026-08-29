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
        "DECIMAL_GAUSS6_TO8_SIGNED_SOURCE_AND_PROP16_GREEN_IMAGE_NUMERICALLY_"
        "CONVERGED_INSIDE_THE_HALO;_OUTWARD_INTERVAL_Y_Z1_AND_GAUSS8_CENTER_"
        "DEPENDENT_Z2_CONE_REBUILD_OPEN"
    )
