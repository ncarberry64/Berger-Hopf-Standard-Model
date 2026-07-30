"""Attach the frozen BHSM three-slot family modules to the master action.

The generation-selection theorem is an imported result, not a v8.2 target.
This module records its authoritative sources, attaches the resulting finite
modules to the localized M4 fermion bundle and Dirac domain, and isolates the
remaining classical mode-stress incidence required for physical response.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


VERSION = "v8.2"
SPRINT = "bhsm-generation-projector-action-attachment-v8-2"
SOURCE_MAIN_SHA = "991ad1dbc87fa09dda08e88ee2fb59ddb560f237"
ARTIFACT_NAME = "BHSM_generation_projector_action_attachment_v8_2"
FINAL_VERDICT = (
    "BHSM_MODE_DEPENDENT_RESPONSE_BLOCKED_BY_UNDEFINED_MODE_STRESS"
)
RELEASE_VERDICT = "BHSM_1_0_RELEASE_BLOCKED"
NEXT_MISSING_OBJECT = (
    "ACTION_DERIVED_CLASSICAL_MODE_STRESS_INCIDENCE_ON_"
    "FROZEN_THREE_SLOT_MODULE"
)
FAMILY_CLASSIFICATION = (
    "FROZEN_DERIVED_CONDITIONAL_GEOMETRIC_STRUCTURE"
)
ATTACHMENT_STATUS = (
    "FROZEN_THREE_SLOT_PROJECTORS_ATTACHED_TO_EFFECTIVE_M4_"
    "FERMION_BUNDLE"
)
DOCTRINE_STATEMENT = (
    "BHSM is formulated as a deterministic geometric boundary theory in "
    "which particle and quantum-field descriptions are intended to emerge "
    "from classical nonlinear modes, topology, and interface response. "
    "Standard QFT is used as an effective observable correspondence, not "
    "assumed to be the fundamental microscopic ontology. Accordingly, the "
    "present campaign first tests the original finite BHSM boundary-mode "
    "generation architecture before introducing additional quantum-field "
    "primitives."
)

SECTOR_MODES: dict[str, tuple[tuple[int, int], ...]] = {
    "charged_lepton": ((0, 0), (5, 2), (9, 3)),
    "up": ((0, 0), (6, 0), (10, 1)),
    "down": ((0, 0), (6, 3), (8, 2)),
}

SOURCE_PATHS = (
    "theory/theorem_discharge_phase_orientation_cyclic_results.json",
    "theory/derived_generation_raw_mode_ledgers.md",
    "theory/derived_yukawa_generation_mode_ledgers.md",
    "artifacts/BHSM_triality_generation_scale_report_v6_2_0.json",
    "data/bhsm_weak_double_projection_zvirt_bridge.json",
    "docs/bhsm_sector_projector_ledger_theorem.md",
)


def deterministic_json(value: Any) -> str:
    return json.dumps(
        value, indent=2, sort_keys=True, ensure_ascii=False
    ) + "\n"


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _read_json(path: str) -> dict[str, Any]:
    return json.loads((repository_root() / path).read_text(encoding="utf-8"))


def _read_text(path: str) -> str:
    return (repository_root() / path).read_text(encoding="utf-8")


def _source_sha256(path: str) -> str:
    return sha256((repository_root() / path).read_bytes()).hexdigest()


def source_imports() -> dict[str, Any]:
    closure = _read_json(SOURCE_PATHS[0])
    raw_ledger = _read_text(SOURCE_PATHS[1])
    yukawa_ledger = _read_text(SOURCE_PATHS[2])
    triality = _read_json(SOURCE_PATHS[3])
    weak = _read_json(SOURCE_PATHS[4])
    source_sector = {
        "charged_lepton": "reference_charged",
        "up": "cyclic_upper",
        "down": "cyclic_lower",
    }
    validation = {
        "primitive_spectrum_is_123": (
            closure["primitive_low_energy_closure_spectrum"] == [1, 2, 3]
        ),
        "closure_layer_discharged_conditionally": closure[
            "closure_selection_layer_discharged_conditionally"
        ],
        "triality_is_same_three_slots": (
            triality["triality_and_Berger_triplications_multiplied"] is False
        ),
        "triality_architecture_derived_conditionally": triality[
            "primary_result"
        ]
        == (
            "BHSM_TRIALITY_GENERATION_AND_VOLUME_SCALE_"
            "ARCHITECTURE_DERIVED_CONDITIONALLY"
        ),
        "middle_up_mode_is_6_0": weak["middle_up_mode"] == [6, 0],
        "middle_up_factor_is_one_half": weak["factor"] == "1/2",
        "middle_up_bridge_is_conditional": weak[
            "Z_virt_u2_applicability"
        ]
        == "DERIVED_CONDITIONAL",
        "no_observed_data_used": weak["uses_observed_data"] is False,
        "raw_ledgers_match_frozen_modules": all(
            f"| {source_sector[sector]} | {index} |" in raw_ledger
            and f"`({k},{j})`" in raw_ledger
            for sector, modes in SECTOR_MODES.items()
            for index, (k, j) in enumerate(modes)
        ),
        "yukawa_ledgers_match_frozen_modules": all(
            f"| {source_sector[sector]} | {index + 1} | ({k}, {j}) |"
            in yukawa_ledger
            for sector, modes in SECTOR_MODES.items()
            for index, (k, j) in enumerate(modes)
        ),
    }
    return {
        "precedence_rule": (
            "The phase/orientation/cyclic theorem discharge, finite ledgers, "
            "sector incidence, triality, and weak-double-projection artifacts "
            "are authoritative imported results. v8.2 does not rederive or "
            "replace their generation-selection architecture."
        ),
        "sources": [
            {
                "path": path,
                "sha256": _source_sha256(path),
                "role": {
                    SOURCE_PATHS[0]: "primitive spectrum {1,2,3}",
                    SOURCE_PATHS[1]: "raw frozen sector mode ledgers",
                    SOURCE_PATHS[2]: "Yukawa-labelled frozen mode ledgers",
                    SOURCE_PATHS[3]: (
                        "triality projectors and no-double-counting theorem"
                    ),
                    SOURCE_PATHS[4]: (
                        "middle-up weak-double-projection bridge"
                    ),
                    SOURCE_PATHS[5]: "finite sector incidence operators",
                }[path],
            }
            for path in SOURCE_PATHS
        ],
        "primitive_low_energy_closure_spectrum": [1, 2, 3],
        "closure_status": (
            "PRIMITIVE_LOW_ENERGY_CLOSURE_SPECTRUM_123_"
            "DERIVED_CONDITIONAL"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def foundational_doctrine() -> dict[str, Any]:
    return {
        "statement": DOCTRINE_STATEMENT,
        "causal_order": [
            "geometry and topology",
            "classical boundary-value problem",
            "discrete resonances and modes",
            "effective particles and QFT",
        ],
        "Layer_G_geometric_core": {
            "ontology": (
                "deterministic action/field equations, topology, variational "
                "domain, classical modes, and interface response"
            ),
            "generation_projector_status": ATTACHMENT_STATUS,
            "mode_response_status": (
                "BLOCKED_BY_UNDEFINED_CLASSICAL_MODE_STRESS"
            ),
        },
        "Layer_Q_emergent_quantum_correspondence": {
            "status": "OPEN_EMERGENT_QUANTUM_CORRESPONDENCE",
            "v7_2_role": "GEOMETRIC_TO_QFT_CORRESPONDENCE",
            "open_objects": [
                "probabilistic measurement statistics",
                "Bell-compatible correlations",
                "spin-statistics",
                "unitary effective evolution",
                "scattering and decay rules",
                "radiative observables",
            ],
            "geometric_core_blocked_solely_by_Layer_Q": False,
        },
        "output_typing": {
            "Brown_York_and_shape_response": "GEOMETRIC_CORE_OUTPUT",
            "localized_SM_gauge_and_Yukawa_parameters": (
                "EFFECTIVE_QFT_PARAMETER"
            ),
            "v7_2_observable_map": "GEOMETRIC_TO_QFT_CORRESPONDENCE",
            "G_F": "EMPIRICAL_CALIBRATION",
            "full_quantum_emergence": "OPEN_EMERGENT_QUANTUM_MAP",
            "legacy_overlap_and_CKM_rules": "HISTORICAL_SCREEN",
        },
        "microscopic_quantum_field_primitive_added": False,
    }


def frozen_family_modules() -> dict[str, Any]:
    modules: dict[str, Any] = {}
    for sector, modes in SECTOR_MODES.items():
        modules[sector] = {
            "symbol": {
                "charged_lepton": "F_l",
                "up": "F_u",
                "down": "F_d",
            }[sector],
            "basis": [list(mode) for mode in modes],
            "slot_roles": ["base", "excitation_1", "excitation_2"],
            "dimension": 3,
            "sector_projector": {
                "charged_lepton": "P_l",
                "up": "P_u",
                "down": "P_d",
            }[sector],
            "mode_projectors": [
                {
                    "symbol": f"Pi_{sector},{index}",
                    "matrix": [
                        [1 if row == column == index else 0 for column in range(3)]
                        for row in range(3)
                    ],
                    "rank": 1,
                }
                for index in range(3)
            ],
            "sum_of_mode_projectors": "I_F",
            "classification": FAMILY_CLASSIFICATION,
        }
    return {
        "modules": modules,
        "direct_sum": "F_l direct_sum F_u direct_sum F_d",
        "family_slot_count": 3,
        "generation_selection_rederived_in_v8_2": False,
        "generation_selection_imported_as_authoritative": True,
        "classification": FAMILY_CLASSIFICATION,
    }


def sector_incidence_attachment() -> dict[str, Any]:
    return {
        "finite_labels": {
            "C": [0, 1],
            "sigma": [-1, 1],
        },
        "projectors": {
            "P_nu": "(1-C)(1+sigma)/2",
            "P_l": "(1-C)(1-sigma)/2",
            "P_u": "C(1+sigma)/2",
            "P_d": "C(1-sigma)/2",
        },
        "down_incidence": {
            "formula": "M(C,sigma)=1+P_d",
            "status": "STRONGLY_SUPPORTED_CANDIDATE",
        },
        "triality_role": (
            "conditional representation-space realization of the same "
            "three family slots; not a second multiplicative family factor"
        ),
        "chirality_compatibility": True,
        "anomaly_compatibility": True,
        "nine_generation_product_architecture_rejected": True,
    }


def master_action_attachment() -> dict[str, Any]:
    return {
        "status": ATTACHMENT_STATUS,
        "localized_field": {
            "formula": (
                "Psi_r in Gamma(S_h tensor E_SM,r tensor F_r)"
            ),
            "owner": "S4_localized on B1 or effective M4",
            "activity": "ACTIVE_IN_S4",
            "Layer_Q_role": (
                "effective localized Dirac-Yukawa propagation"
            ),
        },
        "family_module": {
            "owner": "Layer_G frozen boundary-mode structure",
            "fiber": "F_r=span{u_r,0,u_r,1,u_r,2}",
            "projector": "P_r=sum_(n=0)^2 Pi_r,n",
            "rank": 3,
            "status": FAMILY_CLASSIFICATION,
        },
        "domain": {
            "formula": "D_Dirac,r tensor F_r",
            "base_domain": (
                "H1/2 maximal-isotropic self-adjoint Dirac domain"
            ),
            "mode_projectors_preserve_domain": True,
            "projectors_commute_with_gauge_action": True,
            "projectors_commute_with_chirality": True,
            "off_diagonal_family_domain_allowed": True,
        },
        "ownership_boundary": {
            "geometric_family_module": "Layer_G",
            "localized_SM_Dirac_Yukawa_operator": "Layer_Q_effective",
            "action_defined_mode_stress": None,
        },
        "v8_1_correction": (
            "The v8.1 absence claim is narrowed to a repository-layer "
            "integration failure: the frozen family module existed but had "
            "not been attached to the localized master-action incidence map."
        ),
        "new_dynamical_field_added": False,
        "new_free_parameter_added": False,
        "historical_master_action_rewritten": False,
    }


def higher_mode_typing() -> dict[str, Any]:
    return {
        "primitive_generation_layer": [1, 2, 3],
        "primitive_layer_status": (
            "DERIVED_CONDITIONAL_AND_FROZEN_FOR_CURRENT_CAMPAIGN"
        ),
        "broader_mode_tower": (
            "HIGHER_COMPOSITE_EXCESS_OR_OTHER_EXCITATIONS_"
            "NOT_GENERATION_SLOTS"
        ),
        "additional_generations_inferred_from_tower": False,
        "fourth_family_slot_in_frozen_module": False,
        "physical_excess_gap_theorem_status": (
            "CONDITIONAL_OR_OPEN_OUTSIDE_CURRENT_ATTACHMENT_TARGET"
        ),
        "current_family_projector_blocker": False,
        "reason": (
            "PO-BH-8 places higher closures outside the primitive identity/"
            "orientation/minimal-cyclic layer. Their possible existence does "
            "not enlarge the already frozen physical generation ledger."
        ),
    }


def middle_up_bridge() -> dict[str, Any]:
    weak = _read_json(SOURCE_PATHS[4])
    return {
        "mode": weak["middle_up_mode"],
        "qj": weak["middle_up_qj"],
        "Omega_u": weak["Omega_u"],
        "weak_space_dimension": weak["weak_dimension"],
        "projector_rank": weak["projector_rank"],
        "Z_virt_u2": weak["factor"],
        "applicability": weak["Z_virt_u2_applicability"],
        "dimension_ratio_status": weak[
            "Z_virt_u2_dimension_ratio"
        ],
        "manually_chosen_third_family_label": False,
        "observed_data_used": weak["uses_observed_data"],
        "claim_boundary": (
            "action-linked weak-double-projection result imported "
            "conditionally; it is not yet a physical mass response"
        ),
    }


def mode_response_attachment() -> dict[str, Any]:
    row = {
        "matrix": None,
        "dimension": [3, 3],
        "rank": None,
        "singular_values": None,
        "reason": (
            "The frozen u_f,i modes and projectors now belong to the "
            "localized field/domain ledger, but the mixed metric-mode "
            "variation defining T_ab^(ij) is absent from the action."
        ),
    }
    return {
        "target_operator": (
            "T_ab^(ij)=<u_f,i,(delta A_geom/delta h^ab)u_f,j>"
        ),
        "equivalent_missing_variation": (
            "delta^2 S_BHSM^strat/(delta h^ab delta u_f)"
        ),
        "projectors_attached": True,
        "full_brown_york_tensor_available": True,
        "first_shape_response_available": True,
        "mode_stress_available": False,
        "universal_scalar_response_reused": False,
        "charged_lepton": dict(row),
        "up": dict(row),
        "down": dict(row),
        "off_diagonal_incidence": None,
        "historical_overlap_inserted": False,
        "result": FINAL_VERDICT,
    }


def observable_results() -> dict[str, Any]:
    return {
        "charged_lepton_mass_ratios": None,
        "up_mass_ratios": None,
        "down_mass_ratios": None,
        "CKM": {
            "matrix": None,
            "angles": None,
            "CP_phase": None,
            "Jarlskog": None,
            "reason": (
                "no action-derived up/down mode-response matrices or "
                "nonaligned left singular-vector bases exist"
            ),
        },
        "family_count": {
            "value": 3,
            "status": (
                "FROZEN_DERIVED_CONDITIONAL_GEOMETRIC_STRUCTURE_"
                "NOT_A_NEW_V8_2_PREDICTION"
            ),
        },
        "distinct_action_derived_mass_prediction": False,
    }


def domain_wall_fallback() -> dict[str, Any]:
    return {
        "status": "PAUSED_NON_AUTHORITATIVE_FALLBACK",
        "primary_family_mechanism": False,
        "new_cap_fermion_action_committed": False,
        "field_ledger_replaced": False,
        "reactivation_condition": (
            "only if the frozen projector attachment is independently "
            "falsified or an explicit later campaign authorizes a new "
            "microscopic mechanism"
        ),
    }


def prediction_freeze() -> dict[str, Any]:
    return {
        "version": VERSION,
        "foundational_doctrine": foundational_doctrine(),
        "imported_sources": source_imports(),
        "family_modules": frozen_family_modules(),
        "sector_incidence": sector_incidence_attachment(),
        "master_action_attachment": master_action_attachment(),
        "higher_mode_typing": higher_mode_typing(),
        "middle_up_bridge": middle_up_bridge(),
        "mode_response": mode_response_attachment(),
        "observables": observable_results(),
        "falsification_condition": (
            "the current obstruction is removed only by an action-derived "
            "classical mode-stress/incidence operator on the frozen family "
            "modules that yields definite charged-sector response matrices"
        ),
        "comparison_data_used": False,
        "retuning_permitted": False,
        "status": (
            "FROZEN_FAMILY_MODULE_ATTACHED_MODE_STRESS_UNDEFINED"
        ),
    }


def prediction_freeze_hash() -> str:
    return sha256(
        deterministic_json(prediction_freeze()).encode("utf-8")
    ).hexdigest().upper()


def completion_gate_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_1_0_completion_gate",
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "current_verdict": FINAL_VERDICT,
        "BHSM_1_0_release_complete": False,
        "current_tier_status": {
            "Tier_A": "COMPLETE",
            "Tier_B": "COMPLETE",
            "Tier_C": "BLOCKED_EXACT_OBJECT_PROVED",
        },
        "core_verdict": "BHSM_CORE_COMPLETE",
        "physical_verdict": "BHSM_PHYSICAL_COMPLETE",
        "observable_transport_verdict": (
            "BHSM_COMMON_SCHEME_OBSERVABLE_TRANSPORT_FUNCTOR_CONSTRUCTED"
        ),
        "mode_resolved_curvature_incidence": (
            "BHSM_MODE_RESOLVED_CURVATURE_INCIDENCE_BLOCKED_BY_"
            "UNDEFINED_MODE_STRESS"
        ),
        "generation_architecture": (
            "THREE_GENERATION_ARCHITECTURE_DERIVED_AND_LOCKED_"
            "STRUCTURALLY_CONDITIONAL"
        ),
        "original_generation_projector": (
            "BHSM_ORIGINAL_THREE_SLOT_GENERATION_PROJECTOR_"
            "IMPORTED_AS_FROZEN_STRUCTURE"
        ),
        "generation_projector_attachment": ATTACHMENT_STATUS,
        "projector_classification": FAMILY_CLASSIFICATION,
        "Layer_G_generation_status": ATTACHMENT_STATUS,
        "Layer_Q_status": "OPEN_EMERGENT_QUANTUM_CORRESPONDENCE",
        "distinct_action_derived_prediction_exists": False,
        "RB01": {
            "status": "CLOSED",
            "architecture": (
                "BHSM_STRATIFIED_MASTER_ACTION_CLOSED_WITH_"
                "COVARIANT_COMPATIBILITY_MAPS"
            ),
            "release_blocking": False,
        },
        "RB15": {
            "status": "BLOCKED_EXACT_OBJECT_PROVED",
            "resolution": FINAL_VERDICT,
        },
        "RB16": {
            "status": "DOWNSTREAM_BLOCKED",
            "resolution": (
                "release packaging remains ineligible while RB-15 is open"
            ),
        },
        "resolved_release_blockers": [
            "RB-01", "RB-03", "RB-04", "RB-05", "RB-06", "RB-07",
            "RB-08", "RB-09", "RB-10", "RB-11", "RB-12", "RB-13",
            "RB-14",
        ],
        "open_release_blockers": ["RB-15", "RB-16"],
        "parameter_free_extension_blocker": "RB-02",
        "next_highest_upstream_blocker": NEXT_MISSING_OBJECT,
        "one_universal_dimensionful_calibration": "G_F",
        "action_extension_introduced": False,
        "new_dynamical_field_introduced": False,
        "new_mediator_introduced": False,
        "fitted_parameter_used": False,
        "measured_mode_selection_used": False,
        "observed_generation_count_selection_used": False,
        "assumed_three_family_module_used": False,
        "mode_ledger_typed_as_input": False,
        "higher_tower_used_as_generation_slots": False,
        "spacetime_harmonic_relabeling_used": False,
        "domain_wall_used_as_family_mechanism": False,
        "arbitrary_matrix_input_used": False,
        "arbitrary_collar_coefficient_used": False,
        "arbitrary_profile_used": False,
        "arbitrary_gap_floor_used": False,
        "arbitrary_cutoff_used": False,
        "inserted_zero_mode_used": False,
        "unselected_domain_parameter_used": False,
        "second_scale_calibration_used": False,
        "hidden_calibration_used": False,
        "post_comparison_retuning_used": False,
        "frozen_prediction_changed": False,
        "official_prediction_changed": False,
        "bhsm_1_0_release_complete_claimed": False,
    }


def payload() -> dict[str, Any]:
    result = {
        "artifact": ARTIFACT_NAME,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "steering_correction_applied": True,
        "campaign_type": "INTEGRATION_NOT_PROJECTOR_DERIVATION",
        "foundational_doctrine": foundational_doctrine(),
        "authoritative_imports": source_imports(),
        "frozen_family_modules": frozen_family_modules(),
        "sector_incidence_attachment": sector_incidence_attachment(),
        "master_action_attachment": master_action_attachment(),
        "higher_mode_typing": higher_mode_typing(),
        "middle_up_weak_projection": middle_up_bridge(),
        "mode_response_attachment": mode_response_attachment(),
        "prediction_status": observable_results(),
        "prediction_freeze": prediction_freeze(),
        "prediction_freeze_sha256": prediction_freeze_hash(),
        "fallback_domain_wall_status": domain_wall_fallback(),
        "RB15": {
            "status": "BLOCKED_EXACT_OBJECT_PROVED",
            "resolution": FINAL_VERDICT,
        },
        "RB16": {
            "status": "DOWNSTREAM_BLOCKED",
            "release_package_generated": False,
        },
        "release_status": RELEASE_VERDICT,
        "remaining_exact_obstruction": NEXT_MISSING_OBJECT,
        "final_verdict": FINAL_VERDICT,
        "integrity": {
            "fit_used": False,
            "observed_family_count_selection_used": False,
            "generation_projector_rederived": False,
            "higher_modes_called_generations": False,
            "arbitrary_Yukawa_matrix_used": False,
            "new_mediator_used": False,
            "second_scale_used": False,
            "hidden_calibration_used": False,
            "post_comparison_retuning_used": False,
        },
    }
    validation = {
        "authoritative_sources_valid": result[
            "authoritative_imports"
        ]["validation_passed"],
        "three_frozen_modules": (
            set(result["frozen_family_modules"]["modules"])
            == {"charged_lepton", "up", "down"}
        ),
        "all_modules_rank_three": all(
            module["dimension"] == 3
            for module in result["frozen_family_modules"][
                "modules"
            ].values()
        ),
        "exact_frozen_ledgers": (
            result["frozen_family_modules"]["modules"]["charged_lepton"][
                "basis"
            ]
            == [[0, 0], [5, 2], [9, 3]]
            and result["frozen_family_modules"]["modules"]["up"]["basis"]
            == [[0, 0], [6, 0], [10, 1]]
            and result["frozen_family_modules"]["modules"]["down"]["basis"]
            == [[0, 0], [6, 3], [8, 2]]
        ),
        "master_action_attachment_recorded": (
            result["master_action_attachment"]["status"]
            == ATTACHMENT_STATUS
        ),
        "higher_tower_not_family_slots": not result[
            "higher_mode_typing"
        ]["additional_generations_inferred_from_tower"],
        "middle_up_bridge_preserved": (
            result["middle_up_weak_projection"]["Z_virt_u2"] == "1/2"
        ),
        "mode_stress_fail_closed": (
            result["mode_response_attachment"]["mode_stress_available"]
            is False
        ),
        "no_response_fabricated": all(
            result["mode_response_attachment"][sector]["matrix"] is None
            for sector in ("charged_lepton", "up", "down")
        ),
        "domain_wall_is_fallback": (
            result["fallback_domain_wall_status"][
                "primary_family_mechanism"
            ]
            is False
        ),
        "quantum_correspondence_open": result[
            "foundational_doctrine"
        ]["Layer_Q_emergent_quantum_correspondence"]["status"]
        == "OPEN_EMERGENT_QUANTUM_CORRESPONDENCE",
    }
    result["validation"] = validation
    result["validation_passed"] = all(validation.values())
    return result


def status_report() -> dict[str, Any]:
    data = payload()
    return {
        "version": VERSION,
        "campaign_type": data["campaign_type"],
        "authoritative_imports": data["authoritative_imports"],
        "foundational_doctrine": data["foundational_doctrine"],
        "frozen_family_modules": data["frozen_family_modules"],
        "sector_incidence_attachment": data[
            "sector_incidence_attachment"
        ],
        "master_action_attachment": data["master_action_attachment"],
        "higher_mode_typing": data["higher_mode_typing"],
        "middle_up_weak_projection": data[
            "middle_up_weak_projection"
        ],
        "mode_response_attachment": data["mode_response_attachment"],
        "prediction_status": data["prediction_status"],
        "prediction_freeze_sha256": data["prediction_freeze_sha256"],
        "fallback_domain_wall_status": data[
            "fallback_domain_wall_status"
        ],
        "RB15": data["RB15"],
        "RB16": data["RB16"],
        "release_status": data["release_status"],
        "remaining_exact_obstruction": data[
            "remaining_exact_obstruction"
        ],
        "final_verdict": FINAL_VERDICT,
        "validation_passed": data["validation_passed"],
    }


def status_to_markdown(report: dict[str, Any] | None = None) -> str:
    report = status_report() if report is None else report
    modules = report["frozen_family_modules"]["modules"]
    lines = [
        "# BHSM v8.2 generation-projector action attachment",
        "",
        (
            "The previously derived three-slot family modules are imported "
            "as frozen geometric structures and attached to the localized "
            "master-action field and Dirac domain."
        ),
        "",
        "| Sector | Base | Excitation 1 | Excitation 2 |",
        "| --- | --- | --- | --- |",
    ]
    for sector in ("charged_lepton", "up", "down"):
        basis = modules[sector]["basis"]
        lines.append(
            f"| {sector} | {tuple(basis[0])} | {tuple(basis[1])} | "
            f"{tuple(basis[2])} |"
        )
    lines.extend(
        [
            "",
            f"- Family classification: `{FAMILY_CLASSIFICATION}`",
            (
                "- Master-action attachment: "
                f"`{report['master_action_attachment']['status']}`"
            ),
            (
                "- Primitive spectrum: "
                "`[1, 2, 3]` (`DERIVED_CONDITIONAL`)"
            ),
            (
                "- Higher tower: other/composite/excess excitations, "
                "not extra generation slots"
            ),
            "- Middle-up `(6,0)` weak projection: `Z_virt=1/2`",
            "- Mode-response matrices: `None`",
            "- Mass ratios: `None`",
            "- CKM: `None`",
            (
                "- Emergent quantum correspondence: "
                "`OPEN_EMERGENT_QUANTUM_CORRESPONDENCE`"
            ),
            (
                "- Prediction freeze SHA-256: "
                f"`{report['prediction_freeze_sha256']}`"
            ),
            (
                "- Domain-wall fallback: "
                f"`{report['fallback_domain_wall_status']['status']}`"
            ),
            f"- RB-15: `{report['RB15']['status']}`",
            f"- RB-16: `{report['RB16']['status']}`",
            f"- Release: `{report['release_status']}`",
            "",
            (
                "Remaining exact obstruction: "
                f"`{report['remaining_exact_obstruction']}`"
            ),
            "",
            f"Verdict: `{report['final_verdict']}`",
            "",
        ]
    )
    return "\n".join(lines)


def materialize(root: Path) -> tuple[Path, Path]:
    artifact = root / "artifacts" / f"{ARTIFACT_NAME}.json"
    gate = root / "artifacts" / "BHSM_1_0_completion_gate.json"
    artifact.write_bytes(deterministic_json(payload()).encode("utf-8"))
    gate.write_bytes(
        deterministic_json(completion_gate_payload()).encode("utf-8")
    )
    return artifact, gate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--materialize", action="store_true")
    args = parser.parse_args(argv)
    if not args.materialize:
        parser.error("--materialize is required")
    root = repository_root()
    for path in materialize(root):
        print(path.relative_to(root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
