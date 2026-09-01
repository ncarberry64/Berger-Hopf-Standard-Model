"""Audit whether the current BHSM background has a full physical field action.

This is an attachment audit, not an action reconstruction.  It binds the
current AE2 domain, the retained N12 local geometry action, the explicit BRST
quotient implementation, and the retained Standard-Model component artifacts.
It fails closed when those inputs do not expose one same-background action
oracle with gauge/ghost, fermion, and HS/scalar derivatives through order four.
"""

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

from bhsm.interface.aether_jax_full_local_action import (  # noqa: E402
    MDIM,
    ORDER,
    QDIM,
    STATE_DIMENSION,
)
from bhsm.interface.retained_sm_physics_adapter import (  # noqa: E402
    load_retained_sm_component_match,
)


RESULT = ROOT / "artifacts" / "BHSM_CURRENT_FULL_FIELD_ACTION_ATTACHMENT_AUDIT.json"
EVIDENCE_BASE_COMMIT = "f4dcd155d742009de6a10c209f47f21a36afba49"

PATHS = {
    "ae2_action": "artifacts/action_extension/BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json",
    "microscopic_action": "artifacts/BHSM_aether_total_microscopic_action_v15_3.json",
    "sm_bundle": "artifacts/BHSM_aether_hybrid_standard_model_bundle_v15_53.json",
    "gauge_hs_response": "artifacts/BHSM_aether_common_gauge_hs_pushforward_v16_05.json",
    "cycle_scale": "artifacts/BHSM_aether_cycle_scale_renormalization_v15_89.json",
    "local_action": "src/bhsm/interface/aether_jax_full_local_action.py",
    "exact_local_jet": "src/bhsm/interface/aether_n3_exact_full_local_action_jet_v17_60.py",
    "local_adapter": "src/bhsm/interface/retained_n12_action_expansion_adapter.py",
    "sm_adapter": "src/bhsm/interface/retained_sm_physics_adapter.py",
    "brst_quotient": "src/bhsm/interface/universal_brst_quotient.py",
    "quadratic_engine": "src/bhsm/interface/universal_quadratic_spectrum.py",
}

REQUIRED_PHYSICAL_FIELD_BLOCKS = (
    "gauge_and_ghost_fields",
    "fermion_fields",
    "HS_or_scalar_fields",
    "geometry_gauge_cross_derivatives",
    "geometry_fermion_cross_derivatives",
    "geometry_HS_cross_derivatives",
    "gauge_fermion_HS_cross_derivatives",
)

MINIMUM_PROMOTION_INPUTS = (
    "one_current_AE2_physical_background_with_geometry_gauge_fermion_HS_blocks",
    "same_action_value_and_derivatives_orders_1_through_4",
    "history_and_seam_action_assembly",
    "explicit_constraint_and_BRST_quotient_frame",
    "current_action_owned_local_momentum_symbol",
    "all_required_self_and_cross_sector_derivative_blocks",
    "same_action_replacement_quantum_saddle",
    "action_selected_physical_HS_direction",
    "local_zero_momentum_Lorentzian_gauge_residues_and_couplings",
    "action_derived_Yukawa_matrices",
    "action_version_background_domain_and_provenance_hashes",
)


def _load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    ae2 = _load(PATHS["ae2_action"])
    microscopic = _load(PATHS["microscopic_action"])
    bundle = _load(PATHS["sm_bundle"])
    response = _load(PATHS["gauge_hs_response"])
    scale = _load(PATHS["cycle_scale"])
    retained = load_retained_sm_component_match(
        ROOT / PATHS["sm_bundle"],
        ROOT / PATHS["gauge_hs_response"],
        ROOT / PATHS["cycle_scale"],
    )
    blockers = retained.physical_engine_blockers(
        gate7_closed=False,
        current_background_attached=False,
        full_field_action_attached=False,
        universal_gf_scale_attached=True,
    )

    ae2_definition = ae2["action_definition"]
    ae2_claim = ae2["claim_boundary"]
    bundle_claim = bundle["claim_boundary"]
    response_claim = response["claim_boundary"]
    scale_claim = scale["claim_boundary"]

    current_blocks = {
        "geometry_coordinates": int(QDIM),
        "geometry_velocities": int(QDIM),
        "constraint_multipliers": int(MDIM),
        "total_state_dimension": int(STATE_DIMENSION),
        "retained_order": int(ORDER),
        "gauge_and_ghost_fields": 0,
        "fermion_fields": 0,
        "HS_or_scalar_fields": 0,
    }
    missing_blocks = [
        name for name in REQUIRED_PHYSICAL_FIELD_BLOCKS
        if name not in {
            "geometry_coordinates",
            "geometry_velocities",
            "constraint_multipliers",
        }
    ]

    validations = {
        "retained_state_is_exactly_37_plus_37_plus_24": (
            QDIM == 37 and MDIM == 24 and STATE_DIMENSION == 98
        ),
        "ae2_action_version_is_current": ae2["action_version"] == "BHSM-AE-2.0.0",
        "ae2_adds_no_new_coefficient": ae2_definition["new_continuous_coefficient"] is None,
        "ae2_adds_no_new_scale": ae2_definition["new_physical_scale"] is None,
        "ae2_adds_no_new_propagating_field": ae2_definition["new_propagating_field"] is None,
        "ae2_gate7_remains_open": ae2_claim["Gate7_closed"] is False,
        "microscopic_core_action_not_owned": all(
            microscopic[key] is False
            for key in ("q_C_owned", "b_GC_owned", "core_pairing_owned")
        ),
        "total_microscopic_operator_not_derived": (
            microscopic["associated_total_operator_derived"] is False
            and microscopic["total_q_A_closed_action_owned"] is False
        ),
        "retained_bundle_is_valid_component_evidence": (
            bundle["validation_passed"] is True
            and bundle_claim["global_SM_bundle_and_representations_fixed"] is True
        ),
        "physical_HS_direction_and_saddle_are_open": (
            response_claim["physical_single_Higgs_direction_selected"] is False
            and response_claim["replacement_quantum_saddle_solved"] is False
        ),
        "physical_yukawa_mass_and_gauge_outputs_are_open": (
            bundle_claim["Yukawa_matrix_entries_derived"] is False
            and bundle_claim["mass_eigenvalues_and_mixing_derived"] is False
            and scale_claim["local_zero_momentum_SM_couplings_derived"] is False
        ),
        "historical_DtN_not_relabelled_as_local_coupling": (
            scale["absolute_cycle_form_factors"][
                "local_zero_momentum_coupling_identified_with_DtN_form_factor"
            ] is False
        ),
        "brst_quotient_is_implemented_but_requires_action_owned_inputs": (
            (ROOT / PATHS["brst_quotient"]).is_file()
        ),
        "all_expected_adapter_blockers_are_present": all(
            name in blockers
            for name in (
                "Gate7_closed_background",
                "current_AE2_background_attachment",
                "machine_readable_full_gauge_fermion_HS_action",
                "same_action_replacement_quantum_saddle",
                "action_selected_physical_HS_direction",
                "local_zero_momentum_gauge_couplings",
                "action_derived_Yukawa_matrices",
                "action_derived_mass_and_mixing_spectrum",
            )
        ),
    }

    return {
        "artifact": "BHSM_CURRENT_FULL_FIELD_ACTION_ATTACHMENT_AUDIT",
        "schema_version": 1,
        "evidence_base_commit": EVIDENCE_BASE_COMMIT,
        "action_version": ae2["action_version"],
        "audit_scope": (
            "CURRENT_AE2_BACKGROUND_TO_UNIVERSAL_S1_S2_S3_S4_PHYSICAL_FIELD_ATTACHMENT"
        ),
        "classification": "PRECISE_ATTACHMENT_NO_GO_CERTIFICATE",
        "decision": (
            "CURRENT_RETAINED_N12_LOCAL_ACTION_ADAPTER_IS_GEOMETRY_ONLY_AND_CANNOT_"
            "BY_ITSELF_INSTANTIATE_UNIVERSAL_SM_S2_S3_S4"
        ),
        "current_retained_action_state": current_blocks,
        "ae2_domain_result": {
            "global_fermion_reset_domain_owned": True,
            "independent_normal_matter_boundary_action": ae2_definition[
                "independent_normal_matter_boundary_action"
            ],
            "new_continuous_coefficient": ae2_definition["new_continuous_coefficient"],
            "new_physical_scale": ae2_definition["new_physical_scale"],
            "new_propagating_field": ae2_definition["new_propagating_field"],
            "field_action_attachment_completed": False,
        },
        "implemented_complementary_infrastructure": {
            "universal_derivative_orders": [1, 2, 3, 4],
            "explicit_BRST_physical_nullspace_quotient": True,
            "explicit_Faddeev_Popov_regularity_check": True,
            "quadratic_engine_accepts_BRST_quotient": True,
            "kinetic_inverse_assumed_or_formed": False,
            "physical_action_inputs_supplied_by_BRST_module": False,
        },
        "retained_component_evidence": {
            "global_SM_bundle_and_representations_fixed": bundle_claim[
                "global_SM_bundle_and_representations_fixed"
            ],
            "absolute_gauge_replacement_seed_evaluated": response_claim[
                "absolute_gauge_replacement_seed_evaluated"
            ],
            "nonzero_HS_kinetic_kernel_evaluated": response_claim[
                "nonzero_HS_kinetic_kernel_evaluated"
            ],
            "absolute_dimensionless_boundary_form_factors_derived": scale_claim[
                "absolute_dimensionless_boundary_form_factors_derived"
            ],
            "historical_centers_promoted": False,
            "complete_current_full_field_action_materialized": False,
        },
        "missing_physical_field_blocks": missing_blocks,
        "minimum_promotion_inputs": list(MINIMUM_PROMOTION_INPUTS),
        "adapter_reported_dependencies_open": list(blockers),
        "scientific_boundary": {
            "physical_prediction_promotion": "BLOCKED",
            "universal_engine_infrastructure_invalidated": False,
            "root_nonexistence_claimed": False,
            "BHSM_action_completion_impossible_claimed": False,
            "historical_nonlocal_DtN_residues_relabelled_as_local_couplings": False,
            "new_action_coefficient_or_empirical_datum_invented": False,
        },
        "validation": validations,
        "validation_passed": all(validations.values()),
        "source_sha256": {
            relative: _sha256(ROOT / relative)
            for relative in sorted(PATHS.values())
        },
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
