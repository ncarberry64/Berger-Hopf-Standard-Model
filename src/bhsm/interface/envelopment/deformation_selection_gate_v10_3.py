"""BHSM v10.3 minimal deformation-domain selection and completion gate."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .common_envelopment_mode_v10_3 import common_mode_payload
from .coupled_mode_rank_v10_3 import coupled_rank_payload
from .deformation_intertwiner_v10_3 import intertwiner_payload
from .embedding_constraint_v10_3 import EMBEDDING_VERDICT, embedding_payload
from .effective_mode_reductions_v10_3 import effective_reduction_payload
from .full_configuration_space_v10_3 import CONFIGURATION_VERDICT, configuration_payload
from .gauge_invariant_deformation_v10_3 import DEFORMATION_VERDICT, deformation_payload
from .global_zero_mode_v10_3 import GLOBAL_VERDICT, global_payload
from .local_radion_v10_3 import RADION_VERDICT, radion_payload
from .relational_axioms import AUTHOR_DOCTRINE, deterministic_json, doctrine_sha256
from .stress_pullback_v10_3 import STRESS_VERDICT, stress_payload
from .three_mode_architecture_v10_3 import (
    ARCHITECTURE_VERDICT,
    NEXT_EXACT_OBJECT,
    PRIMARY_VERDICT,
    architecture_payload,
)
from .spacetime_removal_depth_v10_3 import DEPTH_VERDICT, depth_payload
from .three_mode_interference_v10_3 import interference_payload
from .seam_projection_v10_3 import SEAM_VERDICT, seam_payload
from .global_scale_anchor_v10_3 import GLOBAL_VERDICT as GLOBAL_SCALE_VERDICT, global_scale_payload
from .generation_phase_interface_v10_3 import generation_phase_payload


VERSION = "v10.3"
SPRINT = "bhsm-physical-deformation-domain-v10-3"
SOURCE_V10_2_SHA = "dfdbc29217f13bc2c7c5f46a47ce554052b23503"
MINIMALITY_VERDICT = "BHSM_PRE_UNIFICATION_CANDIDATE_AUDIT_INCONCLUSIVE"

ARTIFACT_FILES = {
    "configuration": "BHSM_full_configuration_space_v10_3.json",
    "dof": "BHSM_physical_deformation_dof_ledger_v10_3.json",
    "stress": "BHSM_common_domain_stress_pullback_v10_3.json",
    "global": "BHSM_global_restoring_constraint_v10_3.json",
    "common_mode": "BHSM_common_envelopment_mode_v10_3.json",
    "intertwiner": "BHSM_deformation_intertwiner_v10_3.json",
    "rank": "BHSM_coupled_physical_rank_v10_3.json",
    "three_mode": "BHSM_three_mode_architecture_v10_3.json",
    "depth": "BHSM_spacetime_removal_depth_gate_v10_3.json",
    "interference": "BHSM_three_mode_interference_gate_v10_3.json",
    "seam": "BHSM_seam_projection_gate_v10_3.json",
    "scale": "BHSM_global_scale_anchor_policy_v10_3.json",
    "selection": "BHSM_minimal_deformation_selection_gate_v10_3.json",
}


CRITERIA = (
    "action_owned",
    "gauge_invariant",
    "one_physical_scalar",
    "positive_kinetic",
    "well_posed_domain",
    "complete_localized_stress_source",
    "global_restoring_relation",
    "no_new_mediator",
    "no_new_continuous_coefficient",
    "frozen_limit_recovers_current_action",
    "relational_holism_compatible",
    "weak_field_path",
)


def candidate_rows() -> list[dict[str, Any]]:
    return [
        {
            "candidate": "direct M4 embedding X:M4->M8",
            "action_owned": False,
            "gauge_invariant": "unresolved",
            "one_physical_scalar": False,
            "positive_kinetic": None,
            "well_posed_domain": False,
            "complete_localized_stress_source": False,
            "global_restoring_relation": False,
            "no_new_mediator": True,
            "no_new_continuous_coefficient": "possible but unproved",
            "frozen_limit_recovers_current_action": True,
            "relational_holism_compatible": True,
            "weak_field_path": False,
            "fatal_reason": "codimension four and X is absent from the action domain",
        },
        {
            "candidate": "lifted Sigma7 codimension-one embedding",
            "action_owned": False,
            "gauge_invariant": "conditional after quotient",
            "one_physical_scalar": "conditional",
            "positive_kinetic": None,
            "well_posed_domain": False,
            "complete_localized_stress_source": False,
            "global_restoring_relation": False,
            "no_new_mediator": True,
            "no_new_continuous_coefficient": "possible but unproved",
            "frozen_limit_recovers_current_action": True,
            "relational_holism_compatible": True,
            "weak_field_path": False,
            "fatal_reason": "no Sigma7 action owner or M4-to-Sigma7 localization map",
        },
        {
            "candidate": "local Hopf breathing beta",
            "action_owned": True,
            "gauge_invariant": True,
            "one_physical_scalar": True,
            "positive_kinetic": True,
            "well_posed_domain": False,
            "complete_localized_stress_source": False,
            "global_restoring_relation": False,
            "no_new_mediator": True,
            "no_new_continuous_coefficient": True,
            "frozen_limit_recovers_current_action": True,
            "relational_holism_compatible": True,
            "weak_field_path": "conditional",
            "fatal_reason": "runaway/no background plus incomplete cross-stratum ownership",
        },
        {
            "candidate": "critical scalar-wall fold q",
            "action_owned": True,
            "gauge_invariant": True,
            "one_physical_scalar": True,
            "positive_kinetic": True,
            "well_posed_domain": True,
            "complete_localized_stress_source": False,
            "global_restoring_relation": False,
            "no_new_mediator": True,
            "no_new_continuous_coefficient": False,
            "frozen_limit_recovers_current_action": True,
            "relational_holism_compatible": "not established",
            "weak_field_path": False,
            "fatal_reason": "not a normal/radion mode; G5 remains unselected and parent stress is incomplete",
        },
        {
            "candidate": "coupled q_env=delta beta+beta0' psi",
            "action_owned": False,
            "gauge_invariant": True,
            "one_physical_scalar": "formal",
            "positive_kinetic": "radion part only",
            "well_posed_domain": False,
            "complete_localized_stress_source": False,
            "global_restoring_relation": False,
            "no_new_mediator": True,
            "no_new_continuous_coefficient": True,
            "frozen_limit_recovers_current_action": True,
            "relational_holism_compatible": True,
            "weak_field_path": False,
            "fatal_reason": "psi absent and beta0'=0 on the current homogeneous background",
        },
    ]


def admissible(row: dict[str, Any]) -> bool:
    return all(row[key] is True for key in CRITERIA)


def extension_comparison() -> list[dict[str, Any]]:
    return [
        {
            "class": "distributional dynamical seam",
            "new_field_content": "varied embedding support and its normal bundle",
            "new_continuous_parameters": [],
            "unresolved_choice": "M4 codimension four versus lifted Sigma7 codimension one",
            "adopted": False,
        },
        {
            "class": "smooth parent defect",
            "new_field_content": "action-selected localization profile or soliton realization",
            "new_continuous_parameters": "none only if width follows from existing action",
            "unresolved_choice": "which M8 field localizes every M4 sector",
            "adopted": False,
        },
        {
            "class": "full local-radion pushforward",
            "new_field_content": "none in M8; replaces/completes lower-stratum ownership",
            "new_continuous_parameters": [],
            "unresolved_choice": "relation to independently owned S5 and S4 actions",
            "adopted": False,
        },
    ]


def minimality_payload() -> dict[str, Any]:
    rows = candidate_rows()
    selected = [row["candidate"] for row in rows if admissible(row)]
    return {
        "criteria": list(CRITERIA),
        "candidates": rows,
        "fully_admissible_candidates": selected,
        "selected_variable": None,
        "unique": None,
        "buoyancy_physical_scalar_count": 0,
        "new_fields_adopted": [],
        "new_parameters_adopted": [],
        "extensions": extension_comparison(),
        "physical_inequivalence_proved": False,
        "reason_inconclusive": "candidate rows are reduced representations until the common cross-domain Hessian is known",
        "verdict": MINIMALITY_VERDICT,
    }


def completion_payload() -> dict[str, Any]:
    configuration = configuration_payload()
    embedding = embedding_payload()
    radion = radion_payload()
    deformation = deformation_payload()
    stress = stress_payload()
    global_result = global_payload()
    minimality = minimality_payload()
    common_mode = common_mode_payload()
    intertwiner = intertwiner_payload()
    reductions = effective_reduction_payload()
    rank = coupled_rank_payload()
    architecture = architecture_payload()
    depth = depth_payload()
    interference = interference_payload()
    seam = seam_payload()
    scale = global_scale_payload()
    generations = generation_phase_payload()
    validation = {
        "configuration_valid": configuration["validation_passed"],
        "embedding_valid": embedding["validation_passed"],
        "radion_valid": radion["validation_passed"],
        "deformation_valid": deformation["validation_passed"],
        "stress_valid": stress["validation_passed"],
        "global_valid": global_result["validation_passed"],
        "no_candidate_selected": minimality["fully_admissible_candidates"] == [],
        "no_extension_adopted": not any(row["adopted"] for row in extension_comparison()),
        "common_mode_valid": common_mode["validation_passed"],
        "intertwiner_valid": intertwiner["validation_passed"],
        "rank_valid": rank["validation_passed"],
        "equivalence_unresolved": common_mode["equivalence_status"] == "EQUIVALENCE_UNRESOLVED",
        "inequivalence_not_promoted": not common_mode["physically_inequivalent"],
        "three_mode_architecture_valid": architecture["validation_passed"],
        "depth_gate_valid": depth["validation_passed"],
        "third_mode_not_substituted": depth["selected_depth_functional"] is None,
        "seam_projection_valid": seam["validation_passed"],
        "seam_not_counted": not seam["independent_physical_mode"],
        "interference_gate_valid": interference["validation_passed"],
        "no_interference_output": not interference["physical_output_emitted"],
        "global_scale_policy_valid": scale["validation_passed"],
        "generation_interface_valid": generations["validation_passed"],
        "doctrine_preserved": doctrine_sha256() == "f981a6501526a3ff324cbf5cb4f1e26b1f7d3ecd0c7b2759c200f6aa1ee184b0",
    }
    return {
        "artifact": "BHSM_minimal_deformation_selection_gate_v10_3",
        "version": VERSION,
        "sprint": SPRINT,
        "source_v10_2_sha": SOURCE_V10_2_SHA,
        "canonical_paradigm": AUTHOR_DOCTRINE["paradigm"],
        "primary_verdict": PRIMARY_VERDICT,
        "configuration_verdict": CONFIGURATION_VERDICT,
        "embedding_verdict": EMBEDDING_VERDICT,
        "radion_verdict": RADION_VERDICT,
        "deformation_verdict": DEFORMATION_VERDICT,
        "stress_verdict": STRESS_VERDICT,
        "global_verdict": GLOBAL_VERDICT,
        "minimality_verdict": MINIMALITY_VERDICT,
        "architecture_verdict": ARCHITECTURE_VERDICT,
        "depth_verdict": DEPTH_VERDICT,
        "seam_verdict": SEAM_VERDICT,
        "global_scale_verdict": GLOBAL_SCALE_VERDICT,
        "configuration": configuration,
        "embedding": embedding,
        "localized_radion": radion,
        "gauge_invariant_deformation": deformation,
        "common_domain_stress": stress,
        "global_restoring_constraint": global_result,
        "common_envelopment_mode": common_mode,
        "deformation_intertwiner": intertwiner,
        "effective_mode_reductions": reductions,
        "coupled_physical_rank": rank,
        "three_mode_architecture": architecture,
        "spacetime_removal_depth": depth,
        "three_mode_interference": interference,
        "seam_projection": seam,
        "global_scale_anchor": scale,
        "generation_phase_interface": generations,
        "minimality": minimality,
        "v10_2_no_go_preserved": True,
        "topological_buoyancy_claimed": False,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "measured_inputs_used": False,
        "new_gravity_mediator": False,
        "new_fields_adopted": [],
        "new_continuous_parameters": [],
        "fundamental_dissipation": False,
        "physical_mass_or_matrix_emitted": False,
        "seam_fold_hopf_unified": False,
        "seam_fold_hopf_physically_inequivalent": False,
        "equivalence_status": "ONE_MODE_EQUIVALENCE_INVALIDATED_BY_AUTHOR_ONTOLOGY",
        "three_distinct_physical_modes": "AUTHOR_AXIOM",
        "third_mode_action_owned": False,
        "physical_depth_value": None,
        "physical_output_scale": None,
        "generation_phases": [None, None, None],
        "quantum_probabilities": None,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "next_exact_object": NEXT_EXACT_OBJECT,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    completion = completion_payload()
    return {
        "configuration": completion["configuration"],
        "dof": {
            "artifact": "BHSM_physical_deformation_dof_ledger_v10_3",
            "embedding": completion["embedding"],
            "localized_radion": completion["localized_radion"],
            "gauge_invariant_deformation": completion["gauge_invariant_deformation"],
            "buoyancy_physical_scalar_count": completion["minimality"]["buoyancy_physical_scalar_count"],
            "verdict": PRIMARY_VERDICT,
        },
        "stress": completion["common_domain_stress"],
        "global": completion["global_restoring_constraint"],
        "common_mode": completion["common_envelopment_mode"],
        "intertwiner": {
            **completion["deformation_intertwiner"],
            "effective_mode_reductions": completion["effective_mode_reductions"],
        },
        "rank": completion["coupled_physical_rank"],
        "three_mode": completion["three_mode_architecture"],
        "depth": completion["spacetime_removal_depth"],
        "interference": completion["three_mode_interference"],
        "seam": completion["seam_projection"],
        "scale": completion["global_scale_anchor"],
        "selection": completion,
    }


def canonical_completion_gate_payload() -> dict[str, Any]:
    from .buoyancy_gate_v10_2 import canonical_completion_gate_payload as v10_2_gate

    gate = v10_2_gate()
    gate.update(
        {
            "version": VERSION,
            "sprint": SPRINT,
            "source_v10_2_sha": SOURCE_V10_2_SHA,
            "current_verdict": PRIMARY_VERDICT,
            "next_highest_upstream_blocker": NEXT_EXACT_OBJECT,
            "physical_deformation_action_domain_derived": False,
            "buoyancy_physical_scalar_count": 0,
            "common_envelopment_mode_equivalence": "INVALIDATED_BY_AUTHOR_ONTOLOGY",
            "seam_fold_hopf_physically_inequivalent": False,
            "three_distinct_physical_modes": "AUTHOR_AXIOM",
            "third_spacetime_removal_mode_action_owned": False,
            "physical_depth_emitted": False,
            "physical_output_scale_emitted": False,
            "new_fields_in_v10_3": [],
            "new_continuous_parameters_in_v10_3": [],
            "BHSM_1_0_release_complete": False,
        }
    )
    gate["RB15"] = {
        "status": "BLOCKED_BY_MISSING_ACTION_OWNED_SPACETIME_REMOVAL_DEPTH_MODE",
        "resolution": NEXT_EXACT_OBJECT,
    }
    return gate


def command_payload(command: str) -> dict[str, Any]:
    completion = completion_payload()
    sections = {
        "deformation-domain-status": completion["configuration"],
        "embedding-constraint-status": completion["embedding"],
        "local-radion-status": completion["localized_radion"],
        "common-stress-pullback-status": completion["common_domain_stress"],
        "global-zero-mode-status": completion["global_restoring_constraint"],
        "deformation-selection-status": completion["minimality"],
        "common-envelopment-mode-status": completion["common_envelopment_mode"],
        "deformation-intertwiner-status": completion["deformation_intertwiner"],
        "coupled-deformation-rank-status": completion["coupled_physical_rank"],
        "three-mode-envelopment-status": completion["three_mode_architecture"],
        "spacetime-removal-depth-v10-3-status": completion["spacetime_removal_depth"],
        "spacetime-removal-depth-status": completion["spacetime_removal_depth"],
        "three-mode-interference-status": completion["three_mode_interference"],
        "seam-projection-status": completion["seam_projection"],
        "global-scale-anchor-status": completion["global_scale_anchor"],
        "generation-phase-interface-status": completion["generation_phase_interface"],
    }
    if command not in sections:
        raise ValueError(f"unknown v10.3 status command: {command}")
    return {
        "version": VERSION,
        "command": command,
        "primary_verdict": PRIMARY_VERDICT,
        "section": sections[command],
        "topological_buoyancy_claimed": False,
        "frozen_predictions_changed": False,
        "next_exact_object": NEXT_EXACT_OBJECT,
    }


def command_to_markdown(command: str, payload: dict[str, Any] | None = None) -> str:
    data = command_payload(command) if payload is None else payload
    return "\n".join(
        [
            f"# BHSM v10.3 {command}",
            "",
            f"Primary verdict: `{data['primary_verdict']}`",
            "",
            "- Topological Buoyancy claimed: `false`",
            "- Frozen predictions changed: `false`",
            "- New field or parameter adopted: `false`",
            "",
            "## Exact next object",
            "",
            f"`{data['next_exact_object']}`",
        ]
    ) + "\n"


def materialize(root: Path | None = None) -> list[Path]:
    repository = Path(__file__).resolve().parents[4] if root is None else Path(root)
    target = repository / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for key, payload in artifact_payloads().items():
        path = target / ARTIFACT_FILES[key]
        path.write_text(deterministic_json(payload), encoding="utf-8", newline="\n")
        paths.append(path)
    canonical = target / "BHSM_1_0_completion_gate.json"
    canonical.write_text(deterministic_json(canonical_completion_gate_payload()), encoding="utf-8", newline="\n")
    paths.append(canonical)
    return paths
