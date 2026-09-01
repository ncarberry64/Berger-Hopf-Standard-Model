"""Materialize the AE2 photon/neutrino provenance and Gate-7 audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.action_extension_ae2_neutrino_photon_propagation import (  # noqa: E402
    ACTION_VERSION,
    PROVENANCE_CLASSES,
    dimensionless_splitting_ratio,
    electroweak_null_channel,
    final_adjudication,
    neutral_seed_spectrum,
    oscillation_phase_scaling_gate,
    propagation_family_adjudication,
)


TARGET = ROOT / "artifacts/flagship_integration"
OUTPUTS = {
    "provenance": "BHSM_AE2_PHOTON_NEUTRINO_PROPAGATION_PROVENANCE.json",
    "operator": "BHSM_AE2_NEUTRAL_PROPAGATION_OPERATOR.json",
    "stiffness": "BHSM_AE2_NEUTRINO_PROPAGATION_STIFFNESS.json",
    "phase": "BHSM_AE2_NEUTRINO_OSCILLATION_PHASE_GATE.json",
    "ratio": "BHSM_AE2_NEUTRINO_DIMENSIONLESS_SPLITTING_RATIO.json",
    "photon": "BHSM_AE2_PHOTON_NULL_CHANNEL_AUDIT.json",
    "pmns": "BHSM_AE2_PMNS_ACTION_REDERIVATION_AUDIT.json",
    "cp": "BHSM_AE2_NEUTRINO_CP_HOLONOMY_AUDIT.json",
    "reconvergence": "BHSM_AE2_NEUTRINO_GATE7_RECONVERGENCE.json",
}

INPUTS = (
    "artifacts/action_extension/BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json",
    "artifacts/BHSM_electromagnetic_surviving_generator_v6_3_0.json",
    "artifacts/BHSM_gauge_boson_mass_matrix_v6_4_0.json",
    "artifacts/BHSM_gauge_mass_matrix_global_audit_v6_5_0.json",
    "artifacts/BHSM_generation_projector_action_attachment_v8_2.json",
    "artifacts/BHSM_classical_mode_stress_incidence_v8_3.json",
    "artifacts/neutral_operator_no_fit_output_v1.json",
    "artifacts/BHSM_neutrino_curvature_threshold_v0_9.json",
    "artifacts/BHSM_neutral_spectral_report_v1_3.json",
    "artifacts/neutrino_bedrock_dynamic_layer_v1.json",
    "artifacts/BHSM_neutral_high_energy_propagation_operator_v6_6_0.json",
    "artifacts/BHSM_neutral_L_over_E_phase_law_v6_6_0.json",
    "artifacts/BHSM_neutral_compact_operator_reduction_v6_7_0.json",
    "artifacts/BHSM_neutral_phase_law_v6_7_0.json",
    "artifacts/PMNS_no_fit_operator_output_v1.json",
    "artifacts/BHSM_PMNS_geometric_transport_attachment_v6_6_0.json",
    "artifacts/BHSM_PMNS_neutral_eigenbasis_attachment_v6_7_0.json",
    "artifacts/CP_no_fit_holonomy_output_v1.json",
    "artifacts/BHSM_cp_holonomy_attachment_resolution_attempt_v1_0.json",
    "artifacts/BHSM_cp_holonomy_o_int_attachment_theorem_v1_1.json",
    "artifacts/BHSM_aether_rank16_u1_hs_vertex_matrices_v16_01.json",
    "artifacts/flagship_integration/BHSM_N12_FORWARD_FIXED_CHANNEL_TRANSFER.json",
    "artifacts/flagship_integration/BHSM_N12_FORWARD_COMMON_SOURCE_INCIDENCE.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_COMPACT_SOURCE_DINI_CLOSURE.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_ANGULAR_DINI_UNIFORMITY_AUDIT.json",
    "artifacts/current_semantics/BHSM_CURRENT_COMPLETION_DAG.json",
    "src/bhsm/interface/action_extension_ae2_neutrino_photon_propagation.py",
    "scripts/audit_bhsm_ae2_photon_neutrino_propagation.py",
)


def _load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def _sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest().upper()


def _inputs() -> dict[str, str]:
    return {relative: _sha256(relative) for relative in INPUTS}


def _base(artifact: str, status: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "action_version": ACTION_VERSION,
        "status": status,
        "audit_type": "READ_ONLY_ACTION_PROVENANCE_AND_OPERATOR_TYPE_CHECK",
        "new_action_term_added": False,
        "new_physical_scale_added": False,
        "empirical_derivation_inputs_used": False,
        "frozen_predictions_changed": False,
        "FULL_BHSM_COMPLETE": False,
    }


def build_payloads() -> dict[str, dict[str, Any]]:
    missing = [relative for relative in INPUTS if not (ROOT / relative).is_file()]
    if missing:
        raise FileNotFoundError(f"propagation audit inputs missing: {missing}")

    ae2 = _load(INPUTS[0])
    em = _load(INPUTS[1])
    gauge_local = _load(INPUTS[2])
    gauge_global = _load(INPUTS[3])
    family = _load(INPUTS[4])
    stress = _load(INPUTS[5])
    neutral_seed = _load(INPUTS[6])
    threshold = _load(INPUTS[7])
    spectral = _load(INPUTS[8])
    bedrock = _load(INPUTS[9])
    high_energy = _load(INPUTS[10])
    l_over_e = _load(INPUTS[11])
    compact_neutral = _load(INPUTS[12])
    phase_old = _load(INPUTS[13])
    pmns_old = _load(INPUTS[14])
    pmns_transport = _load(INPUTS[15])
    pmns_neutral = _load(INPUTS[16])
    cp_seed = _load(INPUTS[17])
    cp_attach = _load(INPUTS[18])
    cp_operator = _load(INPUTS[19])
    rank16 = _load(INPUTS[20])
    fixed = _load(INPUTS[21])
    incidence = _load(INPUTS[22])
    compact_dini = _load(INPUTS[23])
    angular = _load(INPUTS[24])
    completion_dag = _load(INPUTS[25])

    gate7_angular_nodes = [
        record for record in completion_dag["records"]
        if record.get("canonical_id") == "G7_07_ANGULAR_TAIL"
    ]
    if len(gate7_angular_nodes) != 1:
        raise RuntimeError("current DAG must contain exactly one G7_07 node")
    gate7_angular_node = gate7_angular_nodes[0]
    current_owner_nodes = [
        record for record in completion_dag["records"]
        if record.get("current_status") == "OPEN_CURRENT_OWNER"
    ]
    if len(current_owner_nodes) != 1:
        raise RuntimeError("current DAG must contain exactly one open current owner")
    current_owner_node = current_owner_nodes[0]

    source_hashes = _inputs()
    raw_seed = neutral_seed_spectrum(neutral_seed["K_nu"])
    photon_null = electroweak_null_channel(1.0, 0.6, 4.0)
    phase_gate = oscillation_phase_scaling_gate(
        None,
        translation_energy_generator_owned=False,
        physical_momentum_map_owned=False,
    )
    ratio = dimensionless_splitting_ratio(None)
    common_family = propagation_family_adjudication()
    adjudication = final_adjudication()

    provenance_rows = [
        {
            "object": "transverse physical EM/U1em carrier",
            "classification": "CONDITIONAL",
            "qualified_classifications": ["GEOMETRY_DERIVED", "CONDITIONAL"],
            "source": INPUTS[1],
            "finding": (
                "Q_em=T_n+Y_BH and its representation null direction are "
                "derived, but the current action has not traced that direction "
                "through the complete transverse quotient/domain as a physical photon."
            ),
        },
        {
            "object": "current AE2 matter Dirac carrier",
            "classification": "ACTION_DERIVED",
            "qualified_classifications": ["ACTION_DERIVED"],
            "source": INPUTS[0],
            "finding": (
                "The canonically normalized Dirac action and reset-glued "
                "self-adjoint domain are owned by BHSM-AE-2.0.0."
            ),
        },
        {
            "object": "neutral neutrino carrier",
            "classification": "NOT_DERIVED",
            "qualified_classifications": ["GEOMETRY_DERIVED", "CONDITIONAL", "NOT_DERIVED"],
            "source": "src/charged_kf_generator.py plus current AE2/family artifacts",
            "finding": (
                "A finite neutral representation label P_nu exists, but a "
                "physical invariant neutral propagation subbundle/operator is not derived."
            ),
        },
        {
            "object": "three-family/three-slot neutral carrier",
            "classification": "NOT_DERIVED",
            "qualified_classifications": ["OWNER_ONTOLOGY", "CONDITIONAL", "NOT_DERIVED"],
            "source": INPUTS[4],
            "finding": (
                "Three slots are frozen ontology/conditional geometry, while "
                "the attached action modules are F_l direct_sum F_u direct_sum F_d "
                "and contain no F_nu."
            ),
        },
        {
            "object": "historical neutral K_nu boundary seed",
            "classification": "BOUNDARY_SEED",
            "qualified_classifications": ["BOUNDARY_SEED", "HISTORICAL"],
            "source": INPUTS[6],
            "finding": "The raw seed is indefinite and is not a physical mass or stiffness matrix.",
        },
        {
            "object": "current factorized Gate7 product-Dirac",
            "classification": "ACTION_DERIVED",
            "qualified_classifications": ["ACTION_DERIVED"],
            "source": INPUTS[21],
            "finding": (
                "Each retained fermion channel is A_lambda^*A_lambda on the "
                "AE2 domain with native resolvent variable z, not p^2."
            ),
        },
        {
            "object": "current PMNS artifact",
            "classification": "FROZEN_OUTPUT",
            "qualified_classifications": ["FROZEN_OUTPUT", "CONDITIONAL", "HISTORICAL"],
            "source": INPUTS[14],
            "finding": (
                "The stored matrix uses a canonical charged-diagonal convention "
                "and fixed angles; it is not U_l^dagger U_nu from action operators."
            ),
        },
        {
            "object": "current Z6/pi3 CP holonomy",
            "classification": "BOUNDARY_SEED",
            "qualified_classifications": ["BOUNDARY_SEED", "FROZEN_OUTPUT", "CONDITIONAL"],
            "source": INPUTS[17],
            "finding": (
                "exp(i*pi/3) is a flavor/relative-holonomy seed; its standalone "
                "interaction operator and neutrino propagation attachment are absent."
            ),
        },
    ]
    provenance_validation = {
        "classification_vocabulary_exact": all(
            item in PROVENANCE_CLASSES
            for row in provenance_rows
            for item in row["qualified_classifications"]
        ),
        "AE2_action_version_current": ae2["action_version"] == ACTION_VERSION,
        "AE2_has_no_new_field_or_scale": (
            ae2["action_definition"]["new_physical_scale"] is None
            and ae2["action_definition"]["new_propagating_field"] is None
        ),
        "family_modules_exclude_neutral_module": (
            family["frozen_family_modules"]["direct_sum"]
            == "F_l direct_sum F_u direct_sum F_d"
        ),
        "family_selection_imported_not_rederived": family["frozen_family_modules"]["generation_selection_rederived_in_v8_2"] is False,
        "raw_K_nu_indefinite": raw_seed["positive_semidefinite"] is False,
        "PMNS_uses_charged_diagonal_convention": "CHARGED_DIAGONAL" in pmns_old["PMNS_boundary_no_fit_output"],
        "CP_standalone_operator_open": cp_operator["theorem_status"] == "OPEN_EXACT_MISSING_THEOREM",
    }
    provenance = {
        **_base(
            "BHSM_AE2_PHOTON_NEUTRINO_PROPAGATION_PROVENANCE",
            "PROVENANCE_SPLIT_COMPLETED_NO_HISTORICAL_PROMOTION",
        ),
        "classification_vocabulary": list(PROVENANCE_CLASSES),
        "objects": provenance_rows,
        "guardrails": {
            "raw_K_nu_is_physical_mass_matrix": False,
            "positive_Wentzell_margin_is_photon_mass": False,
            "Gate7_z_is_p_squared": False,
            "neutrino_electromagnetic_charge_added": False,
            "oscillation_causes_mass": False,
            "massless_neutrino_forced": False,
        },
        "inputs": source_hashes,
        "validation": provenance_validation,
        "validation_passed": all(provenance_validation.values()),
    }

    operator_validation = {
        "full_AE2_Dirac_domain_self_adjoint": ae2["validation"]["graph_maximal_isotropic"] is True,
        "full_AE2_squared_domain_owned": "Dom(D_AE2^2)" in ae2["action_definition"]["squared_operator_domain"],
        "neutral_finite_label_exists": em["charge_table"][0]["Q_em"] == "0",
        "three_slot_neutral_action_module_absent": "neutral" not in family["frozen_family_modules"]["modules"],
        "action_intertwiner_absent": stress["remaining_exact_obstruction"].startswith("ACTION_DERIVED_SPECTRAL_INTERTWINER"),
        "historical_K_prop_not_action_derived": high_energy["K_prop_action_source"] == "not derived",
        "minimal_light_operator_is_zero": compact_neutral["K_prop_light"] == [[0.0] * 3 for _ in range(3)],
    }
    operator = {
        **_base(
            "BHSM_AE2_NEUTRAL_PROPAGATION_OPERATOR",
            "OPEN_MISSING_ACTION_OWNED_NEUTRAL_THREE_SLOT_PROJECTION",
        ),
        "full_carrier": {
            "operator": "D_AE2 and D_AE2^2",
            "status": "ACTION_DERIVED",
            "domain": ae2["action_definition"]["squared_operator_domain"],
        },
        "neutral_representation_label": {
            "formula": "P_nu=(1-C)(1+sigma)/2",
            "status": "GEOMETRY_DERIVED_CONDITIONAL_LABEL_ONLY",
        },
        "target": "P_nu^(3) D_AE2^2 P_nu^(3)",
        "target_status": "OPEN",
        "missing": [
            "an action-derived rank-three neutral invariant subbundle",
            "a projector P_nu^(3) commuting with D_AE2, U_R, gauge and BRST actions",
            "the complete projected self-adjoint domain",
            "a nontrivial action-owned family response/stiffness block",
        ],
        "not_equal_to": [
            "historical raw K_nu boundary seed",
            "representative K_prop matrix from v6.6",
            "Gate7 spectral parameter z",
        ],
        "inputs": source_hashes,
        "validation": operator_validation,
        "validation_passed": all(operator_validation.values()),
    }

    stiffness_validation = {
        "raw_seed_has_negative_eigenvalue": min(raw_seed["eigenvalues"]) < 0.0,
        "raw_seed_not_promoted": raw_seed["raw_seed_may_be_used_as_physical_mass_matrix"] is False,
        "conditional_A_nu_missing": spectral["stiffness_ratio"]["curvature_penalty"]["numeric_available"] is False,
        "conditional_Z_nu_missing": spectral["stiffness_ratio"]["kinetic_stiffness"]["numeric_available"] is False,
        "dimensionful_mass_absent": spectral["dimensionful_mass_available"] is False,
        "v66_K_prop_not_action_owned": high_energy["K_prop_action_source"] == "not derived",
        "v67_light_response_degenerate_zero": compact_neutral["nontrivial_L_over_E_generated"] is False,
    }
    stiffness = {
        **_base(
            "BHSM_AE2_NEUTRINO_PROPAGATION_STIFFNESS",
            "OPEN_NO_POSITIVE_ACTION_OWNED_THREE_SLOT_STIFFNESS_MATRIX",
        ),
        "historical_boundary_seed": {
            "symbol": "K_nu",
            "classification": "BOUNDARY_SEED",
            **raw_seed,
        },
        "conditional_topographic_formula": {
            "formula": "mu_nu=sqrt(A_nu/Z_nu)*K_neutral,eff",
            "status": "CONDITIONAL_NOT_ACTION_CLOSED",
            "A_nu": "OPEN",
            "Z_nu": "OPEN",
            "K_neutral_eff": "OPEN_PHYSICAL_MAP",
            "promoted": False,
        },
        "current_minimal_light_block": compact_neutral["K_prop_light"],
        "current_minimal_light_block_effect": "THREEFOLD_ZERO_DEGENERACY_NO_SPLITTING",
        "positive_propagation_stiffness_matrix": None,
        "adjudication": "OPEN",
        "inputs": source_hashes,
        "validation": stiffness_validation,
        "validation_passed": all(stiffness_validation.values()),
    }

    phase_validation = {
        "historical_v66_law_conditional": "CONDITIONALLY" in l_over_e["status"],
        "historical_K_prop_action_source_missing": high_energy["K_prop_action_source"] == "not derived",
        "minimal_current_phase_is_zero": phase_old["law"] == "Delta phi_ij=0 for the three degenerate retained zero modes",
        "physical_energy_generator_not_fabricated": phase_gate["translation_energy_generator_owned"] is False,
        "physical_momentum_map_not_fabricated": phase_gate["physical_momentum_map_owned"] is False,
        "physical_one_over_E_not_claimed": phase_gate["physical_one_over_E_phase_derived"] is False,
        "Gate7_native_variable_is_z_not_p2": incidence["incidence"]["native_spectral_parameter"].startswith("z_"),
    }
    phase = {
        **_base(
            "BHSM_AE2_NEUTRINO_OSCILLATION_PHASE_GATE",
            "OPEN_MISSING_ACTION_STIFFNESS_AND_TRANSLATION_ENERGY_MAP",
        ),
        "gate": phase_gate,
        "historical_conditional_template": {
            "operator": l_over_e["operator"],
            "law": l_over_e["law"],
            "classification": "CONDITIONAL",
            "why_not_promoted": high_energy["K_prop_action_source"],
        },
        "current_minimal_neutral_result": {
            "law": phase_old["law"],
            "nontrivial_L_over_E_generated": compact_neutral["nontrivial_L_over_E_generated"],
        },
        "same_stiffness_must_control": [
            "mass response",
            "relative propagation phase",
            "oscillation",
            "subluminal group velocity",
        ],
        "inputs": source_hashes,
        "validation": phase_validation,
        "validation_passed": all(phase_validation.values()),
    }

    ratio_validation = {
        "ratio_not_fabricated": ratio["ratio"] is None,
        "ratio_status_open": ratio["status"] == "OPEN",
        "no_experimental_splittings_used": True,
        "current_minimal_denominator_zero": compact_neutral["light_transverse_eigenvalues"] == [0.0, 0.0, 0.0],
    }
    ratio_payload = {
        **_base(
            "BHSM_AE2_NEUTRINO_DIMENSIONLESS_SPLITTING_RATIO",
            "OPEN_ACTION_OWNED_NONDEGENERATE_EIGENVALUES_ABSENT",
        ),
        **ratio,
        "input_eigenvalues": None,
        "historical_or_experimental_value_imported": False,
        "current_minimal_zero_block_ratio": "UNDEFINED_0_OVER_0",
        "inputs": source_hashes,
        "validation": ratio_validation,
        "validation_passed": all(ratio_validation.values()),
    }

    photon_validation = {
        "surviving_generator_derived": em["status"] == "BHSM_ELECTROMAGNETIC_SURVIVING_GENERATOR_DERIVED",
        "vacuum_Q_em_neutral": em["vacuum_charge"] == "0",
        "algebraic_null_residual_zero": photon_null["Q_em_null_residual"] < 1.0e-12,
        "algebraic_null_unique_in_conditional_block": photon_null["nullity"] == 1,
        "gauge_mass_block_conditional": "CONDITIONALLY" in gauge_local["status"],
        "global_profile_normalization_open": gauge_global["global_profile_normalization_derived"] is False,
        "physical_transverse_channel_not_overclaimed": photon_null["physical_photon_null_channel_derived"] is False,
    }
    photon = {
        **_base(
            "BHSM_AE2_PHOTON_NULL_CHANNEL_AUDIT",
            "OPEN_MISSING_ACTION_DERIVED_PHOTON_NULL_CHANNEL",
        ),
        "representation_result": photon_null,
        "surviving_generator": em["generator"],
        "conditional_mass_block_status": gauge_local["status"],
        "physical_channel_requirements_open": [
            "trace Q_em through the retained constraint-reduced transverse/coexact quotient",
            "prove invariance of that domain under the current action and reset",
            "show the physical quadratic operator has Mu_gamma^2=0",
            "retain the massless pole under the owned normalization",
        ],
        "Wentzell_guardrail": (
            "THE_POSITIVE_TRANSVERSE_GAUGE_WENTZELL_MARGIN_IS_AN_INTERFACE_"
            "DOMAIN_IMPEDANCE_AND_IS_NOT_A_PHOTON_MASS"
        ),
        "Mu_gamma_squared": None,
        "PHYSICAL PHOTON NULL CHANNEL": "OPEN",
        "inputs": source_hashes,
        "validation": photon_validation,
        "validation_passed": all(photon_validation.values()),
    }

    pmns_validation = {
        "historical_matrix_frozen": pmns_old["official_predictions_changed"] is False,
        "historical_charged_diagonal_convention": "CHARGED_DIAGONAL" in pmns_old["PMNS_boundary_no_fit_output"],
        "v66_neutral_eigenvectors_not_derived": pmns_transport["neutral_eigenvectors_derived"] is False,
        "v67_neutral_basis_not_unique": pmns_neutral["eigenbasis_unique"] is False,
        "charged_action_response_absent": stress["response_matrices"]["charged_lepton"]["matrix"] is None,
        "action_U_l_absent": True,
        "action_U_nu_absent": True,
        "old_matrix_not_promoted": True,
    }
    pmns = {
        **_base(
            "BHSM_AE2_PMNS_ACTION_REDERIVATION_AUDIT",
            "OPEN_MISSING_ACTION_DERIVED_CHARGED_AND_NEUTRAL_EIGENBASES",
        ),
        "required_formula": "U_PMNS=U_l^dagger*U_nu",
        "action_U_l": None,
        "action_U_nu": None,
        "action_PMNS": None,
        "historical_output": {
            "classification": ["FROZEN_OUTPUT", "CONDITIONAL", "HISTORICAL"],
            "convention": pmns_old["convention"],
            "matrix": pmns_old["matrix"],
            "Jarlskog": pmns_old["J_PMNS_BH"],
            "promoted": False,
        },
        "charged_diagonal_convention_role": "COMPARISON_ONLY",
        "PMNS BASIS-MISMATCH DERIVATION": "OPEN",
        "inputs": source_hashes,
        "validation": pmns_validation,
        "validation_passed": all(pmns_validation.values()),
    }

    cp_validation = {
        "pi_over_three_seed_present": cp_seed["delta_BH_formula"] == "pi/3",
        "standalone_operator_open": cp_operator["theorem_status"] == "OPEN_EXACT_MISSING_THEOREM",
        "attachment_only_partial": cp_attach["attachment_resolution_status"].startswith("PARTIALLY_RESOLVED"),
        "PMNS_action_basis_absent": pmns["action_PMNS"] is None,
        "neutrino_splittings_absent": ratio_payload["ratio"] is None,
        "AE2_independent_Cayley_phase_absent": ae2["action_definition"]["independent_Cayley_phase"] is None,
        "Gate7_denominator_not_regulated_by_pi3": compact_dini["CP_Z6_parallel_route"]["acts_on_exact_threshold_transfer_denominator"] is False,
    }
    cp = {
        **_base(
            "BHSM_AE2_NEUTRINO_CP_HOLONOMY_AUDIT",
            "PI_OVER_THREE_IS_FLAVOR_SEED_ONLY_NOT_PROPAGATION_ATTACHMENT",
        ),
        "phase": "exp(i*pi/3)",
        "classification": ["BOUNDARY_SEED", "FROZEN_OUTPUT", "CONDITIONAL"],
        "acts_on_action_owned_neutral_stiffness_operator": False,
        "acts_on_action_derived_PMNS_basis": False,
        "acts_on_Gate7_threshold_transfer_denominator": False,
        "CP_conjugation": "phase_maps_to_exp(-i*pi/3)_ONLY_AFTER_AN_OPERATOR_ATTACHMENT_EXISTS",
        "Jarlskog_action_derived": False,
        "phase_without_splittings_is_physical_oscillation_CP": False,
        "PI/3 CP HOLONOMY ATTACHMENT": "FLAVOR-SEED-ONLY",
        "inputs": source_hashes,
        "validation": cp_validation,
        "validation_passed": all(cp_validation.values()),
    }

    reconvergence_validation = {
        "same_AE2_full_Dirac_domain": ae2["action_version"] == ACTION_VERSION,
        "Gate7_product_factor_retained": fixed["fixed_channel_theorem"]["rank16_product_Dirac_channel"]["factor"].startswith("A_lambda="),
        "Gate7_rank16_has_three_neutrino_multiplicity": rank16["rank16_trace_ledger"]["family_matrix"] == "I3",
        "Gate7_uses_z_not_p2": incidence["incidence"]["momentum_or_p2_label_used"] is False,
        "neutral_action_projection_not_fabricated": operator["target_status"] == "OPEN",
        "no_neutrino_stiffness_transferred_to_Gate7": stiffness["positive_propagation_stiffness_matrix"] is None,
        "fixed_channel_Dini_remains_closed": angular["adjudication"]["fixed_channel_source_Dini"] == "CLOSED_DO_NOT_REOPEN",
        "Gate7_angular_owner_unchanged": angular["frontier_sharpening"]["G7_07_angular_tail"] == "OPEN_CURRENT_OWNER",
        "current_completion_DAG_consumed": (
            completion_dag["action_version"] == ACTION_VERSION
            and completion_dag["validation_passed"] is True
            and gate7_angular_node["current_status"].startswith("CLOSED_BY_OWNER")
            and current_owner_node["canonical_id"] == "G7_08_FORCE"
        ),
        "neutral_reconnaissance_does_not_replace_current_DAG_owner": all(
            "NEUTRINO" not in record.get("canonical_id", "")
            and "PHOTON" not in record.get("canonical_id", "")
            for record in completion_dag["records"]
        ),
        "frozen_predictions_unchanged": True,
        "full_BHSM_false": adjudication["FULL_BHSM_COMPLETE"] is False,
    }
    reconvergence = {
        **_base(
            "BHSM_AE2_NEUTRINO_GATE7_RECONVERGENCE",
            "PARTIAL_SHARED_GEOMETRY_NO_NEUTRINO_OPERATOR_PROMOTION",
        ),
        "common_family": common_family,
        "exact_relation": (
            "THE_NEUTRAL_KINETIC_REPRESENTATION_IS_A_SUBCARRIER_OF_THE_SAME_"
            "AE2_SPIN_TIMES_G_SM_DIRAC_BUNDLE_USED_BY_GATE7,_BUT_NO_ACTION_"
            "DERIVED_THREE_SLOT_NEUTRAL_PROJECTOR_OR_PROPAGATION_STIFFNESS_"
            "HAS_BEEN_SHOWN_TO_COMMUTE_WITH_THAT_OPERATOR"
        ),
        "transferable_results": [
            "AE2 reset-glued self-adjoint full Dirac domain",
            "fixed-channel product-Dirac factorization",
            "compact-source fixed-channel Dini theorem",
        ],
        "nontransferable_results": [
            "historical K_nu",
            "representative v6.6 K_prop",
            "historical PMNS matrix",
            "pi/3 flavor seed",
            "any p, E, group velocity, mass, or oscillation interpretation",
        ],
        "Gate7_status": "ACTIVE_NOT_CLOSED",
        "Gate7_current_owner": current_owner_node["canonical_id"],
        "Gate7_current_owner_detail": current_owner_node["physical_meaning"],
        "superseded_current_owner": "G7_07_ANGULAR_TAIL",
        "completion_DAG_dependency_changed_by_this_sprint": False,
        "Gate7_changed_by_this_sprint": False,
        "final_adjudication": adjudication,
        "inputs": source_hashes,
        "validation": reconvergence_validation,
        "validation_passed": all(reconvergence_validation.values()),
    }

    payloads = {
        "provenance": provenance,
        "operator": operator,
        "stiffness": stiffness,
        "phase": phase,
        "ratio": ratio_payload,
        "photon": photon,
        "pmns": pmns,
        "cp": cp,
        "reconvergence": reconvergence,
    }
    if set(payloads) != set(OUTPUTS):
        raise RuntimeError("propagation artifact registry mismatch")
    return payloads


def deterministic_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def materialize() -> list[Path]:
    payloads = build_payloads()
    failed = [name for name, payload in payloads.items() if not payload["validation_passed"]]
    if failed:
        details = {
            name: [key for key, value in payloads[name]["validation"].items() if not value]
            for name in failed
        }
        raise RuntimeError(f"propagation audit validation failed: {details}")
    TARGET.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, filename in OUTPUTS.items():
        path = TARGET / filename
        path.write_bytes(deterministic_bytes(payloads[name]))
        paths.append(path)
    return paths


if __name__ == "__main__":
    for output in materialize():
        print(output)
