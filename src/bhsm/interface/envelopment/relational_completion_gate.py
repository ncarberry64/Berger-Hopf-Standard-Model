"""BHSM v10.1 relational doctrine completion, artifacts, and CLI payloads."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .boundary_complementarity import complementarity_payload
from .geometry_reconciliation import geometry_payload
from .global_conservation import conservation_payload
from .neutrino_identity import neutrino_payload
from .relational_axioms import (
    ACTION_LIMIT_VERDICT,
    AUTHOR_DOCTRINE,
    FOUNDATION_VERDICT,
    NEXT_EXACT_OBJECT,
    PRIMARY_VERDICT,
    SOURCE_V10_SHA,
    SPRINT,
    VERSION,
    constraint_ledger,
    deterministic_json,
    doctrine_sha256,
)
from .topological_buoyancy import buoyancy_payload


ARTIFACT_FILES = {
    "doctrine": "BHSM_relational_envelopment_holism_axioms_v10_1.json",
    "constraints": "BHSM_relational_envelopment_constraint_ledger_v10_1.json",
    "buoyancy": "BHSM_topological_buoyancy_gate_v10_1.json",
    "conservation": "BHSM_global_conservation_gate_v10_1.json",
    "complementarity": "BHSM_boundary_complementarity_gate_v10_1.json",
    "neutrino": "BHSM_neutrino_relational_identity_gate_v10_1.json",
}


def extended_parent_action_audit() -> dict[str, Any]:
    return {
        "action_used": "v10.0 S_BHSM^env=S8^env+S5+S_GHY+S4,intrinsic+S_compatibility+S_current",
        "new_terms_added_in_v10_1": [],
        "new_continuous_parameters": [],
        "fields": ["G_AB", "chi", "sigma", "eta", "Lambda_eta", "stratified gauge and boundary fields"],
        "domains": ["M8", "M5 caps", "M4 intrinsic seam", "collar", "finite family fibers"],
        "symmetry": "diffeomorphism and declared gauge covariance, conditional on compatible stratum maps",
        "mass_dimensions": "unchanged from v10.0 dimensional audit",
        "coefficient_source": "v10.0 structural postulate plus retained pre-v10 action ledgers",
        "field_equations": "v10 eta equation plus retained metric, scalar, cap ADM, matcher, intrinsic, and current equations",
        "boundary_conditions": "fixed endpoint/regular cap data and matcher domains exist; one complete orbit domain is not selected",
        "stress_tensor": "eta stress is explicit; total cross-stratum stress pullback remains open",
        "currents": "eta connection current explicit; physical gauge/common-current pullback remains open",
        "constraints": ["eta unit norm", "Hamiltonian/momentum", "cap matcher", "gauge quotient"],
        "required_by_author_axiom": "no new term; v10.1 tests the current action against hard constraints",
        "intrinsic_SM_descends_from_metric": False,
        "classification": "DERIVED_CONDITIONAL",
    }


def measurement_gate() -> dict[str, Any]:
    return {
        "closed_system_state": "Phi_total=Phi_incoming+Phi_environment+Phi_detector",
        "classification": "AUTHOR_ONTOLOGY",
        "initial_asymptotic_states": None,
        "final_asymptotic_states": None,
        "interaction_channels": None,
        "conserved_charge_interface": "conditional sector ledgers only",
        "transition_amplitudes": None,
        "normalized_probabilities": None,
        "detector_amplification": None,
        "decoherence_after_subsystem_reduction": None,
        "frequency_matching_is_measurement_theorem": False,
        "verdict": "BHSM_CLOSED_SYSTEM_TRANSITION_PROBABILITY_THEOREM_REMAINS_OPEN",
        "exact_missing_object": "CLOSED_SYSTEM_TRANSITION_AMPLITUDE",
    }


def hindsight() -> dict[str, list[str]]:
    return {
        "VALIDATED": [
            "exact author doctrine preserved in deterministic semantic JSON",
            "typed author-axiom, ontology, architectural-constraint, and theorem classifications",
            "S3 x M4 identified as a seven-dimensional lifted seam/local reduction rather than M8",
            "normal collar rho, Hopf radion a_F, and proxy texture scale R kept distinct",
            "v10 p2+p8 radial equilibrium follows from variation and is stable conditionally",
            "no explicit dissipative or memory term in the current parent action",
            "on-shell local stress conservation identity with explicit boundary-flux qualification",
            "eta map degree conservation under smooth fixed-domain evolution",
            "eta-sector conjugation involution preserves norm, action invariant, and stress while reversing the phase current",
        ],
        "INVALIDATED": [
            "author axioms treated as already proven physics",
            "S3 x M4 identified with the full eight-dimensional parent",
            "coordinate-dependent integral of T00 called total cosmic energy",
            "phenomenological buoyancy force inserted by hand",
            "antiparticle fields deleted before full equivalence",
            "Dirac/Majorana observable questions declared absent by ontology",
            "local entropy language treated as a proof of global reversibility",
            "frequency matching treated as normalized measurement probabilities",
        ],
        "OPEN": [
            NEXT_EXACT_OBJECT,
            "GLOBAL_HAMILTONIAN_OR_QUASILOCAL_CONSERVATION_THEOREM",
            "MICROSCOPIC_ENVELOPMENT_COARSE_GRAINING_AND_ENTROPY_PRODUCTION_THEOREM",
            "ETA_BOUNDARY_COMPLEMENTARITY_INVOLUTION_WITH_FULL_GAUGE_REPRESENTATION_DATA",
            "NEUTRINO_VERTEX_PHASE_OBSERVABLE_MAP",
            "CLOSED_SYSTEM_TRANSITION_AMPLITUDE",
            "ACTION_SELECTED_GAUGE_DRESSED_CHARGED_SELF_ENVELOPMENT_RELATIVE_PERIODIC_ORBIT_WITH_LOCAL_CHIRAL_TRANSGRESSION",
        ],
    }


def completion_payload() -> dict[str, Any]:
    geometry = geometry_payload()
    buoyancy = buoyancy_payload()
    conservation = conservation_payload()
    complementarity = complementarity_payload()
    neutrino = neutrino_payload()
    constraints = constraint_ledger()
    validation = {
        "doctrine_exact_hash_recorded": len(doctrine_sha256()) == 64,
        "constraint_ledger_valid": constraints["validation_passed"],
        "geometry_reconciled": geometry["validation_passed"],
        "buoyancy_fails_closed": buoyancy["validation_passed"],
        "conservation_qualified": conservation["validation_passed"],
        "complementarity_fails_closed": complementarity["validation_passed"],
        "neutrino_fails_closed": neutrino["validation_passed"],
        "no_new_action_term": extended_parent_action_audit()["new_terms_added_in_v10_1"] == [],
        "no_physical_probability": measurement_gate()["normalized_probabilities"] is None,
    }
    return {
        "artifact": "BHSM_relational_envelopment_completion_gate_v10_1",
        "version": VERSION,
        "sprint": SPRINT,
        "source_v10_sha": SOURCE_V10_SHA,
        "primary_verdict": PRIMARY_VERDICT,
        "foundation_verdict": FOUNDATION_VERDICT,
        "action_limit_verdict": ACTION_LIMIT_VERDICT,
        "canonical_paradigm": AUTHOR_DOCTRINE["paradigm"],
        "foundational_axiom": AUTHOR_DOCTRINE["foundational_axiom"],
        "doctrine_sha256": doctrine_sha256(),
        "constraints": constraints,
        "geometry": geometry,
        "extended_parent_action": extended_parent_action_audit(),
        "topological_buoyancy": buoyancy,
        "time_entropy_conservation": conservation,
        "boundary_complementarity": complementarity,
        "neutrino_identity": neutrino,
        "measurement": measurement_gate(),
        "hindsight": hindsight(),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "measured_values_used_as_theorem_inputs": False,
        "new_elementary_particles": [],
        "new_gravity_mediator": False,
        "fundamental_dissipation_introduced": False,
        "physical_mass_emitted": False,
        "physical_CKM_emitted": False,
        "physical_PMNS_emitted": False,
        "next_exact_object": NEXT_EXACT_OBJECT,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    constraints = constraint_ledger()
    constraints["geometry_reconciliation"] = geometry_payload()
    return {
        "doctrine": AUTHOR_DOCTRINE,
        "constraints": constraints,
        "buoyancy": buoyancy_payload(),
        "conservation": conservation_payload(),
        "complementarity": complementarity_payload(),
        "neutrino": neutrino_payload(),
    }


def canonical_completion_gate_payload() -> dict[str, Any]:
    from .completion_gate import canonical_completion_gate_payload as v10_gate

    gate = v10_gate()
    gate.update(
        {
            "version": VERSION,
            "sprint": SPRINT,
            "source_v10_sha": SOURCE_V10_SHA,
            "current_verdict": PRIMARY_VERDICT,
            "action_limit_verdict": ACTION_LIMIT_VERDICT,
            "canonical_paradigm": AUTHOR_DOCTRINE["paradigm"],
            "doctrine_sha256": doctrine_sha256(),
            "next_highest_upstream_blocker": NEXT_EXACT_OBJECT,
            "author_doctrine_integrated": True,
            "author_doctrine_promoted_to_physical_theorem": False,
            "new_terms_in_v10_1": [],
            "new_continuous_parameters_in_v10_1": [],
            "physical_particle_derivation_complete": False,
            "physical_matrix_promoted": False,
            "BHSM_1_0_release_complete": False,
        }
    )
    gate["RB15"] = {
        "status": "BLOCKED_BY_RELATIONAL_GLOBAL_LOCAL_ACTION_CONSTRAINT",
        "resolution": NEXT_EXACT_OBJECT,
    }
    return gate


def command_payload(command: str) -> dict[str, Any]:
    full = completion_payload()
    sections = {
        "relational-envelopment-status": full,
        "topological-buoyancy-status": full["topological_buoyancy"],
        "global-conservation-status": full["time_entropy_conservation"],
        "boundary-complementarity-status": full["boundary_complementarity"],
        "neutrino-identity-status": full["neutrino_identity"],
        "relational-constraint-status": full["constraints"],
    }
    if command not in sections:
        raise ValueError(f"unknown v10.1 status command: {command}")
    return {
        "version": VERSION,
        "command": command,
        "primary_verdict": PRIMARY_VERDICT,
        "section": sections[command],
        "author_axiom_promoted_to_theorem": False,
        "frozen_predictions_changed": False,
        "physical_matrix_emitted": False,
        "next_exact_object": NEXT_EXACT_OBJECT,
    }


def command_to_markdown(command: str, payload: dict[str, Any] | None = None) -> str:
    data = command_payload(command) if payload is None else payload
    return "\n".join(
        [
            f"# BHSM v10.1 {command}",
            "",
            f"Primary verdict: `{data['primary_verdict']}`",
            "",
            "- Author axiom promoted to theorem: `false`",
            "- Frozen predictions changed: `false`",
            "- Physical matrix emitted: `false`",
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
