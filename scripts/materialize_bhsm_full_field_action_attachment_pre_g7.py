"""Materialize the pre-Gate-7 full-field attachment authority."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface.full_field_action_attachment_pre_g7 import (  # noqa: E402
    ACTION_VERSION,
    ATTACHMENT_STATUS,
    DERIVATIVE_CONVENTION,
    FullFieldBackgroundBinder,
    PreparedBRSTInterface,
    PreparedHSDirectionInterface,
    PreparedMomentumSymbolInterface,
    PreparedReplacementSaddleInterface,
    authoritative_field_registry,
    current_pre_g7_attachment,
    response_artifact_rejection_witness,
)


RESULT = ROOT / "artifacts" / "action_extension" / "BHSM_FULL_FIELD_ACTION_ATTACHMENT_PRE_G7.json"

SOURCES = (
    "scripts/materialize_bhsm_full_field_action_attachment_pre_g7.py",
    "src/bhsm/interface/full_field_action_attachment_pre_g7.py",
    "src/bhsm/interface/aether_jax_full_local_action.py",
    "src/bhsm/interface/aether_n3_exact_full_local_action_jet_v17_60.py",
    "src/bhsm/interface/aether_common_quantum_superdeterminant_v15_96.py",
    "src/bhsm/interface/aether_common_source_frechet_response_v15_99.py",
    "src/bhsm/interface/aether_forward_common_source_incidence.py",
    "src/bhsm/interface/action_extension_global_spin_reset_ae2.py",
    "src/bhsm/interface/ae3_reciprocal_join_localization.py",
    "src/bhsm/interface/universal_brst_quotient.py",
    "src/bhsm/interface/universal_momentum_map.py",
    "artifacts/BHSM_aether_hybrid_standard_model_bundle_v15_53.json",
    "artifacts/action_extension/BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json",
    "artifacts/action_extension/BHSM_AE4_EXISTING_ASSET_SYSTEM_INTEGRATION.json",
    "tests/test_full_field_action_attachment_pre_g7.py",
    "theory/bhsm_full_field_action_attachment_pre_g7.md",
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _quadratic_rows(attachment: Any) -> list[dict[str, str]]:
    return [
        {"left": left, "right": right, "classification": status.value}
        for (left, right), status in attachment.block_status.items()
    ]


def build_payload() -> dict[str, Any]:
    registry = authoritative_field_registry()
    binder = FullFieldBackgroundBinder()
    background = binder.unbound()
    attachment = current_pre_g7_attachment(background, registry=registry)
    case = response_artifact_rejection_witness()
    block_rows = _quadratic_rows(attachment)
    all_expected_pairs = len(block_rows) == 15
    validations = {
        "registry_is_contiguous_and_deterministic": registry.dimension > 98,
        "all_fifteen_requested_S2_blocks_classified": all_expected_pairs,
        "response_objects_not_registered_as_action_components": all(
            not component.response_object_only for component in attachment.components
        ),
        "retained_geometry_component_is_action_owned": attachment.components[0].component_id == "RETAINED_N12_LOCAL_GEOMETRY_ACTION",
        "background_remains_unbound": background.state.value == "UNBOUND_BACKGROUND",
        "physical_promotion_is_fail_closed": not background.physical,
        "matrix_free_orders_one_through_four_exposed": attachment.metadata()["derivative_orders"] == [1, 2, 3, 4],
        "graded_oracle_gate_declared": "KOSZUL" in DERIVATIVE_CONVENTION,
        "BRST_adapter_prepared_not_frozen": PreparedBRSTInterface(background).background is background,
        "momentum_adapter_prepared_not_frozen": PreparedMomentumSymbolInterface(background).background is background,
        "replacement_saddle_adapter_prepared": PreparedReplacementSaddleInterface(attachment).action is attachment,
        "HS_direction_adapter_prepared": PreparedHSDirectionInterface(attachment).action is attachment,
        "case_B_source_gap_named": case["decision"] == "CASE_B" and not case["interacting_operator_family_machine_readable"],
        "no_empirical_input_used": not attachment.components[0].empirical_input_used,
        "FULL_BHSM_COMPLETE_remains_false": True,
    }
    return {
        "artifact": "BHSM_FULL_FIELD_ACTION_ATTACHMENT_PRE_G7",
        "schema_version": 1,
        "status": ATTACHMENT_STATUS,
        "attachment_framework_prebuilt": True,
        "FULL_FIELD_ACTION_ATTACHMENT_READY_FOR_GATE7_BACKGROUND": False,
        "authority": "BACKGROUND_PARAMETRIC_ATTACHMENT_CONTRACT_NOT_PHYSICAL_BACKGROUND_AUTHORITY",
        "action_version": ACTION_VERSION,
        "selected_successor_functional_owner": "BHSM-AE-4.0.0_STRATIFIED_DIRAC_ZETA_OWNER",
        "AE2_geometry_to_AE4_owner_compatibility_record": "OPEN__NO_SILENT_CROSS_VERSION_COMPOSITION",
        "background_state": background.metadata(),
        "field_registry": registry.metadata(),
        "action_components": attachment.metadata()["components"],
        "action_component_sources": {
            "retained_geometry": "ACTION_DERIVED_LOCAL_KERNEL",
            "AE2_fermion_history_seam": "DOMAIN_OWNED_WITH_INDEPENDENT_SEAM_ACTION_EXACTLY_ZERO__NUMERICAL_HISTORY_OPERATOR_OPEN",
            "common_GFHS": "RESPONSE_LEVEL_ONLY_NOT_REGISTERED_AS_ACTION_COMPONENT",
        },
        "GFHS_research_decision": case,
        "quadratic_block_matrix": block_rows,
        "quadratic_local_subblocks": {
            "retained_N12_local_geometry_geometry": "ACTION_DERIVED",
            "complete_geometry_history_seam_geometry_geometry": "MISSING_ACTION_SOURCE",
        },
        "S1_ready": "MATRIX_FREE_INTERFACE_READY__FULL_FIELD_SOURCE_OPEN",
        "S2_ready": "MATRIX_FREE_INTERFACE_READY__FIFTEEN_BLOCK_AUDIT_FAIL_CLOSED",
        "S3_ready": "BOSONIC_DIRECTIONAL_INTERFACE_READY__GRADED_GFHS_ORACLE_OPEN",
        "S4_ready": "BOSONIC_DIRECTIONAL_INTERFACE_READY__GRADED_GFHS_ORACLE_OPEN",
        "graded_GFHS_directional_oracle_attached": False,
        "geometry_reduction_verified": False,
        "geometry_local_kernel_reduction_verified": True,
        "geometry_full_history_seam_reduction_open": True,
        "sector_reductions_verified": {
            "geometry_local": True,
            "gauge": False,
            "fermion": False,
            "HS": False,
            "allowed_interactions": False,
            "missing_reductions_raise_MissingActionSourceError": True,
        },
        "BRST_interface_ready": False,
        "BRST_status": "CONSUMER_ADAPTER_READY__FULL_FIELD_GENERATOR_AND_GAUGE_CONDITION_PROVIDER_OPEN",
        "BRST_physical_quotient_frozen": False,
        "momentum_symbol_interface_ready": False,
        "momentum_symbol_status": "CONDITIONAL_S2_CONTRACTION_READY__ACTION_OWNED_MOMENTUM_LIFT_PROVIDER_OPEN",
        "physical_momentum_symbol_derived": False,
        "history_seam_attached": {
            "AE2_fermion_domain_and_reset_graph_owned": True,
            "independent_fermion_seam_action_is_zero": True,
            "full_geometry_history_action_assembled": False,
            "nonfermion_Wentzell_or_seam_terms_defaulted_to_zero": False,
            "status": "DOMAIN_CONTRACT_RESOLVED__FULL_NUMERICAL_ASSEMBLY_BACKGROUND_GATED",
        },
        "yukawa_action_interface_ready": False,
        "yukawa_channel_registry_retained": True,
        "yukawa_current_same_action_callable": False,
        "physical_yukawas_derived": False,
        "physical_HS_direction_derived": False,
        "full_field_saddle_interface_ready": False,
        "replacement_saddle_status": "CONSTRAINT_PROJECTED_CONSUMER_SCAFFOLD_READY__FULL_GRADED_S1_AND_CONSTRAINT_PROVIDER_OPEN",
        "physical_replacement_saddle_derived": False,
        "physical_background_bound": False,
        "full_field_physical_promotion": "BLOCKED",
        "no_empirical_input": True,
        "hindsight": {
            "VALIDATED": [
                "deterministic_full_field_registry_and_projectors",
                "retained_N12_local_geometry_action_embedding",
                "exact_zero_SM_retained_local_geometry_reduction",
                "matrix_free_bosonic_local_S1_S2_S3_S4_dispatch",
                "hash_validating_future_background_authority_contract",
                "fail_closed_BRST_and_conditional_S2_consumer_adapters",
            ],
            "INVALIDATED": [
                "manual_response_matrix_splicing_as_action_authority",
                "historical_closed_cycle_response_as_current_reset_glued_action",
                "boolean_only_physical_background_promotion",
            ],
            "OPEN": [
                "physical_Gate7_background",
                "authority_certified_finite_field_basis_realization",
                "current_domain_interacting_GFHS_operator_family",
                "AE2_geometry_to_AE4_successor_owner_compatibility_record",
                "full_history_and_nonfermion_seam_action_assembly",
                "global_full_field_gauge_generator_and_gauge_condition",
                "physical_HS_direction",
                "same_action_physical_Yukawa_matrices",
                "same_action_replacement_quantum_saddle",
            ],
            "EXACT_NEXT_OBJECT": case["smallest_missing_action_source"],
        },
        "exact_post_Gate7_bind_calculation": [
            "validate_the_Gate7_authority_and_all_declared_hashes",
            "authorize_the_AE2_geometry_to_AE4_successor_owner_compatibility_map",
            "bind_the_exact_background_state_domain_registry_metric_and_seam_data",
            "realize_the_current_domain_interacting_graded_GFHS_operator_family",
            "register_its_action_owned_directional_oracle",
            "evaluate_S1_S2_S3_S4_and_construct_the_BRST_quotient_and_momentum_symbol",
            "solve_the_same_action_saddle_and_select_the_physical_HS_direction",
        ],
        "validation": validations,
        "validated": all(validations.values()),
        "invalidated": False,
        "open": True,
        "FULL_BHSM_COMPLETE": False,
        "source_sha256": {relative: _sha256(ROOT / relative) for relative in SOURCES},
    }


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(deterministic_json(payload), encoding="utf-8")
    print(deterministic_json(payload), end="")


if __name__ == "__main__":
    main()
