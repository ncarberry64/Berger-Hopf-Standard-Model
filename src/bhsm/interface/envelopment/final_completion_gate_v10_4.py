"""Deterministic BHSM v10.4 completion and obstruction gate."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .cosmic_unit_anchor_v10_4 import ANCHOR_VERDICT, cosmic_anchor_payload
from .depth_constraint_reduction_v10_4 import (
    EXTENSION_VERDICT,
    NEXT_EXACT_OBJECT,
    REDUCTION_VERDICT,
    reduction_payload,
)
from .generation_monodromy_v10_4 import GENERATION_VERDICT, generation_payload
from .global_equilibrium_v10_4 import GLOBAL_VERDICT, global_equilibrium_payload
from .particle_cycle_v10_4 import PARTICLE_VERDICT, particle_cycle_payload
from .physical_mass_mixing_gate_v10_4 import MASS_MIXING_VERDICT, mass_mixing_payload
from .proper_volume_depth_v10_4 import proper_volume_payload
from .relational_axioms import AUTHOR_DOCTRINE, deterministic_json, doctrine_sha256
from .three_mode_action_v10_4 import ACTION_VERDICT, three_mode_action_payload
from .three_mode_orbit_v10_4 import ORBIT_VERDICT, orbit_payload


VERSION = "v10.4"
SPRINT = "bhsm-spacetime-removal-completion-v10-4"
SOURCE_V10_3_SHA = "887f1e57c2aa967dc3abde61ad19f4745491d7eb"
PRIMARY_VERDICT = EXTENSION_VERDICT

ARTIFACT_FILES = {
    "depth": "BHSM_spacetime_removal_depth_gate_v10_4.json",
    "three_mode": "BHSM_three_mode_action_v10_4.json",
    "global": "BHSM_global_equilibrium_gate_v10_4.json",
    "anchor": "BHSM_cosmic_unit_anchor_v10_4.json",
    "particle": "BHSM_particle_cycle_gate_v10_4.json",
    "mass_mixing": "BHSM_generation_mass_mixing_gate_v10_4.json",
    "completion": "BHSM_final_completion_gate_v10_4.json",
}


def hindsight_payload() -> dict[str, list[str]]:
    return {
        "VALIDATED": [
            "the common-pullback metric volume ratio is a scalar on the regular parent domain",
            "q_V=-(7/8) delta rho on a fixed proper-time homogeneous slice",
            "the exact P1 DeWitt reduction separates one constrained negative volume direction from two positive shape directions",
            "the physical projection of q_V into the reduced beta/gamma space is zero",
            "exact metric degeneracy lies outside the current inverse-metric action domain",
            "no compared geometric extension strictly dominates without an author action choice",
        ],
        "INVALIDATED": [
            "determinant suppression treated as locally gauge invariant without a background pullback",
            "seam treated as a physical fourth mode",
            "unreduced conformal factor labeled a propagating physical ghost",
            "coordinate singularity equated with core physics",
            "arbitrary depth potential inserted",
            "particle mass used as unit calibration",
            "three geometric modes identified with three generations",
            "incomplete current used to print CKM or PMNS",
        ],
        "OPEN": [
            NEXT_EXACT_OBJECT,
            "ACTION_OWNED_THREE_MODE_COMMON_DOMAIN_KINETIC_HESSIAN_AND_SOURCE",
            "STABLE_RELATIVE_PERIODIC_THREE_MODE_ORBIT_AND_PHYSICAL_FLOQUET_SPECTRUM",
            "COMPLETE_ACTION_SELECTED_GLOBAL_EQUILIBRIUM_AND_ELIGIBLE_COSMIC_ANCHOR",
            "ACTION_OWNED_SECTOR_MONODROMY_AND_FROZEN_SLOT_TO_PHASE_INTERTWINERS",
            "NORMALIZED_M4_CORE_BLEED_OUT_REDUCTION_AND_COMPLETE_COMMON_CURRENTS",
        ],
    }


def completion_marks() -> dict[str, Any]:
    return {
        "Mark_I_Foundation": "REACHED",
        "Mark_II_Conditional_architecture": "REACHED_CONDITIONALLY",
        "Mark_III_Physical_derivation": "NOT_REACHED",
        "Mark_IV_Empirical_replacement": "NOT_REACHED",
        "Mark_III_failed_requirements": [
            "healthy action-owned q_D",
            "complete three-mode interaction and stable cycles",
            "selected global geometry and eligible cosmic unit anchor",
            "physical masses, CKM, PMNS, and normalized M4 theory",
        ],
    }


def completion_payload() -> dict[str, Any]:
    depth = proper_volume_payload()
    reduction = reduction_payload()
    action = three_mode_action_payload()
    orbit = orbit_payload()
    global_result = global_equilibrium_payload()
    anchor = cosmic_anchor_payload()
    particles = particle_cycle_payload()
    generations = generation_payload()
    mass_mixing = mass_mixing_payload()
    marks = completion_marks()
    validation = {
        "depth_valid": depth["validation_passed"],
        "reduction_valid": reduction["validation_passed"],
        "volume_no_go_exact": reduction["existing_action_verdict"] == REDUCTION_VERDICT,
        "no_extension_adopted": reduction["new_geometric_fields_adopted"] == [],
        "three_mode_fail_closed": action["target_rank_three_reached"] is False,
        "orbit_not_fabricated": orbit["numerical_solve_performed"] is False,
        "global_not_promoted": global_result["unique_dimensionless_shape"] is False,
        "anchor_not_used": anchor["anchor_count_used"] == 0,
        "particle_cycles_not_fabricated": particles["physical_particle_cycle_count"] == 0,
        "generation_modes_distinct": generations["three_modes_identified_with_generations"] is False,
        "no_mass_or_matrices": mass_mixing["physical_mass_values"] is None and not mass_mixing["matrices_printed"],
        "doctrine_preserved": doctrine_sha256() == "f981a6501526a3ff324cbf5cb4f1e26b1f7d3ecd0c7b2759c200f6aa1ee184b0",
        "mark_III_closed": marks["Mark_III_Physical_derivation"] == "NOT_REACHED",
    }
    return {
        "artifact": "BHSM_final_completion_gate_v10_4",
        "version": VERSION,
        "sprint": SPRINT,
        "source_v10_3_sha": SOURCE_V10_3_SHA,
        "canonical_paradigm": AUTHOR_DOCTRINE["paradigm"],
        "primary_verdict": PRIMARY_VERDICT,
        "depth_verdict": REDUCTION_VERDICT,
        "three_mode_verdict": ACTION_VERDICT,
        "orbit_verdict": ORBIT_VERDICT,
        "global_verdict": GLOBAL_VERDICT,
        "anchor_verdict": ANCHOR_VERDICT,
        "particle_verdict": PARTICLE_VERDICT,
        "generation_verdict": GENERATION_VERDICT,
        "mass_mixing_verdict": MASS_MIXING_VERDICT,
        "spacetime_removal_depth": depth,
        "constraint_reduction_and_extension_decision": reduction,
        "three_mode_action": action,
        "three_mode_orbit_and_interference": orbit,
        "global_equilibrium": global_result,
        "cosmic_unit_anchor": anchor,
        "particle_cycles": particles,
        "generation_monodromy": generations,
        "physical_mass_mixing_and_M4_readout": mass_mixing,
        "completion_marks": marks,
        "hindsight_20_20": hindsight_payload(),
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "measured_particle_inputs_used": [],
        "global_unit_anchor_used": False,
        "new_geometric_fields_adopted": [],
        "new_continuous_parameters_adopted": [],
        "new_gravity_mediator": False,
        "fundamental_dissipation": False,
        "physical_BHSM_complete": False,
        "empirical_replacement_complete": False,
        "physical_outputs": {"depth": None, "interference_energy": None, "masses": None, "CKM": None, "PMNS": None},
        "next_exact_object": NEXT_EXACT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    completion = completion_payload()
    depth = {
        **completion["spacetime_removal_depth"],
        "constraint_reduction": completion["constraint_reduction_and_extension_decision"],
    }
    mass_mixing = {
        **completion["physical_mass_mixing_and_M4_readout"],
        "generation_monodromy": completion["generation_monodromy"],
    }
    return {
        "depth": depth,
        "three_mode": {**completion["three_mode_action"], "orbit_and_interference": completion["three_mode_orbit_and_interference"]},
        "global": completion["global_equilibrium"],
        "anchor": completion["cosmic_unit_anchor"],
        "particle": completion["particle_cycles"],
        "mass_mixing": mass_mixing,
        "completion": completion,
    }


def canonical_completion_gate_payload() -> dict[str, Any]:
    from .deformation_selection_gate_v10_3 import canonical_completion_gate_payload as v10_3_gate

    gate = v10_3_gate()
    gate.update(
        {
            "version": VERSION,
            "sprint": SPRINT,
            "source_v10_3_sha": SOURCE_V10_3_SHA,
            "current_verdict": PRIMARY_VERDICT,
            "next_highest_upstream_blocker": NEXT_EXACT_OBJECT,
            "proper_volume_depth_verdict": REDUCTION_VERDICT,
            "third_spacetime_removal_mode_action_owned": False,
            "three_mode_action_complete": False,
            "physical_particle_cycles_complete": False,
            "physical_mass_mixing_complete": False,
            "new_fields_in_v10_4": [],
            "new_continuous_parameters_in_v10_4": [],
            "BHSM_1_0_release_complete": False,
        }
    )
    gate["RB15"] = {"status": "BLOCKED_BY_GEOMETRIC_DEPTH_EXTENSION_AUTHOR_SELECTION", "resolution": NEXT_EXACT_OBJECT}
    gate["RB16"] = {"status": "DOWNSTREAM_BLOCKED", "resolution": "no physical mass, CKM, or PMNS artifact is licensed"}
    return gate


COMMAND_SECTIONS = {
    "spacetime-removal-depth-status": "spacetime_removal_depth",
    "three-mode-action-status": "three_mode_action",
    "global-equilibrium-status": "global_equilibrium",
    "cosmic-unit-anchor-status": "cosmic_unit_anchor",
    "particle-cycle-status": "particle_cycles",
    "physical-mass-mixing-status": "physical_mass_mixing_and_M4_readout",
    "v10-4-final-completion-status": None,
}


def command_payload(command: str) -> dict[str, Any]:
    if command not in COMMAND_SECTIONS:
        raise ValueError(f"unknown v10.4 status command: {command}")
    completion = completion_payload()
    key = COMMAND_SECTIONS[command]
    section = completion if key is None else completion[key]
    return {
        "version": VERSION,
        "command": command,
        "primary_verdict": PRIMARY_VERDICT,
        "section": section,
        "physical_BHSM_complete": False,
        "frozen_predictions_changed": False,
        "next_exact_object": NEXT_EXACT_OBJECT,
    }


def command_to_markdown(command: str, payload: dict[str, Any] | None = None) -> str:
    data = command_payload(command) if payload is None else payload
    return "\n".join(
        [
            f"# BHSM v10.4 {command}",
            "",
            f"Primary verdict: `{data['primary_verdict']}`",
            "",
            f"Depth verdict: `{REDUCTION_VERDICT}`",
            "",
            "- Physical derivation complete: `false`",
            "- Frozen predictions changed: `false`",
            "- New geometric field or parameter adopted: `false`",
            "- Particle calibration used: `false`",
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
