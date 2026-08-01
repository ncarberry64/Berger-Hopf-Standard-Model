"""Deterministic BHSM v10.2 completion gate and CLI payloads."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .backreaction_v10_2 import BACKREACTION_VERDICT, backreaction_payload
from .buoyancy_functional_v10_2 import (
    NEXT_EXACT_OBJECT,
    PRIMARY_VERDICT,
    SCALE_VERDICT,
    WEAK_FIELD_VERDICT,
    buoyancy_functional_payload,
)
from .global_constraint_v10_2 import GLOBAL_VERDICT, global_constraint_payload
from .normal_geometry_v10_2 import GEOMETRY_VERDICT, geometry_payload
from .radion_variation_v10_2 import RADION_VERDICT, radion_payload
from .relational_axioms import AUTHOR_DOCTRINE, deterministic_json, doctrine_sha256


VERSION = "v10.2"
SPRINT = "bhsm-topological-buoyancy-functional-v10-2"
SOURCE_V10_1_SHA = "8673bcf146a0a239a114ec49d7ec3e1f0bf0ef2b"

ARTIFACT_FILES = {
    "geometry": "BHSM_normal_radion_geometry_v10_2.json",
    "constraint": "BHSM_global_constraint_audit_v10_2.json",
    "functional": "BHSM_topological_buoyancy_functional_v10_2.json",
    "backreaction": "BHSM_local_envelopment_backreaction_v10_2.json",
    "completion": "BHSM_buoyancy_completion_gate_v10_2.json",
}


def action_audit() -> dict[str, Any]:
    return {
        "action_varied": "current stratified S8^env+S5+S_GHY+S4,intrinsic+S_compatibility+S_current",
        "normal_variation": "diagnostic identities only; embedding is fixed",
        "radion_variation": "exact in homogeneous M8 reduction; no positive static equilibrium",
        "GHY_boundary_cancellation": "Dirichlet metric differentiability retained; no embedding equation created",
        "Hamiltonian_constraint": "derived and propagating, but not a global restoring modulus law",
        "momentum_constraint": "derived; homogeneous invariant branch satisfies it",
        "new_terms": [],
        "new_continuous_parameters": [],
        "new_fields": [],
        "new_gravity_mediator": False,
        "fundamental_dissipation": False,
    }


def hindsight() -> dict[str, list[str]]:
    return {
        "VALIDATED": [
            "normal projector, collar Jacobian, and standard shape identities",
            "fixed-embedding ownership of the physical M4 seam",
            "action-owned homogeneous M8 Hopf radion",
            "strictly negative static Hopf-radion curvature derivative",
            "Hamiltonian and momentum constraints with constraint propagation",
            "fixed eta degree is scale free",
            "zero M4-radion mixed action blocks in the current incidence ledger",
            "complete current-action obstruction theorem",
        ],
        "INVALIDATED": [
            "coordinate rho shift treated as physical displacement",
            "proxy R treated as gravitational depth",
            "fixed topology treated as scale fixing",
            "Hamiltonian constraint treated as scalar total cosmic energy",
            "GHY term treated as an embedding action",
            "fixed V_star or curvature target imported without action ownership",
            "phenomenological buoyancy force inserted",
            "arbitrary weak-field or numerical background scan",
        ],
        "OPEN": [
            NEXT_EXACT_OBJECT,
            "ACTION_SELECTED_GLOBAL_RADION_BACKGROUND",
            "LOCALIZED_NORMAL_STRESS_PULLBACK",
            "GAUGE_INVARIANT_ENVELOPMENT_COMPACTNESS_OBSERVABLE",
            "UNIVERSAL_WEAK_FIELD_LIMIT",
            "GLOBAL_DIMENSIONFUL_UNIT_BRIDGE",
        ],
    }


def completion_payload() -> dict[str, Any]:
    geometry = geometry_payload()
    radion = radion_payload()
    constraint = global_constraint_payload()
    backreaction = backreaction_payload()
    functional = buoyancy_functional_payload()
    validation = {
        "geometry_valid": geometry["validation_passed"],
        "radion_valid": radion["validation_passed"],
        "constraint_valid": constraint["validation_passed"],
        "backreaction_valid": backreaction["validation_passed"],
        "functional_valid": functional["validation_passed"],
        "no_new_terms": action_audit()["new_terms"] == [],
        "no_new_parameters": action_audit()["new_continuous_parameters"] == [],
        "doctrine_preserved": doctrine_sha256() == "f981a6501526a3ff324cbf5cb4f1e26b1f7d3ecd0c7b2759c200f6aa1ee184b0",
    }
    return {
        "artifact": "BHSM_buoyancy_completion_gate_v10_2",
        "version": VERSION,
        "sprint": SPRINT,
        "source_v10_1_sha": SOURCE_V10_1_SHA,
        "canonical_paradigm": AUTHOR_DOCTRINE["paradigm"],
        "foundational_axiom": AUTHOR_DOCTRINE["foundational_axiom"],
        "primary_verdict": PRIMARY_VERDICT,
        "geometry_verdict": GEOMETRY_VERDICT,
        "radion_verdict": RADION_VERDICT,
        "global_constraint_verdict": GLOBAL_VERDICT,
        "backreaction_verdict": BACKREACTION_VERDICT,
        "weak_field_verdict": WEAK_FIELD_VERDICT,
        "scale_verdict": SCALE_VERDICT,
        "action": action_audit(),
        "geometry": geometry,
        "radion": radion,
        "global_constraint": constraint,
        "local_backreaction": backreaction,
        "buoyancy_functional": functional,
        "hindsight": hindsight(),
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "measured_values_used": False,
        "physical_depth_emitted": False,
        "physical_mass_scale_emitted": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "next_exact_object": NEXT_EXACT_OBJECT,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "geometry": {**geometry_payload(), "radion": radion_payload()},
        "constraint": global_constraint_payload(),
        "functional": buoyancy_functional_payload(),
        "backreaction": backreaction_payload(),
        "completion": completion_payload(),
    }


def canonical_completion_gate_payload() -> dict[str, Any]:
    from .relational_completion_gate import canonical_completion_gate_payload as v10_1_gate

    gate = v10_1_gate()
    gate.update(
        {
            "version": VERSION,
            "sprint": SPRINT,
            "source_v10_1_sha": SOURCE_V10_1_SHA,
            "current_verdict": PRIMARY_VERDICT,
            "next_highest_upstream_blocker": NEXT_EXACT_OBJECT,
            "topological_buoyancy_derived": False,
            "current_action_exhausted_for_buoyancy": True,
            "new_terms_in_v10_2": [],
            "new_continuous_parameters_in_v10_2": [],
            "physical_particle_derivation_complete": False,
            "physical_matrix_promoted": False,
            "BHSM_1_0_release_complete": False,
        }
    )
    gate["RB15"] = {
        "status": "BLOCKED_BY_NO_PHYSICAL_NORMAL_RADION_ACTION_DOMAIN_AND_GLOBAL_RESTORING_CONSTRAINT",
        "resolution": NEXT_EXACT_OBJECT,
    }
    return gate


def command_payload(command: str) -> dict[str, Any]:
    completion = completion_payload()
    sections = {
        "normal-radion-status": {"geometry": completion["geometry"], "radion": completion["radion"]},
        "global-constraint-status": completion["global_constraint"],
        "topological-buoyancy-status": completion["buoyancy_functional"],
        "local-backreaction-status": completion["local_backreaction"],
        "buoyancy-weak-field-status": completion["buoyancy_functional"]["weak_field"],
    }
    if command not in sections:
        raise ValueError(f"unknown v10.2 status command: {command}")
    return {
        "version": VERSION,
        "command": command,
        "primary_verdict": PRIMARY_VERDICT,
        "section": sections[command],
        "proxy_R_promoted": False,
        "new_gravity_mediator": False,
        "frozen_predictions_changed": False,
        "next_exact_object": NEXT_EXACT_OBJECT,
    }


def command_to_markdown(command: str, payload: dict[str, Any] | None = None) -> str:
    data = command_payload(command) if payload is None else payload
    return "\n".join(
        [
            f"# BHSM v10.2 {command}",
            "",
            f"Primary verdict: `{data['primary_verdict']}`",
            "",
            "- Proxy R promoted to physical depth: `false`",
            "- New gravity mediator: `false`",
            "- Frozen predictions changed: `false`",
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
