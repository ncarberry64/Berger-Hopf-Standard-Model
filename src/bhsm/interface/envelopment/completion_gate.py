"""Deterministic BHSM v10.0 completion marks and repository artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .collective_reduction import global_scale_audit, reduction_payload
from .dynamic_action import action_payload
from .floquet import family_and_floquet_payload
from .foundation import (
    FOUNDATION_VERDICT,
    NEXT_EXACT_OBJECT,
    PRIMARY_VERDICT,
    SOURCE_PR208_SHA,
    SPRINT,
    VERSION,
    foundation_payload,
)


ARTIFACT_FILES = {
    "foundation": "BHSM_machian_geometric_envelopment_foundation_v10_0.json",
    "completion": "BHSM_dynamic_envelopment_completion_gate_v10_0.json",
    "reduction": "BHSM_dynamic_envelope_reduction_v10_0.json",
    "scale": "BHSM_global_scale_gate_v10_0.json",
}


def deterministic_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def completion_marks() -> dict[str, Any]:
    return {
        "Mark_I_foundational_completion": {
            "status": "REACHED",
            "basis": FOUNDATION_VERDICT,
        },
        "Mark_II_conditional_architecture_completion": {
            "status": "REACHED_CONDITIONALLY",
            "conditions": [
                "eta is adopted as a structural bosonic unit-spinor order parameter",
                "physical rotation/exchange representatives still require localized texture quotients",
                "local M4 chirality requires a transgression theorem",
                "cycle forms require a stable physical orbit and action-owned immersions",
            ],
        },
        "Mark_III_physical_derivation_completion": {
            "status": "OPEN",
            "missing": [
                "charged timelike orbit",
                "nested color-neutral hadron orbit",
                "three-sector neutrino propagation orbit",
                "physical Floquet stability",
                "absolute unit bridge",
                "CKM and PMNS",
                "normalized four-dimensional theory",
            ],
        },
        "Mark_IV_empirical_replacement": {
            "status": "OPEN",
            "missing": [
                "precomparison physical predictions",
                "production runtime",
                "independent reproduction",
                "successful established and novel tests",
            ],
        },
    }


def hindsight() -> dict[str, list[str]]:
    return {
        "VALIDATED": [
            "canonical relative-periodic envelopment definitions and classification vocabulary",
            "based Map_*^N(S7,S7) fundamental group pi8(S7)=Z2",
            "separation of the Z2 class from physical rotation and exchange loops",
            "eta Euler-Lagrange equation, boundary form, stress, and connection current architecture",
            "seven-dimensional p=2 and p=8 scaling powers",
            "finite-radius p2+p8 collective equilibrium, stiffness, energy, and small-breathing frequency",
            "explicit normalized degree-one prototype profile integrals by independent quadratures",
            "fixed-R nonlinear sigma-amplitude branch formula",
            "stationary-cycle reduction to the v8.9 Gram-Hessian lens",
            "exact overall-scale degeneracy of the current coupling family",
        ],
        "INVALIDATED": [
            "rigid fixed-radius particle ontology",
            "fixed-coordinate boundary inserted before nonlinear formation",
            "metric-plus-scalars completion",
            "quadratic-only eta texture as a finite-radius Derrick equilibrium",
            "isolated-quark completion as the primary confinement object",
            "static-only physical mass or mixing extraction",
            "measurement by verbal resonance without normalized probabilities",
            "arbitrary local mass calibration",
            "current existence as automatic proof of CKM",
            "bosonic eta declared anticommuting to obtain FR statistics",
        ],
        "OPEN": [
            NEXT_EXACT_OBJECT,
            "ACTION_OWNED_2PI_ROTATION_LOOP_IN_THE_LOCALIZED_TEXTURE_QUOTIENT",
            "ACTION_OWNED_TWO_TEXTURE_EXCHANGE_LOOP_AND_HOMOTOPY_IDENTIFICATION",
            "LOCAL_ETA_TEXTURE_TO_M4_CHIRAL_CLIFFORD_TRANSGRESSION",
            "ACTION_OWNED_C3_FLOQUET_TO_FROZEN_KJQ_INTERTWINER",
            "FULL_RANK_COMMON_CURRENT_PULLBACK_ON_A_STABLE_PHYSICAL_ORBIT",
            "CLOSED_COSMIC_BOUNDARY_VALUE_AND_TOPOLOGICAL_NORMALIZATION_THEOREM",
            "COLOR_NEUTRAL_PARENT_WITH_STABLE_COLOR_OPEN_SUB_ENVELOPMENTS",
            "THREE_SECTOR_NEAR_NULL_NEUTRINO_MONODROMY_WITH_WEAK_CURRENT_PULLBACK",
            "COUPLED_BASIN_TRANSITION_AMPLITUDE_AND_PROBABILITY_THEOREM",
            "CANONICALLY_NORMALIZED_FOUR_DIMENSIONAL_ACTION_AND_RUNTIME",
        ],
    }


def completion_status() -> dict[str, Any]:
    foundation = foundation_payload()
    action = action_payload()
    reduction = reduction_payload()
    dynamics = family_and_floquet_payload()
    scale = global_scale_audit()
    validation = {
        "foundation_validated": foundation["validation_passed"],
        "action_validated": action["validation_passed"],
        "reduction_validated": reduction["validation_passed"],
        "Mark_I_reached": completion_marks()["Mark_I_foundational_completion"]["status"] == "REACHED",
        "Mark_II_conditional": completion_marks()["Mark_II_conditional_architecture_completion"]["status"] == "REACHED_CONDITIONALLY",
        "Mark_III_open": completion_marks()["Mark_III_physical_derivation_completion"]["status"] == "OPEN",
        "Mark_IV_open": completion_marks()["Mark_IV_empirical_replacement"]["status"] == "OPEN",
        "no_physical_matrix": dynamics["physical_CKM"] is None and dynamics["physical_PMNS"] is None,
        "frozen_predictions_unchanged": True,
        "measured_flavor_inputs_absent": not dynamics["measured_flavor_inputs_used"],
    }
    return {
        "artifact": "BHSM_dynamic_envelopment_completion_gate_v10_0",
        "version": VERSION,
        "sprint": SPRINT,
        "source_pr208_sha": SOURCE_PR208_SHA,
        "primary_verdict": PRIMARY_VERDICT,
        "foundation_verdict": FOUNDATION_VERDICT,
        "completion_marks": completion_marks(),
        "canonical_foundation": foundation,
        "extended_action": action,
        "collective_reduction": reduction,
        "dynamic_family_and_sectors": dynamics,
        "global_scale": scale,
        "hindsight": hindsight(),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "measured_flavor_inputs_used": False,
        "new_continuous_parameters": [],
        "new_elementary_fermions": [],
        "new_mediators": [],
        "new_structural_bosonic_field": "eta",
        "physical_mass_emitted": False,
        "physical_CKM_emitted": False,
        "physical_PMNS_emitted": False,
        "next_exact_object": NEXT_EXACT_OBJECT,
    }


def global_scale_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_global_scale_gate_v10_0",
        "version": VERSION,
        "sprint": SPRINT,
        "source_pr208_sha": SOURCE_PR208_SHA,
        **global_scale_audit(),
        "frozen_predictions_changed": False,
        "measured_particle_scale_used": False,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "foundation": foundation_payload(),
        "completion": completion_status(),
        "reduction": reduction_payload(),
        "scale": global_scale_payload(),
    }


def canonical_completion_gate_payload() -> dict[str, Any]:
    from ..master_action import geometry_only_geon_fr_carrier_completion as v91

    gate = v91.completion_gate_payload()
    gate.update(
        {
            "version": VERSION,
            "sprint": SPRINT,
            "source_pr208_sha": SOURCE_PR208_SHA,
            "current_verdict": PRIMARY_VERDICT,
            "next_highest_upstream_blocker": NEXT_EXACT_OBJECT,
            "action_extension_introduced": True,
            "action_extension_classification": "STRUCTURAL_POSTULATE",
            "new_dynamical_field_introduced": True,
            "new_dynamical_field": "eta (constrained structural bosonic order parameter)",
            "physical_particle_derivation_complete": False,
            "foundational_completion": "REACHED",
            "conditional_architecture": "REACHED_CONDITIONALLY",
            "physical_derivation": "OPEN",
            "empirical_replacement": "OPEN",
            "physical_matrix_promoted": False,
            "BHSM_1_0_release_complete": False,
        }
    )
    gate["RB15"] = {
        "status": "BLOCKED_BY_NO_ACTION_SELECTED_CHARGED_RELATIVE_PERIODIC_ORBIT",
        "resolution": NEXT_EXACT_OBJECT,
    }
    gate["RB16"] = {
        "status": "DOWNSTREAM_BLOCKED",
        "resolution": "no physical mass, CKM, or PMNS artifact is licensed",
    }
    return gate


def status_to_markdown(payload: dict[str, Any] | None = None, *, title: str | None = None) -> str:
    data = completion_status() if payload is None else payload
    marks = data.get("completion_marks", completion_marks())
    return "\n".join(
        [
            f"# {title or 'BHSM v10.0 Machian Geometric Envelopment'}",
            "",
            f"Primary verdict: `{data.get('primary_verdict', PRIMARY_VERDICT)}`",
            "",
            f"- Foundational completion: `{marks['Mark_I_foundational_completion']['status']}`",
            f"- Conditional architecture: `{marks['Mark_II_conditional_architecture_completion']['status']}`",
            f"- Physical derivation: `{marks['Mark_III_physical_derivation_completion']['status']}`",
            f"- Empirical replacement: `{marks['Mark_IV_empirical_replacement']['status']}`",
            "- Physical CKM/PMNS emitted: `false`",
            "- Frozen predictions changed: `false`",
            "",
            "## Exact next object",
            "",
            f"`{data.get('next_exact_object', NEXT_EXACT_OBJECT)}`",
        ]
    ) + "\n"


def command_payload(command: str) -> dict[str, Any]:
    status = completion_status()
    sections = {
        "unified-envelopment-status": status,
        "dynamic-envelope-status": status["collective_reduction"],
        "completion-marks-status": {"completion_marks": status["completion_marks"]},
        "global-scale-status": status["global_scale"],
        "particle-orbit-status": status["dynamic_family_and_sectors"],
    }
    if command not in sections:
        raise ValueError(f"unknown v10 status command: {command}")
    return {
        "version": VERSION,
        "command": command,
        "primary_verdict": PRIMARY_VERDICT,
        "section": sections[command],
        "physical_mass_emitted": False,
        "physical_matrix_emitted": False,
        "frozen_predictions_changed": False,
        "next_exact_object": NEXT_EXACT_OBJECT,
    }


def command_to_markdown(command: str, payload: dict[str, Any] | None = None) -> str:
    data = command_payload(command) if payload is None else payload
    return "\n".join(
        [
            f"# BHSM v10.0 {command}",
            "",
            f"Primary verdict: `{data['primary_verdict']}`",
            "",
            "- Physical mass emitted: `false`",
            "- Physical matrix emitted: `false`",
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
    written: list[Path] = []
    for key, payload in artifact_payloads().items():
        path = target / ARTIFACT_FILES[key]
        path.write_text(deterministic_json(payload), encoding="utf-8", newline="\n")
        written.append(path)
    canonical = target / "BHSM_1_0_completion_gate.json"
    canonical.write_text(deterministic_json(canonical_completion_gate_payload()), encoding="utf-8", newline="\n")
    written.append(canonical)
    return written
